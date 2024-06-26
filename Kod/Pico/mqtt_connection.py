from umqtt.robust import MQTTClient
import network
import time
import ujson

class MQTTCONN():
    
    # Inicijalizacija klase na osnovu SSID-a i passworda
    # Konekcija na WiFi i MQTT
    def __init__(self, SSID, password):
    
        self.target_azimuth = 0
        self.target_altitude = 0
        self.nic = network.WLAN(network.STA_IF)
        self.nic.active(True)
        self.nic.connect(SSID, password)

        print("Povezivanje")
        while not self.nic.isconnected():
            print(".")
            time.sleep(1)
        print("Povezano")

        self.conn = MQTTClient(client_id='n23doj2pdj', server='broker.emqx.io', user='', password='', port=1883)
        self.conn.connect()
        self.conn.set_callback(self._response)
        self.conn.subscribe(b"planet_tracker/response/#")
        print("Konekcija sa MQTT brokerom uspostavljena")    

    # Funkcija za pretplatu
    def _response(self, topic, msg):  
        print('Received message:', topic, msg)
        data = ujson.loads(msg)
        
        self.target_azimuth = data.get("az")
        self.target_altitude = data.get("alt")

    # Funkcija za slanje zahtjeva
    def request(self, id):
        self.conn.publish(b'planet_tracker/request', str(id))
        print("Request sent")
        self.conn.wait_msg()
        
    # Vraca dobaavljenje koordinate
    def get_coordinates(self):
        return self.target_azimuth, self.target_altitude


    
    