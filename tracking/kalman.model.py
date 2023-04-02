from sympy import *
from sympy.matrices import Matrix, eye, zeros, ones, diag, GramSchmidt
import pathlib

output_images_path = "tracking/kalman-cpp-math/"

def save_math_ent(name, ent):
    print(name, ent.shape)
    pathlib.Path(output_images_path).mkdir(parents=True, exist_ok=True)
    # sudo apt install texlive-latex-extra dvipng
    preview(ent, viewer='file', filename=(output_images_path+name+'.png'), dvioptions=['-D','1200']) # , viewer='gimp'

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

save_math_ent("Q", Q)

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

save_math_ent("F", F)

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

save_math_ent("P", P)

"""
Measurement matrix
H: Measurement matrix [1x4]
"""

H = Matrix([[1.0, 0.0, 0.0, 0.0]])

save_math_ent("H", H)


"""
Measurement error matrix
 *  sigma_x: standard deviation of variable x (uncertainty in measurement x)
 *  R: [[sigma_x^2]] [1x1]
"""
R = Matrix([vt])

save_math_ent("R", R)

"""
state X = [x1,x2,x3,x4] = [pos, speed, acc, jerk]

"""

x1, x2, x3, x4 = symbols('x1 x2 x3 x4')

X_k = Matrix([x1, x2, x3, x4])

save_math_ent("X_k", X_k)

"""
1)
take last known state X_{k} and project it ahead in time, one step forward using the transition matrix:
 *  X_{k+1} = F_{k,k+1} * X_{k} + B * w_{k}
 ignore w_{k} as it comes from the environment
"""

X_kp1 = F * X_k

save_math_ent("X_kp1", X_kp1)

"""
2)
Project the error covariance ahead:
 *  P_{k,k+1} = F_{k,k+1} * P_{-k,k} * F_{k,k+1}.T + Q_{k,k+1}
"""

P_kp1 = F * P * F.transpose() + Q
save_math_ent("P_kp1", P_kp1)

"""
3)
 *  Calculate uncertainty in estimate + uncertainty in measurement:
 *  S = H*P_{k,k+1}*H.T + R
"""

S = H * P_kp1 * H.transpose() + R
save_math_ent("S", S)

"""
4)
 *  Calculate uncertainty in estimate:
 *  C = (P_{k,k+1}*H.T)
 """

C = P_kp1 * H.transpose()
save_math_ent("C",C)




## inverse_ADJ


"""
5)

 *  Calculate Kalman Gain:  (S^-1 is the inverted S matrix, in the 1d case it is just a recropical of a scalar)
 *  K = C * S^-1
"""

K = C * S.inverse_ADJ()

save_math_ent("K", K)

"""
6)
 *  Update the estimate via z (get the last measurement)
 *  Z = self.theta_displacement.reshape(H.shape[0],1) assume x is 1D [1x1]
"""

"""
measurement = (time, phase_a_minus_vn) = (dt, s)

dt = self.calculate_diff_time(last_time, current_time)
ds = self.calculate_diff_theta(last_theta, current_theta)

first time
self.theta_displacement = np.array([measurement[1]]) = [ds] [1x1]
then after
self.theta_displacement = self.theta_displacement(last-) + ds * 1.0  [1x1] + [1x1]
"""

# t_km1 t_k s_km1 s_k


t_km1, t_k, s_km1, s_k = symbols('t_km1 t_k s_km1 s_k')
_dt = t_k - t_km1
_ds = s_k - s_km1
# s_k = s_km1 + _ds

Z = Matrix([_ds]).reshape(H.shape[0],1)

save_math_ent("Z", Z)

"""
7)
 *  Calculate Innovation or Residual (assuming 1d case)
 *  Y = Z - (H*X_{k+1})
"""

Y = Z - (H * X_kp1)

save_math_ent("Y", Y)

"""
8)
 *  Calculate filtered new state
 *  X_FINAL_{k+1} = X_{k+1} + (K*Y)
"""

X_kp1_final = X_kp1 + (K * Y)

save_math_ent("X_kp1_final", X_kp1_final)

"""
9)
 *  Before next iteration update the error covariance
 *  P_{-k,k} = (I - (K*H)) * P_{k,k+1}
"""

I = eye(4)

save_math_ent("(I - (K*H))", (I - (K*H)))

P_kp2 = (I - (K*H)) * P_kp1
save_math_ent("P_kp2", P_kp2)


# k++ loop