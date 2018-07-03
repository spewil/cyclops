# -*- coding: utf-8 -*-

import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QLabel, QPushButton, QLineEdit, QVBoxLayout, \
    QHBoxLayout, QStatusBar, QAction

import cv2
import time
import datetime
import numpy as np
from random import shuffle
import json

CV_ESC_KEY = 27
CV_ENT_KEY = 13

class Raster(QMainWindow):
    def __init__(self):
        super().__init__()
        with open("settings.json", "r") as f:
            self.settings_dict = json.load(f)
        self.experiment_path = self.settings_dict["folder_path"]

        self.title = "Raster"
        self.left = 100
        self.top = 100
        self.window_width = 480
        self.window_height = 640
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.window_width, self.window_height)
        self.resize(300, 400)
        main_widget = QWidget()
        self.window_layout = QVBoxLayout()
        self.window_layout.setAlignment(Qt.AlignCenter)
        main_widget.setLayout(self.window_layout);
        self.setCentralWidget(main_widget)

        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.setStatusTip("Save current settings and close")
        quit_action.triggered.connect(self.close_gui)
        load_settings_action = QAction("Save Settings", self)
        load_settings_action.setShortcut("Ctrl+L")
        load_settings_action.setStatusTip("Load settings")
        load_settings_action.triggered.connect(self.load_settings)
        save_settings_action = QAction("Save Settings", self)
        save_settings_action.setShortcut("Ctrl+S")
        save_settings_action.setStatusTip("Save current settings")
        save_settings_action.triggered.connect(self.save_settings)
        main_menu = self.menuBar()
        fileMenu = main_menu.addMenu("&File")
        fileMenu.addAction(load_settings_action)
        fileMenu.addAction(save_settings_action)
        fileMenu.addAction(quit_action)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        frame_size_layout = QHBoxLayout()
        frame_size_label = QLabel("Width x Height : ")
        self.res_label = QLabel(str(self.settings_dict["cam_x_res"]) + " x " + str(self.settings_dict["cam_y_res"]))
        self.res_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        frame_size_layout.addWidget(frame_size_label)
        frame_size_layout.addWidget(self.res_label)
        self.window_layout.addLayout(frame_size_layout)

        self.make_open_loop_controls()

        update_button = QPushButton("Import Settings", self)
        update_button.clicked.connect(self.load_settings)
        self.window_layout.addWidget(update_button)
        save_button = QPushButton("Save Settings", self)
        save_button.clicked.connect(self.save_settings)
        self.window_layout.addWidget(save_button)
        start_button = QPushButton("START", self)
        start_button.clicked.connect(self.run)
        self.window_layout.addWidget(start_button)
        self.open_loop_keys = ["rows", "cols", "duration_s", "interval_s"]

    def update_frame_size(self):
        self.res_label.setText(str(self.settings_dict["cam_x_res"]) + " x " + str(self.settings_dict["cam_y_res"]))

    def update_setting(self, key, val):
        self.settings_dict[key] = val
        self.statusBar.showMessage("\"" + str(key) + "\"" + " changed to " + str(val), 3000)

    def save_settings(self, filename):
        with open(filename, "w") as fp:
            json.dump(self.settings_dict, fp, sort_keys=True, indent=4)
        self.statusBar.showMessage("settings saved")

    def load_settings(self):
        with open("settings.json", "r") as f:
            settings_dict = json.load(f)
            for key, val in zip(settings_dict.keys(), settings_dict.values()):
                if key not in set(self.open_loop_keys):
                    self.update_setting(key, val)
        self.update_frame_size()
        self.statusBar.showMessage("settings loaded")

    def close_gui(self):
        with open("settings.json", "w") as fp:
            json.dump(self.settings_dict, fp, sort_keys=True, indent=4)
        self.close()
        QApplication.instance().quit()

    def run(self):
        did_setup = self.setup()
        if did_setup:
            base = np.zeros((self.settings_dict["cam_y_res"], self.settings_dict["cam_x_res"]))
            cv2.namedWindow("Raster")
            for mask in self.masks:
                base[mask] = 255
                if self.settings_dict["transform_on"]:
                    cv2.imshow("Raster", cv2.warpAffine(base, self.transform, (self.settings_dict["cam_x_res"], self.settings_dict["cam_y_res"])))
                    if cv2.waitKey(int(self.settings_dict["duration_s"] * 1000)) is CV_ESC_KEY:
                        break
                else:
                    cv2.imshow("Raster", base)
                    if cv2.waitKey(int(self.settings_dict["duration_s"] * 1000)) is CV_ESC_KEY:
                        break
                time.sleep(self.settings_dict["interval_s"])
                base[mask] = 0
            cv2.destroyAllWindows()
        else:
            pass

    def setup(self):
        self.load_settings()
        if self.settings_dict["folder_path"] != "None":
            if self.settings_dict["cols"] > self.settings_dict["cam_x_res"] or self.settings_dict["rows"] > self.settings_dict["cam_y_res"]:
                raise Exception("Too many rows or columns.")
            if self.settings_dict["soft_roi"] != None:
                sx0, sy0, sx1, sy1 = self.settings_dict["soft_roi"]
                self.soft_width = sx1 - sx0 + 1
                self.soft_height = sy1 - sy0 + 1
                idxs = self.define_grid((self.soft_height, self.soft_width), (self.settings_dict["rows"], self.settings_dict["cols"]))
            else:
                sx0, sy0, sx1, sy1 = (1,1,self.settings_dict["cam_x_res"],self.settings_dict["cam_y_res"])
                idxs = self.define_grid((self.settings_dict["cam_y_res"], self.settings_dict["cam_x_res"]), (self.settings_dict["rows"], self.settings_dict["cols"]))
            masks = []
            mask = np.zeros((self.settings_dict["cam_y_res"], self.settings_dict["cam_x_res"]))
            for r in range(self.settings_dict["rows"]):
                for c in range(self.settings_dict["cols"]):
                    mask[idxs[0][r][0] + sx0:idxs[0][r][1] + sx0, idxs[1][c][0] + sy0:idxs[1][c][1] + sy0] = 1
                    masks.append(mask.astype(np.bool))
                    mask = np.zeros((self.settings_dict["cam_y_res"], self.settings_dict["cam_x_res"]))
            self.mask_order = list(range(len(masks)))
            shuffle(self.mask_order)
            self.masks = [masks[k] for k in self.mask_order]
            self.update_setting("open_loop_order", self.mask_order)
            self.save_settings("settings.json")
            self.save_settings(self.experiment_path+"settings.json")
            np.save(self.experiment_path+"raster_order.npy", self.mask_order)

            if self.settings_dict["transform_on"]:
                print("applying transform")
                self.transform = np.load("transform.npy")
            else:
                self.transform = None
            setup = True
        else:
            print("No new folder created, must run Recorder first!")
            setup = False
        return setup

    def define_grid(self, size_data, shape_grid):
        '''
        :param size_data: Size/shape of incoming data.
        :param shape_grid: Size/shape of required output
        :return: list of lists of tuples (start_idx, stop_idx)

        Note that the leftover pixels are pushed to the end of every dimension as leftovers.
        This should only really matter when there are lots of leftoxer pixels, so not often.
        '''
        if len(size_data) is not len(shape_grid):
            raise Exception("Dimensions of data and grid must be equal.")

        indices = []
        # rows, cols, stacks...
        for size, shape in zip(size_data, shape_grid):
            extra_pxls = size % shape
            num_pxls = size // shape
            curr_indices = []
            for r in range(shape):
                if r is shape-1:
                    curr_indices.append((r*num_pxls,(r+1)*num_pxls + extra_pxls))
                else:
                    curr_indices.append((r*num_pxls,(r+1)*num_pxls))
            indices.append(curr_indices)
        return indices

    def add_label(self, title, val):
        label_title = QLabel(title)
        label = QLabel(str(val))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout = QHBoxLayout()
        layout.addWidget(label_title)
        layout.addWidget(label)
        self.window_layout.addLayout(layout)
        return label

    def make_open_loop_controls(self):
        row_line = QLineEdit("", self)
        row_label = QLabel("Rows")
        col_line = QLineEdit("", self)
        col_label = QLabel("Columns")
        duration_line = QLineEdit("", self)
        duration_label = QLabel("Duration")
        interval_line = QLineEdit("", self)
        interval_label = QLabel("Interval")
        double_validator = QDoubleValidator()
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        duration_line.setValidator(double_validator)
        interval_line.setValidator(double_validator)
        row_line.returnPressed.connect(lambda: self.update_setting("rows", int(row_line.text())))
        col_line.returnPressed.connect(lambda: self.update_setting("cols", int(col_line.text())))
        duration_line.returnPressed.connect(lambda: self.update_setting("duration_s", duration_line.text()))
        interval_line.returnPressed.connect(lambda: self.update_setting("interval_s", interval_line.text()))
        self.open_loop_labels = [row_label, col_label, duration_label, interval_label]
        self.open_loop_lines = [row_line, col_line, duration_line, interval_line]
        keys = ["rows", "cols", "duration_s", "interval_s"]
        control_layout = QHBoxLayout()
        for label, line, key in zip(self.open_loop_labels, self.open_loop_lines, keys):
            label.setAlignment(Qt.AlignCenter)
            line.setPlaceholderText(str(self.settings_dict[key]))
            layout = QVBoxLayout()
            layout.addWidget(label)
            layout.addWidget(line)
            layout.setSpacing(0)
            control_layout.addLayout(layout)
        self.window_layout.addLayout(control_layout)

app = QApplication(sys.argv)
window = Raster()
window.show()
sys.exit(app.exec_())