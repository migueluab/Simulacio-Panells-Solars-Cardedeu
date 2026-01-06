import numpy as np
import datetime
import matplotlib.pyplot as plt
import trajectoria
from canvibase import posiciosol

#--- DADES TRAJECTÒRIA TERRA --- #

x_tierra = trajectoria.x 
y_tierra = trajectoria.y
z_tierra = np.array([0.0] * x_tierra.size)

# --- Configuració Inicial --- #
# Definim el dia del periheli (Considerem que és el 3 de Gener de 2026)
dia_periheli = datetime.date(2026, 1, 3) 

#Fem una llista amb els dies fins el 3 de gener de 2027
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



# --- EXEMPLE--- #
# Grafiquem la posició del sol pel dia que vulguem
plt.figure(figsize=(10, 6))

# --- Configuració Inicial ---
#Escollim el dia
mes_input = int(input('Mes:'))
dia_input = int(input('Dia:'))
data_plot = datetime.date(2026, mes_input, dia_input)


# Calculem la diferencia de dies respecte el periheli
delta = data_plot - dia_periheli

# Coordenades de la terra en aquest dia (UA)
vector_posicio_plot = np.array([x_tierra[delta.days], y_tierra[delta.days], z_tierra[delta.days]])

az_plot = []
alt_plot = []

# --- Bucle --- #
for minut in range(0, 24 * 60, 10):
    # 1. Crear l'hora local
    hora_local_plot = datetime.datetime(
            data_plot.year, data_plot.month, data_plot.day, 0, 0
        ) + datetime.timedelta(minutes=minut)

    # 2. Convertir a UTC
    if data_plot > datetime.date(2026, 3, 29) and data_plot < datetime.date(2026, 10, 26):
        offset_horari_plot = 2
    else: 
        offset_horari_plot = 1

    data_utc_plot = hora_local_plot - datetime.timedelta(hours=offset_horari_plot)

    # 3. Calcular azimut i alçada
    az, alt = posiciosol(vector_posicio_plot, data_utc_plot)

    #4. Filtrar
    if alt > -10:
        az_plot.append(az)
        alt_plot.append(alt)
        if hora_local_plot.minute == 0:
            plt.plot(az, alt, 'yo', markersize=4, zorder=5)     
            plt.text(az, alt + 2,
                    f"{hora_local_plot.strftime('%H:%M')}", 
                    fontsize=8, 
                    ha='center')

# --- Gràfica --- #
plt.plot(az_plot, alt_plot, label=f'Trajectòria Solar ({data_utc_plot.strftime("%Y-%m-%d")}) Hora Local UTC+{offset_horari_plot})', color='orange', linewidth=2)
plt.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.6)

label_style = {'color': 'red', 'fontsize': 12, 'fontweight': 'bold', 'ha': 'center', 'va': 'top'}
plt.text(90, -15 , 'E', **label_style)
plt.text(180, -15 , 'S', **label_style)
plt.text(270, -15 , 'O', **label_style)

plt.xlabel("Azimut (Graus)", labelpad=15)
plt.ylabel("Elevació (Graus)")
plt.xticks(np.arange(0, 361, 20))
plt.yticks(np.arange(-10, 91, 10))
plt.xlim(0, 360)
plt.ylim(-10, 90)

plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.gca().tick_params(direction="in")
plt.savefig(f'figures/trajectoriasolar({data_utc_plot.strftime("%Y-%m-%d")}).png', bbox_inches='tight')