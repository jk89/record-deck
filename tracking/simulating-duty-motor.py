from time import sleep
import numpy
import math
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d

dutyToEquilibriumOmegaCoefficient =  255 / 150 # say 255 duty is max speed at say speed is 150
transitionDeadTime = 1
transitionResponseTime = 100
omegaNoise = 1

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
    return gain / (1 + math.exp((signDeltaDuty*(currentTime - transitionTimeMiddlePoint))/growFallTransitionSpeed))

##################
# reverse

def calculateOmegaAtCurrentTime2(transitionTime, oldDuty, newDuty):
    global dutyToEquilibriumOmegaCoefficient
    global transitionDeadTime
    global transitionResponseTime
    global omegaNoise
    deltaDuty = newDuty - oldDuty
    gain = dutyToEquilibriumOmegaCoefficient * (deltaDuty)
    signDeltaDuty = float(deltaDuty) / abs(deltaDuty)
    transitionTimeMiddlePoint = transitionTime + transitionDeadTime + (float(transitionResponseTime) / 2)
    growFallTransitionSpeed = transitionResponseTime * 1.0 # this is a guess
    def tick(currentTime):
        nextOmega =  gain / (1 + math.exp((signDeltaDuty * (transitionTimeMiddlePoint - currentTime))/growFallTransitionSpeed))
        noise = numpy.random.normal(nextOmega, omegaNoise, size=1)[0]
        return nextOmega + noise
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
        return numpy.random.normal(currentOmegaMean, omegaNoise, size=1)[0]
    return tick

################# plotting

doc = curdoc()
p = figure(title="Omega vs time simulation via logistic with noise", plot_width=1200)
plotData = ColumnDataSource(dict(time=[],omega=[]))
p.line(source=plotData, x='time', y='omega', color="black", legend_label="time vs omega")
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
    streamObj = {"time": [currentTime], "omega": [currentOmega]}
    print(streamObj)
    plotData.stream(streamObj)
    sleep(0.1)
    doc.add_next_tick_callback(timeStep)


    currentTime += 1
    pass

# add simulated duty transitions
duty_transition(currentTime + 100, initialDuty + 1) # at t = 100 increment duty by one
# duty_transition(currentTime + 500, initialDuty - 1) # at t = 500 decrement duty by one

# start bokeh

doc.add_next_tick_callback(timeStep)
