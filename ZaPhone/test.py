"""

Za koristenje potrebna aplikacija na telefonu https://sensorstream-imu-gps.en.softonic.com/android?ex=RAMP-2046.2
U aplikaciji unijeti IP adresu racunara i port 5555, odabrati UDP

"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import socket
import threading
import math
from plotanje import *

# Ovdje kooridnate cilja, lafo
target = [ 87, -54 ]

def filter(old_vector, new_vector, ratio):
    return [ old_vector[i] * (1 - ratio) + new_vector[i] * ratio for i in range(3) ]

HOST = ''  
PORT = 5555        

filtered_acc = [0, 0, 0]
filtered_mag = [0, 0, 0]

# 172.16.9.49

def upute(target, current):
    x_delta = target[0] - current[0]
    x_delta = (x_delta + 180) % 360 - 180
    y_delta = target[1] - current[1]

    angle = math.degrees(math.atan2(y_delta, x_delta))

    angle_length = math.degrees(
        math.acos(math.cos(math.radians(target[1])) * math.cos(math.radians(current[1])) * math.cos(math.radians(target[0]) -
               math.radians(current[0])) + math.sin(math.radians(target[1])) * math.sin(math.radians(current[1])))
    )

    print("Ugao zakretanja: na ekranu: ", angle)
    print("Ugao udaljenosti: ", angle_length)

                         
    return angle, angle_length

def socket_listener():
    global filtered_acc
    global filtered_mag 
    global pitch_bias
    global roll_bias
    global screen

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind((HOST, PORT))

        while True:
            try:
                message, address = s.recvfrom(1000)
                message = str(message).split(',')

                if (len(message) > 9):
                    if len(x_data) > 100:  
                        x_data.pop(0)
                        y_data.pop(0)
                        z_data.pop(0)
                        mx_data.pop(0)
                        my_data.pop(0)
                        mz_data.pop(0)
                        az_data.pop(0)
                        alt_data.pop(0)

                    if len(angle_data) > 5:
                        angle_data.pop(0)

                    new_acc = [ float(item.strip().strip("'")) for item in message[2:5] ]
                    new_mag = [ float(item.strip().strip("'")) for item in message[10:13] ]

                    filtered_acc = filter(filtered_acc, new_acc, 0.1)
                    filtered_mag = filter(filtered_mag, new_mag, 0.1)

                    x_data.append(filtered_acc[0])
                    y_data.append(filtered_acc[1])
                    z_data.append(filtered_acc[2])
                    
                    mx_data.append(filtered_mag[0])
                    my_data.append(filtered_mag[1])
                    mz_data.append(filtered_mag[2])

                    G = np.array(filtered_acc)
                    M = np.array(filtered_mag)
                    D = -G

                    # G = G / np.linalg.norm(G)
                    # M = M / np.linalg.norm(M)


                    E = np.cross(D, M)
                    E = E / np.linalg.norm(E)

                    N = np.cross(E, D)
                    N = N / np.linalg.norm(N)

                    
                    altitude = math.asin(-G[2] / np.linalg.norm(G))

                    X = np.array([1, 0, 0])
                    Y = np.array([0, 1, 0])
                    Z = np.array([0, 0, 1])

                    # Ugao izmedju xy ravnine i N
                    # Katastrofalna preciznost

                    # Z_perp = math.sin(-altitude) * G
                    # Z_proj = -Z - Z_perp
                    # Z_proj = Z_proj / np.linalg.norm(Z_proj)

                    # azimuth = math.acos(np.dot(N, Z_proj))
                    # cross = np.cross(N, Z_proj)

                    # if np.dot(cross, G) > 0:
                    #     azimuth = 2 * math.pi - azimuth


                    # Ugao izmedju y ose i N
                    # Precizno u bobu, netacno par stepeni vjr. zbog pravog vs. magnetnog sjevera

                    azimuth = math.acos(np.dot(N, Y))
                    cross = np.cross(N, Y) 
                    
                    if np.dot(cross, G) > 0:
                        azimuth = 2 * math.pi - azimuth
                    azimuth = (azimuth + math.pi / 2) % (2 * math.pi)
                    
                    print("Target: ", target)
                    print("Azimuth: ", round(math.degrees(azimuth)))
                    print("Latitude: ", round(math.degrees(altitude)))
                    
                    angle, length = upute(target, [math.degrees(azimuth), math.degrees(altitude)])
                    angle_data.append((math.radians(angle), min(length, NEGLIBILE_DEGREES)))
                    
                    az_data.append(math.degrees(azimuth))
                    alt_data.append(math.degrees(altitude))

                    print()
                    print()
            except Exception as e: print(e)

socket_thread = threading.Thread(target=socket_listener)
socket_thread.daemon = True 
socket_thread.start()

ani = animation.FuncAnimation(fig, update, init_func=init, blit=True, interval=100)
plt.show()