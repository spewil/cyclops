import numpy as np 
import tifffile as tiff 

def compute_ROI(x0, x1, h):

    if x1 <= x0:
        raise Error("ROI must have x1 > x0")
    elif x1-x0 < 160:
        raise Error("Width must be greater than 160")

    # Ensure coords are bounded properly
    x0 = max(0, x0 - x0%160) + 1 
    x1 = min(2560, x1 + 160 - x1%160)

    # make h even 
    if h%2 is not 0:
        h += 1

    # compute the y coords (must be symmetric for pco.edge)
    h_2 = h // 2

    # height must be even, minimum is 16 
    # x values are multiples of 160, minimum is 160

    half_y_max = 2160 // 2
    y0 = half_y_max - h_2 + 1
    y1 = half_y_max + h_2

    return (x0,y0,x1,y1)

# get size of first image here!
x0 = 0
x1 = 2560 // 2
h = 2160 // 2

roi_tuple = compute_ROI(x0,x1,h)
w = roi_tuple[2] - roi_tuple[0] + 1

filename = input('Enter .npy filepath: ')

out_filename = input('Enter desired .tiff filepath: ')

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
