import sys
import json
from bokeh.palettes import Spectral6
import numpy as np
import metrics
from bokeh.plotting import output_file, save

if len(sys.argv)  > 2:
    run_id = sys.argv[1]
    process_inliers = sys.argv[2]
else:
    print("Expected 2 arguments run_id [str] and process_inliers [bool]")
    exit(1)

#
filename_in_zc_inliers = 'datasets/data/calibration-data/%s/zero_crossing_detections.channels.inliers.json' % (run_id)
filename_analysis = 'datasets/data/calibration-data/%s/kmedoids_clustered_zero_crossing_channel_detections.all.analysis.json' % (run_id)
filename_hist = 'datasets/data/calibration-data/%s/zero_crossing_detections.histogram.all.json' % (run_id)

with open(filename_hist, "r") as fin:
    zc_hist_data = json.loads(fin.read())

with open(filename_in_zc_inliers, "r") as fin:
    km_data = json.loads(fin.read())

with open(filename_analysis, "r") as fin:
    analysis = json.loads(fin.read())

number_of_clusters = len(km_data["zc_channel_ar_data"])
cluster_names = ["Cluster " + str(i+1) for i in range(number_of_clusters)]

angles = []

for angle_data in zc_hist_data:
    angles.append(angle_data["angle"])

hist_names = ["kernel_a_rising", "kernel_a_falling", "kernel_b_rising", "kernel_b_falling", "kernel_c_rising", "kernel_c_falling"]
channel_names = ["zc_channel_ar_data", "zc_channel_af_data", "zc_channel_br_data", "zc_channel_bf_data", "zc_channel_cr_data", "zc_channel_cf_data"]

identifier = analysis["channel_data_cluster_identifier"]
mean = analysis["mean"]
stdev = analysis["stdev"]

for channel_idx in range(len(channel_names)):
    channel_name = channel_names[channel_idx]
    hist_name = hist_names[channel_idx]
    km_channel_data = km_data[channel_name]
    for cluster_idx in range(len(km_channel_data)):
        channel_cluster_data_obj = km_channel_data[cluster_idx] # each of these is an array of features [[angle1],[angle2]]
        channel_cluster_data = channel_cluster_data_obj["cluster_members"].copy()
        channel_cluster_data.append(channel_cluster_data_obj["centroid"])

upper={}
lower={}
base={}

for channel_name in channel_names:
    #mean = mean[channel_name]
    upper[channel_name] = {}
    lower[channel_name] = {}
    base[channel_name] = {}
    for i in range(number_of_clusters):
        c_mean = mean[channel_name][i]
        c_stdev = stdev[channel_name][i]
        upper[channel_name][i] = (c_mean + c_stdev) % 16384
        lower[channel_name][i] = (c_mean - c_stdev)  % 16384
        base[channel_name][i] = c_mean

plot_data = {}
max_value = 0
for channel_idx in range(len(channel_names)):
    channel_name = channel_names[channel_idx] # 'kernel_a_rising'
    hist_name = hist_names[channel_idx] # 'zc_channel_ar_data'
    plot_data[hist_name] = {"angles":angles} # e.g. plot_data["kernel_a_rising"] = {"angles":angles}

    for cluster_name in cluster_names:
        plot_data[hist_name][cluster_name] = []
     # e.g. plot_data["kernel_a_rising"] = {"angles":angles, "Cluster1":[], "Cluster2":[], "Cluster3":[], "Cluster4":[], "Cluster5":[], "Cluster6":[]}

    for angle_data in zc_hist_data:
        angle = angle_data["angle"]
        # print("hist name", hist_name, "identifier[hist_name]", identifier[hist_name], angle)

        if angle in identifier[hist_name]:
            cluster_idx = identifier[hist_name][angle] # e.g. identifier["kernel_a_rising"][201] == 0
            cluster_name = cluster_names[cluster_idx]
            plot_data[hist_name][cluster_name].append(angle_data[hist_name])
            if angle_data[hist_name] > max_value:
                max_value = angle_data[hist_name]
            for one_cluster_name in cluster_names:
                if one_cluster_name != cluster_name:
                    plot_data[hist_name][one_cluster_name].append(0)
            #excluded_clusters = [i for i in cluster_names if i != cluster_name]
            #plot_data[hist_name][cluster_name].append(0)
        else:
            for cluster_name in cluster_names:
                plot_data[hist_name][cluster_name].append(0)


from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, LinearAxis, Whisker, Span
from bokeh.io import show, output_file
from bokeh.transform import factor_cmap
#pip install colour

from colour import Color
# hist_names = ["kernel_a_rising", "kernel_a_falling", "kernel_b_rising", "kernel_b_falling", "kernel_c_rising", "kernel_c_falling"]

# pX_vn = figure(title="Plot of phaseX, vn and angle vs time", plot_width=1200, y_range=(0, 200))
figs = []
for hist_name_idx in range(len(hist_names)): #plot_data.keys():
    #print("hist_name_idx", hist_name_idx, hist_names)
    hist_name = hist_names[hist_name_idx]
    channel_name = channel_names[hist_name_idx]
    fig = figure(title=hist_name, plot_height=150, plot_width=1600) # 12000 1600 plot_width=1200, y_range=(0, 17000) plot_width=10000 # plot_width=10000,
    fig.x_range=Range1d(0, 18500)
    start_color = None
    end_color = None
    if hist_name == "kernel_a_rising" or hist_name == "kernel_a_falling": # red
        start_color=Color("#8b0000")
        end_color=Color("#ffcccb")
    if hist_name == "kernel_b_rising" or hist_name == "kernel_b_falling": # yellow
        start_color=Color("#8B8000")
        end_color=Color("#FFFF00")
    if hist_name == "kernel_c_rising" or hist_name == "kernel_c_falling": # black
        start_color=Color("#000000")
        end_color=Color("#D3D3D3")
    colors = [i.get_web() for i in list(start_color.range_to(end_color,number_of_clusters))]
    fig.vbar_stack(cluster_names, x='angles', source=plot_data[hist_name], legend_label=cluster_names, color=colors) #color=colors,
    
    # get base lower and upper
    c_lower = list(lower[channel_name].values())
    c_upper = list(upper[channel_name].values())
    c_base = list(base[channel_name].values())

    for cluster_idx in range(len(c_base)):
        c_c_lower = c_lower[cluster_idx]
        c_c_upper = c_upper[cluster_idx]
        c_c_base = c_base[cluster_idx]

        # add 3 lines to fig
        lower_bound_line = Span(location=c_c_lower, dimension='height', line_color='blue', line_dash='dashed', line_width=1)
        fig.add_layout(lower_bound_line)
        upper_bound_line = Span(location=c_c_upper, dimension='height', line_color='blue', line_dash='dashed', line_width=1)
        fig.add_layout(upper_bound_line)
        base_bound_line = Span(location=c_c_base, dimension='height', line_color='purple', line_dash='dashed', line_width=1)
        fig.add_layout(base_bound_line)

    #source_error = ColumnDataSource(data=dict(base=c_base, lower=c_lower, upper=c_upper))

    #fig.add_layout(
    #    Whisker(source=source_error, base="base", upper="upper", lower="lower", dimension="height")
    #)
    #  fill_color=factor_cmap('cluster_names', palette=Spectral6, factors=cluster_names)
    figs.append(fig)

# eliminate outliers

filtered_channel_data={}
channel_data_outliers={}
number_of_standard_deviations = 3

for channel_idx in range(len(channel_names)):
    channel_name = channel_names[channel_idx] # 'kernel_a_rising'
    hist_name = hist_names[channel_idx] # 'zc_channel_ar_data'
    km_channel_data = km_data[channel_name]
    filtered_channel_data[channel_name] = []
    channel_data_outliers[channel_name] = []
    # for each cluster
    for cluster_idx in range(len(km_channel_data)):
        
        channel_cluster_data_obj = km_channel_data[cluster_idx] # each of these is an array of features [[angle1],[angle2]]
        channel_cluster_data = channel_cluster_data_obj["cluster_members"].copy()
        channel_cluster_data.append(channel_cluster_data_obj["centroid"])

        c_stdev = stdev[channel_name][cluster_idx]

        pairwise_distances = metrics.get_pairwise_distances_for_channel(channel_cluster_data, channel_cluster_data_obj["centroid"])
        inliers = []
        outliers = []
        #channel_cluster_data
        for cluster_data_idx in range(len(channel_cluster_data)):
            distance = pairwise_distances[cluster_data_idx]
            if distance > (c_stdev*number_of_standard_deviations):
                outliers.append(channel_cluster_data[cluster_data_idx])
            else:
                inliers.append(channel_cluster_data[cluster_data_idx])
                filtered_channel_data[channel_name].append(channel_cluster_data[cluster_data_idx])
        #filtered_channel_data[channel_name].append(inliers)
        channel_data_outliers[channel_name].append(outliers)
        
print("filtered_channel_data",filtered_channel_data)
print("-------------------------------")
print("channel_data_outliers", channel_data_outliers)



zc_clusters_without_outliers_file = filename + ".zc-inliers.json"
zc_clusters_outliers = filename + ".zc-outliers.json"

if process_inliers == False:
    with open(zc_clusters_without_outliers_file, "w") as fout:
        fout.write(json.dumps(filtered_channel_data))

    with open(zc_clusters_outliers, "w") as fout:
        fout.write(json.dumps(channel_data_outliers))

doc = curdoc()
curdoc().add_root(column(*figs))

if process_inliers == False: # first run with outliers
    output_file(filename=filename+".clustering_with_outliers.html", title="Channel clusters for zero-crossing histogram with outliers")
else:
    output_file(filename=filename+".clustering_inliers.html", title="Channel clusters for zero-crossing histogram without outliers")


save(doc)

def bohek_callback():
    pass