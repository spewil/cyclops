# https://stackoverflow.com/questions/37099262/drawing-filled-polygon-using-mouse-events-in-open-cv-using-python

# this is for the preprocessing steps

    # we ask if we want to complete the transform calculation
    # if not, load the transform.npy matrix into memory
        # if transform.npy doesn't exist-- return an error

# ============================================================================

import numpy as np
import cv2
from pathlib import Path
import time

# ============================================================================

CANVAS_SIZE = (600,800)
FINAL_LINE_COLOR = (255, 255, 255)
WORKING_LINE_COLOR = (127, 127, 127)

# ============================================================================

class TransformCalculator:
    def __init__(self, camera):
        self.camera = camera

        self.h = camera.img_height
        self.w = camera.img_width

        self.reference_frame = np.zeros((self.h,self.w))
        self.overlayed_frame = np.zeros((self.h,self.w))

        self.transform = None

        self.done = False # Flag signalling we're done
        self.current = (0, 0) # Current position, so we can draw the line-in-progress
        self.reference_points = [[100,100],[self.w//2,self.h-100],[self.w-100,100]]
        self.overlayed_points = []

        # ask if we want an affine or perspective transform here?

        transform_file = Path("transform.npy")
        if transform_file.is_file():
            with open("transform.npy", 'rb') as f_in:
                self.transform = np.load(f_in)
        else:
            self.transform = self.compute_transform()
            print('in preprocessing: ', self.transform)

    def on_mouse(self, event, x, y, flags, params):
        # Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)

        if self.done: # Nothing more to do
            return

        if event == cv2.EVENT_MOUSEMOVE:
            # update current mouse position
            self.current = (x, y)

        elif event == cv2.EVENT_LBUTTONDOWN:
            # Left click means adding a point at current position to the list of points
            print("Adding overlayed point #%d with position(%d,%d)" % (len(self.overlayed_points), x, y))
            self.overlayed_points.append([x, y])
            cv2.circle(self.overlayed_frame, (x, y), 5, (255, 255, 255), 5)
            if len(self.overlayed_points) == 3:
                print("All points chosen.")
                self.done = True

    def compute_transform(self):
        # open the two frames -- numpy arrays
        cv2.namedWindow("Reference")
        numbers = ['1', '2', '3']
        for number, pt in zip(numbers,self.reference_points):
            cv2.circle(self.reference_frame, (pt[0], pt[1]), 5, (255, 255, 255), 5)
            cv2.putText(self.reference_frame, number,(pt[0]-10, pt[1]-10), cv2.FONT_HERSHEY_PLAIN, 6, (255, 255, 255))
        cv2.imshow("Reference", self.reference_frame)

        cv2.namedWindow("Overlayed")
        cv2.imshow("Overlayed", self.overlayed_frame)
        cv2.setMouseCallback("Overlayed", self.on_mouse)

        while not self.done:
            time.sleep(.01)

            self.overlayed_frame = self.camera.get_image()
            self.overlayed_frame = np.asarray(self.overlayed_frame).reshape(self.h, self.w)
            self.overlayed_frame.byteswap(inplace=True)
            self.overlayed_frame = self.overlayed_frame.astype(np.uint8, copy=False)

            cv2.imshow("Reference", self.reference_frame)
            cv2.imshow("Overlayed", self.overlayed_frame)

            if cv2.waitKey(10) == 27 or self.done:
                self.done = True
        cv2.destroyAllWindows()

        print(self.reference_points)
        print(self.overlayed_points)

        return cv2.getAffineTransform(np.array(self.reference_points, dtype=np.float32), np.array(self.overlayed_points, dtype=np.float32))


class MaskCalculator:
    def __init__(self, display_frame):
        self.window_name = "Display" # Name for our window

        self.done = False # Flag signalling we're done
        self.current = (0, 0) # Current position, so we can draw the line-in-progress
        self.points = [] # List of points defining our polygon

    def run(self):
        # Let's create our working window and set a mouse callback to handle events
        cv2.namedWindow(self.window_name, flags=cv2.CV_WINDOW_AUTOSIZE)
        cv2.imshow(self.window_name, np.zeros(CANVAS_SIZE, np.uint8))
        cv2.waitKey(1)
        cv2.SetMouseCallback(self.window_name, self.on_mouse)

        while(not self.done):
            # This is our drawing loop, we just continuously draw new images
            # and show them in the named window
            canvas = np.zeros(CANVAS_SIZE, np.uint8)
            if (len(self.points) > 0):
                # Draw all the current polygon segments
                cv2.polylines(canvas, np.array([self.points]), False, FINAL_LINE_COLOR, 1)
                # And  also show what the current segment would look like
                cv2.line(canvas, self.points[-1], self.current, WORKING_LINE_COLOR)
            # Update the window
            cv2.imshow(self.window_name, canvas)
            # And wait 50ms before next iteration (this will pump window messages meanwhile)
            if cv2.waitKey(50) == 27: # ESC hit
                self.done = True

        # User finised entering the polygon points, so let's make the final drawing
        canvas = np.zeros(CANVAS_SIZE, np.uint8)
        # of a filled polygon
        if (len(self.points) > 0):
            cv2.fillPoly(canvas, np.array([self.points]), FINAL_LINE_COLOR)
        # And show it
        cv2.imshow(self.window_name, canvas)
        # Waiting for the user to press any key
        cv2.waitKey()

        cv2.destroyWindow(self.window_name)
        return canvas
