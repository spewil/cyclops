# brownian motion in 2D is pulling gaussian step change 
def Brownian_Blob(num_pixels, time, fps):

    if len(num_pixels.shape) != 2:
        raise ValueError('num_pixels is not 2D')

    x = np.linspace(0, num_pixels[0], num_pixels[0])[:,None]
    y = np.linspace(0, num_pixels[1], num_pixels[1])[None,:]

    timesteps = np.linspace(0,5000,fps*time)
    arrays = []
    mean = np.array([num_pixels/2., num_pixels/2.])
    sig_x = 0.05*num_pixels 
    sig_y = 0.05*num_pixels
    for t in timesteps:
        mean += np.random.randn(2)*.01*num_pixels
        sig_x += np.random.randn(1)
        sig_y += np.random.randn(1)
        arrays.append(255*np.exp(-((1./sig_x**2)*(x - mean[0])**2 + (1./sig_y**2)*((y - mean[1]))**2)))
    return arrays 