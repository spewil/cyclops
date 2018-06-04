# -*- coding: utf-8 -*-

import pco_sdk
import time

MAX_CAM_X_RES = 2560
MAX_CAM_Y_RES = 2160

class PcoCamError(Exception):
    pass

class camera:

    __cam = pco_sdk.sdk()

    def __init__(self, frame_rate_mHz, exposure_time_ns, x_binning, y_binning, x0, y0, x1, y1):

        error = self.__cam.reset_lib()
        print("reset lib:", self.__cam.get_error_text(error))
        error = self.__cam.open_camera()
        if error:
            raise PcoCamError("open camera:", self.__cam.get_error_text(error))

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

            # # BINNING
            # error, ret = self.__cam.set_binning(2, 2)
            # print("set binning: ", self.__cam.get_error_text(error))
            # print("desired x_binning: ", x_binning)
            # print("desired y_binning: ", y_binning)
            #
            # # ROI
            # error = self.__cam.set_roi(x0, y0, x1, y1)
            # print("set roi:", self.__cam.get_error_text(error))

            # CHECK SETTINGS
            # TODO: Offer option if the current =/= desired
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

            # SET PARAMS
            error = self.__cam.set_image_parameters(self.xRes,self.yRes)
            print("set image parameters:", self.__cam.get_error_text(error))
            error = self.__cam.set_transfer_parameters_auto()
            print("set transfer parameters auto:", self.__cam.get_error_text(error))

            # ARM AND RECORDER
            error = self.__cam.arm()
            print("arm:", self.__cam.get_error_text(error))

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

            error = self.__cam.allocate_buffer(100)
            print("allocate buffer: ",self.__cam.get_error_text(error))



            # error, img_count = self.__cam.recorder_create()
            # print("recorder create:", self.__cam.get_error_text(error))
            # print("maximum available img count:", img_count)
            #
            # if error != 0:
            #     error = self.__cam.recorder_stop_record()
            #     print("recorder stop:", self.__cam.get_error_text(error))
            #     error = self.__cam.recorder_delete()
            #     print("recorder delete:", self.__cam.get_error_text(error))
            #     error, img_count = self.__cam.recorder_create()
            #     print("recorder create:", self.__cam.get_error_text(error))
            #
            # error = self.__cam.recorder_init()
            # print("recorder init", self.__cam.get_error_text(error))
            #
            # error = self.__cam.recorder_start_record()
            # print("recorder start record:", self.__cam.get_error_text(error))
            #
            # error, ret = self.__cam.recorder_get_settings()
            # print("recorder get settings:", self.__cam.get_error_text(error))
            # print("recorder_mode: ", ret["recorder_mode"].value)
            # print("max_img_count: ", ret["max_img_count"].value)
            # print("req_img_count: ", ret["req_img_count"].value)
            # print("img_width: ", ret["img_width"].value)
            # print("img_height: ", ret["img_height"].value)
            #
            # error, ret = self.__cam.recorder_get_image_size()
            # print("recorder get image size:", self.__cam.get_error_text(error))
            # print("img_width: ", ret["img_width"].value)
            # print("img_height: ", ret["img_height"].value)
            # self.img_width = ret["img_width"].value
            # self.img_height = ret["img_height"].value

    def get_image(self):

        error, buffer = self.__cam.recorder_copy_image(1, 1, self.img_width, self.img_height)
        return buffer

    def close(self):

        error = self.__cam.recorder_stop_record()
        print("recorder stop recorder:", self.__cam.get_error_text(error))
        error = self.__cam.recorder_delete()
        print("recorder delete:", self.__cam.get_error_text(error))
        error = self.__cam.close_camera()
        print("close camera:", self.__cam.get_error_text(error))
        error = self.__cam.reset_lib()
        print("reset lib:", self.__cam.get_error_text(error))