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
print(list(map(lambda x: (x.shape), [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data])))


# define model function
def model(angular_position, angular_displacement, phase_current_displacement, *fourier_coefficients):
    phase_a_current = 0
    phase_b_current = 0
    phase_c_current = 0
    for i, coefficient in enumerate(fourier_coefficients):
        phase_a_current += coefficient * np.sin((i+1) * (angular_position + angular_displacement))
        phase_b_current += coefficient * np.sin((i+1) * (angular_position + angular_displacement + phase_current_displacement))
        phase_c_current += coefficient * np.sin((i+1) * (angular_position + angular_displacement + 2 * phase_current_displacement))
    return phase_a_current, phase_b_current, phase_c_current

# define Fourier series model function
def fourier_model(angular_position, phase_current_displacement, *fourier_coefficients):
    phase_a_current = 0
    phase_b_current = 0
    phase_c_current = 0
    for i, coefficient in enumerate(fourier_coefficients):
        phase_a_current += coefficient * np.sin((i+1) * angular_position)
        phase_b_current += coefficient * np.sin((i+1) * (angular_position + phase_current_displacement))
        phase_c_current += coefficient * np.sin((i+1) * (angular_position + 2 * phase_current_displacement))
    return phase_a_current, phase_b_current, phase_c_current

"""
def f_1(x, p0, p1):
    return p0 + p1*x

def f_2(x, p0, p1, p2):
    return p0 + p1*x + p2*x**2
"""

phase_a_current, phase_b_current, phase_c_current = fourier_model(angle_data, np.asarray([a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]), *[1.0])
print(list(map(lambda x: len(x), [phase_a_current, phase_b_current, phase_c_current])))
print(np.asarray([a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]).shape)
print(angle_data.shape)
print(angle_data.reshape(1,angle_data.shape[0]).shape)

curve_fit(fourier_model, angle_data, np.asarray([a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]))

"""
# fit Fourier series model to data
fourier_params, fourier_cov = curve_fit(fourier_model, angle_data, (a_neg_vn_data, b_neg_vn_data, c_neg_vn_data))
fourier_coefficients = fourier_params
fourier_errors = np.sqrt(np.diag(fourier_cov))

# fit the model to the data using the calculated Fourier coefficients
params, cov = curve_fit(model, angle_data, (a_neg_vn_data, b_neg_vn_data, c_neg_vn_data), p0=[0, 0], args=fourier_coefficients)
errors = np.sqrt(np.diag(cov))

# the optimal values for the parameters are the angular_displacement and phase_current_displacement
angular_displacement = params[0]
phase_current_displacement = params[1]

print(f'angular_displacement: {angular_displacement:.2f} +/- {errors[0]:.2f}')
print(f'phase_current_displacement: {phase_current_displacement:.2f} +/- {errors[1]:.2f}') 
"""
print("TERM")