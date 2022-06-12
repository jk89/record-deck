# Run in root directory

from time import sleep
import numpy
import math
import sys
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d


datasetName = sys.argv[1] if len(sys.argv) > 1 else 0 

filename = 'datasets/data/calibration-data/%s' % (datasetName)

std_in = None
with open(filename) as f: 
    std_in = f.readlines()

# std_in = sys.std_in.readlines() does not work with bohek serve
len_std_in = len(std_in)

plot_data = ColumnDataSource(
    dict(
        time=[],
        angle=[],
        phase_a=[],
        phase_b=[],
        phase_c=[],
        vn=[],
        vvn=[],
        phase_a_minus_vn=[],
        phase_b_minus_vn=[],
        phase_c_minus_vn=[],
        phase_a_minus_vvn=[],
        phase_b_minus_vvn=[],
        phase_c_minus_vvn=[],
    )
)

# Plot of phaseX, vn
pX_vn = figure(title="Plot of phaseX vs vn", plot_width=1200)
pX_vn.line(source=plot_data, x='time', y='phase_a', color="red", legend_label="time vs phase_a")
pX_vn.line(source=plot_data, x='time', y='phase_b', color="yellow", legend_label="time vs phase_b")
pX_vn.line(source=plot_data, x='time', y='phase_c', color="black", legend_label="time vs phase_c")
pX_vn.line(source=plot_data, x='time', y='vn', color="blue", legend_label="time vs vn")


# Plot of phaseX - vn
pX_minus_vn = figure(title="Plot of phaseX - vn", plot_width=1200)
pX_minus_vn.line(source=plot_data, x='time', y='phase_a_minus_vn', color="red", legend_label="time vs phase_a_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='phase_b_minus_vn', color="yellow", legend_label="time vs phase_b_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='phase_c_minus_vn', color="black", legend_label="time vs phase_c_minus_vn")
pX_minus_vn.line(source=plot_data, x='time', y='vn', color="blue", legend_label="time vs vn")

# Plot of phaseX - vvn
pX_minus_vnn = figure(title="Plot of phaseX - vnn", plot_width=1200)
pX_minus_vnn.line(source=plot_data, x='time', y='phase_a_minus_vvn', color="red", legend_label="time vs phase_a_minus_vvn")
pX_minus_vnn.line(source=plot_data, x='time', y='phase_b_minus_vvn', color="yellow", legend_label="time vs phase_b_minus_vvn")
pX_minus_vnn.line(source=plot_data, x='time', y='phase_c_minus_vvn', color="black", legend_label="time vs phase_c_minus_vvn")
pX_minus_vnn.line(source=plot_data, x='time', y='vvn', color="blue", legend_label="time vs vvn")


doc = curdoc()
curdoc().add_root(column(pX_vn, pX_minus_vn,pX_minus_vnn))

idx = 0 
def callback():
    global idx
    if ( idx + 1 >= len_std_in):
        return
    else:
        line = std_in[idx]
        line = line.strip()
        dataStr = line.split("\t")
        parity = dataStr[0]
        angle = float(dataStr[1])
        phase_a = float(dataStr[2])
        phase_b = float(dataStr[3])
        phase_c = float(dataStr[4])
        vn = float(dataStr[5])
        vvn = (phase_a + phase_b + phase_c) / 3

        phase_a_minus_vn = phase_a - vn
        phase_b_minus_vn = phase_b - vn
        phase_c_minus_vn = phase_c - vn

        phase_a_minus_vvn = phase_a - vvn
        phase_b_minus_vvn = phase_b - vvn
        phase_c_minus_vvn = phase_c - vvn

        streamObj = {
            "time" : [idx],
            "angle": [angle],
            "phase_a": [phase_a],
            "phase_b": [phase_b],
            "phase_c": [phase_c],
            "vn": [vn],
            "vvn": [vvn],
            "phase_a_minus_vn": [phase_a_minus_vn],
            "phase_b_minus_vn": [phase_b_minus_vn],
            "phase_c_minus_vn": [phase_c_minus_vn],
            "phase_a_minus_vvn": [phase_a_minus_vvn],
            "phase_b_minus_vvn": [phase_b_minus_vvn],
            "phase_c_minus_vvn": [phase_c_minus_vvn]
        }

        plot_data.stream(streamObj)
        idx += 1
        doc.add_next_tick_callback(callback)

doc.add_next_tick_callback(callback)
