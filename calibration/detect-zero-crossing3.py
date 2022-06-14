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


alpha = 50
theta_resolution_error = 1
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
        kalman_angle=[],
        kalman_a_minus_vn=[],
        kalman_b_minus_vn=[],
        kalman_c_minus_vn=[],
    )
)


kalman_pX_minus_vn = figure(title="Plot of (kalman phase_X_minus_vn and kalman angle)", plot_width=1200, y_range=(-60, 150))
kalman_pX_minus_vn.xaxis.axis_label = 'Time [ticks]'
kalman_pX_minus_vn.yaxis.axis_label = '(Phase X - Virtual Neutral) Voltage [steps]'
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_a_minus_vn', color="red", legend_label="time vs kalman_a_minus_vn")
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_b_minus_vn', color=(246,190,0), legend_label="time vs kalman_b_minus_vn")
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_c_minus_vn', color="black", legend_label="time vs kalman_c_minus_vn")

kalman_pX_minus_vn.extra_y_ranges = {"angle": Range1d(start=0, end=16834)}
kalman_pX_minus_vn.add_layout(LinearAxis(y_range_name="angle", axis_label="Angle [steps]"), 'right')
kalman_pX_minus_vn.line(source=plot_data, x='time', y='kalman_angle', color="purple", legend_label="time vs kalman_angle", y_range_name="angle")

# kalman_pX_minus_vvn.line(source=plot_data, x='time', y='kalman_angle_norm', color="blue", legend_label="time vs kalman_angle_norm")


doc = curdoc()
curdoc().add_root(column(kalman_pX_minus_vn))


skip_to_line = 0

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
        angle = float(data_str[0])
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


data = pass_data()
print(data)

def perform_kalman_on_data(data):
    kalman_result = ([], [], [], [], [])
    for idx in range(len_std_in - 1):
        #angle = data[0][idx]
        #make up angle as its not recorded for now
        angle = int(np.random.normal(idx, 10, size=1)[0]) % 16384
        phase_a = data[1][idx]
        phase_b = data[2][idx]
        phase_c = data[3][idx]
        vn = data[4][idx]
        phase_a_minus_vn = phase_a - vn
        phase_b_minus_vn = phase_b - vn
        phase_c_minus_vn = phase_c - vn

        (_, kalman_state_a_minus_vn) = Kalman_a_minus_vn.estimate_state_vector_eular_and_kalman((idx, phase_a_minus_vn))
        (_, kalman_state_b_minus_vn) = Kalman_b_minus_vn.estimate_state_vector_eular_and_kalman((idx, phase_b_minus_vn))
        (_, kalman_state_c_minus_vn) = Kalman_c_minus_vn.estimate_state_vector_eular_and_kalman((idx, phase_c_minus_vn))
        (_, kalman_state_angle) = Kalman_angle.estimate_state_vector_eular_and_kalman((idx, angle))

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

            kalman_result[0].append(int(idx))
            kalman_result[1].append(float(int(kalman_angle) % 16384))
            kalman_result[2].append(float(kalman_a_minus_vn))
            kalman_result[3].append(float(kalman_b_minus_vn))
            kalman_result[4].append(float(kalman_c_minus_vn))

            #print(kalman_result)
            #sys.exit()
    return kalman_result

processed_data = perform_kalman_on_data(data)

rising_zero_crossing_kernel = [-1, 0, 1]
# -1 indicates negative
# +1 indicates positive
# 0 indicates either
kernel_size = len(rising_zero_crossing_kernel)
falling_zero_crossing_kernel = []
for k in range(kernel_size):
    rising_value = rising_zero_crossing_kernel[k]
    falling_value = 0 if rising_value == 0 else -rising_value
    falling_zero_crossing_kernel.append(falling_value)

def detect_zero_crossings(processed_data, rising_zero_crossing_kernel, falling_zero_crossing_kernel):
    zc_channel_data = ([], [], [])
    len_data = len(processed_data[0])

    def get_relevant_data(idx):
        angle = processed_data[1][idx]
        a_m_vn = processed_data[2][idx]
        b_m_vn = processed_data[3][idx]
        c_m_vn = processed_data[4][idx]
        return (angle, a_m_vn, b_m_vn, c_m_vn)

    kernel_mid_point = (kernel_size - 1) / 2
    valid_start_idx = kernel_mid_point - 1
    valid_end_idx = len_data - (kernel_mid_point + 1)

    # channels are time [0], and kalman: angle [1], a-vn [2], b-vn [3], c-vn [4]
    for d_idx in range(0, len_data - 1):
        #can we compute zc at this window?
        if d_idx > valid_start_idx and d_idx <= valid_end_idx:
            # [-1, -1, 0, 1, 1] rising_zero_crossing_kernel

            rising_signal = (True, True, True)
            falling_signal = (True, True, True)
            # kernel midpoint is currently on idx
            for k_idx in range(0, kernel_size - 1):
                kd_idx = (k_idx + d_idx) - kernel_mid_point
                kd_element = get_relevant_data(kd_idx)
                # angle, a-vn, b-vn, c-vn
                rising_test = rising_zero_crossing_kernel[k_idx]
                falling_test = falling_zero_crossing_kernel[k_idx]
                for channel_idx in range(2, 5): # 2, 3, 4 #  (1, 4) 1, 2, 3
                    sign_kd_element = 0
                    if kd_element[channel_idx] > 0:
                        sign_kd_element = +1
                    elif kd_element[channel_idx] < 0:
                        sign_kd_element = -1

                    # rising
                    if (sign_kd_element != rising_test):
                        rising_signal[channel_idx - 2] = False
                    # falling 
                    if (sign_kd_element != falling_test):
                        falling_signal[channel_idx - 2] = False

            for channel_idx in range(0, 3):
                if rising_signal[channel_idx] == True and falling_signal[channel_idx] == False:
                    zc_channel_data[channel_idx].append(+1)
                elif rising_signal[channel_idx] == False and falling_signal[channel_idx] == True:
                    zc_channel_data[channel_idx].append(-1)
                else:
                    zc_channel_data[channel_idx].append(0)
        else:
            zc_channel_data[0].append(0)
            zc_channel_data[1].append(0)
            zc_channel_data[2].append(0)
    return zc_channel_data

def callback():
    global processed_data
    streamObj = {
        "time" : processed_data[0],
        "kalman_angle": processed_data[1],
        "kalman_a_minus_vn": processed_data[2],
        "kalman_b_minus_vn": processed_data[3],
        "kalman_c_minus_vn": processed_data[4],
    }

    plot_data.stream(streamObj)
    #doc.add_next_tick_callback(callback)

doc.add_next_tick_callback(callback)
