import sympy as sp

t = sp.symbols("t")

e_a = sp.Function("e_a")(t)

w_m = sp.Function("w_m")(t)
dw_mdt = sp.Derivative(w_m, t)
d2w_mdt2 = sp.Derivative(dw_mdt, t)

j_m, r_a, k_b, k_t, d_m, l_a = sp.symbols('j_m r_a k_b k_t d_m l_a', real=True, positive=True)  

a = l_a * j_m / k_t
b = (l_a * d_m + r_a * j_m) / k_t
c = (k_b + ((d_m * r_a) / k_t))

kirchoff_newton_ode = sp.Eq(a*d2w_mdt2 + b*dw_mdt + c*w_m, e_a)
# solve
sol = sp.dsolve(kirchoff_newton_ode,w_m) 
print(sol)
print("######")
print(sp.print_latex(sol))