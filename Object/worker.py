import Assets
import pygame.sprite
from Layer import Layer

class Worker(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        self._layer = Layer.WORKER
        self.image = Assets.get_sprites("worker")
        if self.image is None:
            raise ValueError("Không tìm thấy sprite cho 'worker'")
        self.rect = self.image.get_rect(topleft=(x, y))
        super().__init__(*groups)