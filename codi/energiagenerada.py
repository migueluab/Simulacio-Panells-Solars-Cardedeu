import numpy as np
import datetime
import matplotlib.pyplot as plt
import trajectoria
import matplotlib.dates as mdates
from func_canvibase import posiciosol

#--- DADES TRAJECTÒRIA TERRA --- #
x_tierra = trajectoria.x 
y_tierra = trajectoria.y
z_tierra = np.array([0.0] * x_tierra.size)

# --- Configuració Inicial --- #
# Definim el dia del periheli (Considerem que és el 3 de Gener de 2026)
dia_periheli = datetime.date(2026, 1, 3) 

# Fem una llista amb els dies fins el 3 de gener de 2027
numdies = 365
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


# --- PARÀMETRES DEL PROBLEMA --- #
I_d = 1362 # Constant solar (W/m^2)
A = 2 # Àrea de les plaques (m^2)
N = 4 # Nombre de plaques
potencia_maxima_panel = 400 # Potència pic per panel (W)

# --- INICIALITZACIÓ --- #
beta_provar = np.arange(0, 91, 1)
t = np.arange(1, 366, 1)
gamma = np.radians(180) #Per conveniencia asumiré que l'orientació de les plaques es de 180, ja que quan el sol està al punt més alt azimut és a 180
Energia_diaria_Wh = [] #Guardarem energia en Watt-hora, no només potència instantànea.

Energia_total = []

# --- BUCLE ---
for beta_provada in beta_provar:
    beta_rad = np.radians(beta_provada)
    Energia_acum = 0
    for alt_list, az_list in zip(lists_altures, lists_azimuts): 
        
        altures = np.array(alt_list) 
        azimuts = np.array(az_list) 
        
        # Filtrem valors positius, nomès volem valors de dia
        mask = altures > 0
        
        # Eliminem els valors de les altures i azimutals per a quan no és de dia
        rad_altures = np.radians(altures[mask])
        rad_az = np.radians(azimuts[mask])

        # Fórmula del cosinus incident
        cos_inc = (np.sin(rad_altures)* np.cos(beta_rad) + np.cos(rad_altures) * np.sin(beta_rad) * np.cos(rad_az - gamma))  

        irradiancia = I_d * np.maximum(cos_inc, 0 ) # Càlcul de irradiància (W/m^2), utilitzem np.maximum per a evitar obtenir valors negatius.
        
        potencia_inst = irradiancia*(potencia_maxima_panel*N/1000) # Potència bruta
        potencia_real = np.minimum(potencia_inst, potencia_maxima_panel*N) # Si la potencia supera el màxim de les plaques, es retalla
        energia_dia_wh = np.sum(potencia_real) * (10 / 60.0) # Càlcul d'energia diaria en Watt-hora
        Energia_acum +=  energia_dia_wh
    Energia_total.append(Energia_acum)

Energia_max_anual = np.argmax(Energia_total)
millor_beta = beta_provar[Energia_max_anual]
max_energia_wh = Energia_total[Energia_max_anual]

print(f"RESULTAT: L'angle òptim és {millor_beta} graus.")
print(f"Energia anual estimada: {max_energia_wh/1000:.2f} kWh")

#Tornem a iterar amb l'angle óptim per a veure quanta energia al dia generarem. 
beta_optim_rad = np.radians(millor_beta)
Energia_dia_op = []

for alt_list, az_list in zip(lists_altures, lists_azimuts): 
    altures = np.array(alt_list) 
    azimuts = np.array(az_list) 
    
    mask = altures > 0
    rad_altures = np.radians(altures[mask])
    rad_az = np.radians(azimuts[mask])

    cos_inc = (np.sin(rad_altures) * np.cos(beta_optim_rad) + 
               np.cos(rad_altures) * np.sin(beta_optim_rad) * np.cos(rad_az - gamma))
    
    irradiancia = I_d * np.maximum(cos_inc, 0)
    potencia_inst = irradiancia*(potencia_maxima_panel*N/1000)
    potencia_real = np.minimum(potencia_inst, potencia_maxima_panel*N)
    energia_dia_wh_op = np.sum(potencia_real) * (10 / 60.0)

    # Guardem l'energia de cada dia
    Energia_dia_op.append(np.sum(potencia_real) * (10.0 / 60.0))


plt.figure(figsize=(10, 6))
plt.plot(dies, np.array(Energia_dia_op)/1000, color='orange', label=f'Inclinació {millor_beta}º')

ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

plt.xlabel("Data de l'any", fontsize=12)
plt.ylabel("Energia Diària (kWh)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig('figures/produccio_anual_optima.png')
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(beta_provar, np.array(Energia_total)/1000, color='blue', linewidth=2)
plt.axvline(millor_beta, color='red', linestyle='--', label=f'Angle Òptim: {millor_beta}º')

plt.xlabel("Angle d'Inclinació (Graus)", fontsize=12)
plt.ylabel("Energia Total Anual (kWh)", fontsize=12)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('figures/optimitzacio_beta.png')