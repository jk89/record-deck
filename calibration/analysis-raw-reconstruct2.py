from scipy.optimize import curve_fit
import numpy as np
import json
import sys
import matplotlib.pyplot as plt
import utils
# constants
poles = 14
max_iter = 500000
number_of_coefficients = 1

#util
def mmap(lamb, values):
    return list(map(lamb, values))

# get argument run_id
run_ids = sys.argv[1] if len(sys.argv) > 1 else 0 
run_ids = run_ids.split(",")
print("Analysing run:", run_ids)

def determine_direction(run_id):
    if "ccw" in run_id:
        return True
    elif "cw" in run_id:
        return False
    else:
        raise Exception("No idea what direction we are going from the file")

# load file data
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
    cw_data_mapped_to_ccw = mmap(lambda cw_data: (cw_data[0], cw_data[1][0], utils.step_to_rad(cw_data[1][1]), -1.0 * cw_data[1][2], -1.0*cw_data[1][3], -1.0*cw_data[1][4]), cw_data_raw)
    ccw_data_mapped_to_cw = mmap(lambda ccw_data: (ccw_data[0], ccw_data[1][0], utils.step_to_rad(ccw_data[1][1]), -1.0 * ccw_data[1][2], -1.0*ccw_data[1][3], -1.0*ccw_data[1][4]), ccw_data_raw)
    
    # convert raw data encoder values
    cw_data_raw = mmap(lambda cw_data: (cw_data[0], cw_data[1][0], utils.step_to_rad(cw_data[1][1]), cw_data[1][2], cw_data[1][3], cw_data[1][4]), cw_data_raw)
    ccw_data_raw = mmap(lambda ccw_data: (ccw_data[0], ccw_data[1][0], utils.step_to_rad(ccw_data[1][1]), ccw_data[1][2], ccw_data[1][3], ccw_data[1][4]), ccw_data_raw)

    # concat mapped ccw to cw and mapped cw to ccw
    #print("cw_data_mapped_to_ccw angel", cw_data_mapped_to_ccw[0][2])
    #print("cw_data_mapped_to_ccw va", cw_data_mapped_to_ccw[0][3])
    #print("cw_data_mapped_to_ccw vb", cw_data_mapped_to_ccw[0][4])
    #print("cw_data_mapped_to_ccw vc", cw_data_mapped_to_ccw[0][5])

    #print("ccw_data_mapped_to_cw angel", ccw_data_mapped_to_cw[0][2])
    #print("ccw_data_mapped_to_cw va", ccw_data_mapped_to_cw[0][3])
    #print("ccw_data_mapped_to_cw vb", ccw_data_mapped_to_cw[0][4])
    #print("ccw_data_mapped_to_cw vc", ccw_data_mapped_to_cw[0][5])

    def merge_direction(raw, mapped):
        # merge and flatten raw
        angles_bin = np.asarray([], dtype=np.float64)
        anvn_bin = np.asarray([], dtype=np.float64)
        bnvn_bin = np.asarray([], dtype=np.float64)
        cnvn_bin = np.asarray([], dtype=np.float64)
        # 

        for run_id, times, angles, anvns, bnvns, cnvns in raw:
            angles_bin = angles# np.concatenate((angles_bin, angles), axis=0)
            anvn_bin = anvns# np.concatenate((anvn_bin, anvns), axis=0)
            bnvn_bin = bnvns# np.concatenate((bnvn_bin, bnvns), axis=0)
            cnvn_bin = cnvns#np.concatenate((cnvn_bin, cnvns), axis=0)

        #for run_id, times, angles, anvns, bnvns, cnvns in mapped:
        #    angles_bin = np.concatenate((angles_bin, angles), axis=0)
        #    anvn_bin = np.concatenate((anvn_bin, anvns), axis=0)
        #    bnvn_bin = np.concatenate((bnvn_bin, bnvns), axis=0)
        #    cnvn_bin = np.concatenate((cnvn_bin, cnvns), axis=0)

        return (angles_bin, anvn_bin, bnvn_bin, cnvn_bin)
    
    cw_data = merge_direction(cw_data_raw, ccw_data_mapped_to_cw)
    ccw_data = merge_direction(ccw_data_raw, cw_data_mapped_to_ccw)
    return {"cw": cw_data, "ccw": ccw_data}

datahhh = combine_merged_smoothed_datasets(run_ids)
print("datahhh")
print(datahhh)
print(np.min(datahhh["cw"][0]))
print(np.max(datahhh["cw"][0]))
print("00000000000000000")
angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data = datahhh["cw"]
all_file_data = [angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]
# remove -ve voltages as they are skewed badly by lack of -ve adc values
#a_neg_vn_data[a_neg_vn_data<0] = 0
#b_neg_vn_data[b_neg_vn_data<0] = 0
#c_neg_vn_data[c_neg_vn_data<0] = 0

# modify angle_data to be in degrees rather than steps
#encoder_value_to_angle = (2 * np.pi) / 2 ** 14
#angle_data = angle_data * encoder_value_to_angle

def print_metrics(data):
    print("File data metrics:")
    print(list(map(lambda x: len(x), data)))
    print(list(map(lambda x: x[0], data)))
    print(list(map(lambda x: type(x[0]), data)))
    print(list(map(lambda x: (x.shape), data)))
    print("----------------------")

print_metrics(all_file_data)

# ravel data to allow curve fitting
data_to_fit = np.asarray([a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]).ravel()
data_max = np.max(data_to_fit)

print("Data voltages max:", data_max)

# calculate number of electrical cycles per mechanical revolution 
sin_period_coeff = (poles / 2)
print("Calculate number of electrical cycles per mechanical revolution", sin_period_coeff)

######
# Define models:

# define model function
def model(fourier_coefficients):
    def fixed_param_model(angular_position, angular_displacement, phase_current_displacement):
        phase_a_current = np.zeros((1,angular_position.shape[0]))# 0
        phase_b_current = np.zeros((1,angular_position.shape[0]))# 0
        phase_c_current = np.zeros((1,angular_position.shape[0])) # 0
        for i, coefficient in enumerate(fourier_coefficients):
            phase_a_current += coefficient * np.sin((i+1) * sin_period_coeff * (angular_position + angular_displacement))
            phase_b_current += coefficient * np.sin((i+1) * sin_period_coeff * (angular_position + angular_displacement + phase_current_displacement))
            phase_c_current += coefficient * np.sin((i+1) * sin_period_coeff * (angular_position + angular_displacement + (2 * phase_current_displacement)))
        return np.asarray([phase_a_current, phase_b_current, phase_c_current]).ravel()
    return fixed_param_model

# define Fourier series model function
def fourier_model(angular_position, phase_current_displacement, *fourier_coefficients):
    phase_a_current = np.zeros((1,angular_position.shape[0]))# 0# np.zeros((1,angular_position.shape[0]))
    phase_b_current = np.zeros((1,angular_position.shape[0]))# 0
    phase_c_current = np.zeros((1,angular_position.shape[0])) #0
    for i, coefficient in enumerate(fourier_coefficients):
        phase_a_current += coefficient * np.sin((i+1) * sin_period_coeff * angular_position)
        phase_b_current += coefficient * np.sin((i+1) * sin_period_coeff * (angular_position + phase_current_displacement))
        phase_c_current += coefficient * np.sin((i+1) * sin_period_coeff * (angular_position + (2 * phase_current_displacement)))
    return np.asarray([phase_a_current, phase_b_current, phase_c_current]).ravel()

# End models
############

# fit Fourier series model to data
coefficient_default_value = 1 #data_max
initial_fourier_coefficients = tuple([coefficient_default_value for i in range(number_of_coefficients)])

# fit fourier model
print("Fitting fourier model.... please wait...")
fourier_params, fourier_cov = curve_fit(fourier_model, angle_data, data_to_fit, p0=initial_fourier_coefficients, maxfev=max_iter)
fourier_coefficients = fourier_params
fourier_errors = np.sqrt(np.diag(fourier_cov))

# print fourier coeff information
print("Fourier model information:")
print("initial_fourier_coefficients", initial_fourier_coefficients, len(initial_fourier_coefficients))
print("fourier_coefficients", fourier_coefficients)
print("fourier_errors", fourier_errors)
print("----------------------")

def deg_to_rad(deg):
    return deg * np.pi/180

def rad_to_deg(rad):
    return rad * 180/np.pi

# fit the model to the data using the calculated Fourier coefficients
# angular_position, angular_displacement, phase_current_displacement, *fourier_coefficients
print("Fitting final model.... please wait...")
params, cov = curve_fit(model(fourier_coefficients), angle_data, data_to_fit, [0, deg_to_rad(120)], maxfev=max_iter)
errors = np.sqrt(np.diag(cov))

# the optimal values for the parameters are the angular_displacement and phase_current_displacement
angular_displacement = params[0]
phase_current_displacement = params[1]

print("Final model fit information:")
print(f'angular_displacement [degrees]: {rad_to_deg(angular_displacement):.2f} +/- {rad_to_deg(errors[0]):.2f}')
print(f'phase_current_displacement [degrees]: {rad_to_deg(phase_current_displacement):.2f} +/- {rad_to_deg(errors[1]):.2f}') 
print("----------------------")

# generate fitted_model data and force model with 120 seperation

fitted_data = model(fourier_coefficients)(angle_data, angular_displacement, phase_current_displacement)
fitted_data_force_120 = model(fourier_coefficients)(angle_data, angular_displacement, deg_to_rad(120))

# reshape the raveled data to make it plotable
plot_dependant_data = mmap(lambda x: x.reshape(3, angle_data.shape[0]),[fitted_data,data_to_fit])

# plot helpers
def create_voltage_scatter(ax,independant_axis_data,dependant_axis_data):
    mmap(lambda x: ax.scatter(independant_axis_data,dependant_axis_data[x[0]],zorder=1, color=x[1], s=1, label=x[2]),[[0, "red", "a-vn"],[1, "yellow", "b-vn"],[2, "black","c-vn"]])
    ax.legend(loc="center right")
    ax.set_xlim(left=0, right=2*np.pi)
    ax.hlines(y=[0], xmin=[0], xmax=[2*np.pi], colors='purple', linestyles='--', lw=1, label='Multiple Lines')

def plot_data(title,independant_axis_data,plot_independant_axes_data):
    fig, ax = plt.subplots(nrows=len(plot_independant_axes_data), ncols=1, figsize=(60, 5))
    fig.suptitle(title)
    mmap(lambda i: create_voltage_scatter(ax[i],independant_axis_data,plot_independant_axes_data[i]),[i for i in range(len(ax))])
    return fig

# create plots
print("Creating plot.... please wait...")
plot_title = 'Fit parameters:\n angular_disp=%.2f±%.1f phase_current_disp=%.2f±%.1f' % (rad_to_deg(angular_displacement), rad_to_deg(errors[0]), rad_to_deg(phase_current_displacement), rad_to_deg(errors[1]))
fig = plot_data(plot_title, angle_data, plot_dependant_data)

# save plot as file
print("Saving plot.... please wait...")
fout='%s_Fourier_pos_voltage_fit2.png' % ("ssadsdsasd")
print(fout)
fig.savefig(fout, pad_inches=0, bbox_inches='tight')

#plt.show()
print("Done :)")