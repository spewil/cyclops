import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QLabel, QPushButton, QLineEdit, QVBoxLayout, \
    QHBoxLayout, QComboBox, QCheckBox, QFileDialog, QAction, QStatusBar, QListWidget, QListWidgetItem

import os
import datetime
import pathlib
import json
import numpy as np

try:
    from lib.setup_utilities import TransformCalculator, PolygonSelector, select_rectangular_roi
    from lib.recorder import Recorder
except:
    from setup_utilities import TransformCalculator, PolygonSelector, select_rectangular_roi
    from recorder import Recorder

CAM_MAX_X_RES = 2560
CAM_MAX_Y_RES = 2160
CAM_MAX_X_STEP = 160

class Cyclops(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "CyCLOpS"
        self.left = 100
        self.top = 100
        self.width = 480
        self.height = 640
        self.settings_dict = {}
        self.controls = {}
        self.main = None

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(300, 400)
        main_widget = QWidget()
        self.window_layout = QVBoxLayout()
        self.window_layout.setAlignment(Qt.AlignCenter)
        main_widget.setLayout(self.window_layout);
        self.setCentralWidget(main_widget);
        show_settings_action = QAction("Show Settings", self)
        show_settings_action.setShortcut("Ctrl+Shift+S")
        show_settings_action.setStatusTip("Show current settings")
        show_settings_action.triggered.connect(self.show_settings)
        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.setStatusTip("Save current settings and close")
        quit_action.triggered.connect(self.close_gui)
        save_settings_action = QAction("Save Settings", self)
        save_settings_action.setShortcut("Ctrl+S")
        save_settings_action.setStatusTip("Save current settings")
        save_settings_action.triggered.connect(self.save_settings)
        set_default_action = QAction("Restore Default Settings", self)
        set_default_action.setStatusTip("Restore settings to default.json")
        set_default_action.triggered.connect(lambda: self.load_settings("default.json"))
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("&File")
        fileMenu.addAction(show_settings_action)
        fileMenu.addAction(save_settings_action)
        fileMenu.addAction(quit_action)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.open_loop_keys = ["rows", "cols", "duration_s", "interval_s"]
        self.load_settings("settings.json")
        self.load_transform("transform.npy")
        self.update_setting("folder_path", "None")

        #### ADD ALL WIDGETS ####
        load_layout = QHBoxLayout()
        load_settings_button = self.add_button("Load Settings", None, lambda: self.load_settings(None))
        load_transform_button = self.add_button("Load Transform", None, lambda: self.load_transform(None))
        load_layout.addWidget(load_settings_button)
        load_layout.addWidget(load_transform_button)
        self.window_layout.addLayout(load_layout)
        self.control_lock = self.add_button("LOCK", None, self.toggle_control_lock)
        framerate_line, _, _ = self.add_line("Framerate [Hz]: ", "frame_rate_mHz", 1e3)
        self.exposure_line, _, _ = self.add_line("Exposure Time [ms]: ", "exposure_time_ns", 1e6)
        fps_label = self.add_label("FPS: ", "exposure_time_ns")
        fps_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        fps_label.setText("{0:.2f}".format(1000 / self.settings_dict["exposure_time_ns"]))
        self.binning_types = ["1", "2", "4"]
        self.binning_dropdown = self.add_dropdown("Binning: ", "binning", self.binning_types)
        self.roi_label = self.add_label("Frame Size (x\u2081, y\u2081, x\u2082, y\u2082): ", "roi")

        frame_size_layout = QHBoxLayout()
        frame_size_label = QLabel("Width x Height : ")
        self.res_label = QLabel(str(self.settings_dict["cam_x_res"]) + " x " + str(self.settings_dict["cam_y_res"]))
        self.res_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        frame_size_layout.addWidget(frame_size_label)
        frame_size_layout.addWidget(self.res_label)
        self.window_layout.addLayout(frame_size_layout)

        self.make_roi_widget()
        self.control_types = ["Closed-Loop", "Open-Loop", "None"]
        self.control_dropdown = self.add_dropdown("Control Type: ", "control_type", self.control_types)
        self.threshold_line, self.threshold_label, self.threshold_layout = self.add_line("Control Threshold: ",
                                                                                         "closed_loop_threshold", 1)
        self.soft_roi_types = ["Rectangular", "Polygonal", "None"]
        self.soft_roi_dropdown = self.add_dropdown("Soft ROI Type: ", "soft_roi_type", self.soft_roi_types)
        display_box = self.add_checkbox("Show Display", "display_on")
        # control_box = self.add_checkbox("Show Control", "control_on")
        save_box = self.add_checkbox("Save Images", "save_on")
        self.transform_box = self.add_checkbox("Apply Transform", "transform_on")
        self.soft_roi_button = self.add_button("Set Soft ROI", "soft_roi_set", self.set_soft_roi)
        transform_button = self.add_button("Compute Transform", "transform", self.compute_transform)
        set_layout = QHBoxLayout()
        set_layout.addWidget(self.soft_roi_button)
        set_layout.addWidget(transform_button)
        self.window_layout.addLayout(set_layout)

        self.record_button = self.add_button("RECORD", None, self.record_video)
        save_button = self.add_button("Save Settings", None, self.save_settings)
        quit_button = self.add_button("QUIT", None, self.close_gui)

        #### CONNECT WIDGETS TO SPECIAL FUNCTIONS ####
        self.exposure_line.returnPressed.connect(
            lambda: fps_label.setText("{0:.2f}".format(1e9 / self.settings_dict["exposure_time_ns"])))
        self.control_dropdown.currentIndexChanged.connect(self.set_control_type)
        self.soft_roi_dropdown.currentIndexChanged.connect(self.set_soft_roi_type)
        self.binning_dropdown.currentIndexChanged.connect(self.set_binning)

        # set everything
        self.set_binning()
        self.set_control_type()
        self.set_soft_roi_type()

        #### LOCK CONTROLS ####
        self.lock_controls = False
        self.toggle_control_lock()

    ######################
    #    SET SETTINGS    #
    ######################

    def record_video(self):
        experiment_folder = os.path.join(os.path.normpath("C:/Users/Kelly_group01/Documents"), str(datetime.date.today())+"__"+str(datetime.datetime.now().time().strftime("%H_%M_%S")))
        self.experiment_path = os.path.join(os.path.normpath(experiment_folder),"")
        pathlib.Path(experiment_folder).mkdir(parents=True, exist_ok=True)
        self.update_setting("folder_path", self.experiment_path)
        self.save_settings()
        print("settings saved.")
        print("filessaved:",self.experiment_path)
        self.recorder = Recorder(self.settings_dict)
        self.recorder.record()
        self.update_setting("folder_path", "None")
        self.save_settings()

    def compute_transform(self):
        transformer = TransformCalculator(self.settings_dict)
        self.transform = transformer.compute_transform()
        self.transform = np.array(self.transform)
        np.save("transform.npy", self.transform)
        print("transform computed")

    def load_transform(self, filename):
        if filename == None:
            filename, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                      "NPY Files (*.npy);")
            self.transform = np.load(filename)
        else:
            self.transform = np.load(filename)

    def load_settings(self, filename):
        if filename == None:
            filename, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                      "JSON Files (*.json);")
            with open(filename, "r") as f:
                settings_dict = json.load(f)
                for key, val in zip(settings_dict.keys(), settings_dict.values()):
                    self.update_setting(key, val)
        else:
            with open(filename, "r") as f:
                settings_dict = json.load(f)
                for key, val in zip(settings_dict.keys(), settings_dict.values()):
                    self.update_setting(key, val)

    def save_settings(self):
        with open("settings.json", "w") as fp:
            json.dump(self.settings_dict, fp, sort_keys=True, indent=4)
        self.statusBar.showMessage("settings saved")

    def show_settings(self):
        list = QListWidget()
        list.resize(500, 500)
        for key, val in zip(self.settings_dict.keys(), self.settings_dict.values()):
            item = QListWidgetItem(key + " : " + str(val))
            list.addItem(item)
        self.window = list
        self.window.show()

    def update_setting(self, key, val):
        self.settings_dict[key] = val
        self.statusBar.showMessage("\"" + str(key) + "\"" + " changed to " + str(val), 3000)

    def set_binning(self):
        old_binning = self.settings_dict["binning"]
        binning = int(self.binning_types[self.binning_dropdown.currentIndex()])
        ratio = old_binning / binning
        if self.settings_dict["roi"][0] == 1:
            left = 1
        else:
            left = int((self.settings_dict["roi"][0] - 1) * ratio + 1)
        if self.settings_dict["roi"][1] == 1:
            top = 1
        else:
            top = int((self.settings_dict["roi"][1] - 1) * ratio + 1)
        new_label = (left, top, int(self.settings_dict["roi"][2] * ratio), int(self.settings_dict["roi"][3] * ratio))
        self.update_setting("roi", new_label)
        self.update_setting("binning", binning)
        self.update_setting("cam_x_res", int(self.settings_dict["cam_x_res"]*ratio))
        self.update_setting("cam_y_res", int(self.settings_dict["cam_y_res"]*ratio))
        self.roi_label.setText(str(self.settings_dict["roi"]))
        self.res_label.setText(str(self.settings_dict["cam_x_res"]) + " x " + str(self.settings_dict["cam_y_res"]))
        self.repaint()

    def set_control_type(self):
        type = self.control_types[self.control_dropdown.currentIndex()]
        self.update_setting("control_type", type)
        if type == "Closed-Loop":
            self.threshold_label.show()
            self.threshold_line.show()
        elif type == "Open-Loop" or type == "None":
            self.threshold_label.hide()
            self.threshold_line.hide()
        else:
            pass
        self.repaint()

    def set_soft_roi_type(self):
        type = self.soft_roi_types[self.soft_roi_dropdown.currentIndex()]
        if type == "Rectangular": #self.soft_roi_types[0]:
            self.soft_roi_button.setEnabled(True)
            self.mask = np.load("rectangular_roi_mask.npy")
        elif type == "Polygonal": #self.soft_roi_types[1]:
            self.soft_roi_button.setEnabled(True)
            self.mask = np.load("rectangular_roi_mask.npy")
        elif type == "None":
            self.soft_roi_button.setEnabled(False)
            self.mask = None
        else:
            pass
        self.update_setting("soft_roi_type", type)
        self.repaint()

    def set_soft_roi(self):
        type = self.soft_roi_types[self.soft_roi_dropdown.currentIndex()]
        if type == "Rectangular":
            self.mask, soft_roi = select_rectangular_roi(self.settings_dict)
            self.update_setting("soft_roi", soft_roi)
            self.update_setting("rectangular_soft_roi", soft_roi)
            np.save("rectangular_roi_mask.npy", self.mask)
        elif type == "Polygonal":
            selector = PolygonSelector(self.settings_dict)
            self.mask, soft_roi = selector.compute_mask()
            self.update_setting("soft_roi", soft_roi)
            self.update_setting("polygonal_soft_roi", soft_roi)
            np.save("polygonal_roi_mask.npy", self.mask)
        else:
            pass

    def closeEvent(self, event):
        self.close_gui()

    def close_gui(self):
        with open("settings.json", "w") as fp:
            json.dump(self.settings_dict, fp, sort_keys=True, indent=4)
        print("saved settings")
        np.save("transform.npy", self.transform)
        print("saved transform")
        self.close()
        QApplication.instance().quit()

    #############################
    #    MAKE GUI COMPONENTS    #
    #############################

    def toggle_control_lock(self):
        self.lock_controls = not self.lock_controls
        for control in self.controls.values():
            control.setEnabled(not control.isEnabled())
        if self.lock_controls:
            self.control_lock.setText("UNLOCK")
        else:
            self.control_lock.setText("LOCK")
        self.repaint()

    def add_button(self, title, key, func):
        button = QPushButton(title, self)
        button.clicked.connect(func)
        self.window_layout.addWidget(button)
        if key != None:
            self.controls[key] = button
        return button

    def add_label(self, title, key):
        label_title = QLabel(title)
        label = QLabel(str(self.settings_dict[key]))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout = QHBoxLayout()
        layout.addWidget(label_title)
        layout.addWidget(label)
        self.window_layout.addLayout(layout)
        return label

    def add_checkbox(self, title, key):
        box = QCheckBox(self)
        box.setText(title)
        box.setChecked(self.settings_dict[key])
        box.toggled.connect(lambda: self.update_setting(key, box.isChecked()))
        layout = QHBoxLayout()
        layout.addWidget(box)
        layout.setAlignment(Qt.AlignCenter)
        self.window_layout.addLayout(layout)
        self.controls[key] = box
        return box

    def add_dropdown(self, title, key, items):
        dropdown = QComboBox(self)
        dropdown.addItems(items)
        dropdown.setCurrentIndex(items.index(str(self.settings_dict[key])))
        label = QLabel(title)
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(dropdown)
        self.window_layout.addLayout(layout)
        self.controls[key] = dropdown
        return dropdown

    def add_line(self, title, key, multiplier):
        label = QLabel(title)
        line = QLineEdit("", self)
        int_validator = QIntValidator()
        line.setValidator(int_validator)
        line.setPlaceholderText(str(int(self.settings_dict[key] // multiplier)))
        line.returnPressed.connect(lambda: self.update_setting(key, int(int(line.text()) * multiplier)))
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(line)
        self.window_layout.addLayout(layout)
        self.controls[key] = line
        line.clearFocus()
        return line, label, layout

    def make_roi_widget(self):
        left_left_button = QPushButton("\u2190", self)
        left_right_button = QPushButton("\u2192", self)
        right_left_button = QPushButton("\u2190", self)
        right_right_button = QPushButton("\u2192", self)
        top_button = QPushButton("\u2191", self)
        bottom_button = QPushButton("\u2193", self)
        buttons = [left_left_button, left_right_button, top_button, bottom_button, right_left_button,
                   right_right_button]
        roi_keys = ["left_left", "left_right", "top", "bottom", "right_left", "right_right"]

        # check that it"s okay-- if yes, update settings_dict and label
        left_left_button.clicked.connect(lambda: self.move_left("left"))
        left_right_button.clicked.connect(lambda: self.move_left("right"))
        right_left_button.clicked.connect(lambda: self.move_right("left"))
        right_right_button.clicked.connect(lambda: self.move_right("right"))
        top_button.clicked.connect(lambda: self.change_height("increase"))
        top_button.setAutoRepeat(True)
        top_button.setAutoRepeatDelay(500)
        bottom_button.clicked.connect(lambda: self.change_height("decrease"))
        bottom_button.setAutoRepeat(True)
        bottom_button.setAutoRepeatDelay(500)

        left_layout = QVBoxLayout()
        middle_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        left_H_layout = QHBoxLayout()
        left_H_layout.addWidget(left_left_button)
        left_H_layout.addWidget(left_right_button)
        middle_H_layout = QHBoxLayout()
        middle_H_layout.addWidget(top_button)
        middle_H_layout.addWidget(bottom_button)
        right_H_layout = QHBoxLayout()
        right_H_layout.addWidget(right_left_button)
        right_H_layout.addWidget(right_right_button)

        left_label = QLabel("Left Edge", self)
        left_label.setAlignment(Qt.AlignCenter)
        middle_label = QLabel("Height")
        middle_label.setAlignment(Qt.AlignCenter)
        right_label = QLabel("Right Edge")
        right_label.setAlignment(Qt.AlignCenter)

        left_layout.addWidget(left_label)
        left_layout.addLayout(left_H_layout)
        left_layout.setSpacing(0)
        middle_layout.addWidget(middle_label)
        middle_layout.addLayout(middle_H_layout)
        middle_layout.setSpacing(0)
        right_layout.addWidget(right_label)
        right_layout.addLayout(right_H_layout)
        right_layout.setSpacing(0)

        control_layout = QHBoxLayout()
        control_layout.addLayout(left_layout)
        control_layout.addLayout(middle_layout)
        control_layout.addLayout(right_layout)

        for key, button in zip(roi_keys, buttons):
            self.controls[key] = button

        self.window_layout.addLayout(control_layout)

    def move_left(self, dir):
        w = self.settings_dict["roi"][2] - self.settings_dict["roi"][0] + 1
        if dir == "left":
            if self.settings_dict["roi"][0] - CAM_MAX_X_STEP > 0:
                new_tuple = (self.settings_dict["roi"][0] - CAM_MAX_X_STEP, *self.settings_dict["roi"][1:4])
                self.update_setting("roi", new_tuple)
                self.roi_label.setText(str(self.settings_dict["roi"]))
        else:
            if w - CAM_MAX_X_STEP >= CAM_MAX_X_STEP:
                new_tuple = (self.settings_dict["roi"][0] + CAM_MAX_X_STEP, *self.settings_dict["roi"][1:4])
                self.update_setting("roi", new_tuple)
                self.roi_label.setText(str(self.settings_dict["roi"]))
        self.update_setting("cam_x_res", self.settings_dict["roi"][2] - self.settings_dict["roi"][0] + 1)
        self.res_label.setText(str(self.settings_dict["cam_x_res"]) + " x " + str(self.settings_dict["cam_y_res"]))

    def move_right(self, dir):
        w = self.settings_dict["roi"][2] - self.settings_dict["roi"][0] + 1
        if dir == "right":
            if self.settings_dict["roi"][2] + CAM_MAX_X_STEP <= CAM_MAX_X_RES // self.settings_dict["binning"]:
                new_tuple = (*self.settings_dict["roi"][0:2], self.settings_dict["roi"][2] + CAM_MAX_X_STEP,
                             self.settings_dict["roi"][3])
                self.update_setting("roi", new_tuple)
                self.roi_label.setText(str(self.settings_dict["roi"]))
        else:
            if w - CAM_MAX_X_STEP >= CAM_MAX_X_STEP:
                new_tuple = (*self.settings_dict["roi"][0:2], self.settings_dict["roi"][2] - CAM_MAX_X_STEP,
                             self.settings_dict["roi"][3])
                self.update_setting("roi", new_tuple)
                self.roi_label.setText(str(self.settings_dict["roi"]))
        self.update_setting("cam_x_res", self.settings_dict["roi"][2] - self.settings_dict["roi"][0] + 1)
        self.res_label.setText(str(self.settings_dict["cam_x_res"]) + " x " + str(self.settings_dict["cam_y_res"]))

    def change_height(self, dir):
        h = self.settings_dict["roi"][3] - self.settings_dict["roi"][1] + 1
        if dir == "increase":
            if self.settings_dict["roi"][1] - 1 >= 1:
                new_tuple = (
                    self.settings_dict["roi"][0], self.settings_dict["roi"][1] - 1, self.settings_dict["roi"][2],
                    self.settings_dict["roi"][3] + 1)
                self.update_setting("roi", new_tuple)
                self.roi_label.setText(str(self.settings_dict["roi"]))
        else:
            if h - 2 > 0:
                new_tuple = (
                    self.settings_dict["roi"][0], self.settings_dict["roi"][1] + 1, self.settings_dict["roi"][2],
                    self.settings_dict["roi"][3] - 1)
                self.update_setting("roi", new_tuple)
                self.roi_label.setText(str(self.settings_dict["roi"]))
        self.update_setting("cam_y_res", self.settings_dict["roi"][3] - self.settings_dict["roi"][1] + 1)
        self.res_label.setText(str(self.settings_dict["cam_x_res"]) + " x " + str(self.settings_dict["cam_y_res"]))

app = QApplication(sys.argv)
window = Cyclops()
window.show()
sys.exit(app.exec_())
