
import ctypes
import numpy as np
try:
    import pco_camera
except ImportError:
    from lib import pco_camera

class ColorControlError(Exception):
    pass

class ColorControlValueError(ColorControlError, ValueError):
    pass

MAX_CAM_X_RES = 2560
MAX_CAM_Y_RES = 2160
CAM_X_ROI_STEP = 160
CV_ESC_KEY = 27

def compute_roi(x0, x1, h):
    if x1 <= x0:
        raise ColorControlError("ROI must have x1 > x0")

    elif x1-x0 < CAM_X_ROI_STEP:
        raise ColorControlValueError("Width must be greater than {}".format(CAM_X_ROI_STEP))

    # Ensure coords are bo
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


x0 = 0
x1 = MAX_CAM_X_RES // 2
h = MAX_CAM_Y_RES // 2
w = x1 - x0 + 1

frame_rate_mHz = int(1e4)
exposure_time_ns = int(1e7)
threshold = 100.
x_binning = 2
y_binning =2
roi_tuple = compute_roi(x0, x1, h)

buffer = (ctypes.c_uint16 * (w * h))()
camera = pco_camera.camera(frame_rate_mHz, exposure_time_ns, x_binning, y_binning, *roi_tuple)

# run this two times
# for i in range(2):
#
#     # i think buffer has to be copied here in order to be saved
#
#     buffer = camera.get_image(*roi_tuple)  # <class '__main__.c_ushort_Array_{{w * h}}'>
#     print('object id of buffer: ',id(buffer))
#     print('type of buffer: ',type(buffer))
#     print('address of buffer: ',ctypes.addressof(buffer))
#     print('type of buffer element: ',type(buffer[0]))
#
#     new_buffer = buffer
#     print('object id of new buffer: ',id(new_buffer))
#     print('type of new buffer element: ',type(new_buffer[0]))
#     print('address of buffer: ',ctypes.addressof(new_buffer))
#
#     # to construct new memory block:
#     # new_pointer = ctypes.cast(ctype_structure, ctypes.POINTER({{type(ctype_structure)}}))
#
#     # turn this into a numpy array?
#     numpy_array_from_buffer = np.array(np.frombuffer(buffer, dtype=np.uint8))
#     # numpy_array_from_iterable = np.array(np.fromiter(buffer, dtype=np.uint8))