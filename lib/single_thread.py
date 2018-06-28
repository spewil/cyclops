# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import json

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import pathlib
import tifffile as tiff
import multiprocessing as mp

from lib import pco_camera
from lib import FPS
from lib.transform_calculator import TransformCalculator
from lib.transform_calculator import PolygonSelector
from lib import raster

# ============================================================================

MAX_CAM_X_RES = 2560
MAX_CAM_Y_RES = 2160
CAM_X_ROI_STEP = 160
CAM_Y_ROI_STEP = 1
CV_ESC_KEY = 27
CV_ENT_KEY = 13
CV_d_KEY = 100
FPS_BOT = FPS.FPS()

# ============================================================================

class ColorControlError(Exception):
    pass

class CameraSetupError(Exception):
    pass

def convert_npy_to_tiff(npy_file, w, h):
    filename = npy_file
    out_filename = os.path.splitext(npy_file)[0] + '.tiff'
    idx = 1
    with open(filename, 'rb') as f_in:
        while True:
            try:
                frame = np.load(f_in).reshape(h, w)
                tiff.imsave(os.path.join(os.path.abspath(os.path.join(filename, os.pardir)), out_filename), frame, append=True)
                idx += 1
            except IOError:
                print("Conversion complete.")
                break

def compute_roi(x0, x1, h, binning):
    max_binned_width = MAX_CAM_X_RES // binning
    max_binned_height = MAX_CAM_Y_RES // binning

    if x1 - x0 > max_binned_width:
        raise ColorControlError("ROI width must be < ", max_binned_width)
    elif h > max_binned_height:
        raise ColorControlError("ROI height must be < ", max_binned_height)
    elif x1 <= x0:
        raise ColorControlError("ROI must have x1 > x0")
    elif x1 - x0 < CAM_X_ROI_STEP:
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

def roi_test():
    array = np.zeros((500,500))
    cv2.namedWindow("ROI Selection")
    rectangle = cv2.selectROI("ROI Selection", array, False, False)
    cv2.destroyAllWindows()
    print("soft ROI set:", rectangle)
    x, y, w, h = rectangle
    mask = np.zeros(array.shape)
    mask[y:y+h, x:x+w] = 1
    array[mask.astype(bool)] = 1
    while True:
        cv2.imshow("blah", array)
        if cv2.waitKey(1) is CV_ENT_KEY:
            break

def select_rectangular_roi(camera):
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
    mask = np.zeros(array.shape)
    mask[y:y+h, x:x+w] = 1
    return mask.astype(np.bool)

def restart_camera(camera, settings_dict):
    camera.close()
    return pco_camera.Camera(settings_dict['frame_rate_mHz'], settings_dict['exposure_time_ns'], settings_dict['binning'], settings_dict['binning'], *settings_dict['roi_tuple'])

def populate_settings_dict():
    settings_dict = {}
    settings_dict['frame_rate_mHz'] = int(int(input("Enter framerate in Hertz."))*1e3)
    settings_dict['exposure_time_ns'] = int(int(input("Enter exposure time in milliseconds."))*1e6)
    settings_dict['binning'] = int(input("Enter binning (1, 2 or 4 are nice)."))
    return settings_dict

def run():
    # pass these flags as CLI args?
    transform = False
    display = True
    save = True

    # file base name
    experiment_name = str(datetime.datetime.now().time().strftime("%H_%M_%S"))
    # file folder name
    experiment_folder = str(datetime.date.today())
    # absolute path to the folder
    folder_path = os.path.join(os.path.normpath('C:/Users/Kelly_group01/Documents'), experiment_folder)
    # absolute path to the base name
    experiment_path = os.path.join(os.path.normpath('C:/Users/Kelly_group01/Documents'), experiment_folder, experiment_name)
    pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)

    settings_path = experiment_path + '.json'
    if os.path.exists(settings_path):
        previous_settings = input(
            "There is a settings file in this folder. Would you like to reuse your last saved settings? y/n")
        if previous_settings is 'n':
            load_settings = input("Would you like to load a settings file? y/n ")
            if load_settings is 'y':
                root = tk.Tk()
                root.attributes("-topmost", True)  # this also works
                root.lift()
                root.withdraw()
                file_path = filedialog.askopenfilename()
                try:
                    with open(file_path) as f:
                        settings_dict = json.load(f)
                except:
                    settings_dict = populate_settings_dict()
                root.destroy()
            elif load_settings is 'n':
                settings_dict = populate_settings_dict()
            else:
                raise CameraSetupError("You must enter y/n.")
        elif previous_settings is 'y':
            with open(settings_path) as f:
                settings_dict = json.load(f)
        else:
            raise CameraSetupError("You must enter 'y' or 'n'.")
    else:
        load_settings = input("No previous settings found. Would you like to choose a settings file? y/n ")
        if load_settings is 'y':
            root = tk.Tk()
            # root.attributes("-topmost", True)
            root.lift()
            root.withdraw()
            file_path = filedialog.askopenfilename()
            try:
                with open(file_path) as f:
                    settings_dict = json.load(f)
            except:
                settings_dict = populate_settings_dict()
        elif load_settings is 'n':
            settings_dict = populate_settings_dict()
        else:
            raise CameraSetupError("You must enter y/n.")

    if save:
        image_path = experiment_path + '.npy'
        print("Image will be saved to: ", image_path)

    '''
    Hard ROI selection
    This should be hardcoded and, if necessary, played with when the camera is mounted, etc. 
    Right now, compute_roi puts the desired size as close to the center of the image as it can 
    at the mercy of the X and Y step sizes (160 and 2) and symmetry requirements. 
    '''
    w = (MAX_CAM_X_RES // settings_dict['binning']) // 2
    h = (MAX_CAM_Y_RES // settings_dict['binning']) // 2
    roi_tuple = compute_roi(0, w, h, settings_dict['binning'])
    x0, y0, x1, y1 = roi_tuple
    w = x1 - x0 + 1
    h = y1 - y0 + 1
    print("computed roi: ", roi_tuple)
    settings_dict['roi_tuple'] = roi_tuple

    camera = pco_camera.Camera(settings_dict['frame_rate_mHz'], settings_dict['exposure_time_ns'], settings_dict['binning'], settings_dict['binning'], *settings_dict['roi_tuple'])

    if transform:
        print('calculating transform...')
        transformer = TransformCalculator(camera)
        M = np.array(transformer.transform)
        camera = restart_camera(camera, settings_dict)

    ##### soft ROI selection ######
    set_ROI = input("would you like to set a soft ROI? y/n")
    if set_ROI is 'y':
        soft_ROI = True
        roi_type = input("Polygonal or Rectangular ROI? p/r")
        if roi_type == 'p':
            selector = PolygonSelector(camera)
            mask = selector.mask
            camera = restart_camera(camera, settings_dict)
        elif roi_type == 'r':
            mask = select_rectangular_roi(camera)
            camera = restart_camera(camera, settings_dict)
        else:
            raise CameraSetupError("ROI type must be 'p' or 'r'.")
    elif set_ROI is 'n':
        soft_ROI = False
    else:
        raise CameraSetupError("You must enter 'y' or 'n'.")

    ##### control selection #####
    control_type = input("Would you like output to be closed-loop, open-loop, or neither? Enter c/o/n")
    if control_type is 'c':
        control = np.zeros((h, w))
        threshold = int(input("Enter the control threshold (100 is a good place to start)."))
        settings_dict['threshold'] = threshold
        settings_dict['control_type'] = control_type
        cv2.namedWindow("Control")
    elif control_type is 'o':
        rows = int(input("Enter number of rows."))
        cols = int(input("Enter number of columns."))
        duration = int(input("Enter duration of grid elements in seconds."))
        interval = int(input("Enter interval between grid elements in seconds."))
        settings_dict['control_type'] = control_type
        settings_dict['rows'] = rows
        settings_dict['cols'] = cols
        settings_dict['duration'] = duration
        settings_dict['interval'] = interval
        mp.set_start_method('spawn')
        p = mp.Process(target=raster.show_raster, args=(h, w, rows, cols, duration, interval))
        p.start()
        p.join()
    elif control_type is 'n':
        pass
    else:
        raise CameraSetupError("You must enter 'c', 'o', or 'n'.")

    if display:
        cv2.namedWindow("Preview")

    # how many images per gigabyte?
    max_saved_frames = int(1e9) // int(w*h)
    print('frames per file: ',max_saved_frames)
    settings_dict['frames_per_file'] = max_saved_frames

    idx = 1
    file_number = 1
    if save:
        file_buffer = open(image_path, 'ab')
    record = True
    camera.start_record()
    FPS_BOT.start()
    while record is True:
        array = camera.get_latest_array()

        if display:
            if idx % 10 == 0:
                cv2.imshow("Preview", array)
                if cv2.waitKey(1) is CV_ENT_KEY:
                    display = False

        if control_type is 'c':
            if soft_ROI:
                # retval, dst = cv.threshold(src, thresh, maxval, type[, dst])
                control[mask] = 255 * ((array[mask] >= threshold).astype(float))
            else:
                # retval, dst = cv.threshold(src, thresh, maxval, type[, dst])
                control = 255 * ((array >= threshold).astype(float))

            if transform:
                cv2.imshow("Control", cv2.warpAffine(control, M, (w, h)))
                if cv2.waitKey(1) is CV_ENT_KEY:
                    record = False
            else:
                cv2.imshow("Control", control)
                if cv2.waitKey(1) is CV_ENT_KEY:
                    record = False

        if save:
            if idx > max_saved_frames:
                file_number += 1
                file_buffer.close()
                file_buffer = open(image_path + '_' + str(file_number), 'ab')
                idx = 1
            np.save(file_buffer, array)

        idx += 1
        FPS_BOT.update()

    if control_type is 'o':
        p.join()

    FPS_BOT.stop()
    camera.close()
    cv2.destroyAllWindows()
    print("Frames per second over %d frames: %6.2f" % (idx - 1, FPS_BOT.fps()))

    # save current settings
    with open(os.path.join(os.path.normpath('C:/Users/Kelly_group01/Documents'), experiment_folder, 'settings.json'), 'w') as f:
        json.dump(settings_dict, f)
    # save unique settings to this experiment
    with open(experiment_path+'.json', 'w') as f:
        json.dump(settings_dict, f)

    if save:
        file_buffer.close()
        print("converting to tiff... ")
        convert_npy_to_tiff(image_path, w, h)


if __name__ == '__main__':
    run()
