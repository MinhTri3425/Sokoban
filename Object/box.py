import Assets
import pygame.sprite
from Layer import Layer

class Box(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        self._layer = Layer.BOX
        self.image = Assets.get_sprites("box")
        if self.image is None:
            raise ValueError("Không tìm thấy sprite cho 'box'")
        self.rect = self.image.get_rect(topleft=(x, y))
        super().__init__(*groups)