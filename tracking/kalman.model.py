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
Q = Matrix([
    [Pow(dt, 7)/256,Pow(dt, 6)/72,Pow(dt, 5)/30,Pow(dt, 4)/24],
    [Pow(dt, 6)/72,Pow(dt, 5)/20,Pow(dt, 4)/8,Pow(dt, 3)/6],
    [Pow(dt, 5)/30,Pow(dt, 4)/8,Pow(dt, 3)/3,Pow(dt, 2)/2],
    [Pow(dt, 4)/24,Pow(dt, 3)/6,Pow(dt, 2)/2,dt]
    ])

""" F_low_alpha_T
    ([
        [1.0, T  , t2Over2, math.pow(T,3)/6],
        [0.0, 1.0, T              , t2Over2],
        [0.0, 0.0, 1.0            , T],
        [0.0, 0.0, 0.0            , 1.0]
    ])
    """

F = Matrix([
    [1.0, dt, Pow(dt,2)/2, Pow(dt,3)/6],
    [0.0, 1.0, dt, Pow(dt, 2) / 2],
    [0.0, 0.0, 1.0, dt],
    [0.0, 0.0, 0.0, 1.0]
    ])

"""
initial p

        [self.variance_theta   , self.variance_theta/T         , self.variance_theta/T2    , 0                   ],
        [self.variance_theta/T , (2*self.variance_theta)/T2    , (3*self.variance_theta)/T3, ((5*self.variance_jerk)/6)*T2],
        [self.variance_theta/T2, (3*self.variance_theta)/T3    , (6*self.variance_theta)/T4, self.variance_jerk * T       ],
        [0           , ((5*self.variance_jerk*T2)/6), self.variance_jerk*T     , self.variance_jerk]

"""

initP = Matrix([
    [vt, vt/dt, vt/Pow(dt,2), 0.0],
    [vt/dt, (2*vt)/Pow(dt, 2), (3*vt)/Pow(dt, 3), ((5*vj)/6)*Pow(dt, 2)],
    [vt/Pow(dt, 2), (3*vt) / Pow(dt, 3), (6*vt)/Pow(dt,4), vj * dt],
    [0.0, (5*vj*Pow(dt, 2))/6, vj * dt, vj]
])

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
