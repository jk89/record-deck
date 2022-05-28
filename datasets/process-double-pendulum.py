# dataset details
# author={Asseman, Alexis and Kornuta, Tomasz and Ozcan, Ahmet},
# https://developer.ibm.com/exchanges/data/all/double-pendulum-chaotic/

# this code processes the 20 datasets yielding the time increment (estimated from information in the website above) and the pendulum arm angles
# author of this code
# Jonathan Kelsey

import math
import sys
import numpy as np

x=0
y=1
dt=40.0/17500.0
t=0
radToDeg = 180.0 / math.pi

datasetNumber = sys.argv[1] if len(sys.argv) > 1 else 0 
datasetNumber = int(datasetNumber)
if datasetNumber > 20 or datasetNumber < 0:
    raise Exception("Only datasets from 0 to 20") 
filename = 'datasets/data/double-pendulum/original/dpc_dataset_csv/%d.csv' % (datasetNumber)

with open(filename) as f: 
    lines = f.readlines()
    for line in lines:
        _line = line.strip()
        data = _line.split(",")

        a = (int(data[0]),int(data[1]))
        b = (int(data[2]),int(data[3]))
        c = (int(data[4]),int(data[5]))

        #ab = b - a
        ab = (b[x] - a[x], b[y] - a[y])
        abV = np.array(ab)
        
        angle_ab = np.arctan2(abV[y],abV[x]) * radToDeg
        # this angle is -180 to 180, so we get transitions like this
        #3.4285714285713733 , -179.12309225856936 , -6.480210478691782
        #3.4308571428570875 , 179.80544801593285 , -5.559947263309535
        # as tracking is designed so far we need a 14 bit integer
        angle_ab = int(((angle_ab + 180) / 360) * 2**14)

        #bc = c - b
        bc = (c[x] - b[x], c[y] - b[y])
        bcV = np.array(bc)
        angle_cb = np.arctan2(bcV[y],bcV[x]) * radToDeg
        angle_cb = int(((angle_cb + 180) / 360) * 2**14)

        print(t, ",", angle_ab, ",", angle_cb)

        t+=dt

