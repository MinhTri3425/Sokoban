import Assets
import pygame.sprite
from Layer import Layer

class Dock(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        self._layer = Layer.DOCK
        self.image = Assets.get_sprite("dock")
        if self.image is None:
            raise ValueError("Không tìm thấy sprite cho 'dock'")
        self.rect = self.image.get_rect(topleft=(x, y))
        super().__init__(*groups)