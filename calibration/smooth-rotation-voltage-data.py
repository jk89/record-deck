# Run in root directory

from time import sleep
import numpy as np
import math
import sys
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, LinearAxis
import json
from kalman import Kalman_Filter_1D

# create a kalman filter for each channel (a-vn, b-vn, c-vn, angle)
alpha = 6
theta_resolution_error = 0.01
jerk_error = 0.0000002
Kalman_a_minus_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_b_minus_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_c_minus_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
alpha = 50
theta_resolution_error = 1
jerk_error = 0.0000002
Kalman_angle = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)

# parse dataset argument
dataset_name = sys.argv[1] if len(sys.argv) > 1 else 0 
filename = 'datasets/data/calibration-data/%s' % (dataset_name)

# read dataset data
std_in = None
with open(filename) as f: 
    std_in = f.readlines()
len_std_in = len(std_in)

# create graphing columns
plot_data = ColumnDataSource(
    dict(
        time=[],
        kalman_angle=[],
        kalman_a_minus_vn=[],
        kalman_b_minus_vn=[],
        kalman_c_minus_vn=[],
    )
)

# create chart for (phaseXi - vn and angle)
kalman_pX_minus_vn = figure(title="Plot of (kalman phase_X_minus_vn and kalman angle)", plot_width=3200, plot_height=1080, y_range=(-60, 150))
kalman_pX_minus_vn.xaxis.axis_label = 'Time [ticks]'
kalman_pX_minus_vn.yaxis.axis_label = '(Phase X - Virtual Neutral) Voltage [steps]'
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_a_minus_vn', color="red", legend_label="time vs kalman_a_minus_vn")
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_b_minus_vn', color=(246,190,0), legend_label="time vs kalman_b_minus_vn")
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_c_minus_vn', color="black", legend_label="time vs kalman_c_minus_vn")
kalman_pX_minus_vn.extra_y_ranges = {"angle": Range1d(start=0, end=16834)}
kalman_pX_minus_vn.add_layout(LinearAxis(y_range_name="angle", axis_label="Angle [steps]"), 'right')
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_angle', color="purple", legend_label="time vs kalman_angle", y_range_name="angle")

# add chart to current document
doc = curdoc()
curdoc().add_root(column(kalman_pX_minus_vn))

# function to read the array of lines of the file and append them to measurements arrays
skip_to_line = 0
def pass_data():
    angles=[]
    phase_a_measurements = []
    phase_b_measurements = []
    phase_c_measurements = []
    vn_measurements = []
    times=[]

    for line_idx in range(skip_to_line, len_std_in):
        line = std_in[line_idx]
        line_strip = line.strip()
        data_str = line_strip.split("\t")
        time = float(data_str[0])
        angle = float(data_str[1])
        phase_a = float(data_str[2])
        phase_b = float(data_str[3])
        phase_c = float(data_str[4])
        vn = float(data_str[5])

        times.append(time)
        angles.append(angle)
        phase_a_measurements.append(phase_a)
        phase_b_measurements.append(phase_b)
        phase_c_measurements.append(phase_c)
        vn_measurements.append(vn)
    
    return (
        np.asarray(times),
        np.asarray(angles),
        np.asarray(phase_a_measurements),
        np.asarray(phase_b_measurements),
        np.asarray(phase_c_measurements),
        np.asarray(vn_measurements)
        )

# process data
data = pass_data()
print(data)

# this preforms kalman on (a-vn, b-vn, c-vn and angle) and returns the results for each channel
def perform_kalman_on_data(data):
    kalman_result = ([], [], [], [], [])
    for idx in range(len_std_in - 1):
        # unpack data
        #angle = data[0][idx]
        #make up angle as its not recorded for now
        time = data[0][idx]
        angle = data[1][idx]
        phase_a = data[2][idx]
        phase_b = data[3][idx]
        phase_c = data[4][idx]
        vn = data[5][idx]

        # compute phaseXi - vn
        phase_a_minus_vn = phase_a - vn
        phase_b_minus_vn = phase_b - vn
        phase_c_minus_vn = phase_c - vn

        # compute kalman
        (_, kalman_state_a_minus_vn) = Kalman_a_minus_vn.estimate_state_vector_eular_and_kalman((time, phase_a_minus_vn))
        (_, kalman_state_b_minus_vn) = Kalman_b_minus_vn.estimate_state_vector_eular_and_kalman((time, phase_b_minus_vn))
        (_, kalman_state_c_minus_vn) = Kalman_c_minus_vn.estimate_state_vector_eular_and_kalman((time, phase_c_minus_vn))
        (_, kalman_state_angle) = Kalman_angle.estimate_state_vector_eular_and_kalman((time, angle))

        # unpack kalman data if it exists
        kalman_a_minus_vn = 0
        kalman_b_minus_vn = 0
        kalman_c_minus_vn = 0
        kalman_angle = 0

        # we have enough measurements for a valid state estimate via kalman
        if kalman_state_a_minus_vn is not None:
            # unpack
            kalman_state_a_minus_vn = kalman_state_a_minus_vn[0]
            kalman_state_b_minus_vn = kalman_state_b_minus_vn[0]
            kalman_state_c_minus_vn = kalman_state_c_minus_vn[0]
            kalman_state_angle = kalman_state_angle[0]

            kalman_a_minus_vn = kalman_state_a_minus_vn[0]
            kalman_b_minus_vn = kalman_state_b_minus_vn[0]
            kalman_c_minus_vn = kalman_state_c_minus_vn[0]
            kalman_angle = kalman_state_angle[0]

            kalman_result[0].append(time)
            kalman_result[1].append(float(int(kalman_angle) % 16384))
            kalman_result[2].append(float(kalman_a_minus_vn))
            kalman_result[3].append(float(kalman_b_minus_vn))
            kalman_result[4].append(float(kalman_c_minus_vn))
    return kalman_result

# process data
processed_data = perform_kalman_on_data(data)
# save
json_data = json.dumps(processed_data)
# json
with open("calibration/__pycache__/kalman-filtered-" + dataset_name + ".json", "a") as fout:
    fout.write(json_data)


# define callback to be called on each bokeh tick
# this streams the kalman results on (time, a-vn, b-vn, c-vn, vn and angle) and streams to the bohek

def bohek_callback():
    global processed_data

    # create stream_obj
    stream_obj = {
        "time" : processed_data[0],
        "kalman_angle": processed_data[1],
        "kalman_a_minus_vn": processed_data[2],
        "kalman_b_minus_vn": processed_data[3],
        "kalman_c_minus_vn": processed_data[4],
    }

    # stream data to bohek
    plot_data.stream(stream_obj)
    # no need to add callback as only calculating results once

# add callback for first tick
doc.add_next_tick_callback(bohek_callback)
