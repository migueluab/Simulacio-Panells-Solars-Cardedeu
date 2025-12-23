import numpy as np
import matplotlib.pyplot as plt

#Condicions inicials
r_0 = 1
v_0 = 0
theta_0 = 0

l_0 = 1

v_per = 30270
r_per = 1.4709e11
G = 6.67e-11
M_sol = 1.989e30
kappa_0 = - (G*M_sol) / (v_per**2 * r_per)
print(kappa_0)

t_sim = 2*np.pi
h = 2*np.pi/365

Y = np.array([r_0,v_0,theta_0])

def sistema(t,Y,l,kappa): #equacions del sistema
    r, v, theta = Y

    dr_dt = v
    dv_dt = (l**2/r**3) + (kappa/r**2)
    dtheta_dt = l/r**2
    return np.array([dr_dt, dv_dt, dtheta_dt])

def pas_rk4(f,t,Y,h,l, kappa): #pas de runge-kutta4
    k_1 = f(t,Y, l , kappa)
    k_2 = f(t + h/2, Y+h/2 * k_1, l , kappa)
    k_3 = f(t + h/2, Y+ h/2 * k_2, l , kappa)
    k_4 = f(t + h, Y + h * k_3, l , kappa)
    return Y + h/6 * (k_1 + 2*k_2 + 2*k_3 + k_4)

#llista de valors per a guardar els valors
llista_r = []
llista_theta = []
llista_t = []

t_actual = 0

#bucle dels pasos
while Y[2]< 2*np.pi:
    llista_r.append(Y[0])
    llista_theta.append(Y[2])
    llista_t.append(t_actual)

    Y = pas_rk4(sistema, t_actual, Y, h, l_0, kappa_0)

    t_actual += h

t_real = t_actual * (r_per/v_per)
dies = t_real/(24*60*60)
print(dies)

#passo a coordenades cartesianes per a representarlo graficament en un pla
r_adim = np.array(llista_r)
theta_rad = np.array(llista_theta)

x = r_adim * np.cos(theta_rad)
y = r_adim * np.sin(theta_rad)

plt.figure()
plt.plot(x, y, label='Trayectoria de la Terra', color='blue')

plt.scatter([0], [0], color='orange', s=200, label='Sol (Foco)')

plt.axis('equal') 
plt.grid(True, linestyle='--', alpha=0.6)
plt.xlabel('x (r0)')
plt.ylabel('y (r0)')
plt.title('Órbita Terrestre (RK4)')
plt.legend()
plt.show()

