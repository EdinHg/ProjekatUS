from machine import Pin, Timer
import time
from rotary import Rotary

CLK_PIN = 0
DT_PIN = 1
SW_PIN = 2

r_encoder = Rotary(CLK_PIN, DT_PIN, SW_PIN)
r_encoder.enable_handlers()

while True:
    pass