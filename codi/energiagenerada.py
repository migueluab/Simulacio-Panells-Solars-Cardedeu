import numpy as np
import matplotlib.pyplot as plt
import trajectoria
from canvibase import posiciosol
import posiciosolcardedeu

# Suposem que le splaques estan paral·leles al terra
# Angle que formen vector normal a la placa i vector posicio sol: alçada

I_d = 1362000 # Constant solar en W/m^2
A = 2 #Àrea de les plaques en m^2
N = 4 #Nombre de plaques
rend = 400/1000*2 #Rendiment de les plaques
I_abs_diaria = []
I_abs_horaria = []
P_gen = []
t = np.arange(1, 366, 1)

# --- BUCLE --- #
# Calculem la potencia generada a cada hora de cada dia, fent servir les llistes de les alçades
for alt_list, min_list in zip(posiciosolcardedeu.lists_altures, posiciosolcardedeu.lists_minuts):
    I = 0
    P = 0
    I_hora = []
    for alt, min in zip(alt_list, min_list):
        I_temp = 0
        I += I_d * np.cos(alt* (2*np.pi/360)) # És el sinus perquè l'alçada és l'angle amb l'horitzontal
        I_temp += I_d * np.cos(alt* (2*np.pi/360)) 
        if min % 60 == 0:
            I_hora.append(I_temp)
            I_temp = 0
        P_temp = I_d * np.cos(alt * (2*np.pi/360)) * A * N * rend
        if P_temp < 400 * N: # Cada placa pot absorbir fins a 400 W/m^2
            P += P_temp
        else:
            P += 400 * N
    I_abs_diaria.append(I)
    I_abs_horaria.append(I_hora)
    P_gen.append(P)


# --- GRÀFIC --- #
plt.figure(figsize=(10, 6))

plt.plot(t, np.array(P_gen))
#plt.plot(np.arange(0,len(I_abs_horaria[0]), 1), I_abs_horaria[0]) 
#COMENTARIO A BORRAR: El calculo de la intensidad cada hora no funciona, 
# pero el de la potencia sí, en verdad no hace falta era solo para comparar con el PVGS
plt.show()
