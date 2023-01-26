from scipy.optimize import curve_fit
import numpy as np
import json
import sys
import matplotlib.pyplot as plt
import analyse
import utils
import models
import plots
poles = 14
max_iter = 500000
run_ids = sys.argv[1] if len(sys.argv) > 1 else 0 
run_ids = run_ids.split(",")
print("Analysing runs:", run_ids)

combined_data = utils.combine_merged_smoothed_datasets(run_ids)

# test run_ids
print("combined_data")
print(combined_data)

for key in combined_data.keys():
    print(key, len(combined_data[key][0]), len(combined_data[key][1]), len(combined_data[key][2]), len(combined_data[key][3]))

model = models.get_sin_model(poles)

data_to_fit_cw = combined_data["cw"] #0 angle 1 a 2 b 3 c
data_to_fit_ccw = combined_data["ccw"] #0 angle 1 a 2 b 3 c

print("data_to_fit_cw", data_to_fit_cw)
print("cw_0_min", np.min(data_to_fit_cw[0]))
print("cw_0_max", np.max(data_to_fit_cw[0]))
print("cw_1_min", np.min(data_to_fit_cw[1]))
print("cw_1_max", np.max(data_to_fit_cw[1]))
print("cw_2_min", np.min(data_to_fit_cw[2]))
print("cw_2_max", np.max(data_to_fit_cw[2]))
print("cw_3_min", np.min(data_to_fit_cw[3]))
print("cw_3_max", np.max(data_to_fit_cw[3]))
print("================================")

print("data_to_fit_ccw", data_to_fit_ccw)
print("ccw_0_min", np.min(data_to_fit_ccw[0]))
print("ccw_0_max", np.max(data_to_fit_ccw[0]))
print("ccw_1_min", np.min(data_to_fit_ccw[1]))
print("ccw_1_max", np.max(data_to_fit_ccw[1]))
print("ccw_2_min", np.min(data_to_fit_ccw[2]))
print("ccw_2_max", np.max(data_to_fit_ccw[2]))
print("ccw_3_min", np.min(data_to_fit_ccw[3]))
print("ccw_3_max", np.max(data_to_fit_ccw[3]))
print("================================")

#a_neg_vn_data[a_neg_vn_data<0] = 0
data_to_fit_cw[1][data_to_fit_cw[1] < 0] = 0
data_to_fit_cw[2][data_to_fit_cw[2] < 0] = 0
data_to_fit_cw[3][data_to_fit_cw[3] < 0] = 0

data_to_fit_ccw[1][data_to_fit_ccw[1] < 0] = 0
data_to_fit_ccw[2][data_to_fit_ccw[2] < 0] = 0
data_to_fit_ccw[3][data_to_fit_ccw[3] < 0] = 0

print("Fitting cw model")
cw_voltage_data = np.asarray([data_to_fit_cw[1], data_to_fit_cw[2], data_to_fit_cw[3]]).ravel()
params_cw, cov_cw = curve_fit(model, xdata=data_to_fit_cw[0], ydata=cw_voltage_data, p0=[0, utils.deg_to_rad(240)], maxfev=max_iter)
errors_cw = np.sqrt(np.diag(cov_cw))
angular_displacement_cw = params_cw[0]
phase_current_displacement_cw = params_cw[1]

print("Fitting ccw model")
ccw_voltage_data = np.asarray([data_to_fit_ccw[1], data_to_fit_ccw[2], data_to_fit_ccw[3]]).ravel()
params_ccw, cov_ccw = curve_fit(model, xdata=data_to_fit_ccw[0], ydata=ccw_voltage_data, p0=[0, utils.deg_to_rad(240)], maxfev=max_iter)
errors_ccw = np.sqrt(np.diag(cov_ccw))
angular_displacement_ccw = params_ccw[0]
phase_current_displacement_ccw = params_ccw[1]


print("Final model fit information:")

print(f'angular_displacement_cw [rads]: {(angular_displacement_cw):.2f} +/- {(errors_cw[0]):.2f}')
print(f'phase_current_displacement_cw [rads]: {(phase_current_displacement_cw):.2f} +/- {(errors_cw[1]):.2f}')
print(f'angular_displacement_cw [degrees]: {utils.rad_to_deg(angular_displacement_cw):.2f} +/- {utils.rad_to_deg(errors_cw[0]):.2f}')
print(f'phase_current_displacement_cw [degrees]: {utils.rad_to_deg(phase_current_displacement_cw):.2f} +/- {utils.rad_to_deg(errors_cw[1]):.2f}') 
print(f'angular_displacement_cw [steps]: {utils.rad_to_step(angular_displacement_cw):.2f} +/- {utils.rad_to_step(errors_cw[0]):.2f}')
print(f'phase_current_displacement_cw [steps]: {utils.rad_to_step(phase_current_displacement_cw):.2f} +/- {utils.rad_to_step(errors_cw[1]):.2f}') 
print("-----------------------")
print(f'angular_displacement_ccw [rads]: {(angular_displacement_ccw):.2f} +/- {(errors_ccw[0]):.2f}')
print(f'phase_current_displacement_ccw [rads]: {(phase_current_displacement_ccw):.2f} +/- {(errors_ccw[1]):.2f}')
print(f'angular_displacement_ccw [degrees]: {utils.rad_to_deg(angular_displacement_ccw):.2f} +/- {utils.rad_to_deg(errors_ccw[0]):.2f}')
print(f'phase_current_displacement_ccw [degrees]: {utils.rad_to_deg(phase_current_displacement_ccw):.2f} +/- {utils.rad_to_deg(errors_ccw[1]):.2f}') 
print(f'angular_displacement_ccw [steps]: {utils.rad_to_step(angular_displacement_ccw):.2f} +/- {utils.rad_to_step(errors_ccw[0]):.2f}')
print(f'phase_current_displacement_ccw [steps]: {utils.rad_to_step(phase_current_displacement_ccw):.2f} +/- {utils.rad_to_step(errors_ccw[1]):.2f}') 


# now simulate the model

print("Applying cw model")
fitted_data_cw = model(data_to_fit_cw[0], angular_displacement_cw, phase_current_displacement_cw)
print("Applying ccw model")
fitted_data_ccw = model(data_to_fit_ccw[0], angular_displacement_ccw, phase_current_displacement_ccw)


print("Creating plot.... please wait...")
plot_title = 'Fit parameters:\n cw angular_disp=%.2f±%.1f phase_current_disp=%.2f±%.1f\n' % (utils.rad_to_deg(angular_displacement_cw), utils.rad_to_deg(errors_cw[0]), utils.rad_to_deg(phase_current_displacement_cw), utils.rad_to_deg(errors_cw[1]))
plot_title += 'ccw angular_disp=%.2f±%.1f phase_current_disp=%.2f±%.1f' % (utils.rad_to_deg(angular_displacement_ccw), utils.rad_to_deg(errors_ccw[0]), utils.rad_to_deg(phase_current_displacement_ccw), utils.rad_to_deg(errors_ccw[1]))

fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(60, 5))
fig.suptitle(plot_title,fontsize=8)

# .reshape(3, data_to_fit_cw[0].shape[0])
plots.create_voltage_scatter(ax[0], data_to_fit_cw[0], cw_voltage_data.reshape(3, data_to_fit_cw[0].shape[0]))
plots.create_voltage_scatter(ax[1], data_to_fit_cw[0], fitted_data_cw.reshape(3, data_to_fit_cw[0].shape[0]))

plots.create_voltage_scatter(ax[2], data_to_fit_ccw[0], ccw_voltage_data.reshape(3, data_to_fit_ccw[0].shape[0]))
plots.create_voltage_scatter(ax[3], data_to_fit_ccw[0], fitted_data_ccw.reshape(3, data_to_fit_ccw[0].shape[0]))

#create_voltage_scatter(ax[0],partial_angle_data,data_to_fit_cw.reshape(3, partial_angle_data.shape[0])) 
#create_voltage_scatter(ax[1],angle_data,fitted_data_cw.reshape(3, angle_data.shape[0])) 

#create_voltage_scatter(ax[2],partial_angle_data,data_to_fit_ccw.reshape(3, partial_angle_data.shape[0])) 
#create_voltage_scatter(ax[3],angle_data,fitted_data_ccw.reshape(3, angle_data.shape[0])) 


# save plot as file
print("Saving plot.... please wait...")
fout='datasets/data/calibration-data/tester_simplemodel_voltage_fit.png'# % (combined_zc_map_id)
print(fout)
fig.savefig(fout, pad_inches=0, bbox_inches='tight')

#plt.show()
print("Done :)")


print("data_to_fit_cw", data_to_fit_cw)
print("cw_0_min", np.min(data_to_fit_cw[0]))
print("cw_0_max", np.max(data_to_fit_cw[0]))
print("cw_1_min", np.min(data_to_fit_cw[1]))
print("cw_1_max", np.max(data_to_fit_cw[1]))
print("cw_2_min", np.min(data_to_fit_cw[2]))
print("cw_2_max", np.max(data_to_fit_cw[2]))
print("cw_3_min", np.min(data_to_fit_cw[3]))
print("cw_3_max", np.max(data_to_fit_cw[3]))
print("================================")

print("data_to_fit_ccw", data_to_fit_ccw)
print("ccw_0_min", np.min(data_to_fit_ccw[0]))
print("ccw_0_max", np.max(data_to_fit_ccw[0]))
print("ccw_1_min", np.min(data_to_fit_ccw[1]))
print("ccw_1_max", np.max(data_to_fit_ccw[1]))
print("ccw_2_min", np.min(data_to_fit_ccw[2]))
print("ccw_2_max", np.max(data_to_fit_ccw[2]))
print("ccw_3_min", np.min(data_to_fit_ccw[3]))
print("ccw_3_max", np.max(data_to_fit_ccw[3]))
print("================================")