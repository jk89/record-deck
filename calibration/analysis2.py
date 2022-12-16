import numpy as np
from scipy.optimize import curve_fit
POT_RESISTANCE=33000

""" Brief: 

When we mount an encoder onto a bldc motor, initally we place this at a random angle.
We need to take voltage measurements over time to calibrate the encoder such that the
angle it reads corresponds to 0 electrical degrees. It currently does not.

By taking time series data of the phase voltages, a common neutral voltage and the 
encoder values over time one can derive this displacement. The procedure is as follows:

We want to optimise via least squares method using a model we provide: the angular_displacement and the 
phase_current_displacement (should ideally be 120 for 3 phase [might not be due to manufacturing issues]),
that is to say we wish to co-optimise these values such that the error from the recorded data away from
model that we defined is minimised. 

Unfotunately with the callibration ADC circuit is not ideal, it does not detect negative voltages and thus
one half of the waveform is missing. The resulting ADC readout is far from sinusoidal, this makes our
modeling task a little more challenging. The adc measurements are periodic however and this works in
our favour as we can model the data via Fourier series and then register our adc datas custom shape
without having to account for the base reasons of why it is not sinusoidal.

Description:

This code fits a model to some recorded data of phase voltages and angular positions, 
and then using that model to calculate the optimal values for the parameters angular_displacement and 
phase_current_displacement.

The model function model takes as input an angular_position and the two parameters angular_displacement
and phase_current_displacement, as well as an arbitrary number of fourier_coefficients. It uses these
coefficients to calculate the phase current for each of the three phases (A, B, and C) using a Fourier
series expansion.

The Fourier series expansion is a way of representing a periodic function as a sum of sinusoidal functions.
In this case, the function being represented is the phase current as a function of the angular
position. The fourier_model function is a simplified version of the model function that does not
have the angular_displacement and phase_current_displacement parameters. It is used to fit a Fourier
series expansion to the recorded phase current data and calculate the optimal values for the fourier_coefficients.

Once the optimal values for the fourier_coefficients have been calculated, they are passed as arguments 
to the model function, which is then fit to the recorded data again to calculate the optimal values for
angular_displacement and phase_current_displacement. The curve_fit function from the scipy.optimize
module is used to fit the model to the data.
"""

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

# load recorded phase voltages and angular positions
phase_a_voltages = [] # load recorded phase A voltages
phase_b_voltages = [] # load recorded phase B voltages
phase_c_voltages = [] # load recorded phase C voltages
virtual_neutral_voltage = [] # load recorded virtual neutral voltage
angular_positions = [] # load recorded angular positions

# calculate phase currents from recorded phase voltages
phase_a_currents = (phase_a_voltages - virtual_neutral_voltage) / POT_RESISTANCE
phase_b_currents = (phase_b_voltages - virtual_neutral_voltage) / POT_RESISTANCE
phase_c_currents = (phase_c_voltages - virtual_neutral_voltage) / POT_RESISTANCE

# fit Fourier series model to data
fourier_params, fourier_cov = curve_fit(fourier_model, angular_positions, (phase_a_currents, phase_b_currents, phase_c_currents))
fourier_coefficients = fourier_params
fourier_errors = np.sqrt(np.diag(fourier_cov))

# fit the model to the data using the calculated Fourier coefficients
params, cov = curve_fit(model, angular_positions,(phase_a_currents, phase_b_currents, phase_c_currents), p0=[0, 0], args=fourier_coefficients)
errors = np.sqrt(np.diag(cov))

# the optimal values for the parameters are the angular_displacement and phase_current_displacement
angular_displacement = params[0]
phase_current_displacement = params[1]

print(f'angular_displacement: {angular_displacement:.2f} +/- {errors[0]:.2f}')
print(f'phase_current_displacement: {phase_current_displacement:.2f} +/- {errors[1]:.2f}') 
