from bokeh.plotting import curdoc, figure
from bokeh.models import ColumnDataSource, Range1d
import sys 
timing = __import__('small-timeout')

dt = 0.00228571428 / (10**-9) # [ns]



stdIn = sys.stdin.readlines()
lenStdIn = len(stdIn)
print(stdIn)


# '40.64228571428481 , 8534 , 3083\n'
idx = 0

def callback(dt, ns):
    global idx
    if ( idx + 1 >= lenStdIn):
        pass
    else:
        line = stdIn[idx]
        line = line.strip()
        dataStr = line.split(",")
        _dt = float(dataStr[0])
        theta = int(dataStr[1])
        print(_dt, theta)
        idx += 1
maxIdx = len(stdIn) - 1

timing.temporalTimeout(dt, callback, "ok")

