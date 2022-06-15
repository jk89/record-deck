import pyspark
from pyspark.sql import SQLContext
from pyspark.sql import Window
from pyspark.sql.functions import pandas_udf, col,from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, DoubleType
import pandas as pd
import json

dataset_name = "serial-data-2.dat"
json_cache_name = "kalman-filtered-" + dataset_name + ".json"
json_file_path = "calibration/__pycache__/" + json_cache_name
json_str_data = None
data = None
with open(json_file_path, "r") as fin:
    json_str_data = fin.read()
    data = json.loads(json_str_data)

zipped_data = list(zip(*data))

# data like:
# [[idx],[kalman_angle],[kalman_a_minus_vn],[kalman_b_minus_vn], [kalman_c_minus_vn]]

sc = pyspark.SparkContext(master="spark://10.0.0.3:6060")
sqlContext = SQLContext(sc)

# create kernel for zero_crossing detection, -1 means require negative, +1 require positive, 0 - ignore value
rising_zero_crossing_kernel = [-1.0, 0.0, 1.0]#[-1.0, -1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, +1.0, +1.0, +1.0]
kernel_size = len(rising_zero_crossing_kernel)  # 11 (11-1)/2=5
kernel_midpoint = int((kernel_size - 1) / 2)
falling_zero_crossing_kernel = []
for k in range(kernel_size):
    rising_value = rising_zero_crossing_kernel[k]
    falling_value = 0 if rising_value == 0 else -rising_value
    falling_zero_crossing_kernel.append(falling_value)


test_data = [(0, -10.0), (1, -6.0), (2, -4.0), (3, -1.0), (4, 0.0), (5, 1.0),
             (6, 0.0), (7, +1.0), (8, +2.0), (9, +6.0), (10, +10.0), (11, +11.0), (12, +12.0)]
# 13 datapoint

tupleSchema = StructType([
    StructField("l", FloatType(), False),
    StructField("r", FloatType(), False)])


@pandas_udf("double")
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


@pandas_udf("double")
def zc_channel_kernel_rising(v: pd.Series) -> float:

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
    else:
        return 0


@pandas_udf("double")
def zc_channel_kernel_falling(v: pd.Series) -> float:

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

    if falling_signal == True and rising_signal == False:
        return +1
    else:
        return 0


#df = sqlContext.createDataFrame(
#    test_data, ("id", "v"))
#w = Window.rowsBetween(-kernel_midpoint, kernel_midpoint)
#df.withColumn('zc_kernel_results', zc_channel_kernel("v").over(w)).show()

# create real df


# data like:
# [[idx],[kalman_angle],[kalman_a_minus_vn],[kalman_b_minus_vn], [kalman_c_minus_vn]]

adc_encoder_df = sqlContext.createDataFrame(zipped_data, ("idx", "angle", "a", "b", "c"))

w = Window.rowsBetween(-kernel_midpoint, kernel_midpoint)

# zc_channel_kernel_falling

adc_encoder_df = adc_encoder_df.withColumn('kernel_a_rising', zc_channel_kernel_rising("a").over(w))
adc_encoder_df = adc_encoder_df.withColumn('kernel_a_falling', zc_channel_kernel_falling("a").over(w))
adc_encoder_df = adc_encoder_df.withColumn('kernel_b_rising', zc_channel_kernel_rising("b").over(w))
adc_encoder_df = adc_encoder_df.withColumn('kernel_b_falling', zc_channel_kernel_falling("b").over(w))
adc_encoder_df = adc_encoder_df.withColumn('kernel_c_rising', zc_channel_kernel_rising("c").over(w))
adc_encoder_df = adc_encoder_df.withColumn('kernel_c_falling', zc_channel_kernel_falling("c").over(w))

# adc_encoder_df['a_rising_sum'] = adc_encoder_df.groupby(['angle'])['kernel_a_rising'].transform('sum')
# .agg({'att1': "count", 'att3': "sum",'att4': 'mean'})
# df2 = adc_encoder_df.groupby('angle').sum() # ['kernel_a_rising']
adc_encoder_df = adc_encoder_df.orderBy("angle").groupby('angle').agg(
    {
        'kernel_a_rising': "sum",
        'kernel_a_falling': "sum",

        'kernel_b_rising': "sum",
        'kernel_b_falling': "sum",

        'kernel_c_rising': "sum",
        'kernel_c_falling': "sum",
    }
)
#adc_encoder_df.show(16383)

processed_data = adc_encoder_df.collect()


#unzipped_data = list(zip(*processed_data))

#angle_voltage_zc_data = [
#    adc_encoder_df.select("angle").collect(),
#    adc_encoder_df.select("sum(kernel_a_rising)").collect(),
#    adc_encoder_df.select("sum(kernel_a_falling)").collect(),
#    adc_encoder_df.select("sum(kernel_b_rising)").collect(),
#   adc_encoder_df.select("sum(kernel_b_falling)").collect(),
#    adc_encoder_df.select("sum(kernel_c_rising)").collect(),
#    adc_encoder_df.select("sum(kernel_c_falling)").collect(),
#]

# df['tfr'].values

#adc_encoder_df.show(1000)

print(processed_data)
