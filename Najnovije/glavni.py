from machine import SPI, Pin, I2C
from mqtt_stuff import MQTTCONN
from image import Image_holder
import display_driver_utils
from rotary import Rotary
from orientation import *
from bmm150 import BMM150
from bma2x2 import BMA2X2
import usys as sys
import lvgl as lv
import ili9xxx
import math
import time

mqtt = MQTTCONN("Yo", "00000000")

i2c = I2C(id=1, sda=Pin(26), scl=Pin(27), freq=100000)
print(i2c.scan())

spi = SPI(0, baudrate=2_000_000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
drv = ili9xxx.Ili9341(spi=spi, dc=15, cs=17, rst=20)

PIXEL_PER_DEGREE = 50

last_interrupt_time = 0
debounce_time = 200

CLK_PIN = 0
DT_PIN = 1
SW_PIN = 2

targets = [
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "sun"
]

target = 0
mode = 0
target_radians = (0, 0)

update_screen_timer = Timer()

lv.init()

######################## ORIENTING SCREEN ################################

orienting_screen = lv.obj()
orienting_screen.set_style_bg_color(lv.color_hex(0x0000FF), 0)

current_coords_label = lv.label(orienting_screen)
current_coords_label.set_text("0, 0")

target_coords_label = lv.label(orienting_screen)
target_coords_label.set_text("0, 0")
target_coords_label.align(lv.ALIGN.TOP_RIGHT, 0, 0)

large_circle_radius = 100

large_circle = lv.obj(orienting_screen)
large_circle.set_size(large_circle_radius * 2, large_circle_radius * 2)
large_circle.align(lv.ALIGN.CENTER, 0, 0)
large_circle.set_style_radius(large_circle_radius, 0)
large_circle.set_style_bg_color(lv.color_black(), 0)
large_circle.set_style_border_color(lv.color_black(), 0)
large_circle.set_style_border_width(2, 0)

image = Image_holder(orienting_screen)

######################## MENU SCREEN ################################

menu_screen = lv.obj()
unos_label = lv.label(menu_screen)
unos_label.set_text("Odaberite planetu")
unos_label.align(lv.ALIGN.CENTER, 0, 0)

######################################################################

time.sleep(2)

acc = BMA2X2(i2c)
mag = BMM150(i2c)

orient = Orientation(acc, mag)

def update_screen(t):
    global target_radians
    
    current_azimuth = orient.get_azimuth()
    current_latitude = orient.get_latitude()
    
    rad, distance = orient.upute(
        current_azimuth, current_latitude, target_radians[0], target_radians[1]
    )
    
    image.move_image(rad, distance * PIXEL_PER_DEGREE)
    
    azimuth = round(math.degrees(current_azimuth))
    latitude = round(math.degrees(current_latitude))
    
    current_coords_label.set_text(f"Az, Lat: {azimuth}, {latitude}")
    lv.task_handler()
    
lv.screen_load(menu_screen)
    
def encoder_click_handler(t):
    global last_interrupt_time, target, targets, mode, mqtt, target_radians, image, update_screen_timer, orient
    global menu_screen, orienting_screen, r_encoder, current_coords_label
    
    
    current_time = time.ticks_ms()
        
    if time.ticks_diff(current_time, last_interrupt_time) > debounce_time:
        last_interrupt_time = current_time
        if mode == 0:
            # Set target
            target = r_encoder.get_target()

            # Load the planet image and orientation screen
            image.load_image(targets[target])
            lv.screen_load(orienting_screen)
            
            # Fetch initial coordinates from mqtt and set labels
            mqtt.request(target)
            azimuth, latitude = mqtt.get_coordinates()
            target_radians = (math.radians(azimuth), math.radians(latitude))
            target_coords_label.set_text(f"{targets[target]}: {azimuth}, {latitude}") 
            
            # Start timers for orientation
            update_screen_timer.init(period=200, callback=update_screen)
            orient.start_reading(period=100)
            
            # Disable rotation on encoder, current LED stays fixed
            r_encoder.disable_rotation_handler()
            
            # Change mode
            mode = 1
        else:
            # Remove image from memory
            image.remove_image()
            
            # Deinitialize timers
            orient.end_reading()
            update_screen_timer.deinit()
            
            # Enable rotation on encoder
            r_encoder.enable_rotation_handler()
            
            # Load menu screen and change mode
            lv.screen_load(menu_screen)
            mode = 0


r_encoder = Rotary(CLK_PIN, DT_PIN, SW_PIN, encoder_click_handler)
r_encoder.enable_rotation_handler()
r_encoder.enable_click_handler()

while True:
    pass