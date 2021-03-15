def SineSq(x,amp,freq,phi_0,y_off):
    return amp*np.sin(freq*x+phi_0)**2+y_off