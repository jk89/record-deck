import numpy as np
import metrics
from typing import Dict, List, Tuple
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

def get_ideal_distance(n_poles):
    return float(16384) / (3.0 * float(n_poles))

def dict_to_value_ordered_lkv_tuple_list(label, dict) -> List[Tuple]: # label, key, value
    keys = list(dict.keys())
    values = list(dict.values())
    kv = [(label, keys[i], values[i]) for i in range(len(keys))]
    # order this by value
    return sorted(kv, key=lambda x: x[2]) # , reverse=True

def mean_to_ordered_lkv(mean: Dict):
    lkv_tuples = []
    label_keys = list(mean.keys())
    for label in label_keys:
        current_lkv_tuple_list = dict_to_value_ordered_lkv_tuple_list(label, mean[label])
        lkv_tuples = lkv_tuples + current_lkv_tuple_list
    # sort globally
    return sorted(lkv_tuples, key=lambda x: x[2])

def get_ordered_angles_from_mean(ordered_mean_lkv_tuple_list):
    return list(map(lambda x: x[2], ordered_mean_lkv_tuple_list))

def displacement_from_ideal(zc_ordered_angles, ideal_spacing):
    displacement_distances_from_ideal = []
    distances = []
    for i in range(len(zc_ordered_angles)):
        c_position = np.asarray([zc_ordered_angles[i]])
        previous_position = i - 1
        if (previous_position < -1):
            previous_position = len(zc_ordered_angles) - 1
        l_position = np.asarray([zc_ordered_angles[previous_position]])
        distance = np.abs(metrics.calculate_distance_mod_scalar(l_position, c_position))[0]
        displacement_distances_from_ideal.append(distance - ideal_spacing)
        distances.append(distance)
    # displacement_distances_from_ideal is vector of d - dm
    ddfi = np.asarray(displacement_distances_from_ideal)
    # if we square these displacements then sum them, divide that by N then sqrt we have
    sq_ddfi = ddfi ** 2
    sum_sq_ddfi = sq_ddfi.sum()
    norm_sum_sq_ddfi = sum_sq_ddfi / float(len(displacement_distances_from_ideal))
    std_dev_from_ideal = np.sqrt(norm_sum_sq_ddfi)
    # a metric of deviation from ideal
    return displacement_distances_from_ideal, std_dev_from_ideal, distances

def get_error_report_stats(zc_displacements_from_ideal, conseq_distances):
    np_displacement_from_ideal = np.asarray(zc_displacements_from_ideal)
    np_angle_displacement = np.asarray(conseq_distances)
    avg_angle_displacement = np.mean(np_angle_displacement)
    std_angle_displacement = np.std(np_angle_displacement)
    np_norm_displacement_from_ideal = np.abs(np_displacement_from_ideal)
    max_norm_displacement_from_ideal = np.max(np_norm_displacement_from_ideal)
    min_norm_displacement_from_ideal = np.min(np_norm_displacement_from_ideal)
    avg_norm_displacement_from_ideal = np.mean(np_norm_displacement_from_ideal)
    std_norm_displacement_from_ideal = np.std(np_norm_displacement_from_ideal)
    min_displacement_from_ideal = np.min(np_displacement_from_ideal)
    max_displacement_from_ideal = np.max(np_displacement_from_ideal)
    avg_displacement_from_ideal = np.mean(np_displacement_from_ideal)
    std_displacement_from_ideal = np.std(np_displacement_from_ideal)
    return {
        "avg_angle_displacement": avg_angle_displacement,
        "std_angle_displacement": std_angle_displacement,
        "max_norm_displacement_from_ideal": max_norm_displacement_from_ideal,
        "min_norm_displacement_from_ideal": min_norm_displacement_from_ideal,
        "avg_norm_displacement_from_ideal": avg_norm_displacement_from_ideal,
        "std_norm_displacement_from_ideal": std_norm_displacement_from_ideal,
        "min_displacement_from_ideal": min_displacement_from_ideal,
        "max_displacement_from_ideal": max_displacement_from_ideal,
        "avg_displacement_from_ideal": avg_displacement_from_ideal,
        "std_displacement_from_ideal": std_displacement_from_ideal
    }

## create error report based on new_mean and new_std
def create_error_report(n_clusters, channel_names, mean, stdev, ideal_distance, global_error, error_analysis):
    text=""" 
        <h1>Quantitative error analysis:</h1>
    """
   
    # create table
    # what would be the headers?
    # <table></table>
    # <tr><th></th>...</tr>
    table = """<th>Channel name</th>"""
    for cluster_idx in range(n_clusters):
        table+="<th>Cluster %s</th>" % (str(cluster_idx + 1))
    table+="<th>Min error</th>"
    table+="<th>Max error</th>"
    table+="<th>Avg±std error</th>"

    table+="<th>Min error % of ideal</th>"
    table+="<th>Max error % of ideal</th>"
    table+="<th>Avg±std error % of ideal</th>"

    table = "<tr>%s</tr>" % (table)

    # now construct rows from the mean and stdev
    for channel_name in channel_names:
        row="""<td><b>%s</b></td>""" % (channel_name)
        print("mean", mean)
        print("stdev", stdev)
        print("channel_name", channel_name)
        channel_mean = mean[channel_name]
        channel_stdev = stdev[channel_name]
        for cluster_idx in range(n_clusters):
            if cluster_idx in channel_mean: # fix this normalise keys to strings always
                channel_cluster_mean = channel_mean[cluster_idx]
                channel_cluster_stdev = channel_stdev[cluster_idx]
            else:
                channel_cluster_mean = channel_mean[str(cluster_idx)]
                channel_cluster_stdev = channel_stdev[str(cluster_idx)]
            row+="""<td>%.4f±%.4f</td>""" % (channel_cluster_mean, channel_cluster_stdev)
        # work out channel min max and avg+-std
        
        np_channel_stdev = np.asarray(list(channel_stdev.values()))
        min_of_channel_errors = np.min(np_channel_stdev)
        max_of_channel_errors = np.max(np_channel_stdev)
        mean_of_channel_errors = np.mean(np_channel_stdev)
        std_of_channel_errors = np.std(np_channel_stdev)

        row+="<td>%.4f</td>" % (min_of_channel_errors)
        row+="<td>%.4f</td>" % (max_of_channel_errors)
        row+="<td>%.4f±%.4f</td>" % (mean_of_channel_errors, std_of_channel_errors)

        row+="<td>%.4f</td>" % (100.0 * (min_of_channel_errors/ideal_distance))
        row+="<td><b>%.4f</b></td>" % (100.0 * (max_of_channel_errors/ideal_distance))
        row+="<td>%.4f±%.4f</td>" % (100.0 * (mean_of_channel_errors/ideal_distance), 100.0 * (std_of_channel_errors/ideal_distance))
        
        row = """<tr>%s</tr>""" % (row)
        table += row
    table = "<table>%s</table>" % (table)

    text += """
        <h2>Cluster circular means and error</h2>
        <p>Mean cluster values and error indicates how well we know the location of the zero-crossing events, measured in [Angular steps]</p>
        """
    text += table
    # <tr><td></td>...</tr>
    text += """
        <h2>Global error:</h2>
        <h3>Global error from ideal symmetry indicates how consecutive zc-event distances deviate from ideal symmetry</h3>
        """
    text+="<ul>"
    text+="<li>Ideal distance and average displacement from ideal value error: <span style='color: red'>%.4f</span>±<b>%.4f</b> [Angular steps]</li>" % (ideal_distance, global_error)
    text+="<li>Relative error of zc-events from ideal: <b>%.4f</b> [relative error percentage]</li>" % ((global_error / ideal_distance ) * 100.0)
    text+="<li>Actual measured mean and stdev of displacements: <b>%.4f±%.4f</b> | <b>%.4f±%.4f</b> [percentage of ideal]</li>" % (error_analysis["avg_angle_displacement"], error_analysis["std_angle_displacement"], (error_analysis["avg_angle_displacement"]/ ideal_distance) * 100.0, (error_analysis["std_angle_displacement"]/ ideal_distance) * 100.0)
    text+="</ul>"

    text+="<h3>Absolute displacement from ideal symmetry</h3>"
    text+="<ul>"
    text+="<li>Min value: %.4f [Angular steps] | <b>%.4f</b> [percentage of ideal]</li>" % (error_analysis["min_norm_displacement_from_ideal"], 100.0*(error_analysis["min_norm_displacement_from_ideal"]/ideal_distance))
    text+="<li>Max value: %.4f [Angular steps] | <b>%.4f</b> [percentage of ideal]</li>" % (error_analysis["max_norm_displacement_from_ideal"], 100.0*(error_analysis["max_norm_displacement_from_ideal"]/ideal_distance))
    text+="<li>Average value: %.4f±%.4f [Angular steps] | <b>%.4f±%.4f</b> [percentage of ideal]</li>" % (error_analysis["avg_norm_displacement_from_ideal"], error_analysis["std_norm_displacement_from_ideal"], 100.0*(error_analysis["avg_norm_displacement_from_ideal"]/ideal_distance), 100.0*(error_analysis["std_norm_displacement_from_ideal"]/ideal_distance))
    text+="</ul>"

    text+="<h3>Displacement from ideal symmetry</h3>"
    text+="<ul>"
    text+="<li>Min value: %.4f [Angular steps] | <b>%.4f</b> [percentage of ideal]</li>" % (error_analysis["min_displacement_from_ideal"], 100.0*(error_analysis["min_displacement_from_ideal"]/ideal_distance))
    text+="<li>Max value: %.4f [Angular steps] | <b>%.4f</b> [percentage of ideal]</li>" % (error_analysis["max_displacement_from_ideal"], 100.0*(error_analysis["max_displacement_from_ideal"]/ideal_distance))
    text+="<li>Average value: %.4f±%.4f [Angular steps] | <b>%.4f±%.4f</b> [percentage of ideal]</li>" % (error_analysis["avg_displacement_from_ideal"], error_analysis["std_displacement_from_ideal"], 100.0*(error_analysis["avg_displacement_from_ideal"]/ideal_distance), 100.0*(error_analysis["std_displacement_from_ideal"]/ideal_distance))
    text+="</ul>"
    return text