import numpy as np
import math

alpha = 50

# error in angular resolution
# half a whole integer as time and encoder position will tick with 1 t++ e++
angularResolutionError = 0.5 # 100pc of population within this bound
# 3 standard deviations are ~99.7% of the population
stdev_x = angularResolutionError / 3 # estimate
varianceX = stdev_x * stdev_x # about 0.027

#error in jerk
stdev_j =0.00001 #0.001 #0.1
varienceJ = stdev_j * stdev_j
varianceJ = stdev_j * stdev_j #/ (2 * alpha)

q = 2 * alpha * varianceJ # should be q = 0.01

# perhaps the standard deviation IS the resolution error in this case +/- 0.5
# variance would be 0.25

# perhaps the standard deviation IS the smallest unit in this case 1 varience 1


def create_inital_P(T):
    T2 = T ** 2
    T3 = T ** 3
    T4 = T ** 4
    return np.matrix([
        [varianceX   , varianceX/T         , varianceX/T2    , 0                   ],
        [varianceX/T , (2*varianceX)/T2    , (3*varianceX)/T3, ((5*varianceJ)/6)*T2],
        [varianceX/T2, (3*varianceX)/T3    , (6*varianceX)/T4, varianceJ * T       ],
        [0           , ((5*varianceJ*T2)/6), varienceJ*T     , varienceJ]
    ])

# F is the dynamic matrix 

def create_F_full(T):
    global alpha
    p1 = (2 - (2 * alpha * T) + (math.pow(alpha,2) * math.pow(T,2)) - (2 * math.exp(-1 * alpha * T))) / (2 * math.pow(alpha, 3))
    q1 = ((math.exp(-1 * alpha * T) - 1 + (alpha * T)) / math.pow(alpha, 2))
    r1 = (1-math.exp(-1 * alpha * T)) / alpha
    s1 = math.exp(-1 * alpha * T)
    print((T, p1, q1, r1, s1))
    return np.matrix([
        [1.0, T  , math.pow(T,2)/2, p1],
        [0.0, 1.0, T              , q1],
        [0.0, 0.0, 1.0            , r1],
        [0.0, 0,0, 0.0            , s1]
    ])

def create_F_lowAlphaT(T):
    t2Over2 = math.pow(T,2)/2    
    return np.matrix([
        [1.0, T  , t2Over2, math.pow(T,3)/6],
        [0.0, 1.0, T              , t2Over2],
        [0.0, 0.0, 1.0            , T],
        [0.0, 0.0, 0.0            , 1.0]
    ])

#print(create_F_full(0.1))
#print("-----------------------")
#print(create_F_lowAlphaT(0.1))

# H is the measurement matrix

H = np.matrix([[1.0, 0.0, 0.0, 0.0]]) # selecting for theta only

# Q is the Process Noise Covariance Matrix Q

def create_Q_lowAlphaT(T):
    T7Over256 = (T**7)/256
    T6Over72 = (T ** 6)/72
    T5Over30 = (T ** 5)/30
    T5Over20 = (T ** 5)/20
    T4Over24 = (T ** 4)/24
    T4Over8 = (T ** 4)/8
    T3Over6 = (T**3)/6
    T3Over3 = (T**3)/3
    T2Over2 = (T**2)/2
    return np.matrix([
        [T7Over256, T6Over72, T5Over30, T4Over24],
        [T6Over72 , T5Over20, T4Over8 , T3Over6 ],
        [T5Over30 , T4Over8 , T3Over3 , T2Over2],
        [T4Over24 , T3Over6 , T2Over2 , T]
    ]) *q

# acceleration(d) = (b*(B-2*C+D)+c*(C-D)+d*(C-B))/((b-c)*(b-d)*(c-d))
# acceleration(c) = (a*(A-2*B+C)+b*(B-C)+c*(B-A))/((a-b)*(a-c)*(b-c))
# jerk(d) = a(d) - a(c) / (d - c)

# (((b*(B-2*C+D)+c*(C-D)+d*(C-B))/((b-c)*(b-d)*(c-d))) - ((a*(A-2*B+C)+b*(B-C)+c*(B-A))/((a-b)*(a-c)*(b-c)))) divided by another (d-c)

# measurements like (dt, angular pos)

measurements = []
thetaMaxValue = 2**14
timeMaxValue = 2**32 # 4294967296


#0.01142857142857143 , 31 , 12921
#0.013714285714285717 , 16357 , 12712

# we could have time a, time b

## forward
# 1 2 +1 diff +1
# 360 1 +1 diff  -359

# 10 270 diff (270 - 10) = +260 | a < b | b - a > 0
# if a < b && 

# 290 20 diff (360 - 290) = 70 .. + 20 = +90 | a > b | (360  - a) + b > 0 | b - a < 0
# if a > b &&  (360 - a)

## backward
# 2 1 -1 diff -1
# 1 360 -1 diff 359

# 270 10 diff (10 - 270) = -260 | a > b | b - a < 0
# if a > b && 
# 20 290 diff (290 - 360) = - 70 ... - 20 = -90 |  a < b | (b - 360) - a < 0 | b - a > 0
# if a < b && 



# again.......



# 10 270 | (270-360) - 10 = -100

# pseudo code

# if a < b:
# we are either going in the forward direction or (going backwards and crossing 0 past or to max value)
    #if (b - 360) - a < 0:
        #backwards
        #return (b - 360) - a
    #else:
        #forwards
        #return b - a

# elif a > b:
# we are either going in the backward direction or (going forward and crossing 360 past or to min value)
    #if (360  - a) + b > 0:
        #forwards
        #return (360  - a) + b 
    #else:
        #backwards
        #return b - a

# another algorithm
# target current


def kalman_step():
    pass


def calculateDiffTheta(lastTheta, currentTheta):
    delta = (currentTheta - lastTheta) % thetaMaxValue
    return -(thetaMaxValue - delta) if delta > (thetaMaxValue/2) else delta

def calculateDiffTime(lastTime, currentTime):
    if (currentTime < lastTime):
        # overflow!
        # last time might be 4294967295
        # current time might be 10
        # (4294967296 - 4294967295) + 10
        # 1 + 10 = 11
        return (timeMaxValue - lastTime) + currentTime
    else:
        # current time might be 20, last time might be 10
        return currentTime - lastTime


lastState = np.asarray(())
lastP = np.matrix([])
lastMeasurement = np.asarray(())

def takeMeasurement(dt, theta):
    # dt is the last time - current time
    # consider theta going past 360 degrees TODO
    measurements.append((dt,theta))
    state_estimate = estimateStateVectorEularAndKalman((dt,theta))

    return state_estimate

R = np.matrix([[varianceX]])
I = np.eye(4)

def perform_kalman(dt):
    global lastState
    global lastP
    F = create_F_lowAlphaT(dt)
    Q = create_Q_lowAlphaT(dt)

    # project state ahead
    nextState = F*lastState # FIXME be careful if the nextState projection involves a transition over 0/360 mark (mod stuff)

    # Project the error covariance ahead
    P = F*lastP*F.T + Q    

    # Measurement Update (Correction)
    # ===============================
    # Compute the Kalman Gain
    # P is 4 by 4
    # H is 1 by 4
    # s is the uncertainty in estimate + uncertainty in measurement

    #https://www.kalmanfilter.net/kalman1d.html
    #https://academic.csuohio.edu/embedded/Publications/Thesis/Kiran_thesis.pdf
    # k = uncertainty in estimate / (uncertainty in estimate + uncertainty in measurement)
    #  H*P*H.T take this as the uncertainty in estimate as it is the right shape

    S = H*P*H.T + R

    K = (P*H.T) * np.linalg.pinv(S)

    # Update the estimate via z
    # get the last measurement
    Z = lastMeasurement.reshape(H.shape[0],1) # measurements[:,5].reshape(H.shape[0],1) # used to be lastState
    # https://academic.csuohio.edu/embedded/Publications/Thesis/Kiran_thesis.pdf page 19

    y = Z - (H*nextState) # Innovation or Residual
    finalState = nextState + (K*y) # FIXME be careful if next state projection goes past 0 / 360
    # alternative is to allow theta to go past 360 and below 0 and keep track of the total angular displacement
    # this essentially turns the problem into a fully linear system with no mod
    lastState = finalState
    
    # Update the error covariance
    lastP = (I - (K*H))*P
    
    # calculate error of the final state
    errorLastState = H*lastP*H.T

    return (lastState, errorLastState, S, K,)

previous_states = [] # (time, theta,omega,alpha,jerk)

def estimateStateVectorEularAndKalman(measurement):
    global lastState
    global previous_states
    global lastP
    global lastMeasurement
    # FIXME all distance measurements theta old - theta new MUST account for going over
    # 360 degrees
    currentIndex = len(previous_states) - 1
    kalmanState = None

    # process this state
    if currentIndex == -1:
        # just add time and theta
        previous_states.append((measurement[0], measurement[1], 0, 0, 0))
    elif currentIndex == 0:
        # we have a theta recorded previously ... calc omega
        lastTime = previous_states[currentIndex][0]
        lastTheta = previous_states[currentIndex][1]
        currentTime = measurement[0]
        currentTheta = measurement[1]
        dt = calculateDiffTime(lastTime, currentTime)
        ds = calculateDiffTheta(lastTheta, currentTheta)
        currentOmega = (ds) / (dt)
        #print("A",lastTime, currentTime, dt, lastTheta, currentTheta, ds)
        previous_states.append((measurement[0], measurement[1], currentOmega, 0 ,0))
    elif currentIndex == 1:
        # we have an omega estimate recorder previously ... calc omega,alpha
        lastTime = previous_states[currentIndex][0]
        lastTheta = previous_states[currentIndex][1]
        currentTime = measurement[0]
        currentTheta = measurement[1]
        dt = calculateDiffTime(lastTime, currentTime)
        ds = calculateDiffTheta(lastTheta, currentTheta)
        currentOmega = (ds) / (dt)
        lastOmega = previous_states[currentIndex][2]
        currentAlpha = (currentOmega - lastOmega) / (dt)
        #print("B", lastTime, currentTime, dt, lastTheta, currentTheta, ds, currentOmega - lastOmega)
        state_estimate = (measurement[0], measurement[1], currentOmega, currentAlpha ,0)
        np_state_estimate = np.matrix([np.asarray(state_estimate[1:])]).T
        lastState = np_state_estimate
        lastMeasurement = np.array([measurement[1]])
        lastP = create_inital_P(dt)
        kalmanState = perform_kalman(dt)
        previous_states.append(state_estimate)
    else:
        # we have an alpha estimate recorder previously ... calc omega,alpha, jerk
        lastTime = previous_states[currentIndex][0]
        lastTheta = previous_states[currentIndex][1]
        currentTime = measurement[0]
        currentTheta = measurement[1]
        dt = calculateDiffTime(lastTime, currentTime)
        ds = calculateDiffTheta(lastTheta, currentTheta)
        # print(lastTheta, currentTheta, dt, ds)
        currentOmega = (ds) / (dt)
        lastOmega = previous_states[currentIndex][2]
        currentAlpha = (currentOmega - lastOmega) / (dt)
        lastAlpha = previous_states[currentIndex][3]
        jerk = (currentAlpha - lastAlpha) / (dt)
        #print("C", lastTime, currentTime, dt, lastTheta, currentTheta, ds, currentOmega - lastOmega, lastAlpha - currentAlpha)
        state_estimate = (measurement[0], measurement[1], currentOmega, currentAlpha, jerk)
        
        # to account for going beyond 0/360 will reset the measurement and thus angular displacement is not actually measurement[1]
        # each time we go from say 350 -> 10 (+20) clockwise or 10 -> 360 (-20) counter-clockwise
        #lastMeasurement = np.array([measurement[1]])
        #instead we will just sum the difference to the previous measurement
        lastMeasurement = lastMeasurement + ds * 1.0 # make sure it is a float to avoid overflows

        #now to get the real theta we would just take lastState[0] % 360

        kalmanState = perform_kalman(dt)
        previous_states.append(state_estimate)

    return (previous_states[currentIndex + 1],kalmanState)

def estimateStateVector():
    if len(measurements) < 4:
        return (None, None, None, None)
    #latest position 
    currentIndex = len(measurements) - 1
    # measurement index 0 is time interval, index 1 is rotation variable
    # call this index position d
    m_d = measurements[currentIndex]
    m_c = measurements[currentIndex - 1]
    m_b = measurements[currentIndex - 2]
    m_a = measurements[currentIndex - 3]

    theta = m_d[1] # angular position
    omega = (m_d[1] - m_c[1]) / (m_d[0] - m_c[0]) # angular distance / time = angular velocity
    #alpha = (b*(B-2*C+D)+c*(C-D)+d*(C-B))/((b-c)*(b-d)*(c-d)) angular velocity / time = angular acceleration
    alpha = (m_b[0]*(m_b[1]-2*m_c[1]+D)+m_c[0]*(m_c[1]-D)+m_d[0]*(m_c[1]-m_b[1]))/((m_b[0]-m_c[0])*(m_b[0]-m_d[0])*(m_c[0]-m_d[0]))
    # angular jerk = angular acceleration / time
    #https://www.wolframalpha.com/input?i=%28%28%28b*%28B-2*C%2BD%29%2Bc*%28C-D%29%2Bd*%28C-B%29%29%2F%28%28b-c%29*%28b-d%29*%28c-d%29%29%29+-+%28%28a*%28A-2*B%2BC%29%2Bb*%28B-C%29%2Bc*%28B-A%29%29%2F%28%28a-b%29*%28a-c%29*%28b-c%29%29%29%29
    #jerk = (((-1.0 * a * (A - (2 * B) + C)) + (A * c) - (B * (b + c)) + (b * C))/((a - b) * (a - c)) + ((-1 * b * (B - (2 * C) + D)) + (B * d) - (C * (c + d)) + (c * D))/((b - d) (d - c)))/((b - c)*(d - c))
    jerk = (((-1.0 * m_a[0] * (m_a[1] - (2 * m_b[1]) + m_c[1])) + (m_a[1] * m_c[0]) - (m_b[1] * (m_b[0] + m_c[0])) + (m_b[0] * m_c[1]))/((m_a[0] - m_b[0]) * (m_a[0] - m_c[0])) + ((-1 * m_b[0] * (m_b[1] - (2 * m_c[1]) + m_d[1])) + (m_b[1] * m_d[0]) - (m_c[1] * (m_c[0] + m_d[0])) + (m_c[0] * m_d[1]))/((m_b[0] - m_d[0]) (m_d[0] - m_c[0])))/((m_b[0] - m_c[0])*(m_d[0] - m_c[0]))

    return (theta, omega, alpha, jerk)