# Run in root directory

from time import sleep
import numpy as np
import math
import sys
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, LinearAxis

from kalman import Kalman_Filter_1D
# create a kalman filter for each channel a, b, c

alpha = 6
theta_resolution_error = 0.01
jerk_error = 0.0000002
Kalman_a_minus_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_b_minus_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_c_minus_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_vn = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)

alpha = 6
theta_resolution_error = 0.01
jerk_error = 0.0000002
Kalman_angle = Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)

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
        phase_a_minus_vn=[],
        phase_b_minus_vn=[],
        phase_c_minus_vn=[],
        vn=[],
        kalman_a_minus_vn=[],
        kalman_b_minus_vn=[],
        kalman_c_minus_vn=[],
        kalman_vn=[],
        kalman_angle=[]
    )
)

# Plot of phaseX, vn
pX_vn = figure(title="Plot of phaseX, vn and angle vs time", plot_width=1200, y_range=(0, 200))
pX_vn.line(source=plot_data, x='time', y='phase_a', color="red", legend_label="time vs phase_a")
pX_vn.line(source=plot_data, x='time', y='phase_b', color=(246,190,0), legend_label="time vs phase_b")
pX_vn.line(source=plot_data, x='time', y='phase_c', color="black", legend_label="time vs phase_c")
pX_vn.line(source=plot_data, x='time', y='vn', color="blue", legend_label="time vs vn")

pX_vn.xaxis.axis_label = 'Time [ticks]'
pX_vn.yaxis.axis_label = '(Phase X or VN) Voltage [steps]'
pX_vn.extra_y_ranges = {"angle": Range1d(start=0, end=16834)}
pX_vn.add_layout(LinearAxis(y_range_name="angle", axis_label="Angle [steps]"), 'right')
pX_vn.line(source=plot_data, x='time', y='angle', color="purple", legend_label="time vs angle", y_range_name="angle")


# Plot of phaseX - vn
pX_minus_vn = figure(title="Plot of (phaseX - vn) and angle vs time", plot_width=1200, y_range=(-100, 150))
pX_minus_vn.line(source=plot_data, x='time', y='phase_a_minus_vn', color="red", legend_label="time vs phase_a_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='phase_b_minus_vn', color=(246,190,0), legend_label="time vs phase_b_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='phase_c_minus_vn', color="black", legend_label="time vs phase_c_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='vn', color="blue", legend_label="time vs vn")

pX_minus_vn.xaxis.axis_label = 'Time [ticks]'
pX_minus_vn.yaxis.axis_label = '(Phase X - VN) Voltage [steps]'
pX_minus_vn.extra_y_ranges = {"angle": Range1d(start=0, end=16834)}
pX_minus_vn.add_layout(LinearAxis(y_range_name="angle", axis_label="Angle [steps]"), 'right')
pX_minus_vn.line(source=plot_data, x='time', y='angle', color="purple", legend_label="time vs angle", y_range_name="angle")

#kalman

kalman_pX_minus_vn = figure(title="Plot of (kalman phase_X_minus_vn and angle) vs time", plot_width=1200, y_range=(-100, 150))
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_a_minus_vn', color="red", legend_label="time vs kalman_a_minus_vn")
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_b_minus_vn', color=(246,190,0), legend_label="time vs kalman_b_minus_vn")
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_c_minus_vn', color="black", legend_label="time vs kalman_c_minus_vn")

kalman_pX_minus_vn.xaxis.axis_label = 'Time [ticks]'
kalman_pX_minus_vn.yaxis.axis_label = '(Kalman [Phase X - VN]) Voltage [steps]'
kalman_pX_minus_vn.extra_y_ranges = {"angle": Range1d(start=0, end=16834)}
kalman_pX_minus_vn.add_layout(LinearAxis(y_range_name="angle", axis_label="Angle [steps]"), 'right')
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_angle', color="purple", legend_label="time vs angle", y_range_name="angle")


# kalman_pX_minus_vvn.line(source=plot_data, x='time', y='kalman_vn_norm', color="blue", legend_label="time vs kalman_vn_norm")


doc = curdoc()
curdoc().add_root(column(pX_vn, pX_minus_vn, kalman_pX_minus_vn))


skip_to_line = 650

def pass_data():
    angles=[]
    phase_a_measurements = []
    phase_b_measurements = []
    phase_c_measurements = []
    vn_measurements = []

    for line_idx in range(skip_to_line, len_std_in):
        line = std_in[line_idx]
        line_strip = line.strip()
        data_str = line_strip.split("\t")
        angle = float(int(np.random.normal(line_idx, 100, size=1)[0]) % 16384)# hack #float(data_str[0])
        phase_a = float(data_str[1])
        phase_b = float(data_str[2])
        phase_c = float(data_str[3])
        vn = float(data_str[4])

        angles.append(angle)
        phase_a_measurements.append(phase_a)
        phase_b_measurements.append(phase_b)
        phase_c_measurements.append(phase_c)
        vn_measurements.append(vn)
    
    return (
        np.asarray(angles),
        np.asarray(phase_a_measurements),
        np.asarray(phase_b_measurements),
        np.asarray(phase_c_measurements),
        np.asarray(vn_measurements)
        )

def get_channel_statistics(data):
    return (
        np.mean(data[0]), # angle step
        np.mean(data[1]), # a
        np.mean(data[2]), # b
        np.mean(data[3]), # c
        np.mean(data[4]), # vn
    )

data = pass_data()
print(data)
stats = get_channel_statistics(data)
# print( (float( stats[2])))

idx = 0 
def callback():
    global idx
    if ( idx + 1 >= len_std_in):
        return
    else:
        angle = data[0][idx]
        
        phase_a = data[1][idx]
        phase_b = data[2][idx]
        phase_c = data[3][idx]
        vn = data[4][idx]

        phase_a_minus_vn = phase_a - vn
        phase_b_minus_vn = phase_b - vn
        phase_c_minus_vn = phase_c - vn

        # kalman

        (_, kalman_state_a_minus_vn) = Kalman_a_minus_vn.estimate_state_vector_eular_and_kalman((idx, phase_a_minus_vn))
        (_, kalman_state_b_minus_vn) = Kalman_b_minus_vn.estimate_state_vector_eular_and_kalman((idx, phase_b_minus_vn))
        (_, kalman_state_c_minus_vn) = Kalman_c_minus_vn.estimate_state_vector_eular_and_kalman((idx, phase_c_minus_vn))
        (_, kalman_state_vn) = Kalman_vn.estimate_state_vector_eular_and_kalman((idx, vn))
        (_, kalman_state_angle) = Kalman_angle.estimate_state_vector_eular_and_kalman((idx, angle))
        

        kalman_a_minus_vn = 0
        kalman_b_minus_vn = 0
        kalman_c_minus_vn = 0
        kalman_vn = 0
        kalman_angle = 0


        if kalman_state_a_minus_vn is not None:
            kalman_state_a_minus_vn = kalman_state_a_minus_vn[0]
            kalman_state_b_minus_vn = kalman_state_b_minus_vn[0]
            kalman_state_c_minus_vn = kalman_state_c_minus_vn[0]
            kalman_state_vn = kalman_state_vn[0]
            kalman_state_angle = kalman_state_angle[0]

            kalman_a_minus_vn = kalman_state_a_minus_vn[0]
            kalman_b_minus_vn = kalman_state_b_minus_vn[0]
            kalman_c_minus_vn = kalman_state_c_minus_vn[0]
            kalman_vn = kalman_state_vn[0]
            kalman_angle = kalman_state_angle[0]
            
            pass
        else:
            pass

        streamObj = {
            "time" : [idx],
            "angle": [angle],
            "phase_a": [phase_a],
            "phase_b": [phase_b],
            "phase_c": [phase_c],
            "phase_a_minus_vn": [phase_a_minus_vn],
            "phase_b_minus_vn": [phase_b_minus_vn],
            "phase_c_minus_vn": [phase_c_minus_vn],
            "vn": [vn],
            "kalman_a_minus_vn": [kalman_a_minus_vn],
            "kalman_b_minus_vn": [kalman_b_minus_vn],
            "kalman_c_minus_vn": [kalman_c_minus_vn],
            "kalman_vn": [kalman_vn],
            "kalman_angle": [kalman_angle]
         
        }

        plot_data.stream(streamObj)
        idx += 1
        doc.add_next_tick_callback(callback)

doc.add_next_tick_callback(callback)
