from sympy import *
from sympy.matrices import Matrix, eye, zeros, ones, diag, GramSchmidt
import pathlib

output_images_path = "tracking/kalman-cpp-math2/"

def save_math_ent(name, ent):
    print(name, ent.shape)
    pathlib.Path(output_images_path).mkdir(parents=True, exist_ok=True)
    # sudo apt install texlive-latex-extra dvipng
    print(latex(ent))
    preview(ent, viewer='file', filename=(output_images_path+name+'.png'), dvioptions=['-D','1200']) # , viewer='gimp'

"""
Goal:

To decompose the Kalman logic into its elementary mathmatical operations so they can be expressed and computed
without linear algebra. This time keeping common dependancies computed seperated and then used downstream in a computed
format. We want to minimise the number of overall computations and hence we need to know the dependancies of computed objects.
See the PDF for details but the summary is that we need for each loop to compute these objects, from these dependancies.

Needed computations.
P_{k+2} -> K, P_{k+1}
X_{k+1}_kalman -> K, Y, X_{k+1}

Dependancies
P_{k+1} -> P_{k}, Q
Y -> X_{k+1}, Z
X_{k+1} -> F, X_{k}

Dynamic definitions
P_{k}
Q_{k}
F_{k}
Z
dt
ds

const definition 
H
R


"""



dt, vt, vj = symbols('dt vt vj')


q11, q12, q13, q14, q21, q22, q23, q24, q31, q32, q33, q34, q41, q42, q43, q44 = symbols('q11 q12 q13 q14 q21 q22 q23 q24 q31 q32 q33 q34 q41 q42 q43 q44')
Q = Matrix([
    [q11, q12, q13, q14],
    [q21, q22, q23, q24],
    [q31, q32, q33, q34],
    [q41, q42, q43, q44]
])

save_math_ent("Q", Q)

f11, f12, f13, f14, f21, f22, f23, f24, f31, f32, f33, f34, f41, f42, f43, f44 = symbols('f11 f12 f13 f14 f21 f22 f23 f24 f31 f32 f33 f34 f41 f42 f43 f44')
F = Matrix([
    [f11, f12, f13, f14],
    [f21, f22, f23, f24],
    [f31, f32, f33, f34],
    [f41, f42, f43, f44]
])

save_math_ent("F", F)

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

# save_math_ent("H", H)


"""
Measurement error matrix
 *  sigma_x: standard deviation of variable x (uncertainty in measurement x)
 *  R: [[sigma_x^2]] [1x1]
"""
R = Matrix([vt])

#save_math_ent("R", R)

"""
state X = [x1,x2,x3,x4] = [pos, speed, acc, jerk]

"""

x1, x2, x3, x4 = symbols('x1 x2 x3 x4')

X_k = Matrix([x1, x2, x3, x4])

#save_math_ent("X_k", X_k)

"""
1)
take last known state X_{k} and project it ahead in time, one step forward using the transition matrix:
 *  X_{k+1} = F_{k,k+1} * X_{k} + B * w_{k}
 ignore w_{k} as it comes from the environment
"""

X_kp1 = F * X_k

save_math_ent("X_kp1", X_kp1)


# simplfy this dependancy for further down the chain
X_kp1_11, X_kp1_21, X_kp1_31, X_kp1_41  = symbols('X_kp1_11 X_kp1_21 X_kp1_31 X_kp1_41')
X_kp1_simple = Matrix([
    [X_kp1_11],
    [X_kp1_21],
    [X_kp1_31],
    [X_kp1_41]
])

save_math_ent("X_kp1_simple", X_kp1_simple)

"""
2)
Project the error covariance ahead: (P_{-k,k} is the last_p P_kp0)
 *  P_{k,k+1} = F_{k,k+1} * P_{-k,k} * F_{k,k+1}.T + Q_{k,k+1}
"""

P_kp1 = F * P * F.transpose() + Q
save_math_ent("P_kp1", P_kp1)

# simplfy this dependancy for further down the chain
P_kp1_11, P_kp1_12, P_kp1_13, P_kp1_14, P_kp1_21, P_kp1_22, P_kp1_23, P_kp1_24, P_kp1_31, P_kp1_32, P_kp1_33, P_kp1_34, P_kp1_41, P_kp1_42, P_kp1_43, P_kp1_44  = symbols('P_kp1_11 P_kp1_12 P_kp1_13 P_kp1_14 P_kp1_21 P_kp1_22 P_kp1_23 P_kp1_24 P_kp1_31 P_kp1_32 P_kp1_33 P_kp1_34 P_kp1_41 P_kp1_42 P_kp1_43 P_kp1_44')
P_kp1_simple = Matrix([
    [P_kp1_11, P_kp1_12, P_kp1_13, P_kp1_14],
    [P_kp1_21, P_kp1_22, P_kp1_23, P_kp1_24],
    [P_kp1_31, P_kp1_32, P_kp1_33, P_kp1_34],
    [P_kp1_41, P_kp1_42, P_kp1_43, P_kp1_44]
])
save_math_ent("P_kp1_simple", P_kp1_simple)


"""
3)
 *  Calculate uncertainty in estimate + uncertainty in measurement:
 *  S = H*P_{k,k+1}*H.T + R
"""

S = H * P_kp1_simple * H.transpose() + R
# save_math_ent("S", S)

"""
4)
 *  Calculate uncertainty in estimate:
 *  C = (P_{k,k+1}*H.T)
 """

C = P_kp1_simple * H.transpose()
# save_math_ent("C",C)




## inverse_ADJ


"""
5)

 *  Calculate Kalman Gain:  (S^-1 is the inverted S matrix, in the 1d case it is just a recropical of a scalar)
 *  K = C * S^-1
"""

K = C * S.inverse_ADJ()

save_math_ent("K", K)

# simplfy this dependancy for further down the chain
K_11, K_21, K_31, K_41  = symbols('K_11 K_21 K_31 K_41')
K_simple = Matrix([
    [K_11],
    [K_21],
    [K_31],
    [K_41]
])
save_math_ent("K_simple", K_simple)


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

Y = Z - (H * X_kp1_simple)

save_math_ent("Y", Y)

# simplfy this dependancy for further down the chain
Y_11  = symbols('Y_11')
Y_simple = Matrix([
    [Y_11]
])
save_math_ent("Y_simple", Y_simple)

"""
8)
 *  Calculate filtered new state
 *  X_FINAL_{k+1} = X_{k+1} + (K*Y)
"""

X_kp1_final = X_kp1_simple + (K_simple * Y_simple)

save_math_ent("X_kp1_final", X_kp1_final)



"""
9)
 *  Before next iteration update the error covariance
 *  P_{-k,k} = (I - (K*H)) * P_{k,k+1}
"""

I = eye(4)

P_kp2 = (I - (K_simple*H)) * P_kp1_simple
save_math_ent("P_kp2", P_kp2)

"""
calculate error 
errorlast_state = self.H*self.last_p*self.H.T
"""

kalman_error = H * P * H.transpose()
save_math_ent("kalman_error", kalman_error)

# k++ loop