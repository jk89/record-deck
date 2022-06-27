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

print("kirchoff_newton_ode solve for dw/dt")
dwdt_kirchoff_newton_ode = sp.solve(kirchoff_newton_ode, sp.diff(w_m(t), t))
sp.preview(dwdt_kirchoff_newton_ode, viewer='file', filename='bldc-dwdt_kirchoff_newton_ode.png', dvioptions=['-D','1200']) # , viewer='gimp'

# solve
kirchoff_newton_ode_sol = sp.dsolve(kirchoff_newton_ode, w_m(t), ics={w_m(0):0, sp.diff(w_m(t), t).subs(t,0): 0}) 

print ("kirchoff_newton_ode_sol:")
sp.print_latex(kirchoff_newton_ode_sol)
sp.preview(kirchoff_newton_ode_sol, viewer='file', filename='bldc-kirchoff-newton-ode-solution.png', dvioptions=['-D','1200']) # , viewer='gimp'

# diff 

first_diff_kirchoff_newton_ode_sol = sp.diff(kirchoff_newton_ode_sol, t)
print ("first_diff_kirchoff_newton_ode_solution:")
sp.print_latex(first_diff_kirchoff_newton_ode_sol)
sp.preview(first_diff_kirchoff_newton_ode_sol, viewer='file', filename='bldc-first_diff_kirchoff_newton_ode_solution.png', dvioptions=['-D','1200']) # , viewer='gimp'
