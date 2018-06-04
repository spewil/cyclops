# -*- coding: utf-8 -*-

from collections import deque

from lib import pco_sdk

MAX_CAM_X_RES = 2560
MAX_CAM_Y_RES = 2160
NUM_BUFFERS = 1

class PcoCamError(Exception):
    pass

class BufferInfo(object):
    def __init__(self, num, pointer, address, event):
        self.idx = num
        self. pointer = pointer
        self.address = address
        self.event = event

class Camera:

    __cam = pco_sdk.sdk()

    def __init__(self, frame_rate_mHz, exposure_time_ns, x_binning, y_binning, x0, y0, x1, y1):

        self.queue = deque([], maxlen=100)
        self.buffers = []

        error = self.__cam.reset_lib()
        print("reset lib:", self.__cam.get_error_text(error))
        error = self.__cam.open_camera()
        if error:
            raise PcoCamError("open camera:", self.__cam.get_error_text(error))

        # TODO: implement "if error" for each setup step below
        if error == 0:

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

            error = self.__cam.set_trigger_mode(0)
            print("set trigger mode: ", self.__cam.get_error_text(error))

            # # BINNING
            # error, ret = self.__cam.set_binning(2, 2)
            # print("set binning: ", self.__cam.get_error_text(error))
            # print("desired x_binning: ", x_binning)
            # print("desired y_binning: ", y_binning)
            #
            # # ROI
            # error = self.__cam.set_roi(x0, y0, x1, y1)
            # print("set roi:", self.__cam.get_error_text(error))

            # TODO: check if current =/= desired
            # error, ret = self.__cam.get_binning()
            # print("get binning: ", self.__cam.get_error_text(error))
            # print("current x_binning: ",ret["x_binning"])
            # print("current y_binning: ",ret["y_binning"])
            error, ret = self.__cam.get_frame_rate()
            print("get framerate: ", self.__cam.get_error_text(error))
            print("current framerate_mHz: ",ret["frame rate mHz"])
            # print("current exposure_ns: ",ret["exposure time ns"])
            # error, ret = self.__cam.get_roi()
            # print("get roi: ", self.__cam.get_error_text(error))
            # print("current roi:",ret["x0"],ret["y0"],ret["x1"],ret["y1"])

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

            # set up buffers
            self.buffer_size = self.xRes*self.yRes*16
            for i in range(NUM_BUFFERS):
                error, ret = self.__cam.allocate_buffer(self.buffer_size)
                print("allocated buffers", self.__cam.get_error_text(error))
                if error == 0:
                    idx = ret['buffer_idx']
                    pointer = ret['buffer_p']
                    address = ret['buffer_address']
                    event = ret['event']
                    print("allocated buffer address: ", address)
                    self.buffers.append(BufferInfo(idx, pointer, address, event))

    def add_buffers_to_queue(self):
        for buffer in self.buffers:
            error = self.__cam.add_buffer(buffer.idx, self.xRes, self.yRes)
            # print("added buffer at address || index: ", buffer.address, "||", buffer.idx, ": ", self.__cam.get_error_text(error))
            self.queue.append(buffer)

    def start_record(self):

        error = self.__cam.set_recording_state(1)
        print("set recording state:", self.__cam.get_error_text(error))

        if error:
            self.stop_record()
            self.close()

        self.add_buffers_to_queue()

    def stop_record(self):
        error = self.__cam.set_recording_state(0)
        print("set recording state:", self.__cam.get_error_text(error))

    def close(self):

        error = self.__cam.close_camera()
        print("close camera:", self.__cam.get_error_text(error))

        for buffer in self.buffers:
            error = self.__cam.free_buffer(buffer.idx)
            print("buffer ",buffer.idx,"closed: ",self.__cam.get_error_text(error))

        error = self.__cam.reset_lib()
        print("reset lib:", self.__cam.get_error_text(error))