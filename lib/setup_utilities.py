# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import cv2
from tifffile import imsave
try:
    from lib import pco_camera
except:
    import pco_camera

# ============================================================================

CV_ESC_KEY = 27
CV_ENT_KEY = 13

# ============================================================================

class FPS:
    def __init__(self):
        # store the start time, end time, and total number of frames
        # that were examined between the start and end intervals
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()

    def update(self):
        # increment the total number of frames examined during the
        # start and end intervals
        self._numFrames += 1

    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        return (self._end - self._start).total_seconds()

    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()

def convert_npy_to_tiff(npy_file, w, h):
    filename = npy_file
    out_filename = os.path.splitext(npy_file)[0] + '.tiff'
    idx = 1
    with open(filename, 'rb') as f_in:
        while True:
            try:
                frame = np.load(f_in).reshape(h, w)
                imsave(os.path.join(os.path.abspath(os.path.join(filename, os.pardir)), out_filename), frame, append=True)
                idx += 1
            except IOError:
                print("Conversion complete.")
                break

def select_rectangular_roi(settings):
    settings_dict = settings
    camera = pco_camera.Camera(settings_dict["frame_rate_mHz"],
                                    settings_dict["exposure_time_ns"],
                                    settings_dict["binning"],
                                    settings_dict["binning"],
                                    *settings_dict["roi"])
    fromCenter = False
    showCrosshair = False
    cv2.namedWindow("Choose Frame")
    camera.start_record()
    print("Hit Enter to choose a frame.")
    while True:
        array = camera.get_latest_array()
        cv2.imshow("Choose Frame", array)
        if cv2.waitKey(1) is CV_ENT_KEY:
            break
    cv2.destroyAllWindows()
    camera.stop_record()
    cv2.namedWindow("ROI Selection")
    rectangle = cv2.selectROI("ROI Selection", array, fromCenter, showCrosshair)
    cv2.destroyAllWindows()
    print("soft ROI set:", rectangle)
    x, y, w, h = rectangle
    mask = np.zeros((settings_dict["cam_y_res"],settings_dict["cam_x_res"]))
    mask[y:y+h, x:x+w] = 1
    soft_roi = x, y, x+w, y+h
    camera.close()
    return mask.astype(np.bool), soft_roi

class TransformCalculator:
    def __init__(self, settings_dict):
        self.camera = pco_camera.Camera(settings_dict["frame_rate_mHz"],
                                        settings_dict["exposure_time_ns"],
                                        settings_dict["binning"],
                                        settings_dict["binning"],
                                        *settings_dict["roi"])
        self.reference_frame = np.zeros((self.camera.yRes, self.camera.xRes))
        self.transform = None
        self.done = False # Flag signalling we're done
        self.current = (0, 0) # Current position, so we can draw the line-in-progress
        self.reference_points = [[100,100],[self.camera.xRes - 100,100],[self.camera.xRes // 2, self.camera.yRes-100]]
        self.overlayed_points = []

    def on_mouse(self, event, x, y, flags, params):
        if self.done:
            return
        if event == cv2.EVENT_MOUSEMOVE:
            self.current = (x, y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            print("Adding overlayed point #%d with position(%d,%d)" % (len(self.overlayed_points)+1, x, y))
            self.overlayed_points.append([x, y])
            if len(self.overlayed_points) == 3:
                print("All points chosen.")
                self.done = True

    def compute_transform(self):
        cv2.namedWindow("Reference")
        numbers = ['1', '2', '3']
        for number, pt in zip(numbers,self.reference_points):
            cv2.circle(self.reference_frame, (pt[0], pt[1]), 5, (255, 255, 255), 5)
            cv2.putText(self.reference_frame, number,(pt[0]-10, pt[1]-10), cv2.FONT_HERSHEY_PLAIN, 6, (255, 255, 255))
        cv2.imshow("Reference", self.reference_frame)
        cv2.namedWindow("Overlayed")
        cv2.setMouseCallback("Overlayed", self.on_mouse)
        self.camera.start_record()
        while not self.done:
            overlayed_frame = self.camera.get_latest_array()
            cv2.imshow("Reference", self.reference_frame)
            for pt in self.overlayed_points:
                cv2.circle(overlayed_frame, (pt[0], pt[1]), 5, (255, 255, 255), 5)
            cv2.imshow("Overlayed", overlayed_frame)
            if cv2.waitKey(1) == CV_ENT_KEY or self.done:
                self.done = True
        self.camera.stop_record()
        cv2.destroyAllWindows()
        self.camera.close()
        return cv2.getAffineTransform(np.array(self.reference_points, dtype=np.float32), np.array(self.overlayed_points, dtype=np.float32))

class PolygonSelector:
    def __init__(self, settings_dict):
        self.done = False
        self.current = (0, 0)
        self.polygon_points = []
        self.camera = pco_camera.Camera(settings_dict["frame_rate_mHz"],
                                        settings_dict["exposure_time_ns"],
                                        settings_dict["binning"],
                                        settings_dict["binning"],
                                        *settings_dict["roi"])

    def on_mouse(self, event, x, y, flags, params):
        if self.done:
            return
        if event == cv2.EVENT_MOUSEMOVE:
            self.current = (x, y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            print("Adding overlayed point #%d with position(%d,%d) " % (len(self.polygon_points)+1, x, y))
            self.polygon_points.append([x, y])
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.done = True

    def compute_mask(self):
        cv2.namedWindow("Overlayed")
        cv2.setMouseCallback("Overlayed", self.on_mouse)
        self.camera.start_record()
        while not self.done:
            overlayed_frame = self.camera.get_latest_array()
            for pt in self.polygon_points:
                cv2.circle(overlayed_frame, (pt[0], pt[1]), 5, (255, 255, 255), 5)
            cv2.imshow("Overlayed", overlayed_frame)
            if cv2.waitKey(1) == CV_ENT_KEY or self.done:
                self.done = True
        self.camera.stop_record()
        cv2.destroyAllWindows()
        self.camera.close()
        return cv2.fillConvexPoly(np.zeros((self.camera.yRes,self.camera.xRes)), np.array(self.polygon_points, dtype=np.int32), 1).astype(np.bool), self.polygon_points