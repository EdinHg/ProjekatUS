# Konstante koristene u okviru projekta

# Uspostavljanje konekcije sa MQTT klijentom
SSID = "Lab220"
PASSWORD = "lab220lozinka"

# Inicijalizacija I2C objekta
I2C_ID = 1
I2C_SDA = 26
I2C_SCL = 27
I2C_FREQ = 100000

# Inicijalizacija SPI objekta
SPI_ID = 0
SPI_BAUDRATE = 2_000_000
SPI_SCK = 18
SPI_MOSI = 19
SPI_MISO = 16

# Inicijalizacija ILI9341 objekta za upravljanje displejom
DISPLAY_DC = 15
DISPLAY_CS = 17
DISPLAY_RST = 20

# Konstante koristene u ostatku programa
LAST_INTERRUPT_TIME = 0
PIXEL_PER_DEGREE = 50
DEBOUNCE_TIME_MS = 200
CLK_PIN = 0
DT_PIN = 1
SW_PIN = 2

TARGETS = [
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "sun"
]

BACKGROUND_COLOR_BLUE = 0x0000FF
LARGE_CIRCLE_RADIUS = 100