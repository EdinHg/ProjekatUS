"""

Za slanje podataka o planetama

"""
import paho.mqtt.client as mqtt
import ephem
from time import gmtime, strftime
from datetime import datetime

planete = [
    ephem.Mercury(),
    ephem.Venus(),
    ephem.Mars(),
    ephem.Jupiter(),
    ephem.Saturn(),
    ephem.Uranus(),
    ephem.Neptune(),
#    ephem.Pluto(), ne ti
    ephem.Sun() # Nije planeta znam, ima 8 ledica na pi pico taman, stfu
]


longituda = '18.396463242986567'
latituda = '43.856281349667505'
mars = ephem.Mars()

observer = ephem.Observer()
observer.lon = longituda
observer.lat = latituda
observer.date = strftime("%Y/%m/%d %H:%M:%S", gmtime())


broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'edinhg/request'  
topic_pub = 'edinhg/response/' 

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    text = msg.payload.decode()
    print(f"Message received on topic {msg.topic}: {text}")


    try:
        planeta_id = int(text)
        observer.date = strftime("%Y/%m/%d %H:%M:%S", gmtime())
        planeta = planete[planeta_id]
        planeta.compute(observer)
        response = str(planeta.az) + ", " + str(planeta.alt)
        client.publish(topic_pub + planeta.name, response)
        print(f"Response sent to topic: {topic_pub + planeta.name}")

    except Exception as e: print(e)

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)

client.loop_forever()