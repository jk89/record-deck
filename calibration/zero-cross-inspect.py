import sys
import json
from bokeh.palettes import Spectral6


dataset_name = sys.argv[1] if len(sys.argv) > 1 else 0 
filename = 'datasets/data/calibration-data/%s' % (dataset_name)

zc_file = filename + ".zc-hist.json"
km_file = filename + ".zc.json.kmedoids-clustered.json"

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

for channel_idx in range(len(channel_names)):
    channel_name = channel_names[channel_idx]
    hist_name = hist_names[channel_idx]
    km_channel_data = km_data[channel_name] # e.g. zc_channel_ar_data
    # km_channel_data .... 7 clusters of [[[angle1],[angle2],[angle3]],[],[],[],[],[],[]]

    identifier[hist_name] = {}

    for cluster_idx in range(len(km_channel_data)):
        channel_cluster_data = km_channel_data[cluster_idx] # each of these is an array of features [[angle1],[angle2]]
        for feature in channel_cluster_data:
            angle = feature[0] # 1d extraction
            #identifier[hist_name] # identifier['kernel_a_rising'][16321]
            identifier[hist_name][angle] = cluster_idx
            #if identifier[hist_name].has_key(angle) == False:
            #    identifier[hist_name][]
        pass
print(identifier)

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

print(plot_data)

from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, LinearAxis
from bokeh.io import show, output_file
from bokeh.transform import factor_cmap
#pip install colour

from colour import Color
# hist_names = ["kernel_a_rising", "kernel_a_falling", "kernel_b_rising", "kernel_b_falling", "kernel_c_rising", "kernel_c_falling"]

# pX_vn = figure(title="Plot of phaseX, vn and angle vs time", plot_width=1200, y_range=(0, 200))
figs = []
for hist_name in plot_data.keys():
    fig = figure(title=hist_name, plot_height=110, plot_width=12000) # 1600 plot_width=1200, y_range=(0, 17000) plot_width=10000 # plot_width=10000,
    fig.x_range=Range1d(0, 17000)
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
    #  fill_color=factor_cmap('cluster_names', palette=Spectral6, factors=cluster_names)
    figs.append(fig)

doc = curdoc()
curdoc().add_root(column(*figs))


def bohek_callback():
    pass