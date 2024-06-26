from machine import SPI, Pin, I2C
from mqtt_connection import MQTTCONN
from image_holder import Image_holder
from rotary import Rotary
from orientation import *
from bmm150 import BMM150
from bma2x2 import BMA2X2
from data import *
import display_driver_utils
import usys as sys
import lvgl as lv
import ili9xxx
import math
import time


target = 0 # ID planete
mode = 0 # Mod rada
target_degrees = (0, 0) # Koordinate planete za prikaz
target_radians = (0, 0) # Koordinate planete za racunanje

update_screen_timer = Timer() # Timer za azuriranje ekrana

# I2C za senzore
i2c = I2C(id=I2C_ID, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=I2C_FREQ)
print(i2c.scan())

# SPI za displej i ili9341 driver za LVGL
spi = SPI(SPI_ID, baudrate=SPI_BAUDRATE, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
drv = ili9xxx.Ili9341(spi=spi, dc=DISPLAY_DC, cs=DISPLAY_CS, rst=DISPLAY_RST)

######################## MENU SCREEN ################################

lv.init()
menu_screen = lv.obj()
unos_label = lv.label(menu_screen)

# Obavijest o povezivanju
unos_label.set_text("Povezivanje sa internetom i brokerom...")
unos_label.align(lv.ALIGN.CENTER, 0, 0)

lv.screen_load(menu_screen)

######################################################################

# Konekcija na WiFi i MQTT
mqtt = MQTTCONN(SSID, PASSWORD)

# Obavijest o uspjesnoj konekciji
unos_label.set_text("Konekcija uspjesna")
lv.task_handler()

######################## ORIENTING SCREEN ################################

orienting_screen = lv.obj()
orienting_screen.set_style_bg_color(lv.color_hex(BACKGROUND_COLOR_BLUE), 0)

current_coords_label = lv.label(orienting_screen)
current_coords_label.set_text("0, 0")

target_coords_label = lv.label(orienting_screen)
target_coords_label.set_text("0, 0")
target_coords_label.align(lv.ALIGN.TOP_RIGHT, 0, 0)

large_circle = lv.obj(orienting_screen)
large_circle.set_size(LARGE_CIRCLE_RADIUS * 2, LARGE_CIRCLE_RADIUS * 2)
large_circle.align(lv.ALIGN.CENTER, 0, 0)
large_circle.set_style_radius(LARGE_CIRCLE_RADIUS, 0)
large_circle.set_style_bg_color(lv.color_black(), 0)
large_circle.set_style_border_color(lv.color_black(), 0)
large_circle.set_style_border_width(2, 0)

############################################################################

# Cuva sliku planete
image = Image_holder(orienting_screen)


acc = BMA2X2(i2c) # Akcelerometar
mag = BMM150(i2c) # Magnetometar

orient = Orientation(acc, mag) # Klasa za orijentaciju

# Funkcija za azuriranje ekrana
def update_screen(t):
    global target_radians
    
    current_azimuth = orient.get_azimuth()
    current_altitude = orient.get_altitude()
    
    rad, distance = orient.get_directions(
        current_azimuth, current_altitude, target_radians
    )
    
    # Postavlja sliku na osnovu ugla i distance
    # Distanca se mnozi sa PIXEL_PER_DEGREE kako bi se dobila udaljenost u pikselima
    image.move_image(rad, distance * PIXEL_PER_DEGREE)
    
    # Auriranje koordinata koje se prikazuju
    azimuth = round(math.degrees(current_azimuth))
    altitude = round(math.degrees(current_altitude))
    current_coords_label.set_text(f"Az, Alt: {azimuth}, {altitude}")
    lv.task_handler()
    
def encoder_click_handler(t):
    global last_interrupt_time, target, targets, mode, mqtt, target_radians, target_degrees, image, update_screen_timer, orient
    global menu_screen, orienting_screen, r_encoder, current_coords_label
    
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_interrupt_time) > DEBOUNCE_TIME_MS:
        last_interrupt_time = current_time
        if mode == 0:
            # Postavi id ciljane planete
            target = r_encoder.get_target()
            
            # Ucitaj sliku
            image.load_image(targets[target])
            lv.screen_load(orienting_screen)
            
            # Dobavi koordinate
            mqtt.request(target)
            target_degrees = mqtt.get_coordinates()
            target_radians = (math.radians(target_degrees[0]), math.radians(target_degrees[1]))
            target_coords_label.set_text(f"{targets[target]}: {target_degrees[0]}, {target_degrees[1]}")
            
            # Pokreni tajmere za azuriranje ekrana i citanje 
            update_screen_timer.init(period=300, callback=update_screen)
            orient.start_reading(period=100)
            
            # Ukloni handler za rotaciju, LED ostaje fiksna
            r_encoder.disable_rotation_handler()
            
            # Promijeni mod
            mode = 1
        else:
            # Ukloni sliku iz memorije
            image.remove_image()
            
            # Deinicijaliziraj tajmere
            orient.end_reading()
            update_screen_timer.deinit()
            
            # Pokreni rotaciju na enkoderu
            r_encoder.enable_rotation_handler()
            
            # Učitaj meni
            lv.screen_load(menu_screen)
            mode = 0

# Handler za kalibraciju
def start_calibration(t):
    global mag

    # Ukoliko je u modu 1, prebaci na meni
    if mode == 1:
        image.remove_image()
        orient.end_reading()
        update_screen_timer.deinit()            
        lv.screen_load(menu_screen)

    r_encoder.disable_rotation_handler()            

    unos_label.set_text("Kalibracija magnetometra...")
    lv.task_handler()
    mag.calibrate(samples=600, delay=100)
    lv.task_handler()

    unos_label.set_text("Kalibracija zavrsena")
    lv.task_handler()
    time.sleep(1)
    unos_label.set_text("Odaberite planetu")
    lv.task_handler()
    r_encoder.enable_rotation_handler()

unos_label.set_text("Odaberite planetu")
lv.task_handler()

# Taster za kalibraciju
calibration_button = Pin(3, Pin.IN).irq(trigger=Pin.IRQ_RISING, handler=start_calibration)

# Inicijalizacija rotacionog enkodera
r_encoder = Rotary(CLK_PIN, DT_PIN, SW_PIN, encoder_click_handler)
r_encoder.enable_rotation_handler()
r_encoder.enable_click_handler()

while True:
    pass