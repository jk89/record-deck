import sympy as sp

t = sp.symbols("t")

e_a=sp.symbols("e_a", cls=sp.Function) 
w_m=sp.symbols("w_m", cls=sp.Function) 

dw_mdt = w_m(t).diff(t)
d2w_mdt2 = dw_mdt.diff(t)

j_m, r_a, k_b, k_t, d_m, l_a = sp.symbols("j_m r_a k_b k_t d_m l_a", real=True, positive=True)  

a = l_a * j_m / k_t
b = (l_a * d_m + r_a * j_m) / k_t
c = (k_b + ((d_m * r_a) / k_t))

kirchoff_newton_ode = sp.Eq(a*d2w_mdt2 + b*dw_mdt + c*w_m(t), e_a(t))
# solve
sol = sp.dsolve(kirchoff_newton_ode,w_m(t), ics={w_m(0):0, sp.diff(w_m(t), t).subs(t,0): 0}) 
print(sol)
print("######")
sp.print_latex(sol)

sp.preview(sol, viewer='file', filename='sol.png') # , viewer='gimp'