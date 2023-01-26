import numpy as np
import json

def mmap(lamb, values):
    return list(map(lamb, values))

def get_smoothed_voltage_data(run_id):
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
    return list(map(lambda x:np.asarray(x), [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]))

def determine_direction(run_id):
    if "ccw" in run_id:
        return True
    elif "cw" in run_id:
        return False
    else:
        raise Exception("No idea what direction we are going from the file: " + run_id)

def deg_to_rad(deg):
    return deg * np.pi/180

def rad_to_deg(rad):
    return rad * 180/np.pi

def rad_to_step(rad):
    return (2 ** 14 / (2 * np.pi)) * rad

def step_to_rad(step):
    return ((2 * np.pi) / 2 ** 14) * step

def step_to_deg(step):
    return ((360)/2**14) * step

def deg_to_step(deg):
    return ((2**14)/360) * deg

def combine_merged_smoothed_datasets(run_ids):
    print("run_ids", run_ids)
    cw_run_ids=list(filter(lambda run_id: determine_direction(run_id) == False, run_ids))
    ccw_run_ids=list(filter(lambda run_id: determine_direction(run_id) == True, run_ids))
    #if (len(cw_run_ids) != len(ccw_run_ids)):
    #    raise "Need to have the same number of cw and ccw runs"
    # retrieve data from both datasets
    cw_data_raw = mmap(lambda run_id: (run_id, get_smoothed_voltage_data(run_id)), cw_run_ids)
    ccw_data_raw = mmap(lambda run_id: (run_id, get_smoothed_voltage_data(run_id)), ccw_run_ids)
    # map cw to ccw and ccw to cw
    # each looks like ..... (run_id,[time,angle, anvn, bnvn, cnvn])
    cw_data_mapped_to_ccw = mmap(lambda cw_data: (cw_data[0], cw_data[1][0], step_to_rad(cw_data[1][1]), -1.0 * cw_data[1][2], -1.0*cw_data[1][3], -1.0*cw_data[1][4]), cw_data_raw)
    ccw_data_mapped_to_cw = mmap(lambda ccw_data: (ccw_data[0], ccw_data[1][0], step_to_rad(ccw_data[1][1]), -1.0 * ccw_data[1][2], -1.0*ccw_data[1][3], -1.0*ccw_data[1][4]), ccw_data_raw)
    
    # convert raw data encoder values
    cw_data_raw = mmap(lambda cw_data: (cw_data[0], cw_data[1][0], step_to_rad(cw_data[1][1]), cw_data[1][2], cw_data[1][3], cw_data[1][4]), cw_data_raw)
    ccw_data_raw = mmap(lambda ccw_data: (ccw_data[0], ccw_data[1][0], step_to_rad(ccw_data[1][1]), ccw_data[1][2], ccw_data[1][3], ccw_data[1][4]), ccw_data_raw)

    # concat mapped ccw to cw and mapped cw to ccw
    #print("cw_data_mapped_to_ccw angel", cw_data_mapped_to_ccw[0][2])
    #print("cw_data_mapped_to_ccw va", cw_data_mapped_to_ccw[0][3])
    #print("cw_data_mapped_to_ccw vb", cw_data_mapped_to_ccw[0][4])
    #print("cw_data_mapped_to_ccw vc", cw_data_mapped_to_ccw[0][5])

    #print("ccw_data_mapped_to_cw angel", ccw_data_mapped_to_cw[0][2])
    #print("ccw_data_mapped_to_cw va", ccw_data_mapped_to_cw[0][3])
    #print("ccw_data_mapped_to_cw vb", ccw_data_mapped_to_cw[0][4])
    #print("ccw_data_mapped_to_cw vc", ccw_data_mapped_to_cw[0][5])

    def mute_neg_voltages(merged_direction, run_direction, a, b, c):
        if merged_direction == False:
            if run_direction == True:
                pass #cw loose -ve voltages
                a[a>0]=0
                b[b>0]=0
                c[c>0]=0
            elif run_direction == False:
                pass #ccw loose +ve voltages
                a[a<0]=0
                b[b<0]=0
                c[c<0]=0
        elif merged_direction == True:
            if run_direction == True:
                pass #cw loose -ve voltages
                a[a<0]=0
                b[b<0]=0
                c[c<0]=0
            elif run_direction == False:
                pass #ccw loose +ve voltages
                a[a>0]=0
                b[b>0]=0
                c[c>0]=0
        return (a, b, c)

    def merge_direction(merge_direction, raw, mapped):
        merge_direction = determine_direction(merge_direction) #False is cw True is ccw
        # merge and flatten raw
        angles_bin = np.asarray([], dtype=np.float64)
        anvn_bin = np.asarray([], dtype=np.float64)
        bnvn_bin = np.asarray([], dtype=np.float64)
        cnvn_bin = np.asarray([], dtype=np.float64)
        # 

        for run_id, times, angles, anvns, bnvns, cnvns in raw:
            run_direction = determine_direction(run_id) #False is cw True is ccw
            (anvns, bnvns, cnvns) = mute_neg_voltages(merge_direction, run_direction, anvns, bnvns, cnvns)
            angles_bin = np.concatenate((angles_bin, angles), axis=0)
            anvn_bin = np.concatenate((anvn_bin, anvns), axis=0)
            bnvn_bin = np.concatenate((bnvn_bin, bnvns), axis=0)
            cnvn_bin = np.concatenate((cnvn_bin, cnvns), axis=0)

        for run_id, times, angles, anvns, bnvns, cnvns in mapped:
            run_direction = determine_direction(run_id) #False is cw True is ccw
            (anvns, bnvns, cnvns) = mute_neg_voltages(merge_direction, run_direction, anvns, bnvns, cnvns)
            angles_bin = np.concatenate((angles_bin, angles), axis=0)
            anvn_bin = np.concatenate((anvn_bin, anvns), axis=0)
            bnvn_bin = np.concatenate((bnvn_bin, bnvns), axis=0)
            cnvn_bin = np.concatenate((cnvn_bin, cnvns), axis=0)

        return (angles_bin, anvn_bin, bnvn_bin, cnvn_bin)
    
    cw_data = merge_direction("cw", cw_data_raw, ccw_data_mapped_to_cw)
    ccw_data = merge_direction("ccw", ccw_data_raw, cw_data_mapped_to_ccw)
    return {"cw": cw_data, "ccw": ccw_data}
"""
data_to_fit_cw[1][data_to_fit_cw[1] < 0] = 0
data_to_fit_cw[2][data_to_fit_cw[2] < 0] = 0
data_to_fit_cw[3][data_to_fit_cw[3] < 0] = 0

data_to_fit_ccw[1][data_to_fit_ccw[1] < 0] = 0
data_to_fit_ccw[2][data_to_fit_ccw[2] < 0] = 0
data_to_fit_ccw[3][data_to_fit_ccw[3] < 0] = 0
"""