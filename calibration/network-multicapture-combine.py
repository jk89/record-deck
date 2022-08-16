import pandas as pd
import sys

# read dataset argument
dataset_name = sys.argv[1] if len(sys.argv) > 1 else 0 
filename = './datasets/data/calibration-data/%s' % (dataset_name)

df = pd.read_json(filename, lines=True)

df = df.groupby(by="time")
df = df.agg({"time": "max", "deviceId": set, "line": set})
df["lineCount"] = df["line"].map(lambda x: len(x))

matched_unique_records = df[df["lineCount"]==2]
print(matched_unique_records)

# line counts of 3, 2 and 1

total_unique_times = len(df)
total_unique_times_matched = len(matched_unique_records)
total_unique_times_unmatched = len(df[df["lineCount"]==1])
total_unique_times_overmatched = len(df[df["lineCount"]>2])

print("Total collected datapoints from either device:", total_unique_times)
print("Unmatched datapoints from the same time from either device:", total_unique_times_unmatched)
print("More than two matches for a datapoint from both devices:", total_unique_times_overmatched)

print("Correctly paired datapoint matches:", total_unique_times_matched)
print("Percentage matched vs total:", float(total_unique_times_matched * 100) / float(total_unique_times), "%")

#pd.set_option("display.max_rows", None, "display.max_columns", None)
# collect lines column 
line_data = matched_unique_records["line"].values.tolist()

def build_line_from_matched_record(matched_record):
    record_1, record_2 = matched_record

    record_1_split = record_1.split("\t")
    len_record_1_split = len(record_1_split)

    record_2_split = record_2.split("\t")
    len_record_2_split = len(record_2_split)

    line_out=None
    #print(len_record_1_split, len_record_2_split)

    ##[{'803261\t14587', '803261\t193\t0\t67\t60'}]

    if len_record_1_split == 2 and len_record_2_split == 5:
        # record 1 is the encoder
        encoder_value = record_1_split[1]

        # record 2 is the adc
        adc_a_value = record_2_split[1]
        adc_b_value = record_2_split[2]
        adc_c_value = record_2_split[3]
        adc_vn_value = record_2_split[4]

        time = record_2_split[0]

        line_out=[time, encoder_value, adc_a_value, adc_b_value, adc_c_value, adc_vn_value]

    elif len_record_1_split == 5 and len_record_2_split == 2:
        # record 1 is the adc
        adc_a_value = record_1_split[1]
        adc_b_value = record_1_split[2]
        adc_c_value = record_1_split[3]
        adc_vn_value = record_1_split[4]
        
        # record 2 is the encoder
        encoder_value = record_2_split[1]

        time = record_2_split[0]

        line_out=[time, encoder_value, adc_a_value, adc_b_value, adc_c_value, adc_vn_value]
    else:
        print(matched_record, record_1_split, record_2_split)
        return None #raise "Something is wrong"
    return "\t".join(line_out)+"\n"


file_out = filename + ".matched.csv"
with open(file_out, "w") as fout:
    for matched_record in line_data:
        combined_line = build_line_from_matched_record(matched_record)
        if (combined_line != None):
            fout.write(combined_line)