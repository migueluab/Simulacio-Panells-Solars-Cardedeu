import numpy as np
import matplotlib.pyplot as plt

#constants físiques i normalització
G = 6.67e-11
M_sol = 1.989e30

#dades de normalització (Periheli)
r_per = 1.4709e11
v_per = 30270
UA = 149597870700

#constant k del problema reduït
k = - (G * M_sol) / (v_per**2 * r_per)
l = 1 # Moment angular adimensional (normalitzat)

#condicions inicials (adimensionals)
r0 = 1
v0 = 0
theta0 = 0
Y_inicial = np.array([theta0, r0, v0])

#pas temporal (h)
h = 3600 * 24 * v_per / r_per 

#equacions
def derivades(t, Y):
    #calcula les derivades dtheta, dr, dv
    theta, r, v = Y
    
    dtheta_dt = l / r**2
    dr_dt = v
    dv_dt = (l**2 / r**3) + (k / r**2) # Equació radial
    
    return np.array([dtheta_dt, dr_dt, dv_dt])

def calcular_energia(Y):
    theta, r, v = Y
    # v és la velocitat radial (dr/dt)
    # la velocitat angular tangencial és v_theta = l/r
    ec_radial = 0.5 * v**2
    ec_angular = 0.5 * (l / r)**2
    potencial = k / r
    return ec_radial + ec_angular + potencial

# --- MÈTODE 1: EULER EXPLÍCIT ---
def pas_euler_explicit(f, t, Y, h):
    
    derivs = f(t, Y)
    return Y + h * derivs

# --- MÈTODE 2: EULER SEMI-IMPLÍCIT (Cromer) ---
def pas_euler_semi_implicit(t, Y, h):
    theta, r, v = Y
    
    #calculem l'acceleració amb la posició actual
    accel = (l**2 / r**3) + (k / r**2)
    
    #actualitzem Velocitat primer
    v_nou = v + h * accel
    
    #actualitzem radi amb la v_nou
    r_nou = r + h * v_nou
    
    #actualitzem theta amb el r_nou
    dtheta = l / r_nou**2
    theta_nou = theta + h * dtheta
    
    return np.array([theta_nou, r_nou, v_nou])

# --- MÈTODE 3: RK4 (Referència) ---
def pas_rk4(f, t, Y, h):
    k1 = f(t, Y)
    k2 = f(t + h/2, Y + h/2 * k1)
    k3 = f(t + h/2, Y + h/2 * k2)
    k4 = f(t + h, Y + h * k3)
    return Y + h/6 * (k1 + 2*k2 + 2*k3 + k4)

#bucle de simulació
#preparem les dades per a cada mètode
E0 = calcular_energia(Y_inicial)
metodes = {
    "Euler Explícit": {
        "func": pas_euler_explicit, "Y": Y_inicial.copy(), 
        "t": [], "x": [], "y": [], "error": [], # <--- AFEGIT "error": []
        "color": "red", "style": "--"
    },
    "Euler Semi-Implícit": {
        "func": pas_euler_semi_implicit, "Y": Y_inicial.copy(), 
        "t": [], "x": [], "y": [], "error": [], # <--- AFEGIT "error": []
        "color": "green", "style": "-."
    },
    "RK4 (Referència)": {
        "func": pas_rk4, "Y": Y_inicial.copy(), 
        "t": [], "x": [], "y": [], "error": [], # <--- AFEGIT "error": []
        "color": "blue", "style": "-"
    }
}

#simulem una mica més d'un any (per veure si l'òrbita es tanca)
simulacio_dies = 400
t_total_adim = simulacio_dies * (24*3600) * (v_per/r_per) #conversió dies -> adimensional

#bucle principal
t_actual = 0
while t_actual < t_total_adim:
    
    for nom, dades in metodes.items():
        #guardem posició actual (convertida a UA i cartesiana)
        theta_i, r_i, v_i = dades["Y"]
        
        #conversió a coordenades cartesianes i UA per pintar
        r_real = r_i * r_per / UA
        x_i = r_real * np.cos(theta_i)
        y_i = r_real * np.sin(theta_i)
        
        dades["x"].append(x_i)
        dades["y"].append(y_i)
        dades["t"].append(t_actual)
        
        #CÀLCUL DE L'ERROR D'ENERGIA
        E_actual = calcular_energia(dades["Y"])
        error_relatiu = abs((E_actual - E0) / E0)
        dades["error"].append(error_relatiu)

        #fem el pas
        if nom == "Euler Semi-Implícit":
            dades["Y"] = pas_euler_semi_implicit(t_actual, dades["Y"], h)
        else:
            dades["Y"] = dades["func"](derivades, t_actual, dades["Y"], h)
            
    t_actual += h

#gràfiques
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

#gràfic trajectòries
ax1.plot(0, 0, 'o', color='gold', markersize=15, label='Sol', markeredgecolor='orange')
for nom, dades in metodes.items():
    ax1.plot(dades["x"], dades["y"], label=nom, color=dades["color"], linestyle=dades["style"], linewidth=1.5)

ax1.set_title("Comparativa Trajectòries")
ax1.set_xlabel("x (UA)")
ax1.set_ylabel("y (UA)")
ax1.axis('equal')
ax1.grid(True, alpha=0.3)
ax1.legend()

#gràfic error d'Energia (Escala Logarítmica)
for nom, dades in metodes.items():
    #convertim el temps a dies
    temps_dies = np.array(dades["t"]) * (r_per/v_per) / (24*3600)
    ax2.plot(temps_dies, dades["error"], label=nom, color=dades["color"], linestyle=dades["style"])

ax2.set_title("Error Relatiu d'Energia (Conservació)")
ax2.set_xlabel("Temps (dies)")
ax2.set_ylabel("|(E - E0) / E0|")
ax2.set_yscale('log')
ax2.grid(True, which="both", ls="-", alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig('figures/comparativa_error_metodes.png', bbox_inches='tight')
plt.show()
