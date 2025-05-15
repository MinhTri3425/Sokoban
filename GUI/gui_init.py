import pygame
import os
from Game import Game
from Assets import load_sprites

class SokobanGUIInit:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Sokoban Game - Nintendo Switch Edition")
        load_sprites()

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.LIGHT_GRAY = (230, 230, 230)
        self.GREEN = (0, 200, 0)
        self.RED = (200, 0, 0)
        self.BLUE = (0, 0, 200)
        self.DARK_BLUE = (0, 0, 150)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (128, 0, 128)

        # Nintendo Switch colors
        self.SWITCH_LEFT_COLOR = (0, 120, 255)
        self.SWITCH_RIGHT_COLOR = (255, 0, 0)
        self.SWITCH_BODY_COLOR = (20, 20, 20)
        self.SWITCH_SCREEN_COLOR = (40, 40, 40)
        self.SWITCH_LEFT_SHADOW = (0, 80, 180)
        self.SWITCH_RIGHT_SHADOW = (180, 0, 0)
        self.SWITCH_LEFT_HIGHLIGHT = (80, 170, 255)
        self.SWITCH_RIGHT_HIGHLIGHT = (255, 80, 80)
        self.BACKGROUND_COLOR = (0, 0, 0)

        # Dimensions
        self.border_thickness = 80
        self.ui_height = 30
        self.top_border_extension = self.ui_height
        self.side_extension = 80
        self.switch_side_width = 230
        self.screen_width = 576
        self.screen_height = 576
        self.extended_screen_width = self.screen_width + self.side_extension * 2
        self.total_width = self.extended_screen_width + self.switch_side_width * 2
        self.total_height = self.screen_height + self.ui_height + self.top_border_extension
        self.bg_padding = 40
        self.window_width = self.total_width + self.bg_padding * 2
        self.window_height = self.total_height + self.bg_padding * 2
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.white_border_thickness = 2

        # Game state
        self.current_level = 1
        self.max_level = self.count_levels()
        self.move_count = 0
        self.game = None
        self.dock_list = []
        self.game_completed = False
        self.solving = False
        self.solution_path = []
        self.solution_index = 0
        self.solution_delay = 300
        self.last_solution_move_time = 0
        self.show_congrats = False
        self.congrats_alpha = 0
        self.congrats_fade_in = True
        self.pending_undo = 0

        # Algorithm comparison
        self.comparing = False
        self.comparison_results = {}
        self.comparison_start_time = 0
        self.comparison_duration = 0

        # Animation variables
        self.animation_in_progress = False
        self.animation_start_time = 0
        self.animation_duration = 200
        self.animation_start_pos = (0, 0)
        self.animation_end_pos = (0, 0)
        self.animation_direction = (0, 0)
        self.animation_box_start = None
        self.animation_box_end = None
        self.undo_animation_in_progress = False
        self.undo_animation_start_time = 0
        self.undo_animation_duration = 200
        self.undo_animation_start_pos = (0, 0)
        self.undo_animation_end_pos = (0, 0)
        self.undo_animation_box_start = None
        self.undo_animation_box_end = None
        self.undo_previous_state = None
        self.undo_current_state = None

        # Fonts
        font_path = pygame.font.match_font("arial")
        self.font = pygame.font.Font(font_path, 24)
        self.small_font = pygame.font.Font(font_path, 18)
        self.title_font = pygame.font.Font(font_path, 32)
        self.congrats_font = pygame.font.Font(font_path, 36)

        # Confetti
        self.confetti_colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (255, 165, 0), (128, 0, 128)
        ]
        self.confetti = []

        # Initialize game
        self.load_level(self.current_level)
        self.clock = pygame.time.Clock()

    def count_levels(self):
        count = 0
        while os.path.exists(f"Level/level{count + 1}.txt"):
            count += 1
        return max(1, count)

    def load_level(self, level_number):
        try:
            with open(f"Level/level{level_number}.txt") as f:
                level_data = [list(line.strip('\n')) for line in f]
            self.game = Game(level_data, [])
            self.dock_list = self.game.listDock()
            self.move_count = 0
            self.game_completed = False
            self.solving = False
            self.solution_path = []
            self.solution_index = 0
            self.show_congrats = False
            self.congrats_alpha = 0
            self.confetti = []
        except FileNotFoundError:
            print(f"Level {level_number} not found")
