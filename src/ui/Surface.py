from pygame import Surface as PygameSurface

from pygame.draw import *
from pygame.font import Font as PygameFont
from pygame.display import flip
from pygame.mouse import get_pos as get_mouse_position


class Surface:

    def __init__(self, screen, size, position):
        self.screen = screen
        self.size = size
        self.position = position
        self.surf = PygameSurface(size)

    def update(self):
        """Обновление поверхности"""
        pass

    def blit(self):
        """Наложение всех деталей на поверхность"""
        self.screen.blit(self.surf, self.position)
