import pygame
import math

class SokobanGUIUI:
    def __init__(self, gui_init):
        self.gui_init = gui_init
        self.setup_ui_buttons()
        self.game_screen_rect = pygame.Rect(
            self.gui_init.bg_padding + self.gui_init.switch_side_width + self.gui_init.side_extension,
            self.gui_init.bg_padding + self.gui_init.top_border_extension,
            self.gui_init.screen_width,
            self.gui_init.screen_height
        )

    def setup_ui_buttons(self):
        # Joy-Con center positions
        self.joycon_left_center_x = self.gui_init.bg_padding + self.gui_init.switch_side_width // 2
        self.joycon_right_center_x = self.gui_init.bg_padding + self.gui_init.total_width - self.gui_init.switch_side_width // 2
        self.dpad_size = 60
        self.dpad_spacing = 15
        dpad_center_y = self.gui_init.bg_padding + self.gui_init.top_border_extension + 150

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
        self.joy_undo = pygame.Rect(
            self.joycon_left_center_x - button_width // 2,
            self.gui_init.bg_padding + self.gui_init.total_height - bottom_padding - button_height,
            button_width, button_height
        )
        self.joy_reset = pygame.Rect(
            self.joycon_right_center_x - button_width // 2,
            self.gui_init.bg_padding + self.gui_init.total_height - bottom_padding - button_height,
            button_width, button_height
        )

        # Algorithm buttons
        algo_center_y = self.gui_init.bg_padding + self.gui_init.top_border_extension + 150
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

        # Algorithm comparison button
        self.joy_compare = pygame.Rect(
            self.joycon_right_center_x - button_width // 2,
            algo_center_y + self.dpad_size + self.dpad_spacing * 3,
            button_width, button_height
        )

        # Level navigation buttons
        self.circle_button_radius = 18
        self.padding = 45
        self.minus_button_x = self.gui_init.bg_padding + self.gui_init.switch_side_width - self.padding
        self.minus_button_y = self.gui_init.bg_padding + self.padding
        self.plus_button_x = self.gui_init.bg_padding + self.gui_init.switch_side_width + self.gui_init.extended_screen_width + self.padding
        self.plus_button_y = self.gui_init.bg_padding + self.padding

    def draw_diamond_button(self, rect, text, color, text_color=None, pressed=False):
        if text_color is None:
            text_color = self.gui_init.WHITE
        if not pressed:
            shadow_rect = rect.copy()
            shadow_rect.move_ip(3, 3)
            shadow_points = [
                (shadow_rect.centerx, shadow_rect.top),
                (shadow_rect.right, shadow_rect.centery),
                (shadow_rect.centerx, shadow_rect.bottom),
                (shadow_rect.left, shadow_rect.centery)
            ]
            pygame.draw.polygon(self.gui_init.screen, (50, 50, 50), shadow_points)
        points = [
            (rect.centerx, rect.top),
            (rect.right, rect.centery),
            (rect.centerx, rect.bottom),
            (rect.left, rect.centery)
        ]
        if pressed:
            adjusted_points = [(x+2, y+2) for x, y in points]
            pygame.draw.polygon(self.gui_init.screen, color, adjusted_points)
            pygame.draw.polygon(self.gui_init.screen, self.gui_init.BLACK, adjusted_points, 2)
        else:
            pygame.draw.polygon(self.gui_init.screen, color, points)
            pygame.draw.polygon(self.gui_init.screen, self.gui_init.BLACK, points, 2)
        text_surf = self.gui_init.small_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        if pressed:
            text_rect.move_ip(2, 2)
        self.gui_init.screen.blit(text_surf, text_rect)

    def draw_joy_con_button(self, rect, text, color, text_color=None, pressed=False):
        if text_color is None:
            text_color = self.gui_init.WHITE
        if not pressed:
            shadow_rect = rect.copy()
            shadow_rect.move_ip(3, 3)
            pygame.draw.rect(self.gui_init.screen, (50, 50, 50), shadow_rect, border_radius=10)
        button_rect = rect.copy()
        if pressed:
            button_rect.move_ip(2, 2)
        pygame.draw.rect(self.gui_init.screen, color, button_rect, border_radius=10)
        pygame.draw.rect(self.gui_init.screen, self.gui_init.BLACK, button_rect, 2, border_radius=10)
        text_surf = self.gui_init.small_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.gui_init.screen.blit(text_surf, text_rect)

    def draw_circle_button(self, center_x, center_y, radius, color, text=None, pressed=False):
        if not pressed:
            pygame.draw.circle(self.gui_init.screen, (50, 50, 50), (center_x+3, center_y+3), radius)
        pos = (center_x, center_y)
        if pressed:
            pos = (center_x+2, center_y+2)
        pygame.draw.circle(self.gui_init.screen, color, pos, radius)
        pygame.draw.circle(self.gui_init.screen, self.gui_init.BLACK, pos, radius, 2)
        if text:
            text_surf = self.gui_init.font.render(text, True, self.gui_init.WHITE)
            text_rect = text_surf.get_rect(center=pos)
            self.gui_init.screen.blit(text_surf, text_rect)

    def draw_ui(self):
        level_text = self.gui_init.font.render(f"Level: {self.gui_init.current_level}/{self.gui_init.max_level}", True, self.gui_init.WHITE)
        move_text = self.gui_init.font.render(f"Moves: {self.gui_init.move_count}", True, self.gui_init.WHITE)
        self.gui_init.screen.blit(level_text, (self.gui_init.window_width // 2 - 100, self.gui_init.bg_padding + self.gui_init.top_border_extension + self.gui_init.screen_height + 2))
        self.gui_init.screen.blit(move_text, (self.gui_init.window_width // 2 + 100, self.gui_init.bg_padding + self.gui_init.top_border_extension + self.gui_init.screen_height + 2))
        self.draw_diamond_button(self.dpad_up, "↑", self.gui_init.BLACK)
        self.draw_diamond_button(self.dpad_down, "↓", self.gui_init.BLACK)
        self.draw_diamond_button(self.dpad_left, "←", self.gui_init.BLACK)
        self.draw_diamond_button(self.dpad_right, "→", self.gui_init.BLACK)
        self.draw_joy_con_button(self.joy_undo, "Undo", self.gui_init.BLUE)
        self.draw_joy_con_button(self.joy_reset, "Reset", self.gui_init.RED)
        self.draw_diamond_button(self.joy_bfs, "BFS", self.gui_init.PURPLE)
        self.draw_diamond_button(self.joy_dfs, "DFS", self.gui_init.DARK_BLUE)
        self.draw_diamond_button(self.joy_astar, "A*", self.gui_init.YELLOW, self.gui_init.BLACK)
        self.draw_diamond_button(self.joy_stop, "Stop", self.gui_init.RED if self.gui_init.solving else self.gui_init.GRAY)
        self.draw_joy_con_button(self.joy_compare, "Compare", self.gui_init.GREEN)
        self.draw_circle_button(self.minus_button_x, self.minus_button_y, self.circle_button_radius, self.gui_init.BLACK, "-")
        self.draw_circle_button(self.plus_button_x, self.plus_button_y, self.circle_button_radius, self.gui_init.BLACK, "+")

    def draw_rounded_rect(self, surface, color, rect, radius, border_width=0):
        rect = pygame.Rect(rect)
        pygame.draw.rect(surface, color, rect.inflate(-radius * 2, 0))
        pygame.draw.rect(surface, color, rect.inflate(0, -radius * 2))
        pygame.draw.circle(surface, color, (rect.left + radius, rect.top + radius), radius)
        pygame.draw.circle(surface, color, (rect.right - radius, rect.top + radius), radius)
        pygame.draw.circle(surface, color, (rect.left + radius, rect.bottom - radius), radius)
        pygame.draw.circle(surface, color, (rect.right - radius, rect.bottom - radius), radius)
        if border_width > 0:
            pygame.draw.rect(surface, self.gui_init.BLACK, rect.inflate(-radius * 2, 0), border_width)
            pygame.draw.rect(surface, self.gui_init.BLACK, rect.inflate(0, -radius * 2), border_width)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.left + radius, rect.top + radius), radius, border_width)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.right - radius, rect.top + radius), radius, border_width)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.left + radius, rect.bottom - radius), radius, border_width)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.right - radius, rect.bottom - radius), radius, border_width)

    def draw_custom_joycon(self, surface, rect, color, highlight_color, is_left=True):
        rect = pygame.Rect(rect)
        outer_radius = 50
        inner_radius = 10
        pygame.draw.rect(surface, color, rect)
        if is_left:
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.left, rect.top), outer_radius)
            pygame.draw.circle(surface, color, (rect.left + outer_radius, rect.top + outer_radius), outer_radius)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.left, rect.bottom), outer_radius)
            pygame.draw.circle(surface, color, (rect.left + outer_radius, rect.bottom - outer_radius), outer_radius)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.right, rect.top), inner_radius)
            pygame.draw.circle(surface, color, (rect.right - inner_radius, rect.top + inner_radius), inner_radius)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.right, rect.bottom), inner_radius)
            pygame.draw.circle(surface, color, (rect.right - inner_radius, rect.bottom - inner_radius), inner_radius)
        else:
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.right, rect.top), outer_radius)
            pygame.draw.circle(surface, color, (rect.right - outer_radius, rect.top + outer_radius), outer_radius)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.right, rect.bottom), outer_radius)
            pygame.draw.circle(surface, color, (rect.right - outer_radius, rect.bottom - outer_radius), outer_radius)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.left, rect.top), inner_radius)
            pygame.draw.circle(surface, color, (rect.left + inner_radius, rect.top + inner_radius), inner_radius)
            pygame.draw.circle(surface, self.gui_init.BLACK, (rect.left, rect.bottom), inner_radius)
            pygame.draw.circle(surface, color, (rect.left + inner_radius, rect.bottom - inner_radius), inner_radius)
        highlight_width = 15
        highlight_rect = rect.inflate(-highlight_width*2, -highlight_width*2)
        pygame.draw.rect(surface, highlight_color, highlight_rect, width=2, border_radius=40)

    def draw_console(self):
        shadow_offset = 6
        console_shadow_rect = pygame.Rect(
            self.gui_init.bg_padding + shadow_offset,
            self.gui_init.bg_padding + shadow_offset,
            self.gui_init.total_width,
            self.gui_init.total_height
        )
        self.draw_rounded_rect(self.gui_init.screen, (15, 15, 15), console_shadow_rect, 50)
        switch_rect = pygame.Rect(
            self.gui_init.bg_padding,
            self.gui_init.bg_padding,
            self.gui_init.total_width,
            self.gui_init.total_height
        )
        self.draw_rounded_rect(self.gui_init.screen, self.gui_init.BLACK, switch_rect, 50)
        left_joycon_rect = pygame.Rect(
            self.gui_init.bg_padding,
            self.gui_init.bg_padding,
            self.gui_init.switch_side_width,
            self.gui_init.total_height
        )
        self.draw_custom_joycon(self.gui_init.screen, left_joycon_rect, self.gui_init.SWITCH_LEFT_COLOR,
                               self.gui_init.SWITCH_LEFT_HIGHLIGHT, is_left=True)
        right_joycon_rect = pygame.Rect(
            self.gui_init.bg_padding + self.gui_init.switch_side_width + self.gui_init.extended_screen_width,
            self.gui_init.bg_padding,
            self.gui_init.switch_side_width,
            self.gui_init.total_height
        )
        self.draw_custom_joycon(self.gui_init.screen, right_joycon_rect, self.gui_init.SWITCH_RIGHT_COLOR,
                               self.gui_init.SWITCH_RIGHT_HIGHLIGHT, is_left=False)
        body_rect = pygame.Rect(
            self.gui_init.bg_padding + self.gui_init.switch_side_width,
            self.gui_init.bg_padding,
            self.gui_init.extended_screen_width,
            self.gui_init.total_height
        )
        pygame.draw.rect(self.gui_init.screen, self.gui_init.BLACK, body_rect)
        screen_black_rect = pygame.Rect(
            self.gui_init.bg_padding + self.gui_init.switch_side_width + self.gui_init.side_extension - 5,
            self.gui_init.bg_padding + self.gui_init.top_border_extension - 5,
            self.gui_init.screen_width + 10,
            self.gui_init.screen_height + 10
        )
        pygame.draw.rect(self.gui_init.screen, self.gui_init.BLACK, screen_black_rect, border_radius=8)
        pygame.draw.rect(self.gui_init.screen, self.gui_init.SWITCH_SCREEN_COLOR, self.game_screen_rect)

    def draw_white_border(self):
        white_border_rect = pygame.Rect(
            self.gui_init.bg_padding + self.gui_init.switch_side_width,
            self.gui_init.bg_padding,
            self.gui_init.extended_screen_width,
            self.gui_init.total_height
        )
        pygame.draw.rect(
            self.gui_init.screen,
            self.gui_init.WHITE,
            white_border_rect,
            self.gui_init.white_border_thickness,
            border_radius=8
        )
