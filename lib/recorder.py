# -*- coding: utf-8 -*-

import json

import cv2
import numpy as np

try:
    from lib.setup_utilities import convert_npy_to_tiff, FPS
    from lib import pco_camera
except:
    from setup_utilities import convert_npy_to_tiff, FPS
    import pco_camera
# ============================================================================

MAX_CAM_X_RES = 2560
MAX_CAM_Y_RES = 2160
CAM_X_ROI_STEP = 160
CAM_Y_ROI_STEP = 1
CV_ESC_KEY = 27
CV_ENT_KEY = 13
FPS_BOT = FPS()

# ============================================================================

class ColorControlError(Exception):
    pass

class CameraSetupError(Exception):
    pass

class Recorder:
    def __init__(self, settings):
        self.settings = settings
        self.experiment_path = self.settings["folder_path"]
        self.max_saved_frames = int(1e9) // int(self.settings["cam_x_res"]*self.settings["cam_y_res"])
        print("Frames per file: ",self.max_saved_frames)

        if self.settings["transform_on"]:
            self.transform = np.load("transform.npy")

        if self.settings["soft_roi_type"] != "None":
            if self.settings["soft_roi_type"] == "Rectangular":
                self.mask = np.load("rectangular_roi_mask.npy")
            elif self.settings["soft_roi_type"] == "Polygonal":
                self.mask = np.load("polygonal_roi_mask.npy")

    def record(self):
        self.camera = pco_camera.Camera(self.settings["frame_rate_mHz"],
                                        self.settings["exposure_time_ns"],
                                        self.settings["binning"],
                                        self.settings["binning"],
                                        *self.settings["roi"])
        if self.settings["save_on"]:
            image_path = self.experiment_path + "images0001.npy"
            print("Image will be saved to: ",self.experiment_path,"images.tiff")
            file_buffer = open(image_path, "ab")

        cv2.namedWindow("Preview")
        if self.settings["control_on"] == True:
            control = np.zeros((self.settings["cam_y_res"], self.settings["cam_x_res"]))

        idx = 1
        file_number = 1
        record = True
        self.camera.start_record()
        FPS_BOT.start()
        while record is True:
            array = self.camera.get_latest_array()
            if self.settings["display_on"] is True:
                if idx % 10 == 0:
                    cv2.imshow("Preview", array)
                    if cv2.waitKey(1) is CV_ENT_KEY:
                        record = False
            if self.settings["control_type"] == "Closed-Loop":
                if self.settings["soft_roi_type"] != "None":
                    # retval, dst = cv.threshold(src, thresh, maxval, type[, dst])
                    control[self.mask] = 255 * ((array[self.mask] >= self.settings["closed_loop_threshold"]).astype(float))
                else:
                    # retval, dst = cv.threshold(src, thresh, maxval, type[, dst])
                    control = 255 * ((array >= self.settings["closed_loop_threshold"]).astype(float))
                if self.settings["transform_on"]:
                    cv2.imshow("Control", cv2.warpAffine(control, self.transform, (self.settings["cam_x_res"], self.settings["cam_y_res"])))
                    if cv2.waitKey(1) is CV_ENT_KEY:
                        record = False
                else:
                    cv2.imshow("Control", control)
                    if cv2.waitKey(1) is CV_ENT_KEY:
                        record = False
            if self.settings["save_on"]:
                if idx > self.max_saved_frames:
                    file_number += 1
                    file_buffer.close()
                    file_buffer = open(self.experiment_path + "images_" + str(file_number).zfill(4) + ".npy", "ab")
                    idx = 1
                np.save(file_buffer, array)

            idx += 1
            FPS_BOT.update()
        FPS_BOT.stop()
        self.camera.stop_record()
        self.camera.close()
        cv2.destroyAllWindows()
        print("Frames per second over %d frames: %6.2f" % (idx - 1, FPS_BOT.fps()))

        with open(self.experiment_path+"settings.json", "w") as f:
            json.dump(self.settings, f, sort_keys=True, indent=4)

        if self.settings["soft_roi_type"] != "None":
            np.save(self.experiment_path+"roi_mask.npy", self.mask)

        if self.settings["transform_on"]:
            np.save(self.experiment_path+"transform.npy", self.transform)

        if self.settings["save_on"]:
            file_buffer.close()
            print("converting to tiff... ")
            convert_npy_to_tiff(image_path, self.settings["cam_x_res"], self.settings["cam_y_res"])

if __name__ == "__main__":
    with open("settings.json", "r") as f:
        settings_dict = json.load(f)
    r = Recorder(settings_dict)
    r.record()