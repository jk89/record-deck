from scipy.optimize import curve_fit
import numpy as np
import json
import sys

run_id = sys.argv[1] if len(sys.argv) > 1 else 0 
file_in_json = 'datasets/data/calibration-data/%s/kalman_smoothed_merged_capture_data.json' % (run_id)

time_data = []
angle_data = []
a_neg_vn_data = []
b_neg_vn_data = []
c_neg_vn_data = []

with open(file_in_json, "r") as fin:
    json_data_str = "\n".join(fin.readlines())
    json_data = json.loads(json_data_str)
    time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data = json_data

time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data = list(map(lambda x:np.asarray(x), [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]))

print(list(map(lambda x: len(x), [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data])))
print(list(map(lambda x: x[0], [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data])))
print(list(map(lambda x: type(x[0]), [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data])))

print("TERM")