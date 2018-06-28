import sys

from PyQt5.QtCore import QDir, Qt, QSize, QThread, QObject, pyqtSignal, pyqtSlot, QRect, QPoint
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QBrush, QIntValidator
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QLabel, QPushButton, QDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox

import cv2
import numpy as np
import time

class GUI(QWidget):

    def __init__(self):
        super().__init__()

        self.title = 'CyCLOpS Controller'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480

        # load settings from file here
        self.settings_dict = {}
        self.settings_dict['framerate_mHz'] = 100
        self.settings_dict['exposure_time_ns'] = 25
        self.settings_dict['binning'] = 2
        self.settings_dict['control_type'] = 'Open-Loop'
        self.settings_dict['soft_roi_type'] = 'Rectangular'
        self.settings_dict['display_on'] = True
        self.settings_dict['control_on'] = True
        self.settings_dict['save_on'] = True
        self.settings_dict['threshold'] = 100

        # self.control_running = False
        # self.label = QLabel(self)
        # # 1 - create Worker and Thread inside the GUI
        # self.worker = Worker()  # no parent!
        # self.thread = QThread()  # no parent!
        # # 2 - Connect Worker`s Signals to GUI method slots to post data.
        # self.worker.imageready.connect(self.display_image)
        # # 3 - Move the Worker object to the Thread object
        # self.worker.moveToThread(self.thread)
        # # # 4 - Connect Worker Signals to the Thread slots
        # self.thread.finished.connect(self.thread.quit)
        # # 5 - Connect Thread started signal to Worker operational slot method
        # self.thread.started.connect(self.worker.do_work)
        # # * - Thread finished signal will close the app if you want!
        # # self.thread.finished.connect(app.exit)
        # # 6 - Start the thread
        # # self.thread.start()
        # # 7 - Start the form
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(300, 400)
        self.window_layout = QVBoxLayout()
        self.window_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.window_layout)

        self.add_button('Load Settings', self.load_settings)

        self.add_line('Framerate [Hz]: ', 'framerate_mHz', 1e3)
        self.add_line('Exposure Time [ms]: ', 'exposure_time_ns', 1e6)
        self.add_line('Control Threshold: ', 'threshold', 1)

        self.add_dropdown('Binning: ', 'binning', ['1', '2', '4'])
        self.add_dropdown('Control Type: ', 'control_type', ['Closed-Loop', 'Open-Loop'])
        self.add_dropdown('Soft ROI Type: ', 'soft_roi_type', ['Rectangular', 'Polygonal'])

        self.add_checkbox('Display', 'display_on')
        self.add_checkbox('Control', 'control_on')
        self.add_checkbox('Save', 'save_on')

        self.add_button('Set Soft ROI', self.set_soft_roi)
        self.add_button('RECORD', self.show_video)
        self.add_button('QUIT', self.close_gui)

    def add_button(self, title, func):
        button = QPushButton(title, self)
        button.clicked.connect(func)
        self.window_layout.addWidget(button)
        return button

    def add_checkbox(self, title, key):
        box = QCheckBox(self)
        box.setText(title)
        box.setChecked(self.settings_dict[key])
        box.toggled.connect(lambda: self.update_settings(key, box.isChecked()))
        layout = QHBoxLayout()
        layout.addWidget(box)
        layout.setAlignment(Qt.AlignCenter)
        self.window_layout.addLayout(layout)
        return box

    def add_dropdown(self, title, key, items):
        dropdown = QComboBox(self)
        dropdown.addItems(items)
        dropdown.activated[str].connect(lambda: self.update_settings(key, dropdown.currentText()))
        label = QLabel(title)
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(dropdown)
        self.window_layout.addLayout(layout)
        return dropdown

    def add_line(self, title, key, multiplier):
        label = QLabel(title)
        line = QLineEdit('', self)
        int_validator = QIntValidator()
        line.setValidator(int_validator)
        line.setPlaceholderText(str(self.settings_dict[key]))
        line.returnPressed.connect(lambda: self.update_settings(key, int(int(line.text())*multiplier)))
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(line)
        self.window_layout.addLayout(layout)
        return line

    def load_settings(self):
        pass

    def set_soft_roi(self):
        pass
        # if self.settigns_dict['soft_roi_type'] is 'Polygonal':
        #     selector = PolygonSelector(camera)
        #     mask = selector.mask
        #     camera = restart_camera(camera, settings_dict)
        # elif self.settigns_dict['soft_roi_type'] is 'Rectangular':
        #     mask = select_rectangular_roi(camera)
        #     camera = restart_camera(camera, settings_dict)

    def update_settings(self, key, value):
        self.settings_dict[key] = value
        print(key,' changed to ', value)
        print(type(value))

    def close_gui(self):
        # save settings to file
        QApplication.instance().quit()

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

app = QApplication(sys.argv)
window = GUI()
window.show()
sys.exit(app.exec_())

