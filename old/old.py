# old stuff

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

def gen_fft_indices(n):
    a = range(0, n/2+1)
    b = range(1, n/2)
    b.reverse()
    b = [-i for i in b]
    return a + b

def gaussian_random_field(alpha=-3.0, size = 100):
    def Pk2(kx, ky):
        if kx == 0 and ky == 0:
            return 0.0
        return np.sqrt((np.sqrt(kx**2 + ky**2))**alpha)
    noise = np.fft.fft2(np.random.normal(size = (size, size)))
    amplitude = np.zeros((size,size))
    for i, kx in enumerate(gen_fft_indices(size)):
        for j, ky in enumerate(gen_fft_indices(size)):
            amplitude[i, j] = Pk2(kx, ky)
    return np.fft.ifft2(noise * amplitude)

import matplotlib.animation as animation

##################################

##################################

def model0(k):
    return k**0*0.5

def gen_2Dgauss(N, Lx, Ly, model):

    field = np.zeros((N,N), dtype = complex)

    dkx = (2.*np.pi)/Lx
    dky = (2.*np.pi)/Ly

    for ix in range(0, N):
        if ix <= N/2:
            kx = ix*dkx
        else:
            kx = (ix-N)*dkx
    
        for iy in range(0, N):
            if iy <= N/2:
                ky = iy*dky
            else:
                ky = (iy-N)*dky
        
            kval = (kx**2 + ky**2)**0.5
        
            field[ix, iy] = np.random.normal(0.,(model(kval)/2.)**0.5) + np.random.normal(0.,(model(kval)/2.)**0.5)*1j

    # Now we have to set \delta(-k) = \delta^*(k)
    # Note that \delta_n = \delta_{n+N} and therefore we have to set \delta(2dk,-dk) = \delta^*(2dk,dk)
    for ix in range(N/2+1, N):
    
        jx = N-ix
    
        field[ix, 0] = field[jx, 0].real - field[jx, 0].imag*1j
        field[0, ix] = field[0, jx].real - field[0, jx].imag*1j

        for iy in range(1, N):
        
            jy = N-iy
        
            field[ix, iy] = field[jx, jy].real - field[jx, jy].imag*1j

    if N % 2 == 0:
        for ix in range(1, N/2):
            jx = N-ix
            
            field[N/2,ix] = field[N/2,jx].real - field[N/2,jx].imag*1j


        kval = dkx*N/2
        # Set the complex part to zero if there is no partner (note the factor of 2 difference)
        field[0,N/2] = np.random.normal(0.,model(kval)**0.5) + 0.*1j;
        field[N/2,0] = np.random.normal(0.,model(kval)**0.5) + 0.*1j;
        
        kval = (dkx*N/2)*(2**0.5)
        
        field[N/2,N/2] = np.random.normal(0.,model(kval)**0.5) + 0.*1j;

    field[0,0] = 0. + 0.*1j
    
    return field

def main():
    
    Lx = 1.
    Ly = 1.
    V = Lx*Ly
    N = 101
    dk = (2.*np.pi)/Lx
    
    #-----------------------------------------#
    #-- Generate Gaussian random field -------#
    #-----------------------------------------#
    
    kspace_field = gen_2Dgauss(N, Lx, Ly, model0)
    
    config_field = np.fft.ifft2(kspace_field)*kspace_field.size**0.5
    
    fig, ax = pl.subplots()
    im = ax.imshow(config_field.real, cmap=pl.cm.jet)
    fig.colorbar(im, ax=ax)
    pl.title("field.real, config_space")
    pl.show()
    
    fig, ax = pl.subplots()
    im = ax.imshow(config_field.imag, cmap=pl.cm.jet)
    fig.colorbar(im, ax=ax)
    pl.title("field.imag, config_space")
    pl.show()

if __name__ == '__main__':
    main()