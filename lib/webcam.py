import numpy as np
import cv2
import time

CV_ESC_KEY = 27

class WebcamCaptureError(ValueError):
    pass

class webcam:
    def __init__(self, window_name):
        self.cap = cv2.VideoCapture(0)
        self.window_name = window_name

    def get_image(self):
        ret, frame = self.cap.read()
        if not ret:
            raise WebcamCaptureError
        else:
            return frame

    def close_capture(self):
        self.cap.release()
        cv2.destroyAllWindows()


def display_raw_frames(camera):
    while True:
        processed_frame = cv2.cvtColor(camera.get_image(), cv2.COLOR_BGR2GRAY)

        cv2.imshow('Control Output', processed_frame)

        time.sleep(.1)

        if cv2.waitKey(1) == CV_ESC_KEY:
            break

if __name__ == '__main__':
    camera = webcam('Test')
    display_raw_frames(camera)