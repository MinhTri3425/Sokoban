import pygame
import copy
import random
import math
from Object.box import Box
from Object.box_docked import BoxDocked
from Object.floor import Floor
from Object.wall import Wall
from Object.worker import Worker
from Object.dock import Dock
from Game import Game
from .gui_sound import SokobanGUISound

class SokobanGUIGame:
    def __init__(self, gui_init):
        self.gui_init = gui_init
        self.gui_sound = SokobanGUISound(gui_init)

    def find_player_and_box_positions(self, matrix):
        player_pos = None
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] in ['@', '+']:
                    player_pos = (i, j)
                    break
            if player_pos:
                break
        return player_pos

    def find_differences(self, old_matrix, new_matrix):
        print("Finding differences between matrices")
        old_player_pos = self.find_player_and_box_positions(old_matrix)
        new_player_pos = self.find_player_and_box_positions(new_matrix)
        print(f"Old player pos: {old_player_pos}, New player pos: {new_player_pos}")
        
        old_box_positions = []
        new_box_positions = []
        for i in range(len(old_matrix)):
            for j in range(len(old_matrix[i])):
                if old_matrix[i][j] in ['$', '*'] and new_matrix[i][j] not in ['$', '*']:
                    old_box_positions.append((i, j))
                if new_matrix[i][j] in ['$', '*'] and old_matrix[i][j] not in ['$', '*']:
                    new_box_positions.append((i, j))
        
        box_moved = False
        old_box_pos = None
        new_box_pos = None
        if len(old_box_positions) == 1 and len(new_box_positions) == 1:
            old_box_pos = old_box_positions[0]
            new_box_pos = new_box_positions[0]
            box_moved = True
            print(f"Box moved: from {old_box_pos} to {new_box_pos}")
        
        return old_player_pos, new_player_pos, old_box_pos, new_box_pos

    def undo_move(self):

        if not self.gui_init.game.stack_matrix:
           # print("Undo blocked: No previous moves to undo")
            return
        previous_state = self.gui_init.game.stack_matrix.pop() 

        old_matrix = copy.deepcopy(self.gui_init.game.matrix)  
        self.gui_init.game.matrix = copy.deepcopy(previous_state) 


        self.gui_init.game.player = self.find_player_and_box_positions(self.gui_init.game.matrix)[0]
        self.gui_init.game.boxes = self.find_player_and_box_positions(self.gui_init.game.matrix)[1]
        self.gui_init.game.print_game(self.gui_init.screen)

        if old_matrix != self.gui_init.game.matrix:
            if self.gui_init.move_count > 0:
                self.gui_init.move_count -= 1
            #print(f"Move count after undo: {self.gui_init.move_count}")

        #print("Undo applied successfully.")

    def apply_solution_move(self):
        if not self.gui_init.solving or self.gui_init.solution_index >= len(self.gui_init.solution_path) or self.gui_init.animation_in_progress or self.gui_init.undo_animation_in_progress:
            if self.gui_init.solution_index >= len(self.gui_init.solution_path):
                self.gui_init.solving = False
            return
        now = pygame.time.get_ticks()
        if now - self.gui_init.last_solution_move_time < self.gui_init.solution_delay:
            return
        move = self.gui_init.solution_path[self.gui_init.solution_index]
        direction = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}.get(move)
        if direction:
            self.make_move(direction)
        self.gui_init.solution_index += 1
        self.gui_init.last_solution_move_time = now

    def make_move(self, direction):
        # print(f"make_move called: direction={direction}, move_count={self.gui_init.move_count}, stack_len={len(self.gui_init.game.stack_matrix)}")
        if self.gui_init.game_completed or self.gui_init.animation_in_progress or self.gui_init.undo_animation_in_progress:
            #print("Move blocked: Game completed or animation in progress")
            return
        old_matrix = copy.deepcopy(self.gui_init.game.matrix)
        player_pos = self.gui_init.game.getPosition()
        new_player_row = player_pos[0] + direction[0]
        new_player_col = player_pos[1] + direction[1]
        if (new_player_row < 0 or new_player_row >= len(self.gui_init.game.matrix) or
            new_player_col < 0 or new_player_col >= len(self.gui_init.game.matrix[0]) or
            self.gui_init.game.matrix[new_player_row][new_player_col] == '#'):
           # print("Move blocked: Invalid position or wall")
            return
        pushing_box = False
        box_new_row, box_new_col = None, None
        if self.gui_init.game.matrix[new_player_row][new_player_col] in ['$', '*']:
            pushing_box = True
            box_new_row = new_player_row + direction[0]
            box_new_col = new_player_col + direction[1]
            if (box_new_row < 0 or box_new_row >= len(self.gui_init.game.matrix) or
                box_new_col < 0 or box_new_col >= len(self.gui_init.game.matrix[0]) or
                self.gui_init.game.matrix[box_new_row][box_new_col] in ['#', '$', '*']):
               # print("Move blocked: Box cannot be pushed")
                return
        self.gui_init.game.move(*direction, self.gui_init.dock_list)
        if old_matrix != self.gui_init.game.matrix:
            self.gui_init.game.stack_matrix.append(copy.deepcopy(self.gui_init.game.matrix))
            self.gui_init.move_count += 1
            self.gui_init.animation_in_progress = True
            self.gui_init.animation_start_time = pygame.time.get_ticks()
            self.gui_init.animation_start_pos = player_pos
            self.gui_init.animation_end_pos = (new_player_row, new_player_col)
            self.gui_init.animation_direction = direction
            if pushing_box:
                self.gui_init.animation_box_start = (new_player_row, new_player_col)
                self.gui_init.animation_box_end = (box_new_row, box_new_col)
            else:
                self.gui_init.animation_box_start = None
                self.gui_init.animation_box_end = None
            self.gui_sound.play_move_sound()
            # print(f"Move completed: move_count={self.gui_init.move_count}, new player_pos={(new_player_row, new_player_col)}, stack_len={len(self.gui_init.game.stack_matrix)}")
            if self.gui_init.game.is_completed(self.gui_init.dock_list) and not self.gui_init.game_completed:
                self.gui_init.game_completed = True
                self.gui_init.show_congrats = True
                self.gui_init.congrats_alpha = 0
                self.gui_init.congrats_fade_in = True
                self.create_confetti()
                self.gui_sound.play_victory_sound()
        else:
            print("Move skipped: No change in matrix")

    def create_confetti(self):
        self.gui_init.confetti = []
        for _ in range(100):
            x = random.randint(0, self.gui_init.screen_width)
            y = -random.randint(0, 50)
            size = random.randint(5, 15)
            speed_x = random.uniform(-1, 1)
            speed_y = random.uniform(1, 3)
            color = random.choice(self.gui_init.confetti_colors)
            rotation = random.uniform(0, 360)
            rot_speed = random.uniform(-5, 5)
            self.gui_init.confetti.append({
                'x': x, 'y': y, 'size': size,
                'speed_x': speed_x, 'speed_y': speed_y,
                'color': color, 'rotation': rotation,
                'rot_speed': rot_speed
            })

    def update_confetti(self):
        for particle in self.gui_init.confetti[:]:
            particle['y'] += particle['speed_y']
            particle['x'] += particle['speed_x']
            particle['rotation'] += particle['rot_speed']
            if particle['y'] > self.gui_init.screen_height:
                self.gui_init.confetti.remove(particle)

    def draw_confetti(self, subscreen):
        for particle in self.gui_init.confetti:
            if (0 <= particle['x'] < self.gui_init.screen_width and 0 <= particle['y'] < self.gui_init.screen_height):
                rect = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
                rect.fill(particle['color'])
                rotated = pygame.transform.rotate(rect, particle['rotation'])
                rect_center = (particle['x'], particle['y'])
                rect_rect = rotated.get_rect(center=rect_center)
                subscreen.blit(rotated, rect_rect)

    def draw_congratulations(self, subscreen):
        if not self.gui_init.show_congrats:
            return
        if self.gui_init.congrats_fade_in:
            self.gui_init.congrats_alpha += 3
            if self.gui_init.congrats_alpha >= 255:
                self.gui_init.congrats_alpha = 255
                self.gui_init.congrats_fade_in = False
        overlay = pygame.Surface((self.gui_init.screen_width, self.gui_init.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(180, self.gui_init.congrats_alpha)))
        subscreen.blit(overlay, (0, 0))
        congrats_text = self.gui_init.congrats_font.render("Level Complete!", True, self.gui_init.WHITE)
        congrats_text.set_alpha(self.gui_init.congrats_alpha)
        congrats_rect = congrats_text.get_rect(center=(self.gui_init.screen_width // 2, self.gui_init.screen_height // 2 - 40))
        subscreen.blit(congrats_text, congrats_rect)
        next_level_text = self.gui_init.font.render("Press + for next level", True, self.gui_init.WHITE)
        next_level_text.set_alpha(self.gui_init.congrats_alpha)
        next_level_rect = next_level_text.get_rect(center=(self.gui_init.screen_width // 2, self.gui_init.screen_height // 2 + 20))
        subscreen.blit(next_level_text, next_level_rect)
        if self.gui_init.congrats_alpha > 100:
            star_radius = 25
            star_positions = [
                (self.gui_init.screen_width // 2 - 120, self.gui_init.screen_height // 2 - 100),
                (self.gui_init.screen_width // 2, self.gui_init.screen_height // 2 - 120),
                (self.gui_init.screen_width // 2 + 120, self.gui_init.screen_height // 2 - 100)
            ]
            for pos in star_positions:
                self.draw_star(subscreen, pos, star_radius, self.gui_init.YELLOW, self.gui_init.congrats_alpha)

    def draw_star(self, surface, center, radius, color, alpha):
        x, y = center
        points = []
        for i in range(10):
            angle = math.pi * 2 * i / 10 - math.pi / 2
            r = radius if i % 2 == 0 else radius * 0.4
            points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
        star_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.polygon(star_surface, color + (alpha,), [(p[0]-x+radius, p[1]-y+radius) for p in points])
        surface.blit(star_surface, (x - radius, y - radius))

    def draw_game_with_animation(self, subscreen):
        Game.fill_screen_with_floor((self.gui_init.screen_width, self.gui_init.screen_height), subscreen)
        current_time = pygame.time.get_ticks()
        tile_size = 64
        if not self.gui_init.animation_in_progress and not self.gui_init.undo_animation_in_progress:
            self.gui_init.game.print_game(subscreen)
            return
        if self.gui_init.animation_in_progress:
            elapsed = current_time - self.gui_init.animation_start_time
            progress = min(1.0, elapsed / self.gui_init.animation_duration)
            if progress >= 1.0:
                self.gui_init.animation_in_progress = False
                self.gui_init.animation_start_pos = None
                self.gui_init.animation_end_pos = None
                self.gui_init.animation_box_start = None
                self.gui_init.animation_box_end = None
                self.gui_init.animation_direction = None
                self.gui_init.game.print_game(subscreen)
                # print("Move animation completed")
                return
            for row_index, row in enumerate(self.gui_init.game.matrix):
                for col_index, char in enumerate(row):
                    if (row_index, col_index) in [
                        self.gui_init.animation_start_pos,
                        self.gui_init.animation_end_pos,
                        self.gui_init.animation_box_start,
                        self.gui_init.animation_box_end,
                    ]:
                        continue
                    x, y = col_index * tile_size, row_index * tile_size
                    self.draw_tile(char, x, y, subscreen)
            current_x = self.gui_init.animation_start_pos[1] * tile_size + (self.gui_init.animation_end_pos[1] - self.gui_init.animation_start_pos[1]) * tile_size * progress
            current_y = self.gui_init.animation_start_pos[0] * tile_size + (self.gui_init.animation_end_pos[0] - self.gui_init.animation_start_pos[0]) * tile_size * progress
            player = Worker(current_x, current_y)
            subscreen.blit(player.image, player.rect)
            if self.gui_init.animation_box_start and self.gui_init.animation_box_end:
                box_current_x = self.gui_init.animation_box_start[1] * tile_size + (self.gui_init.animation_box_end[1] - self.gui_init.animation_box_start[1]) * tile_size * progress
                box_current_y = self.gui_init.animation_box_start[0] * tile_size + (self.gui_init.animation_box_end[0] - self.gui_init.animation_box_start[0]) * tile_size * progress
                is_docked = self.gui_init.game.matrix[self.gui_init.animation_box_end[0]][self.gui_init.animation_box_end[1]] == '*'
                box = BoxDocked(box_current_x, box_current_y) if is_docked else Box(box_current_x, box_current_y)
                subscreen.blit(box.image, box.rect)
        elif self.gui_init.undo_animation_in_progress:
            elapsed = current_time - self.gui_init.undo_animation_start_time
            progress = min(1.0, elapsed / self.gui_init.undo_animation_duration)
            if progress >= 1.0:
                self.gui_init.undo_animation_in_progress = False
                if self.gui_init.move_count > 0 and self.gui_init.undo_previous_state:
                    self.gui_init.move_count -= 1
                    self.gui_init.game.matrix = copy.deepcopy(self.gui_init.undo_previous_state)
                    self.gui_init.game.player = self.find_player_and_box_positions(self.gui_init.game.matrix)
                    if self.gui_init.game.stack_matrix:
                        self.gui_init.game.stack_matrix.pop()
                    # print(f"Undo completed: player_pos={self.gui_init.game.player}, move_count={self.gui_init.move_count}, stack_len={len(self.gui_init.game.stack_matrix)}")
                self.gui_init.undo_previous_state = None
                self.gui_init.undo_animation_start_pos = None
                self.gui_init.undo_animation_end_pos = None
                self.gui_init.undo_animation_box_start = None
                self.gui_init.undo_animation_box_end = None
                self.gui_init.game_completed = self.gui_init.game.is_completed(self.gui_init.dock_list)
                if not self.gui_init.game_completed:
                    self.gui_init.show_congrats = False
                self.gui_init.game.print_game(subscreen)
                return
            for row_index, row in enumerate(self.gui_init.game.matrix):
                for col_index, char in enumerate(row):
                    if (row_index, col_index) in [
                        self.gui_init.undo_animation_start_pos,
                        self.gui_init.undo_animation_end_pos,
                        self.gui_init.undo_animation_box_start,
                        self.gui_init.undo_animation_box_end,
                    ]:
                        continue
                    x, y = col_index * tile_size, row_index * tile_size
                    self.draw_tile(char, x, y, subscreen)
            current_x = self.gui_init.undo_animation_start_pos[1] * tile_size + (self.gui_init.undo_animation_end_pos[1] - self.gui_init.undo_animation_start_pos[1]) * tile_size * progress
            current_y = self.gui_init.undo_animation_start_pos[0] * tile_size + (self.gui_init.undo_animation_end_pos[0] - self.gui_init.undo_animation_start_pos[0]) * tile_size * progress
            player = Worker(current_x, current_y)
            subscreen.blit(player.image, player.rect)
            if self.gui_init.undo_animation_box_start and self.gui_init.undo_animation_box_end:
                box_current_x = self.gui_init.undo_animation_box_start[1] * tile_size + (self.gui_init.undo_animation_box_end[1] - self.gui_init.undo_animation_box_start[1]) * tile_size * progress
                box_current_y = self.gui_init.undo_animation_box_start[0] * tile_size + (self.gui_init.undo_animation_box_end[0] - self.gui_init.undo_animation_box_start[0]) * tile_size * progress
                is_docked = False
                if self.gui_init.undo_previous_state:
                    row, col = self.gui_init.undo_animation_box_end
                    if 0 <= row < len(self.gui_init.undo_previous_state) and 0 <= col < len(self.gui_init.undo_previous_state[row]):
                        is_docked = self.gui_init.undo_previous_state[row][col] == '*'
                box = BoxDocked(box_current_x, box_current_y) if is_docked else Box(box_current_x, box_current_y)
                subscreen.blit(box.image, box.rect)

    def draw_tile(self, char, x, y, subscreen):
        if char == '#':
            obj = Wall(x, y)
        elif char == '.':
            obj = Dock(x, y)
        elif char == '$':
            obj = Box(x, y)
        elif char == '*':
            obj = BoxDocked(x, y)
        else:
            return
        subscreen.blit(obj.image, obj.rect)

    def draw_comparison_results(self, subscreen):
        
        if not self.gui_init.comparing:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.gui_init.comparison_start_time > self.gui_init.comparison_duration:
            self.gui_init.comparing = False
            return

        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.gui_init.screen_width, self.gui_init.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Giảm độ tối để dễ nhìn hơn
        subscreen.blit(overlay, (0, 0))

        center_x = self.gui_init.screen_width // 2 - 20

        # Draw title
        self.gui_init.title_font.set_bold(True)
        title_text = self.gui_init.title_font.render("Algorithm Comparison", True, self.gui_init.WHITE)
        title_rect = title_text.get_rect(center=(center_x, 50))
        subscreen.blit(title_text, title_rect)

        # Draw headers
        y_pos = 120
        headers = ["Algorithm", "Time", "Length", "Nodes", "Memory"]
        col_widths = [0, 120, 240, 360, 470]
        x_positions = [center_x - 250 + offset for offset in col_widths]
        
        for i, header in enumerate(headers):
            # self.gui_init.font.set_bold(True)
            header_text = self.gui_init.font.render(header, True, self.gui_init.YELLOW)
            subscreen.blit(header_text, (x_positions[i], y_pos))

        y_pos += 40

        # Draw results
        for algorithm in ["BFS", "DFS", "A*"]:
            if algorithm in self.gui_init.comparison_results:
                result = self.gui_init.comparison_results[algorithm]

                # Algorithm name
                algo_text = self.gui_init.font.render(algorithm, True, self.gui_init.WHITE)
                subscreen.blit(algo_text, (x_positions[0], y_pos))

                # Time
                time_text = self.gui_init.font.render(f"{result['time']:.4f}", True, self.gui_init.WHITE)
                subscreen.blit(time_text, (x_positions[1], y_pos))

                # Path length
                if result["solution_found"]:
                    path_text = self.gui_init.font.render(f"{result['path_length']}", True, self.gui_init.WHITE)
                else:
                    path_text = self.gui_init.font.render("N/A", True, self.gui_init.RED)
                subscreen.blit(path_text, (x_positions[2], y_pos))

                # Nodes explored
                nodes_text = self.gui_init.font.render(f"{result['nodes_explored']}", True, self.gui_init.WHITE)
                subscreen.blit(nodes_text, (x_positions[3], y_pos))

                # Memory peak
                memory_text = self.gui_init.font.render(f"{result['memory_peak']:.2f}", True, self.gui_init.WHITE)
                subscreen.blit(memory_text, (x_positions[4], y_pos))

                y_pos += 40

        # Draw conclusion
        best_time = best_path = None
        best_time_algo = best_path_algo = None

        for algorithm, result in self.gui_init.comparison_results.items():
            if result["solution_found"]:
                if best_time is None or result["time"] < best_time:
                    best_time = result["time"]
                    best_time_algo = algorithm
                if best_path is None or (result["path_length"] > 0 and result["path_length"] < best_path):
                    best_path = result["path_length"]
                    best_path_algo = algorithm

        y_pos += 20
        if best_time_algo:
            fastest_text = self.gui_init.font.render(f"Fastest: {best_time_algo} ({best_time:.4f}s)", True, self.gui_init.GREEN)
            subscreen.blit(fastest_text, (center_x - 150, y_pos))

        y_pos += 40
        if best_path_algo:
            optimal_text = self.gui_init.font.render(f"Shortest path: {best_path_algo} ({best_path} moves)", True, self.gui_init.GREEN)
            subscreen.blit(optimal_text, (center_x - 150, y_pos))

        # Draw algorithm characteristics
        y_pos += 60
        characteristics = [
            "BFS: Guarantees shortest path, but uses more memory",
            "DFS: Uses less memory, but may find longer paths",
            "A*: Balances speed and path quality using heuristics"
        ]

        for char in characteristics:
            char_text = self.gui_init.small_font.render(char, True, self.gui_init.LIGHT_GRAY)
            subscreen.blit(char_text, (center_x - 200, y_pos))
            y_pos += 35  # Giãn dòng dễ đọc

        # Draw close instruction with shadow
        y_pos += 20
        close_text = self.gui_init.small_font.render("Click anywhere to close", True, self.gui_init.LIGHT_GRAY)
        close_rect = close_text.get_rect(center=(center_x, y_pos))

        shadow = self.gui_init.small_font.render("Click anywhere to close", True, (0, 0, 0))
        subscreen.blit(shadow, (close_rect.x + 2, close_rect.y + 2))
        subscreen.blit(close_text, close_rect)
