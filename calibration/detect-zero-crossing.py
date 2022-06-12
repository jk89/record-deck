# Run in root directory

from time import sleep
import numpy as np
import math
import sys
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d

from kalman import Kalman_Filter_1D
# create a kalman filter for each channel a, b, c

alpha = 20
theta_resolution_error = 10
jerk_error = 0.000001
kA = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
kB = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
kC = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)

datasetName = sys.argv[1] if len(sys.argv) > 1 else 0 

filename = 'datasets/data/calibration-data/%s' % (datasetName)

std_in = None
with open(filename) as f: 
    std_in = f.readlines()

# std_in = sys.std_in.readlines() does not work with bohek serve
len_std_in = len(std_in)

plot_data = ColumnDataSource(
    dict(
        time=[],
        angle=[],
        phase_a=[],
        phase_b=[],
        phase_c=[],
        vn=[],
        vvn=[],
        phase_a_minus_vn=[],
        phase_b_minus_vn=[],
        phase_c_minus_vn=[],
        phase_a_minus_vvn=[],
        phase_b_minus_vvn=[],
        phase_c_minus_vvn=[],
        phase_a_norm = [],
        phase_b_norm = [],
        phase_c_norm = [],
        phase_a_norm_minus_norm_vvn=[],
        phase_b_norm_minus_norm_vvn=[],
        phase_c_norm_minus_norm_vvn=[],
        norm_vvn=[],
        kalman_a_norm=[],
        kalman_b_norm=[],
        kalman_c_norm=[]
        
    )
)

# Plot of phaseX, vn
pX_vn = figure(title="Plot of phaseX vs vn", plot_width=1200)
pX_vn.line(source=plot_data, x='time', y='phase_a', color="red", legend_label="time vs phase_a")
pX_vn.line(source=plot_data, x='time', y='phase_b', color="yellow", legend_label="time vs phase_b")
pX_vn.line(source=plot_data, x='time', y='phase_c', color="black", legend_label="time vs phase_c")
pX_vn.line(source=plot_data, x='time', y='vn', color="blue", legend_label="time vs vn")


# Plot of phaseX - vn
pX_minus_vn = figure(title="Plot of (phaseX - vn)", plot_width=1200)
pX_minus_vn.line(source=plot_data, x='time', y='phase_a_minus_vn', color="red", legend_label="time vs phase_a_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='phase_b_minus_vn', color="yellow", legend_label="time vs phase_b_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='phase_c_minus_vn', color="black", legend_label="time vs phase_c_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='vn', color="blue", legend_label="time vs vn")

# Plot of phaseX - vvn
pX_minus_vnn = figure(title="Plot of (phaseX - vnn)", plot_width=1200)
pX_minus_vnn.line(source=plot_data, x='time', y='phase_a_minus_vvn', color="red", legend_label="time vs phase_a_minus_vvn")
pX_minus_vnn.line(source=plot_data, x='time', y='phase_b_minus_vvn', color="yellow", legend_label="time vs phase_b_minus_vvn")
pX_minus_vnn.line(source=plot_data, x='time', y='phase_c_minus_vvn', color="black", legend_label="time vs phase_c_minus_vvn")
pX_minus_vnn.line(source=plot_data, x='time', y='vvn', color="blue", legend_label="time vs vvn")

# Plot of norm phaseX - vvn
## DIFFERENt CHArt titlE
norm_pX_minus_vnn = figure(title="Plot of (norm phaseX - norm_vvn)", plot_width=1200)
norm_pX_minus_vnn.line(source=plot_data, x='time', y='phase_a_norm_minus_norm_vvn', color="red", legend_label="time vs phase_a_norm_minus_norm_vvn")
norm_pX_minus_vnn.line(source=plot_data, x='time', y='phase_b_norm_minus_norm_vvn', color="yellow", legend_label="time vs phase_b_norm_minus_norm_vvn")
norm_pX_minus_vnn.line(source=plot_data, x='time', y='phase_c_norm_minus_norm_vvn', color="black", legend_label="time vs phase_c_norm_minus_norm_vvn")
norm_pX_minus_vnn.line(source=plot_data, x='time', y='norm_vvn', color="blue", legend_label="time vs norm_vvn")


norm_pX = figure(title="Plot of (norm phaseX)", plot_width=1200)
norm_pX.line(source=plot_data, x='time', y='phase_a_norm', color="red", legend_label="time vs phase_a_norm")
norm_pX.line(source=plot_data, x='time', y='phase_b_norm', color="yellow", legend_label="time vs phase_b_norm")
norm_pX.line(source=plot_data, x='time', y='phase_c_norm', color="black", legend_label="time vs phase_c_norm")
norm_pX.line(source=plot_data, x='time', y='norm_vvn', color="blue", legend_label="time vs norm_vvn")

#kalman

kalman_pX = figure(title="Plot of (kalman phaseX)", plot_width=1200)
kalman_pX.line(source=plot_data, x='time', y='kalman_a_norm', color="red", legend_label="time vs kalman_a_norm")
kalman_pX.line(source=plot_data, x='time', y='kalman_b_norm', color="yellow", legend_label="time vs kalman_b_norm")
kalman_pX.line(source=plot_data, x='time', y='kalman_c_norm', color="black", legend_label="time vs kalman_c_norm")


doc = curdoc()
curdoc().add_root(column(pX_vn, pX_minus_vn,pX_minus_vnn, kalman_pX, norm_pX, norm_pX_minus_vnn))

def pass_data():
    angles=[]
    parities=[]
    phase_a_measurements = []
    phase_b_measurements = []
    phase_c_measurements = []
    vn_measurements = []

    for line in std_in:
        line_strip = line.strip()
        data_str = line_strip.split("\t")
        parity = float(data_str[0])
        angle = float(data_str[1])
        phase_a = float(data_str[2])
        phase_b = float(data_str[3])
        phase_c = float(data_str[4])
        vn = float(data_str[5])

        angles.append(angle)
        parities.append(parity)
        phase_a_measurements.append(phase_a)
        phase_b_measurements.append(phase_b)
        phase_c_measurements.append(phase_c)
        vn_measurements.append(vn)
    
    return (
        np.asarray(angles),
        np.asarray(parities),
        np.asarray(phase_a_measurements),
        np.asarray(phase_b_measurements),
        np.asarray(phase_c_measurements),
        np.asarray(vn_measurements)
        )

def get_channel_statistics(data):
    return (
        np.mean(data[0]), # angle step
        np.mean(data[1]), # parity
        np.mean(data[2]), # a
        np.mean(data[3]), # b
        np.mean(data[4]), # c
        np.mean(data[5]), # vn
    )

data = pass_data()
print(data)
stats = get_channel_statistics(data)
# print( (float( stats[2])))

idx = 0 
def callback():
    global idx
    print("in callack", len_std_in, idx)
    if ( idx + 1 >= len_std_in):
        return
    else:
        parity = data[0][idx]
        angle = data[1][idx]
        
        phase_a = data[2][idx]
        phase_b = data[3][idx]
        phase_c = data[4][idx]

        u_phase_a = float(stats[2])
        u_phase_b = float(stats[3])
        u_phase_c = float(stats[4])

        phase_a_norm = phase_a / u_phase_a
        phase_b_norm = phase_b / u_phase_b
        phase_c_norm = phase_c / u_phase_c

        vn = data[5][idx]
        vvn = (phase_a + phase_b + phase_c) / 3
        norm_vvn = (phase_a_norm + phase_b_norm + phase_c_norm) / 3

        phase_a_minus_vn = phase_a - vn
        phase_b_minus_vn = phase_b - vn
        phase_c_minus_vn = phase_c - vn

        phase_a_minus_vvn = phase_a - vvn
        phase_b_minus_vvn = phase_b - vvn
        phase_c_minus_vvn = phase_c - vvn

        phase_a_norm_minus_norm_vvn = phase_a_norm - norm_vvn
        phase_b_norm_minus_norm_vvn = phase_b_norm - norm_vvn
        phase_c_norm_minus_norm_vvn = phase_c_norm - norm_vvn

        # kalman
        print("pre kalman", idx)
        (_, kalman_state_a) = kA.estimate_state_vector_eular_and_kalman((idx, phase_a_norm))
        (_, kalman_state_b) = kB.estimate_state_vector_eular_and_kalman((idx, phase_b_norm))
        (_, kalman_state_c) = kC.estimate_state_vector_eular_and_kalman((idx, phase_c_norm))

        kalman_a_norm = 0
        kalman_b_norm = 0
        kalman_c_norm = 0

        if kalman_state_a is not None and kalman_state_b is not None and kalman_state_c is not None:
            kalman_state_a = kalman_state_a[0]
            kalman_state_b = kalman_state_b[0]
            kalman_state_c = kalman_state_c[0]
            kalman_a_norm = kalman_state_a[0]
            kalman_b_norm = kalman_state_b[0]
            kalman_c_norm = kalman_state_c[0]
            pass
        else:
            pass

        streamObj = {
            "time" : [idx],
            "angle": [angle],
            "phase_a": [phase_a],
            "phase_b": [phase_b],
            "phase_c": [phase_c],
            "vn": [vn],
            "vvn": [vvn],
            "norm_vvn": [norm_vvn],
            "phase_a_norm": [phase_a_norm],
            "phase_b_norm": [phase_b_norm],
            "phase_c_norm": [phase_c_norm],
            "phase_a_minus_vn": [phase_a_minus_vn],
            "phase_b_minus_vn": [phase_b_minus_vn],
            "phase_c_minus_vn": [phase_c_minus_vn],
            "phase_a_minus_vvn": [phase_a_minus_vvn],
            "phase_b_minus_vvn": [phase_b_minus_vvn],
            "phase_c_minus_vvn": [phase_c_minus_vvn],
            "phase_a_norm_minus_norm_vvn": [phase_a_norm_minus_norm_vvn],
            "phase_b_norm_minus_norm_vvn": [phase_b_norm_minus_norm_vvn],
            "phase_c_norm_minus_norm_vvn": [phase_c_norm_minus_norm_vvn],
            "kalman_a_norm": [kalman_a_norm],
            "kalman_b_norm": [kalman_b_norm],
            "kalman_c_norm": [kalman_c_norm]
        }

        print(streamObj)

        plot_data.stream(streamObj)
        idx += 1
        doc.add_next_tick_callback(callback)

doc.add_next_tick_callback(callback)
