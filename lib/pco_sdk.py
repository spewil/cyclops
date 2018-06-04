# -*- coding: utf-8 -*-

import ctypes as C
from ctypes import wintypes

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

    # def recorder_create(self):
    #     self.recorder_handle = C.c_void_p(0)
    #     self.PCO_Recorder.PCO_RecorderCreate.argtypes = [C.POINTER(C.c_void_p), C.POINTER(C.c_void_p), C.POINTER(C.c_uint32), C.c_uint16, C.c_uint32, C.POINTER(C.c_uint8), C.c_uint16, C.POINTER(C.c_uint32)]
    #     dwImgDistributionArr, dwMaxImgCountArr = (C.c_uint32(1), C.c_uint32())
    #     buffer = (C.c_char * 500)()
    #     p_buffer = C.cast(buffer, C.POINTER(C.c_ubyte))
    #     # cannot have access to image buffer in file save mode... (mode 1)
    #     # HANDLE* phRec                             //in
    #     # HANDLE* phCamArr                          //in, out
    #     # const DWORD* dwImgDistributionArr         //in
    #     # WORD wArrLength                           //in
    #     # DWORD dwRecMode                           //in
    #         # 1 = file
    #         # 2 = sequence buffer
    #         # 4 = ring buffer
    #     # const char* szFilePath                    //in
    #     # WORD wFileType                            //in
    #     # DWORD* dwMaxImgCountArr                   //out
    #     error = self.PCO_Recorder.PCO_RecorderCreate(self.recorder_handle, self.camera_handle, dwImgDistributionArr, 1, 4, p_buffer, 0, dwMaxImgCountArr)
    #     return error, dwMaxImgCountArr.value
    #
    # def recorder_get_settings(self):
    #     self.PCO_Recorder.PCO_RecorderGetSettings.argtypes = [C.c_void_p, C.c_void_p, C.POINTER(C.c_uint32), C.POINTER(C.c_uint32), C.POINTER(C.c_uint32), C.POINTER(C.c_uint16), C.POINTER(C.c_uint16)]
    #     dwRecmode = C.c_uint32()
    #     dwMaxImgCount = C.c_uint32()
    #     dwReqImgCount = C.c_uint32()
    #     wWidth = C.c_uint16()
    #     wHeight = C.c_uint16()
    #     error = self.PCO_Recorder.PCO_RecorderGetSettings(self.recorder_handle, self.camera_handle, dwRecmode, dwMaxImgCount, dwReqImgCount, wWidth, wHeight)
    #     ret = {}
    #     if error == 0:
    #         ret.update({"recorder_mode": dwRecmode})
    #         ret.update({"max_img_count": dwMaxImgCount})
    #         ret.update({"req_img_count": dwReqImgCount})
    #         ret.update({"img_width": wWidth})
    #         ret.update({"img_height": wHeight})
    #     return error, ret
    #
    # def recorder_get_image_size(self):
    #     '''
    #     phRec HANDLE
    #         HANDLE to a previously created recorder object
    #     phCam HANDLE
    #         HANDLE to the camera the image size should be retrieved
    #     wWidth WORD*
    #         Pointer to a WORD to get the image width of the camera
    #     wHeight WORD*
    #         Pointer to a WORD to get the image height of the camera
    #     '''
    #     self.PCO_Recorder.PCO_RecorderGetImageSize.argtypes = [C.c_void_p, C.c_void_p, C.POINTER(C.c_uint16), C.POINTER(C.c_uint16)]
    #     wWidth = C.c_uint16()
    #     wHeight = C.c_uint16()
    #     error = self.PCO_Recorder.PCO_RecorderGetImageSize(self.recorder_handle, self.camera_handle, wWidth, wHeight)
    #     ret = {}
    #     if error == 0:
    #         ret.update({"img_width": wWidth})
    #         ret.update({"img_height": wHeight})
    #     return error, ret
    #
    # def recorder_delete(self):
    #     self.PCO_Recorder.PCO_RecorderDelete.argtypes = [C.c_void_p]
    #     error = self.PCO_Recorder.PCO_RecorderDelete(self.recorder_handle)
    #     return error
    #
    # def recorder_init(self):
    #     '''
    #     phRec HANDLE
    #         HANDLE to a previously created recorder object
    #     dwImgCountArr DWORD*
    #         Pointer to an array for required image counts for all cameras (at least 4 images per camera are required)
    #     wArrLength WORD
    #         Length of the transferred array
    #     wNoOverwrite  WORD
    #         Flag to decide if existing files should be kept. If not set existing files will be deleted
    #     '''
    #     self.PCO_Recorder.PCO_RecorderInit.argtypes = [C.c_void_p, C.POINTER(C.c_uint32), C.c_uint16, C.c_uint16]
    #     # this is the buffer size, the required number of images in the record
    #     dwImgCountArr = (C.c_uint32(1000))
    #     error = self.PCO_Recorder.PCO_RecorderInit(self.recorder_handle, dwImgCountArr, 1, 0)
    #     return error
    #
    # def recorder_start_record(self):
    #     self.PCO_Recorder.PCO_RecorderInit.argtypes = [C.c_void_p, C.c_void_p]
    #     error = self.PCO_Recorder.PCO_RecorderStartRecord(self.recorder_handle, self.camera_handle)
    #     return error
    #
    # def recorder_stop_record(self):
    #     self.PCO_Recorder.PCO_RecorderStopRecord.argtypes = [C.c_void_p, C.c_void_p]
    #     error = self.PCO_Recorder.PCO_RecorderStopRecord(self.recorder_handle, self.camera_handle)
    #     return error
    #
    # '''
    # If the recorder mode is record-to-memory in conjunction
    # with ring buffer mode and acquisition is running, it is possible
    # that the required image will be overwritten during copy. In this
    # case the resulting data will be unpredictable. So be careful
    # using the function during this state.
    #
    # '''
    # def recorder_copy_image(self, x0, y0, x1, y1):
    #     self.PCO_Recorder.PCO_RecorderCopyImage.argtypes = [C.c_void_p, C.c_void_p, C.c_uint32, C.c_uint16, C.c_uint16, C.c_uint16, C.c_uint16, C.POINTER(C.c_uint16)]
    #     wImgBuf = (C.c_uint16 * (((x1-x0)+1)*((y1-y0)+1)))()
    #     # this call to cast *should* make a new memory chunk...
    #     p_wImgBuf = C.cast(wImgBuf, C.POINTER(C.c_uint16))
    #     error = self.PCO_Recorder.PCO_RecorderCopyImage(self.recorder_handle, self.camera_handle, C.c_uint32(0xffffffff), x0, y0, x1, y1, p_wImgBuf)
    #     # C.c_uint32(0xffffffff) = gets the latest image
    #     return error, wImgBuf

    '''
    To get images from a recording camera both image number values 
    dw1stImage and dwLastImage must be set to zero.
    
    Because with the first PCO_AddBufferEx call the internal request 
    queue is setup and this might be a time consuming operation, first 
    images of the camera might get lost. Therefore PCO_AddBufferEx
    should be called before setting the PCO_SetRecordingStateto [on]. 
    
    When a  separate  thread  is  used  for  image  grabbing,  
    synchronization  between  camera  control thread and image 
    transfer thread must be designed carefully.
    
    get buffer info
    allocate buffers
    free buffer
    
    '''
    def get_buffer_info(self):
        pass

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
        return error, ret

    def free_buffer(self, buf_num):
        self.SC2_Cam.PCO_FreeBuffer.argtypes = [wintypes.HANDLE, wintypes.SHORT]
        sBufNr = wintypes.SHORT(buf_num)
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
        self.SC2_Cam.PCO_CancelImages.argtypes = [wintypes.HANDLE]
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
        wFrameRateMode = C.c_uint16(1)
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

    # DATA DEPTH IS 16
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
