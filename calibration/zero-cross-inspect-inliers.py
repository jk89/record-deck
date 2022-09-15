import sys
import json
from typing import List
from bokeh.palettes import Spectral6
import numpy as np
import metrics
from bokeh.plotting import output_file, save

if len(sys.argv)  > 1:
    run_id = sys.argv[1]
else:
    print("Expected 2 arguments run_id [str]")
    exit(1)

# kmedoids_clustered_zero_crossing_channel_detections.inliers.json
filename_in_zc_inliers = 'datasets/data/calibration-data/%s/kmedoids_clustered_zero_crossing_channel_detections.inliers.json' % (run_id)
filename_analysis = 'datasets/data/calibration-data/%s/kmedoids_clustered_zero_crossing_channel_detections.inliers.analysis.json' % (run_id)
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
    #print("km_channel_data", km_channel_data)
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
        c_mean = mean[channel_name][str(i)]
        c_stdev = stdev[channel_name][str(i)]
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
    for angle_data in zc_hist_data:
        angle = angle_data["angle"]
        if str(angle) in identifier[hist_name]:
            cluster_idx = identifier[hist_name][str(angle)] # e.g. identifier["kernel_a_rising"][201] == 0
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
from bokeh.models import ColumnDataSource, Range1d, LinearAxis, Whisker, Span, Div
from bokeh.io import show, output_file
from bokeh.transform import factor_cmap
#pip install colour

from colour import Color
# hist_names = ["kernel_a_rising", "kernel_a_falling", "kernel_b_rising", "kernel_b_falling", "kernel_c_rising", "kernel_c_falling"]

# pX_vn = figure(title="Plot of phaseX, vn and angle vs time", plot_width=1200, y_range=(0, 200))
figs = []

# create title div
# number_of_clusters
text="""
<h1>Zero-crossing analysis:</h1>
<h2>Zero-crossing kernel output plot</h2>
<p>
Here we can see the three phases split into 2 channels each (one for a rising zero-crossing detection and one for a falling zero-crossing detection per channel). Then for each channel the zero-crossing are clusted based on their modular distance from each other.
The number of poles (e.g. NUM_POLES) divided by 2 (e.g. NUM_CLUSTERS) give us an indication of the number of zero-crossing cluster there are per channel (e.g. 7).
The distribution of zero crossing occurances (counts) is plotted, along with the mean (purple) and standard deviation (blue). Outliers beyond some constant beyond the standard deviation of each zero crossing cluster per channel
have been eliminated.
</p>
"""
text = text.replace('NUM_CLUSTERS', str(number_of_clusters))
text = text.replace('NUM_POLES', str(number_of_clusters * 2))

figs.append(Div(text=text))

for hist_name_idx in range(len(hist_names)): #plot_data.keys():
    #print("hist_name_idx", hist_name_idx, hist_names)
    hist_name = hist_names[hist_name_idx]
    channel_name = channel_names[hist_name_idx]
    # hist_name e.g. kernel_a_rising
    full_plot_title = "Plot of zero-crossing detection counts [number] vs angle [step] for channel " + hist_name 
    fig = figure(title=full_plot_title, plot_height=150, plot_width=1600) # 12000 1600 plot_width=1200, y_range=(0, 17000) plot_width=10000 # plot_width=10000,
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
    
    #fig.xaxis.axis_label = 'Angle [steps]'
    fig.yaxis.axis_label = 'Counts [number]'
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


# calculate zc map histogram
# mean

"""
mean": {"zc_channel_ar_data": {"0": 7150, "1": 14144, "2": 2474, "3": 11767, "4": 4725, "5": 210, "6": 9524}, "zc_channel_af_data": {"0": 1266, "1": 10549, "2": 5811, "3": 15274, "4": 12827, "5": 8262, "6": 3486}, "zc_channel_br_data": {"0": 7925, "1": 14930, "2": 3170, "3": 12500, "4": 5481, "5": 10236, "6": 950}, "zc_channel_bf_data": {"0": 4277, "1": 11325, "2": 16129, "3": 6678, "4": 13680, "5": 9081, "6": 2046}, "zc_channel_cr_data": {"0": 8716, "1": 15751, "2": 3926, "3": 13301, "4": 6295, "5": 10985, "6": 1703}, "zc_channel_cf_data": {"0": 12096, "1": 2792, "2": 7503, "3": 14501, "4": 539, "5": 5061, "6": 9847}
"""

# iterate each angle
# for each channel
# see if angle exists in channel

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

channel_data_combined = {"a": [], "b": [], "c": [], "angles":angles}
combined_channel_names = ["a", "b", "c"]

channel_data_combined_single_transition = {"combined_channel_data": [], "angles":angles}
# , "b": [], "c": [], 

for angle in angles:
    #print("angle", angle, type(angle)) # int
    match = False
    for mean_zc_channel_key in mean.keys():
        #print("mean_zc_channel_key", mean_zc_channel_key)
        mean_zc_channel = mean[mean_zc_channel_key]
        mean_zc_channel_angles = list(mean_zc_channel.values())
        #print("mean_zc_channel_angles", mean_zc_channel_angles)
        for c_angle in mean_zc_channel_angles:
            str_c_Angle = str(c_angle)
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
        # 
        channel_data_combined_single_transition["combined_channel_data"].append(0)
        for remaining_channel in combined_channel_names:
            channel_data_combined[remaining_channel].append(0)
            pass

figs.append(Div(text="""
<h2>Channel cluster population density</h2>
<p>
For each channel there exists a certain number of clusters (by angle) of zero crossing detections as determined by the motor systems pole count divided by 2. 
The population count for each channel cluster should be well balanced.
</p>
"""))

# process cluster membership
# for each channel 1->6
# for each cluster 
for hist_name_idx in range(len(hist_names)): #plot_data.keys():
    #print("hist_name_idx", hist_name_idx, hist_names)
    hist_name = hist_names[hist_name_idx]
    channel_name = channel_names[hist_name_idx] # this is what we use to lookup a channels cluster membership
    km_channel_data = km_data[channel_name]

    cluster_density = {}
    #print("km_channel_data", km_channel_data)
    for cluster_idx in range(len(km_channel_data)):
        cluster_count = len(km_channel_data[cluster_idx]["cluster_members"]) + 1
        cluster_density[cluster_idx] = cluster_count
    
    # flatten to 2 arrays
    cluster_density_keys = list(cluster_density.keys())
    cluster_density_values = []
    for cluster_density_key in cluster_density_keys:
        cluster_density_values.append(cluster_density[cluster_density_key])
    cluster_density_obj = {"cluster_density_keys" : cluster_density_keys, "cluster_density_values":cluster_density_values}
    
    fig = figure( title="Channel cluster density for " + str(hist_name) + ".",
           toolbar_location=None,  plot_width=1600, plot_height=150)
    fig.vbar_stack(["cluster_density_values"],x="cluster_density_keys", source=cluster_density_obj, width=0.01) #ordered_pulse_hist_keys, ordered_pulse_hist_values)
    fig.xaxis.axis_label = 'Cluster identifier'
    fig.yaxis.axis_label = 'Counts [number]'
    figs.append(fig)

    #fig = 

    # km_data[channel_name] = [{centroid, cluster_members},{},.. etc]
    




figs.append(Div(text="""
<h2>Combined phase zero-crossing plot</h2>
<p>
Post clustering, the mean of each channels zero-crossing channel detections is known. Therefore we can reduce the data so that there is only a single definitive pulse (rising or falling) for every cluster within each zero-crossing channel. The combined zero-crossing
events are combined into a single plot.
Note that whether or not a zero-crossing event is rising or falling is depicted by the polarity of the spike +1 indicates rising and -1 indicates falling for that phase.
</p>
"""))

red=Color("red")
yellow=Color("#F6BE00")
black=Color("black")

colors = [i.get_web() for i in [red, yellow, black]]

fig = figure(title="Combined multichannel averaged angular zero-crossing events plot", plot_height=300, plot_width=1600) # 12000 1600 plot_width=1200, y_range=(0, 17000) plot_width=10000 # plot_width=10000,
fig.x_range=Range1d(0, 18500)
fig.vbar_stack(combined_channel_names, x='angles', source=channel_data_combined, legend_label=combined_channel_names, color=colors) #color=colors,
fig.xaxis.axis_label = 'Angle [steps]'
fig.yaxis.axis_label = 'Zero-crossing rising/falling detection event polarity'
figs.append(fig)

figs.append(Div(text="""
<h2>Flattened binary zero-crossing spike train</h2>
<p>
    To investigate the angular perodicity the zero-crossing events per phase have been collapsed into a binary spike train. Here we are not interested
    by the peroidicity of each phase but instead the combined peroidicity for all channels for all phases.
</p>
"""))

fig = figure(title="Flattened binary zero-crossing spike train", plot_height=300, plot_width=1600) # 12000 1600 plot_width=1200, y_range=(0, 17000) plot_width=10000 # plot_width=10000,
fig.x_range=Range1d(0, 18500)
fig.vbar_stack(["combined_channel_data"], x='angles', width=1, source=channel_data_combined_single_transition) #color=colors, legend_label=["combined_channel_data"]
fig.xaxis.axis_label = 'Angle [steps]'
fig.yaxis.axis_label = 'Binary Zero-crossing detection event spike train'

figs.append(fig)

from scipy.fft import fft, ifft, dct, fftshift, fftfreq

#y = fft(np.asarray(channel_data_combined_single_transition["combined_channel_data"]))
#print(y)

import scipy.signal as signal
#w = signal.windows.blackman(16384) w * 
# poles 14 .... 7 * 6 = 42..... 16384/42
freqs = fftfreq(16384, 1)
freqs = fftshift(freqs)
ps = np.abs(fft(np.asarray(channel_data_combined_single_transition["combined_channel_data"]), len(channel_data_combined_single_transition["combined_channel_data"])))
print ("ps", ps)
ps = ps**2
print ("ps", ps)
ps = fftshift(ps)
ps = (ps)
print ("ps", ps)

# np.abs
#ps = np.log(ps)
# idx = np.argsort(freqs)


"""
yf = fft(y)
xf = fftfreq(N, T)
xf = fftshift(xf)
yplot = fftshift(yf)
import matplotlib.pyplot as plt
plt.plot(xf, 1.0/N * np.abs(yplot))
"""
print("freq ps", freqs.shape, ps.shape)

p = figure( title="Frequency [hz] vs Power spectrum [unit] of binary spike train",
           toolbar_location=None, plot_width=800)

# np.fft.fftshift(freq), np.fft.fftshift(np.abs(X)),
#p.vbar(x=freqs, top=ps, width=0.01)
p.line(freqs, ps, line_width=1)
p.x_range=Range1d(0, np.max(freqs))
p.xaxis.axis_label = 'Frequency [hz]'
p.yaxis.axis_label = 'Amplitude [unit]'


#p.line(x=freqs, top=ps)
#figs.append(p)

## calculate a histogram of the spaces between consequetive spacing of spike pulse
# train. Careful of the mod, we need to match the first pulse to the last.
# so for x(0) we need distance from x(16384)

import metrics # calculate_distance_mod_scalar

def round_nearest(value, base):
    return base * round(value/base)

def bin_modular_binary_spike_train_distances(binary_spike_train: List, bin_size: int = None):
    print("binary_spike_train", binary_spike_train)
    pulse_positions = []
    pulse_distances = []
    for angle_step_idx in range(len(binary_spike_train)):
        pulse_output = binary_spike_train[angle_step_idx]
        if pulse_output == 1:
            pulse_positions.append(angle_step_idx)
    print("pulse_positions", pulse_positions)
    for i in range(len(pulse_positions)):
        c_position = np.asarray([pulse_positions[i]])
        previous_position = i - 1
        if (previous_position < -1):
            previous_position = len(pulse_positions) - 1
        l_position = np.asarray([pulse_positions[previous_position]])
        distance = np.abs(metrics.calculate_distance_mod_scalar(l_position, c_position))[0]
        if bin_size != None:
            distance = round_nearest(distance, bin_size)
        pulse_distances.append(distance)

    pulse_hist = {}
    for distance in pulse_distances:
        if distance in pulse_hist:
            pulse_hist[distance] += 1
        else:
            pulse_hist[distance] = 1
        
    print("pulse_hist", pulse_hist)

    ordered_pulse_hist_keys = list(pulse_hist.keys())
    ordered_pulse_hist_keys.sort()
    ordered_pulse_hist_values = []
    for i in range(len(ordered_pulse_hist_keys)):
        key = ordered_pulse_hist_keys[i]
        value = pulse_hist[key]
        ordered_pulse_hist_values.append(value)
          
    return {
        "ordered_pulse_hist_keys": ordered_pulse_hist_keys,
        "ordered_pulse_hist_values": ordered_pulse_hist_values
    }
    pass

bin_to_nearest= 5
pulse_hist_data = bin_modular_binary_spike_train_distances(channel_data_combined_single_transition["combined_channel_data"], bin_to_nearest)
print("pulse_hist_data", pulse_hist_data)

h = figure( title="Binned histogram of consecutive pulse spike train event distances. Binned to nearest " + str(bin_to_nearest) + " angular steps.",
           toolbar_location=None,  plot_width=800)
h.vbar_stack(["ordered_pulse_hist_values"],x="ordered_pulse_hist_keys", source=pulse_hist_data) #ordered_pulse_hist_keys, ordered_pulse_hist_values)
h.yaxis.axis_label = 'Counts [number]'
h.xaxis.axis_label = 'Binned distance [angular steps]'

figs.append(Div(text="""
<h2>Temporal / spectral analysis of combined binary zero-crossing event spike train</h2>
<p>
In order to determine the peroidicity of the spike train there are two methods, one generate an fft on the spike train and look for peaks in frequency which dominate, the second
strategy is to measure the distance between each zero-crossing spike with the next spike in the train, the distances can
be rounded and binned into a historgram showing us the number occurance of spike distance of a certain binned value, if the motor is perfectly symmetrical it would be expected to see a 
dominate pulse delay time.
</p>
"""))

figs.append(row([p,h]))
# fig.vbar_stack(["combined_channel_data"], x='angles', width=1, source=channel_data_combined_single_transition, legend_label=["combined_channel_data"]) #color=colors,

#print(mean)

#print(channel_data_combined)
doc = curdoc()
curdoc().add_root(column(*figs))


file_out_zc = 'datasets/data/calibration-data/%s/zero_crossing_detections.channels.inliers.html' % (run_id)

output_file(filename=file_out_zc, title="Channel clusters for zero-crossing histogram with outliers")

save(doc)

def bohek_callback():
    pass