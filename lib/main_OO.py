# -*- coding: utf-8 -*-

import ctypes
from threading import Thread
import cv2 
import numpy as np
import pathlib
import time 
from collections import deque
import os 

import pco_camera
import controller 

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        # thread.start()
        return thread
    # function handle
    return wrapper

def compute_ROI(x0, x1, h):

    if x1 <= x0:
        raise Error("ROI must have x1 > x0")
    elif x1-x0 < 160:
        raise Error("Width must be greater than 160")

    # Ensure coords are bounded properly
    x0 = max(0, x0 - x0%160) + 1 
    x1 = min(2560, x1 + 160 - x1%160)

    # make h even 
    if h%2 is not 0:
        h += 1

    # compute the y coords (must be symmetric for pco.edge)
    h_2 = h // 2

    # height must be even, minimum is 16 
    # x values are multiples of 160, minimum is 160

    half_y_max = 2160 // 2
    y0 = half_y_max - h_2 + 1
    y1 = half_y_max + h_2

    return (x0,y0,x1,y1)

class Cyclops():

    # initialize the camera 
    def __init__(self, threshold, x0, x1, h, frame_rate, exposure_time, image_path=None):


        self.roi_tuple = compute_ROI(x0,x1,h)
        print('Desired ROI: ', self.roi_tuple)

        self.w = self.roi_tuple[2] - self.roi_tuple[0] + 1
        self.h = h 

        self.threshold = threshold

        # change this to combine pco_camera
        self.camera = pco_camera.camera(frame_rate, exposure_time, *self.roi_tuple)

        self.buffer = (ctypes.c_uint16 * (self.w*self.h))()
        self.sync = 1

        # call the threads from here to start them 
        self.threads  = []

        # set up threads
        # parse kwargs 
        if image_path is not None:

            self.save = True

            self.image_path = image_path
            self.image_folder, self.image_name = os.path.split(os.path.abspath(self.image_path))

            if os.path.exists(image_path):
                sync = 0
                raise ValueError('This file already exists in this directory! Designate new .npy filename.')

            # make the folder if it doesn't exist
            pathlib.Path(self.image_folder).mkdir(parents=True, exist_ok=True)

            self.save_queue = deque([self.buffer])

            w = self.write_images_to_disk()
            self.threads.append(w)

        else:
            self.save = False

        self.control_queue = deque([self.buffer], maxlen=1)
        self.preview_queue = deque([self.buffer], maxlen=1)

        a = self.append_queues()
        self.threads.append(a)

        c = self.output_control(self.threshold)
        self.threads.append(c)

        p = self.preview_frame()
        self.threads.append(p)

        for thread in self.threads:
            thread.start()        
        # finish 
        for thread in self.threads:
            thread.join()

    @threaded
    def append_queues(self):

        while self.sync is 1:

            self.buffer = self.camera.get_image(*self.roi_tuple)

            # print('appended buffer id: %i' %id(self.buffer))

            # artificially lower framerate 
            time.sleep(0.02)
            if self.save:
                self.save_queue.append(self.buffer)

            self.control_queue.append(self.buffer)
            self.preview_queue.append(self.buffer)

        self.camera.close()

    @threaded
    def output_control(self, threshold):

        output_frame = np.zeros((self.h,self.w,3))
        
        while True:

            if self.control_queue:

                control_frame = self.buffer
                # print('control buffer id: %i' %id(control_frame))

                input_frame = np.asarray(self.buffer).reshape(self.h, self.w)
                input_frame.byteswap(True)

                output_frame[:,:,0] = controller.BangBang(input_frame.astype(np.uint8, copy=False), threshold)
                cv2.imshow('Control Output', output_frame)
                    
                if cv2.waitKey(1) == 27:
                    self.sync = 0
                    break

        # close windows 
        cv2.destroyAllWindows()

    @threaded
    def preview_frame(self):

        while True:

            if self.preview_queue:

                # copy this so it doesn't interfere with the control
                preview_frame = (ctypes.c_uint16 * (self.w*self.h)).from_buffer_copy() #self.preview_queue.pop()
                # print('previewed buffer id: %i' %id(preview_frame))

                input_frame = np.array(preview_frame).reshape(self.h, self.w)
                input_frame.byteswap(True)

                input_frame = input_frame.astype(np.uint8, copy=False)
                cv2.imshow('Preview', input_frame)

                if cv2.waitKey(1) == 27:
                    self.sync = 0
                    break

        # close windows
        cv2.destroyAllWindows()

    @threaded
    def write_images_to_disk(self):

        # open a file for saving 
        with open(self.image_path, 'ab') as f:

            while True:

                # if the queue is not empty
                if self.save_queue:

                    print('Saving an image...')

                    # grab the most recent buffer 
                    oldest_buffer = self.save_queue.popleft()
                    oldest_buffer = np.asarray(oldest_buffer).byteswap(True)
                    np.save(f, oldest_buffer.astype(np.uint8, copy=False))

                # if the queue is empty and experiment no longer running
                if not self.save_queue and not self.sync:
                    print('Save queue is empty! Length = ', len(self.save_queue))
                    break

if __name__ == '__main__':

    # user info 
    x0 = 0
    x1 = 500
    h = 500

    exposure_time = int(1e7)# nanosec
    frame_rate = int(1e4) # milliHz
    threshold = 100.

    image_name = 'test_image.npy'
    folder_name = '4_26' #input('Enter experiment name: ')
    image_path = 'C:/Users/Kelly_group01/Documents/'+folder_name+'/'+image_name

    # def __init__(self, threshold, x0, x1, h, frame_rate, exposure_time, image_path=None):
    experiment = Cyclops(threshold, x0, x1, h, frame_rate, exposure_time, image_path=image_path)