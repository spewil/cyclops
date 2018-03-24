

def video2arrays(filename):
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture(filename)

    # Check if camera opened successfully
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")

    frames = []

    # Read until video is completed
    while cap.isOpened():
    # Capture frame-by-frame
        ret, frame = cap.read()

        if ret == True:
            # Display the resulting frame
            frames.append(frame[:,:,0])

        # Break the loop
        else: 
            break

    # When everything done, release the video capture object
    cap.release() 
    # Closes all the frames
    cv2.destroyAllWindows()
    
    return frames

# convert list of numpy arrays to pngs 
def arrays2pngs(images,filepath):
    num = 0
    for image in images: 
        img = Image.fromarray(image).convert('RGB')
        img.save(filepath + '%i.png' % num)
        num += 1 

# convert list of pngs to mp4
def pngs2mp4(image_folder,video_filename):

    if os.path.exists(video_filename):
        os.remove(video_filename)

    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    # VideoWriter(outvid, fourcc, float(fps), size, is_color
    video = cv2.VideoWriter(filename=video_filename, fourcc=-1, fps=24, frameSize=(width,height), isColor=False)

    num = 0
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, '%d.png' % num)))
        num += 1
    cv2.destroyAllWindows()
    video.release()