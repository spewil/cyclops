# -*- coding: utf-8 -*-

import ctypes as C

class sdk:

    SC2_Cam = 0
    camera_handle = C.c_void_p(0)

    PCO_Recorder = 0
    recorder_handle = C.c_void_p(0)

    def __init__(self):

        # self.SC2_Cam = C.windll.LoadLibrary("C:/Program Files (x86)/Digital Camera Toolbox/pco.runtime/bin64/SC2_Cam.dll")
        self.SC2_Cam = C.windll.LoadLibrary("./dll/SC2_Cam.dll")
        self.SC2_Cam.PCO_ResetLib()
        # self.PCO_Recorder = C.windll.LoadLibrary("C:/Program Files (x86)/Digital Camera Toolbox/pco.runtime/bin64/PCO_Recorder.dll")
        self.PCO_Recorder = C.windll.LoadLibrary("./dll/PCO_Recorder.dll")

    def recorder_create(self):
        self.recorder_handle = C.c_void_p(0)
        self.PCO_Recorder.PCO_RecorderCreate.argtypes = [C.POINTER(C.c_void_p), C.POINTER(C.c_void_p), C.POINTER(C.c_uint32), C.c_uint16, C.c_uint32, C.POINTER(C.c_uint8), C.c_uint16, C.POINTER(C.c_uint32)]
        dwImgDistributionArr, dwMaxImgCountArr = (C.c_uint32(1), C.c_uint32())
        buffer = (C.c_char * 500)()
        p_buffer = C.cast(buffer, C.POINTER(C.c_ubyte))
        # cannot have access to image buffer in file save mode... (mode 1)
        # HANDLE* phRec                             //in
        # HANDLE* phCamArr                          //in, out
        # const DWORD* dwImgDistributionArr         //in
        # WORD wArrLength                           //in
        # DWORD dwRecMode                           //in
            # 1 = file
            # 2 = sequence buffer
            # 4 = ring buffer
        # const char* szFilePath                    //in
        # WORD wFileType                            //in
        # DWORD* dwMaxImgCountArr                   //out
        error = self.PCO_Recorder.PCO_RecorderCreate(self.recorder_handle, self.camera_handle, dwImgDistributionArr, 1, 4, p_buffer, 0, dwMaxImgCountArr)
        return error, dwMaxImgCountArr.value

    def recorder_get_settings(self):
        self.PCO_Recorder.PCO_RecorderGetSettings.argtypes = [C.c_void_p, C.c_void_p,
                                                              C.POINTER(C.c_uint32), C.POINTER(C.c_uint32), C.POINTER(C.c_uint32),
                                                              C.POINTER(C.c_uint16), C.POINTER(C.c_uint16)]
        dwRecmode = C.c_uint32()
        dwMaxImgCount = C.c_uint32()
        dwReqImgCount = C.c_uint32()
        wWidth = C.c_uint16()
        wHeight = C.c_uint16()

        error = self.PCO_Recorder.PCO_RecorderGetSettings(self.recorder_handle, self.camera_handle, dwRecmode, dwMaxImgCount, dwReqImgCount, wWidth, wHeight)

        ret = {}
        if error == 0:
            ret.update({"recorder_mode": dwRecmode})
            ret.update({"max_img_count": dwMaxImgCount})
            ret.update({"req_img_count": dwReqImgCount})
            ret.update({"img_width": wWidth})
            ret.update({"img_height": wHeight})
        return error, ret

    def recorder_get_image_size(self):
        '''
        phRec HANDLE HANDLE to a previously created recorder object
        phCam HANDLE HANDLE to the camera the image size should be retrieved
        wWidth WORD* Pointer to a WORD to get the image width of the camera
        wHeight WORD* Pointer to a WORD to get the image height of the camera
        '''
        self.PCO_Recorder.PCO_RecorderGetImageSize.argtypes = [C.c_void_p, C.c_void_p,
                                                              C.POINTER(C.c_uint16), C.POINTER(C.c_uint16)]
        wWidth = C.c_uint16()
        wHeight = C.c_uint16()

        error = self.PCO_Recorder.PCO_RecorderGetImageSize(self.recorder_handle, self.camera_handle, wWidth, wHeight)

        ret = {}
        if error == 0:
            ret.update({"img_width": wWidth})
            ret.update({"img_height": wHeight})
        return error, ret

    def recorder_delete(self):
        self.PCO_Recorder.PCO_RecorderDelete.argtypes = [C.c_void_p]
        error = self.PCO_Recorder.PCO_RecorderDelete(self.recorder_handle)
        return error

    def recorder_init(self):
        '''
        phRec HANDLE
            HANDLE to a previously created recorder object
        dwImgCountArr DWORD*
            Pointer to an array for required image counts for all cameras (at least 4 images per camera are required)
        wArrLength WORD
            Length of the transferred array
        wNoOverwrite  WORD
            Flag to decide if existing files should be kept. If not set existing files will be deleted
        '''
        self.PCO_Recorder.PCO_RecorderInit.argtypes = [C.c_void_p, C.POINTER(C.c_uint32), C.c_uint16, C.c_uint16]

        # i think this is the buffer size, the required number of images in the record
        dwImgCountArr = (C.c_uint32(1000))
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

    '''
    If the recorder mode is record-to-memory in conjunction 
    with ring buffer mode and acquisition is running, it is possible 
    that the required image will be overwritten during copy. In this 
    case the resulting data will be unpredictable. So be careful 
    using the function during this state.
    '''
    def recorder_copy_image(self, x0, y0, x1, y1):
        self.PCO_Recorder.PCO_RecorderCopyImage.argtypes = [C.c_void_p, C.c_void_p, C.c_uint32, C.c_uint16, C.c_uint16, C.c_uint16, C.c_uint16, C.POINTER(C.c_uint16)]
        wImgBuf = (C.c_uint16 * (((x1-x0)+1)*((y1-y0)+1)))()
        # this call to cast *should* make a new memory chunk...
        p_wImgBuf = C.cast(wImgBuf, C.POINTER(C.c_uint16))
        error = self.PCO_Recorder.PCO_RecorderCopyImage(self.recorder_handle, self.camera_handle, C.c_uint32(0xffffffff), x0, y0, x1, y1, p_wImgBuf)
        # C.c_uint32(0xffffffff) = gets the latest image
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
        self.SC2_Cam.PCO_GetROI.argtypes = [C.c_void_p, C.POINTER(C.c_uint16)
        , C.POINTER(C.c_uint16)
        , C.POINTER(C.c_uint16)
        , C.POINTER(C.c_uint16)
        ]
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

    # -------------------------------------------------------------------------
    # 2.6.8 PCO_GetFrameRate
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # 2.6.9 PCO_SetFrameRate
    # -------------------------------------------------------------------------
    def set_frame_rate(self, frame_rate_mHz, exposure_time_ns):
        self.SC2_Cam.PCO_SetFrameRate.argtypes = [C.c_void_p, C.POINTER(C.c_uint16), C.c_uint16, C.POINTER(C.c_uint32), C.POINTER(C.c_uint32)]
        wFrameRateStatus = C.c_uint16()
        wFrameRateMode = C.c_uint16()
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

    # PCO_SetTransferParametersAuto()(SDK Manual page 202)
    def set_transfer_parameters_auto(self):
        self.SC2_Cam.PCO_SetTransferParametersAuto.argtypes = [C.c_void_p, C.POINTER(C.c_void_p), C.c_int]
        buffer = C.c_void_p(0)
        ilen = C.c_int(0)

        error = self.SC2_Cam.PCO_SetTransferParametersAuto(self.camera_handle, buffer, ilen)

        return error

    # The PCO_SetTimestampMode() function sets the timestamp mode of the camera(SDK Manual page 148):
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

    def get_camera_setup(self):
        self.SC2_Cam.PCO_GetCameraSetup.argytpes = [C.c_void_p, C.POINTER(C.c_uint16), C.POINTER(C.c_uint32), C.POINTER(C.c_uint16)]

        wType = C.c_uint16(0)

        dwSetup = (C.c_uint32 * 4)()
        p_dwSetup = C.cast(dwSetup, C.POINTER(C.c_ulong))

        wLen = C.c_uint16(4)

        error = self.SC2_Cam.PCO_GetCameraSetup(self.camera_handle, wType, p_dwSetup, wLen)

        ret = {}
        if error == 0:
            ret.update({'setup_array': dwSetup.value})

        return error, ret

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
