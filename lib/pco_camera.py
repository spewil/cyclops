# -*- coding: utf-8 -*-

import pco_sdk


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

            error, ret = self.__cam.get_roi()
            print("default roi:",ret["x0"],ret["y0"],ret["x1"],ret["y1"])
            error = self.__cam.set_roi(x0, y0, x1, y1)
            print("set roi:", self.__cam.get_error_text(error))
            error, ret = self.__cam.get_roi()
            print("current roi:",ret["x0"],ret["y0"],ret["x1"],ret["y1"])            

            # error = self.__cam.set_delay_exposure_time(0, exposure_time_ns//1000)
            # print("set delay exposure time:", self.__cam.get_error_text(error))

            error, ret = self.__cam.get_frame_rate()
            print("default: ", "framerate_mHz: ",ret["frame rate mHz"], "; exposure_ns",ret["exposure time ns"])
            error, ret = self.__cam.set_frame_rate(frame_rate_mHz, exposure_time_ns)
            print("desired: ", "framerate_mHz: ",frame_rate_mHz, "; exposure_ns",exposure_time_ns)
            error, ret = self.__cam.get_frame_rate()
            print("current: ", "framerate_mHz: ",ret["frame rate mHz"], "; exposure_ns: ",ret["exposure time ns"])

            error, ret = self.__cam.get_binning()
            print("default: ", "x_binning: ",ret["x_binning"], "; y_binning: ",ret["y_binning"])
            error, ret = self.__cam.set_binning(x_binning, y_binning)
            print("desired: ", "x_binning: ",x_binning, "; y_binning: ",y_binning)
            error, ret = self.__cam.get_binning()
            print("current: ", "x_binning: ",ret["x_binning"], "; y_binning: ",ret["y_binning"])

            error = self.__cam.set_trigger_mode(0)
            print("set trigger mode:", self.__cam.get_error_text(error))
            # get trigger mode? 

            error = self.__cam.arm()
            print("arm:", self.__cam.get_error_text(error))

            error, img_count = self.__cam.recorder_create()
            print("recorder create:", self.__cam.get_error_text(error))

            if error != 0:
                error = self.__cam.recorder_stop_record()
                print("recorder stop:", self.__cam.get_error_text(error))
                error = self.__cam.recorder_delete()
                print("recorder delete:", self.__cam.get_error_text(error))
                error, img_count = self.__cam.recorder_create()
                print("recorder create:", self.__cam.get_error_text(error))

            error = self.__cam.recorder_init()
            print("recorder init", self.__cam.get_error_text(error))
            error = self.__cam.recorder_start_record()
            print("recorder start record:", self.__cam.get_error_text(error))

    def get_image(self, x0, y0, x1, y1):

        error, buffer = self.__cam.recorder_copy_image(0, x0, y0, x1, y1)
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