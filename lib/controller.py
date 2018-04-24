"""
#                |----| 
#   state_t ---->|    |----> control_t+1 
#                |____|

    implements bang-bang control given a state and a threshold

    current state: is an array

    threshold: float value above which inhibition turns on 

    returns: the on or off control signal for each state variable 
"""

import numpy as np

""" implements bang-bang control

"""
def BangBang(current_state, target_state):

    # scale state to [0,1]
    # current_state = current_state/np.max(current_state)

    # if type(current_state) != 'numpy.ndarray':
    #     print(type(current_state))
    #     raise ValueError("state must be a numpy array")

    # this should be an arbitrary array of the same size?
    # if type(target_state) != float:
    #     raise ValueError("threshold must be a float")    

    # a boolean array becomes a 0,1 array
    return np.array(current_state <= target_state).astype(float)

""" implements proportional control

"""
def Proportional(current_state, target_state, gain, scale_max=255):

    # scale state to [0,1]
    current_state = current_state/scale_max

    if type(current_state) != 'numpy.ndarray':
        current_state = np.array(current_state).astype(float)
    
    if type(target_state) != float:
        raise ValueError("target must be a float")        

    if type(gain) != float:
        raise ValueError("gain must be a float")    

    # grab elements above target state
    pixels_above_threshold = np.multiply(np.array(current_state > target_state).astype(float),current_state)
    targets_above_threshold = np.multiply(np.array(current_state > target_state).astype(float),target_state)    

    # subtract the target state 
    error = np.subtract(pixels_above_threshold, targets_above_threshold)

    # apply gain to error
    return gain*error