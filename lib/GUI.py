import sys
import math

from PyQt5.QtCore import QDir, Qt, QSize, QThread, QObject, pyqtSignal, pyqtSlot, QRect, QPoint
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QBrush, QIntValidator
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QLabel, QPushButton, QDialog, QLineEdit, QVBoxLayout, \
    QHBoxLayout, QComboBox, QCheckBox, QFileDialog

import cv2
import numpy as np
import time
import random

CAM_MAX_X_RES = 2560
CAM_MAX_Y_RES = 2160
CAM_MAX_X_STEP = 160

class GUI(QWidget):

    def __init__(self):
        super().__init__()

        self.title = 'CyCLOpS'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480

        # make a new settings dict
        self.settings_dict = {}
        # load default settings from file here
        # self.load_settings('settings.json')

        ####################################################
        # this will go away
        self.settings_dict['framerate_mHz'] = 100
        self.settings_dict['exposure_time_ns'] = 25
        self.settings_dict['binning'] = 2
        self.settings_dict['control_type'] = 'Open-Loop'
        self.settings_dict['soft_roi_type'] = None
        self.settings_dict['display_on'] = True
        self.settings_dict['control_on'] = True
        self.settings_dict['save_on'] = True
        self.settings_dict['threshold'] = 100
        self.settings_dict['soft_roi'] = (1, 2, 3, 4)
        self.settings_dict['do_transform'] = True
        self.settings_dict['transform'] = None
        self.settings_dict['rectangular_roi'] = None
        self.settings_dict['polygonal_roi'] = None

        ####################################################

        self.settings_dict['cam_x_res'] = CAM_MAX_X_RES // self.settings_dict['binning']
        self.settings_dict['cam_y_res'] = CAM_MAX_Y_RES // self.settings_dict['binning']
        self.settings_dict['cam_x_step'] = CAM_MAX_X_STEP // self.settings_dict['binning']
        self.settings_dict['roi'] = (1, 1, self.settings_dict['cam_x_res'], self.settings_dict['cam_y_res'])

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(300, 400)
        self.window_layout = QVBoxLayout()
        self.window_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.window_layout)
        self.controls = {}

        #### ADD ALL WIDGETS ####
        load_button = self.add_button('Load Settings', None, self.load_settings)
        self.control_lock = self.add_button('LOCK', None, self.toggle_control_lock)

        framerate_line = self.add_line('Framerate [Hz]: ', 'framerate_mHz', 1e3)
        self.exposure_line = self.add_line('Exposure Time [ms]: ', 'exposure_time_ns', 1e6)

        self.binning_types = ['1', '2', '4']
        self.binning_dropdown = self.add_dropdown('Binning: ', 'binning', self.binning_types)
        self.roi_label = self.add_label('Frame Size: \n(x\u2081, y\u2081, x\u2082, y\u2082)', 'roi')
        self.make_hard_roi_widget()

        self.control_types = ['Closed-Loop', 'Open-Loop']
        self.control_dropdown = self.add_dropdown('Control Type: ', 'control_type', self.control_types)
        self.threshold_line = self.add_line('Control Threshold: ', 'threshold', 1)

        self.soft_roi_types = ['Rectangular', 'Polygonal', 'None']
        self.soft_roi_dropdown = self.add_dropdown('Soft ROI Type: ', 'soft_roi_type', self.soft_roi_types)

        display_box = self.add_checkbox('Show Display', 'display_on')
        control_box = self.add_checkbox('Show Control', 'control_on')
        save_box = self.add_checkbox('Save Images', 'save_on')
        self.transform_box = self.add_checkbox('Apply Transform', 'do_transform')

        fps_label = self.add_label('FPS: ', 'exposure_time_ns')
        fps_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        fps_label.setText("{0:.2f}".format(1000 / self.settings_dict['exposure_time_ns']))
        self.soft_roi_label = self.add_label('Soft ROI: ', 'soft_roi')
        self.soft_roi_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.transform_label = self.add_label('Transform: ', 'transform')
        self.transform_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.soft_roi_button = self.add_button('Set Soft ROI', 'soft_roi', self.set_soft_roi)
        transform_button = self.add_button('Compute Transform', 'transform', self.compute_transform)
        record_button = self.add_button('RECORD', None, self.show_video)
        quit_button = self.add_button('QUIT', None, self.close_gui)

        self.setting_label = self.add_label('', None)

        #### CONNECT WIDGETS TO SPECIAL FUNCTIONS ####
        self.exposure_line.returnPressed.connect(lambda: fps_label.setText("{0:.2f}".format(1e9 / self.settings_dict['exposure_time_ns'])))
        self.transform_box.toggled.connect(self.check_transform)
        self.control_dropdown.currentIndexChanged.connect(self.set_control_type)
        self.soft_roi_dropdown.currentIndexChanged.connect(self.set_soft_roi_type)
        self.binning_dropdown.currentIndexChanged.connect(self.set_binning)

        #### LOCK CONTROLS ####
        self.lock_controls = False
        self.toggle_control_lock()

    ######################################################

    def make_hard_roi_widget(self):
        left_left_button = QPushButton('\u2190', self)
        left_right_button = QPushButton('\u2192', self)
        right_left_button = QPushButton('\u2190', self)
        right_right_button = QPushButton('\u2192', self)
        top_button = QPushButton('\u2191', self)
        bottom_button = QPushButton('\u2193', self)
        buttons = [left_left_button, left_right_button, top_button, bottom_button, right_left_button, right_right_button]
        roi_keys = ['left_left', 'left_right', 'top', 'bottom', 'right_left', 'right_right']

        # check that it's okay-- if yes, update settings_dict and label
        left_left_button.clicked.connect(lambda: move_left('left'))
        left_right_button.clicked.connect(lambda: move_left('right'))
        right_left_button.clicked.connect(lambda: move_right('left'))
        right_right_button.clicked.connect(lambda: move_right('right'))
        top_button.clicked.connect(lambda: change_height('increase'))
        bottom_button.clicked.connect(lambda: change_height('decrease'))

        control_layout = QHBoxLayout()
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

        left_label = QLabel('Left Edge', self)
        left_label.setAlignment(Qt.AlignCenter)
        middle_label = QLabel('Height')
        middle_label.setAlignment(Qt.AlignCenter)
        right_label = QLabel('Right Edge')
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

        def move_left(dir):
            w = self.settings_dict['roi'][2] - self.settings_dict['roi'][0] + 1
            if dir is 'left':
                if self.settings_dict['roi'][0] - self.settings_dict['cam_x_step'] > 0:
                    new_tuple = (self.settings_dict['roi'][0] - self.settings_dict['cam_x_step'], *self.settings_dict['roi'][1:4])
                    self.update_setting('roi', new_tuple)
                    self.roi_label.setText(str(self.settings_dict['roi']))
                    self.repaint()
            else: # dir is 'right':
                if w - self.settings_dict['cam_x_step'] >= self.settings_dict['cam_x_step']:
                    new_tuple = (self.settings_dict['roi'][0] + self.settings_dict['cam_x_step'], *self.settings_dict['roi'][1:4])
                    self.update_setting('roi', new_tuple)
                    self.roi_label.setText(str(self.settings_dict['roi']))
                    self.repaint()

        def move_right(dir):
            w = self.settings_dict['roi'][2] - self.settings_dict['roi'][0] + 1
            if dir is 'right':
                if self.settings_dict['roi'][2] + self.settings_dict['cam_x_step'] <= self.settings_dict['cam_x_res']:
                    new_tuple = (*self.settings_dict['roi'][0:2], self.settings_dict['roi'][2] + self.settings_dict['cam_x_step'], self.settings_dict['roi'][3])
                    self.update_setting('roi', new_tuple)
                    self.roi_label.setText(str(self.settings_dict['roi']))
                    self.repaint()
            else: # dir is 'left':
                if w - self.settings_dict['cam_x_step'] >= self.settings_dict['cam_x_step']:
                    new_tuple = (*self.settings_dict['roi'][0:2], self.settings_dict['roi'][2] - self.settings_dict['cam_x_step'], self.settings_dict['roi'][3])
                    self.update_setting('roi', new_tuple)
                    self.roi_label.setText(str(self.settings_dict['roi']))
                    self.repaint()

        def change_height(dir):
            h = self.settings_dict['roi'][3] - self.settings_dict['roi'][1] + 1
            if dir is 'increase':
                if self.settings_dict['roi'][1] - 1 >= 1:
                    new_tuple = (self.settings_dict['roi'][0], self.settings_dict['roi'][1] - 1, self.settings_dict['roi'][2], self.settings_dict['roi'][3] + 1)
                    self.update_setting('roi', new_tuple)
                    self.roi_label.setText(str(self.settings_dict['roi']))
                    self.repaint()
            else: #dir is 'down'
                if h - 2 > 0:
                    new_tuple = (self.settings_dict['roi'][0], self.settings_dict['roi'][1] + 1, self.settings_dict['roi'][2],
                                 self.settings_dict['roi'][3] - 1)
                    self.update_setting('roi', new_tuple)
                    self.roi_label.setText(str(self.settings_dict['roi']))
                    self.repaint()

    def set_soft_roi(self):
        # if self.settings_dict['soft_roi_type'] is 'Polygonal':
        #     selector = PolygonSelector(camera)
        #     mask = selector.mask
        #     camera = restart_camera(camera, settings_dict)
        # elif self.settings_dict['soft_roi_type'] is 'Rectangular':
        #     mask = select_rectangular_roi(camera)
        #     camera = restart_camera(camera, settings_dict)
        soft_roi = str(random.sample(range(200), 5))
        self.update_setting('soft_roi', soft_roi)
        self.soft_roi_label.setText(str(soft_roi))
        self.repaint()

    def load_settings(self, filename):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "JSON Files (*.json);")
        # load JSON file
        # dict = load_json
        for key, val in zip(dict.keys(), dict.values()):
            self.update_setting(key, val)
        return dict

    def compute_transform(self):
        transform = str(random.sample(range(200), 5))
        self.transform_label.setText(str(transform))
        self.update_setting('transform', transform)
        self.repaint()

    def set_binning(self):
        old_binning = self.settings_dict['binning']
        binning = int(self.binning_types[self.binning_dropdown.currentIndex()])
        ratio = old_binning/binning
        self.update_setting('cam_x_res', CAM_MAX_X_RES // binning)
        self.update_setting('cam_y_res', CAM_MAX_Y_RES // binning)
        self.update_setting('cam_x_step', CAM_MAX_X_STEP // binning)
        if self.settings_dict['roi'][0] is 1:
            left = 1
        else:
            left = int((self.settings_dict['roi'][0]-1)*ratio + 1)
        if self.settings_dict['roi'][1] is 1:
            top = 1
        else:
            top = int((self.settings_dict['roi'][1]-1)*ratio + 1)
        new_label = (left, top, int(self.settings_dict['roi'][2]*ratio), int(self.settings_dict['roi'][3]*ratio))
        self.update_setting('roi', new_label)
        self.update_setting('binning', binning)
        self.roi_label.setText(str(self.settings_dict['roi']))
        self.repaint()

    def check_transform(self):
        if self.transform_box.isChecked() and self.settings_dict['transform'] is None:
            print('No transform found in your settings! Computing transform... ')
            self.compute_transform()

    def show_video(self):
        fromCenter = False
        showCrosshair = False
        cv2.namedWindow("Choose Frame")
        if self.settings_dict['control_on']:
            cv2.namedWindow("Second Frame")
        print("Hit Enter to choose a frame.")
        cap = cv2.VideoCapture(0)
        while True:
            ret, array = cap.read()
            cv2.imshow("Choose Frame", array)
            if self.settings_dict['control_on']:
                cv2.imshow("Second Frame", array)
            if cv2.waitKey(1) is 13:
                break
        cv2.destroyAllWindows()

    def close_gui(self):
        # save default settings to settings.json
        QApplication.instance().quit()

    ######################################################

    def update_setting(self, key, val):
        self.settings_dict[key] = val
        self.setting_label.setText(str(key)+' changed to '+str(val))

    def set_control_type(self):
        type = self.control_types[self.control_dropdown.currentIndex()]
        self.update_setting('control_type', type)
        if type is 'Closed-Loop':
            self.threshold_line.setEnabled(True)
        elif type is 'Open-Loop':
            self.threshold_line.setEnabled(False)
        else:
            pass

    def set_soft_roi_type(self):
        type = self.soft_roi_types[self.soft_roi_dropdown.currentIndex()]
        self.update_setting('soft_roi_type', type)
        if type is 'Rectangular':
            self.soft_roi_label.show()
            if self.settings_dict['soft_roi'] is None:
                self.set_soft_roi()
            self.soft_roi_label.setText(str(self.settings_dict['soft_roi']))
            self.soft_roi_button.setEnabled(True)
        elif type is 'Polygonal':
            self.soft_roi_label.setText('(Polygonal)')
            if self.settings_dict['soft_roi'] is None:
                self.set_soft_roi()
            self.soft_roi_button.setEnabled(True)
        elif type is 'None':
            self.soft_roi_label.hide()
            self.soft_roi_button.setEnabled(False)
        else:
            pass

    def toggle_control_lock(self):
        self.lock_controls = not self.lock_controls
        for control in self.controls.values():
            control.setEnabled(not control.isEnabled())
        if self.lock_controls:
            self.control_lock.setText('UNLOCK')
        else:
            self.control_lock.setText('LOCK')
        self.repaint()

    def add_button(self, title, key, func):
        button = QPushButton(title, self)
        button.clicked.connect(func)
        self.window_layout.addWidget(button)
        if key is not None:
            self.controls[key] = button
        return button

    def add_label(self, title, key):
        label_title = QLabel(title)
        if key is not None:
            label = QLabel(str(self.settings_dict[key]))
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            label = QLabel()
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
        line = QLineEdit('', self)
        int_validator = QIntValidator()
        line.setValidator(int_validator)
        line.setPlaceholderText(str(self.settings_dict[key]))
        line.returnPressed.connect(lambda: self.update_setting(key, int(int(line.text()) * multiplier)))
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(line)
        self.window_layout.addLayout(layout)
        self.controls[key] = line
        line.clearFocus()
        return line

app = QApplication(sys.argv)
window = GUI()
window.show()
sys.exit(app.exec_())
