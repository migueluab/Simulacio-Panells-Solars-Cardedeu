import numpy as np
import matplotlib as plt

R = 2 * np.pi /360
N_i = 365
N = 1
Lat = 41.63 * R
for i in range(0,N_i):
    Delta = R *23.45 * np.sin((360*(N+284)*R/365))
    w_s = np.arccos(-np.tan(Lat)*np.tan(Delta))
    H = 2 * w_s /(15 * R)
    print('Dia',N,H, 'hores')
    N = N + 1
