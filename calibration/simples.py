import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


"""
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def func(x, a0, a1):
    return a0 + a1 * x

x, y = np.arange(10), np.arange(10) + np.random.randn(10)/10
popt, pcov = curve_fit(func, x, y, p0=(1, 1))

# Plot the results
plt.title('Fit parameters:\n a0=%.2e a1=%.2e' % (popt[0], popt[1]))
# Data
plt.plot(x, y, 'rx')
# Fitted function
x_fine = np.linspace(x[0], x[-1], 100)
plt.plot(x_fine, func(x_fine, popt[0], popt[1]), 'b-')
plt.savefig('Linear_fit.png')
plt.show()


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

def func(angular_position, phase_current_displacement):
    _1 = np.sin( angular_position )
    _2 = np.sin( angular_position + phase_current_displacement)
    _3 = np.sin( angular_position + 2 * phase_current_displacement)
    return np.asarray([_1, _2, _3]).ravel()

def deg_to_rad(deg):
    return deg * np.pi/180

def rad_to_deg(rad):
    return rad * 180/np.pi

angles = np.arange(0, 2*np.pi, 2*np.pi/100)
test_data = func(angles, deg_to_rad(60))

print(angles.shape)
print(test_data.shape)
popt, pcov = curve_fit(func, angles, test_data, p0=(1))
print("RET")
print(popt, pcov)

print (rad_to_deg(popt[0]))