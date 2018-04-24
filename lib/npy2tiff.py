
x0 = 0
x1 = 2560
h = 2160
roi_tuple = compute_ROI(x0,x1,h)
w = roi_tuple[2] - roi_tuple[0] + 1

filename = input('Enter .npy filepath: ')

out_filename = input('Enter desired .tiff filepath: ')

# frames = []
with open(filename, 'rb') as f_in:

    while True:

        try: 
            frame = np.load(f_in).reshape(h,w)
            # frames.append(frame)
            tiff.imsave(out_filename, frame, append=True)

        # when we run out of loads
        except IOError:
            break
    # save a list of images 
    # tiff.imsave('images.tiff', np.array(frames))
