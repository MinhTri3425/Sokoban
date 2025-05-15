import pygame
from pygame.locals import *
import sys
from .gui_init import SokobanGUIInit
from .gui_ui import SokobanGUIUI
from .gui_game import SokobanGUIGame
from .gui_event import SokobanGUIEvent
from .gui_sound import SokobanGUISound

class SokobanGUIMain:
    def __init__(self):
        self.gui_init = SokobanGUIInit()
        self.gui_ui = SokobanGUIUI(self.gui_init)
        self.gui_game = SokobanGUIGame(self.gui_init)
        self.gui_event = SokobanGUIEvent(self.gui_init, self.gui_ui, self.gui_game)
        self.gui_sound = SokobanGUISound(self.gui_init)

    def run(self):
        """Main game loop"""
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.gui_event.handle_click(event.pos)
                elif event.type == KEYDOWN:
                    self.gui_event.handle_keydown(event)

            # Apply solution move if solving
            if self.gui_init.solving:
                self.gui_game.apply_solution_move()

            # Update confetti if game is completed
            if self.gui_init.game_completed:
                self.gui_game.update_confetti()

            # Fill screen with background color
            self.gui_init.screen.fill(self.gui_init.BACKGROUND_COLOR)

            # Draw unified shadow and console
            self.gui_ui.draw_console()

            # Create subscreen for game rendering
            subscreen = self.gui_init.screen.subsurface(self.gui_ui.game_screen_rect)

            # Draw game with animation
            self.gui_game.draw_game_with_animation(subscreen)

            # Draw confetti if game is completed
            if self.gui_init.game_completed:
                self.gui_game.draw_confetti(subscreen)

            # Draw congratulations overlay
            if self.gui_init.show_congrats:
                self.gui_game.draw_congratulations(subscreen)
                
            # Draw algorithm comparison results if comparing
            if self.gui_init.comparing:
                self.gui_game.draw_comparison_results(subscreen)

            # Draw UI elements
            self.gui_ui.draw_ui()

            # Draw white border
            self.gui_ui.draw_white_border()

            # Update display
            pygame.display.flip()
            self.gui_init.clock.tick(60)

        # Stop all sounds before quitting
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SokobanGUIMain()
    game.run()
