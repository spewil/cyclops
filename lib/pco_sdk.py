# -*- coding: utf-8 -*-

import ctypes as C
from ctypes import wintypes


# TODO: remove all magic numbers

class sdk:

    SC2_Cam = 0
    camera_handle = C.c_void_p(0)

    PCO_Recorder = 0
    recorder_handle = C.c_void_p(0)

    def __init__(self):
        self.SC2_Cam = C.windll.LoadLibrary("./dll/SC2_Cam.dll")
        # self.SC2_Cam = C.windll.LoadLibrary("C:/Program Files (x86)/Digital Camera Toolbox/pco.sdk/bin64/SC2_Cam.dll")
        self.SC2_Cam.PCO_ResetLib()

    def get_buffer_status(self, buf_num):
        self.SC2_Cam.PCO_GetBufferStatus.argtypes = [wintypes.HANDLE, wintypes.SHORT, C.POINTER(C.c_uint32), C.POINTER(C.c_uint32)]
        sBufNr = wintypes.SHORT(buf_num)
        dwStatusDLL = C.c_uint32()
        dwStatusDrv = C.c_uint32()
        error = self.SC2_Cam.PCO_GetBufferStatus(self.camera_handle, sBufNr, dwStatusDLL, dwStatusDrv)
        ret = {}
        if error == 0:
            ret.update({'dll_status': dwStatusDLL.value})
            ret.update({'drv_status': dwStatusDrv.value})
        return error, ret

    def allocate_buffer(self, buf_size):
        self.SC2_Cam.PCO_AllocateBuffer.argtypes = [wintypes.HANDLE, C.POINTER(C.c_int), C.c_uint32, C.POINTER(C.POINTER(C.c_uint16)), C.POINTER(wintypes.HANDLE)]
        sBufNr = C.c_int(-1) # index
        dwSize = C.c_uint32(buf_size) # number of bytes
        wBuf = C.POINTER(C.c_uint16)() # buffer pointer
        hEvent = wintypes.HANDLE()
        error = self.SC2_Cam.PCO_AllocateBuffer(self.camera_handle, C.byref(sBufNr), dwSize, C.byref(wBuf), C.byref(hEvent))
        ret = {}
        if error == 0:
            ret.update({'buffer_idx': sBufNr.value})
            ret.update({'buffer_p': wBuf})
            ret.update({'buffer_address': C.addressof(wBuf.contents)})
            ret.update({'event': hEvent.value})
            ret.update({'size': buf_size})
        return error, ret

    def free_buffer(self, buf_num):
        self.SC2_Cam.PCO_FreeBuffer.argtypes = [wintypes.HANDLE, C.c_int]
        sBufNr = C.c_int(buf_num)
        error = self.SC2_Cam.PCO_FreeBuffer(self.camera_handle, sBufNr)
        return error

    def add_buffer(self, buf_num, width, height):
        self.SC2_Cam.PCO_AddBufferEx.argtypes = [wintypes.HANDLE, C.c_uint32, C.c_uint32, C.c_int, C.c_uint16, C.c_uint16, C.c_uint16]
        dw1stImage = C.c_uint32(0)
        dwLastImage = C.c_uint32(0)
        sBufNr = C.c_int(buf_num)
        wXRes = C.c_uint16(width)
        wYRes = C.c_uint16(height)
        wBitPerPixel = C.c_uint16(16)
        error = self.SC2_Cam.PCO_AddBufferEx(self.camera_handle, dw1stImage, dwLastImage, sBufNr, wXRes, wYRes, wBitPerPixel)
        return error

    def cancel_images(self):
        self.SC2_Cam.PCO_CancelImages.argtypes = [C.POINTER(C.c_void_p)]
        error = self.SC2_Cam.PCO_CancelImages(self.camera_handle)
        return error

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

    def get_binning(self):
        self.SC2_Cam.PCO_GetBinning.argtypes = [C.c_void_p, C.POINTER(C.c_uint16), C.POINTER(C.c_uint16)]
        wBinHorz = C.c_uint16()
        wBinVert = C.c_uint16()
        error = self.SC2_Cam.PCO_GetBinning(self.camera_handle, wBinHorz, wBinVert)
        ret = {}
        if error == 0:
            ret.update({'x_binning': wBinHorz.value})
            ret.update({'y_binning': wBinVert.value})
        return error, ret

    def set_binning(self, x_binning, y_binning):
        self.SC2_Cam.PCO_SetBinning.argtypes = [C.c_void_p, C.c_uint16, C.c_uint16]
        wBinHorz = C.c_uint16(x_binning)
        wBinVert = C.c_uint16(y_binning)
        error = self.SC2_Cam.PCO_SetBinning(self.camera_handle, wBinHorz, wBinVert)
        ret = {}
        if error == 0:
            ret.update({'x_binning': wBinHorz.value})
            ret.update({'y_binning': wBinVert.value})
        return error, ret

    def set_roi(self, wRoiX0, wRoiY0, wRoiX1, wRoiY1):
        self.SC2_Cam.PCO_SetROI.argtypes = [C.c_void_p, C.c_uint16, C.c_uint16, C.c_uint16, C.c_uint16]
        error = self.SC2_Cam.PCO_SetROI(self.camera_handle, wRoiX0, wRoiY0, wRoiX1, wRoiY1)
        return error   

    def get_roi(self):
        self.SC2_Cam.PCO_GetROI.argtypes = [C.c_void_p, C.POINTER(C.c_uint16), C.POINTER(C.c_uint16), C.POINTER(C.c_uint16), C.POINTER(C.c_uint16)]
        wRoiX0 = C.c_uint16()
        wRoiY0 = C.c_uint16()
        wRoiX1 = C.c_uint16()
        wRoiY1 = C.c_uint16()
        error = self.SC2_Cam.PCO_GetROI(self.camera_handle, wRoiX0, wRoiY0, wRoiX1, wRoiY1)
        ret = {}
        if error == 0:
            ret.update({'x0': wRoiX0.value})
            ret.update({'y0': wRoiY0.value})
            ret.update({'x1': wRoiX1.value})
            ret.update({'y1': wRoiY1.value})
        return error, ret                                                          

    def get_frame_rate(self):
        self.SC2_Cam.PCO_GetFrameRate.argtypes = [C.c_void_p, C.POINTER(C.c_uint16), C.POINTER(C.c_uint32), C.POINTER(C.c_uint32)]
        wFrameRateStatus = C.c_uint16()
        dwFrameRate = C.c_uint32()
        dwFrameRateExposure = C.c_uint32()
        error = self.SC2_Cam.PCO_GetFrameRate(self.camera_handle, wFrameRateStatus, dwFrameRate, dwFrameRateExposure)
        ret = {}
        if error == 0:
            ret.update({'status': wFrameRateStatus.value})
            ret.update({'frame rate mHz':dwFrameRate.value})
            ret.update({'exposure time ns':dwFrameRateExposure.value})
        return error, ret

    def set_frame_rate(self, frame_rate_mHz, exposure_time_ns):
        self.SC2_Cam.PCO_SetFrameRate.argtypes = [C.c_void_p, C.POINTER(C.c_uint16), C.c_uint16, C.POINTER(C.c_uint32), C.POINTER(C.c_uint32)]
        wFrameRateStatus = C.c_uint16()
        wFrameRateMode = C.c_uint16(2)
        dwFrameRate = C.c_uint32(frame_rate_mHz)
        dwFrameRateExposure = C.c_uint32(exposure_time_ns)
        error = self.SC2_Cam.PCO_SetFrameRate(self.camera_handle, wFrameRateStatus, wFrameRateMode, dwFrameRate, dwFrameRateExposure)
        ret = {}
        if error == 0:
            ret.update({'status': wFrameRateStatus.value})
            ret.update({'mode': wFrameRateMode.value})
            ret.update({'frame rate mHz': dwFrameRate.value})
            ret.update({'exposure time ns': dwFrameRateExposure.value})

        return error, ret

    def get_sizes(self):
        self.SC2_Cam.PCO_GetSizes.argtypes = [C.c_void_p, C.POINTER(C.c_uint16), C.POINTER(C.c_uint16), C.POINTER(C.c_uint16), C.POINTER(C.c_uint16)]
        wXResAct = C.c_uint16()
        wYResAct = C.c_uint16()
        wXResMax = C.c_uint16()
        wYResMax = C.c_uint16()
        error = self.SC2_Cam.PCO_GetSizes(self.camera_handle, wXResAct, wYResAct, wXResMax, wYResMax)
        ret = {}
        if error == 0:
            ret.update({'xResAct': wXResAct.value})
            ret.update({'yResAct': wYResAct.value})
            ret.update({'xResMax': wXResMax.value})
            ret.update({'yResMax': wYResMax.value})
        return error, ret

    def arm(self):
        self.SC2_Cam.PCO_ArmCamera.argtypes = [C.c_void_p]
        error = self.SC2_Cam.PCO_ArmCamera(self.camera_handle)
        return error

    def set_image_parameters(self, x_res, y_res):
        self.SC2_Cam.PCO_SetImageParameters.argtypes = [C.c_void_p, C.c_uint16, C.c_uint16, C.c_uint32, C.c_void_p, C.c_int]
        wxres = C.c_uint16(x_res)
        wyres = C.c_uint16(y_res)
        dwFlags = C.c_uint32(1)
        param = C.c_void_p()
        ilen = C.c_int()
        error = self.SC2_Cam.PCO_SetImageParameters(self.camera_handle, wxres, wyres, dwFlags, param, ilen)
        return error

    def set_transfer_parameters_auto(self):
        self.SC2_Cam.PCO_SetTransferParametersAuto.argtypes = [C.c_void_p, C.POINTER(C.c_void_p), C.c_int]
        buffer = C.c_void_p(0)
        ilen = C.c_int(0)
        error = self.SC2_Cam.PCO_SetTransferParametersAuto(self.camera_handle, buffer, ilen)
        return error

    def set_timestamp_mode(self, mode):
        self.SC2_Cam.PCO_SetTimestampMode.argtypes = [C.c_void_p, C.c_uint16]
        timestamp_mode = {'off': 0, 'binary': 1, 'binary & ascii': 2, 'ascii': 3}
        error = self.SC2_Cam.PCO_SetTimestampMode(self.camera_handle, timestamp_mode[mode])
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
        return output_string.strip("/0")

    def reset_settings_to_default(self):
        self.SC2_Cam.PCO_ResetSettingsToDefault.argtypes = [C.c_void_p]
        error = self.SC2_Cam.PCO_ResetSettingsToDefault(self.camera_handle)
        return error

    def set_delay_exposure_time(self, delay, exposure_time_ns):
        self.SC2_Cam.PCO_SetDelayExposureTime.argtypes = [C.c_void_p, C.c_uint32, C.c_uint32, C.c_uint16, C.c_uint16]
        error = self.SC2_Cam.PCO_SetDelayExposureTime(self.camera_handle, delay, exposure_time_ns, 2, 2)
        return error

    def set_trigger_mode(self, trigger):
        self.SC2_Cam.PCO_SetTriggerMode.argtypes = [C.c_void_p, C.c_uint16]
        error = self.SC2_Cam.PCO_SetTriggerMode(self.camera_handle, trigger)
        return error

    def set_recording_state(self, wState):
        self.SC2_Cam.PCO_SetRecordingState.argtypes = [C.c_void_p, C.c_uint16]
        error = self.SC2_Cam.PCO_SetRecordingState(self.camera_handle, wState)
        return error
