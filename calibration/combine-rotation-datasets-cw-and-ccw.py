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
folders_description = ",".join(folders)
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
    assert sum_combined_channel == float(n_clusters), "The sum of the combined channels %f should equal the number of clusters %f" % (sum_combined_channel, float(n_clusters))
    # sum_combined_channel
    print("channel_name, sum_combined_channel", channel_name, sum_combined_channel)
    combined_normalised_hists[channel_name] = list(np_combined_channel)

print("combined_normalised_hists", combined_normalised_hists)

#next we need to plot merged_normalised_histogram howver it would be nice to display the 
# clusters with a different colour just like inspect.

# in order to do this we need iterate the angles and for each channel cluster collect
# the relelvant bits of the histogram

# merged_clustered contains cluster members
# idenfitifer identifies each angle and which cluster per channel it is (not continuous)

cluster_names = ["Cluster " + str(i+1) for i in range(n_clusters)]


combined_plot_data = {}
for channel_name in channel_names:
    combined_plot_data[channel_name] = {"angles": angles}
    for cluster_idx in range(n_clusters):
        cluster_name = cluster_names[cluster_idx]
        combined_plot_data[channel_name][cluster_name] = []
    for angle in angles:
        angle_str = str(angle)
        if str(angle_str) in identifier[channel_name]:
            cluster_idx = identifier[channel_name][str(angle)] # e.g. identifier["kernel_a_rising"][201] == 0
            cluster_name = cluster_names[cluster_idx]
            count_angle_data = combined_normalised_hists[channel_name][angle]
            combined_plot_data[channel_name][cluster_name].append(count_angle_data)
            for one_cluster_name in cluster_names:
                if one_cluster_name != cluster_name:
                    combined_plot_data[channel_name][one_cluster_name].append(0)
        else:
            for cluster_name in cluster_names:
                combined_plot_data[channel_name][cluster_name].append(0)

print("combined_plot_data", combined_plot_data)

# recover old errors

def load_analysis_files(foldername):
    folder_file_path = "./datasets/data/calibration-data/%s/kmedoids_clustered_zero_crossing_channel_detections.inliers.analysis.json" % (foldername)
    with open(folder_file_path, "r") as fin:
        return json.loads(fin.read())

analysis_files = list(map(load_analysis_files, folders))

# real all analysis files find mean-stdev mean and mean+stdev
upper={}
lower={}
base={} # dataset, channel, cluster

for analysis_file_idx in range(len(analysis_files)):
    run_name = folders[analysis_file_idx]
    analysis_file = analysis_files[analysis_file_idx]
    upper[run_name] = {}
    lower[run_name] = {}
    base[run_name] = {}
    for channel_name in channel_names:
        upper[run_name][channel_name] = {}
        lower[run_name][channel_name] = {}
        base[run_name][channel_name] = {}
        for i in range(n_clusters):
            # get mean and stdev from analysis file
            c_mean = analysis_file["mean"][channel_name][str(i)]
            c_stdev = analysis_file["stdev"][channel_name][str(i)]
            upper[run_name][channel_name][i] = (c_mean + c_stdev) % 16384
            lower[run_name][channel_name][i] = (c_mean - c_stdev)  % 16384
            base[run_name][channel_name][i] = c_mean
            pass

# calculate new errors and mean ... need weighted circular mean function
import math
def circular_mean(cluster_members, weights):
    cos_components = []
    sin_components = []
    # make cluster members unique?
    for cluster_member_angle in list(set(cluster_members)): #  # cluster_members
        weight = weights[cluster_member_angle]
        scale = (2*math.pi/16384)
        cos_components.append(weight * math.cos(scale * cluster_member_angle)) # weight *
        sin_components.append(weight * math.sin(scale * cluster_member_angle))
    np_cos_components = np.asarray(cos_components)
    np_sin_components = np.asarray(sin_components)
    mean_cos = np.sum(np_cos_components) # maybe mean
    mean_sin = np.sum(np_sin_components)

    # norm to unit vector
    #sum_means = mean_cos + mean_sin
    #mean_cos = mean_cos / sum_means
    #mean_sin = mean_sin / sum_means

    ## maybe normalise to a unit vector
    avg_angle = (np.arctan2(mean_sin, mean_cos) * (16384/(2*np.pi))) % 16384
    print("cluster_members", cluster_members)
    print("avg_angle", avg_angle)
    return avg_angle

new_mean = {}

# ok cicrular mean what do we need
for channel_name in channel_names:
    new_mean[channel_name] = {}
    for cluster_idx in range(n_clusters):
        weights = combined_plot_data[channel_name][cluster_names[cluster_idx]]
        centroid = merged_clustered[channel_name][cluster_idx]["centroid"]
        # these help us weight the mean but we also need the angles
        cluster_members = merged_clustered[channel_name][cluster_idx]["cluster_members"].copy()
        cluster_members.append(centroid)
        # flatten feature as its only 1D
        print("cluster_members", cluster_members)
        cluster_member_angles = [i[0] for i in cluster_members]
        new_mean[channel_name][cluster_idx] = circular_mean(cluster_member_angles, weights)
"""
weights
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.005952380952380952, 0.005952380952380952, 0.011904761904761904, 0.008928571428571428, 0.011904761904761904, 0.011904761904761904, 0.03273809523809524, 0.020833333333333332, 0.011904761904761904, 0.05654761904761905, 0.026785
merged_clustered 
{'zc_channel_ar_data': [{'centroid': [2424], 'cluster_members': [[2399], [2399], 
"""
print("new_mean", new_mean)

# create new standard deiation
import analyse
new_std = {}
for channel_name in channel_names:
    new_std[channel_name] = {}
    for cluster_idx in range(n_clusters):
        centroid = merged_clustered[channel_name][cluster_idx]["centroid"]
        # these help us weight the mean but we also need the angles
        cluster_members = merged_clustered[channel_name][cluster_idx]["cluster_members"].copy()
        cluster_members.append(centroid)
        # flatten feature as its only 1D
        print("cluster_members", cluster_members)
        # cluster_member_angles = [i[0] for i in cluster_members]
        new_std[channel_name][cluster_idx] = analyse.get_stdev_for_channel(cluster_members, centroid)

print("new_std", new_std)

new_upper = {}
new_lower = {}
new_base = {}

for channel_name in channel_names:
    new_upper[channel_name] = {}
    new_lower[channel_name] = {}
    new_base[channel_name] = {}
    for cluster_idx in range(n_clusters):
        c_std = new_std[channel_name][cluster_idx]
        c_mean = new_mean[channel_name][cluster_idx]
        new_upper[channel_name][cluster_idx] = c_mean + c_std
        new_lower[channel_name][cluster_idx] = c_mean - c_std
        new_base[channel_name][cluster_idx] = c_mean




from report import Report

report_title = "Combination report: %s" % (folders_description)
combination_report = Report(report_title, "./datasets/data/calibration-data/combination-report-%s.html" % (folders_description))

# channel_names = ["zc_channel_ar_data", "zc_channel_af_data", "zc_channel_br_data", "zc_channel_bf_data", "zc_channel_cr_data", "zc_channel_cf_data"]
from colour import Color

for channel_name in channel_names:
    fig = Report.figure(title=channel_name, plot_height=150, plot_width=1600)
    fig.x_range=Report.models["Range1d"](0, 18500)
    start_color = None
    end_color = None
    if channel_name == "zc_channel_ar_data" or channel_name == "zc_channel_af_data": # red
        start_color=Color("#8b0000")
        end_color=Color("#ffcccb")
    if channel_name == "zc_channel_br_data" or channel_name == "zc_channel_bf_data": # yellow
        start_color=Color("#8B8000")
        end_color=Color("#FFFF00")
    if channel_name == "zc_channel_cr_data" or channel_name == "zc_channel_cf_data": # black
        start_color=Color("#000000")
        end_color=Color("#D3D3D3")
    colors = [i.get_web() for i in list(start_color.range_to(end_color,n_clusters))]
    fig.vbar_stack(cluster_names, x='angles', source=combined_plot_data[channel_name], legend_label=cluster_names, color=colors) #color=colors,
    
    # add old errors
    for i in range(p):
        run_name = folders[i]
        _upper = upper[run_name]
        _lower = lower[run_name]
        _base = base[run_name]

        c_lower = list(_upper[channel_name].values())
        c_upper = list(_lower[channel_name].values())
        c_base = list(_base[channel_name].values())

        for cluster_idx in range(len(c_base)):
            c_c_lower = c_lower[cluster_idx]
            c_c_upper = c_upper[cluster_idx]
            c_c_base = c_base[cluster_idx]

            # add 3 lines to fig
            lower_bound_line = Report.models["Span"](location=c_c_lower, dimension='height', line_color='blue', line_dash='dashed', line_width=1)
            fig.add_layout(lower_bound_line)
            upper_bound_line = Report.models["Span"](location=c_c_upper, dimension='height', line_color='blue', line_dash='dashed', line_width=1)
            fig.add_layout(upper_bound_line)
            base_bound_line = Report.models["Span"](location=c_c_base, dimension='height', line_color='purple', line_dash='dashed', line_width=1)
            fig.add_layout(base_bound_line)
    
    # add new mean
    for cluster_idx in range(n_clusters):
        mean_value = new_mean[channel_name][cluster_idx]
        new_mean_line = Report.models["Span"](location=mean_value, dimension='height', line_color='purple', line_dash='solid', line_width=1)
        fig.add_layout(new_mean_line)

    # add new stdev
    for cluster_idx in range(n_clusters):
        upper_value = new_upper[channel_name][cluster_idx]
        lower_value = new_lower[channel_name][cluster_idx]
        base_value = new_base[channel_name][cluster_idx]
        
        new_lower_line = Report.models["Span"](location=lower_value, dimension='height', line_color='blue', line_dash='solid', line_width=1)
        fig.add_layout(new_lower_line)
        new_upper_line = Report.models["Span"](location=upper_value, dimension='height', line_color='blue', line_dash='solid', line_width=1)
        fig.add_layout(new_upper_line)

    combination_report.add_figure(fig)

def channel_name_to_descriptor(channel_name):
    # e.g. channel_names = ["zc_channel_ar_data", "zc_channel_af_data", "zc_channel_br_data", "zc_channel_bf_data", "zc_channel_cr_data", "zc_channel_cf_data"]
    if channel_name == "zc_channel_ar_data":
        return ("a", +1)
    elif channel_name == "zc_channel_af_data":
        return ("a", -1)
    elif channel_name == "zc_channel_br_data":
        return ("b", +1)
    elif channel_name == "zc_channel_bf_data":
        return ("b", -1)
    elif channel_name == "zc_channel_cr_data":
        return ("c", +1)
    elif channel_name == "zc_channel_cf_data":
        return ("c", -1)
    return None

# ok now we have the means create a spike train
# new_mean {'zc_channel_ar_data': {0: 176.06523200393107, 1:
channel_data_combined_single_transition = {"combined_channel_data": [], "angles":angles}
channel_data_combined = {"a": [], "b": [], "c": [], "angles":angles}
combined_channel_names = ["a", "b", "c"]


for angle in angles:
    #print("angle", angle, type(angle)) # int
    match = False
    for mean_zc_channel_key in new_mean.keys():
        #print("mean_zc_channel_key", mean_zc_channel_key)
        mean_zc_channel = new_mean[mean_zc_channel_key]
        mean_zc_channel_angles = list(mean_zc_channel.values())
        #print("mean_zc_channel_angles", mean_zc_channel_angles)
        for c_angle in mean_zc_channel_angles:
            i_angle = round(c_angle)
            str_c_Angle = str(i_angle)
            str_angle = str(angle)
            if str_angle == str_c_Angle:
                #match for this channel
                combined_channel_name, polarity = channel_name_to_descriptor(mean_zc_channel_key)
                channel_data_combined[combined_channel_name].append(polarity)
                channel_data_combined_single_transition["combined_channel_data"].append(abs(polarity))
                remaining_channels = list(filter(lambda x: x!=combined_channel_name, combined_channel_names))
                for remaining_channel in remaining_channels:
                    channel_data_combined[remaining_channel].append(0)
                    #channel_data_combined_single_transition[combined_channel_name].append(0)
                match = True
                #print("combined_channel_name, remaining_channels", combined_channel_name, remaining_channels)
                pass
    if match == False:
        channel_data_combined_single_transition["combined_channel_data"].append(0)
        for remaining_channel in combined_channel_names:
            channel_data_combined[remaining_channel].append(0)
            pass

print("channel_data_combined", channel_data_combined)
print("channel_data_combined_single_transition", channel_data_combined_single_transition)

# render spike train


red=Color("red")
yellow=Color("#F6BE00")
black=Color("black")

colors = [i.get_web() for i in [red, yellow, black]]

#add phase spike train

fig = Report.figure(title="Combined multichannel averaged angular zero-crossing events plot", plot_height=300, plot_width=1600) # 12000 1600 plot_width=1200, y_range=(0, 17000) plot_width=10000 # plot_width=10000,
fig.x_range=Report.models["Range1d"](0, 18500)
fig.vbar_stack(combined_channel_names, x='angles', source=channel_data_combined, legend_label=combined_channel_names, color=colors) #color=colors,
fig.xaxis.axis_label = 'Angle [steps]'
fig.yaxis.axis_label = 'Zero-crossing rising/falling detection event polarity'
combination_report.add_figure(fig)

# add binary spike train

fig = Report.figure(title="Flattened binary zero-crossing spike train", plot_height=300, plot_width=1600) # 12000 1600 plot_width=1200, y_range=(0, 17000) plot_width=10000 # plot_width=10000,
fig.x_range=Report.models["Range1d"](0, 18500)
fig.vbar_stack(["combined_channel_data"], x='angles', width=1, source=channel_data_combined_single_transition) #color=colors, legend_label=["combined_channel_data"]
fig.xaxis.axis_label = 'Angle [steps]'
fig.yaxis.axis_label = 'Binary Zero-crossing detection event spike train'

combination_report.add_figure(fig)

# temporal analysis ===========================


freqs, ps = analyse.peform_fft(channel_data_combined_single_transition["combined_channel_data"])

p = Report.figure( title="Frequency [hz] vs Power spectrum [unit] of binary spike train",
           toolbar_location=None, plot_width=800)

# np.fft.fftshift(freq), np.fft.fftshift(np.abs(X)),
#p.vbar(x=freqs, top=ps, width=0.01)
p.line(freqs, ps, line_width=1)
p.x_range=Report.models["Range1d"](0, np.max(freqs))
p.xaxis.axis_label = 'Frequency [hz]'
p.yaxis.axis_label = 'Amplitude [unit]'


#p.line(x=freqs, top=ps)
#figs.append(p)

## calculate a histogram of the spaces between consequetive spacing of spike pulse
# train. Careful of the mod, we need to match the first pulse to the last.
# so for x(0) we need distance from x(16384)

import metrics # calculate_distance_mod_scalar


bin_to_nearest= 10
pulse_hist_data = analyse.bin_modular_binary_spike_train_distances(channel_data_combined_single_transition["combined_channel_data"], bin_to_nearest)
print("pulse_hist_data", pulse_hist_data)

h = Report.figure( title="Binned histogram of consecutive pulse spike train event distances. Binned to nearest " + str(bin_to_nearest) + " angular steps.",
           toolbar_location=None,  plot_width=800)
h.vbar_stack(["ordered_pulse_hist_values"],x="ordered_pulse_hist_keys", source=pulse_hist_data) #ordered_pulse_hist_keys, ordered_pulse_hist_values)
h.yaxis.axis_label = 'Counts [number]'
h.xaxis.axis_label = 'Binned distance [angular steps]'

text="""
<h2>Temporal / spectral analysis of combined binary zero-crossing event spike train</h2>
<p>
In order to determine the peroidicity of the spike train there are two methods, one generate an fft on the spike train and look for peaks in frequency which dominate, the second
strategy is to measure the distance between each zero-crossing spike with the next spike in the train, the distances can
be rounded and binned into a historgram showing us the number occurance of spike distance of a certain binned value, if the motor is perfectly symmetrical it would be expected to see a 
dominate pulse delay time.
</p>
"""
combination_report.add_figure(Report.models["Div"](text = text))

temporal_analysis_combined_row = Report.layouts["row"]([p, h]) 
combination_report.add_figure(temporal_analysis_combined_row)



combination_report.render_to_file()