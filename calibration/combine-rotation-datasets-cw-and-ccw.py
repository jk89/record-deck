import numpy as np
import sys
import json
import kmedoids2

run_ids = sys.argv[1] if len(sys.argv) > 1 else 0
print(run_ids)
if (run_ids == 0):
    print("Need to provide run_ids [str] e.g. sept2,sept3")
    exit()

#run_ids are comma seperated folder names
run_ids = run_ids.replace("run_ids=", "")
folders = run_ids.split(",")

p = len(folders)
if (p % 2 != 0):
    print("Need to provide equal numbers of cw and ccw runs")
    exit()


def find_number_of_clusters(foldername):
    filename_in_old_analysis = "./datasets/data/calibration-data/%s/kmedoids_clustered_zero_crossing_channel_detections.inliers.analysis.json" % (foldername)
    with open(filename_in_old_analysis, "r") as fin:
        data = json.loads(fin.read())
        number_of_clusters = len(list(data["mean"]["zc_channel_ar_data"].keys()))
    return number_of_clusters
    # {"mean": {"zc_channel_ar_data": {keys}

n_clusters = find_number_of_clusters(folders[0]) # should validate this
print("n_clusters", n_clusters)

print("folders", folders)
def load_inliers_files(foldername):
    folder_file_path = "./datasets/data/calibration-data/%s/zero_crossing_detections.channels.inliers.json" % (foldername)
    with open(folder_file_path, "r") as fin:
        return json.loads(fin.read())

# get datasets
datasets = list(map(lambda foldername: load_inliers_files(foldername), folders))

hist_names = ["kernel_a_rising", "kernel_a_falling", "kernel_b_rising", "kernel_b_falling", "kernel_c_rising", "kernel_c_falling"]
channel_names = ["zc_channel_ar_data", "zc_channel_af_data", "zc_channel_br_data", "zc_channel_bf_data", "zc_channel_cr_data", "zc_channel_cf_data"]

angles = [i for i in range(2**14)]
#print("angles", angles)
def convert_zc_inliers_to_hist(dataset):
    # dataset {zc_channel_ar_data: [[angle],[angle],....]}
    # iterate the angles
    # for each channel

    #for angle in angles:
   #     row = {angle: angle}

    binned_channel_data = {}
    for channel_name in channel_names:
        binned_channel_data[channel_name] = {}
        channel_data = dataset[channel_name]
        for data_point in channel_data:
            angle = data_point[0]
            if angle in binned_channel_data[channel_name]:
                binned_channel_data[channel_name][angle] += 1
            else:
                binned_channel_data[channel_name][angle] = 1
    # add zeros
    # binned_channel_data
    for channel_name in channel_names:
        for angle in angles:
            if angle not in binned_channel_data[channel_name]:
                binned_channel_data[channel_name][angle] = 0
            

    #print("binned_channel_data", binned_channel_data)
    ordered_binned_channel_data = {}
    for channel_name in channel_names:
        ordered_binned_channel_data[channel_name] = {}
        for angle in angles:
            count = binned_channel_data[channel_name][angle]
            ordered_binned_channel_data[channel_name][angle] = count

    #print("ordered_binned_channel_data", ordered_binned_channel_data)

    output = {}
    # extract historgrams
    for channel_name in channel_names:
        channel_data = ordered_binned_channel_data[channel_name]
        channel_data_keys = list(channel_data.keys())
        channel_data_values = [] #channel_data.values()
        for channel_data_key in channel_data_keys:
            channel_data_values.append(channel_data[channel_data_key])
        output[channel_name] = {"angles": channel_data_keys, "data": channel_data_values}
    return output


histograms = list(map(convert_zc_inliers_to_hist, datasets))

print("histograms", histograms)

#merged_histograms = list(map(,histograms)) # reduce? map angles?
merged_channel_hists = {}
for channel_name in channel_names:
    np_channel_data = None
    np_channel_data_set = False
    for dataset_idx in range(p):
        channel_hist = histograms[dataset_idx][channel_name]["data"]
        np_channel_hist = np.asarray(channel_hist)
        if np_channel_data_set == False:
            np_channel_data_set = True
            np_channel_data = np_channel_hist
        else:
            #concat
            np_channel_data = np_channel_data + np_channel_hist 
    channel_data = list(np_channel_data)
    #channel_data = [[i] for i in channel_data]
    merged_channel_hists[channel_name] = channel_data

print("merged_channel_hists", merged_channel_hists)

# ok now reconstruct channel angles from merged_channel_hists
channel_angles = {}
for channel_name in channel_names:
    channel_angles[channel_name] = []
    # merged_channel_hists[channel_name] like  {'zc_channel_ar_data': [0, 0, 0, 0, 0, 0, 0, 10....], 'zc...'
    for histogram_value_idx in range(len(merged_channel_hists[channel_name])):
        angle = histogram_value_idx
        histogram_value = merged_channel_hists[channel_name][histogram_value_idx]
        # histogram_value e.g. 0 or some count 12 etc
        for i in range(histogram_value):
            channel_angles[channel_name].append([angle])

print("channel_angles", channel_angles)

# so cluster this!

import spark_context as spark_context
from pyspark.sql import SparkSession
import metrics 

sc = spark_context.get_spark_context()
spark = SparkSession(sc)

metric = {"scalar": metrics.sum_of_squares_mod_scalar, "vector": metrics.sum_of_squares_mod_vector}

def fit_merged(): # same format as kmedoids_clustered_zero_crossing_channel_detections.inliers.json
    final_output = {}
    # we need to know number of expected_number_channel_cluster
    for channel_name in channel_names:
        final_output[channel_name] = []
        channel_data = channel_angles[channel_name] # n_clusters
        fit = kmedoids2.fit(sc, channel_data, n_clusters, metric)
        centroids = fit[0]
        clusters = fit[1]
        for centeroid_idx in range(len(centroids)):
            centeroid_id = centroids[centeroid_idx]
            centeroid_cluster = clusters[centeroid_idx]
            centeroid_data = channel_data[centeroid_id]
            centeroid_cluster_data = [channel_data[i] for i in centeroid_cluster]
            centroid_obj = {"centroid": centeroid_data, "cluster_members": centeroid_cluster_data}
            final_output[channel_name].append(centroid_obj)
    return final_output

merged_clustered = fit_merged()
print("merged_clustered", merged_clustered)

# ok now with merged dataset we need to build an identifier obj
# which for each channel and for each angle idenfitifies a cluster id
def get_cluster_identifier(merged_clustered):
    identifier = {}
    for channel_name in channel_names:
        identifier[channel_name] = {}
        merged_clustered_channel_data = merged_clustered[channel_name]
        # merged_clustered_channel_data like [{'centroid': [2424], 'cluster_members': 
        for cluster_idx in range(len(merged_clustered_channel_data)):
            cluster_members = merged_clustered_channel_data[cluster_idx]["cluster_members"].copy()
            cluster_members.append(merged_clustered_channel_data[cluster_idx]["centroid"])
            # so cluster_members are like [[angle],[angle],[angle],...etc]
            for angle_feature in cluster_members:
                angle = angle_feature[0]
                identifier[channel_name][str(angle)] = cluster_idx
    return identifier

identifier = get_cluster_identifier(merged_clustered)
print("identifier", identifier)

# identifier like {'zc_channel_ar_data': {'14060': 0, '14064': 0, 

# collect the counts

dataset_channel_cluster_counts = {}
for histogram_idx in range(len(histograms)):
    histogram = histograms[histogram_idx]
    run_id = folders[histogram_idx]
    dataset_channel_cluster_counts[run_id] = {}
    for channel_name in channel_names:
        dataset_channel_histogram = histogram[channel_name]["data"] # counts per angle
        dataset_channel_cluster_counts[run_id][channel_name] = {}
        # this is to hold cluster_idx vs count
        # identifier
        # iterate angles
        for angle in angles:
            str_angle = str(angle)
            count = dataset_channel_histogram[angle]
            cluster_idx = None 
            if str_angle in identifier[channel_name]:
                cluster_idx = identifier[channel_name][str_angle]
            if cluster_idx is not None and count != 0:
                if cluster_idx in dataset_channel_cluster_counts[run_id][channel_name]:
                    dataset_channel_cluster_counts[run_id][channel_name][cluster_idx] += count
                else:
                    dataset_channel_cluster_counts[run_id][channel_name][cluster_idx] = count
            #cluster_idx = ifstr_angle in identifier[channel_name] 

"""
histograms like
[ # dataset1 data
    {'zc_channel_ar_data': {'angles': [.............],
'data': [0, 0, 0, 0, 0, 0, 1, 1, 0, 3, 3, 3, 3, 7, 8, 1]}, {}, {}, {}, {}, {}
,
dataset2 data
]
"""

print("dataset_channel_cluster_counts", dataset_channel_cluster_counts)

"""
dataset_channel_cluster_counts data like
16sept-ccw
: 
zc_channel_af_data
: 
{0: 137, 1: 138, 2: 135, 3: 136, 4: 141, 5: 140, 6: 134}

"""

# next now we have dataset_channel_cluster_counts we can attempt to normalise each
# of the histograms

# for each histogram channel we can iterate every angle
# we can use identifier to find that angles cluster_idx
# we can get from the histogram the counts (non-zero) for this angle if it is identifier
# and we can use dataset_channel_cluster_counts to find the channel cluster total

def weight_histogram(histogram_idx, histogram):
    output = {}
    for channel_name in channel_names:
        output[channel_name] = []
        channel_histogram_data = histogram[channel_name]["data"]
        for angle in angles:
            str_angle = str(angle)
            counts = channel_histogram_data[angle]
            if counts == 0:
                output[channel_name].append(0)
                continue
            cluster_idx = None
            if str_angle in identifier[channel_name]:
                cluster_idx = identifier[channel_name][str_angle]
            if cluster_idx is None:
                raise ("Error happened angle, channel_name, dataset_idx, cluster idx", angle, channel_name, histogram_idx, cluster_idx)
            cluster_n = dataset_channel_cluster_counts[folders[histogram_idx]][channel_name][cluster_idx]
            weighted_count = float(counts) / (float(cluster_n) * p) # missing p
            output[channel_name].append(weighted_count)
    return output

id_hist = list(map(lambda x: (x, histograms[x]),range(p)))
weighted_hists = list(map(lambda x: weight_histogram(x[0], x[1]), id_hist))
# using bind would be more functional list=[1,2] list.bind(str) == ["1", "2"] could use lambda as bind arg
print("weighted hist", weighted_hists)
## like [{'zc_channel_ar_data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
# now combine
combined_normalised_hists = {}
for channel_name in channel_names:
    #combined_normalised_hists[channel_name]
    np_combined_channel = None
    channel_set = False
    for i in range(p):
        c_dataset_channel_hist = weighted_hists[i][channel_name]
        if channel_set == False:
            np_combined_channel = np.asarray(c_dataset_channel_hist)
            channel_set = True
        else:
            np_combined_channel = np_combined_channel + np.asarray(c_dataset_channel_hist)
    # calculate sum of the channel
    sum_combined_channel = np.sum(np_combined_channel)
    print("channel_name, sum_combined_channel", channel_name, sum_combined_channel)
    combined_normalised_hists[channel_name] = list(np_combined_channel)

print("combined_normalised_hists", combined_normalised_hists)