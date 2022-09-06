import sys
import json
from bokeh.palettes import Spectral6
import numpy as np
import metrics
from bokeh.plotting import output_file, save

if len(sys.argv)  > 2:
    dataset_name = sys.argv[1]
    process_inliers = sys.argv[2]
    if process_inliers == "True":
        process_inliers = True
    elif process_inliers == "False":
        process_inliers = False
    else:
        print("Expected process_inliers='True' or process_inliers='False'")
        exit(1)
else:
    print("Expected 2 arguments dataset_name [str] and process_inliers [bool]")
    exit(1)

filename = 'datasets/data/calibration-data/%s' % (dataset_name)

zc_file = filename + ".zc-hist.json"
if process_inliers == False:
    km_file = filename + ".zc.json.kmedoids-clustered.json"
else:
# sept2_test_2.jsonl.matched.csv.kalman-filtered.json.zc-inliers.json.kmedoids-clustered-inliers.json
    km_file = filename + ".zc-inliers.json.kmedoids-clustered-inliers.json"

with open(zc_file, "r") as fin:
    zc_hist_data = json.loads(fin.read())
# [{"angle": 0, "kernel_a_rising": 0, "kernel_a_falling": 0, "kernel_b_rising": 0, "kernel_b_falling": 0, "kernel_c_rising": 0, "kernel_c_falling": 0},

with open(km_file, "r") as fin:
    km_data = json.loads(fin.read())
# {"zc_channel_ar_data": [[[201], [202], 
# zc_channel_ar_data: 7 clusters of [[[angle1],[angle2],[angle3]],[],[],[],[],[],[]]

number_of_clusters = len(km_data["zc_channel_ar_data"])
print(number_of_clusters) #7
cluster_names = ["Cluster " + str(i+1) for i in range(number_of_clusters)]
print(cluster_names)

angles = []

for angle_data in zc_hist_data:
    angles.append(angle_data["angle"])

hist_names = ["kernel_a_rising", "kernel_a_falling", "kernel_b_rising", "kernel_b_falling", "kernel_c_rising", "kernel_c_falling"]
channel_names = ["zc_channel_ar_data", "zc_channel_af_data", "zc_channel_br_data", "zc_channel_bf_data", "zc_channel_cr_data", "zc_channel_cf_data"]

#km_data
identifier = {}

mean = {}
stdev = {}

for channel_idx in range(len(channel_names)):
    channel_name = channel_names[channel_idx]
    hist_name = hist_names[channel_idx]
    # km_channel_data = km_data[channel_name] # e.g. zc_channel_ar_data
    # centroid:[angle0], cluster_members:[[angle1],[angle2],[angle3]]

    km_channel_data = km_data[channel_name]

    #print(km_data[channel_name])
    #km_channel_data = km_data[channel_name]["cluster_members"].copy()
    #km_channel_data.append(km_data[channel_name]["centroid"])
    #mean[channel_name] = km_data[channel_name]["centroid"]
    #stdev[channel_name] = get_stdev_for_channel(km_channel_data, km_data[channel_name]["centroid"])
    mean[channel_name] = {}
    stdev[channel_name] = {}
    # km_channel_data .... 7 clusters of [,[],[],[],[],[],[]]

    identifier[hist_name] = {}

    for cluster_idx in range(len(km_channel_data)):
        
        channel_cluster_data_obj = km_channel_data[cluster_idx] # each of these is an array of features [[angle1],[angle2]]
        channel_cluster_data = channel_cluster_data_obj["cluster_members"].copy()
        channel_cluster_data.append(channel_cluster_data_obj["centroid"])

        print("channel_cluster_data", channel_cluster_data)
        print('channel_cluster_data_obj["centroid"]', channel_cluster_data_obj["centroid"])
        print('channel_cluster_data_obj["cluster_members"]', channel_cluster_data_obj["cluster_members"])


    #mean[channel_name] = km_data[channel_name]["centroid"]
    #stdev[channel_name] = get_stdev_for_channel(km_channel_data, km_data[channel_name]["centroid"])

        mean[channel_name][cluster_idx] = channel_cluster_data_obj["centroid"][0]
        stdev[channel_name][cluster_idx]= metrics.get_stdev_for_channel(channel_cluster_data, channel_cluster_data_obj["centroid"])
        
        for feature in channel_cluster_data:
            angle = feature[0] # 1d extraction
            #identifier[hist_name] # identifier['kernel_a_rising'][16321]
            identifier[hist_name][angle] = cluster_idx
            #if identifier[hist_name].has_key(angle) == False:
            #    identifier[hist_name][]
        pass
#print(identifier)

print("mean stdev")

print(mean)


print("------------------")

print(stdev)

print("==============================")


## enumerate and find upper and lower bounds
"""
mean stdev
{'zc_channel_ar_data': {0: 211, 1: 9524, 2: 4725, 3: 14144, 4: 7151, 5: 11767, 6: 2474}, 'zc_channel_af_data': {0: 15273, 1: 8262, 2: 3486, 3: 12827, 4: 5811, 5: 10549, 6: 1266}, 'zc_channel_br_data': {0: 5481, 1: 12500, 2: 950, 3: 7926, 4: 14931, 5: 10235, 6: 3170}, 'zc_channel_bf_data': {0: 4277, 1: 11326, 2: 16129, 3: 6678, 4: 13680, 5: 9080, 6: 2046}, 'zc_channel_cr_data': {0: 15752, 1: 8716, 2: 3926, 3: 13301, 4: 6295, 5: 10985, 6: 1702}, 'zc_channel_cf_data': {0: 539, 1: 9847, 2: 5061, 3: 14501, 4: 7503, 5: 12096, 6: 2792}}
------------------
{'zc_channel_ar_data': {0: 3.801444513886381, 1: 3.959352294029327, 2: 3.9326004799182774, 3: 4.28136626410059, 4: 4.077677154997948, 5: 4.0523534677334085, 6: 100.18624812680376}, 'zc_channel_af_data': {0: 111.75462893043242, 1: 4.82131704404675, 2: 101.09013644403944, 3: 3.9494353033929133, 4: 108.49433073658825, 5: 4.133791878423205, 6: 4.401425793945394}, 'zc_channel_br_data': {0: 3.609709129556009, 1: 3.5864669380937024, 2: 3.9732112663424144, 3: 3.8830955914771166, 4: 4.049451598973271, 5: 3.710081654405054, 6: 214.24817116174842}, 'zc_channel_bf_data': {0: 7.599974696314152, 1: 5.3412930798361815, 2: 118.52507825248327, 3: 5.011985634456667, 4: 4.413659723728456, 5: 4.947766380586572, 6: 109.81104382772551}, 'zc_channel_cr_data': {0: 3.8704511567597315, 1: 3.9828061838406366, 2: 158.43019740876545, 3: 3.88814185168488, 4: 4.1036569057366385, 5: 3.448500668804502, 6: 3.306262625536515}, 'zc_channel_cf_data': {0: 5.163028447054891, 1: 4.098062669976976, 2: 5.181982359722058, 3: 4.300022799757156, 4: 4.70710768360976, 5: 4.576153020888641, 6: 3.988734135035826}}
"""

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

print("lower", lower)
print("upper", upper)
print("base", base)

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

    print("c_lower", c_lower)

    


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