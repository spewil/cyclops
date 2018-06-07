import numpy as np
import pco_camera
import ctypes
import tifffile as tiff
import time 
from datetime import datetime
import os.path

from tools import compute_ROI

x0 = 0
x1 = 2560
h = 2160
exposure_time = 15 # milliseconds

roi_tuple = compute_ROI(x0,x1,h)

w = roi_tuple[2] - roi_tuple[0] + 1

camera = pco_camera.camera(roi_tuple, exposure_time)
buffer = (ctypes.c_uint16 * (w*h))()

# let the camera load 
time.sleep(10)

filename = 'image.npy'

# if this file exists, it will just be appended!
if os.path.exists(filename):
    raise ValueError('This file already exists!')

with open(filename, 'ab') as f:

    for i in range(100):

        buffer = camera.get_image(*roi_tuple)
        oldest_buffer = np.asarray(buffer).byteswap(True)
        oldest_buffer = oldest_buffer.astype(np.uint8, copy=False)
        np.save(f, oldest_buffer)

camera.close()

# frames = []
with open(filename, 'rb') as f_in:

    while True:

        try: 
            frame = np.load(f_in).reshape(h,w)
            # frames.append(frame)
            tiff.imsave('images.tiff', frame, append=True)

        # when we run out of loads
        except IOError:
            break
    # save a list of images 
    # tiff.imsave('images.tiff', np.array(frames))
