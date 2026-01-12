import numpy as np
import matplotlib.pyplot as plt

# --- PARÀMETRES DEL PROBLEMA --- #
#Condicions inicials
r_0 = 1
v_0  = 0 #dr/dt, al periheli val zero (només component angular = vertical)
theta_0 = 0
l = 1

#Normalització
r_per = 1.4709e11
v_per = 30270
UA = 149597870700
G = 6.67e-11
M_sol = 1.989e30
k = - (G*M_sol) / (v_per**2 * r_per)

#Pas temporal
h = 3600*24 * v_per/r_per

#Vector condicions inicials
Y = np.array([theta_0,r_0,v_0])

# --- FUNCIONS --- #
def f(t,Y):
    '''Aquesta funció pren 
    els valors de t, theta, r, v
    i els posa a les nostres edos''' 
    theta, r, v = Y
    dtheta_dt = l/r**2
    dr_dt = v
    dv_dt = (l**2/r**3) + (k/r**2)

    return np.array([dtheta_dt, dr_dt, dv_dt])

def pas_rk4(f,t,Y):
    '''Aquesta funció fa 
    un pas de runge-Kutta 
    per una funció general'''
    k_1 = f(t,Y)
    k_2 = f(t + h/2, Y + h/2 * k_1)
    k_3 = f(t + h/2, Y + h/2 * k_2)
    k_4 = f(t + h, Y + h * k_3)

    return Y + h/6 * (k_1 + 2*k_2 + 2*k_3 + k_4)

# --- ITERACIÓ RK4 --- #
# Llistes de valors
t = []
theta = []
r = []

t_i = 0

#Bucle
while Y[0] < 2*np.pi:
    t.append(t_i)
    theta.append(Y[0])
    r.append(Y[1])
    Y = pas_rk4(f, t_i, Y)
    t_i += h

#Temps en dies
t_i = t_i * (r_per/v_per)
dies = t_i/(24*60*60)

# Càlcul d'excentritat 
r_max = np.max(r)
r_min = np.min(r)

e = (r_max - r_min)/(r_max+r_min)
#Passem a coordenades cartesianes i unitats astronòmiques(UA)
theta = np.array(theta)
r = np.array(r) * r_per / UA

x = r * np.cos(theta)
y = r * np.sin(theta)

# --- Gràfica ---
plt.figure(figsize = (10,6))

plt.scatter([0], [0], color='gold', s=200, label='Sol (Focus)') #Representem el sol al focus
plt.scatter(x[0], y[0], color = 'forestgreen', s = 50, label = 'Terra al Periheli', zorder = 1) #Representarem també la terra al periheli

plt.plot(x, y, label='Trajectòria de la Terra', color='deepskyblue', zorder = 0)

plt.axis('equal') 
plt.grid(True, linestyle='--', alpha=0.3)
plt.xlabel('x (UA)')
plt.ylabel('y (UA)')
plt.legend(loc = 'upper left', fontsize = 10)
plt.tight_layout()
plt.savefig('figures/trajectoriaterra.png', bbox_inches='tight')