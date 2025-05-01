import pygame
import os

class SokobanGUISound:
    def __init__(self, gui_init):
        self.gui_init = gui_init
        self.load_sounds()
        self.play_background_music()

    def load_sounds(self):
        try:
            if not os.path.exists("Sound"):
                os.makedirs("Sound")
            self.background_music = pygame.mixer.Sound(os.path.join("Sound", "backgroud.mp3"))
            self.background_music.set_volume(0.8)
            self.victory_sound = pygame.mixer.Sound(os.path.join("Sound", "victory.mp3"))
            self.victory_sound.set_volume(1.0)
            self.move_sound = pygame.mixer.Sound(os.path.join("Sound", "move.wav"))
            self.move_sound.set_volume(0.08)
            print("All sounds loaded successfully")
        except Exception as e:
            print(f"Error loading sounds: {e}")
            self.background_music = None
            self.victory_sound = None
            self.move_sound = None

    def play_background_music(self):
        if self.background_music:
            try:
                pygame.mixer.Channel(0).play(self.background_music, loops=-1)
            except Exception as e:
                print(f"Error playing background music: {e}")

    def play_victory_sound(self):
        if self.victory_sound:
            try:
                pygame.mixer.Channel(1).play(self.victory_sound)
            except Exception as e:
                print(f"Error playing victory sound: {e}")

    def play_move_sound(self):
        if self.move_sound:
            try:
                pygame.mixer.Channel(2).play(self.move_sound)
            except Exception as e:
                print(f"Error playing move sound: {e}")