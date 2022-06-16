from time import sleep
import numpy
import math
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d
from kalman import kalman

Kalman_Filter_1D = kalman.Kalman_Filter_1D

# alpha
alpha = 50

# error in angle
angular_resolution_error = 0.5

#error in jerk
jerk_error =0.001

kalman = Kalman_Filter_1D(alpha, angular_resolution_error, jerk_error)#('kalman-ideas')

duty_to_equilibrium_omega_coefficient =  255 / 150 # say 255 duty is max speed at say speed is 150
transition_dead_time = 10
transition_response_time = 300 / 100
omega_noise = 0.25

##############################

def omega_estimate_factors(old_duty, new_duty, t0, td, t2):
    global duty_to_equilibrium_omega_coefficient
    delta_duty = new_duty - old_duty
    gain = duty_to_equilibrium_omega_coefficient * (delta_duty)
    transition_response_time = t2 - t0 -td
    transition_time_middle_point = float(transition_response_time) / 2
    sign_delta_duty = float(delta_duty) / abs(delta_duty)
    grow_fall_transition_speed = transition_response_time * 1
    return (gain, transition_time_middle_point, sign_delta_duty, grow_fall_transition_speed)

##################
# reverse

def calculate_omega_at_current_time(transition_time, old_duty, new_duty):
    global duty_to_equilibrium_omega_coefficient
    global transition_dead_time
    global transition_response_time
    global omega_noise
    delta_duty = new_duty - old_duty
    gain = duty_to_equilibrium_omega_coefficient * delta_duty#(delta_duty)
    trt = transition_response_time
    transition_time_middle_point = transition_time + transition_dead_time + (float(trt) / 2)
    grow_fall_transition_speed = trt / 2 # this is a guess
    def tick(current_time):
        old_omega = old_duty * duty_to_equilibrium_omega_coefficient
        denominator = (1 + math.exp((  -1.0 * (current_time - transition_time_middle_point))/float(grow_fall_transition_speed)))
        next_omega =  gain / denominator
        print("old_duty, current_duty, delta_duty, next_omega, old_omega", old_duty, current_duty, delta_duty, next_omega, old_omega) 
        next_omega = (next_omega) + old_omega
        noise = numpy.random.normal(next_omega, omega_noise, size=1)[0]
        return noise
    return tick

def get_current_omega_equilibrium(current_duty):
    global duty_to_equilibrium_omega_coefficient
    return duty_to_equilibrium_omega_coefficient * current_duty

current_duty = 0
current_theta = 0
current_omega = 0
current_time = 0
initial_duty = 10
initial_omega = 0

transitions = {}
def duty_transition(time, nextDuty):
    transitions[time] = nextDuty

def random_evolution_function(current_omega_mean):
    global omega_noise
    def tick(current_time):
        return numpy.random.normal(current_omega_mean, omega_noise, size=1)[0]
    return tick

################# plotting

doc = curdoc()
p = figure(title="Omega, duty vs time simulation via logistic with noise", plot_width=1200)

plot_data = ColumnDataSource(dict(time=[],s_omega=[], s_theta=[], duty=[], e_alpha=[], e_omega=[], e_jerk=[], k_omega=[], k_alpha=[], k_jerk=[], k_theta=[]))

p.line(source=plot_data, x='time', y='s_omega', color="black", legend_label="time vs omega")
p.line(source=plot_data, x='time', y='duty', color="purple", legend_label="time vs duty")

p_k_theta = figure(title="Kalman/Eular Sensor Theta vs Time", plot_width=1200)
p_k_omega = figure(title="Kalman/Eular Omega vs Time", plot_width=1200)
p_k_alpha = figure(title="Kalman/Eular Alpha vs Time", plot_width=1200)
p_k_jerk = figure(title="Kalman/Eular Jerk vs Time", plot_width=1200)

p_k_theta.scatter(source=plot_data, x='time', y='s_theta', color="lightblue", legend_label="time vs Simulated Sensor Theta")
p_k_theta.line(source=plot_data, x='time', y='k_theta', color="blue", legend_label="time vs ((Displacement Simulated Sensor Theta) % 2**14)")
p_k_theta.line(source=plot_data, x='time', y='duty', color="purple", legend_label="time vs duty")


p_k_omega.scatter(source=plot_data, x='time', y='s_omega', color="pink", legend_label="time vs Eular Omega")
p_k_omega.line(source=plot_data, x='time', y='k_omega', color="red", legend_label="time vs Kalman Omega")
p_k_omega.line(source=plot_data, x='time', y='duty', color="purple", legend_label="time vs duty")

p_k_alpha.scatter(source=plot_data, x='time', y='e_alpha', color="lightgreen", legend_label="time vs Eular Alpha")
p_k_alpha.line(source=plot_data, x='time', y='k_alpha', color="green", legend_label="time vs Kalman Alpha")
p_k_alpha.line(source=plot_data, x='time', y='duty', color="purple", legend_label="time vs duty")

p_k_jerk.scatter(source=plot_data, x='time', y='e_jerk', color="grey", legend_label="time vs Eular Jerk")
p_k_jerk.line(source=plot_data, x='time', y='k_jerk', color="black", legend_label="time vs Kalman Jerk")
p_k_jerk.line(source=plot_data, x='time', y='duty', color="purple", legend_label="time vs duty")




curdoc().add_root(column(p,p_k_theta,p_k_omega,p_k_alpha,p_k_jerk))

################### time evolution

current_evolution_formula = None
def time_step():
    global current_time, current_evolution_formula, current_duty, current_theta, current_omega, initial_omega

    if current_time == 0:
        #initalise
        current_duty = initial_duty
        initial_omega = get_current_omega_equilibrium(initial_duty)
        current_theta = 0
        current_evolution_formula = random_evolution_function(initial_omega)
    
    if current_time in transitions:
        # transition duty
        old_duty = current_duty
        current_duty = transitions[current_time]
        current_evolution_formula = calculate_omega_at_current_time(current_time, old_duty, current_duty)

    # get next data
    current_omega = current_evolution_formula(current_time)
    (state_estimate, kalman_state) = kalman.estimate_state_vector_eular_and_kalman((current_time, current_theta))

    if kalman_state:
        X_k = kalman_state[0]

    stream_obj = {
            'time': [state_estimate[0]],
            's_theta': [float(current_theta % 2 ** 14)],
            "duty": [current_duty],
            's_omega': [current_omega],
            'e_omega': [state_estimate[2]],
            'e_alpha': [state_estimate[3]],
            'e_jerk': [state_estimate[4]],
            "k_theta":[X_k[0,0] % 2 ** 14] if kalman_state else [0],
            "k_omega":[X_k[1,0]] if kalman_state else [0],
            "k_alpha": [X_k[2,0]] if kalman_state else [0],
            "k_jerk":[X_k[3,0]] if kalman_state else [0],
    }

    plot_data.stream(stream_obj)
    sleep(0.05)
    if (current_time > 1000):
        return
    doc.add_next_tick_callback(time_step)

    current_theta += current_omega # integrate theta
    current_time += 1
    pass


start_time = 50


# add simulated duty transitions
duty_transition(start_time+  50, initial_duty + 1)
duty_transition(start_time+ 100, initial_duty)

duty_transition(start_time+  200, initial_duty - 1)
duty_transition(start_time + 250, initial_duty)

duty_transition(start_time + 350, initial_duty + 2)
duty_transition(start_time + 400, initial_duty)

duty_transition(start_time + 500, initial_duty - 2)
duty_transition(start_time + 550, initial_duty)

duty_transition(start_time + 650, initial_duty + 3)
duty_transition(start_time + 700, initial_duty)

duty_transition(start_time + 800, initial_duty - 3)
duty_transition(start_time + 850, initial_duty)

duty_transition(start_time + 650, initial_duty + 4)
duty_transition(start_time + 700, initial_duty)

duty_transition(start_time + 800, initial_duty - 4)
duty_transition(start_time + 850, initial_duty)


# start bokeh

doc.add_next_tick_callback(time_step)
