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

print("zc_map", zc_map)

reformed_zc = analyse.mean_and_std_to_rising_falling(zc_map["mean"], zc_map["std"])

print("reformed_zc", reformed_zc)

angles = np.asarray(reformed_zc["channel_data"]["angles"], dtype=np.float64)
channel_data_a = np.asarray(reformed_zc["channel_data"]["a"], dtype=np.float64)
channel_data_b = np.asarray(reformed_zc["channel_data"]["b"], dtype=np.float64)
channel_data_c = np.asarray(reformed_zc["channel_data"]["c"], dtype=np.float64)
encoder_value_to_angle = (2 * np.pi) / 2 ** 14
rad_angle_to_encoder_value = 2 ** 14 / (2 * np.pi)
angle_data = angles * encoder_value_to_angle
channel_error_a = np.asarray(reformed_zc["channel_error"]["a"], dtype=np.float64)
channel_error_b = np.asarray(reformed_zc["channel_error"]["b"], dtype=np.float64)
channel_error_c = np.asarray(reformed_zc["channel_error"]["c"], dtype=np.float64)

print(channel_data_a)
print(channel_error_a)

sin_period_coeff = (poles / 2)

def model(angular_position, coefficient, angular_displacement, phase_current_displacement):
    phase_a_current = np.zeros((1,angular_position.shape[0]))# 0
    phase_b_current = np.zeros((1,angular_position.shape[0]))# 0
    phase_c_current = np.zeros((1,angular_position.shape[0])) # 0
    phase_a_current += coefficient * np.sin(sin_period_coeff * (angular_position + angular_displacement))
    phase_b_current += coefficient * np.sin(sin_period_coeff * (angular_position + angular_displacement + phase_current_displacement))
    phase_c_current += coefficient * np.sin(sin_period_coeff * (angular_position + angular_displacement + (2 * phase_current_displacement)))
    return np.asarray([phase_a_current, phase_b_current, phase_c_current]).ravel()

data_to_fit = np.asarray([channel_data_a, channel_data_b, channel_data_c]).ravel()
data_error_to_fit = np.asarray([channel_error_a, channel_error_b, channel_error_a]).ravel()

def deg_to_rad(deg):
    return deg * np.pi/180

def rad_to_deg(rad):
    return rad * 180/np.pi

def rad_to_step(rad):
    return rad_angle_to_encoder_value * rad

# fit the model to the data using the calculated Fourier coefficients
# angular_position, angular_displacement, phase_current_displacement, *fourier_coefficients
print("Fitting final model.... please wait...")

sigmaaaa= 1./(data_error_to_fit*data_error_to_fit)
print("sigmaaaa done", json.dumps(list(sigmaaaa)))
params, cov = curve_fit(model, xdata=angle_data, ydata=data_to_fit, sigma=sigmaaaa, p0=[1, 0, deg_to_rad(120)], maxfev=max_iter)
errors = np.sqrt(np.diag(cov))

coefficient = params[0]
angular_displacement = params[1]
phase_current_displacement = params[2]

print("Final model fit information:")
print(f'coefficient [degrees]: {coefficient:.2f} +/- {rad_to_deg(errors[0]):.2f}')
print(f'angular_displacement [degrees]: {rad_to_deg(angular_displacement):.2f} +/- {rad_to_deg(errors[1]):.2f}')
print(f'phase_current_displacement [degrees]: {rad_to_deg(phase_current_displacement):.2f} +/- {rad_to_deg(errors[2]):.2f}') 

print(f'angular_displacement [steps]: {rad_to_step(angular_displacement):.2f} +/- {rad_to_step(errors[1]):.2f}')
print(f'phase_current_displacement [steps]: {rad_to_step(phase_current_displacement):.2f} +/- {rad_to_step(errors[2]):.2f}') 

print("----------------------")
