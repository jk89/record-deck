# Run in root directory

from time import sleep
import numpy as np
import math
import sys
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, LinearAxis, Span
import tracking.kalman as kalman



# create a kalman filter for each channel a-vn, b-vn, c-vn, vn & angle
alpha = 6
theta_resolution_error = 0.01
jerk_error = 0.0000002
Kalman_a_minus_vn = kalman.Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_b_minus_vn = kalman.Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_c_minus_vn = kalman.Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)
Kalman_vn = kalman.Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)

alpha = 6
theta_resolution_error = 0.01
jerk_error = 0.0000002
Kalman_angle = kalman.Kalman_Filter_1D(alpha, theta_resolution_error, jerk_error)

# read dataset argument
dataset_name = sys.argv[1] if len(sys.argv) > 1 else 0 
filename = 'datasets/data/calibration-data/%s/merged_capture_data.csv' % (dataset_name)

# open dataset file
std_in = None
with open(filename) as f: 
    std_in = f.readlines()
len_std_in = len(std_in)

# define columns for graphs
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

# zero crossing horizontal line
hline = Span(location=0, dimension='width', line_color='grey', line_width=1)

# Plot of phaseX - vn
pX_minus_vn = figure(title="Plot of (phaseX - vn) and angle vs time", plot_width=1200, y_range=(-100, 150))
pX_minus_vn.line(source=plot_data, x='time', y='phase_a_minus_vn', color="red", legend_label="time vs phase_a_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='phase_b_minus_vn', color=(246,190,0), legend_label="time vs phase_b_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='phase_c_minus_vn', color="black", legend_label="time vs phase_c_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='vn', color="blue", legend_label="time vs vn")
pX_minus_vn.renderers.extend([hline])

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
kalman_pX_minus_vn.renderers.extend([hline])


# add graphs to document
doc = curdoc()
curdoc().add_root(column(pX_vn, pX_minus_vn, kalman_pX_minus_vn))


skip_to_line = 0
# function to read the array of lines of the file and append them to measurements arrays
def pass_data():
    times=[]
    angles=[]
    phase_a_measurements = []
    phase_b_measurements = []
    phase_c_measurements = []
    vn_measurements = []

    for line_idx in range(skip_to_line, len_std_in):
        line = std_in[line_idx]
        line_strip = line.strip()
        data_str = line_strip.split("\t")
        time = float(data_str[0])
        angle = float(data_str[1])# float(int(np.random.normal(line_idx, 100, size=1)[0]) % 16384)# hack #float(data_str[0])
        phase_a = float(data_str[2])
        phase_b = float(data_str[3])
        phase_c = float(data_str[4])
        vn = float(data_str[5])

        #print(angle, float(data_str[0]))

        angles.append(angle)
        times.append(time)
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

# define callback to be called on each bokeh tick
# this preforms kalman on (a-vn, b-vn, c-vn, vn and angle) and streams to the bohek
idx = 0 
def bokeh_callback():
    global idx
    if ( idx + 1 >= len_std_in):
        return
    else:
        # unpack data
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
        (_, kalman_state_vn) = Kalman_vn.estimate_state_vector_eular_and_kalman((time, vn))
        (_, kalman_state_angle) = Kalman_angle.estimate_state_vector_eular_and_kalman((time, angle))
        
        # unpack kalman data if it exists
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

        # create stream_obj
        stream_obj = {
            "time" : [time],
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
            "kalman_angle": [float(int(kalman_angle) % 16384)]
        }

        # stream data to bohek
        plot_data.stream(stream_obj)
        print(stream_obj)
        # increment id
        idx += 1
        # re-add callback for next tick
        doc.add_next_tick_callback(bokeh_callback)

# add callback for first tick
doc.add_next_tick_callback(bokeh_callback)
