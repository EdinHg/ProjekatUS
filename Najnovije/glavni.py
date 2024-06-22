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
from data import *

mqtt = MQTTCONN(SSID, PASSWORD)

i2c = I2C(id=I2C_ID, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=I2C_FREQ)
print(i2c.scan())

spi = SPI(SPI_ID, baudrate=SPI_BAUDRATE, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
drv = ili9xxx.Ili9341(spi=spi, dc=DISPLAY_DC, cs=DISPLAY_CS, rst=DISPLAY_RST)

last_interrupt_time = 0

target = 0
mode = 0
target_radians = (0, 0)

update_screen_timer = Timer()

lv.init()

######################## ORIENTING SCREEN ################################

orienting_screen = lv.obj()
orienting_screen.set_style_bg_color(lv.color_hex(BACKGROUND_COLOR_BLUE), 0)

current_coords_label = lv.label(orienting_screen)
current_coords_label.set_text(COORDINATES_LABEL)

target_coords_label = lv.label(orienting_screen)
target_coords_label.set_text(COORDINATES_LABEL)
target_coords_label.align(lv.ALIGN.TOP_RIGHT, 0, 0)

large_circle = lv.obj(orienting_screen)
large_circle.set_size(LARGE_CIRCLE_RADIUS * 2, LARGE_CIRCLE_RADIUS * 2)
large_circle.align(lv.ALIGN.CENTER, 0, 0)
large_circle.set_style_radius(LARGE_CIRCLE_RADIUS, 0)
large_circle.set_style_bg_color(lv.color_black(), 0)
large_circle.set_style_border_color(lv.color_black(), 0)
large_circle.set_style_border_width(2, 0)

image = Image_holder(orienting_screen)

######################## MENU SCREEN ################################

menu_screen = lv.obj()
unos_label = lv.label(menu_screen)
unos_label.set_text(MENU_SCREEN_TEXT)
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
    global last_interrupt_time, target, TARGETS, mode, mqtt, target_radians, image, update_screen_timer, orient
    global menu_screen, orienting_screen, r_encoder, current_coords_label
    
    
    current_time = time.ticks_ms()
        
    if time.ticks_diff(current_time, last_interrupt_time) > DEBOUNCE_TIME_MS:
        last_interrupt_time = current_time
        if mode == 0:
            # Set target
            target = r_encoder.get_target()

            # Load the planet image and orientation screen
            image.load_image(TARGETS[target])
            lv.screen_load(orienting_screen)
            
            # Fetch initial coordinates from mqtt and set labels
            mqtt.request(target)
            azimuth, latitude = mqtt.get_coordinates()
            target_radians = (math.radians(azimuth), math.radians(latitude))
            target_coords_label.set_text(f"{TARGETS[target]}: {azimuth}, {latitude}") 
            
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