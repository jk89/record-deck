import numpy as np
import math


def Kalman_Filter_1D_create_Q_low_alpha_T(self, T):
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
    ]) * self.q

def Kalman_Filter_1D_create_initial_P(self, T):
    T2 = T ** 2
    T3 = T ** 3
    T4 = T ** 4
    return np.matrix([
        [self.variance_theta   , self.variance_theta/T         , self.variance_theta/T2    , 0                   ],
        [self.variance_theta/T , (2*self.variance_theta)/T2    , (3*self.variance_theta)/T3, ((5*self.variance_jerk)/6)*T2],
        [self.variance_theta/T2, (3*self.variance_theta)/T3    , (6*self.variance_theta)/T4, self.variance_jerk * T       ],
        [0           , ((5*self.variance_jerk*T2)/6), self.variance_jerk*T     , self.variance_jerk]
    ])

def Kalman_Filter_1D_create_F_low_alpha_T(self, T):
    t2Over2 = math.pow(T,2)/2    
    return np.matrix([
        [1.0, T  , t2Over2, math.pow(T,3)/6],
        [0.0, 1.0, T              , t2Over2],
        [0.0, 0.0, 1.0            , T],
        [0.0, 0.0, 0.0            , 1.0]
    ])

def Kalman_Filter_1D_calculate_diff_theta(self, last_theta, current_theta):
    delta = (current_theta - last_theta) % self.max_theta_step
    return -(self.max_theta_step - delta) if delta > (self.max_theta_step/2) else delta

def Kalman_Filter_1D_calculate_diff_time(self, last_time, current_time):
    if (current_time < last_time):
        # overflow!
        return (self.max_time_value - last_time) + current_time
    else:
        # current time might be 20, last time might be 10
        return current_time - last_time


def Kalman_Filter_1D_perform_kalman(self, dt):
    F = self.create_F_low_alpha_T(dt)
    Q = self.create_Q_low_alpha_T(dt)

    # project state ahead
    next_state = F*self.last_state # FIXME be careful if the next_state projection involves a transition over 0/360 mark (mod stuff)

    # Project the error covariance ahead
    P = F*self.last_p*F.T + Q    

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

    S = self.H*P*self.H.T + self.R

    K = (P*self.H.T) * np.linalg.pinv(S)

    # Update the estimate via z
    # get the last measurement
    Z = self.theta_displacement.reshape(self.H.shape[0],1) # measurements[:,5].reshape(H.shape[0],1) # used to be last_state
    # https://academic.csuohio.edu/embedded/Publications/Thesis/Kiran_thesis.pdf page 19

    y = Z - (self.H*next_state) # Innovation or Residual
    final_state = next_state + (K*y) # FIXME be careful if next state projection goes past 0 / 360
    # alternative is to allow theta to go past 360 and below 0 and keep track of the total angular displacement
    # this essentially turns the problem into a fully linear system with no mod
    self.last_state = final_state
    
    # Update the error covariance
    self.last_p = (self.I - (K*self.H))*P
    
    # calculate error of the final state
    errorlast_state = self.H*self.last_p*self.H.T

    return (self.last_state, errorlast_state, S, K,)


def Kalman_Filter_1D_estimate_state_vector_eular_and_kalman(self, measurement):
    # FIXME all distance measurements theta old - theta new MUST account for going over
    # 360 degrees
    current_idx = len(self.states) - 1
    kalman_state = None

    print("measurement", measurement, current_idx)

    # process this state
    if current_idx == -1:
        # just add time and theta
        self.states.append((measurement[0], measurement[1], 0, 0, 0))
    elif current_idx == 0:
        # we have a theta recorded previously ... calc omega
        last_time = self.states[current_idx][0]
        last_theta = self.states[current_idx][1]
        current_time = measurement[0]
        current_theta = measurement[1]
        dt = self.calculate_diff_time(last_time, current_time)
        ds = self.calculate_diff_theta(last_theta, current_theta)
        current_omega = (ds) / (dt)
        #print("A",last_time, current_time, dt, last_theta, current_theta, ds)
        self.states.append((measurement[0], measurement[1], current_omega, 0 ,0))
    elif current_idx == 1:
        # we have an omega estimate recorder previously ... calc omega,alpha
        last_time = self.states[current_idx][0]
        last_theta = self.states[current_idx][1]
        current_time = measurement[0]
        current_theta = measurement[1]
        dt = self.calculate_diff_time(last_time, current_time)
        ds = self.calculate_diff_theta(last_theta, current_theta)
        current_omega = (ds) / (dt)
        last_omega = self.states[current_idx][2]
        currentAlpha = (current_omega - last_omega) / (dt)
        #print("B", last_time, current_time, dt, last_theta, current_theta, ds, current_omega - last_omega)
        state_estimate = (measurement[0], measurement[1], current_omega, currentAlpha ,0)
        np_state_estimate = np.matrix([np.asarray(state_estimate[1:])]).T
        self.last_state = np_state_estimate
        self.theta_displacement = np.array([measurement[1]])
        self.last_p = self.create_initial_P(dt)
        kalman_state = self.perform_kalman(dt)
        self.states.append(state_estimate)
    else:
        # we have an alpha estimate recorder previously ... calc omega,alpha, jerk
        last_time = self.states[current_idx][0]
        last_theta = self.states[current_idx][1]
        current_time = measurement[0]
        current_theta = measurement[1]
        dt = self.calculate_diff_time(last_time, current_time)
        ds = self.calculate_diff_theta(last_theta, current_theta)
        # print(last_theta, current_theta, dt, ds)
        current_omega = (ds) / (dt)
        last_omega = self.states[current_idx][2]
        currentAlpha = (current_omega - last_omega) / (dt)
        last_alpha = self.states[current_idx][3]
        jerk = (currentAlpha - last_alpha) / (dt)
        #print("C", last_time, current_time, dt, last_theta, current_theta, ds, current_omega - last_omega, last_alpha - currentAlpha)
        state_estimate = (measurement[0], measurement[1], current_omega, currentAlpha, jerk)
        
        # to account for going beyond 0/360 will reset the measurement and thus angular displacement is not actually measurement[1]
        # each time we go from say 350 -> 10 (+20) clockwise or 10 -> 360 (-20) counter-clockwise
        #self.theta_displacement = np.array([measurement[1]])
        #instead we will just sum the difference to the previous measurement
        self.theta_displacement = self.theta_displacement + ds * 1.0 # make sure it is a float to avoid overflows

        #now to get the real theta we would just take last_state[0] % 360

        kalman_state = self.perform_kalman(dt)
        self.states.append(state_estimate)

    return (self.states[current_idx + 1],kalman_state)

def Kalman_Filter_1D_init(self, alpha, theta_resolution_error, jerk_error):
    self.states = []
    self.alpha = alpha
    self.stdev_theta = theta_resolution_error
    self.stdev_jerk = jerk_error
    # compute variance
    self.variance_theta = self.stdev_theta * self.stdev_theta
    self.variance_jerk = self.stdev_jerk * self.stdev_jerk
    # compute q
    self.q = 2 * self.alpha * self.variance_jerk 
    # create H (is the measurement matrix)
    self.H = np.matrix([[1.0, 0.0, 0.0, 0.0]])
    # create R
    self.R = np.matrix([[self.variance_theta]])

    self.max_theta_step = 2**14 # 16384
    self.max_time_value = 2**32 # 4294967296

    self.last_state = np.asarray(())
    self.last_p = np.matrix([])
    self.theta_displacement = np.asarray(())
    self.I = np.eye(4)

class Kalman_Filter_1D():
    __init__ = Kalman_Filter_1D_init
    create_Q_low_alpha_T = Kalman_Filter_1D_create_Q_low_alpha_T
    create_initial_P = Kalman_Filter_1D_create_initial_P
    create_F_low_alpha_T = Kalman_Filter_1D_create_F_low_alpha_T
    calculate_diff_theta = Kalman_Filter_1D_calculate_diff_theta
    calculate_diff_time = Kalman_Filter_1D_calculate_diff_time
    perform_kalman = Kalman_Filter_1D_perform_kalman
    estimate_state_vector_eular_and_kalman = Kalman_Filter_1D_estimate_state_vector_eular_and_kalman


