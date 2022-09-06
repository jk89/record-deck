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

def get_pairwise_distances_for_channel(km_channel_data, centroid):
    cluster_column = []
    centeroid_column = []
    for i in range(0, len(km_channel_data)):
        cluster_column.append(km_channel_data[i])
        centeroid_column.append(centroid)
    cluster_column = np.asarray(cluster_column)
    centeroid_column = np.asarray(centeroid_column)
    return np.sqrt(sum_of_squares_mod_vector(cluster_column, centeroid_column))

# scalar metrics

def sum_of_squares_mod_scalar(p1, p2): # centroid is the 2nd arg # euclidean_mod_point
    theta_max_step = 2**14
    # p1,p2 this is the vector [angle]
    delta = (p2 - p1) % theta_max_step 
    delta = np.where(delta > (theta_max_step/2), - (theta_max_step - delta), delta)
    delta = np.where(delta <= (theta_max_step/2), delta, delta)
    return (delta**2).sum() # np.absolute(delta).sum() # np.sum((p1 - p2)**2)

def root_mean_square_mod_scalar(p1, p2):
    # need to define metrics which obey modular arithmatic
    theta_max_step = 2**14
    # p1,p2 this is the vector [angle]
    delta = (p2 - p1) % theta_max_step 
    delta = np.where(delta > (theta_max_step/2), - (theta_max_step - delta), delta)
    delta = np.where(delta <= (theta_max_step/2), delta, delta)
    n = p1.shape[0]
    return np.sqrt(((delta**2).sum()/n))

def get_stdev_for_channel(km_channel_data, centroid):
    #np_km_channel_data = np.asarray(km_channel_data)
    cluster_column = []
    centeroid_column = []
    for i in range(0, len(km_channel_data)):
        cluster_column.append(km_channel_data[i])
        centeroid_column.append(centroid)
    cluster_column = np.asarray(cluster_column)
    centeroid_column = np.asarray(centeroid_column)
    st_dev = root_mean_square_mod_scalar(cluster_column, centeroid_column)
    return st_dev
