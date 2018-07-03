# -*- coding: utf-8 -*-

import win32event

import ctypes
import numpy as np
from collections import deque
from cffi import FFI

try:
    from lib import pco_sdk
except:
    import pco_sdk

MAX_CAM_X_RES = 2560
MAX_CAM_Y_RES = 2160
NUM_BUFFERS = 4
ffi = FFI()

# TODO:
# catch errors if something goes wrong (don't just print them)
# return verbose if 'de-bug' mode is on

class PcoCamError(Exception):
    pass

class BufferInfo(object):
    def __init__(self, num, pointer, address, event, size):
        self.idx = num
        self. pointer = pointer
        self.address = address
        self.event = event
        self.size = size

class Camera:
    __cam = pco_sdk.sdk()
    def __init__(self, frame_rate_mHz, exposure_time_ns, x_binning, y_binning, x0, y0, x1, y1):
        self.h = y1-y0+1
        self.w = x1-x0+1
        self.queue = deque([], maxlen=NUM_BUFFERS) # deque of BufferInfo objects
        self.buffers = []
        error = self.__cam.reset_lib()

        # TODO: catch errors with PcoCamError
        if error == 0:
            print("reset lib:", self.__cam.get_error_text(error))
            error = self.__cam.open_camera()
            print("open camera:", self.__cam.get_error_text(error))
            error = self.__cam.set_recording_state(0)
            print("set recording state:", self.__cam.get_error_text(error))
            error = self.__cam.reset_settings_to_default()
            print("reset settings to default:", self.__cam.get_error_text(error))

            # FRAMERATE
            error, ret = self.__cam.set_frame_rate(frame_rate_mHz, exposure_time_ns)
            print("set framerate: ", self.__cam.get_error_text(error))
            print("desired framerate_mHz: ",ret["frame rate mHz"])
            print("desired exposure_ns: ",ret["exposure time ns"])

            # TRIGGER MODE
            error = self.__cam.set_trigger_mode(0)
            print("set trigger mode:", self.__cam.get_error_text(error))

            # TIMESTAMPS
            mode = 'binary & ascii'
            error = self.__cam.set_timestamp_mode(mode)
            print("set timestamp mode: ",self.__cam.get_error_text(error))
            print("timestamp mode: ",mode)

            # BINNING
            error, ret = self.__cam.set_binning(x_binning, y_binning)
            print("set binning: ", self.__cam.get_error_text(error))
            print("desired x_binning: ", x_binning)
            print("desired y_binning: ", y_binning)

            # ROI
            error = self.__cam.set_roi(x0, y0, x1, y1)
            print("desired roi: ", x0, y0, x1, y1)
            print("set roi:", self.__cam.get_error_text(error))

            # TODO: check if current =/= desired
            error, ret = self.__cam.get_binning()
            print("get binning: ", self.__cam.get_error_text(error))
            print("current x_binning: ",ret["x_binning"])
            print("current y_binning: ",ret["y_binning"])
            error, ret = self.__cam.get_frame_rate()
            print("get framerate: ", self.__cam.get_error_text(error))
            print("current framerate_mHz: ",ret["frame rate mHz"])
            # print("current exposure_ns: ",ret["exposure time ns"])
            error, ret = self.__cam.get_roi()
            print("get roi: ", self.__cam.get_error_text(error))
            print("current roi:",ret["x0"],ret["y0"],ret["x1"],ret["y1"])

            # GET SIZES
            error, ret = self.__cam.get_sizes()
            print("get sizes: ", self.__cam.get_error_text(error))
            print("X Resolution Actual: ", ret["xResAct"])
            print("Y Resolution Actual: ", ret["yResAct"])
            print("X Resolution Maximum: ", ret["xResMax"])
            print("Y Resolution Maximum: ", ret["yResMax"])
            self.xRes = ret["xResAct"]
            self.yRes = ret["yResAct"]
            self.xResMax = ret["xResMax"]
            self.yResMax = ret["yResMax"]

            # SET PARAMS
            error = self.__cam.set_image_parameters(self.xRes,self.yRes)
            print("set image parameters:", self.__cam.get_error_text(error))
            error = self.__cam.set_transfer_parameters_auto()
            print("set transfer parameters auto:", self.__cam.get_error_text(error))

            # ARM AND RECORDER
            error = self.__cam.arm()
            print("arm:", self.__cam.get_error_text(error))

    def add_buffer_to_queue(self, buf):
        error = self.__cam.add_buffer(buf.idx, self.xRes, self.yRes)
        if error != 0:
            self.stop_record()
            self.close()
            raise PcoCamError("error adding buffer: ", self.__cam.get_error_text(error))

        self.queue.append(buf) # move buffer to the "end" of our queue

    def start_record(self):
        self.buffer_size = self.xRes * self.yRes * 16
        for i in range(NUM_BUFFERS):
            error, ret = self.__cam.allocate_buffer(self.buffer_size)
            if error == 0:
                idx = ret['buffer_idx']
                pointer = ret['buffer_p']
                address = ret['buffer_address']
                event = ret['event']
                size = ret['size']
                print("allocated buffer address: ", address)
                self.buffers.append(BufferInfo(idx, pointer, address, event, size))
            else:
                print("error allocating buffer", self.__cam.get_error_text(error))

        for buf in self.buffers:
            self.add_buffer_to_queue(buf)

        error = self.__cam.set_recording_state(1)
        print("set recording state to RUN:", self.__cam.get_error_text(error))

        if error:
            self.stop_record()
            self.close()
            raise PcoCamError('An error occurred upon recording start: ',self.__cam.get_error_text(error))

    def get_latest_array(self, copy=False, timeout=None):
        '''
        takes the most recent buffer in the queue, waits for it to be finished,
        then resets its event, saves the frame as the latest, and adds the buffer
        to the end of the queue, effectively rotating the queue.
:
        param copy: copy the frame or not
         :param timeout: time in ms to wait before throwing an error
        :return: True if successful
        '''
        buf = self.queue[0] # grab the "first" buffer
        timeout = win32event.INFINITE if timeout is None else max(0, timeout)
        ret = win32event.WaitForSingleObject(buf.event, int(timeout))
        if ret == win32event.WAIT_OBJECT_0:
            error, ret = self.__cam.get_buffer_status(buf.idx)
            drv_status = ret['drv_status']
            if error !=0:
                raise PcoCamError("Get Buffer Status Failed: ", self.__cam.get_error_text(error))
            if drv_status != 0:
                raise PcoCamError(self.__cam.get_error_text(drv_status))
            win32event.ResetEvent(buf.event) # resent the buffer event
        elif ret == win32event.WAIT_TIMEOUT:
            raise TimeoutError("Wait for buffer timed out.")
        else:
            raise Exception("Failed to grab image.")
        latest_buffer = self.queue.popleft()
        self.add_buffer_to_queue(buf)
        self.latest_array = np.asarray((ctypes.c_uint16*(latest_buffer.size//16)).from_address(latest_buffer.address)).newbyteorder().astype(dtype=np.uint8)
        if copy:
            return self.latest_array.reshape(self.yRes, self.xRes)[:]
        else:
            return self.latest_array.reshape(self.yRes, self.xRes)

    def stop_record(self):
        error = self.__cam.set_recording_state(0)
        print("set recording state to OFF:", self.__cam.get_error_text(error))

        self.queue.clear()

        error = self.__cam.cancel_images()
        print("cancel images:", self.__cam.get_error_text(error))

        for buffer in self.buffers:
            error = self.__cam.free_buffer(buffer.idx)
            print("buffer at",buffer.address,"freed: ",self.__cam.get_error_text(error))

        self.buffers = []

    def close(self):
        error = self.__cam.close_camera()
        print("close camera:", self.__cam.get_error_text(error))
        #
        # error = self.__cam.reset_lib()
        # print("reset lib:", self.__cam.get_error_text(error))

    def restart(self):
        self.close()
        self.open()