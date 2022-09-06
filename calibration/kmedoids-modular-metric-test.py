import numpy as np
from pyspark.sql import SparkSession
import calibration.spark_context as spark_context
import kmedoids2
import metrics

# connect to spark master
sc = spark_context.get_spark_context()

spark = SparkSession(sc)

# create sample 1d data
# encoder data will have a maximum value of 0 -> 16383, so be careful 16383 and 1 are for instance
# very close to each other.... 1 and 50 are much further away than 16383

data = [[16381], [16382], [16383], [0], [1], [5000], [6000], [10000]]
# [0, 1, 2, 3, 4, 5, 6, 7]

# 6 5, 7 & 2 0 1 3 5
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


metric = {"point": metrics.sum_of_squares_mod_scalar, "vector": metrics.sum_of_squares_mod_vector}
fit = kmedoids2.fit(sc, data, 2, metric) # seeding="random"
print(data)
print(fit)
