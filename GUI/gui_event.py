import pygame
from pygame.locals import *
from State import State
from solver.bfs import bfs
from solver.dfs import dfs
from solver.a_star import a_star

class SokobanGUIEvent:
    def __init__(self, gui_init, gui_ui, gui_game):
        self.gui_init = gui_init
        self.gui_ui = gui_ui
        self.gui_game = gui_game

    def is_point_in_circle(self, point, center_x, center_y, radius):
        return ((point[0] - center_x) ** 2 + (point[1] - center_y) ** 2) <= radius ** 2

    def handle_click(self, pos):
        if self.is_point_in_circle(pos, self.gui_ui.minus_button_x, self.gui_ui.minus_button_y, self.gui_ui.circle_button_radius):
            if self.gui_init.current_level > 1:
                self.gui_init.current_level -= 1
                self.gui_init.load_level(self.gui_init.current_level)
        elif self.is_point_in_circle(pos, self.gui_ui.plus_button_x, self.gui_ui.plus_button_y, self.gui_ui.circle_button_radius):
            if self.gui_init.current_level < self.gui_init.max_level:
                self.gui_init.current_level += 1
                self.gui_init.load_level(self.gui_init.current_level)
            elif self.gui_init.game_completed:
                self.gui_init.current_level = 1
                self.gui_init.load_level(self.gui_init.current_level)
        elif self.gui_ui.joy_reset.collidepoint(pos):
            self.gui_init.load_level(self.gui_init.current_level)
        elif self.gui_ui.joy_undo.collidepoint(pos):
            self.gui_game.undo_move()
        elif self.gui_ui.joy_bfs.collidepoint(pos):
            self.solve_with("bfs")
        elif self.gui_ui.joy_dfs.collidepoint(pos):
            self.solve_with("dfs")
        elif self.gui_ui.joy_astar.collidepoint(pos):
            self.solve_with("astar")
        elif self.gui_ui.joy_stop.collidepoint(pos):
            self.gui_init.solving = False
            self.gui_init.solution_path = []
        elif self.gui_ui.dpad_up.collidepoint(pos):
            self.gui_game.make_move((-1, 0))
        elif self.gui_ui.dpad_down.collidepoint(pos):
            self.gui_game.make_move((1, 0))
        elif self.gui_ui.dpad_left.collidepoint(pos):
            self.gui_game.make_move((0, -1))
        elif self.gui_ui.dpad_right.collidepoint(pos):
            self.gui_game.make_move((0, 1))

    def handle_keydown(self, event):
        if not self.gui_init.animation_in_progress and not self.gui_init.undo_animation_in_progress:
            if event.key == K_UP:
                self.gui_game.make_move((-1, 0))
            elif event.key == K_DOWN:
                self.gui_game.make_move((1, 0))
            elif event.key == K_LEFT:
                self.gui_game.make_move((0, -1))
            elif event.key == K_RIGHT:
                self.gui_game.make_move((0, 1))
            elif event.key == K_z:
                self.gui_game.undo_move()
            elif event.key == K_r:
                self.gui_init.load_level(self.gui_init.current_level)
            elif event.key == K_EQUALS or event.key == K_PLUS:
                if self.gui_init.game_completed and self.gui_init.current_level < self.gui_init.max_level:
                    self.gui_init.current_level += 1
                    self.gui_init.load_level(self.gui_init.current_level)
            elif event.key == K_MINUS:
                if self.gui_init.current_level > 1:
                    self.gui_init.current_level -= 1
                    self.gui_init.load_level(self.gui_init.current_level)

    def solve_with(self, algorithm):
        if self.gui_init.game_completed or self.gui_init.solving or self.gui_init.animation_in_progress or self.gui_init.undo_animation_in_progress:
            return
        state = State.from_game(self.gui_init.game)
        result = None
        if algorithm == "bfs":
            result = bfs(state)
        elif algorithm == "dfs":
            result = dfs(state)
        else:
            result = a_star(state)
        if result and result[1]:
            self.gui_init.solution_path = result[1]
            self.gui_init.solution_index = 0
            self.gui_init.solving = True
            self.gui_init.last_solution_move_time = pygame.time.get_ticks()