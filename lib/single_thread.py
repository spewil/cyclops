# -*- coding: utf-8 -*-

import os
import time
import datetime

import cv2
import numpy as np
import ctypes
import pathlib
import tifffile as tiff

from lib import pco_camera
from lib import FPS

MAX_CAM_X_RES = 2560
MAX_CAM_Y_RES = 2160
CAM_X_ROI_STEP = 160
CAM_Y_ROI_STEP = 1

CV_ESC_KEY = 27

FPS_BOT = FPS.FPS()
class ColorControlError(Exception):
    pass

def convert_npy_to_tiff(npy_file, w, h):
    filename = npy_file
    out_filename = os.path.splitext(npy_file)[0]+'.tiff'
    idx = 1
    with open(filename, 'rb') as f_in:
        while True:
            try:
                frame = np.load(f_in).reshape(h, w)
                tiff.imsave(os.path.join(os.path.abspath(os.path.join(filename, os.pardir)),out_filename) , frame, append=True)
                # print("frame:", idx)
                idx += 1
            # when we run out of loads
            except IOError:
                print("Conversion complete.")
                break

def compute_roi(x0, x1, h, binning):

    max_binned_width = MAX_CAM_X_RES // binning
    max_binned_height = MAX_CAM_Y_RES // binning

    if x1 - x0 > max_binned_width:
        raise ColorControlError("ROI width must be < ",max_binned_width)
    elif h > max_binned_height:
        raise ColorControlError("ROI height must be < ",max_binned_height)
    elif x1 <= x0:
        raise ColorControlError("ROI must have x1 > x0")
    elif x1-x0 < CAM_X_ROI_STEP:
        raise ColorControlError("Width must be greater than {}".format(CAM_X_ROI_STEP))

    # Ensure coords are bounded properly
    x0 = max(0, x0 - x0 % CAM_X_ROI_STEP) + 1
    x1 = min(max_binned_width, x1 + CAM_X_ROI_STEP - x1 % CAM_X_ROI_STEP)

    # make h even
    if h % 2 is not 0:
        h += 1

    # compute the y coords (must be symmetric for pco.edge)
    h_2 = h // 2

    half_y_max = max_binned_height // 2
    y0 = half_y_max - h_2 + 1
    y1 = half_y_max + h_2

    return x0, y0, x1, y1

if __name__ == '__main__':

    frame_rate_mHz = int(10e3)
    exposure_time_ns = int(1)
    threshold = 100.
    binning = 2

    w = (MAX_CAM_X_RES // binning) // 2
    h = (MAX_CAM_Y_RES // binning) // 2
    roi_tuple = compute_roi(0, w, h, binning)
    print("computed roi: ", roi_tuple)

    save = True
    display = True
    process = True

    if save:
        image_name = str(datetime.datetime.now().time().strftime("%H_%M_%S"))+'.npy'
        image_folder = str(datetime.date.today())
        folder_path = os.path.join(os.path.normpath('C:/Users/Kelly_group01/Documents/'), image_folder)
        image_path = os.path.join(os.path.normpath('C:/Users/Kelly_group01/Documents/'), image_folder, image_name)
        # save path
        if os.path.exists(image_path):
            raise ValueError('File {} already exists in this directory!'
                             'Designate new .npy filename.'.format(image_path))

        # make the folder if it doesn't exist
        pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)

    # compute roi from

    # set up camera
    camera = pco_camera.Camera(frame_rate_mHz, exposure_time_ns, binning, binning, *roi_tuple)

    cv2.namedWindow("Preview")
    cv2.namedWindow("Control")

    # start recording
    camera.start_record()
    # buffers are now allocated

    # add to queue in a loop
    idx = 1
    times = []
    if save:
        file_buffer =  open(image_path, 'ab')
    FPS_BOT.start()
    for i in range(500):

        # convert and grab
        array = camera.get_latest_array()

        t1 = time.time()
        if display:
            if idx % 5 == 0:
                cv2.imshow('Preview', array)
                if cv2.waitKey(1) is CV_ESC_KEY:
                    break

        if process:
            # use ROI box here -- control[roi_y1:roi_y2, roi_x1:roi_x2]
            control = 255*((array >= threshold).astype(float))
            # transform
            cv2.imshow('Control', control)
            if cv2.waitKey(1) is CV_ESC_KEY:
                break

        if save:
            np.save(file_buffer, array)

        t2 = time.time()
        times.append(t2-t1)

        idx += 1

        FPS_BOT.update()
    FPS_BOT.stop()
    camera.close()
    cv2.destroyAllWindows()
    print("Frames per second over %d frames: %6.2f" % (idx-1, FPS_BOT.fps()))

    print("mean time of work: ",np.mean(times))

    if save:
        file_buffer.close()
        print("converting to tiff... ")
        convert_npy_to_tiff(image_path, w, h)