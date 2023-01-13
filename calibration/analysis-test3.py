from scipy.optimize import curve_fit
import numpy as np
import json
import sys
import matplotlib.pyplot as plt

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

# modify angle_data to be in degrees
encoder_value_to_angle = 360 / 2 ** 14
angle_data = angle_data * encoder_value_to_angle

print(list(map(lambda x: len(x), [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data])))
print(list(map(lambda x: x[0], [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data])))
print(list(map(lambda x: type(x[0]), [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data])))
print(list(map(lambda x: (x.shape), [time_data, angle_data, a_neg_vn_data, b_neg_vn_data, c_neg_vn_data])))


# define model function
def model(fourier_coefficients):
    def fixed_param_model(angular_position, angular_displacement, phase_current_displacement):
        phase_a_current = np.zeros((1,angular_position.shape[0]))# 0
        phase_b_current = np.zeros((1,angular_position.shape[0]))# 0
        phase_c_current = np.zeros((1,angular_position.shape[0])) # 0
        for i, coefficient in enumerate(fourier_coefficients):
            phase_a_current += coefficient * np.sin((i+1) * (angular_position + angular_displacement))
            phase_b_current += coefficient * np.sin((i+1) * (angular_position + angular_displacement + phase_current_displacement))
            phase_c_current += coefficient * np.sin((i+1) * (angular_position + angular_displacement + 2 * phase_current_displacement))
        return np.asarray([phase_a_current, phase_b_current, phase_c_current]).ravel()
    return fixed_param_model

def helper_model():
    pass

# define Fourier series model function
def fourier_model(angular_position, phase_current_displacement, *fourier_coefficients):
    phase_a_current = np.zeros((1,angular_position.shape[0]))# 0# np.zeros((1,angular_position.shape[0]))
    phase_b_current = np.zeros((1,angular_position.shape[0]))# 0
    phase_c_current = np.zeros((1,angular_position.shape[0])) #0
    for i, coefficient in enumerate(fourier_coefficients):
        phase_a_current += coefficient * np.sin((i+1) * angular_position)
        phase_b_current += coefficient * np.sin((i+1) * (angular_position + phase_current_displacement))
        phase_c_current += coefficient * np.sin((i+1) * (angular_position + 2 * phase_current_displacement))
    return np.asarray([phase_a_current, phase_b_current, phase_c_current]).ravel()

"""
def f_1(x, p0, p1):
    return p0 + p1*x

def f_2(x, p0, p1, p2):
    return p0 + p1*x + p2*x**2
"""

#phase_a_current, phase_b_current, phase_c_current = fourier_model(angle_data, np.asarray([a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]), *[1.0])
#print(list(map(lambda x: len(x), [phase_a_current, phase_b_current, phase_c_current])))
#print(np.asarray([a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]).shape)
#print(angle_data.shape)
#print(angle_data.reshape(1,angle_data.shape[0]).shape)
data_to_fit = np.asarray([a_neg_vn_data, b_neg_vn_data, c_neg_vn_data]).ravel()

# fit Fourier series model to data
number_of_coefficients = 10
coefficient_default_value = 0
initial_fourier_coefficients = tuple([coefficient_default_value for i in range(number_of_coefficients)]) #(0,0,0,0,0,0,0,0,0,0)
print("initial_fourier_coefficients", initial_fourier_coefficients, len(initial_fourier_coefficients))
fourier_params, fourier_cov = curve_fit(fourier_model, angle_data, data_to_fit, p0=initial_fourier_coefficients)
fourier_coefficients = fourier_params
fourier_errors = np.sqrt(np.diag(fourier_cov))

print("fourier_coefficients", fourier_coefficients)
print("fourier_errors", fourier_errors)

# fit the model to the data using the calculated Fourier coefficients
# angular_position, angular_displacement, phase_current_displacement, *fourier_coefficients
def deg_to_rad(deg):
    return deg * np.pi/180

def rad_to_deg(rad):
    return rad * 180/np.pi


params, cov = curve_fit(model(fourier_coefficients), angle_data, data_to_fit, [0, deg_to_rad(120)])
errors = np.sqrt(np.diag(cov))

# the optimal values for the parameters are the angular_displacement and phase_current_displacement
angular_displacement = params[0]
phase_current_displacement = params[1]


print(f'angular_displacement: {angular_displacement:.2f} +/- {errors[0]:.2f}')
print(f'phase_current_displacement: {phase_current_displacement:.2f} +/- {errors[1]:.2f}') 

print(f'phase_current_displacement: {rad_to_deg(phase_current_displacement):.2f} +/- {rad_to_deg(errors[1]):.2f}') 

# angle_data [multi]
# angular_displacement [fixed]
# phase_current_displacement [fixed]
# fourier_coeff [fixed]
# data_to_fit [multi]
# fitted_data
fitted_data = model(fourier_coefficients)(angle_data, angular_displacement, phase_current_displacement)
# print this data
# scatter for data_to_fit
# line for fitted_data



print("hereeer")

reshaped_fitted_data = fitted_data.reshape(3, angle_data.shape[0])
reshaped_data_to_fit = data_to_fit.reshape(3, angle_data.shape[0])

fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(60, 5))

#ax.suptitle('Fit parameters:\n angular_disp=%.2e phase_current_disp=%.2e' % (angular_displacement, phase_current_displacement))

ax[0].plot(angle_data,reshaped_fitted_data[0],zorder=1, color="red") # line label=""
ax[1].scatter(angle_data,reshaped_data_to_fit[0],zorder=2, color="red", s=1) # scatter

ax[0].plot(angle_data,reshaped_fitted_data[1],zorder=3, color="yellow") # line
ax[1].scatter(angle_data,reshaped_data_to_fit[1],zorder=4, color="yellow", s=1) # scatter

ax[0].plot(angle_data,reshaped_fitted_data[2],zorder=5, color="black") # line
ax[1].scatter(angle_data,reshaped_data_to_fit[2],zorder=6, color="black", s=1) # scatter

fig.savefig('Fourier_voltage_fit.png')
#f2.savefig('Fourier_voltage_fit_raw_data.png')

#plt.show()

print("TERM")