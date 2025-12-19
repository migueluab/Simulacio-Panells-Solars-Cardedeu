import numpy as np
import datetime

# --- 1. CONFIGURACIÓN ---
# Coordenadas aproximadas de Cardedeu, Barcelona
LAT_CARDEDEU = 41.639852  # Grados Norte
LON_CARDEDEU = 2.359517   # Grados Este
# Parámetros Astrodinámicos
OBLICUIDAD = 23.4392911 # Grados Inclinación del eje terrestre (epsilon)
LONGITUD_PERIHELIO = 102.9 # Grados 
# Radio de la Tierra en km y Unidad Astronómica en km
RADIO_TIERRA_KM = 6371.0
UA_KM = 149597870.7
RADIO_TIERRA_UA = RADIO_TIERRA_KM / UA_KM

def calcular_posicion_sol_cardedeu(r_tierra_x, r_tierra_y, r_tierra_z, fecha_utc):  

    # --- PASO A: CORRECCIÓN DE PERIHELIO A VERNAL ---
    rad_per = np.radians(LONGITUD_PERIHELIO)
    Rz = np.array([ #senitdo horario
        [np.cos(rad_per), -np.sin(rad_per), 0],
        [np.sin(rad_per),  np.cos(rad_per), 0],
        [0, 0, 1]
    ])
    
    # Vector original (alineado al perihelio)
    vector_origen = np.array([r_tierra_x, r_tierra_y, r_tierra_z])

    # Nuevo vector (alineado al equinoccio)
    r_sol = np.dot(Rz, vector_origen)

    # --- PASO B: ECLÍPTICA -> ECUATORIAL ---
    rad_obl = np.radians(OBLICUIDAD)
    Rx= np.array([ #senitdo horario
        [1, 0, 0],
        [0, np.cos(rad_obl), -np.sin(rad_obl)],
        [0, np.sin(rad_obl),  np.cos(rad_obl)]
    ])
    
    # Vector en coordenadas Ecuatoriales (x_eq, y_eq, z_eq)
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
    Theta_L = np.radians(Theta_L)
    R_z = np.array([ #senitdo anihorario
        [np.cos(Theta_L), np.sin(Theta_L), 0],
        [-np.sin(Theta_L), np.cos(Theta_L), 0],
        [0, 0, 1]
    ])

    lat_rad = np.radians(LAT_CARDEDEU)
    co_latitud = (np.pi / 2) - lat_rad  # 90º - latitud
    R_y = np.array([ #senitdo anihorario
        [np.cos(co_latitud), 0, -np.sin(co_latitud)],
        [0, 1, 0],
        [np.sin(co_latitud), 0, np.cos(co_latitud)]
    ])  

    # R_T = Ry · Rz · r - (0,0,r_t)
    vec_temp = np.dot(R_z, r_eq)
    vec_temp2 = np.dot(R_y, vec_temp)
    r_topocentrico = vec_temp2 - np.array([0, 0, RADIO_TIERRA_UA])
    
    # --- Paso D: OBTENCIÓN DE AZIMUT Y ALTURA ---
    x_topo, y_topo, z_topo = r_topocentrico
    distancia_topo = np.linalg.norm(r_topocentrico)
    
    # Altura (h): Ángulo sobre el plano XY local
    h = np.degrees(np.arcsin(z_topo / distancia_topo))
    # Azimut (A): Ángulo en el plano XY 
    az = np.degrees(np.arctan2(y_topo, x_topo))
    
    # Ajuste final de Azimut para que 0=Norte, 90=Este (Estándar navegación)
    az = (180 - az) % 360
    
    return az, h

# --- EJEMPLO DE USO ---
# 1. Supón que estamos en el perihelio (3 de Enero, Tierra en eje X)
# Tus coordenadas de la Tierra plotteada (en Unidades Astronómicas, por ejemplo)
# NOTA: Deben estar alineadas tal que X apunte al perihelio.
x_tierra = 1.0 
y_tierra = 0.0
z_tierra = 0.0

# 2. Fecha y hora en la que quieres mirar al cielo (UTC)
# Ejemplo: 3 de Enero a las 8:00 UTC (9:00 hora local)
fecha = datetime.datetime(2026, 1, 3, 8, 0, 0)

azimut, altura = calcular_posicion_sol_cardedeu(x_tierra, y_tierra, z_tierra, fecha)

print(f"--- Vista desde Cardedeu ---")
print(f"Fecha (UTC): {fecha}")
print(f"Azimut: {azimut:.2f}° (Donde 90° es Este puro)")
print(f"Altura: {altura:.2f}° (Si es > 0, el sol ha salido)")

if 85 < azimut < 95 and altura > -5:
    print("Resultado coherente: En el equinoccio, el sol sale por el Este.")