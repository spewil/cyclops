import sys

from PyQt5.QtCore import QDir, Qt, QSize, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QLabel, QPushButton

import cv2
import numpy as np

# worker.py
class Worker(QObject):
    imageready = pyqtSignal(QImage)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    @pyqtSlot()
    def displayImage(self): # A slot takes no params
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            # emit the signal
            self.imageready.emit(p)

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480

        self.label = QLabel(self)

        # 1 - create Worker and Thread inside the Form
        self.worker = Worker()  # no parent!
        self.thread = QThread()  # no parent!

        # 2 - Connect Worker`s Signals to Form method slots to post data.
        self.worker.imageready.connect(self.display_image)

        # 3 - Move the Worker object to the Thread object
        self.worker.moveToThread(self.thread)

        # # 4 - Connect Worker Signals to the Thread slots
        self.thread.finished.connect(self.thread.quit)

        # 5 - Connect Thread started signal to Worker operational slot method
        self.thread.started.connect(self.worker.displayImage)

        # * - Thread finished signal will close the app if you want!
        self.thread.finished.connect(app.exit)

        # 6 - Start the thread
        self.thread.start()

        # 7 - Start the form
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(700, 500)
        # create a label
        self.label.move(30, 10)
        self.label.resize(640, 480)

    def display_image(self, image):
        pixmap_image = QPixmap(QPixmap.fromImage(image))
        self.label.setPixmap(pixmap_image)
        self.label.show()

app = QApplication(sys.argv)
window = GUI()
window.show()
sys.exit(app.exec_())

# https://stackoverflow.com/questions/6783194/background-thread-with-qthread-in-pyqt
# https://gist.github.com/jazzycamel/8abd37bf2d60cce6e01d