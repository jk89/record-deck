from scipy.optimize import curve_fit
import numpy as np
import json
import sys
import matplotlib.pyplot as plt
import analyse

# constants
poles = 14
max_iter = 500000
number_of_coefficients = 1

combined_zc_map_id = sys.argv[1] if len(sys.argv) > 1 else 0
file_in_json_location = 'datasets/data/calibration-data/zc_map_%s.json' % (combined_zc_map_id)
# ymhflwqnmomcaameuhzc


zc_map = None
with open(file_in_json_location, "r") as fin:
    zc_map_str = "\n".join(fin.readlines())
    zc_map = json.loads(zc_map_str)

#print("zc_map", zc_map)

reformed_zc = analyse.mean_and_std_to_rising_falling(zc_map["mean"], zc_map["std"])

#print("reformed_zc", reformed_zc)

angles = np.asarray(reformed_zc["channel_data"]["angles"], dtype=np.float64)
channel_data_a = np.asarray(reformed_zc["channel_data"]["a"], dtype=np.float64)
channel_data_b = np.asarray(reformed_zc["channel_data"]["b"], dtype=np.float64)
channel_data_c = np.asarray(reformed_zc["channel_data"]["c"], dtype=np.float64)
encoder_value_to_angle = (2 * np.pi) / 2 ** 14
rad_angle_to_encoder_value = 2 ** 14 / (2 * np.pi)
channel_error_a = np.asarray(reformed_zc["channel_error"]["a"], dtype=np.float64)
channel_error_b = np.asarray(reformed_zc["channel_error"]["b"], dtype=np.float64)
channel_error_c = np.asarray(reformed_zc["channel_error"]["c"], dtype=np.float64)

partial_sin_wave = analyse.mean_and_std_to_partial_sin_wave(zc_map["mean"])
angle_data = angles * encoder_value_to_angle
partial_angle_data = np.asarray(partial_sin_wave["data"]["angles"]) * encoder_value_to_angle

print("00000000000000000000000000000000000")
print("partial_sin_wave", partial_sin_wave)
print("00000000000000000000000000000000000")

sin_period_coeff = (poles / 2)

def model(angular_position, angular_displacement_cw, phase_current_displacement_cw):
    coefficient=1.0
    phase_a_current = np.zeros((1,angular_position.shape[0]))# 0
    phase_b_current = np.zeros((1,angular_position.shape[0]))# 0
    phase_c_current = np.zeros((1,angular_position.shape[0])) # 0
    phase_a_current += coefficient * np.sin(sin_period_coeff * (angular_position + angular_displacement_cw))
    phase_b_current += coefficient * np.sin(sin_period_coeff * (angular_position + angular_displacement_cw + phase_current_displacement_cw))
    phase_c_current += coefficient * np.sin(sin_period_coeff * (angular_position + angular_displacement_cw + (2 * phase_current_displacement_cw)))
    return np.asarray([phase_a_current, phase_b_current, phase_c_current]).ravel()

data_to_fit_cw = np.asarray([partial_sin_wave["data"]["a"], partial_sin_wave["data"]["b"], partial_sin_wave["data"]["c"]]).ravel()
data_to_fit_ccw = -1.0 * np.asarray([partial_sin_wave["data"]["a"], partial_sin_wave["data"]["b"], partial_sin_wave["data"]["c"]]).ravel()

data_error_to_fit = np.asarray([partial_sin_wave["error"]["a"], partial_sin_wave["error"]["b"], partial_sin_wave["error"]["c"]]).ravel()

def deg_to_rad(deg):
    return deg * np.pi/180

def rad_to_deg(rad):
    return rad * 180/np.pi

def rad_to_step(rad):
    return rad_angle_to_encoder_value * rad

# fit the model to the data using the calculated Fourier coefficients
# angular_position, angular_displacement_cw, phase_current_displacement_cw, *fourier_coefficients

sigmaaaa= 1./(data_error_to_fit*data_error_to_fit)
print("sigmaaaa done", json.dumps(list(sigmaaaa)))

print("Fitting final cw model.... please wait...")


params_cw, cov_cw = curve_fit(model, xdata=partial_angle_data, ydata=data_to_fit_cw, p0=[0, deg_to_rad(240)], sigma=sigmaaaa, maxfev=max_iter)
errors_cw = np.sqrt(np.diag(cov_cw))
angular_displacement_cw = params_cw[0]
phase_current_displacement_cw = params_cw[1]


params_ccw, cov_ccw = curve_fit(model, xdata=partial_angle_data, ydata=data_to_fit_ccw, p0=[0, deg_to_rad(240)], sigma=sigmaaaa, maxfev=max_iter)
errors_ccw = np.sqrt(np.diag(cov_ccw))
angular_displacement_ccw = params_ccw[0]
phase_current_displacement_ccw = params_ccw[1]

print("Final model fit information:")

print(f'angular_displacement_cw [rads]: {(angular_displacement_cw):.2f} +/- {(errors_cw[0]):.2f}')
print(f'phase_current_displacement_cw [rads]: {(phase_current_displacement_cw):.2f} +/- {(errors_cw[1]):.2f}')
print(f'angular_displacement_cw [degrees]: {rad_to_deg(angular_displacement_cw):.2f} +/- {rad_to_deg(errors_cw[0]):.2f}')
print(f'phase_current_displacement_cw [degrees]: {rad_to_deg(phase_current_displacement_cw):.2f} +/- {rad_to_deg(errors_cw[1]):.2f}') 
print(f'angular_displacement_cw [steps]: {rad_to_step(angular_displacement_cw):.2f} +/- {rad_to_step(errors_cw[0]):.2f}')
print(f'phase_current_displacement_cw [steps]: {rad_to_step(phase_current_displacement_cw):.2f} +/- {rad_to_step(errors_cw[1]):.2f}') 
print("-----------------------")
print(f'angular_displacement_ccw [rads]: {(angular_displacement_ccw):.2f} +/- {(errors_ccw[0]):.2f}')
print(f'phase_current_displacement_ccw [rads]: {(phase_current_displacement_ccw):.2f} +/- {(errors_ccw[1]):.2f}')
print(f'angular_displacement_ccw [degrees]: {rad_to_deg(angular_displacement_ccw):.2f} +/- {rad_to_deg(errors_ccw[0]):.2f}')
print(f'phase_current_displacement_ccw [degrees]: {rad_to_deg(phase_current_displacement_ccw):.2f} +/- {rad_to_deg(errors_ccw[1]):.2f}') 
print(f'angular_displacement_ccw [steps]: {rad_to_step(angular_displacement_ccw):.2f} +/- {rad_to_step(errors_ccw[0]):.2f}')
print(f'phase_current_displacement_ccw [steps]: {rad_to_step(phase_current_displacement_ccw):.2f} +/- {rad_to_step(errors_ccw[1]):.2f}') 


print("----------------------")

def mmap(lamb, values):
    return list(map(lamb, values))

def create_voltage_scatter(ax,independant_axis_data,dependant_axis_data):
    mmap(lambda x: ax.scatter(independant_axis_data,dependant_axis_data[x[0]],zorder=1, color=x[1], s=1, label=x[2]),[[0, "red", "a-vn"],[1, "orange", "b-vn"],[2, "black","c-vn"]])
    ax.legend(loc="center right")
    ax.set_xlim(left=0, right=2*np.pi)
    ax.hlines(y=[0], xmin=[0], xmax=[2*np.pi], colors='purple', linestyles='--', lw=1, label='Multiple Lines')



fitted_data_cw = model(angle_data, angular_displacement_cw, phase_current_displacement_cw)
fitted_data_ccw = model(angle_data, angular_displacement_ccw, phase_current_displacement_ccw)

# reshape the raveled data to make it plotable
#plot_dependant_data = mmap(lambda x: x.reshape(3, partial_angle_data.shape[0]),[fitted_data_cw,data_to_fit_cw])

# plot_dependant_data

print("Creating plot.... please wait...")
plot_title = 'Fit parameters:\n cw angular_disp=%.2f±%.1f phase_current_disp=%.2f±%.1f\n' % (rad_to_deg(angular_displacement_cw), rad_to_deg(errors_cw[0]), rad_to_deg(phase_current_displacement_cw), rad_to_deg(errors_cw[1]))
plot_title += 'ccw angular_disp=%.2f±%.1f phase_current_disp=%.2f±%.1f' % (rad_to_deg(angular_displacement_ccw), rad_to_deg(errors_ccw[0]), rad_to_deg(phase_current_displacement_ccw), rad_to_deg(errors_ccw[1]))

fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(60, 5))
fig.suptitle(plot_title,fontsize=8)


create_voltage_scatter(ax[0],partial_angle_data,data_to_fit_cw.reshape(3, partial_angle_data.shape[0])) 
create_voltage_scatter(ax[1],angle_data,fitted_data_cw.reshape(3, angle_data.shape[0])) 

create_voltage_scatter(ax[2],partial_angle_data,data_to_fit_ccw.reshape(3, partial_angle_data.shape[0])) 
create_voltage_scatter(ax[3],angle_data,fitted_data_ccw.reshape(3, angle_data.shape[0])) 


# save plot as file
print("Saving plot.... please wait...")
fout='datasets/data/calibration-data/%s_Fourier_pos_voltage_fit2.png' % (combined_zc_map_id)
print(fout)
fig.savefig(fout, pad_inches=0, bbox_inches='tight')

#plt.show()
print("Done :)")


import matplotlib.colors as mcolors

print(list(mcolors.BASE_COLORS.values()))