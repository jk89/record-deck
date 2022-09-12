import pyspark
import numpy as np
from pyspark.sql import SparkSession
import spark_context as spark_context
import kmedoids2
import sys
import json
import metrics

# connect to spark master
sc = spark_context.get_spark_context()
spark = SparkSession(sc)

if len(sys.argv) > 4:
    run_id = sys.argv[1]
    number_of_poles = int(sys.argv[2])
    infile_name = sys.argv[3]
    outfile_name = sys.argv[4]
else:
    print("Need two arguments run_id [string], number_of_poles [int], infile_name [str], outfile_name [str]")
    exit(1)

file_in = 'datasets/data/calibration-data/%s/%s' % (run_id, infile_name)
file_out = 'datasets/data/calibration-data/%s/%s' % (run_id, outfile_name)
#file_out_zc = 'datasets/data/calibration-data/%s/zero_crossing_detections.channels.all.json' % (run_id)

# sept2_test_2.jsonl.matched.csv.kalman-filtered.json.zc.json

expected_number_channel_clusters = int(number_of_poles/2)

data = None
with open(file_in, "r") as fin:
    json_str_data = fin.read()
    data = json.loads(json_str_data) 

metric = {"scalar": metrics.sum_of_squares_mod_scalar, "vector": metrics.sum_of_squares_mod_vector}

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
        #centeroid_cluster_data.append(centeroid_data)
        centroid_obj = {"centroid": centeroid_data, "cluster_members": centeroid_cluster_data}
        output.append(centroid_obj) #centeroid_cluster_data
    return output

        


output = {
    "zc_channel_ar_data": process_channel(data, "zc_channel_ar_data"),
    "zc_channel_af_data": process_channel(data, "zc_channel_af_data"),

    "zc_channel_br_data": process_channel(data, "zc_channel_br_data"),
    "zc_channel_bf_data": process_channel(data, "zc_channel_bf_data"),

    "zc_channel_cr_data": process_channel(data, "zc_channel_cr_data"),
    "zc_channel_cf_data": process_channel(data, "zc_channel_cf_data"),
}



with open(file_out, "w") as fout: #kmedoids-clustered.json"
    fout.write(json.dumps(output))
