import numpy as np
import metrics
from typing import List
from scipy.fft import fft, ifft, dct, fftshift, fftfreq
import scipy.signal as signal

def round_nearest(value, base):
    return base * round(value/base)

def bin_modular_binary_spike_train_distances(binary_spike_train: List, bin_size: int = None):
    pulse_positions = []
    pulse_distances = []
    for angle_step_idx in range(len(binary_spike_train)):
        pulse_output = binary_spike_train[angle_step_idx]
        if pulse_output == 1:
            pulse_positions.append(angle_step_idx)
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

def peform_fft(data: List):
    #w = signal.windows.blackman(16384) w * 
    freqs = fftfreq(16384, 1)
    freqs = fftshift(freqs)
    ps = np.abs(fft(np.asarray(data), len(data)))
    ps = ps**2
    ps = fftshift(ps)
    return (freqs, ps)

def get_pairwise_distances_for_channel(km_channel_data, centroid):
    cluster_column = []
    centeroid_column = []
    for i in range(0, len(km_channel_data)):
        cluster_column.append(km_channel_data[i])
        centeroid_column.append(centroid)
    cluster_column = np.asarray(cluster_column)
    centeroid_column = np.asarray(centeroid_column)
    return np.sqrt(metrics.sum_of_squares_mod_vector(cluster_column, centeroid_column))

def get_stdev_for_channel(km_channel_data, centroid):
    #np_km_channel_data = np.asarray(km_channel_data)
    cluster_column = []
    centeroid_column = []
    for i in range(0, len(km_channel_data)):
        cluster_column.append(km_channel_data[i])
        centeroid_column.append(centroid)
    cluster_column = np.asarray(cluster_column)
    centeroid_column = np.asarray(centeroid_column)
    st_dev = metrics.root_mean_square_mod_scalar(cluster_column, centeroid_column)
    return st_dev
