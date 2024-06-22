"""

Za crtanje totalno nebitno za projekat

"""

import math
import numpy as np
import matplotlib.pyplot as plt

NEGLIBILE_DEGREES = 5

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8))

x_data, y_data, z_data = [], [], []
mx_data, my_data, mz_data = [], [], []
az_data, alt_data = [], []
angle_data = []


line_x, = ax1.plot([], [], 'r-', label='Accel X')
line_y, = ax1.plot([], [], 'g-', label='Accel Y')
line_z, = ax1.plot([], [], 'b-', label='Accel Z')

line_mx, = ax2.plot([], [], 'c-', label='Mag X')
line_my, = ax2.plot([], [], 'm-', label='Mag Y')
line_mz, = ax2.plot([], [], 'y-', label='Mag Z')

line_az, = ax3.plot([], [], 'k-', label='Azimuth')
line_alt, = ax3.plot([], [], 'r-', label='Altitude')

ax4 = plt.subplot(2, 2, 4, projection='polar')
polar_line, = ax4.plot([], [], 'bo', label='Angle')
ax4.set_ylim(0, NEGLIBILE_DEGREES)

for ax in (ax1, ax2, ax3):
    ax.set_xlim(0, 100)

ax1.set_ylim(-20, 20)
ax2.set_ylim(-100, 100)
ax3.set_ylim(-90, 360)

ax1.set_ylabel('Acceleration')
ax2.set_ylabel('Magnetic Field')
ax3.set_ylabel('Angle')
ax3.set_xlabel('Time')

ax1.legend()
ax2.legend()
ax3.legend()


def init():
    line_x.set_data([], [])
    line_y.set_data([], [])
    line_z.set_data([], [])
    line_mx.set_data([], [])
    line_my.set_data([], [])
    line_mz.set_data([], [])
    line_az.set_data([], [])
    line_alt.set_data([], [])
    polar_line.set_data([], [])
    return line_x, line_y, line_z, line_mx, line_my, line_mz, line_az, line_alt, polar_line

def update(frame):
    line_x.set_data(range(len(x_data)), x_data)
    line_y.set_data(range(len(y_data)), y_data)
    line_z.set_data(range(len(z_data)), z_data)

    line_mx.set_data(range(len(mx_data)), mx_data)
    line_my.set_data(range(len(my_data)), my_data)
    line_mz.set_data(range(len(mz_data)), mz_data)

    line_az.set_data(range(len(az_data)), az_data)
    line_alt.set_data(range(len(alt_data)), alt_data)

    if angle_data:
        angles, lengths = zip(*angle_data)
        polar_line.set_data(angles, lengths)
    else:
        polar_line.set_data([], [])

    return line_x, line_y, line_z, line_mx, line_my, line_mz, line_az, line_alt, polar_line
