
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
