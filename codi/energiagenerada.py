import numpy as np
import datetime
import matplotlib.pyplot as plt
import trajectoria
from func_canvibase import posiciosol

#--- DADES TRAJECTÒRIA TERRA --- #
x_tierra = trajectoria.x 
y_tierra = trajectoria.y
z_tierra = np.array([0.0] * x_tierra.size)

# --- Configuració Inicial --- #
# Definim el dia del periheli (Considerem que és el 3 de Gener de 2026)
dia_periheli = datetime.date(2026, 1, 3) 

# Fem una llista amb els dies fins el 3 de gener de 2027
numdies = 366
dies = [dia_periheli + datetime.timedelta(days=x) for x in range(numdies)]

lists_azimuts = []
lists_altures = []
lists_minuts = []

# --- BUCLE ANY --- #
for dia, x, y, z in zip(dies, x_tierra, y_tierra, z_tierra):
    vector_posicio = np.array([x, y, z])
    list_azimut = []
    list_altura = []
    list_minuts = []

    # --- BUCLE DIA --- #
    for minut in range(0, 24 * 60, 10): 
        # 1. Crear l'hora local
        hora_local = datetime.datetime(
            dia.year, dia.month, dia.day, 0, 0
        ) + datetime.timedelta(minutes=minut)
        
        # 2. Convertir a UTC, segons el dia
        if dia > datetime.date(2026, 3, 29) and dia < datetime.date(2026, 10, 26):
            offset_horari = 2
        else: 
            offset_horari = 1

        data_utc = hora_local - datetime.timedelta(hours=offset_horari)

        # 3. Calcular azimut i alçada
        az, alt = posiciosol(vector_posicio, data_utc)
        
        #4. Filtrar
        if alt > -10:
            list_azimut.append(az)
            list_altura.append(alt)
            list_minuts.append(minut)

    # --- Emmagatzemem els azimuts i altures de cada dia, amb els minuts corresponents --- #
    lists_azimuts.append(list_azimut)
    lists_altures.append(list_altura)
    lists_minuts.append(list_minuts)


# Suposem que les plaques estan paral·leles al terra
# Angle que formen vector normal a la placa i vector posicio sol: alçada
I_d = 1362 # Constant solar (W/m^2)
A = 2 #Àrea de les plaques (m^2)
N = 4 #Nombre de plaques
potencia_maxima_panel = 400 #Potència pic per panel (W)

# --- INICIALITZACIÓ --- #
# Convertim les llistes en arrays de objectes per iterar més fàcil si no són rectangulars
# Si totes les llistes tenen la mateixa longitud, seria millor fer un array 2D directament
t = np.arange(1, 366, 1)
Energia_diaria_Wh = [] #Guardarem energia en Watt-hora, no només potència instantànea.

# --- BUCLE ---
for alt_list, min_list in zip(lists_altures, lists_minuts):
    altures = np.array(alt_list) # Convertim a arrays de numpy per calcular tot el dia de cop (vectorització)
    altures = np.maximum(altures, 0) # El sol només aporta energia si està sobre l'horitzó, a més, limitem per evitar valors negaius en el sinus
    rad_altures = np.radians(altures)
    irradiancia = I_d*np.sin(rad_altures) # Càlcul de irradiància (W/m^2) sobre el pla horitzontal, utilitzem sin(altura)
    # Si la placa és plana al terra, la normal és vertical, i l'angle de incidència és 90 - altura.
    potencia_inst = irradiancia*(potencia_maxima_panel*N/1000) # Potència bruta
    potencia_real = np.minimum(potencia_inst, potencia_maxima_panel*N) # Si la potencia supera el màxim de les plaques, es retalla
    energia_dia_wh = np.sum(potencia_real) / 60.0 # Càlcul d'energia diaria en Watt-hora, suposem que cada dada en la llista correspon a un minut de diferència

    Energia_diaria_Wh.append(energia_dia_wh)

# --- GRÀFIC --- #
plt.figure(figsize=(10, 6))

plt.plot(t, Energia_diaria_Wh)
#plt.plot(np.arange(0,len(I_abs_horaria[0]), 1), I_abs_horaria[0]) 
# COMENTARIO A BORRAR: El calculo de la intensidad cada hora no funciona, 
# pero el de la potencia sí, en verdad no hace falta era solo para comparar con el PVGS

plt.gca().tick_params(direction="in")
plt.savefig(f'figures/energia.png', bbox_inches='tight')