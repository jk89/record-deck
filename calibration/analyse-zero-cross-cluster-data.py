import sys
import json
from bokeh.palettes import Spectral6
import numpy as np
import metrics
from bokeh.plotting import output_file, save

if len(sys.argv)  > 3:
    run_id = sys.argv[1]
    filename_in_zc = sys.argv[2]
    filename_out_analysis = sys.argv[3]
else:
    print("Expected 3 arguments run_id [str], filename_in_zc[str], filename_out_analysis[str]")
    exit(1)

# kmedoids_clustered_zero_crossing_channel_detections.all.json
filename = 'datasets/data/calibration-data/%s/%s' % (run_id, filename_in_zc)
filename_out_analysis = 'datasets/data/calibration-data/%s/%s' % (run_id, filename_out_analysis)
with open(filename, "r") as fin:
    km_data = json.loads(fin.read())

number_of_clusters = len(km_data["zc_channel_ar_data"])
cluster_names = ["Cluster " + str(i+1) for i in range(number_of_clusters)]

hist_names = ["kernel_a_rising", "kernel_a_falling", "kernel_b_rising", "kernel_b_falling", "kernel_c_rising", "kernel_c_falling"]
channel_names = ["zc_channel_ar_data", "zc_channel_af_data", "zc_channel_br_data", "zc_channel_bf_data", "zc_channel_cr_data", "zc_channel_cf_data"]


identifier = {}
mean = {}
stdev = {}

for channel_idx in range(len(channel_names)):
    channel_name = channel_names[channel_idx]
    hist_name = hist_names[channel_idx]
    km_channel_data = km_data[channel_name]
    mean[channel_name] = {}
    stdev[channel_name] = {}
    identifier[hist_name] = {}
    for cluster_idx in range(len(km_channel_data)):
        channel_cluster_data_obj = km_channel_data[cluster_idx] # each of these is an array of features [[angle1],[angle2]]
        channel_cluster_data = channel_cluster_data_obj["cluster_members"].copy()
        channel_cluster_data.append(channel_cluster_data_obj["centroid"])
        mean[channel_name][cluster_idx] = channel_cluster_data_obj["centroid"][0]
        stdev[channel_name][cluster_idx]= metrics.get_stdev_for_channel(channel_cluster_data, channel_cluster_data_obj["centroid"])
        for feature in channel_cluster_data:
            angle = feature[0] # 1d extraction
            identifier[hist_name][angle] = cluster_idx

# fin kmedoids_clustered_zero_crossing_channel_detections.all.json
# filename
file_out = filename_out_analysis
data = {"mean":mean, "stdev": stdev, "channel_data_cluster_identifier": identifier}
data_json = json.dumps(data)

with open(file_out, "w") as fout:
    fout.write(data_json)
