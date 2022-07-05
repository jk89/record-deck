import sympy as sp
t = sp.symbols("t")
e_a=sp.symbols("e_a", cls=sp.Function) # voltage
w_m=sp.symbols("w_m", cls=sp.Function) # angular velocity
dw_mdt = w_m(t).diff(t)
d2w_mdt2 = dw_mdt.diff(t)
J_m, R_a, K_b, K_t, D_m, L_a = sp.symbols("J_m R_a K_b K_t D_m L_a", real=True, positive=True)
eq = sp.Eq(J_m*L_a*sp.Derivative(w_m(t), (t, 2))/K_t + (D_m*R_a/K_t + K_b)*w_m(t) + (D_m*L_a + J_m*R_a)*sp.Derivative(w_m(t), t)/K_t, e_a(t))
sol = sp.dsolve(eq, w_m(t), ics={w_m(0):0, sp.diff(w_m(t), t).subs(t,0): 0}) 
sol = sol.subs(e_a(t), t)
sol = sp.dsolve(sol)
sp.pprint(sol)

#print(sol)
#

