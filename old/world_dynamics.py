
"""
# control_t ---->|----|
#                |    |----> state_t+1
#   state_t ---->|____|
"""
import tools 
import numpy as np

class BrownianBlob:

    def __init__(self, frame_size):

        if len(frame_size) != 2:
            raise ValueError('frame_size is not 2D')

        self.frame_size = frame_size
        self.width = frame_size[0]
        self.height = frame_size[1]

        self.x = np.linspace(0, frame_size[0], frame_size[0])[:, None]
        self.y = np.linspace(0, frame_size[1], frame_size[1])[None, :]

        # timesteps = np.linspace(0,5000,fps*time)
        arrays = []
        self.mean = np.array([self.width / 2., self.height / 2.])
        self.sig = np.array([0.05 * self.width, 0.05 * self.height])
        self.state = 255*np.exp(-((1./self.sig[0]**2)*(self.x - self.mean[0])**2 + (1./self.sig[1]**2)*((self.y - self.mean[1]))**2))
        self.state_passive = self.state.copy()

        self.step = 0

    def update(self, control_input):

        # random walk the mean to a new location
        self.mean += np.random.randn(2)*0.01*self.frame_size
        self.state_passive = 255*np.exp(-((1./self.sig[0]**2)*(self.x - self.mean[0])**2 + (1./self.sig[1]**2)*((self.y - self.mean[1]))**2)) 
        self.state = self.state_passive.copy() - control_input

        self.step += 1

class GaussianField:

    def __init__(self, frame_size):

        def gen_fft_indices(n):

            a = range(0, n / 2 + 1)
            b = range(1, n / 2)
            b.reverse()
            b = [-i for i in b]
            return a + b

        def Pk2(kx, ky):
            if kx == 0 and ky == 0:
                return 0.0
            return np.sqrt((np.sqrt(kx**2 + ky**2))**self.alpha)

        self.alpha = -3.0

        if len(frame_size) != 2:
            raise ValueError('num_pixels is not 2D')

        self.frame_size = frame_size
        self.width, self.height = frame_size[0], frame_size[1]

        self.raw_noise = np.random.normal(size=(self.width, self.height))
        self.noise = np.fft.fft2(self.raw_noise)

        self.amplitude = np.zeros((self.width, self.height))
        for i, kx in enumerate(gen_fft_indices(self.width)):
            for j, ky in enumerate(gen_fft_indices(self.height)):
                self.amplitude[i, j] = Pk2(kx, ky)

        self.state = np.fft.ifft2(self.noise * self.amplitude)

        # shift -- only do this the first time
        self.state_min = np.min(self.state.real)
        self.state += abs(self.state_min)
        # scale
        self.state_max = np.max(self.state.real)
        self.state = (255./self.state_max)*self.state.real

        # some polynomial for update, random coefficients [0,10]
        self.poly_params = np.random.rand(1)*10

        self.step = 0

    # start with fully random, then brownian motion perturb the noise

    def update(self, control_input):

        # perturb the noise by 1% of the max
        # self.raw_noise += self.state_max*0.01*np.random.rand(self.width, self.height)

        # evaluate polynomial at current step
        t_vals = np.array([(0.1*self.step)**gamma for gamma in range(0,len(self.poly_params)+1)])
        # multiply coeffs
        x = np.sum(self.poly_params*t_vals)
        self.raw_noise +=  np.random.rand(self.width, self.height)

        self.noise = np.fft.fft2(self.raw_noise)
        self.state = np.fft.ifft2(self.noise * self.amplitude)

        # scale
        self.state_max = np.max(self.state.real)
        self.state_passive = (255./self.state_max)*self.state.real 
        self.state = self.state_passive.copy() - control_input

        self.step += 1
