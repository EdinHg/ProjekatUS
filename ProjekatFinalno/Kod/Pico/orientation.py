from machine import Timer
import math 
import time


class Orientation:

    # Inicijalizacija klase na osnovu BMX055 senzora
    def __init__(self, acc, mag):
        self.PI = math.pi
        self.PI2 = self.PI / 2
        self.TWOPI = 2 * self.PI
        self.mag = mag
        self.acc = acc
        self.mag_trust = 0.1
        self.acc_trust = 0.1
        self.acc_vals = self.acc.xyz()
        self.mag_vals = self.mag.xyz()
        self.X = [ 1, 0, 0 ]
        self.Y = [ 0, 1, 0 ]
        self.Z = [ 0, 0, 1 ]
        self.reading_timer = Timer()

    # Funkcija koja normalizuje vektor
    def _normalize(self, vector):
        norm = math.sqrt(sum([ item**2 for item in vector ]))
        return [ item / norm for item in vector ]

    # Funkcija koja racuna vektorski proizvod
    def _cross_product(self, a, b):
        return [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        ]

    # Funkcija koja racuna skalarni proizvod
    def _dot_product(self, a, b):
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    
    # Funkcija koja filtrira nove vrijednosti senzora
    def _low_pass_filter(self, old_vector, new_vector, ratio):
        return [ 
            old_vector[i] * (1 - ratio) + new_vector[i] * ratio for i in range(3) 
        ]
    
    # Funkcija koja azurira vrijednosti senzora
    def _update_vals(self, t):
        new_acc = self.acc.xyz()
        new_mag = self.mag.xyz()
        
        self.acc_vals = self._low_pass_filter(self.acc_vals, new_acc, self.acc_trust)
        self.mag_vals = self._low_pass_filter(self.mag_vals, new_mag, self.mag_trust)
    
    # Funkcija koja vraca istocni vektor
    def _get_east(self, D):
        return self._cross_product(D, self.mag_vals)
    
    # Funkcija koja vraca sjeverni vektor
    def _get_north(self):
        D = [ -item for item in self.acc_vals ]
        return self._cross_product(self._get_east(D), D)

    # Funkcija koja vraca azimut
    def get_azimuth(self):
        N = self._get_north()
        
        azimuth = math.acos(self._dot_product(N, self.Y))
        cross = self._cross_product(N, self.Y) 
        
        # Ako se rezultanti vektor istog smjera kao acc, onda je ugao 2PI - ugao
        if self._dot_product(cross, self.acc_vals) > 0:
            azimuth = self.TWOPI - azimuth
            
        # Ovo je bio ugao u odnosu na Y osu, treba dodati PI/2
        azimuth = (azimuth + self.PI2) % self.TWOPI

        return azimuth

    # Funkcija koja vraca altitudu
    def get_altitude(self):
        g_z = self.acc_vals[2]
        if abs(g_z) >= 1:
            return math.copysign(self.PI2, -g_z)
        else:
            return math.asin(-g_z)
        
    # Funkcija koja postavlja povjerenje u senzor magnetnog polja
    def set_mag_trust(self, trust):
        self.mag_trust = trust
        
    # Funkcija koja postavlja povjerenje u senzor akceleracije
    def set_acc_trust(self, trust):
        self.acc_trust = trust

    # Funkcija koja odredjuje ugao i distancu izmedju trenutne i ciljne tacke
    def get_directions(self,current_azimuth, current_altitude, target):
        x_delta = target[0] - current_azimuth
        x_delta = (x_delta + self.PI) % self.TWOPI - self.PI # Normalizacija na [-PI, PI]
        y_delta = target[1] - current_altitude

        screen_orientation_angle = math.atan2(y_delta, x_delta)

        distance_angle = math.acos(math.cos(target[1]) * math.cos(current_altitude) * math.cos(target[0] - current_azimuth) +
                      math.sin(target[1]) * math.sin(current_altitude))
        
        return screen_orientation_angle, distance_angle
    
    # Funkcija koja pokrece citanje senzora
    def start_reading(self, period=100):
        self.reading_timer.init(period=period, callback=self._update_vals)

    # Funkcija koja zavrsava citanje senzora
    def end_reading(self):
        self.reading_timer.deinit()