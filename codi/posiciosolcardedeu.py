import numpy as np
import datetime
import matplotlib.pyplot as plt
import trajectoria
from func_canvibase import posiciosol

#--- DADES TRAJECTÒRIA TERRA --- #
x_tierra = trajectoria.x 
y_tierra = trajectoria.y
#numpy zeros és més ràpid i net
z_tierra = np.zeros(len(x_tierra))

# --- Configuració Inicial --- #
# Definim el dia del periheli (Considerem que és el 3 de Gener de 2026)
dia_periheli = datetime.date(2026, 1, 3) 

#dates del canvi d'hora hivern/estiu pel 2026:
inici_estiu= datetime.date(2026, 3, 29)
fi_estiu= datetime.date(2026, 10, 26)

def obtenir_offset(data):
    #retorna 2h si és horari d'estiu i 1h si és hivern
    if data>=inici_estiu and data < fi_estiu:
        return 2
    return 1


# Grafiquem la posició del sol pel dia que vulguem
def corba_posicio(mes, dia):
    # --- Configuració Inicial ---
    #Escollim el dia
    data_plot = datetime.date(2026, mes, dia)

    # Calculem la diferencia de dies respecte el periheli
    delta = data_plot - dia_periheli
    #fem el mòdul per assegurar de no passar-nos de 365
    idx= delta.days % len(x_tierra)

    # Coordenades de la terra en aquest dia (UA)
    vector_posicio= np.array([x_tierra[idx], y_tierra[idx], z_tierra[idx]])

    az_plot = []
    alt_plot = []

    marques_hores = []

    offset= obtenir_offset(data_plot)

    # --- Bucle --- #
    for minut in range(0, 24 * 60, 10):
        # 1. Crear l'hora local
        hora_local=datetime.datetime(2026, mes, dia) + datetime.timedelta(minutes=minut)

        data_utc = hora_local - datetime.timedelta(hours=offset)

        # 3. Calcular azimut i alçada
        az, alt = posiciosol(vector_posicio, data_utc)

        #4. Filtrar
        if alt > -10:
            az_plot.append(az)
            alt_plot.append(alt)
            if hora_local.minute == 0:
                 marques_hores.append((az, alt, hora_local.strftime('%H:%M')))


    return az_plot, alt_plot, marques_hores, offset

# --- Gràfica --- #
plt.figure(figsize=(10, 6))

mesos = {"Gener": 1, "Febrer": 2, "Març": 3, "Abril": 4, "Maig": 5, "Juny": 6, "Juliol": 7, "Agost": 8, "Septembre": 9, 
         "Octubre": 10, "Novembre": 11, "Desembre": 12} #Diccionari amb els noms dels mesos

#Fem una corba pel primer de cada dos mesos
for key, val in mesos.items():
    if val % 2 != 0:
        #Ara recollim les 4 variables que torna la funció
        azimuts, altures, llista_hores, off_h = corba_posicio(val, 1)
        
        # Pintem els punts de les hores
        for (h_az, h_alt, h_text) in llista_hores:
            plt.plot(h_az, h_alt, 'yo', markersize=4, zorder=5)     
            plt.text(h_az, h_alt, h_text, fontsize=8, ha='center')    
        
        # Pintem la línea de la trajectoria
        # utilitzem azimuts i altures directament, i off_h per la etiqueta
        plt.plot(azimuts, altures, label=f'1 de {key}, Hora local (UTC+{off_h})', linewidth=2)

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