
import time
from powermeter import Powermeter as PM


import matplotlib.pyplot as plt
import matplotlib.animation


"""Powermeter variables"""
unit='dBm'
wavelength=1550
#Alice (tele) powermeters 10/03/20:
PMa = PM('PM100USB', serial='P2008115')
PMb = PM('PM100USB', serial='P2010371') 
PMc = PM('PM100USB', serial='P2003683') 
#PMd = PM('PM100USB', serial='P2007347')
#Charlie powermeters 10/03/20:
PMe = PM('PM100USB', serial='P2005653')
PMf = PM('PM100USB', serial='P2010372') 
PMg = PM('PM100USB', serial='P2008116') 
PMh = PM('PM100USB', serial='P2007346')

t = []
x = []

fig, ax = plt.subplots()
h = ax.axis([0,10,-1,1])
l, = ax.plot([],[])

def animate(i,t,x):
    while i<=10:
        t.append(time.time())
        x.append(PMh.measure())
        l.set_data(t[:i], x[:i])
        ax.clear()
        ax.plot(t,x)

ani = matplotlib.animation.FuncAnimation(fig, animate,fargs=(t,x), interval=1000)
plt.show()