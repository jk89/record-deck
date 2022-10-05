import numpy as np
import metrics
from typing import Dict, List, Tuple
from scipy.fft import fft, ifft, dct, fftshift, fftfreq
import scipy.signal as signal
import math
from report import Report

Translated_Histogram = Dict[str, Dict[str,List[int]]]
Channel_Cluster_Std = Dict[str,Dict[str,float]]
Merged_Channel_Cluster_Means = Dict[str, Dict[int, float]] # {'zc_channel_ar_data': {'14060': 0, '14064': 0, 
Histograms = List[Dict[str,List[int]]] # histograms like [{channelname1:{angles:[0,1,2,3,4...],data:[0,00,0,0,0,1,23,45,6,4,3,1,00000000]}, channelname2:{angles,data},....},]

def circular_mean(cluster_members: List):
    cos_components = []
    sin_components = []
    for cluster_member_angle in cluster_members: # cluster_members
        scale = (2*math.pi/16384)
        cos_components.append(math.cos(scale * cluster_member_angle))
        sin_components.append(math.sin(scale * cluster_member_angle))
        # divide by sum of weights?
    np_cos_components = np.asarray(cos_components)
    np_sin_components = np.asarray(sin_components)
    mean_cos = np.sum(np_cos_components) # maybe mean
    mean_sin = np.sum(np_sin_components)
    avg_angle = (np.arctan2(mean_sin, mean_cos) * (16384/(2*np.pi))) % 16384
    return avg_angle

def weighted_circular_mean(cluster_members, weights): # limitation weights have to sum to one! FIXME
    cos_components = []
    sin_components = []
    # make cluster members unique?
    for cluster_member_angle in list(set(cluster_members)): # cluster_members
        weight = weights[cluster_member_angle]
        scale = (2*math.pi/16384)
        cos_components.append(weight * math.cos(scale * cluster_member_angle))
        sin_components.append(weight * math.sin(scale * cluster_member_angle))
        # divide by sum of weights?
    np_cos_components = np.asarray(cos_components)
    np_sin_components = np.asarray(sin_components)
    mean_cos = np.sum(np_cos_components) # maybe mean
    mean_sin = np.sum(np_sin_components)
    avg_angle = (np.arctan2(mean_sin, mean_cos) * (16384/(2*np.pi))) % 16384
    return avg_angle

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

def dict_to_value_ordered_lkv_tuple_list(label, dict) -> List[Tuple[str, int, float]]: # label, key, value
    keys = list(dict.keys())
    values = list(dict.values())
    kv = [(label, keys[i], values[i]) for i in range(len(keys))]
    # order this by value
    return sorted(kv, key=lambda x: x[2])

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

def shift_datasets_by_cluster_mean_center_displacements_from_combined_center(histograms: Histograms, channel_names: List[str], n_clusters: int, merge_dataset_channel_clusters_identifier_map, merge_dataset_channel_clusters_circular_mean_map: Merged_Channel_Cluster_Means):
    #merge_dataset_channel_clusters_identifier_map is like
    

    #merge_dataset_channel_clusters_circular_mean_map
    # like {'zc_channel_ar_data': {0: 176.06523200393102, 1: 9487.414869993805,

    #circular_mean

    # rebuild dataset channel cluster members # TODO check centroid is correctly in the set
    # iterate histograms and use identifier to cluster the angles

    dataset_channel_cluster_members = {}
    for histogram_idx in range(len(histograms)):
        histogram_idx_str = str(histogram_idx)
        dataset_channel_cluster_members[histogram_idx_str] = {}
        histogram = histograms[histogram_idx]
        for channel_name in channel_names:
            dataset_channel_cluster_members[histogram_idx_str][channel_name] = {}
            histogram_channel = histogram[channel_name]# like {angles:[0,1,2],data:[0,0,1,]}
            histogram_channel_angles = [i for i in range(16384)]
            histogram_channel_data = histogram_channel["data"]
            for angle in histogram_channel_angles:
                angle_str = str(angle)
                angle_dataset_channel_cluster_count = histogram_channel_data[angle]
                if angle_str in merge_dataset_channel_clusters_identifier_map[channel_name]:
                    cluster_idx = merge_dataset_channel_clusters_identifier_map[channel_name][angle_str]
                    if cluster_idx not in dataset_channel_cluster_members[histogram_idx_str][channel_name]:
                        dataset_channel_cluster_members[histogram_idx_str][channel_name][cluster_idx] = []
                    for _ in range(angle_dataset_channel_cluster_count):
                        dataset_channel_cluster_members[histogram_idx_str][channel_name][cluster_idx].append(angle)

    # calculate mean centers for each dataset cluster member
    dataset_channel_cluster_mean_centers = {}
    for histogram_idx in range(len(histograms)):
        histogram_idx_str = str(histogram_idx)
        dataset_channel_cluster_mean_centers[histogram_idx_str] = {}
        for channel_name in channel_names:
            dataset_channel_cluster_mean_centers[histogram_idx_str][channel_name] = {}
            for cluster_idx in list(dataset_channel_cluster_members[histogram_idx_str][channel_name].keys()):
                cluster_idx_str = str(cluster_idx)
                angles = dataset_channel_cluster_members[histogram_idx_str][channel_name][cluster_idx]
                dataset_channel_cluster_circular_mean = circular_mean(angles)
                dataset_channel_cluster_mean_centers[histogram_idx_str][channel_name][cluster_idx_str] = dataset_channel_cluster_circular_mean

    # compare mean centers of each dataset channel cluster to the combined dataset channel cluster means
    
    #    #merge_dataset_channel_clusters_circular_mean_map
    # like {'zc_channel_ar_data': {0: 176.06523200393102, 1: 9487.414869993805,
    #   #dataset_channel_cluster_mean_centers
    # like {"0":{'zc_channel_ar_data': {"0": 176.06523200393102, "1": 9487.414869993805,}
    dataset_channel_cluster_translations = {}
    for dataset_id in list(dataset_channel_cluster_mean_centers.keys()):
        dataset_channel_cluster_translations[dataset_id] = {}
        for channel_name in channel_names:
            dataset_channel_cluster_translations[dataset_id][channel_name] = {}
            # n_clusters
            for cluster_idx in range(n_clusters):
                cluster_idx_str = str(cluster_idx)
                # dataset_channel_cluster_translations[dataset_id][channel_name][cluster_idx_str]
                merged_cluster_mean_center = merge_dataset_channel_clusters_circular_mean_map[channel_name][int(cluster_idx_str)]
                current_dataset_cluster_mean_center = dataset_channel_cluster_mean_centers[dataset_id][channel_name][cluster_idx_str]
                # find the displacement
                # calculate_distance_mod_scalar(last_theta, current_theta) -> current_theta - last_theta
                distance_between_mean_centers = metrics.calculate_distance_mod_scalar(merged_cluster_mean_center,current_dataset_cluster_mean_center)
                #print("dataset channel cluster cluster_mean c_dataset_mean distance", dataset_id, channel_name, cluster_idx_str, merged_cluster_mean_center,current_dataset_cluster_mean_center,  distance_between_mean_centers)
                dataset_channel_cluster_translations[dataset_id][channel_name][cluster_idx_str] = distance_between_mean_centers

    print("dataset_channel_cluster_translations", dataset_channel_cluster_translations)

    # translate the angles and histogram by the distance for each dataset channel cluster
    # translated angle vs count map [channel][cluster_idx]
    # and calculate cluster error
    translated_histogram_map = {}
    channel_cluster_std: Channel_Cluster_Std = {}
    for channel_name in channel_names:
        translated_histogram_map[channel_name] = {}
        channel_cluster_std[channel_name] = {}
        for cluster_idx in range(n_clusters):
            cluster_idx_str = str(cluster_idx)
            translated_histogram_map[channel_name][cluster_idx_str] = {}
            #
            #channel_cluster_std[channel_name][cluster_idx_str] = {}
            for histogram_idx in range(len(histograms)):
                    histogram_idx_str = str(histogram_idx)
                    translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str] = {}
            channel_cluster_translated_angles = []
            for angle in range(16384):
                angle_str = str(angle)

                cluster_idx_identified = None 
                if angle_str in merge_dataset_channel_clusters_identifier_map[channel_name]:
                    cluster_idx_identified = merge_dataset_channel_clusters_identifier_map[channel_name][angle_str]
                
                cluster_idx_identified_str = str(cluster_idx_identified)
                # print("cluster_idx_identified_str, cluster_idx_str", cluster_idx_identified_str, cluster_idx_str, cluster_idx_identified_str == cluster_idx_str)


                for histogram_idx in range(len(histograms)):
                    histogram_idx_str = str(histogram_idx)
                    dataset_channel_angle_count = histograms[histogram_idx][channel_name]["data"][angle]
                    translation = dataset_channel_cluster_translations[histogram_idx_str][channel_name][cluster_idx_str]
                    translated_angle = (angle - translation) % 16384
                    binned_translated_angle = int(round_nearest(translated_angle, 1)) % 16384
                    binned_translated_angle_str = str(binned_translated_angle)

                    if cluster_idx_identified_str == cluster_idx_str:
                        #print("ep", channel_name, histogram_idx_str, cluster_idx_str, translation, angle, translated_angle)
                        for _ in range(dataset_channel_angle_count): # for stdev
                            channel_cluster_translated_angles.append(translated_angle)
                        # for hist
                    if cluster_idx_identified_str == cluster_idx_str:
                        if binned_translated_angle_str not in translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str]:
                            translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str][binned_translated_angle_str] = dataset_channel_angle_count
                        else:
                            translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str][binned_translated_angle_str] += dataset_channel_angle_count
                    else:
                        if binned_translated_angle_str not in translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str]:
                            translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str][binned_translated_angle_str] = 0
                        
                
            # calculate errors pairwise from translated channel cluster angles to their combined mean cluster center
            channel_cluster_combined_circular_mean = merge_dataset_channel_clusters_circular_mean_map[channel_name][int(cluster_idx_str)]
            translated_channel_cluster_std = get_stdev_for_channel(channel_cluster_translated_angles,channel_cluster_combined_circular_mean)
            channel_cluster_std[channel_name][cluster_idx_str] = translated_channel_cluster_std

    # create histogram from histogram map
    # merge the translated dataset channel cluster datapoints ?? maybe not
    # translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str]

    #print("translated_histogram_map", translated_histogram_map)

    translated_histogram: Translated_Histogram = {}

    # we want translated_histogram[channel_name] = {angles:[0,1,2,3], "0"datasetIdx:[0,0,4,2,1,0], "1": [0,0,0,0,0,1]}
    for channel_name in channel_names:
        translated_histogram[channel_name] = {"angles": [i for i in range(16384)]}
        for histogram_idx in range(len(histograms)):
            histogram_idx_str = str(histogram_idx)
            translated_histogram[channel_name][histogram_idx_str] = []


    # translated_histogram_map {'zc_channel_ar_data': {'0': {'0': {'16321': 0, '16322': 0, '16323': 0,
    # translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str][binned_translated_angle_str] = angle_count


    for angle in range(16384):
        angle_str = str(angle)
        # for each angle we need to merge each contribution from each channel_name and cluster_idx for all datasets
        for histogram_idx in range(len(histograms)):
            histogram_idx_str = str(histogram_idx)
            for channel_name in channel_names:
                # all cluster counts
                angle_count = 0
                for cluster_idx in range(n_clusters):
                    cluster_idx_str = str(cluster_idx)
                    ## this is broken
                    #print("ahhhhh", channel_name, cluster_idx_str, histogram_idx_str, angle_str)
                    #print("ahhhhhhhhh2", translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str])
                    dataset_channel_angle_count = translated_histogram_map[channel_name][cluster_idx_str][histogram_idx_str][angle_str]
                    angle_count += dataset_channel_angle_count
                translated_histogram[channel_name][histogram_idx_str].append(angle_count)
    
    return (channel_cluster_std, translated_histogram)




def append_translated_error_report_figure(parent_report: Report, channel_names: List[str], ideal_distance, number_of_clusters: int, channel_cluster_std: Channel_Cluster_Std, merged_channel_cluster_means):
    text="""
    <h2>Quantitative error analysis of translated histograms</h2>
    <p>
        Errors calculated by translating each cluster.
    </p>
    """
    parent_report.add_figure(Report.models["Div"](text=text))
    table = """<th>Channel name</th>"""
    for cluster_idx in range(number_of_clusters):
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
        print("mean", merged_channel_cluster_means)
        print("stdev", channel_cluster_std)
        print("channel_name", channel_name)
        channel_mean = merged_channel_cluster_means[channel_name]
        channel_stdev = channel_cluster_std[channel_name]
        for cluster_idx in range(number_of_clusters):
            if cluster_idx in channel_mean: # fix this normalise keys to strings always
                channel_cluster_mean = channel_mean[cluster_idx]
                channel_cluster_stdev = channel_stdev[str(cluster_idx)]
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
    parent_report.add_figure(Report.models["Div"](text = table))

def append_translated_histogram_figure(parent_report: Report, dataset_names:List[str], number_of_clusters:int, channel_cluster_std: Channel_Cluster_Std, translated_histogram: Translated_Histogram, merged_channel_cluster_means):
    # append header
    text="""
    <h1>Translated histograms - analysing cluster errors accounting for the systemic error</h1>
    <p>
    By calculating the distance from the mean centers of each datasets channel cluster to the mean center of the merged datasets channel cluster.
    The histogram values are translated and error recalculated, thus eliminating the systemic error.
    </p>
    """
    parent_report.add_figure(Report.models["Div"](text=text))
    for channel_name in list(translated_histogram.keys()):
        len_datasets = len(dataset_names)
        histogram_keys = [str(i) for i in range(len_datasets)]
        fig = Report.figure(title=channel_name, plot_height=150, plot_width=1600)
        fig.x_range=Report.models["Range1d"](0, 18500)
        start_color = None
        end_color = None
        if channel_name == "zc_channel_ar_data" or channel_name == "zc_channel_af_data": # red
            start_color=Report.Color("#8b0000")
            end_color=Report.Color("#ffcccb")
        if channel_name == "zc_channel_br_data" or channel_name == "zc_channel_bf_data": # yellow
            start_color=Report.Color("#8B8000")
            end_color=Report.Color("#FFFF00")
        if channel_name == "zc_channel_cr_data" or channel_name == "zc_channel_cf_data": # black
            start_color=Report.Color("#000000")
            end_color=Report.Color("#D3D3D3")
        colors = [i.get_web() for i in list(start_color.range_to(end_color,len_datasets))]
        fig.vbar_stack(histogram_keys, x='angles', source=translated_histogram[channel_name], legend_label=dataset_names, color=colors)
        
        # create errors
        for i in range(number_of_clusters):
            cluster_idx_str = str(i)
            # get cluster error value
            error = channel_cluster_std[channel_name][cluster_idx_str]
            mean = merged_channel_cluster_means[channel_name][i]

            lower_bound_line = Report.models["Span"](location=mean-error, dimension='height', line_color='blue', line_dash='solid', line_width=1)
            fig.add_layout(lower_bound_line)
            upper_bound_line = Report.models["Span"](location=mean+error, dimension='height', line_color='blue', line_dash='solid', line_width=1)
            fig.add_layout(upper_bound_line)
            base_bound_line = Report.models["Span"](location=mean, dimension='height', line_color='purple', line_dash='solid', line_width=1)
            fig.add_layout(base_bound_line)
        
        parent_report.add_figure(fig)


def channel_name_to_descriptor(channel_name):
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

def channel_name_and_direction_state(direction: str, channel_name: str):
    if (direction != "cw" and direction != "ccw"):
       raise "Direction needs to be cw or ccw"
    if channel_name == "zc_channel_ar_data":
        if direction == "cw":
            return 2
        elif direction == "ccw":
            return 5
    elif channel_name == "zc_channel_af_data":
        if direction == "cw":
            return 5
        elif direction == "ccw":
            return 2
    elif channel_name == "zc_channel_br_data":
        if direction == "cw":
            return 4
        elif direction == "ccw":
            return 1
    elif channel_name == "zc_channel_bf_data":
        if direction == "cw":
            return 1
        elif direction == "ccw":
            return 4
    elif channel_name == "zc_channel_cr_data":
        if direction == "cw":
            return 0
        elif direction == "ccw":
            return 3
    elif channel_name == "zc_channel_cf_data":
        if direction == "cw":
            return 3
        elif direction == "ccw":
            return 0
    else:
        raise "Unknown channel_name " + channel_name

def process_mean_kv_sequence_midpoints(sequence, direction):
    len_sequence = len(sequence)
    stripe = []
    for sequence_idx in range(len_sequence):
        c_mean = sequence[sequence_idx][2]
        c_cluster = sequence[sequence_idx][1]
        c_channel = sequence[sequence_idx][0]

        # what was the last value
        l_index = None
        if (sequence_idx == 0):
            l_index = len_sequence - 1
        else:
            l_index = sequence_idx - 1
        l_mean = sequence[l_index][2]
        l_cluster = sequence[l_index][1]
        l_channel = sequence[l_index][0]
        
        midpoint = circular_mean([c_mean, l_mean])
        midpoint = int(round_nearest(midpoint, 1)) % 16384
        state = channel_name_and_direction_state(direction, c_channel)
        # round and mod midpoint TODO

        stripe.append((state, midpoint))
        # c_channel identifies 
    return stripe #circular_mean

State_Map = Dict[str,int]

def create_state_angle_map(state_start_points) -> State_Map:  #direction
    angles = {}
    len_state_start_points = len(state_start_points)
    for zone_idx in range(len_state_start_points):
        c_state, c_angle = state_start_points[zone_idx]
        next_state_idx = None
        if zone_idx == len_state_start_points - 1:
            next_state_idx = 0 # we are at the end
        else:
            next_state_idx = zone_idx + 1
        n_state, n_angle = state_start_points[next_state_idx]

        # angular distance to next state transition
        #if direction == "cw":
        #    pass # n_angle > c_angle
        #elif direction == "ccw":
        #    pass # n_angle < c_angle
        #else:
        #    raise "Need to provide a direction = 'cw' or 'ccw'"
        
        # distance = (n_angle - c_angle) % 16384
        distance = metrics.calculate_distance_mod_scalar(c_angle, n_angle)
        # current - last

        print("angle_map_Create.. c_angle, n_angle, zone_idx, distance", c_angle, n_angle, zone_idx, distance, type(distance))
        # if n_angle > c_angle distance +ve
        # if n_angle < c_angle distance -ve

        distance_range = None
        if (distance < 0):
            distance_range = range(distance + 1, 1) #range(distance, 0)
        elif (distance > 0):
            distance_range = range(0, distance)
        else:
            raise "Distance should not be 0"

        #  [i for i in range(-404,0)] -404,-403,...-1 DOES NOT INCLUDE THIS ANGLE 0 away from c_angle
        # [i for i in range(-403, 1)] -403,-402,... 0
        # range(0,404) 0,1,.....403 CORRECT


        for i in distance_range:
            angle_to_save_state = (c_angle + i) % 16384
            #print("angle_to_save_state", angle_to_save_state)
            angle_to_save_state_str = str(angle_to_save_state)
            angles[angle_to_save_state_str] = c_state
        print("----")
    # order angles
    
    out_map: Dict[str,int] = {}
    for i in range(16384):
       out_map[str(i)] = angles[str(i)]
    return out_map

Final_State_Map_Histogram = Dict[str, int]
def split_states_into_binary_histogram(angle_state_map: State_Map):
    histograms: Final_State_Map_Histogram = {"0":[],"1":[],"2":[],"3":[],"4":[],"5":[],"angles": list(range(16384))}
    states = ["0","1","2","3","4","5"]
    # filter true to keep
    for i in range(16384):
        state = angle_state_map[str(i)]
        state_str = str(state)
        other_states_str = filter(lambda x: x!=state_str,states)
        histograms[state_str].append(1)
        for other_state_str in other_states_str:
            histograms[other_state_str].append(0)
    return histograms

def create_bidirectional_state_angle_map(merged_channel_cluster_means: Merged_Channel_Cluster_Means):
    # create tuple dict
    ordered_mean_lkv_tuple_list_cw = mean_to_ordered_lkv(merged_channel_cluster_means)
    # reverse for ccw
    ordered_mean_lkv_tuple_list_ccw = sorted(ordered_mean_lkv_tuple_list_cw, key=lambda x: x[2], reverse=True)

    #cw_zc_ordered_angles = get_ordered_angles_from_mean(ordered_mean_lkv_tuple_list_cw)
    #ccw_zc_ordered_angles = get_ordered_angles_from_mean(ordered_mean_lkv_tuple_list_ccw)

    print("ordered_mean_lkv_tuple_list_cw")
    print(ordered_mean_lkv_tuple_list_cw)

    print("ordered_mean_lkv_tuple_list_ccw")
    print(ordered_mean_lkv_tuple_list_ccw)

    midpoints_ordered_mean_lkv_tuple_list_cw = process_mean_kv_sequence_midpoints(ordered_mean_lkv_tuple_list_cw, "cw")
    midpoints_ordered_mean_lkv_tuple_list_ccw = process_mean_kv_sequence_midpoints(ordered_mean_lkv_tuple_list_ccw, "ccw")

    print("midpoints_ordered_mean_lkv_tuple_list_cw")
    print(midpoints_ordered_mean_lkv_tuple_list_cw)

    print("midpoints_ordered_mean_lkv_tuple_list_ccw")
    print(midpoints_ordered_mean_lkv_tuple_list_ccw)

    state_map_cw = create_state_angle_map(midpoints_ordered_mean_lkv_tuple_list_cw)
    state_map_ccw = create_state_angle_map(midpoints_ordered_mean_lkv_tuple_list_ccw)

    print("state_map_cw", state_map_cw)
    print("state_map_ccw", state_map_ccw)
    return (state_map_cw, state_map_ccw)

def append_state_map_histogram_figure(parent_report: Report, direction: str, cw_or_ccw_state_map: State_Map):
    histogram_data = split_states_into_binary_histogram(cw_or_ccw_state_map)
    print("state_map_hist", direction, histogram_data)
    states = ["0","1","2","3","4","5"]
    state_names = ["State %s" % (i) for i in states]
    fig = Report.figure(title="%s State Map" % (direction.upper()), plot_height=300, plot_width=1600) # 12000 1600 plot_width=1200, y_range=(0, 17000) plot_width=10000 # plot_width=10000,
    fig.x_range=Report.models["Range1d"](0, 18500)
    start_color=Report.Color("#2F5A3B")
    end_color=Report.Color("#E9692C")
    colors = [i.get_web() for i in list(start_color.range_to(end_color,len(states)))]
    fig.vbar_stack(states, x='angles', source=histogram_data, legend_label=state_names, color=colors)
    fig.xaxis.axis_label = 'Angle [steps]'
    fig.yaxis.axis_label = 'Commutation State'
    parent_report.add_figure(fig)