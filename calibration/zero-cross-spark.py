from pyspark.sql import SQLContext
from pyspark.sql import Window
from pyspark.sql.functions import pandas_udf
import calibration.spark_context as spark_context
import pandas as pd
import json
import sys

run_id = sys.argv[1] if len(sys.argv) > 1 else 0 
file_in = 'datasets/data/calibration-data/%s/kalman_smoothed_merged_capture_data.json' % (run_id)

file_out_zc = 'datasets/data/calibration-data/%s/zero_crossing_detections.channels.all.json' % (run_id)
file_out_hist = 'datasets/data/calibration-data/%s/zero_crossing_detections.histogram.all.json' % (run_id)

# run_id = "serial-data-2.dat"
# Load data.
#json_cache_name = "kalman-filtered-" + run_id + ".json"
json_file_path = file_in# "calibration/__pycache__/" + json_cache_name
json_str_data = None
data = None
with open(json_file_path, "r") as fin:
    json_str_data = fin.read()
    data = json.loads(json_str_data) # [[idx],[kalman_angle],[kalman_a_minus_vn],[kalman_b_minus_vn], [kalman_c_minus_vn]]

zipped_data = list(zip(*data)) # [[idx, kalman_angle, kalman_a_minus_vn, kalman_b_minus_vn, kalman_c_minus_vn],[...],...]

# Get spark context.
sc = spark_context.get_spark_context()
SQLContext = SQLContext(sc)

# Create kernel for zero_crossing detection, -1 means require negative, +1 require positive, 0 ignore value.
rising_zero_crossing_kernel = [-1.0, 0.0, 1.0]
kernel_size = len(rising_zero_crossing_kernel)
kernel_midpoint = int((kernel_size - 1) / 2)
falling_zero_crossing_kernel = []
for k in range(kernel_size):
    rising_value = rising_zero_crossing_kernel[k]
    falling_value = 0 if rising_value == 0 else -rising_value
    falling_zero_crossing_kernel.append(falling_value)


# Define kernel function to detect zero-crossing.
def zc_channel_kernel(v: pd.Series) -> float:
    if v.size < kernel_size:
        return 0
    falling_signal = True
    rising_signal = True
    k_idx = 0
    for kd_idx, kd_element in v.items():
        rising_test = rising_zero_crossing_kernel[k_idx]
        falling_test = falling_zero_crossing_kernel[k_idx]

        sign_kd_element = 0.0
        if kd_element > 0.0:
            sign_kd_element = +1.0
        elif kd_element < 0.0:
            sign_kd_element = -1.0
        # rising
        if (rising_test != 0.0 and sign_kd_element != rising_test):
            if sign_kd_element != 0:
                rising_signal = False
        # falling
        if (falling_test != 0.0 and sign_kd_element != falling_test):
            if sign_kd_element != 0:
                falling_signal = False
        k_idx += 1
    if rising_signal == True and falling_signal == False:
        return +1
    elif rising_signal == False and falling_signal == True:
        return -1
    else:
        return 0

# Rising kernel detector.
@pandas_udf("double")
def zc_channel_kernel_rising(v: pd.Series) -> float:
    rising_or_falling = zc_channel_kernel(v)
    if rising_or_falling == +1.0:
        return 1
    else:
        return 0

# Falling kernel detector.
@pandas_udf("double")
def zc_channel_kernel_falling(v: pd.Series) -> float:
    rising_or_falling = zc_channel_kernel(v)
    if rising_or_falling == -1.0:
        return 1
    else:
        return 0

# Define kalman measurements dataframe.
# [[idx, kalman_angle, kalman_a_minus_vn, kalman_b_minus_vn, kalman_c_minus_vn],[...],...]
rotation_voltage_df = SQLContext.createDataFrame(zipped_data, ("idx", "angle", "a", "b", "c"))
w = Window.rowsBetween(-kernel_midpoint, kernel_midpoint)

# Apply zero detectors to each channel.
rotation_voltage_df = rotation_voltage_df.withColumn('kernel_a_rising', zc_channel_kernel_rising("a").over(w))
rotation_voltage_df = rotation_voltage_df.withColumn('kernel_a_falling', zc_channel_kernel_falling("a").over(w))
rotation_voltage_df = rotation_voltage_df.withColumn('kernel_b_rising', zc_channel_kernel_rising("b").over(w))
rotation_voltage_df = rotation_voltage_df.withColumn('kernel_b_falling', zc_channel_kernel_falling("b").over(w))
rotation_voltage_df = rotation_voltage_df.withColumn('kernel_c_rising', zc_channel_kernel_rising("c").over(w))
rotation_voltage_df = rotation_voltage_df.withColumn('kernel_c_falling', zc_channel_kernel_falling("c").over(w))

# Accumulate within each zero_crossing channel (a-rising, a-falling, b-rising, b-falling, c-rising, c-falling) 6 in total
# the measurements are taken over time and as the motor rotates. Zero crossing detection will find -ve to +ve (or vice versa) transitions.
# Group each channels data by the angle and order it.
rotation_voltage_df = rotation_voltage_df.orderBy("angle").groupby('angle')

# Sum the detections over each respective angle for each channel. This collects a histogram of zero crossing detection counts at a given angle.
zc_channel_histogram = rotation_voltage_df.agg(
    {
        'kernel_a_rising': "sum",
        'kernel_a_falling': "sum",
        'kernel_b_rising': "sum",
        'kernel_b_falling': "sum",
        'kernel_c_rising': "sum",
        'kernel_c_falling': "sum",
    }
)

# Display the zero-crossing histogram
# zc_channel_histogram.show(16383)

# Collect the histogram
processed_data = zc_channel_histogram.collect()

#print(processed_data)

# [ Row(angle=16383.0, sum(kernel_a_rising)=0.0, sum(kernel_a_falling)=0.0, sum(kernel_c_rising)=0.0, sum(kernel_c_falling)=0.0, sum(kernel_b_rising)=0.0, sum(kernel_b_falling)=0.0)]



#import json

#with open(file_in + ".zc.json", "wb") as fout:
#    fout.write(json.dumps(processed_data))

#|16382.0|                 0.0|                  0.0|                 0.0|                  0.0|                 0.0|                  0.0|

angle_data=[]
zc_channel_ar_data=[]
zc_channel_af_data=[]
zc_channel_br_data=[]
zc_channel_bf_data=[]
zc_channel_cr_data=[]
zc_channel_cf_data=[]

# for each angle
#  add the angle to the respective channel above, do this for each count in the histogram
# e.g. if at angle 0 and that there are 3 times a zc was detected in the a_r channel then zc_channel_ar_data.concat([angle,angle,angle])

zc_hist = []

for row in processed_data:
    angle = int(row["angle"])

    kernel_a_rising = int(row["sum(kernel_a_rising)"])
    kernel_a_falling = int(row["sum(kernel_a_falling)"])

    kernel_b_rising = int(row["sum(kernel_b_rising)"])
    kernel_b_falling = int(row["sum(kernel_b_falling)"])

    kernel_c_rising = int(row["sum(kernel_c_rising)"])
    kernel_c_falling = int(row["sum(kernel_c_falling)"])

    angle_data.append(angle)

    zc_hist.append({"kernel_a_rising": kernel_a_rising, "kernel_a_falling": kernel_a_falling, "kernel_b_rising": kernel_b_rising, "kernel_b_falling": kernel_b_falling, "kernel_c_rising": kernel_c_rising, "kernel_c_falling": kernel_c_falling, "angle": angle})

    for i in range(kernel_a_rising):
        zc_channel_ar_data.append([angle])
    for i in range(kernel_a_falling):
        zc_channel_af_data.append([angle])

    for i in range(kernel_b_rising):
        zc_channel_br_data.append([angle])
    for i in range(kernel_b_falling):
        zc_channel_bf_data.append([angle])

    for i in range(kernel_c_rising):
        zc_channel_cr_data.append([angle])
    for i in range(kernel_c_falling):
        zc_channel_cf_data.append([angle])

import json
output = {"angle": angle_data, "zc_channel_ar_data": zc_channel_ar_data, "zc_channel_af_data": zc_channel_af_data, "zc_channel_br_data": zc_channel_br_data, "zc_channel_bf_data": zc_channel_bf_data, "zc_channel_cr_data": zc_channel_cr_data, "zc_channel_cf_data": zc_channel_cf_data}

with open(file_out_zc, "w") as fout:
    fout.write(json.dumps(output))

with open(file_out_hist, "w") as fout:
    fout.write(json.dumps(zc_hist))

pole_count = 12
expected_number_channel_clusters = int(pole_count/2)

# kmedoids
# fit {expected_number_channel_clusters} centroids for each channel

# calculate mean + stdev
# exclude outliers
# recalculate mean

# finalise exact angle where zc occurs for each sample. Coerce mean value to nearest int angle and create datastructure for this.

# determine sequence direction (cw or ccw) and validate that it is consistant throughout the sample.

# save this data if it validated ok


