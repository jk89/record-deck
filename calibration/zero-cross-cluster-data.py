import pyspark
import numpy as np
from pyspark.sql import SparkSession
import kmedoids2
import sys
import json

# connect to spark master
sc = pyspark.SparkContext(master="spark://10.0.0.3:6060")
sc.addPyFile("calibration/kmedoids2.py")
spark = SparkSession(sc)

# vector metric
def euclidean_mod_vector(stack1, stack2):
    print("stack1.shape, stack2.shap", stack1.shape, stack2.shape)
    # need to define metrics which obey modular arithmatic
    theta_max_step = 2**14
    delta = (stack2 - stack1) % theta_max_step
    delta = np.where(delta > (theta_max_step/2), - (theta_max_step - delta), delta)
    delta = np.where(delta <= (theta_max_step/2), delta, delta)
    return np.absolute(delta).sum(axis=1) #.sum() axis=1
    # (np.absolute(stack2-stack1)).sum()

# point metric
def euclidean_mod_point(p1, p2):
    # need to define metrics which obey modular arithmatic
    theta_max_step = 2**14
    # p1,p2 this is the vector [angle]
    delta = (p2 - p1) % theta_max_step 
    delta = np.where(delta > (theta_max_step/2), - (theta_max_step - delta), delta)
    delta = np.where(delta <= (theta_max_step/2), delta, delta)
    return np.absolute(delta).sum() # np.sum((p1 - p2)**2)

if len(sys.argv) > 2:
    dataset_name = sys.argv[1]
    number_of_poles = int(sys.argv[2])
else:
    print("Need two arguments dataset_name [string] and number_of_poles [int]")
    exit(1)

filename = 'datasets/data/calibration-data/%s' % (dataset_name)
expected_number_channel_clusters = int(number_of_poles/2)

data = None
with open(filename, "r") as fin:
    json_str_data = fin.read()
    data = json.loads(json_str_data) 

metric = {"point": euclidean_mod_point, "vector": euclidean_mod_vector}

# process all the data

# output = {"angle": angle_data, "zc_channel_ar_data": zc_channel_ar_data, "zc_channel_af_data": zc_channel_af_data, "zc_channel_br_data": zc_channel_br_data, "zc_channel_bf_data": zc_channel_bf_data, "zc_channel_cr_data": zc_channel_cr_data, "zc_channel_cf_data": zc_channel_cf_data}

zc_channel_ar_cluster_data = None
zc_channel_af_cluster_data = None
zc_channel_br_cluster_data = None
zc_channel_bf_cluster_data = None
zc_channel_cr_cluster_data = None
zc_channel_cf_cluster_data = None


# {"zc_channel_ar_data": [[354, 654, 147, 554, 250, 50, 454], [[305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 355, 356, 357, 358, 359, 36

def process_channel(data, channel_name):
    channel_data = data[channel_name]
    fit = kmedoids2.fit(sc, channel_data, expected_number_channel_clusters, metric) # seeding="random"
    centroids = fit[0]
    clusters = fit[1]

    output = []

    for centeroid_idx in range(len(centroids)):
        centeroid_id = centroids[centeroid_idx]
        centeroid_cluster = clusters[centeroid_idx]

        print("channel_data", channel_data)
        print("centeroid_idx", centeroid_idx)
        print("centeroid_id", centeroid_id)
        print("centeroid_cluster", centeroid_cluster)

        centeroid_data = channel_data[centeroid_id]
        centeroid_cluster_data = [channel_data[i] for i in centeroid_cluster]
        centeroid_cluster_data.append(centeroid_data)

        output.append(centeroid_cluster_data)
    
    return output

        


output = {
    "zc_channel_ar_data": process_channel(data, "zc_channel_ar_data"),
    "zc_channel_af_data": process_channel(data, "zc_channel_af_data"),

    "zc_channel_br_data": process_channel(data, "zc_channel_br_data"),
    "zc_channel_bf_data": process_channel(data, "zc_channel_bf_data"),

    "zc_channel_cr_data": process_channel(data, "zc_channel_cr_data"),
    "zc_channel_cf_data": process_channel(data, "zc_channel_cf_data"),
}



with open(filename + ".kmedoids-clustered.json", "w") as fout:
    fout.write(json.dumps(output))
