import Assets
import pygame.sprite
from Layer import Layer

class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        self._layer = Layer.FLOOR
        self.image = Assets.get_sprites("floor")
        if self.image is None:
            raise ValueError("Không tìm thấy sprite cho 'floor'")
        self.rect = self.image.get_rect(topleft=(x, y))
        super().__init__(*groups)