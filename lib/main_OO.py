# -*- coding: utf-8 -*-

import os
import sys
import time

import ctypes
import threading
from threading import Thread
from collections import deque

import pathlib

import cv2 
import numpy as np

try:
    import pco_camera
    import controller
except ImportError:
    from lib import pco_camera
    from lib import controller

MAX_CAM_X_RES = 2560
MAX_CAM_Y_RES = 2160
CAM_X_ROI_STEP = 160
CV_ESC_KEY = 27


class ColorControlError(Exception):
    pass


class ColorControlValueError(ColorControlError, ValueError):
    pass


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        # thread.start()
        return thread
    # function handle
    return wrapper


def compute_roi(x0, x1, h):
    if x1 <= x0:
        raise ColorControlError("ROI must have x1 > x0")
    elif x1-x0 < CAM_X_ROI_STEP:
        raise ColorControlError("Width must be greater than {}".format(CAM_X_ROI_STEP))

    # Ensure coords are bounded properly
    x0 = max(0, x0 - x0 % CAM_X_ROI_STEP) + 1
    x1 = min(MAX_CAM_X_RES, x1 + CAM_X_ROI_STEP - x1 % CAM_X_ROI_STEP)

    # make h even 
    if h % 2 is not 0:
        h += 1

    # compute the y coords (must be symmetric for pco.edge)
    h_2 = h // 2

    # height must be even, minimum is 16 
    # x values are multiples of 160, minimum is 160

    half_y_max = MAX_CAM_Y_RES // 2
    y0 = half_y_max - h_2 + 1
    y1 = half_y_max + h_2

    return x0, y0, x1, y1


class Cyclops(object):
    FRAME_QUEUE_LOCK = threading.Lock()

    def __init__(self, threshold, x0, x1, h, frame_rate, exposure_time, image_path=None):
        """

        :param float threshold:
        :param int x0:
        :param int x1:
        :param int h:
        :param int frame_rate:
        :param int exposure_time:
        :param str image_path:
        """
        # initialize the camera
        self.roi_tuple = compute_roi(x0, x1, h)
        if __debug__:
            print('Desired ROI: ', self.roi_tuple)

        self.w = self.roi_tuple[2] - self.roi_tuple[0] + 1
        self.h = h 

        self.threshold = threshold

        # change this to combine pco_camera
        x_binning = 2
        y_binning = 2

        try:
            self.camera = pco_camera.camera(frame_rate, exposure_time, x_binning, y_binning, *self.roi_tuple)
        except pco_camera.PcoCamError as err:
            sys.exit('Could not start camera, the following error occurred: {}'.format(err))

        self.buffer = (ctypes.c_uint16 * (self.w*self.h))()
        self.sync = 1

        # call the threads from here to start them 
        self.threads = []

        # set up threads
        # parse kwargs 
        # if image_path is not None:
        #     self.save = True
        #
        #     self.image_path = image_path
        #     self.image_folder, self.image_name = os.path.split(os.path.abspath(self.image_path))
        #     if os.path.exists(image_path):
        #         self.sync = False
        #         raise ColorControlValueError('File {} already exists in this directory!'
        #                                      'Designate new .npy filename.'.format(image_path))
        #
        #     # make the folder if it doesn't exist
        #     pathlib.Path(self.image_folder).mkdir(parents=True, exist_ok=True)
        #
        #     self.save_queue = deque([self.buffer])
        #
        #     w = self.write_images_to_disk()
        #     self.threads.append(w)
        #
        # else:
        #     self.save = False

        # DEBUG:
        self.save = False

        self.preview_frame = (ctypes.c_uint16 * (self.w * self.h)).from_buffer_copy(self.buffer)
        self.new_frame = False

        self.control_queue = deque([self.buffer], maxlen=1)
        self.preview_queue = deque([self.buffer], maxlen=1)

        a = self.append_frame_to_queue()
        self.threads.append(a)

        p = self.display_raw_frame()
        self.threads.append(p)

        # c = self.display_processed_frame(self.threshold)
        # self.threads.append(c)

        for thread in self.threads:
            thread.start()

        for thread in self.threads:  # finish
            thread.join()

    @threaded
    def append_frame_to_queue(self):
        while self.sync:
            self.buffer = self.camera.get_image(*self.roi_tuple)
            # self.preview_frame = (ctypes.c_uint16 * (self.w * self.h)).from_buffer_copy(self.buffer)
            self.new_frame = True
            # time.sleep(0.02)  # artificially lower framerate
            if self.save:
                self.save_queue.append(self.buffer)
        self.camera.close()

    # @threaded
    # def display_processed_frame(self, threshold):
    #     output_frame = np.zeros((self.h, self.w, 3))
    #
    #     while True:
    #         if self.control_queue:
    #             # total loop time: 0.15
    #
    #             # looks at the actual buffer
    #             with Cyclops.FRAME_QUEUE_LOCK:
    #                 input_frame = np.asarray(self.buffer).reshape(self.h, self.w)
    #             input_frame.byteswap(True)
    #
    #             output_frame[:, :, 0] = controller.BangBang(input_frame.astype(np.uint8, copy=False), threshold)
    #
    #             cv2.imshow('Control Output', output_frame)
    #             if cv2.waitKey(1) == CV_ESC_KEY:
    #                 self.sync = 0
    #                 break
    #     cv2.destroyAllWindows()

    @threaded
    def display_raw_frame(self):
        idx = 0
        while True:

            # if self.preview_queue:
            if self.new_frame:
                self.new_frame = False
                # total loop time: 0.05
                # time for buffer copy: 0.016

                # # copy this so it doesn't interfere with the control
                # with Cyclops.FRAME_QUEUE_LOCK:
                #     preview_frame = (ctypes.c_uint16 * (self.w*self.h)).from_buffer_copy(self.buffer)
                # # print('previewed buffer id: %i' %id(preview_frame))

                # input_frame = np.asarray(preview_frame, dtype=np.uint8).reshape(self.h, self.w)
                # preview_frame = (ctypes.c_uint16 * (self.w*self.h)).from_buffer_copy(self.buffer)
                input_frame = np.array(self.buffer).reshape(self.h, self.w)
                input_frame = input_frame.astype(np.uint8, copy=False)
                input_frame.byteswap(inplace=True)

                # input_frame = input_frame.astype(np.uint8, copy=False)

                cv2.putText(input_frame, 'Frame: {}'.format(idx), (1000, 1000),
                                          cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
                idx += 1
                cv2.imshow('Preview', input_frame)
                if cv2.waitKey(1) == CV_ESC_KEY:
                    self.sync = 0
                    break
        cv2.destroyAllWindows()

    @threaded
    def write_images_to_disk(self):
        with open(self.image_path, 'ab') as video_file_buffer:
            while True:
                if self.save_queue:  # if the queue is not empty
                    if __debug__:
                        print('Saving an image...')

                    # grab the most recent buffer 
                    save_frame = (ctypes.c_uint16 * (self.w * self.h)).from_buffer_copy(self.save_queue.popleft())
                    save_frame = np.asarray(save_frame).byteswap(True)
                    np.save(video_file_buffer, save_frame.astype(np.uint8, copy=False))

                # if the queue is empty and experiment no longer running
                if not self.save_queue and not self.sync:
                    print('Save queue is empty! Length = ', len(self.save_queue))
                    break


if __name__ == '__main__':

    # user info 
    x0 = 0
    x1 = MAX_CAM_X_RES
    h = MAX_CAM_Y_RES

    exposure_time_ns = int(1e7)
    frame_rate_mHz = int(1e4)
    threshold = 100.

    image_name = 'test_image.npy'
    folder_name = '4_26'  # input('Enter experiment name: ')
    image_path = os.path.join(os.path.normpath('C:/Users/Kelly_group01/Documents/'), folder_name, image_name)

    # def __init__(self, threshold, x0, x1, h, frame_rate, exposure_time, image_path=None):
    experiment = Cyclops(threshold, x0, x1, h, frame_rate_mHz, exposure_time_ns)  #, image_path=image_path)


