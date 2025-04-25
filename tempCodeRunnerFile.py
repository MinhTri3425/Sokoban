import pygame
import sys
import os
import math
import random
from pygame.locals import *
import copy
from State import State
from solver.bfs import bfs
from solver.dfs import dfs
from solver.a_star import a_star

from Object.box import Box
from Object.box_docked import BoxDocked
from Object.floor import Floor
from Object.wall import Wall
from Object.worker import Worker
from Object.dock import Dock
from Game import Game
from Assets import load_sprites, get_sprites

class SokobanGUI:
    def __init__(self):
        pygame.init()
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
        self.SWITCH_LEFT_COLOR = (0, 120, 255)  # Blue Joy-Con
        self.SWITCH_RIGHT_COLOR = (255, 0, 0)   # Red Joy-Con
        self.SWITCH_BODY_COLOR = (20, 20, 20)   # Dark gray body
        self.SWITCH_SCREEN_COLOR = (40, 40, 40) # Screen background
        
        # Shadow colors for Joy-Cons
        self.SWITCH_LEFT_SHADOW = (0, 80, 180)  # Darker blue for shadow
        self.SWITCH_RIGHT_SHADOW = (180, 0, 0)  # Darker red for shadow
        
        # Highlight colors for Joy-Cons
        self.SWITCH_LEFT_HIGHLIGHT = (80, 170, 255)  # Lighter blue for highlights
        self.SWITCH_RIGHT_HIGHLIGHT = (255, 80, 80)  # Lighter red for highlights

        # Background color (pure black)
        self.BACKGROUND_COLOR = (0, 0, 0)  # Changed to pure black

        # Nintendo Switch dimensions
        self.border_thickness = 80
        self.ui_height = 30
        self.top_border_extension = self.ui_height
        self.side_extension = 80

        # Base dimensions
        self.switch_side_width = 230
        self.screen_width = 576
        self.screen_height = 576
        
        # Extended dimensions
        self.extended_screen_width = self.screen_width + self.side_extension * 2
        self.total_width = self.extended_screen_width + self.switch_side_width * 2
        self.total_height = self.screen_height + self.ui_height + self.top_border_extension
        
        # Background padding around the Switch console
        self.bg_padding = 40
        
        # Create the screen with additional space for the background
        self.window_width = self.total_width + self.bg_padding * 2
        self.window_height = self.total_height + self.bg_padding * 2
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        
        # Border settings
        self.white_border_thickness = 2  # Thickness of the white border
        
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
        
        # Animation variables
        self.animation_in_progress = False
        self.animation_start_time = 0
        self.animation_duration = 200  # milliseconds
        self.animation_start_pos = (0, 0)
        self.animation_end_pos = (0, 0)
        self.animation_direction = (0, 0)
        self.animation_box_start = None
        self.animation_box_end = None
        
        # Undo animation variables
        self.undo_animation_in_progress = False
        self.undo_animation_start_time = 0
        self.undo_animation_duration = 200  # milliseconds
        self.undo_animation_start_pos = (0, 0)
        self.undo_animation_end_pos = (0, 0)
        self.undo_animation_box_start = None
        self.undo_animation_box_end = None
        self.undo_previous_state = None
        self.undo_current_state = None
        
        # Load fonts
        font_path = pygame.font.match_font("freesansbold")
        self.font = pygame.font.Font(font_path, 24)
        self.small_font = pygame.font.Font(font_path, 18)
        self.title_font = pygame.font.Font(font_path, 32)
        self.congrats_font = pygame.font.Font(font_path, 36)

        # Initialize game
        self.load_level(self.current_level)
        self.setup_ui_buttons()
        self.clock = pygame.time.Clock()
        
        # Confetti colors
        self.confetti_colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (255, 165, 0), (128, 0, 128)
        ]
        self.confetti = []

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

    def setup_ui_buttons(self):
        # Calculate Joy-Con center positions - adjusted for background padding
        self.joycon_left_center_x = self.bg_padding + self.switch_side_width // 2
        self.joycon_right_center_x = self.bg_padding + self.total_width - self.switch_side_width // 2
        self.dpad_size = 60
        self.dpad_spacing = 15

        # D-pad position
        dpad_center_y = self.bg_padding + self.top_border_extension + 150

        # D-pad buttons
        self.dpad_up = pygame.Rect(
            self.joycon_left_center_x - self.dpad_size // 2,
            dpad_center_y - self.dpad_size - self.dpad_spacing,
            self.dpad_size, self.dpad_size
        )
        self.dpad_down = pygame.Rect(
            self.joycon_left_center_x - self.dpad_size // 2,
            dpad_center_y + self.dpad_spacing,
            self.dpad_size, self.dpad_size
        )
        self.dpad_left = pygame.Rect(
            self.joycon_left_center_x - self.dpad_size - self.dpad_spacing,
            dpad_center_y - self.dpad_size // 2,
            self.dpad_size, self.dpad_size
        )
        self.dpad_right = pygame.Rect(
            self.joycon_left_center_x + self.dpad_spacing,
            dpad_center_y - self.dpad_size // 2,
            self.dpad_size, self.dpad_size
        )

        # Function buttons
        button_width = 80
        button_height = 35
        bottom_padding = 50
        
        # Undo button (left Joy-Con)
        self.joy_undo = pygame.Rect(
            self.joycon_left_center_x - button_width // 2, 
            self.bg_padding + self.total_height - bottom_padding - button_height,
            button_width, button_height
        )
        
        # Reset button (right Joy-Con)
        self.joy_reset = pygame.Rect(
            self.joycon_right_center_x - button_width // 2, 
            self.bg_padding + self.total_height - bottom_padding - button_height,
            button_width, button_height
        )

        # Algorithm buttons
        algo_center_y = self.bg_padding + self.top_border_extension + 150
        
        # Algorithm selection buttons
        self.joy_bfs = pygame.Rect(
            self.joycon_right_center_x - self.dpad_size // 2,
            algo_center_y - self.dpad_size - self.dpad_spacing,
            self.dpad_size, self.dpad_size
        )
        self.joy_dfs = pygame.Rect(
            self.joycon_right_center_x - self.dpad_size // 2,
            algo_center_y + self.dpad_spacing,
            self.dpad_size, self.dpad_size
        )
        self.joy_astar = pygame.Rect(
            self.joycon_right_center_x - self.dpad_size - self.dpad_spacing,
            algo_center_y - self.dpad_size // 2,
            self.dpad_size, self.dpad_size
        )
        self.joy_stop = pygame.Rect(
            self.joycon_right_center_x + self.dpad_spacing,
            algo_center_y - self.dpad_size // 2,
            self.dpad_size, self.dpad_size
        )

        # Level navigation buttons
        self.circle_button_radius = 18
        self.padding = 45
        
        # Minus button (previous level)
        self.minus_button_x = self.bg_padding + self.switch_side_width - self.padding
        self.minus_button_y = self.bg_padding + self.padding
        self.minus_button_radius = self.circle_button_radius
        
        # Plus button (next level)
        self.plus_button_x = self.bg_padding + self.switch_side_width + self.extended_screen_width + self.padding
        self.plus_button_y = self.bg_padding + self.padding
        self.plus_button_radius = self.circle_button_radius

    def draw_diamond_button(self, rect, text, color, text_color=None, pressed=False):
        if text_color is None:
            text_color = self.WHITE

        # Draw shadow for 3D effect
        if not pressed:
            shadow_rect = rect.copy()
            shadow_rect.move_ip(3, 3)
            shadow_points = [
                (shadow_rect.centerx, shadow_rect.top),
                (shadow_rect.right, shadow_rect.centery),
                (shadow_rect.centerx, shadow_rect.bottom),
                (shadow_rect.left, shadow_rect.centery)
            ]
            pygame.draw.polygon(self.screen, (50, 50, 50), shadow_points)

        # Draw button
        points = [
            (rect.centerx, rect.top),
            (rect.right, rect.centery),
            (rect.centerx, rect.bottom),
            (rect.left, rect.centery)
        ]
        
        # Adjust position if pressed
        if pressed:
            adjusted_points = [(x+2, y+2) for x, y in points]
            pygame.draw.polygon(self.screen, color, adjusted_points)
            pygame.draw.polygon(self.screen, self.BLACK, adjusted_points, 2)
        else:
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, self.BLACK, points, 2)

        # Draw text
        text_surf = self.small_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        if pressed:
            text_rect.move_ip(2, 2)
        self.screen.blit(text_surf, text_rect)

    def draw_joy_con_button(self, rect, text, color, text_color=None, pressed=False):
        if text_color is None:
            text_color = self.WHITE
            
        # Draw shadow for 3D effect
        if not pressed:
            shadow_rect = rect.copy()
            shadow_rect.move_ip(3, 3)
            pygame.draw.rect(self.screen, (50, 50, 50), shadow_rect, border_radius=10)

        # Draw button
        button_rect = rect.copy()
        if pressed:
            button_rect.move_ip(2, 2)
            
        pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, button_rect, 2, border_radius=10)
        
        # Draw text
        text_surf = self.small_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_circle_button(self, center_x, center_y, radius, color, text=None, pressed=False):
        # Draw shadow for 3D effect
        if not pressed:
            pygame.draw.circle(self.screen, (50, 50, 50), (center_x+3, center_y+3), radius)
        
        # Draw button
        pos = (center_x, center_y)
        if pressed:
            pos = (center_x+2, center_y+2)
            
        pygame.draw.circle(self.screen, color, pos, radius)
        pygame.draw.circle(self.screen, self.BLACK, pos, radius, 2)
        
        # Draw text
        if text:
            text_surf = self.font.render(text, True, self.WHITE)
            text_rect = text_surf.get_rect(center=pos)
            self.screen.blit(text_surf, text_rect)

    def draw_ui(self):
        # Game info
        level_text = self.font.render(f"Level: {self.current_level}/{self.max_level}", True, self.WHITE)
        move_text = self.font.render(f"Moves: {self.move_count}", True, self.WHITE)
        
        # Position info text
        self.screen.blit(level_text, (self.window_width // 2 - 100, self.bg_padding + self.top_border_extension + self.screen_height + 2))
        self.screen.blit(move_text, (self.window_width // 2 + 100, self.bg_padding + self.top_border_extension + self.screen_height + 2))

        # Draw D-pad buttons
        self.draw_diamond_button(self.dpad_up, "↑", self.BLACK)
        self.draw_diamond_button(self.dpad_down, "↓", self.BLACK)
        self.draw_diamond_button(self.dpad_left, "←", self.BLACK)
        self.draw_diamond_button(self.dpad_right, "→", self.BLACK)

        # Draw function buttons
        self.draw_joy_con_button(self.joy_undo, "Undo", self.BLUE)
        self.draw_joy_con_button(self.joy_reset, "Reset", self.RED)

        # Draw algorithm buttons
        self.draw_diamond_button(self.joy_bfs, "BFS", self.PURPLE)
        self.draw_diamond_button(self.joy_dfs, "DFS", self.DARK_BLUE)
        self.draw_diamond_button(self.joy_astar, "A*", self.YELLOW, self.BLACK)
        self.draw_diamond_button(self.joy_stop, "Stop", self.RED if self.solving else self.GRAY)

        # Draw level navigation buttons
        self.draw_circle_button(self.minus_button_x, self.minus_button_y, self.minus_button_radius, self.BLACK, "-")
        self.draw_circle_button(self.plus_button_x, self.plus_button_y, self.plus_button_radius, self.BLACK, "+")

    def is_point_in_circle(self, point, center_x, center_y, radius):
        """Check if a point is inside a circle"""
        return ((point[0] - center_x) ** 2 + (point[1] - center_y) ** 2) <= radius ** 2

    def handle_click(self, pos):
        # Check for minus button (previous level)
        if self.is_point_in_circle(pos, self.minus_button_x, self.minus_button_y, self.minus_button_radius):
            if self.current_level > 1:
                self.current_level -= 1
                self.load_level(self.current_level)
        
        # Check for plus button (next level)
        elif self.is_point_in_circle(pos, self.plus_button_x, self.plus_button_y, self.plus_button_radius):
            if self.current_level < self.max_level:
                self.current_level += 1
                self.load_level(self.current_level)
            elif self.game_completed:
                # If on the last level and completed, restart from level 1
                self.current_level = 1
                self.load_level(self.current_level)
        
        # Check other buttons
        elif self.joy_reset.collidepoint(pos): 
            self.load_level(self.current_level)
        elif self.joy_undo.collidepoint(pos): 
            self.undo_move()
        elif self.joy_bfs.collidepoint(pos): 
            self.solve_with("bfs")
        elif self.joy_dfs.collidepoint(pos): 
            self.solve_with("dfs")
        elif self.joy_astar.collidepoint(pos): 
            self.solve_with("astar")
        elif self.joy_stop.collidepoint(pos):
            self.solving = False
            self.solution_path = []
        elif self.dpad_up.collidepoint(pos): 
            self.make_move((-1, 0))
        elif self.dpad_down.collidepoint(pos): 
            self.make_move((1, 0))
        elif self.dpad_left.collidepoint(pos): 
            self.make_move((0, -1))
        elif self.dpad_right.collidepoint(pos): 
            self.make_move((0, 1))

    def solve_with(self, algorithm):
        if self.game_completed or self.solving or self.animation_in_progress or self.undo_animation_in_progress:
            return
            
        state = State.from_game(self.game)
        result = None
        
        if algorithm == "bfs":
            result = bfs(state)
        elif algorithm == "dfs":
            result = dfs(state)
        else:  # A*
            result = a_star(state)
            
        if result and result[1]:
            self.solution_path = result[1]
            self.solution_index = 0
            self.solving = True
            self.last_solution_move_time = pygame.time.get_ticks()

    def find_player_and_box_positions(self, matrix):
        """Find player position and any box being pushed in a matrix"""
        player_pos = None
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] == '@' or matrix[i][j] == '+':
                    player_pos = (i, j)
                    break
            if player_pos:
                break
                
        return player_pos

    def find_differences(self, old_matrix, new_matrix):
        """Find differences between two matrices to determine player and box movement"""
        old_player_pos = self.find_player_and_box_positions(old_matrix)
        new_player_pos = self.find_player_and_box_positions(new_matrix)
        
        # Find box positions that changed
        old_box_positions = []
        new_box_positions = []
        
        for i in range(len(old_matrix)):
            for j in range(len(old_matrix[i])):
                if old_matrix[i][j] in ['$', '*'] and new_matrix[i][j] not in ['$', '*']:
                    old_box_positions.append((i, j))
                if new_matrix[i][j] in ['$', '*'] and old_matrix[i][j] not in ['$', '*']:
                    new_box_positions.append((i, j))
        
        # If we have exactly one box that moved
        if len(old_box_positions) == 1 and len(new_box_positions) == 1:
            return old_player_pos, new_player_pos, old_box_positions[0], new_box_positions[0]
        else:
            return old_player_pos, new_player_pos, None, None

    def undo_move(self):
        if not self.game.stack_matrix or self.animation_in_progress or self.undo_animation_in_progress:
            return
            
        # Store current state before undoing
        current_state = copy.deepcopy(self.game.matrix)
        previous_state = self.game.stack_matrix[-1]
        
        # Find player and box positions in both states
        old_player_pos, new_player_pos, old_box_pos, new_box_pos = self.find_differences(previous_state, current_state)
        
        if old_player_pos and new_player_pos:
            # Set up undo animation
            self.undo_animation_in_progress = True
            self.undo_animation_start_time = pygame.time.get_ticks()
            self.undo_animation_start_pos = new_player_pos
            self.undo_animation_end_pos = old_player_pos
            
            if old_box_pos and new_box_pos:
                self.undo_animation_box_start = new_box_pos
                self.undo_animation_box_end = old_box_pos
            else:
                self.undo_animation_box_start = None
                self.undo_animation_box_end = None
                
            # Store states for animation
            self.undo_previous_state = previous_state
            self.undo_current_state = current_state
            
            # Update game state - only pop one state at a time
            self.game.matrix = self.game.stack_matrix.pop()
            if self.move_count > 0:
                self.move_count -= 1
            self.game_completed = self.game.is_completed(self.dock_list)
            if not self.game_completed:
                self.show_congrats = False
        else:
            # If we couldn't determine positions for animation, just update the state
            self.game.matrix = self.game.stack_matrix.pop()
            if self.move_count > 0:
                self.move_count -= 1
            self.game_completed = self.game.is_completed(self.dock_list)
            if not self.game_completed:
                self.show_congrats = False

    def apply_solution_move(self):
        if not self.solving or self.solution_index >= len(self.solution_path) or self.animation_in_progress or self.undo_animation_in_progress:
            if self.solution_index >= len(self.solution_path):
                self.solving = False
            return
            
        now = pygame.time.get_ticks()
        if now - self.last_solution_move_time < self.solution_delay:
            return
            
        move = self.solution_path[self.solution_index]
        direction = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}.get(move)
        
        if direction:
            self.make_move(direction)
            
        self.solution_index += 1
        self.last_solution_move_time = now

    def make_move(self, direction):
        if self.game_completed or self.animation_in_progress or self.undo_animation_in_progress:
            return
            
        # Store current state for animation
        old_matrix = copy.deepcopy(self.game.matrix)
        player_pos = self.game.getPosition()
        
        # Calculate new positions
        new_player_row = player_pos[0] + direction[0]
        new_player_col = player_pos[1] + direction[1]
        
        # Check if move is valid
        if (new_player_row < 0 or new_player_row >= len(self.game.matrix) or
            new_player_col < 0 or new_player_col >= len(self.game.matrix[0]) or
            self.game.matrix[new_player_row][new_player_col] == '#'):
            return
            
        # Check if pushing a box
        pushing_box = False
        box_new_row, box_new_col = None, None
        
        if self.game.matrix[new_player_row][new_player_col] in ['$', '*']:
            pushing_box = True
            box_new_row = new_player_row + direction[0]
            box_new_col = new_player_col + direction[1]
            
            # Check if box can be pushed
            if (box_new_row < 0 or box_new_row >= len(self.game.matrix) or
                box_new_col < 0 or box_new_col >= len(self.game.matrix[0]) or
                self.game.matrix[box_new_row][box_new_col] in ['#', '$', '*']):
                return
        
        # Save the old state
        self.game.stack_matrix.append(copy.deepcopy(self.game.matrix))
        
        # Set up animation
        self.animation_in_progress = True
        self.animation_start_time = pygame.time.get_ticks()
        self.animation_start_pos = player_pos
        self.animation_end_pos = (new_player_row, new_player_col)
        self.animation_direction = direction
        
        if pushing_box:
            box_char = self.game.matrix[new_player_row][new_player_col]
            self.animation_box_start = (new_player_row, new_player_col)
            self.animation_box_end = (box_new_row, box_new_col)
        else:
            self.animation_box_start = None
            self.animation_box_end = None
        
        # Update the game state
        self.game.move(*direction, self.dock_list)
        
        # Only increment move count if the state actually changed
        if old_matrix != self.game.matrix:
            self.move_count += 1
            
            # Check if level is completed
            if self.game.is_completed(self.dock_list) and not self.game_completed:
                self.game_completed = True
                self.show_congrats = True
                self.congrats_alpha = 0
                self.congrats_fade_in = True
                self.create_confetti()

    def create_confetti(self):
        """Create confetti particles for celebration"""
        self.confetti = []
        
        for _ in range(100):
            x = random.randint(0, self.screen_width)
            y = -random.randint(0, 50)  # Start above the screen
            size = random.randint(5, 15)
            speed_x = random.uniform(-1, 1)
            speed_y = random.uniform(1, 3)
            color = random.choice(self.confetti_colors)
            rotation = random.uniform(0, 360)
            rot_speed = random.uniform(-5, 5)
            
            self.confetti.append({
                'x': x, 'y': y, 'size': size,
                'speed_x': speed_x, 'speed_y': speed_y,
                'color': color, 'rotation': rotation,
                'rot_speed': rot_speed
            })

    def update_confetti(self):
        """Update confetti particle positions"""
        for particle in self.confetti[:]:
            # Update position
            particle['y'] += particle['speed_y']
            particle['x'] += particle['speed_x']
            particle['rotation'] += particle['rot_speed']
            
            # Remove particles that have fallen off screen
            if particle['y'] > self.screen_height:
                self.confetti.remove(particle)

    def draw_confetti(self, subscreen):
        """Draw confetti particles"""
        for particle in self.confetti:
            # Only draw if within subscreen bounds
            if (0 <= particle['x'] < self.screen_width and 0 <= particle['y'] < self.screen_height):
                # Draw rotated rectangle
                rect = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
                rect.fill(particle['color'])
                rotated = pygame.transform.rotate(rect, particle['rotation'])
                rect_center = (particle['x'], particle['y'])
                rect_rect = rotated.get_rect(center=rect_center)
                subscreen.blit(rotated, rect_rect)

    def draw_congratulations(self, subscreen):
        """Draw congratulations overlay on the game screen only"""
        if not self.show_congrats:
            return
            
        # Update alpha for fade effect
        if self.congrats_fade_in:
            self.congrats_alpha += 3
            if self.congrats_alpha >= 255:
                self.congrats_alpha = 255
                self.congrats_fade_in = False
        
        # Create semi-transparent overlay for the game screen only
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(180, self.congrats_alpha)))
        subscreen.blit(overlay, (0, 0))
        
        # Draw congratulations text with current alpha
        congrats_text = self.congrats_font.render("Level Complete!", True, self.WHITE)
        congrats_text.set_alpha(self.congrats_alpha)
        congrats_rect = congrats_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
        subscreen.blit(congrats_text, congrats_rect)
        
        # Draw next level instruction with current alpha
        next_level_text = self.font.render("Press + for next level", True, self.WHITE)
        next_level_text.set_alpha(self.congrats_alpha)
        next_level_rect = next_level_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        subscreen.blit(next_level_text, next_level_rect)
        
        # Draw stars or other decorative elements
        if self.congrats_alpha > 100:
            star_radius = 25
            star_positions = [
                (self.screen_width // 2 - 120, self.screen_height // 2 - 100),
                (self.screen_width // 2, self.screen_height // 2 - 120),
                (self.screen_width // 2 + 120, self.screen_height // 2 - 100)
            ]
            
            for pos in star_positions:
                self.draw_star(subscreen, pos, star_radius, self.YELLOW, self.congrats_alpha)

    def draw_star(self, surface, center, radius, color, alpha):
        """Draw a star shape"""
        x, y = center
        points = []
        
        for i in range(10):
            angle = math.pi * 2 * i / 10 - math.pi / 2
            r = radius if i % 2 == 0 else radius * 0.4
            points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
        
        # Create a surface for the star with alpha channel
        star_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.polygon(star_surface, color + (alpha,), [(p[0]-x+radius, p[1]-y+radius) for p in points])
        
        # Draw the star on the provided surface
        surface.blit(star_surface, (x - radius, y - radius))

    def draw_game_with_animation(self, subscreen):
        """Draw the game with smooth animation"""
        # Fill with floor tiles
        Game.fill_screen_with_floor((self.screen_width, self.screen_height), subscreen)
        
        if not self.animation_in_progress and not self.undo_animation_in_progress:
            # Normal rendering without animation
            self.game.print_game(subscreen)
            return
            
        # Handle forward animation
        if self.animation_in_progress:
            # Calculate animation progress
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.animation_start_time
            progress = min(1.0, elapsed / self.animation_duration)
            
            # If animation is complete
            if progress >= 1.0:
                self.animation_in_progress = False
                self.game.print_game(subscreen)
                return
                
            # Get tile size
            tile_size = 64
            
            # Draw all static elements
            for row_index, row in enumerate(self.game.matrix):
                for col_index, char in enumerate(row):
                    # Skip player and moving box
                    if (row_index, col_index) == self.animation_end_pos:
                        continue
                        
                    if self.animation_box_end and (row_index, col_index) == self.animation_box_end:
                        continue
                        
                    # Skip the original player position
                    if (row_index, col_index) == self.animation_start_pos:
                        continue
                        
                    # Skip the original box position if pushing a box
                    if self.animation_box_start and (row_index, col_index) == self.animation_box_start:
                        continue
                        
                    x = col_index * tile_size
                    y = row_index * tile_size
                    
                    if char == '#':
                        obj = Wall(x, y)
                        subscreen.blit(obj.image, obj.rect)
                    elif char == '.':
                        obj = Dock(x, y)
                        subscreen.blit(obj.image, obj.rect)
                    elif char == '$':
                        obj = Box(x, y)
                        subscreen.blit(obj.image, obj.rect)
                    elif char == '*':
                        obj = BoxDocked(x, y)
                        subscreen.blit(obj.image, obj.rect)
            
            # Draw animated player
            start_x = self.animation_start_pos[1] * tile_size
            start_y = self.animation_start_pos[0] * tile_size
            end_x = self.animation_end_pos[1] * tile_size
            end_y = self.animation_end_pos[0] * tile_size
            
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            player = Worker(current_x, current_y)
            subscreen.blit(player.image, player.rect)
            
            # Draw animated box if pushing one
            if self.animation_box_start and self.animation_box_end:
                box_start_x = self.animation_box_start[1] * tile_size
                box_start_y = self.animation_box_start[0] * tile_size
                box_end_x = self.animation_box_end[1] * tile_size
                box_end_y = self.animation_box_end[0] * tile_size
                
                box_current_x = box_start_x + (box_end_x - box_start_x) * progress
                box_current_y = box_start_y + (box_end_y - box_start_y) * progress
                
                # Check if the box is on a dock in its final position
                if self.game.matrix[self.animation_box_end[0]][self.animation_box_end[1]] == '*':
                    box = BoxDocked(box_current_x, box_current_y)
                else:
                    box = Box(box_current_x, box_current_y)
                    
                subscreen.blit(box.image, box.rect)
        
        # Handle undo animation
        elif self.undo_animation_in_progress:
            # Calculate animation progress
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.undo_animation_start_time
            progress = min(1.0, elapsed / self.undo_animation_duration)
            
            # If animation is complete
            if progress >= 1.0:
                self.undo_animation_in_progress = False
                self.game.print_game(subscreen)
                return
                
            # Get tile size
            tile_size = 64
            
            # Draw all static elements from the current state
            for row_index, row in enumerate(self.game.matrix):
                for col_index, char in enumerate(row):
                    # Skip player position
                    if (row_index, col_index) == self.undo_animation_end_pos:
                        continue
                        
                    # Skip box end position if moving a box
                    if self.undo_animation_box_end and (row_index, col_index) == self.undo_animation_box_end:
                        continue
                    
                    x = col_index * tile_size
                    y = row_index * tile_size
                    
                    if char == '#':
                        obj = Wall(x, y)
                        subscreen.blit(obj.image, obj.rect)
                    elif char == '.':
                        obj = Dock(x, y)
                        subscreen.blit(obj.image, obj.rect)
                    elif char == '$':
                        obj = Box(x, y)
                        subscreen.blit(obj.image, obj.rect)
                    elif char == '*':
                        obj = BoxDocked(x, y)
                        subscreen.blit(obj.image, obj.rect)
            
            # Draw animated player (moving backward)
            start_x = self.undo_animation_start_pos[1] * tile_size
            start_y = self.undo_animation_start_pos[0] * tile_size
            end_x = self.undo_animation_end_pos[1] * tile_size
            end_y = self.undo_animation_end_pos[0] * tile_size
            
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            
            player = Worker(current_x, current_y)
            subscreen.blit(player.image, player.rect)
            
            # Draw animated box if one is being moved
            if self.undo_animation_box_start and self.undo_animation_box_end:
                box_start_x = self.undo_animation_box_start[1] * tile_size
                box_start_y = self.undo_animation_box_start[0] * tile_size
                box_end_x = self.undo_animation_box_end[1] * tile_size
                box_end_y = self.undo_animation_box_end[0] * tile_size
                
                box_current_x = box_start_x + (box_end_x - box_start_x) * progress
                box_current_y = box_start_y + (box_end_y - box_start_y) * progress
                
                # Determine box type based on destination in previous state
                is_docked = False
                if self.undo_previous_state and self.undo_animation_box_end:
                    row, col = self.undo_animation_box_end
                    if row < len(self.undo_previous_state) and col < len(self.undo_previous_state[0]):
                        is_docked = self.undo_previous_state[row][col] == '*'
                
                if is_docked:
                    box = BoxDocked(box_current_x, box_current_y)
                else:
                    box = Box(box_current_x, box_current_y)
                    
                subscreen.blit(box.image, box.rect)

    def draw_rounded_rect(self, surface, color, rect, radius, border_width=0):
        """Draw a rounded rectangle with proper corners"""
        rect = pygame.Rect(rect)
        
        # Draw the main rectangle body
        pygame.draw.rect(surface, color, rect.inflate(-radius * 2, 0))
        pygame.draw.rect(surface, color, rect.inflate(0, -radius * 2))
        
        # Draw the four corner circles
        pygame.draw.circle(surface, color, (rect.left + radius, rect.top + radius), radius)
        pygame.draw.circle(surface, color, (rect.right - radius, rect.top + radius), radius)
        pygame.draw.circle(surface, color, (rect.left + radius, rect.bottom - radius), radius)
        pygame.draw.circle(surface, color, (rect.right - radius, rect.bottom - radius), radius)
        
        # Draw border if specified
        if border_width > 0:
            pygame.draw.rect(surface, self.BLACK, rect.inflate(-radius * 2, 0), border_width)
            pygame.draw.rect(surface, self.BLACK, rect.inflate(0, -radius * 2), border_width)
            pygame.draw.circle(surface, self.BLACK, (rect.left + radius, rect.top + radius), radius, border_width)
            pygame.draw.circle(surface, self.BLACK, (rect.right - radius, rect.top + radius), radius, border_width)
            pygame.draw.circle(surface, self.BLACK, (rect.left + radius, rect.bottom - radius), radius, border_width)
            pygame.draw.circle(surface, self.BLACK, (rect.right - radius, rect.bottom - radius), radius, border_width)

    def draw_custom_joycon(self, surface, rect, color, highlight_color, is_left=True):
        """Draw a Joy-Con with custom corner radii"""
        rect = pygame.Rect(rect)
        
        # Different radii for different corners
        outer_radius = 50  # Outer corners (left side of left Joy-Con, right side of right Joy-Con)
        inner_radius = 10  # Inner corners (right side of left Joy-Con, left side of right Joy-Con)
        
        # Draw the main rectangle body
        pygame.draw.rect(surface, color, rect)
        
        # Determine which corners to round
        if is_left:
            # Left Joy-Con: Round left corners more, right corners less
            # Top-left corner
            pygame.draw.circle(surface, self.BLACK, (rect.left, rect.top), outer_radius)
            pygame.draw.circle(surface, color, (rect.left + outer_radius, rect.top + outer_radius), outer_radius)
            
            # Bottom-left corner
            pygame.draw.circle(surface, self.BLACK, (rect.left, rect.bottom), outer_radius)
            pygame.draw.circle(surface, color, (rect.left + outer_radius, rect.bottom - outer_radius), outer_radius)
            
            # Top-right corner (less rounded)
            pygame.draw.circle(surface, self.BLACK, (rect.right, rect.top), inner_radius)
            pygame.draw.circle(surface, color, (rect.right - inner_radius, rect.top + inner_radius), inner_radius)
            
            # Bottom-right corner (less rounded)
            pygame.draw.circle(surface, self.BLACK, (rect.right, rect.bottom), inner_radius)
            pygame.draw.circle(surface, color, (rect.right - inner_radius, rect.bottom - inner_radius), inner_radius)
        else:
            # Right Joy-Con: Round right corners more, left corners less
            # Top-right corner
            pygame.draw.circle(surface, self.BLACK, (rect.right, rect.top), outer_radius)
            pygame.draw.circle(surface, color, (rect.right - outer_radius, rect.top + outer_radius), outer_radius)
            
            # Bottom-right corner
            pygame.draw.circle(surface, self.BLACK, (rect.right, rect.bottom), outer_radius)
            pygame.draw.circle(surface, color, (rect.right - outer_radius, rect.bottom - outer_radius), outer_radius)
            
            # Top-left corner (less rounded)
            pygame.draw.circle(surface, self.BLACK, (rect.left, rect.top), inner_radius)
            pygame.draw.circle(surface, color, (rect.left + inner_radius, rect.top + inner_radius), inner_radius)
            
            # Bottom-left corner (less rounded)
            pygame.draw.circle(surface, self.BLACK, (rect.left, rect.bottom), inner_radius)
            pygame.draw.circle(surface, color, (rect.left + inner_radius, rect.bottom - inner_radius), inner_radius)
        
        # Add highlight
        highlight_width = 15
        highlight_rect = rect.inflate(-highlight_width*2, -highlight_width*2)
        
        if is_left:
            # Left Joy-Con highlight
            pygame.draw.rect(surface, highlight_color, highlight_rect, width=2, border_radius=40)
        else:
            # Right Joy-Con highlight
            pygame.draw.rect(surface, highlight_color, highlight_rect, width=2, border_radius=40)

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == KEYDOWN:
                    if not self.animation_in_progress and not self.undo_animation_in_progress:
                        if event.key == K_UP:
                            self.make_move((-1, 0))
                        elif event.key == K_DOWN:
                            self.make_move((1, 0))
                        elif event.key == K_LEFT:
                            self.make_move((0, -1))
                        elif event.key == K_RIGHT:
                            self.make_move((0, 1))
                        elif event.key == K_z:
                            self.undo_move()
                        elif event.key == K_r:
                            self.load_level(self.current_level)
                        elif event.key == K_EQUALS or event.key == K_PLUS:
                            if self.game_completed and self.current_level < self.max_level:
                                self.current_level += 1
                                self.load_level(self.current_level)
                        elif event.key == K_MINUS:
                            if self.current_level > 1:
                                self.current_level -= 1
                                self.load_level(self.current_level)

            # Apply solution move if solving
            if self.solving:
                self.apply_solution_move()

            # Update confetti if game is completed
            if self.game_completed:
                self.update_confetti()

            # Fill screen with background color
            self.screen.fill(self.BACKGROUND_COLOR)
            
            # Draw unified shadow for the entire console
            shadow_offset = 6
            console_shadow_rect = pygame.Rect(
                self.bg_padding + shadow_offset, 
                self.bg_padding + shadow_offset, 
                self.total_width, 
                self.total_height
            )
            self.draw_rounded_rect(self.screen, (15, 15, 15), console_shadow_rect, 50)
            
            # Draw black rectangle background around the entire Nintendo Switch
            switch_rect = pygame.Rect(
                self.bg_padding, 
                self.bg_padding, 
                self.total_width, 
                self.total_height
            )
            self.draw_rounded_rect(self.screen, self.BLACK, switch_rect, 50)
            
            # Left Joy-Con (blue) with custom corners
            left_joycon_rect = pygame.Rect(
                self.bg_padding, 
                self.bg_padding, 
                self.switch_side_width, 
                self.total_height
            )
            self.draw_custom_joycon(self.screen, left_joycon_rect, self.SWITCH_LEFT_COLOR, 
                                   self.SWITCH_LEFT_HIGHLIGHT, is_left=True)
            
            # Right Joy-Con (red) with custom corners
            right_joycon_rect = pygame.Rect(
                self.bg_padding + self.switch_side_width + self.extended_screen_width, 
                self.bg_padding, 
                self.switch_side_width, 
                self.total_height
            )
            self.draw_custom_joycon(self.screen, right_joycon_rect, self.SWITCH_RIGHT_COLOR, 
                                   self.SWITCH_RIGHT_HIGHLIGHT, is_left=False)

            # Switch body (black)
            body_rect = pygame.Rect(
                self.bg_padding + self.switch_side_width,
                self.bg_padding,
                self.extended_screen_width,
                self.total_height
            )
            pygame.draw.rect(self.screen, self.BLACK, body_rect)
            
            # Black rectangle surrounding the game screen
            screen_black_rect = pygame.Rect(
                self.bg_padding + self.switch_side_width + self.side_extension - 5,
                self.bg_padding + self.top_border_extension - 5,
                self.screen_width + 10, 
                self.screen_height + 10
            )
            pygame.draw.rect(self.screen, self.BLACK, screen_black_rect, border_radius=8)
            
            # Game screen
            game_screen_rect = pygame.Rect(
                self.bg_padding + self.switch_side_width + self.side_extension,
                self.bg_padding + self.top_border_extension,
                self.screen_width, 
                self.screen_height
            )
            pygame.draw.rect(self.screen, self.SWITCH_SCREEN_COLOR, game_screen_rect)
            
            # Create subscreen for game rendering
            subscreen = self.screen.subsurface(game_screen_rect)
            
            # Draw game with animation
            self.draw_game_with_animation(subscreen)
            
            # Draw confetti if game is completed
            if self.game_completed:
                self.draw_confetti(subscreen)
                
            # Draw congratulations overlay if game is completed (only on the game screen)
            if self.show_congrats:
                self.draw_congratulations(subscreen)

            # Draw UI elements
            self.draw_ui()

            # Draw white rectangular border spanning from right side of left Joy-Con to left side of right Joy-Con
            white_border_rect = pygame.Rect(
                self.bg_padding + self.switch_side_width,  # Right side of left Joy-Con
                self.bg_padding,  # Top of the console
                self.extended_screen_width,  # Width of the middle section
                self.total_height  # Full height of the Joy-Cons
            )
            pygame.draw.rect(self.screen, self.WHITE, white_border_rect, self.white_border_thickness)

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    import random
    game = SokobanGUI()
    game.run()
