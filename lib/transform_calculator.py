# ============================================================================

import numpy as np
import cv2
from pathlib import Path
import time

# ============================================================================

CANVAS_SIZE = (600,800)
FINAL_LINE_COLOR = (255, 255, 255)
WORKING_LINE_COLOR = (127, 127, 127)
CV_ESC_KEY = 27
CV_ENT_KEY = 13

# ============================================================================

class TransformCalculator:
    def __init__(self, camera):
        self.camera = camera
        self.h = camera.yRes
        self.w = camera.xRes
        self.reference_frame = np.zeros((self.h,self.w))
        self.transform = None
        self.done = False # Flag signalling we're done
        self.current = (0, 0) # Current position, so we can draw the line-in-progress
        self.reference_points = [[100,100],[self.w-100,100],[self.w//2,self.h-100]]
        self.overlayed_points = []
        self.transform = self.compute_transform()

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
        return cv2.getAffineTransform(np.array(self.reference_points, dtype=np.float32), np.array(self.overlayed_points, dtype=np.float32))

class PolygonSelector:
    def __init__(self, camera):
        self.camera = camera
        self.h = camera.yRes
        self.w = camera.xRes
        self.done = False
        self.current = (0, 0)
        self.polygon_points = []
        self.mask = self.compute_mask()

    def on_mouse(self, event, x, y, flags, params):
        if self.done:
            return
        if event == cv2.EVENT_MOUSEMOVE:
            self.current = (x, y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            print("Adding overlayed point #%d with position(%d,%d) " % (len(self.polygon_points)+1, x, y))
            print(self.polygon_points)
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
        return cv2.fillConvexPoly(np.zeros((self.h,self.w)), np.array(self.polygon_points, dtype=np.int32), 1).astype(np.bool)
