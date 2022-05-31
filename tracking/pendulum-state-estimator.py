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
p = figure(title="Eular estimate State vector, time, theta, omega, alpha, jerk", plot_width=1200)

p_k_theta = figure(title="Kalman/Eular Theta vs Time", plot_width=1200)
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

plot_data = ColumnDataSource(dict(dt=[],theta=[],omega=[], alpha=[], jerk=[]))
def clear_plot():
    plot_data.data = {k: [] for k in plot_data.data}
dt = None
theta = None
omega = None
alpha = None
jerk = None


p.line(source=plot_data, x='dt', y='jerk', color="black", legend_label="dt vs jerk")
p.line(source=plot_data, x='dt', y='alpha', color="green", legend_label="dt vs alpha")
p.line(source=plot_data, x='dt', y='omega', color="red", legend_label="dt vs omega")
p.line(source=plot_data, x='dt', y='theta', color="blue", legend_label="dt vs Theta")

#r = p.scatter(dt='dt', theta='theta', omega='omega', alpha='alpha', jerk='jerk', source=plot_data)

# plot_data.stream({'dt': dt, 'theta': y, 'omega': o, 'alpha': a, 'jerk': 0 })
idx = 0
sign = lambda x: -1 if x < 0 else (1 if x > 0 else (0 if x == 0 else NaN))

def callback(dt):
    global idx
    if ( idx + 1 >= lenStdIn):
        pass
    else:
        line = stdIn[idx]
        line = line.strip()
        dataStr = line.split(",")
        dt = float(dataStr[0])
        theta = int(dataStr[1])
        stateEstimate = kalman.takeMeasurement(dt, theta)
        logAlpha = (0 if stateEstimate[3] == 0 else math.log(abs(stateEstimate[3])) * sign(stateEstimate[3])) * 1161
        #logJerk = (0 if stateEstimate[4] == 0 else math.log(abs(stateEstimate[4])) * sign(stateEstimate[4])) * 780
        streamObj = {'dt': [stateEstimate[0]], 'theta': [float(stateEstimate[1])/163.84], 'omega': [stateEstimate[2]], 'alpha': [stateEstimate[3]], 'jerk': [stateEstimate[4]] }
        plot_data.stream(streamObj)
        idx += 1
maxIdx = len(stdIn) - 1

def bohek_cb():
    #disable timeout as plotting takes a while so its not going to be in sync
    #timing.temporalTimeout(_dt, callback, "ok")
    callback(_dt)
    doc.add_next_tick_callback(bohek_cb)

doc.add_next_tick_callback(bohek_cb)
