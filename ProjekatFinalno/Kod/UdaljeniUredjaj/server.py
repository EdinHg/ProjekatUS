import paho.mqtt.client as mqtt
import ephem
from time import gmtime, strftime
from datetime import datetime
import ujson

# Lista planeta
planete = [
    ephem.Mercury(),
    ephem.Venus(),
    ephem.Mars(),
    ephem.Jupiter(),
    ephem.Saturn(),
    ephem.Uranus(),
    ephem.Neptune(),
    ephem.Sun()
]


# Kooridnate za kampus ETF-a
longituda = '18.396463242986567'
latituda = '43.856281349667505'

# Postavljanje posmatraca
observer = ephem.Observer()
observer.lon = longituda
observer.lat = latituda
observer.date = strftime("%Y/%m/%d %H:%M:%S", gmtime())


<<<<<<<< HEAD:ProjekatFinalno/Kod/UdaljeniUredjaj/server.py
# Podaci za MQTT
========
>>>>>>>> 6fcb6a50c8781d78ffe40a7d7b4577b415b03ce7:ZaPhone/server.py
broker = 'broker.emqx.io'
port = 1883
topic_sub = 'planet_tracker/request'  
topic_pub = 'planet_tracker/response/' 


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic_sub)

# Obrada zahtjeva
def on_message(client, userdata, msg):
    text = msg.payload.decode()
    print(f"Message received on topic {msg.topic}: {text}")

    try:
        planeta_id = int(text)
        observer.date = strftime("%Y/%m/%d %H:%M:%S", gmtime())

<<<<<<<< HEAD:ProjekatFinalno/Kod/UdaljeniUredjaj/server.py
========

>>>>>>>> 6fcb6a50c8781d78ffe40a7d7b4577b415b03ce7:ZaPhone/server.py
        planeta = planete[planeta_id]
        planeta.compute(observer)
        
        az = str(planeta.az).split(":")
        alt = str(planeta.alt).split(":")
<<<<<<<< HEAD:ProjekatFinalno/Kod/UdaljeniUredjaj/server.py
        data = {'az': int(az[0]), 'alt': int(alt[0])}
========
        data = {'az': int(az[0]), 'lat': int(alt[0])}
>>>>>>>> 6fcb6a50c8781d78ffe40a7d7b4577b415b03ce7:ZaPhone/server.py
        
        client.publish(topic_pub + planeta.name, ujson.dumps(data))
        print(f"Response sent to topic: {topic_pub + planeta.name}")

    except Exception as e: print(e)

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)

client.loop_forever()