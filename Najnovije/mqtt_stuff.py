from umqtt.robust import MQTTClient
import network
import time
import ujson

class MQTTCONN():
    
    def __init__(self, SSID, password):
    
        self.target_azimuth = 0
        self.target_latitude = 0
        self.nic = network.WLAN(network.STA_IF)
        self.nic.active(True)
        self.nic.connect(SSID, password)

        print("Povezivanje")
        while not self.nic.isconnected():
            print(".")
            time.sleep(1)
        print("Povezano")

        self.conn = MQTTClient(client_id='EDINHG', server='broker.emqx.io', user='', password='', port=1883)
        self.conn.connect()
        self.conn.set_callback(self._response)
        self.conn.subscribe(b"edinhg/response/#")
        print("Konekcija sa MQTT brokerom uspostavljena")    

    def _response(self, topic, msg):  
        print('Received message:', topic, msg)
        data = ujson.loads(msg)
        
        self.target_azimuth = data.get("az")
        self.target_latitude = data.get("lat")

    def request(self, id):
        self.conn.publish(b'edinhg/request', str(id))
        print("Request sent")
        self.conn.wait_msg()
        
    def get_coordinates(self):
        return self.target_azimuth, self.target_latitude


    
    