import os 
import pygame

Sprites = {}
def load_sprites():
     path = os.path.join("Assets", "Sprites")
     
     if not os.path.exists(path):
          print(f"Thư mục {path} không tồn tại ")
          return
     
     for file in os.listdir(path):
          try:
               Sp_name = os.path.splitext(file)[0]
               Sprites[Sp_name] = pygame.image.load(os.path.join(path,file))
          except pygame.error as err:
               print(f"Không thể load ảnh {file} : {err}")

def get_sprites(name):
     Sprite = Sprites.get(name)
     if Sprite is None:
          print(f"Không tìm thấy sprite: {name}")
     return Sprite