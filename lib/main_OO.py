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

class MesoLoop():

    def __init__(self):

        

def initialize_camera():

    # stuff 
    pass

def populate_queues(camera, x0, y0, x1, y1, exposure_time):

    global buffer
    global sync
    global save_queue

    while sync is 1:

        buffer = camera.get_image(x0, y0, x1, y1)
        
        save_queue.append(buffer)

    camera.close()

def output_control(w, h, threshold):

    global buffer
    global sync

    output_frame = np.zeros((h,w,3))

    while sync is 1:

        input_frame = np.asarray(buffer).reshape(h, w)
        input_frame.byteswap(True)

        output_frame[:,:,0] = controller.BangBang(input_frame.astype(np.uint8, copy=False), threshold)
        # cv2.namedWindow('Control Output', cv2.WINDOW_AUTOSIZE) 
        cv2.imshow('Control Output', output_frame)
            
        if cv2.waitKey(1) == 27:
            sync = 0

    # close windows 
    cv2.destroyAllWindows()

def preview_frame(w, h):

    global buffer 
    global sync

    # what I want is something like:
    # if preview_thread.isAlive(): OR if dry_run_mode: 
        # do everything normally, pointing at 

    while sync is 1:

        input_frame = np.asarray(buffer).reshape(h, w)
        input_frame.byteswap(True)
        input_frame = input_frame.astype(np.uint8, copy=False)
        # cv2.namedWindow('Preview', cv2.WINDOW_AUTOSIZE) 
        cv2.imshow('Preview', input_frame)

        if cv2.waitKey(1) == 27:
            sync = 0

    # close windows
    cv2.destroyAllWindows()


def pop_images():

    global save_queue
    global sync

    # pops frames out of the queue one by one without saving
    while True:
        if save_queue:
            save_queue.popleft()
        else:
            print('queue is empty! length = ', len(save_queue))
            
            break


def write_images_to_disk(image_folder_path):

    global save_queue

    image_path = image_folder_path + 'images.npy'

    if os.path.exists(image_path):
        raise ValueError('This file already exists! Designate new .npy filename.')

    # make the folder path if it doesn't exist
    pathlib.Path(image_folder_path).mkdir(parents=True, exist_ok=True)

    # open a file for saving 
    with open(image_path, 'ab') as f:

        while True:

            # if the queue is not empty
            if save_queue:
                # grab the most recent buffer 
                oldest_buffer = save_queue.popleft()
                oldest_buffer = np.asarray(oldest_buffer).byteswap(True)
                np.save(f, oldest_buffer.astype(np.uint8, copy=False))

            # if the queue is empty
            else:
                print('queue is empty! length = ', len(save_queue))
                break         


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

    save_queue = deque([buffer])

    sync = 1
    view_lock = Lock()

    threads = []

    populate_thread = Thread(target=populate_queues, args=(camera, *roi_tuple, exposure_time))
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