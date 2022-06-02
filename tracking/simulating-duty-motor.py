from time import sleep
import numpy
import math
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d

dutyToEquilibriumOmegaCoefficient =  255 / 150 # say 255 duty is max speed at say speed is 150
transitionDeadTime = 10
transitionResponseTime = 300 / 100
omegaNoise = 0.1

##############################

def omegaEstimateFactors(oldDuty, newDuty, t0, td, t2):
    global dutyToEquilibriumOmegaCoefficient
    deltaDuty = newDuty - oldDuty
    gain = dutyToEquilibriumOmegaCoefficient * (deltaDuty)
    transitionResponseTime = t2 - t0 -td
    transitionTimeMiddlePoint = float(transitionResponseTime) / 2
    signDeltaDuty = float(deltaDuty) / abs(deltaDuty)
    growFallTransitionSpeed = transitionResponseTime * 1
    return (gain, transitionTimeMiddlePoint, signDeltaDuty, growFallTransitionSpeed)

def calculateOmegaAtCurrentTime(currentTime, estimateFactors):
    (gain, transitionTimeMiddlePoint, signDeltaDuty, growFallTransitionSpeed) = estimateFactors
    return gain / (1 + math.exp((-1.0*signDeltaDuty*(currentTime - transitionTimeMiddlePoint))/float(growFallTransitionSpeed)))

##################
# reverse

def calculateOmegaAtCurrentTime2(transitionTime, oldDuty, newDuty):
    global dutyToEquilibriumOmegaCoefficient
    global transitionDeadTime
    global transitionResponseTime
    global omegaNoise
    deltaDuty = newDuty - oldDuty
    gain = dutyToEquilibriumOmegaCoefficient * deltaDuty#(deltaDuty)
    signDeltaDuty = float(deltaDuty) / abs(deltaDuty)
    trt = transitionResponseTime * abs(deltaDuty) / 2
    transitionTimeMiddlePoint = transitionTime + transitionDeadTime + (float(trt) / 2)
    growFallTransitionSpeed = trt * 1.0 # this is a guess
    def tick(currentTime):
        oldOmega = oldDuty * dutyToEquilibriumOmegaCoefficient

        #if (currentTime) < transitionTime + transitionDeadTime:
        #    noiseyOmega = numpy.random.normal(oldOmega, omegaNoise, size=1)[0]
        #    return oldOmega # noiseyOmega
        #print(transitionTime, transitionDeadTime, float(transitionResponseTime) / 2, gain, deltaDuty)
        
        denominator = (1 + math.exp((  -1.0 * (currentTime - transitionTimeMiddlePoint))/float(growFallTransitionSpeed)))
        # print("gain, denom, transitionTimeMiddlePoint, cTime", gain, denominator, transitionTimeMiddlePoint, currentTime)
        nextOmega =  gain / denominator
        #18.7 -3.39990637865021 60.5 50 10.5
        print("oldDuty, currentDuty, deltaDuty, nextOmega, oldOmega", oldDuty, currentDuty, deltaDuty, nextOmega, oldOmega) 

        nextOmega = (nextOmega) + oldOmega
        

        noise = numpy.random.normal(nextOmega, omegaNoise, size=1)[0]
        return noise # nextOmega + oldOmega #+ # nextOmega#
    return tick

def getCurrentOmegaEquilibrium(currentDuty):
    global dutyToEquilibriumOmegaCoefficient
    return dutyToEquilibriumOmegaCoefficient * currentDuty



currentDuty = 0
currentTheta = 0
currentOmega = 0
currentTime = 0
initialDuty = 10
initialOmega = 0

transitions = {}

def duty_transition(time, nextDuty):
    transitions[time] = nextDuty

def randomEvolutionFunction(currentOmegaMean):
    global omegaNoise
    def tick(currentTime):
        #return currentOmegaMean
        return numpy.random.normal(currentOmegaMean, omegaNoise, size=1)[0]
    return tick

################# plotting

doc = curdoc()
p = figure(title="Omega, duty vs time simulation via logistic with noise", plot_width=1200)
plotData = ColumnDataSource(dict(time=[],omega=[], duty=[]))
p.line(source=plotData, x='time', y='omega', color="black", legend_label="time vs omega")
p.line(source=plotData, x='time', y='duty', color="green", legend_label="time vs duty")

curdoc().add_root(p)

################### time evolution

currentEvolutionFormula = None
def timeStep():
    global currentTime, currentEvolutionFormula, currentDuty, currentTheta, currentOmega, initialOmega


    if currentTime == 0:
        #initalise
        currentDuty = initialDuty
        initialOmega = getCurrentOmegaEquilibrium(initialDuty)
        currentTheta = 0
        currentEvolutionFormula = randomEvolutionFunction(initialOmega)
    

    if currentTime in transitions:
        # transition duty
        oldDuty = currentDuty
        currentDuty = transitions[currentTime]
        currentEvolutionFormula = calculateOmegaAtCurrentTime2(currentTime, oldDuty, currentDuty)

    # get next data
    currentOmega = currentEvolutionFormula(currentTime)
    streamObj = {"time": [currentTime], "omega": [currentOmega], "duty": [currentDuty]}
    print(streamObj)
    plotData.stream(streamObj)
    sleep(0.05)
    if (currentTime > 600):
        return
    doc.add_next_tick_callback(timeStep)


    currentTime += 1
    pass

# add simulated duty transitions
duty_transition(currentTime+  50, initialDuty + 1) # at t = 50 increment duty by one
duty_transition(currentTime + 100, initialDuty) # at t = 100 decrement duty by one
duty_transition(currentTime + 150, initialDuty + 2) # at t = 150 decrement duty by two
duty_transition(currentTime + 200, initialDuty) # at t = 200 decrement duty by two
duty_transition(currentTime + 250, initialDuty + 10) # at t = 250 decrement duty by 10
duty_transition(currentTime + 300, initialDuty) # at t = 300 decrement duty by two


# start bokeh

doc.add_next_tick_callback(timeStep)
