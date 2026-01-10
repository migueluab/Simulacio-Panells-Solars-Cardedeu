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

# --- EXEMPLE--- #
# Grafiquem la posició del sol pel dia que vulguem

def corba_posicio(mes, dia):
    # --- Configuració Inicial ---
    #Escollim el dia
    data_plot = datetime.date(2026, mes, dia)

    # Calculem la diferencia de dies respecte el periheli
    delta = data_plot - dia_periheli

    # Coordenades de la terra en aquest dia (UA)
    vector_posicio_plot = np.array([x_tierra[delta.days], y_tierra[delta.days], z_tierra[delta.days]])

    az_plot = []
    alt_plot = []

    az_ticks = []
    alt_ticks = []
    hora_tick = []

    # --- Bucle --- #
    for minut in range(0, 24 * 60, 10):
        # 1. Crear l'hora local
        hora_local_plot = datetime.datetime(
                data_plot.year, data_plot.month, data_plot.day, 0, 0
            ) + datetime.timedelta(minutes=minut)

        # 2. Convertir a UTC
        if data_plot >= datetime.date(2026, 3, 29) and data_plot < datetime.date(2026, 10, 26):
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
                 az_ticks.append(az)
                 alt_ticks.append(alt)
                 hora_tick.append(hora_local_plot)


    return [az_plot, alt_plot], [az_ticks, alt_ticks, hora_tick], [hora_local_plot, data_utc_plot, offset_horari_plot]

# --- Gràfica --- #
plt.figure(figsize=(10, 6))

mesos = {"Gener": 1, "Febrer": 2, "Març": 3, "Abril": 4, "Maig": 5, "Juny": 6, "Juliol": 7, "Agost": 8, "Septembre": 9, 
         "Octubre": 10, "Novembre": 11, "Desembre": 12} #Diccionari amb els noms dels mesos

#Fem una corba pel primer de cada dos mesos
for key, val in mesos.items():
    if val % 2 != 0:
        corba, ticks, hores = corba_posicio(val, 1)
        for az, alt, hora in zip(ticks[0], ticks[1],ticks[2]):
            plt.plot(az, alt, 'yo', markersize=4, zorder=5)     
            plt.text(az, alt,
                f"{hora.strftime('%H:%M')}", 
                fontsize=8, 
                ha='center')    
        plt.plot(corba[0], corba[1], label=f'1 de {key}, Hora local (UTC+{hores[2]})', linewidth=2)

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
plt.legend(loc='upper right', framealpha=0.9, shadow=True)
plt.tight_layout()
plt.gca().tick_params(direction="in")
plt.savefig(f'figures/trajectoriasolar.png', bbox_inches='tight')