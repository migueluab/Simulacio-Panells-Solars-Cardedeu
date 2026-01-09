import numpy as np
import datetime
import matplotlib.pyplot as plt
import trajectoria

# --- CONFIGURACIÓ ---
# Coordenades aproximades de Cardedeu
LAT_CARDEDEU = 41.639852  # Graus Norte
LON_CARDEDEU = 2.359517   # Graus Este

# Paràmetres Astrodinàmics
OBLIQUITAT = 23.4392911 # Graus
LONGITUT_PERIHELI = 102.9 # Graus 

# Radi de la Terra en km i Unitat Astronómica 
RADI_TERRA_KM = 6371.0
UA_KM = 149597870.7
RADI_TERRA_UA = RADI_TERRA_KM / UA_KM

def calcular_temps_sideral_greenwich(fecha_utc: datetime.datetime) -> float:
    # TEMPS SIDERI LOCAL: formules a la bibliografia (veure informe) 
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
    return Theta_G % 360.0

def posiciosol(vector_origen: np.array, fecha_utc: datetime.datetime):  
    # PAS A: CORRECCIÓ DE PERIHELI A VERNAL
    # Matriu rotació Rz (sentit horari)
    rad_per = np.radians(LONGITUT_PERIHELI)
    Rz = np.array([ 
        [np.cos(rad_per), -np.sin(rad_per), 0],
        [np.sin(rad_per),  np.cos(rad_per), 0],
        [0, 0, 1]
    ])
    
    # Vector alineat al Equinocci
    r_sol = np.dot(Rz, vector_origen)

    # PAS B: ECLÍPTICA -> EQUATORIAL 
    # Matriu rotació Rx (sentit horari)
    rad_obl = np.radians(OBLIQUITAT)
    Rx= np.array([ 
        [1, 0, 0],
        [0, np.cos(rad_obl), -np.sin(rad_obl)],
        [0, np.sin(rad_obl),  np.cos(rad_obl)]
    ])
    
    # Vector en coordenades Equatorials 
    r_eq = np.dot(Rx, -r_sol)

    # PAS C.1: TEMPS SIDERI LOCAL: formules a la bibliografia (veure informe) 
    Theta_G = calcular_temps_sideral_greenwich(fecha_utc)
    Theta_L = (Theta_G + LON_CARDEDEU) % 360.0
   
    # PAS C.2: EQUATORIAL -> TOPOCENTRICA 
    # Matriu rotació Rz (sentit antihorari)
    Theta_L = np.radians(Theta_L)
    R_z = np.array([ 
        [np.cos(Theta_L), np.sin(Theta_L), 0],
        [-np.sin(Theta_L), np.cos(Theta_L), 0],
        [0, 0, 1]
    ])

    # Matriu rotació Ry (sentit antihorari)
    lat_rad = np.radians(LAT_CARDEDEU)
    co_latitud = (np.pi / 2) - lat_rad  # 90º - latitud
    R_y = np.array([ 
        [np.cos(co_latitud), 0, -np.sin(co_latitud)],
        [0, 1, 0],
        [np.sin(co_latitud), 0, np.cos(co_latitud)]
    ])  

    # Vector en coordenades Topocentriques 
    vec_temp = np.dot(R_z, r_eq)
    vec_temp2 = np.dot(R_y, vec_temp)
    r_topo = vec_temp2 - np.array([0, 0, RADI_TERRA_UA])
    
    # PAS D: OBTENCIÓ DE L'AZIMUT I L'ALÇADA 
    x_topo, y_topo, z_topo = r_topo
    distancia_topo = np.linalg.norm(r_topo)
    
    h = np.degrees(np.arcsin(z_topo / distancia_topo))
    az = np.degrees(np.arctan2(y_topo, x_topo))
    
    # Ajust final per tal que 0=Nord, 90=Est (Navegació Estàndard)
    az = (180 - az) % 360
    
    return az, h