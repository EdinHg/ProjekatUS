import display_driver_utils
import usys as sys
import lvgl as lv
import math


class Image_holder:
    
    # Inicijalizacija klase na osnovu ekrana
    def __init__(self, screen):
        sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419
        self.screen = screen
        self.image = None
        self.x = 0
        self.y = 0
        
    # Ucitavanje slike na osnovu imena file-a
    def load_image(self, image_name):
        try:
            script_path = __file__[:__file__.rfind('/')] if __file__.find('/') >= 0 else '.'
        except NameError: 
            script_path = ''
        
        file_path = f'{script_path}/{image_name}.png'

        with open(file_path, 'rb') as f:
            png_data = f.read()

        png_image_dsc = lv.image_dsc_t({
            'data_size': len(png_data),
            'data': png_data 
        })
        
        image = lv.image(self.screen)
        image.set_src(png_image_dsc)
        image.set_align(lv.ALIGN.CENTER)
        image.set_pos(self.x, self.y)
        
        self.image = image
        
    # Pomjeranje slike na osnovu ugla i distance u odnosu na centar
    def move_image(self, rad, distance):
        if distance > 100:
            distance = 100
        
        x = int(distance * math.cos(rad))
        y = int(distance * math.sin(rad))

        self.image.set_pos(x, y)
        
    # Brisnje slike, praznjenje cache-a
    def remove_image(self):
        self.image.delete()