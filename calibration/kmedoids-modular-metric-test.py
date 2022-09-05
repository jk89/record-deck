import pyspark
import numpy as np
from pyspark.sql import SparkSession
import kmedoids2

# connect to spark master
sc = pyspark.SparkContext(master="spark://10.0.0.3:6060")
sc.addPyFile("calibration/kmedoids2.py")
spark = SparkSession(sc)

# create sample 1d data
# encoder data will have a maximum value of 0 -> 16383, so be careful 16383 and 1 are for instance
# very close to each other.... 1 and 50 are much further away than 16383

data = [[16381], [16382], [16383], [0], [1], [5000], [6000], [10000]]
# [0, 1, 2, 3, 4, 5, 6]
n_clusters = 2
# two clear obvious groups here [[16381],[16382],[16383],[0],[1]] and [[5000],[6000],[10000]]

vector_stack_test1 = [
    [16381],
    [16382],
    [16383],
    [0],
    [1],
    [5000],
    [6000]
]
vector_stack_test1 = np.asarray(vector_stack_test1)

vector_stack_test2 = [
    [6000],
    [6000],
    [6000],
    [6000],
    [6000],
    [6000],
    [6000]
]
vector_stack_test2 = np.asarray(vector_stack_test2)

point_stack_test1 = [
    16381,
    16382,
    16383,
    0,
    1,
    5000,
    6000
]
point_stack_test1 = np.asarray(point_stack_test1)

point_stack_test2 = [
    6000,
    6000,
    6000,
    6000,
    6000,
    6000,
    6000
]
point_stack_test2 = np.asarray(point_stack_test2)

# vector metric
def euclidean_mod_vector(stack1, stack2):
    print("stack1.shape, stack2.shap", stack1.shape, stack2.shape)
    # need to define metrics which obey modular arithmatic
    theta_max_step = 2**14
    delta = (stack2 - stack1) % theta_max_step
    delta = np.where(delta > (theta_max_step/2), - (theta_max_step - delta), delta)
    delta = np.where(delta <= (theta_max_step/2), delta, delta)
    return np.sqrt((delta**2).sum(axis=1))# np.absolute(delta).sum(axis=1) #(delta**2).sum(axis=1) #.sum() axis=1
    # (np.absolute(stack2-stack1)).sum()

# point metric
def euclidean_mod_scalar(p1, p2): # scalar
    # need to define metrics which obey modular arithmatic
    theta_max_step = 2**14
    # p1,p2 this is the vector [angle]
    delta = (p2 - p1) % theta_max_step 
    delta = np.where(delta > (theta_max_step/2), - (theta_max_step - delta), delta)
    delta = np.where(delta <= (theta_max_step/2), delta, delta)
    return np.sqrt((delta**2).sum())# np.absolute(delta).sum() # (delta**2).sum() # np.sum((p1 - p2)**2)

metric = {"point": euclidean_mod_scalar, "vector": euclidean_mod_vector}
fit = kmedoids2.fit(sc, data, 2, metric) # seeding="random"
print(data)
print(fit)
