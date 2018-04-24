# -*- coding: utf-8 -*-

import ctypes as C

class sdk:

    SC2_Cam = 0
    camera_handle = C.c_void_p(0)

    PCO_Recorder = 0
    recorder_handle = C.c_void_p(0)

    def __init__(self):

        self.SC2_Cam = C.windll.LoadLibrary("./dll/SC2_Cam.dll")
        self.SC2_Cam.PCO_ResetLib()
        self.PCO_Recorder = C.windll.LoadLibrary("./dll/PCO_Recorder.dll")

    def recorder_create(self):
        self.recorder_handle = C.c_void_p(0)
        self.PCO_Recorder.PCO_RecorderCreate.argtypes = [C.POINTER(C.c_void_p), C.POINTER(C.c_void_p), C.POINTER(C.c_uint32), C.c_uint16, C.c_uint32, C.POINTER(C.c_uint8), C.c_uint16, C.POINTER(C.c_uint32)]
        dwImgDistributionArr, dwMaxImgCountArr = (C.c_uint32(1), C.c_uint32())
        buffer = (C.c_char * 500)()
        p_buffer = C.cast(buffer, C.POINTER(C.c_ubyte))
        error = self.PCO_Recorder.PCO_RecorderCreate(self.recorder_handle, self.camera_handle, dwImgDistributionArr, 1, 4, p_buffer, 0, dwMaxImgCountArr)
        return error, dwMaxImgCountArr.value

    def recorder_delete(self):
        self.PCO_Recorder.PCO_RecorderDelete.argtypes = [C.c_void_p]
        error = self.PCO_Recorder.PCO_RecorderDelete(self.recorder_handle)
        return error

    def recorder_init(self):
        self.PCO_Recorder.PCO_RecorderInit.argtypes = [C.c_void_p, C.POINTER(C.c_uint32), C.c_uint16, C.c_uint16]
        dwImgCountArr = (C.c_uint32(40))
        error = self.PCO_Recorder.PCO_RecorderInit(self.recorder_handle, dwImgCountArr, 1, 0)
        return error

    def recorder_start_record(self):
        self.PCO_Recorder.PCO_RecorderInit.argtypes = [C.c_void_p, C.c_void_p]
        error = self.PCO_Recorder.PCO_RecorderStartRecord(self.recorder_handle, self.camera_handle)
        return error

    def recorder_stop_record(self):
        self.PCO_Recorder.PCO_RecorderStopRecord.argtypes = [C.c_void_p, C.c_void_p]
        error = self.PCO_Recorder.PCO_RecorderStopRecord(self.recorder_handle, self.camera_handle)
        return error

    def recorder_copy_image(self, img, x0, y0, x1, y1):
        self.PCO_Recorder.PCO_RecorderCopyImage.argtypes = [C.c_void_p, C.c_void_p, C.c_uint32, C.c_uint16, C.c_uint16, C.c_uint16, C.c_uint16, C.POINTER(C.c_uint16)]
        wImgBuf = (C.c_uint16 * (((x1-x0)+1)*((y1-y0)+1)))()
        p_wImgBuf = C.cast(wImgBuf, C.POINTER(C.c_uint16))
        error = self.PCO_Recorder.PCO_RecorderCopyImage(self.recorder_handle, self.camera_handle, C.c_uint32(0xffffffff), x0, y0, x1, y1, p_wImgBuf)
        return error, wImgBuf

    def reset_lib(self):
        self.SC2_Cam.PCO_ResetLib.argtypes = [C.POINTER(C.c_void_p)]
        error = self.SC2_Cam.PCO_ResetLib(self.camera_handle)
        return error

    def open_camera(self):
        self.SC2_Cam.PCO_OpenCamera.argtypes = [C.POINTER(C.c_void_p), C.c_uint16]
        error = self.SC2_Cam.PCO_OpenCamera(self.camera_handle, 0)
        return error

    def close_camera(self):
        self.SC2_Cam.PCO_CloseCamera.argtypes = [C.c_void_p]
        error = self.SC2_Cam.PCO_CloseCamera(self.camera_handle)
        return error

    def set_roi(self, wRoiX0, wRoiY0, wRoiX1, wRoiY1):
        self.SC2_Cam.PCO_SetROI.argtypes = [C.c_void_p, C.c_uint16, C.c_uint16, C.c_uint16, C.c_uint16]
        error = self.SC2_Cam.PCO_SetROI(self.camera_handle, wRoiX0, wRoiY0, wRoiX1, wRoiY1)
        return error

    # SET FRAMERATE 
    # def set_framerate(self, mode, framerate, exposure):
    #     self.SC2_Cam.PCO_SetFrameRate.argtypes = [C.c_void_p, ??? ]
    #     error = self.SC2_Cam.PCO_SetFrameRate(self.camera_handle, mode, framerate, exposure)
    #     return error                                                                

    def arm(self):
        self.SC2_Cam.PCO_ArmCamera.argtypes = [C.c_void_p]
        error = self.SC2_Cam.PCO_ArmCamera(self.camera_handle)
        return error

    def get_error_text(self, errorcode):
        self.SC2_Cam.PCO_GetErrorText.argtypes = [C.c_uint32, C.POINTER(C.c_uint32), C.c_uint32]
        buffer = (C.c_char * 500)()
        p_buffer = C.cast(buffer, C.POINTER(C.c_ulong))
        self.SC2_Cam.PCO_GetErrorText(errorcode, p_buffer, 500)
        temp_list = []
        for i in range(100):
            temp_list.append(buffer[i])
        output_string = bytes.join(b'', temp_list).decode('ascii')
        return output_string.strip("\0")

    def reset_settings_to_default(self):
        self.SC2_Cam.PCO_ResetSettingsToDefault.argtypes = [C.c_void_p]
        error = self.SC2_Cam.PCO_ResetSettingsToDefault(self.camera_handle)
        return error

    def set_delay_exposure_time(self, delay, exposure):
        self.SC2_Cam.PCO_SetDelayExposureTime.argtypes = [C.c_void_p, C.c_uint32, C.c_uint32, C.c_uint16, C.c_uint16]
        error = self.SC2_Cam.PCO_SetDelayExposureTime(self.camera_handle, delay, exposure, 2, 2)
        return error

    def set_trigger_mode(self, trigger):
        self.SC2_Cam.PCO_SetTriggerMode.argtypes = [C.c_void_p, C.c_uint16]
        error = self.SC2_Cam.PCO_SetTriggerMode(self.camera_handle, trigger)
        return error

    def set_recording_state(self, wState):
        self.SC2_Cam.PCO_SetRecordingState.argtypes = [C.c_void_p, C.c_uint16]
        error = self.SC2_Cam.PCO_SetRecordingState(self.camera_handle, wState)
        return error
