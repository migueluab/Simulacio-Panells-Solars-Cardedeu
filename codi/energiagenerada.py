import numpy as np
import matplotlib.pyplot as plt
import trajectoria
from canvibase import posiciosol
import posiciosolcardedeu

# Suposem que le splaques estan paral·leles al terra
# Angle que formen vector normal a la placa i vector posicio sol: alçada

I_d = 1362 # Constant solar en W/m^2
A = 2 #Àrea de les plaques en m^2
N = 4 #Nombre de plaques
potencia_maxima_panel = 400 #Potència pic per panel en W

# --- INICIALITZACIÓ --- #
# Convertim les llistes en arrays de objectes per iterar més fàcil si no són rectangulars
#Si totes les llistes tenen la mateixa longitud, seria millor fer un array 2D directament
t = np.arange(1, 366, 1)
Energia_diaria_Wh = [] #Guardarem energia en Watt-hora, no només potència instantànea.

# --- BUCLE ---
for alt_list, min_list in zip(posiciosolcardedeu.lists_altures, posiciosolcardedeu.lists_minuts):
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
#COMENTARIO A BORRAR: El calculo de la intensidad cada hora no funciona, 
# pero el de la potencia sí, en verdad no hace falta era solo para comparar con el PVGS
plt.show()
