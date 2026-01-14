import numpy as np
import datetime
import matplotlib.pyplot as plt
import trajectoria
from func_canvibase import posiciosol
from posiciosolcardedeu import obtenir_offset

#generació de dades solars
#dades trajectòria Terra
x_tierra = trajectoria.x 
y_tierra = trajectoria.y
z_tierra = np.zeros(len(x_tierra))

dia_periheli = datetime.date(2026, 1, 3)
lists_altures = []

#fem un bucle per als 365 dies de l'any
dies_any = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(365)]

for dia in dies_any:
    #busquem posició de la Terra avui
    delta = dia - dia_periheli
    idx = delta.days % len(x_tierra)
    vec_terra = np.array([x_tierra[idx], y_tierra[idx], z_tierra[idx]])
    
    offset = obtenir_offset(dia)
    altures_dia = []
    
    #bucle de minuts (cada 10 minuts)
    for minut in range(0, 1440, 10):
        hora_local = datetime.datetime(dia.year, dia.month, dia.day) + datetime.timedelta(minutes=minut)
        data_utc = hora_local - datetime.timedelta(hours=offset)
        
        #càlcul posició
        az, alt = posiciosol(vec_terra, data_utc)
        altures_dia.append(alt)
        
    lists_altures.append(altures_dia)

#paràmetres tècnics i economics
PREU_PANELL = 600.0       # € (inclou panell, inversor proporcional i instal·lació)
PREU_COMPRA_XARXA = 0.20  # €/kWh (el que paguem si no tenim sol)
PREU_VENDA_EXCEDENT = 0.05 # €/kWh (el que ens paguen pel que sobra)
VIDA_UTIL = 25            # Anys que dura la instal·lació
CONSUM_ANUAL_LLAR = 3500  # kWh/any (consum típic família 4 persones)

CONSTANT_SOLAR = 1362.0   # W/m^2
POTENCIA_PIC_PANELL = 400.0 # W

#perfil de generació per 1 panell
#agafem les llistes de 'posiciosolcardedeu' i calculem quanta energia fa un panell durant tot l'any minut a minut.

potencia_1_panell_minutal = []

#iterem sobre les llistes d'altures
for alt_dia in lists_altures:
    alts = np.array(alt_dia)
    
    #el sol sota l'horitzó no suma
    alts = np.maximum(alts, 0)
    
    #irradiancia = I_0 * sin(altura) per placa horitzontal
    irrad = CONSTANT_SOLAR * np.sin(np.radians(alts))
    
    #potència = Irradiancia * (Eficiència/Area...) 
    #simplificació: Regla de tres amb la potència pic (a 1000 W/m^2 treu 400W)
    pot = irrad * (POTENCIA_PIC_PANELL / 1000.0)
    
    #el panell no pot donar més de 400W encara que hi hagi molt sol
    pot = np.minimum(pot, POTENCIA_PIC_PANELL)
    
    potencia_1_panell_minutal.extend(pot) #afegim al vector llarg de tot l'any

#convertim a array de numpy per operar ràpid
generacio_unitaria = np.array(potencia_1_panell_minutal)

#perfil de consum
#per fer l'optimització realista, necessitem saber quan consumim.
num_minuts = len(generacio_unitaria)

#consum base constant
consum_base_W = (CONSUM_ANUAL_LLAR * 1000) / (365 * 24)
consum_real_W = np.full(num_minuts, consum_base_W)

#bucle d'optimitzacio
llista_panells = range(1, 16) #provarem d'1 a 15 panells
beneficis_nets = []
autoconsum_percent = []

for N in llista_panells:
    #generació total amb N panells
    generacio_total = generacio_unitaria * N
    
    #balanç energètic instantani
    # energia que aprofitem directament es el mínim entre el que produïm i el que necessitem
    energia_autoconsumida_W = np.minimum(generacio_total, consum_real_W)
    
    #energia que ens sobra
    energia_excedent_W = np.maximum(generacio_total - consum_real_W, 0)
    
    #passem de Potència (W) a Energia (kWh) anual
    kwh_autoconsum = np.sum(energia_autoconsumida_W) / 6000
    kwh_excedent = np.sum(energia_excedent_W) / 6000
    
    # balanç economic
    #estalviem el preu de compra pel que autoconsumim
    estalvi_factura = kwh_autoconsum * PREU_COMPRA_XARXA
    #guanyem el preu de venda pel que donem a la xarxa
    pagament_excedents = kwh_excedent * PREU_VENDA_EXCEDENT
    
    flux_caixa_anual = estalvi_factura + pagament_excedents
    
    #càlcul a llarg termini (25 anys)
    inversio_inicial = N * PREU_PANELL
    benefici_total = (flux_caixa_anual * VIDA_UTIL) - inversio_inicial
    
    beneficis_nets.append(benefici_total)
    
    #% d'independència de la xarxa
    total_consum_kwh = np.sum(consum_real_W) / 6000
    autoconsum_percent.append((kwh_autoconsum / total_consum_kwh) * 100)

#gràfic
#busquem el màxim
idx_optim = np.argmax(beneficis_nets)
num_optim = llista_panells[idx_optim]
benefici_maxim = beneficis_nets[idx_optim]

plt.figure(figsize=(10, 6))

#pintem la corba de benefici
plt.plot(llista_panells, beneficis_nets, marker='o', linestyle='-', color='teal', label='Benefici Net (25 anys)')

#marquem el punt òptim
plt.scatter([num_optim], [benefici_maxim], color='red', s=100, zorder=5, label=f'Òptim: {num_optim} panells')
plt.axvline(num_optim, color='red', linestyle='--', alpha=0.3)

plt.title('Optimització Econòmica del Nombre de Panells', fontsize=14)
plt.xlabel('Nombre de Panells (N)', fontsize=12)
plt.ylabel('Benefici Net Acumulat (€)', fontsize=12)
plt.grid(True, alpha=0.5)
plt.legend()
plt.xticks(llista_panells)

#text explicatiu al gràfic
plt.text(num_optim + 0.5, benefici_maxim, 
         f"Màxim Benefici: {benefici_maxim:.0f} €\nAutoconsum: {autoconsum_percent[idx_optim]:.1f}%", 
         verticalalignment='top')

plt.tight_layout()
plt.savefig('figures/optimitzacio_panells.png')
plt.show()

print(f"Resultat: El nombre òptim és {num_optim} panells.")