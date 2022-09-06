from turtle import title
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d
import sys 
import kalman

# import kalman filter class
Kalman_Filter_1D = kalman.Kalman_Filter_1D
# init kalman class with input parameters
# alpha
alpha = 50
# error in angle
angular_resolution_error = 0.5
#error in jerk
jerk_error =0.001
kalman = Kalman_Filter_1D(alpha, angular_resolution_error, jerk_error)#('kalman-ideas')

# parse dataset parameter
dataset_number = sys.argv[1] if len(sys.argv) > 1 else 0 
dataset_number = int(dataset_number)
if dataset_number > 20 or dataset_number < 0:
    raise Exception("Only datasets from 0 to 20") 

_dt = 1# 0.00228571428 / (10**-9) # [ns]

# load data
filename = 'datasets/data/double-pendulum/data%d.csv' % (dataset_number)
std_in = None
with open(filename) as f: 
    std_in = f.readlines()
# std_in = sys.std_in.readlines() does not work with bohek serve
len_std_in = len(std_in)

# define column data source for plot data
plot_data = ColumnDataSource(dict(dt=[],s_theta=[],scaled_s_theta=[],e_omega=[], e_alpha=[], e_jerk=[], d_theta=[], k_omega=[], k_alpha=[], k_jerk=[]))
def clear_plot():
    plot_data.data = {k: [] for k in plot_data.data}
dt = None
s_theta = None
scaled_s_theta = None
e_omega = None
e_alpha = None
e_jerk = None

# create graphs for charting
doc = curdoc()

# chart for eular derivative estimate vs time
p = figure(title="State vector: time & theta measurements, Eular estimate for omega, alpha & jerk", plot_width=1200)
p_k_theta = figure(title="Kalman/Eular Sensor Theta vs Time", plot_width=1200)
p_k_omega = figure(title="Kalman/Eular Omega vs Time", plot_width=1200)
p_k_alpha = figure(title="Kalman/Eular Alpha vs Time", plot_width=1200)
p_k_jerk = figure(title="Kalman/Eular Jerk vs Time", plot_width=1200)

p.line(source=plot_data, x='dt', y='e_jerk', color="black", legend_label="dt vs Eular jerk")
p.line(source=plot_data, x='dt', y='e_alpha', color="green", legend_label="dt vs Eular alpha")
p.line(source=plot_data, x='dt', y='e_omega', color="red", legend_label="dt vs Eular omega")
p.line(source=plot_data, x='dt', y='scaled_s_theta', color="blue", legend_label="dt vs Scaled Sensor Theta (between 0 -> 100)")

# charts for kalman derivative estimate vs time

d_theta = None
k_omega = None
k_alpha = None
k_jerk = None

p_k_theta.scatter(source=plot_data, x='dt', y='s_theta', color="lightblue", legend_label="dt vs Sensor Theta")
p_k_theta.line(source=plot_data, x='dt', y='d_theta', color="blue", legend_label="dt vs ((Displacement Theta) % 2**14)")

p_k_omega.scatter(source=plot_data, x='dt', y='e_omega', color="pink", legend_label="dt vs Eular Omega")
p_k_omega.line(source=plot_data, x='dt', y='k_omega', color="red", legend_label="dt vs Kalman Omega")

p_k_alpha.scatter(source=plot_data, x='dt', y='e_alpha', color="lightgreen", legend_label="dt vs Eular Alpha")
p_k_alpha.line(source=plot_data, x='dt', y='k_alpha', color="green", legend_label="dt vs Kalman Alpha")

p_k_jerk.scatter(source=plot_data, x='dt', y='e_jerk', color="grey", legend_label="dt vs Eular Jerk")
p_k_jerk.line(source=plot_data, x='dt', y='k_jerk', color="black", legend_label="dt vs Kalman Jerk")


# add chart to document
curdoc().add_root(column(p, p_k_theta, p_k_omega, p_k_alpha, p_k_jerk))

# function to process dataset at given time instant, generate kalman
idx = 0
def callback(dt):
    global idx
    if ( idx + 1 >= len_std_in):
        return
    else:
        line = std_in[idx]
        line = line.strip()
        data_str = line.split(",")
        dt = float(data_str[0])
        s_theta = int(data_str[1])
        (state_estimate, kalman_state) = kalman.estimate_state_vector_eular_and_kalman((dt, s_theta))
        if kalman_state:
            X_k = kalman_state[0]
            error = kalman_state[1]
            S = kalman_state[2]
            K = kalman_state[3]

        # create stream obj
        stream_obj = {
            'dt': [state_estimate[0]],
            's_theta': [float(state_estimate[1])],
            'scaled_s_theta': [float(state_estimate[1])/163.84],
            'e_omega': [state_estimate[2]],
            'e_alpha': [state_estimate[3]],
            'e_jerk': [state_estimate[4]],
            "d_theta":[X_k[0,0] % 2 ** 14] if kalman_state else [0],
            "k_omega":[X_k[1,0]] if kalman_state else [0],
            "k_alpha": [X_k[2,0]] if kalman_state else [0],
            "k_jerk":[X_k[3,0]] if kalman_state else [0],
            }

        # stream data
        plot_data.stream(stream_obj)
        # inc data index
        idx += 1
        # add callback for next tick
        doc.add_next_tick_callback(bokeh_callback)

# bokeh callback
def bokeh_callback():
    callback(_dt)

# add first tick callback
doc.add_next_tick_callback(bokeh_callback)
