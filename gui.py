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
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Sokoban Game")
        
        # Load sprites
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
        # Add space for UI elements
        self.ui_height = 150
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
        self.solution_delay = 300  # milliseconds between automated moves
        self.last_solution_move_time = 0
        
        # Font
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        
        # Load the first level
        self.load_level(self.current_level)
        
        # Set up the screen
        self.tile_size = 64
        self.screen_width, self.screen_height = self.game.load_size()
        

        self.screen = pygame.display.set_mode((max(self.screen_width, 600), self.screen_height + self.ui_height))
        
        # UI button areas
        self.setup_ui_buttons()
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()

    def setup_ui_buttons(self):
        """Set up UI button areas"""
        button_width = 100
        button_height = 40
        button_margin = 10
        
        # Game control buttons (top row)
        self.reset_button = pygame.Rect(button_margin, self.screen_height + button_margin, button_width, button_height)
        self.undo_button = pygame.Rect(button_margin * 2 + button_width, self.screen_height + button_margin, button_width, button_height)
        self.prev_level_button = pygame.Rect(button_margin * 3 + button_width * 2, self.screen_height + button_margin, button_width, button_height)
        self.next_level_button = pygame.Rect(button_margin * 4 + button_width * 3, self.screen_height + button_margin, button_width, button_height)
        
        # Solver buttons (bottom row)
        solver_y = self.screen_height + button_margin * 2 + button_height
        self.bfs_button = pygame.Rect(button_margin, solver_y, button_width, button_height)
        self.dfs_button = pygame.Rect(button_margin * 2 + button_width, solver_y, button_width, button_height)
        self.astar_button = pygame.Rect(button_margin * 3 + button_width * 2, solver_y, button_width, button_height)
        self.stop_button = pygame.Rect(button_margin * 4 + button_width * 3, solver_y, button_width, button_height)

    def count_levels(self):
        """Count how many level files exist"""
        level_count = 0
        while True:
            level_path = os.path.join("Level", f"level{level_count + 1}.txt")
            if os.path.exists(level_path):
                level_count += 1
            else:
                break
        return max(1, level_count)  # Ensure at least 1 level

    def load_level(self, level_number):
        """Load a level from file"""
        try:
            level_path = os.path.join("Level", f"level{level_number}.txt")
            with open(level_path, 'r') as file:
                level_data = [list(line.rstrip()) for line in file]
                
            self.game = Game(level_data, [])
            self.dock_list = self.game.listDock()
            self.move_count = 0
            self.game_completed = False
            self.solving = False
            self.solution_path = []
            self.solution_index = 0
            
            # Update screen size based on level dimensions
            self.screen_width, self.screen_height = self.game.load_size()
            self.screen = pygame.display.set_mode((max(self.screen_width, 600), self.screen_height + self.ui_height))
            
            # Recalculate button positions
            self.setup_ui_buttons()
            
        except FileNotFoundError:
            print(f"Level {level_number} not found. Staying on current level.")
            if level_number > self.current_level:
                self.current_level -= 1
            elif level_number < self.current_level:
                self.current_level += 1

    def draw_ui(self):
        """Draw UI elements"""
        # Draw UI background
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, (0, self.screen_height, self.screen_width, self.ui_height))
        
        # Draw title
        title_text = self.title_font.render("SOKOBAN", True, self.BLACK)
        title_rect = title_text.get_rect(midtop=(self.screen_width // 2, self.screen_height + 5))
        self.screen.blit(title_text, title_rect)
        
        # Draw buttons - Game controls
        self.draw_button(self.reset_button, "Reset", self.RED)
        self.draw_button(self.undo_button, "Undo", self.BLUE)
        self.draw_button(self.prev_level_button, "Prev", self.GREEN)
        self.draw_button(self.next_level_button, "Next", self.GREEN)
        
        # Draw buttons - Solvers
        self.draw_button(self.bfs_button, "BFS", self.DARK_BLUE)
        self.draw_button(self.dfs_button, "DFS", self.DARK_BLUE)
        self.draw_button(self.astar_button, "A*", self.DARK_BLUE)
        self.draw_button(self.stop_button, "Stop", self.RED if self.solving else self.GRAY)
        
        # Draw level and move info
        level_text = self.font.render(f"Level: {self.current_level}/{self.max_level}", True, self.BLACK)
        self.screen.blit(level_text, (10, self.screen_height + 100))
        
        moves_text = self.font.render(f"Moves: {self.move_count}", True, self.BLACK)
        self.screen.blit(moves_text, (150, self.screen_height + 100))
        
        # Draw completion message if game is completed
        if self.game_completed:
            complete_text = self.font.render("Level Complete!", True, self.GREEN)
            complete_rect = complete_text.get_rect(midtop=(self.screen_width // 2, self.screen_height + 100))
            self.screen.blit(complete_text, complete_rect)
        
        # Draw solving status if applicable
        if self.solving:
            solving_text = self.small_font.render("Auto-solving...", True, self.BLUE)
            self.screen.blit(solving_text, (300, self.screen_height + 100))

    def draw_button(self, rect, text, color):
        """Draw a button with text"""
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.BLACK, rect, 2)  # Border
        text_surf = self.small_font.render(text, True, self.WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def handle_click(self, pos):
        """Handle mouse clicks on UI elements"""
        if self.reset_button.collidepoint(pos):
            self.load_level(self.current_level)
        elif self.undo_button.collidepoint(pos):
            self.undo_move()
        elif self.next_level_button.collidepoint(pos):
            if self.current_level < self.max_level:
                self.current_level += 1
                self.load_level(self.current_level)
        elif self.prev_level_button.collidepoint(pos):
            if self.current_level > 1:
                self.current_level -= 1
                self.load_level(self.current_level)
        elif self.bfs_button.collidepoint(pos):
            self.solve_with_algorithm("bfs")
        elif self.dfs_button.collidepoint(pos):
            self.solve_with_algorithm("dfs")
        elif self.astar_button.collidepoint(pos):
            self.solve_with_algorithm("astar")
        elif self.stop_button.collidepoint(pos):
            self.solving = False
            self.solution_path = []

    def solve_with_algorithm(self, algorithm):
        """Solve the current level with the specified algorithm"""
        if self.game_completed or self.solving:
            return
            
        # Convert game to state
        start_state = State.from_game(self.game)
        
        # Run the appropriate algorithm
        solution = None
        if algorithm == "bfs":
            solution = bfs(start_state)
        elif algorithm == "dfs":
            solution = dfs(start_state)
        elif algorithm == "astar":
            solution = a_star(start_state)
            
        if solution and solution[1]:  # Check if solution and directions exist
            self.solution_path = solution[1]
            self.solution_index = 0
            self.solving = True
            self.last_solution_move_time = pygame.time.get_ticks()
        else:
            print("No solution found!")

    def apply_solution_move(self):
        """Apply the next move from the solution"""
        if not self.solving or not self.solution_path or self.solution_index >= len(self.solution_path):
            self.solving = False
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_solution_move_time < self.solution_delay:
            return
            
        direction = self.solution_path[self.solution_index]
        if direction == "U":
            self.make_move((-1, 0))
        elif direction == "D":
            self.make_move((1, 0))
        elif direction == "L":
            self.make_move((0, -1))
        elif direction == "R":
            self.make_move((0, 1))
            
        self.solution_index += 1
        self.last_solution_move_time = current_time
        
        if self.solution_index >= len(self.solution_path):
            self.solving = False

    def undo_move(self):
        """Undo the last move"""
        if len(self.game.stack_matrix) > 0:
            self.game.matrix = self.game.stack_matrix.pop()
            if self.move_count > 0:
                self.move_count -= 1
            self.game_completed = self.game.is_completed(self.dock_list)

    def handle_key(self, key):
        """Handle keyboard input for game moves"""
        if self.game_completed or self.solving:
            return
            
        direction = None
        if key == K_UP:
            direction = (-1, 0)
        elif key == K_DOWN:
            direction = (1, 0)
        elif key == K_LEFT:
            direction = (0, -1)
        elif key == K_RIGHT:
            direction = (0, 1)
            
        if direction:
            self.make_move(direction)

    def make_move(self, direction):
        """Make a move in the specified direction"""
        # Save current state before move
        old_matrix = copy.deepcopy(self.game.matrix)
        self.game.stack_matrix.append(old_matrix)
        
        # Make the move
        self.game.move(direction[0], direction[1], self.dock_list)
        
        # Check if the move actually changed the state
        if not self.matrices_equal(self.game.matrix, old_matrix):
            self.move_count += 1
            # Check if game is completed
            self.game_completed = self.game.is_completed(self.dock_list)
        else:
            # If no change, remove the saved state
            self.game.stack_matrix.pop()

    def matrices_equal(self, matrix1, matrix2):
        """Compare two matrices for equality"""
        if len(matrix1) != len(matrix2):
            return False
        for i in range(len(matrix1)):
            if len(matrix1[i]) != len(matrix2[i]):
                return False
            for j in range(len(matrix1[i])):
                if matrix1[i][j] != matrix2[i][j]:
                    return False
        return True

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    else:
                        self.handle_key(event.key)
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            # Apply solution move if solving
            if self.solving:
                self.apply_solution_move()
            
            # Clear screen
            self.screen.fill(self.WHITE)
            
            # Draw floor under everything
            Game.fill_screen_with_floor((self.screen_width, self.screen_height), self.screen)
            
            # Draw game elements
            self.game.print_game(self.screen)
            
            # Draw UI
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Run the game if this file is executed directly
if __name__ == "__main__":
    game_gui = SokobanGUI()
    game_gui.run()