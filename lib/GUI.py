import sys

from PyQt5.QtCore import QDir, Qt, QSize, QThread, QObject, pyqtSignal, pyqtSlot, QRect, QPoint
from PyQt5.QtGui import QImage, QPixmap, QColor, QPainter, QBrush
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QLabel, QPushButton, QDialog

import cv2
import numpy as np
import time


# worker.py
class Worker(QObject):
    imageready = pyqtSignal(QPixmap)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    # all this will do is get the image
    @pyqtSlot()
    def do_work(self):  # A slot takes no params
        cap = cv2.VideoCapture(0)
        while True:
            time.sleep(0.005)
            ret, frame = cap.read()
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            qimage = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            pixmap = QPixmap.fromImage(qimage)
            # emit the signal
            self.imageready.emit(pixmap)


class SecondWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.title = 'Control Window'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(700, 500)
        self.show()
        # has its own label for the second video
        self.label = QLabel(self)
        self.label.move(30, 10)
        self.label.resize(640, 480)
        self.label.show()

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = 'Video Feed'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480

        self.control_running = False

        self.label = QLabel(self)

        self.begin = QPoint()
        self.end = QPoint()

        # 1 - create Worker and Thread inside the GUI
        self.worker = Worker()  # no parent!
        self.thread = QThread()  # no parent!
        # 2 - Connect Worker`s Signals to GUI method slots to post data.
        self.worker.imageready.connect(self.display_image)
        # 3 - Move the Worker object to the Thread object
        self.worker.moveToThread(self.thread)
        # # 4 - Connect Worker Signals to the Thread slots
        self.thread.finished.connect(self.thread.quit)
        # 5 - Connect Thread started signal to Worker operational slot method
        self.thread.started.connect(self.worker.do_work)
        # * - Thread finished signal will close the app if you want!
        # self.thread.finished.connect(app.exit)
        # 6 - Start the thread
        # self.thread.start()
        # 7 - Start the form
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(700, 500)
        # create a label
        self.label.move(30, 10)
        self.label.resize(640, 480)

        button = QPushButton('Start Webcam', self)
        button.setToolTip('Starts a thread to show live webcam.')
        button.move(100, 70)
        button.clicked.connect(self.thread.start)

        button = QPushButton('Open Control View', self)
        button.setToolTip('Opens a new dialog with processed image')
        button.move(300, 70)
        button.clicked.connect(self.make_control_window)

    def display_image(self, pixmap):
        self.label.setPixmap(pixmap)
        if self.control_running:
            # print("control running")
            self.control_window.label.setPixmap(pixmap)

    def make_control_window(self):
        self.control_running = True
        self.control_window = SecondWindow()

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        print("coords: ", self.begin, self.end)
        if not self.begin == self.end:
            self.update()
        else:
            pass
            # coords are the image size


app = QApplication(sys.argv)
window = GUI()
window.show()
sys.exit(app.exec_())

# https://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
# https://gist.github.com/jazzycamel/8abd37bf2d60cce6e01d

# stop a thread from processing with flags?

# if main window is closed, close all windows

# slot = method
# signal = click, QtCore.SIGNAL(‘signalname’), etc

# #Initialze QtGui.QImage() with arguments data, height, width, and QImage.Format
# self.data = np.array(self.data).reshape(2048,2048).astype(np.int32)
# qimage = QtGui.QImage(self.data, self.data.shape[0],self.data.shape[1],QtGui.QImage.Format_RGB32)
# img = PrintImage(QPixmap(qimage))

# make the rectangle only on a file--> add ROI call, otherwise unchangeable
