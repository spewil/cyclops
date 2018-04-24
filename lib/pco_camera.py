# -*- coding: utf-8 -*-

import pco_sdk


class camera:

    __cam = pco_sdk.sdk()

    def __init__(self, roi_tuple, exposureMs):

        error = self.__cam.reset_lib()
        print("reset lib:", self.__cam.get_error_text(error))
        error = self.__cam.open_camera()
        print("open camera:", self.__cam.get_error_text(error))

        if error == 0:
            error = self.__cam.set_recording_state(0)
            print("set recording state:", self.__cam.get_error_text(error))
            error = self.__cam.reset_settings_to_default()
            print("reset settings to default:", self.__cam.get_error_text(error))
            error = self.__cam.set_roi(*roi_tuple)
            print("set roi:", self.__cam.get_error_text(error))
            error = self.__cam.set_delay_exposure_time(0, exposureMs)
            print("set delay exposure time:", self.__cam.get_error_text(error))
            error = self.__cam.set_trigger_mode(0)
            print("set trigger mode:", self.__cam.get_error_text(error))
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

        # error, buffer = self.__cam.recorder_copy_image(0, 1, 1, x, y)
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
