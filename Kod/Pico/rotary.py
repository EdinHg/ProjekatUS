from machine import Pin
import time


class Rotary:
    
    # Inicializacija klase na osnovu pinova i click_handler-a
    def __init__(self, CLK_PIN, DT_PIN, SW_PIN, click_handler):
        self.last_interrupt_time = 0
        self.debounce_time = 200
        self.leds = [ Pin(i, Pin.OUT) for i in range(4, 12) ]
        self.target = 0
        self.leds[self.target].on()
        self.clk = Pin(CLK_PIN, Pin.IN)
        self.dt = Pin(DT_PIN, Pin.IN)
        self.sw = Pin(SW_PIN, Pin.IN)
        self.click_handler = click_handler

    # Funkcija koja upravlja rotaciom enkodera
    def _rotary_encoder_handler(self, t):
        current_time = time.ticks_ms()
        
        if time.ticks_diff(current_time, self.last_interrupt_time) > self.debounce_time:
            self.last_interrupt_time = current_time
            previous = self.target

            if self.dt.value():
                if self.target < 7:
                    self.target += 1
            else:
                if self.target > 0:
                    self.target -= 1

            self.leds[previous].off()
            self.leds[self.target].on()
    
    # Funkcije koje incijaliziraju i deinicijaliziraju handler-e
    def enable_click_handler(self):
        if (self.click_handler == None):
            print("Click handler not set")
        else:
            self.sw.irq(handler=self.click_handler, trigger=Pin.IRQ_FALLING)
    
    def enable_rotation_handler(self):
        self.clk.irq(handler=self._rotary_encoder_handler, trigger=Pin.IRQ_FALLING)
        
    def disable_click_handler(self):
        self.sw.irq(None, 0)
        
    def disable_rotation_handler(self):
        self.clk.irq(None, 0)
        
    # Funkcija koja vraca trenutni target
    def get_target(self):
        return self.target
        
        