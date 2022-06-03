from time import sleep
import numpy
import math
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d
kalman = __import__('kalman-ideas')

dutyToEquilibriumOmegaCoefficient =  255 / 150 # say 255 duty is max speed at say speed is 150
transitionDeadTime = 10
transitionResponseTime = 300 / 100
omegaNoise = 0.25

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
    trt = transitionResponseTime
    transitionTimeMiddlePoint = transitionTime + transitionDeadTime + (float(trt) / 2)
    growFallTransitionSpeed = trt / 2 # this is a guess
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

plotData = ColumnDataSource(dict(time=[],s_omega=[], s_theta=[], duty=[], e_alpha=[], e_omega=[], e_jerk=[], k_omega=[], k_alpha=[], k_jerk=[], k_theta=[]))

p.line(source=plotData, x='time', y='s_omega', color="black", legend_label="time vs omega")
p.line(source=plotData, x='time', y='duty', color="purple", legend_label="time vs duty")

p_k_theta = figure(title="Kalman/Eular Sensor Theta vs Time", plot_width=1200)
p_k_omega = figure(title="Kalman/Eular Omega vs Time", plot_width=1200)
p_k_alpha = figure(title="Kalman/Eular Alpha vs Time", plot_width=1200)
p_k_jerk = figure(title="Kalman/Eular Jerk vs Time", plot_width=1200)

p_k_theta.scatter(source=plotData, x='time', y='s_theta', color="lightblue", legend_label="time vs Simulated Sensor Theta")
p_k_theta.line(source=plotData, x='time', y='k_theta', color="blue", legend_label="time vs ((Displacement Simulated Sensor Theta) % 2**14)")
p_k_theta.line(source=plotData, x='time', y='duty', color="purple", legend_label="time vs duty")


p_k_omega.scatter(source=plotData, x='time', y='s_omega', color="pink", legend_label="time vs Eular Omega")
p_k_omega.line(source=plotData, x='time', y='k_omega', color="red", legend_label="time vs Kalman Omega")
p_k_omega.line(source=plotData, x='time', y='duty', color="purple", legend_label="time vs duty")

p_k_alpha.scatter(source=plotData, x='time', y='e_alpha', color="lightgreen", legend_label="time vs Eular Alpha")
p_k_alpha.line(source=plotData, x='time', y='k_alpha', color="green", legend_label="time vs Kalman Alpha")
p_k_alpha.line(source=plotData, x='time', y='duty', color="purple", legend_label="time vs duty")

p_k_jerk.scatter(source=plotData, x='time', y='e_jerk', color="grey", legend_label="time vs Eular Jerk")
p_k_jerk.line(source=plotData, x='time', y='k_jerk', color="black", legend_label="time vs Kalman Jerk")
p_k_jerk.line(source=plotData, x='time', y='duty', color="purple", legend_label="time vs duty")




curdoc().add_root(column(p,p_k_theta,p_k_omega,p_k_alpha,p_k_jerk))

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
    (stateEstimate, kalmanState) = kalman.takeMeasurement(currentTime, currentTheta)

    if kalmanState:
        X_k = kalmanState[0]

    streamObj = {
            'time': [stateEstimate[0]],
            's_theta': [float(currentTheta % 2 ** 14)],
            "duty": [currentDuty],
            's_omega': [currentOmega],
            'e_omega': [stateEstimate[2]],
            'e_alpha': [stateEstimate[3]],
            'e_jerk': [stateEstimate[4]],
            "k_theta":[X_k[0,0] % 2 ** 14] if kalmanState else [0],
            "k_omega":[X_k[1,0]] if kalmanState else [0],
            "k_alpha": [X_k[2,0]] if kalmanState else [0],
            "k_jerk":[X_k[3,0]] if kalmanState else [0],
    }

    #print(streamObj)
            
    #streamObj = {"time": [currentTime], "omega": [currentOmega], "duty": [currentDuty], "theta": currentTheta}

    plotData.stream(streamObj)
    sleep(0.05)
    if (currentTime > 1000):
        return
    doc.add_next_tick_callback(timeStep)

    currentTheta += currentOmega # integrate theta
    currentTime += 1
    pass


startTime = 50


# add simulated duty transitions
duty_transition(startTime+  50, initialDuty + 1)
duty_transition(startTime+ 100, initialDuty)

duty_transition(startTime+  200, initialDuty - 1)
duty_transition(startTime + 250, initialDuty)

duty_transition(startTime + 350, initialDuty + 2)
duty_transition(startTime + 400, initialDuty)

duty_transition(startTime + 500, initialDuty - 2)
duty_transition(startTime + 550, initialDuty)

duty_transition(startTime + 650, initialDuty + 3)
duty_transition(startTime + 700, initialDuty)

duty_transition(startTime + 800, initialDuty - 3)
duty_transition(startTime + 850, initialDuty)

duty_transition(startTime + 650, initialDuty + 4)
duty_transition(startTime + 700, initialDuty)

duty_transition(startTime + 800, initialDuty - 4)
duty_transition(startTime + 850, initialDuty)


# start bokeh

doc.add_next_tick_callback(timeStep)
