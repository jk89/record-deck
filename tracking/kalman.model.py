from sympy import *
from sympy.matrices import Matrix, eye, zeros, ones, diag, GramSchmidt

"""
Goal:

To decompose the Kalman logic into its elementary mathmatical operations so they can be expressed and computed
without linear algebra.

Needed definitions
dt
Q(dt)
F(dt)
P

"""

# x, t, z, nu = symbols('x t z nu')


dt, vt, vj = symbols('dt vt vj')

""" Q_low_alpha_T
[T7Over256, T6Over72, T5Over30, T4Over24],
[T6Over72 , T5Over20, T4Over8 , T3Over6 ],
[T5Over30 , T4Over8 , T3Over3 , T2Over2],
[T4Over24 , T3Over6 , T2Over2 , T]
"""
init_Q = Matrix([
    [Pow(dt, 7)/256,Pow(dt, 6)/72,Pow(dt, 5)/30,Pow(dt, 4)/24],
    [Pow(dt, 6)/72,Pow(dt, 5)/20,Pow(dt, 4)/8,Pow(dt, 3)/6],
    [Pow(dt, 5)/30,Pow(dt, 4)/8,Pow(dt, 3)/3,Pow(dt, 2)/2],
    [Pow(dt, 4)/24,Pow(dt, 3)/6,Pow(dt, 2)/2,dt]
    ])

q11, q12, q13, q14, q21, q22, q23, q24, q31, q32, q33, q34, q41, q42, q43, q44 = symbols('q11 q12 q13 q14 q21 q22 q23 q24 q31 q32 q33 q34 q41 q42 q43 q44')
Q = Matrix([
    [q11, q12, q13, q14],
    [q21, q22, q23, q24],
    [q31, q32, q33, q34],
    [q41, q42, q43, q44]
])

""" F_low_alpha_T
    ([
        [1.0, T  , t2Over2, math.pow(T,3)/6],
        [0.0, 1.0, T              , t2Over2],
        [0.0, 0.0, 1.0            , T],
        [0.0, 0.0, 0.0            , 1.0]
    ])
    """

init_F = Matrix([
    [1.0, dt, Pow(dt,2)/2, Pow(dt,3)/6],
    [0.0, 1.0, dt, Pow(dt, 2) / 2],
    [0.0, 0.0, 1.0, dt],
    [0.0, 0.0, 0.0, 1.0]
    ])

f11, f12, f13, f14, f21, f22, f23, f24, f31, f32, f33, f34, f41, f42, f43, f44 = symbols('f11 f12 f13 f14 f21 f22 f23 f24 f31 f32 f33 f34 f41 f42 f43 f44')
F = Matrix([
    [f11, f12, f13, f14],
    [f21, f22, f23, f24],
    [f31, f32, f33, f34],
    [f41, f42, f43, f44]
])

"""
initial p

        [self.variance_theta   , self.variance_theta/T         , self.variance_theta/T2    , 0                   ],
        [self.variance_theta/T , (2*self.variance_theta)/T2    , (3*self.variance_theta)/T3, ((5*self.variance_jerk)/6)*T2],
        [self.variance_theta/T2, (3*self.variance_theta)/T3    , (6*self.variance_theta)/T4, self.variance_jerk * T       ],
        [0           , ((5*self.variance_jerk*T2)/6), self.variance_jerk*T     , self.variance_jerk]

"""

init_P = Matrix([
    [vt, vt/dt, vt/Pow(dt,2), 0.0],
    [vt/dt, (2*vt)/Pow(dt, 2), (3*vt)/Pow(dt, 3), ((5*vj)/6)*Pow(dt, 2)],
    [vt/Pow(dt, 2), (3*vt) / Pow(dt, 3), (6*vt)/Pow(dt,4), vj * dt],
    [0.0, (5*vj*Pow(dt, 2))/6, vj * dt, vj]
])

p11, p12, p13, p14, p21, p22, p23, p24, p31, p32, p33, p34, p41, p42, p43, p44 = symbols('p11 p12 p13 p14 p21 p22 p23 p24 p31 p32 p33 p34 p41 p42 p43 p44')
P = Matrix([
    [p11, p12, p13, p14],
    [p21, p22, p23, p24],
    [p31, p32, p33, p34],
    [p41, p42, p43, p44]
])


"""
Measurement matrix
H: Measurement matrix [1x4]
"""

H = Matrix([[1.0, 0.0, 0.0, 0.0]])


"""
Measurement error matrix
 *  sigma_x: standard deviation of variable x (uncertainty in measurement x)
 *  R: [[sigma_x^2]] [1x1]
"""
R = Matrix([vt])


"""
state X = [x1,x2,x3,x4] = [pos, speed, acc, jerk]

"""

x1, x2, x3, x4 = symbols('x1 x2 x3 x4')

X_k = Matrix([x1, x2, x3, x4])

"""
1)
take last known state X_{k} and project it ahead in time, one step forward using the transition matrix:
 *  X_{k+1} = F_{k,k+1} * X_{k} + B * w_{k}
 ignore w_{k} as it comes from the environment
"""

X_kp1 = F * X_k


"""
2)
Project the error covariance ahead:
 *  P_{k,k+1} = F_{k,k+1} * P_{-k,k} * F_{k,k+1}.T + Q_{k,k+1}
"""

P_kp1 = F * P * F.transpose() + Q


"""
3)
 *  Calculate uncertainty in estimate + uncertainty in measurement:
 *  S = H*P_{k,k+1}*H.T + R
"""

S = H * P_kp1 * H.transpose() + R

"""
4)
 *  Calculate uncertainty in estimate:
 *  C = (P_{k,k+1}*H.T)
 """

C = P_kp1 * H.transpose()


"""
5)

 *  Calculate Kalman Gain:  (S^-1 is the inverted S matrix, in the 1d case it is just a recropical of a scalar)
 *  K = C * S^-1
"""

