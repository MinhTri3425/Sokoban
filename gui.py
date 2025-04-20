import pygame
import sys
import os
from pygame.locals import *
import copy
from State import State
from solver.bfs import bfs
from solver.dfs import dfs
from solver.a_star import a_star

# Import game components
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
        pygame.display.set_caption("Sokoban Game - Nintendo Switch Style")

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

        self.ui_height = 30
        self.switch_side_width = 250
        self.screen_width = 576
        self.screen_height = 512
        self.total_width = self.screen_width + self.switch_side_width * 2
        self.total_height = self.screen_height + self.ui_height

        self.screen = pygame.display.set_mode((self.total_width, self.total_height))

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

        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)

        self.load_level(self.current_level)
        self.setup_ui_buttons()
        self.clock = pygame.time.Clock()

    def setup_ui_buttons(self):
        self.joycon_left_center_x = self.switch_side_width // 2
        self.dpad_size = 25
        self.dpad_spacing = 35

        self.dpad_up = pygame.Rect(self.joycon_left_center_x - self.dpad_size // 2, 100, self.dpad_size, self.dpad_size)
        self.dpad_down = pygame.Rect(self.joycon_left_center_x - self.dpad_size // 2, 100 + self.dpad_spacing, self.dpad_size, self.dpad_size)
        self.dpad_left = pygame.Rect(self.joycon_left_center_x - self.dpad_size - self.dpad_spacing // 2, 100 + self.dpad_spacing // 2, self.dpad_size, self.dpad_size)
        self.dpad_right = pygame.Rect(self.joycon_left_center_x + self.dpad_spacing // 2, 100 + self.dpad_spacing // 2, self.dpad_size, self.dpad_size)

        self.joy_reset = pygame.Rect(self.joycon_left_center_x - 30, 200, 60, 25)
        self.joy_undo = pygame.Rect(self.joycon_left_center_x - 30, 240, 60, 25)

        self.joycon_right_center_x = self.total_width - self.switch_side_width // 2

        self.joy_next = pygame.Rect(self.joycon_right_center_x - 30, 280, 60, 25)
        self.joy_prev = pygame.Rect(self.joycon_right_center_x - 30, 320, 60, 25)

        self.joy_bfs = pygame.Rect(self.joycon_right_center_x - 30, 100, 60, 25)
        self.joy_dfs = pygame.Rect(self.joycon_right_center_x - 30, 140, 60, 25)
        self.joy_astar = pygame.Rect(self.joycon_right_center_x - 30, 180, 60, 25)
        self.joy_stop = pygame.Rect(self.joycon_right_center_x - 30, 220, 60, 25)

    def count_levels(self):
        count = 0
        while os.path.exists(f"Level/level{count + 1}.txt"):
            count += 1
        return max(1, count)

    def load_level(self, level_number):
        try:
            with open(f"Level/level{level_number}.txt") as f:
                level_data = [list(line.strip()) for line in f]
            self.game = Game(level_data, [])
            self.dock_list = self.game.listDock()
            self.move_count = 0
            self.game_completed = False
            self.solving = False
            self.solution_path = []
            self.solution_index = 0
        except FileNotFoundError:
            print(f"Level {level_number} not found")

    def draw_joy_con_button(self, rect, text, color, text_color=None):
        if text_color is None:
            text_color = self.WHITE
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        pygame.draw.rect(self.screen, self.BLACK, rect, 2, border_radius=5)
        text_surf = self.small_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_circle_button(self, center_x, center_y, radius, color):
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, self.BLACK, (center_x, center_y), radius, 2)

    def draw_ui(self):
        level_text = self.font.render(f"Level: {self.current_level}/{self.max_level}", True, self.WHITE)
        move_text = self.font.render(f"Moves: {self.move_count}", True, self.WHITE)
        self.screen.blit(level_text, (self.total_width // 2 - 100, self.screen_height + 2))
        self.screen.blit(move_text, (self.total_width // 2 + 100, self.screen_height + 2))

        self.draw_joy_con_button(self.dpad_up, "↑", self.BLACK)
        self.draw_joy_con_button(self.dpad_down, "↓", self.BLACK)
        self.draw_joy_con_button(self.dpad_left, "←", self.BLACK)
        self.draw_joy_con_button(self.dpad_right, "→", self.BLACK)

        self.draw_joy_con_button(self.joy_reset, "Reset", self.RED)
        self.draw_joy_con_button(self.joy_undo, "Undo", self.BLUE)
        self.draw_joy_con_button(self.joy_prev, "Prev", self.GREEN)
        self.draw_joy_con_button(self.joy_next, "Next", self.GREEN)

        self.draw_joy_con_button(self.joy_bfs, "BFS", self.PURPLE)
        self.draw_joy_con_button(self.joy_dfs, "DFS", self.DARK_BLUE)
        self.draw_joy_con_button(self.joy_astar, "A*", self.YELLOW, self.BLACK)
        self.draw_joy_con_button(self.joy_stop, "Stop", self.RED if self.solving else self.GRAY)

        self.draw_circle_button(self.joycon_left_center_x, 400, 15, self.BLACK)
        self.draw_circle_button(self.joycon_right_center_x, 400, 15, self.BLACK)

    def handle_click(self, pos):
        if self.joy_reset.collidepoint(pos): self.load_level(self.current_level)
        elif self.joy_undo.collidepoint(pos): self.undo_move()
        elif self.joy_prev.collidepoint(pos) and self.current_level > 1:
            self.current_level -= 1
            self.load_level(self.current_level)
        elif self.joy_next.collidepoint(pos) and self.current_level < self.max_level:
            self.current_level += 1
            self.load_level(self.current_level)
        elif self.joy_bfs.collidepoint(pos): self.solve_with("bfs")
        elif self.joy_dfs.collidepoint(pos): self.solve_with("dfs")
        elif self.joy_astar.collidepoint(pos): self.solve_with("astar")
        elif self.joy_stop.collidepoint(pos):
            self.solving = False
            self.solution_path = []
        elif self.dpad_up.collidepoint(pos): self.make_move((-1, 0))
        elif self.dpad_down.collidepoint(pos): self.make_move((1, 0))
        elif self.dpad_left.collidepoint(pos): self.make_move((0, -1))
        elif self.dpad_right.collidepoint(pos): self.make_move((0, 1))

    def solve_with(self, algorithm):
        if self.game_completed or self.solving:
            return
        state = State.from_game(self.game)
        result = bfs(state) if algorithm == "bfs" else dfs(state) if algorithm == "dfs" else a_star(state)
        if result and result[1]:
            self.solution_path = result[1]
            self.solution_index = 0
            self.solving = True
            self.last_solution_move_time = pygame.time.get_ticks()

    def undo_move(self):
        if self.game.stack_matrix:
            self.game.matrix = self.game.stack_matrix.pop()
            if self.move_count > 0:
                self.move_count -= 1
            self.game_completed = self.game.is_completed(self.dock_list)

    def apply_solution_move(self):
        if not self.solving or self.solution_index >= len(self.solution_path):
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
        if self.game_completed or self.solving:
            return
        old = copy.deepcopy(self.game.matrix)
        self.game.stack_matrix.append(old)
        self.game.move(*direction, self.dock_list)
        if old != self.game.matrix:
            self.move_count += 1
            self.game_completed = self.game.is_completed(self.dock_list)
        else:
            self.game.stack_matrix.pop()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            if self.solving:
                self.apply_solution_move()

            self.screen.fill(self.BLACK)
            pygame.draw.rect(self.screen, self.SWITCH_LEFT_COLOR, (0, 0, self.switch_side_width, self.total_height))
            pygame.draw.rect(self.screen, self.SWITCH_RIGHT_COLOR, (self.switch_side_width + self.screen_width, 0, self.switch_side_width, self.total_height))
            pygame.draw.rect(self.screen, self.SWITCH_BODY_COLOR, (self.switch_side_width, 0, self.screen_width, self.screen_height))

            # Vẽ hình chữ nhật bao quanh vùng SWITCH_BODY_COLOR
            pygame.draw.rect(self.screen, self.BLACK, (self.switch_side_width, 0, self.screen_width, self.screen_height), 5)

            subscreen = self.screen.subsurface(pygame.Rect(self.switch_side_width, 0, self.screen_width, self.screen_height))
            Game.fill_screen_with_floor((self.screen_width, self.screen_height), subscreen)
            self.game.print_game(subscreen)

            self.draw_ui()

            if self.game_completed:
                complete_text = self.font.render("Level Complete!", True, self.GREEN)
                self.screen.blit(complete_text, complete_text.get_rect(center=(self.total_width // 2, 70)))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SokobanGUI()
    game.run()
