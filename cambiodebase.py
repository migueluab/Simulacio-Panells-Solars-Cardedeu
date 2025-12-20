import numpy as np
import datetime
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN ---
# Coordenadas aproximadas de Cardedeu, Barcelona
LAT_CARDEDEU = 41.639852  # Grados Norte
LON_CARDEDEU = 2.359517   # Grados Este

# Parámetros Astrodinámicos
OBLICUIDAD = 23.4392911 # Grados 
LONGITUD_PERIHELIO = 102.9 # Grados 

# Radio de la Tierra en km y Unidad Astronómica en km
RADIO_TIERRA_KM = 6371.0
UA_KM = 149597870.7
RADIO_TIERRA_UA = RADIO_TIERRA_KM / UA_KM

def calcular_posicion_sol_cardedeu(vector_origen, fecha_utc):  

    # --- PASO A: CORRECCIÓN DE PERIHELIO A VERNAL ---
    # Matriz rotación Rz (sentido horario)
    rad_per = np.radians(LONGITUD_PERIHELIO)
    Rz = np.array([ 
        [np.cos(rad_per), -np.sin(rad_per), 0],
        [np.sin(rad_per),  np.cos(rad_per), 0],
        [0, 0, 1]
    ])
    
    # Nuevo vector (alineado al equinoccio)
    r_sol = np.dot(Rz, vector_origen)

    # --- PASO B: ECLÍPTICA -> ECUATORIAL ---
    # Matriz rotación Rx (sentido horario)
    rad_obl = np.radians(OBLICUIDAD)
    Rx= np.array([ 
        [1, 0, 0],
        [0, np.cos(rad_obl), -np.sin(rad_obl)],
        [0, np.sin(rad_obl),  np.cos(rad_obl)]
    ])
    
    # Vector en coordenadas Ecuatoriales 
    r_eq = np.dot(Rx, -r_sol)

    # --- PASO C.1: TIEMPO SIDEREO LOCAL  ---
    year, month, day = fecha_utc.year, fecha_utc.month, fecha_utc.day
    hour, minute, second = fecha_utc.hour, fecha_utc.minute, fecha_utc.second
    UT = hour + (minute/60) + (second/3600) # Hora universal!
    term1 = 367 * year
    term2 = int((7 * (year + int((month + 9) / 12))) / 4)
    term3 = int((275 * month) / 9)
    J0 = term1 - term2 + term3 + day + 1721013.5

    J2000 = 2451545.0
    T0 = (J0 - J2000) / 36525.0
    Theta_G0 = (100.4606184 + 
                36000.77004 * T0 + 
                0.000387933 * (T0**2) - 
                2.583e-8 * (T0**3))
    
    Theta_G = Theta_G0 + 360.98564724 * (UT / 24.0)
    Theta_L = Theta_G + LON_CARDEDEU
    Theta_L = Theta_L % 360.0
   
    # --- PASO C.2: ECUATORIAL -> TOPOCENTRICA ---
    # Matriz rotación Rz (sentido antihorario)
    Theta_L = np.radians(Theta_L)
    R_z = np.array([ 
        [np.cos(Theta_L), np.sin(Theta_L), 0],
        [-np.sin(Theta_L), np.cos(Theta_L), 0],
        [0, 0, 1]
    ])

    # Matriz rotación Ry (sentido antihorario)
    lat_rad = np.radians(LAT_CARDEDEU)
    co_latitud = (np.pi / 2) - lat_rad  # 90º - latitud
    R_y = np.array([ 
        [np.cos(co_latitud), 0, -np.sin(co_latitud)],
        [0, 1, 0],
        [np.sin(co_latitud), 0, np.cos(co_latitud)]
    ])  

    # Vector en coordenadas Topocentricas 
    vec_temp = np.dot(R_z, r_eq)
    vec_temp2 = np.dot(R_y, vec_temp)
    r_topo = vec_temp2 - np.array([0, 0, RADIO_TIERRA_UA])
    
    # --- Paso D: OBTENCIÓN DE AZIMUT Y ALTURA ---
    x_topo, y_topo, z_topo = r_topo
    distancia_topo = np.linalg.norm(r_topo)
    
    h = np.degrees(np.arcsin(z_topo / distancia_topo))
    az = np.degrees(np.arctan2(y_topo, x_topo))
    
    # Ajuste final de Azimut para que 0=Norte, 90=Este (Navegación Estándar)
    az = (180 - az) % 360
    
    return az, h

# --- EJEMPLO---
# 1. Supón que estamos en el perihelio (3 de Enero, Tierra en eje X)
# Tus coordenadas de la Tierra plotteada (en Unidades Astronómicas, por ejemplo)
x_tierra = 1.0 
y_tierra = 0.0
z_tierra = 0.0
vector_posicion = np.array([x_tierra, y_tierra, z_tierra])

# --- Configuración Inicial ---
# Definimos el día local que queremos graficar (ej: 3 de Enero de 2026)
dia_local = datetime.date(2026, 1, 3) 
offset_horario = 1  # España en invierno es UTC+1 (En verano poner 2)

list_azimut = []
list_altura = []

# --- Bucle de cálculo ---
plt.figure(figsize=(10, 6))
for minuto in range(0, 24 * 60, 10): 
    # 1. Crear la hora local
    hora_local = datetime.datetime(
        dia_local.year, dia_local.month, dia_local.day, 0, 0
    ) + datetime.timedelta(minutes=minuto)
    
    # 2. Convertir a UTC 
    fecha_utc = hora_local - datetime.timedelta(hours=offset_horario)

    # 3. Calcular azimut y altura
    az, alt = calcular_posicion_sol_cardedeu(vector_posicion, fecha_utc)
    
    #4. Filtrar
    if alt > -10:
        list_azimut.append(az)
        list_altura.append(alt)
        if hora_local.minute == 0:
            plt.plot(az, alt, 'yo', markersize=4, zorder=5)     
            plt.text(az, alt + 2,
                    f"{hora_local.strftime('%H:%M')}", 
                    fontsize=8, 
                    ha='center')

# --- Graficar ---
plt.plot(list_azimut, list_altura, label=f'Trayectoria Solar (3 Enero, Hora Local UTC+{offset_horario})', color='orange', linewidth=2)
plt.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.6)

label_style = {'color': 'red', 'fontsize': 12, 'fontweight': 'bold', 'ha': 'center', 'va': 'top'}
plt.text(90, -15 , 'E', **label_style)
plt.text(180, -15 , 'S', **label_style)
plt.text(270, -15 , 'O', **label_style)

plt.xlabel("Azimut (Grados)", labelpad=15)
plt.ylabel("Elevación (Grados)")
plt.xticks(np.arange(0, 361, 20))
plt.yticks(np.arange(-10, 91, 10))
plt.xlim(0, 360)
plt.ylim(-10, 90)

plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()