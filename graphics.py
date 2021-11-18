import matplotlib.pyplot as plt
import numpy as np
t = []
v = []
r = []
def graphic(satellite_v, satellite_r,  time):
    t.append(time)
    v.append(satellite_v)
    r.append(satellite_r)
def draw_garphic():

    #subplot 1
    sp = plt.subplot(221)
    plt.plot(r, v)
    plt.title('v(r)')

    #subplot 2
    sp = plt.subplot(222)
    plt.plot(t, v)
    plt.title('v(t)')

    #subplot 3
    sp = plt.subplot(223)
    plt.plot(t, r)
    plt.title('r(t)')

    plt.show()