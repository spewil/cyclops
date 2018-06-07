This typical step by step implementation shows the basic handling:

// 1. Declarations:
	PCO_General strGeneral;
	PCO_CameraType strCamType;
	PCO_Sensor strSensor;
	PCO_Description strDescription;
	PCO_Timing strTiming;
	PCO_Storage strStorage;
	PCO_Recording strRecording;
	
// 2. Set all buffer 'size' parameters to the expected values:
	strGeneral.wSize = sizeof(strGeneral);
	strGeneral.strCamType.wSize = sizeof(strGeneral.strCamType);
	strCamType.wSize = sizeof(strCamType);
	strSensor.wSize = sizeof(strSensor);
	strSensor.strDescription.wSize = sizeof(strSensor.strDescription);
	strSensor.strDescription2.wSize = sizeof(strSensor.strDescription2);
	strDescription.wSize = sizeof(strDescription);
	strTiming.wSize = sizeof(strTiming);
	strStorage.wSize = sizeof(strStorage);
	strRecording.wSize = sizeof(strRecording);
	
// 3. Open the camera and fill the structures:
	PCO_OPENCAMERA(&hCam, iBoardNumber)
	PCO_GETGENERAL(hCam, &strGeneral)
	PCO_GETCAMERATYPE(hCam, &strCamType)
	PCO_GETSENSORSTRUCT(hCam, &strSensor)
	PCO_GETCAMERADESCRIPTION(hCam, &strDescription)
	PCO_GETTIMINGSTRUCT(hCam, &strTiming)
	PCO_GETRECORDINGSTRUCT(hCam, &strRecording)
	
// 4. Set camera settings (exposure, modes, etc.) and sizes (binning, ROI, etc.).
// 5. Arm the camera.
// 6. Get the sizes and allocate a buffer:
	PCO_GETSIZES(hCam, &actualsizex, &actualsizey, &ccdsizex, &ccdsizey)
	PCO_ALLOCATEBUFFER(hCam, &bufferNr, actualsizex * actualsizey * sizeof(WORD),
	&data, &hEvent)
	In case of CamLink and GigE interface: PCO_CamLinkSetImageParameters(actualsizex,
	actualsizey)
	PCO_ArmCamera(hCam)
	
// 7. Set the recording state to 'Recording' and add your buffer(s).
	PCO_SetRecordingState(hCam, 0x0001);
	PCO_AddBufferEx(hCam, 0, 0, bufferNr, actualsizex, actualsizey, bitres);
	
// 8. Access your images with the pointer got by AllocateBuffer.
	Do a convert and show the image.
// 9. Stop the camera.
	PCO_SetRecordingState(hCam, 0x0000);
	PCO_CancelImages(hCam);
	
// 10. After recording, if you like to read out some images from the CamRAM you can
	use:
	PCO_GetNumberOfImagesInSegment(hCam, wActSeg, &dwValidImageCnt,
	&dwMaxImageCnt);
	PCO_GetImageEx(hCam, wActSeg, dw1stImage, dwLastImage, bufferNr, actualsizex,
	actualsizey, bitres)
	
// 11. Free all buffers and close the camera.
	PCO_FreeBuffer(hCamera, sBufNr);
	PCO_CloseCamera(hCamera);
	