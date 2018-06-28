# -*- coding: utf-8 -*-

import cv2
import os
import time
import numpy as np
import pprint
from random import shuffle
import tkinter as tk
from tkinter import filedialog
CV_ENT_KEY = 13

def print_os_info():
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def define_grid(size_data,shape_grid):
    '''
    :param size_data: Size/shape of incoming data.
    :param shape_grid: Size/shape of required output
    :return: list of lists of tuples (start_idx, stop_idx)

    Note that the leftover pixels are pushed to the end of every dimension as leftovers.
    This should only really matter when there are lots of leftoxer pixels, so not often.
    '''
    if len(size_data) is not len(shape_grid):
        raise Exception("Dimensions of data and grid must be equal.")

    indices = []
    # rows, cols, stacks...
    for size, shape in zip(size_data,shape_grid):
        extra_pxls = size % shape
        num_pxls = size // shape
        curr_indices = []
        for r in range(shape):
            if r is shape-1:
                curr_indices.append((r*num_pxls,(r+1)*num_pxls + extra_pxls))
            else:
                curr_indices.append((r*num_pxls,(r+1)*num_pxls))
        indices.append(curr_indices)
    return indices

def show_raster(height, width, rows, cols, duration, interval):
    if cols > width or rows > height:
        raise Exception("Too many rows or columns.")

    idxs = define_grid((height,width),(rows,cols))

    masks = []
    mask = np.zeros((height, width))
    for r in range(rows):
        for c in range(cols):
            mask[idxs[0][r][0]:idxs[0][r][1],idxs[1][c][0]:idxs[1][c][1]] = 1
            masks.append(mask.astype(np.bool))
            mask = np.zeros((height, width))

    # randomize the order of the masks
    mask_order = list(range(len(masks)))
    shuffle(mask_order)
    masks =[masks[k] for k in mask_order]

    # wait to make sure video is running
    # time.sleep(2)

    base = np.zeros((height, width))
    cv2.namedWindow("raster")
    for mask in masks:
        base[mask] = 255
        cv2.imshow("raster", base)
        if cv2.waitKey(int(duration*1000)) is CV_ENT_KEY:
            break
        time.sleep(interval)
        base[mask] = 0
    cv2.destroyAllWindows()

    return mask_order
