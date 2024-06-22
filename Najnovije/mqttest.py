from umqtt.robust import MQTTClient
from mqtt_stuff import MQTTCONN
import network
import time
import ujson


conn = MQTTCONN("Zivojevic", "DDFLDDFL")

for i in range(8):
    conn.request(i)
    print(conn.get_coordinates())