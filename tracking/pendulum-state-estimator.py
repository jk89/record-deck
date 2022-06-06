from turtle import title
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d
import sys 
import math
timing = __import__('small-timeout')
kalman = __import__('kalman-ideas')

datasetNumber = sys.argv[1] if len(sys.argv) > 1 else 0 
datasetNumber = int(datasetNumber)
if datasetNumber > 20 or datasetNumber < 0:
    raise Exception("Only datasets from 0 to 20") 

doc = curdoc()
p = figure(title="State vector: time & theta measurements, Eular estimate for omega, alpha & jerk", plot_width=1200)

p_k_theta = figure(title="Kalman/Eular Sensor Theta vs Time", plot_width=1200)
p_k_omega = figure(title="Kalman/Eular Omega vs Time", plot_width=1200)
p_k_alpha = figure(title="Kalman/Eular Alpha vs Time", plot_width=1200)
p_k_jerk = figure(title="Kalman/Eular Jerk vs Time", plot_width=1200)

#p.yaxis.fixed_location = 0
#p.xaxis.fixed_location = 0
# row(p, column(p_k_theta, p_k_omega, p_k_alpha, p_k_jerk))
curdoc().add_root(column(p, p_k_theta, p_k_omega, p_k_alpha, p_k_jerk))

filename = 'datasets/data/double-pendulum/data%d.csv' % (datasetNumber)

_dt = 1# 0.00228571428 / (10**-9) # [ns]

stdIn = None
with open(filename) as f: 
    stdIn = f.readlines()

# stdIn = sys.stdin.readlines() does not work with bohek serve
lenStdIn = len(stdIn)

plot_data = ColumnDataSource(dict(dt=[],s_theta=[],scaled_s_theta=[],e_omega=[], e_alpha=[], e_jerk=[], d_theta=[], k_omega=[], k_alpha=[], k_jerk=[]))
def clear_plot():
    plot_data.data = {k: [] for k in plot_data.data}
dt = None
s_theta = None
scaled_s_theta = None
e_omega = None
e_alpha = None
e_jerk = None
p.line(source=plot_data, x='dt', y='e_jerk', color="black", legend_label="dt vs Eular jerk")
p.line(source=plot_data, x='dt', y='e_alpha', color="green", legend_label="dt vs Eular alpha")
p.line(source=plot_data, x='dt', y='e_omega', color="red", legend_label="dt vs Eular omega")
p.line(source=plot_data, x='dt', y='scaled_s_theta', color="blue", legend_label="dt vs Scaled Sensor Theta (between 0 -> 100)")


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


#p_k_omega.line(source=plot_data, x='dt', y='k_omega', color="darkred", legend_label="dt vs Kalman Omega")

idx = 0
sign = lambda x: -1 if x < 0 else (1 if x > 0 else (0 if x == 0 else NaN))

def callback(dt):
    global idx
    if ( idx + 1 >= lenStdIn):
        return
        pass
    else:
        line = stdIn[idx]
        line = line.strip()
        dataStr = line.split(",")
        dt = float(dataStr[0])
        s_theta = int(dataStr[1])
        (stateEstimate, kalmanState) = kalman.takeMeasurement(dt, s_theta)
        if kalmanState:
            X_k = kalmanState[0]
            #print(kalmanState)
            # print(X_k[0,0] % 2 ** 14)

            error = kalmanState[1]
            S = kalmanState[2]
            K = kalmanState[3]
            #print(S)
        streamObj = {
            'dt': [stateEstimate[0]],
            's_theta': [float(stateEstimate[1])],
            'scaled_s_theta': [float(stateEstimate[1])/163.84],
            'e_omega': [stateEstimate[2]],
            'e_alpha': [stateEstimate[3]],
            'e_jerk': [stateEstimate[4]],
            "d_theta":[X_k[0,0] % 2 ** 14] if kalmanState else [0],
            "k_omega":[X_k[1,0]] if kalmanState else [0],
            "k_alpha": [X_k[2,0]] if kalmanState else [0],
            "k_jerk":[X_k[3,0]] if kalmanState else [0],
            }
        plot_data.stream(streamObj)
        idx += 1
        doc.add_next_tick_callback(bohek_cb)
maxIdx = len(stdIn) - 1

def bohek_cb():
    #disable timeout as plotting takes a while so its not going to be in sync
    #timing.temporalTimeout(_dt, callback, "ok")
    callback(_dt)

doc.add_next_tick_callback(bohek_cb)
