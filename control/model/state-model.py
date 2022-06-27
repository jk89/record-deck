import sympy as sp

t = sp.symbols("t")

e_a=sp.symbols("e_a", cls=sp.Function) # voltage
w_m=sp.symbols("w_m", cls=sp.Function) # angular velocity

dw_mdt = w_m(t).diff(t)
d2w_mdt2 = dw_mdt.diff(t)

J_m, R_a, K_b, K_t, D_m, L_a = sp.symbols("J_m R_a K_b K_t D_m L_a", real=True, positive=True)  
# motor inertia/torque coeff, armature resistance, back-emf/angular velocity coeff, torque/current coeff, viscous damping term, armature inductance

a = L_a * J_m / K_t
b = (L_a * D_m + R_a * J_m) / K_t
c = (K_b + ((D_m * R_a) / K_t))

kirchoff_newton_ode = sp.Eq(a*d2w_mdt2 + b*dw_mdt + c*w_m(t), e_a(t))

print("kirchoff_newton_ode:")
sp.print_latex(kirchoff_newton_ode)
sp.preview(kirchoff_newton_ode, viewer='file', filename='bldc-kirchoff-newton-ode.png', dvioptions=['-D','1200']) # , viewer='gimp'

# solve
sol = sp.dsolve(kirchoff_newton_ode,w_m(t), ics={w_m(0):0, sp.diff(w_m(t), t).subs(t,0): 0}) 

print ("ode sol:")
sp.print_latex(sol)
sp.preview(sol, viewer='file', filename='bldc-kirchoff-newton-ode-solution.png', dvioptions=['-D','1200']) # , viewer='gimp'