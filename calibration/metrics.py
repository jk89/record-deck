import numpy as np 

# need to define metrics which obey modular arithmatic

# vector metrics

def sum_of_squares_mod_vector(stack1, stack2): # euclidean_mod_vector
    theta_max_step = 2**14
    delta = (stack2 - stack1) % theta_max_step
    delta = np.where(delta > (theta_max_step/2), - (theta_max_step - delta), delta)
    delta = np.where(delta <= (theta_max_step/2), delta, delta)
    return (delta**2).sum(axis=1) #np.absolute(delta).sum(axis=1) #.sum() axis=1
    # (np.absolute(stack2-stack1)).sum()


# scalar metrics

def sum_of_squares_mod_scalar(p1, p2): # centroid is the 2nd arg # euclidean_mod_point
    theta_max_step = 2**14
    # p1,p2 this is the vector [angle]
    delta = (p2 - p1) % theta_max_step 
    delta = np.where(delta > (theta_max_step/2), - (theta_max_step - delta), delta)
    delta = np.where(delta <= (theta_max_step/2), delta, delta)
    return (delta**2).sum() # np.absolute(delta).sum() # np.sum((p1 - p2)**2)

def calculate_distance_mod_scalar(last_theta, current_theta):
    theta_max_step = 2**14
    delta = (current_theta - last_theta) % theta_max_step
    return -(theta_max_step - delta) if delta > (theta_max_step/2) else delta

def root_mean_square_mod_scalar(p1, p2):
    # need to define metrics which obey modular arithmatic
    theta_max_step = 2**14
    # p1,p2 this is the vector [angle]
    delta = (p2 - p1) % theta_max_step 
    delta = np.where(delta > (theta_max_step/2), - (theta_max_step - delta), delta)
    delta = np.where(delta <= (theta_max_step/2), delta, delta)
    n = p1.shape[0]
    return np.sqrt(((delta**2).sum()/n))

