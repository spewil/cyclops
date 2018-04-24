# -*- coding: utf-8 -*-

import ctypes
from threading import Thread, Lock
import cv2 
import numpy as np
import pathlib
import time 
from collections import deque
import os 

import pco_camera
import controller 
from tools import compute_ROI

def populate_queue(camera, x0, y0, x1, y1, exposure_time):

    global queue
    global sync 

    while sync is 1:

        # slow this down as a lower framerate hack
        time.sleep(.01) 

        queue.append(camera.get_image(x0, y0, x1, y1))
 
    camera.close()

def preview_frame(w, h):

    global queue 
    global sync
    global view_lock

    while sync is 1:

        time.sleep(1)

        ###################
        view_lock.acquire()         
        ###################

        np_array = np.asarray(queue[-1]).reshape(h, w)
        np_array.byteswap(True)
        np_array = np_array.astype(np.uint8, copy=False)

        cv2.imshow('Preview', np_array)

        if cv2.waitKey(1) == 27:
            sync = 0
        
        ###################
        view_lock.release()
        ###################

    # close windows
    cv2.destroyAllWindows()

def pop_images():

    global queue
    global sync

    while sync is 1:
        
        if len(queue) > 5:
            queue.popleft()

def write_images_to_disk(image_folder_path):

    global queue
    global sync

    image_path = image_folder_path + 'images.npy'

    if os.path.exists(image_path):
        raise ValueError('This file already exists! Designate new .npy filename.')

    # make the folder path if it doesn't exist
    pathlib.Path(image_folder_path).mkdir(parents=True, exist_ok=True)

    # open a file for saving 
    with open(image_path, 'ab') as f:

        while True:

            # if populate is alive 
            if sync is 1: 
                # keep the queue at least five buffer frames
                if len(queue) > 5:
                    # grab the most recent buffer 
                    oldest_buffer = queue.popleft()
                    oldest_buffer = np.asarray(oldest_buffer).byteswap(True)
                    np.save(f, oldest_buffer.astype(np.uint8, copy=False))

            # if populate is dead 
            else:
                # try to empty the queue
                if len(queue) > 0:
                    # grab the most recent buffer 
                    oldest_buffer = queue.popleft()
                    oldest_buffer = np.asarray(oldest_buffer).byteswap(True)
                    np.save(f, oldest_buffer.astype(np.uint8, copy=False))

                # if the queue is empty
                else:
                    print('queue is of length: ', len(queue))
                    break            

def output_control(w, h, threshold):

    global queue
    global sync
    global view_lock

    output = np.zeros((h,w,3))
    while sync is 1:

        ###################
        view_lock.acquire()
        ###################

        np_array = np.asarray(queue[-1]).reshape(h, w)
        np_array.byteswap(True)

        output[:,:,0] = controller.BangBang(np_array.astype(np.uint8, copy=False), threshold) 
        cv2.imshow('Control Output', output)
        if cv2.waitKey(1) == 27:
            sync = 0

        ###################
        view_lock.release()
        ###################

    # close windows 
    cv2.destroyAllWindows()


if __name__ == '__main__':

    # user info 
    x0 = 0
    x1 = 2560
    h = 2160
    exposure_time = 15 # milliseconds

    threshold = 100.

    experiment_name = '4_24' #input('Enter experiment name: ')
    image_folder_path = 'C:/Users/Kelly_group01/Documents/'+experiment_name+'/'
    
    save = 0
    preview = 1
    show_control = 1

    roi_tuple = compute_ROI(x0,x1,h)
    w = roi_tuple[2] - roi_tuple[0] + 1

    print(roi_tuple)

    # make the camera 
    camera = pco_camera.camera(roi_tuple, exposure_time)

    # create buffer
    buffer = (ctypes.c_uint16 * (w*h))()
    queue = deque([buffer])

    sync = 1
    view_lock = Lock()

    threads = []

    populate_thread = Thread(target=populate_queue, args=(camera, *roi_tuple, exposure_time))
    threads.append(populate_thread)

    if preview:
        preview_thread = Thread(target=preview_frame, args=(w, h))
        threads.append(preview_thread)

    if save:
        consumer_thread = Thread(target=write_images_to_disk, args=(image_folder_path,))
        threads.append(consumer_thread)
    else:
        consumer_thread = Thread(target=pop_images)
        threads.append(consumer_thread)       

    if show_control:
        output_thread = Thread(target=output_control, args=(w, h, threshold))
        threads.append(output_thread)

    [thread.start() for thread in threads]

    [thread.join() for thread in threads]