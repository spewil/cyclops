

''' implements bang-bang control given a state and a threshold

    current state: is a numpy array

    threshold: float value above which inhibition turns on 

    returns: the on or off control signal for each state variable 
'''
def BangBang(current_state, threshold):
    
    if type(current_state) != 'numpy.ndarray':
        current_state = np.array(current_state).astype(float)
   
    if type(threshold) != float:
        raise ValueError("threshold must be a float")    
    
    # a boolean array becomes a 0,1 array
    return np.array(current_state >= threshold).astype(float)