import pygame
from pygame.locals import *
import time
import tracemalloc
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
        # Close comparison results if showing
        if self.gui_init.comparing:
            self.gui_init.comparing = False
            return
            
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
        elif self.gui_ui.joy_compare.collidepoint(pos):
            self.compare_algorithms()
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
            elif event.key == K_c:
                self.compare_algorithms()

    def solve_with(self, algorithm):
        if self.gui_init.game_completed or self.gui_init.solving or self.gui_init.animation_in_progress or self.gui_init.undo_animation_in_progress:
            return
        state = State.from_game(self.gui_init.game)
        result = None
        if algorithm == "bfs":
            result = self.run_bfs(state)
        elif algorithm == "dfs":
            result = self.run_dfs(state)
        else:
            result = self.run_astar(state)
        if result and result[1]:
            self.gui_init.solution_path = result[1]
            self.gui_init.solution_index = 0
            self.gui_init.solving = True
            self.gui_init.last_solution_move_time = pygame.time.get_ticks()

    def run_bfs(self, state, timeout=10):
        """Run BFS with performance tracking"""
        visited = set()
        queue = [(state, [])]
        nodes_explored = 0
        
        start_time = time.time()
        tracemalloc.start()
        
        while queue and time.time() - start_time < timeout:
            current_state, path = queue.pop(0)
            nodes_explored += 1
            
            if current_state in visited:
                continue
                
            visited.add(current_state)
            
            if current_state.is_goal():
                end_time = time.time()
                current_memory, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                return True, path, {
                    "time": end_time - start_time,
                    "nodes_explored": nodes_explored,
                    "path_length": len(path),
                    "memory_current": current_memory / 1024,
                    "memory_peak": peak_memory / 1024,
                    "solution_found": True
                }
                
            if current_state.is_deadlock():
                continue
                
            for successor in current_state.get_successors():
                if successor not in visited:
                    direction = self.get_direction(current_state.player, successor.player)
                    if direction:
                        queue.append((successor, path + [direction]))
        
        end_time = time.time()
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return False, None, {
            "time": end_time - start_time,
            "nodes_explored": nodes_explored,
            "path_length": 0,
            "memory_current": current_memory / 1024,
            "memory_peak": peak_memory / 1024,
            "solution_found": False
        }

    def run_dfs(self, state, timeout=10):
        """Run DFS with performance tracking"""
        visited = set()
        stack = [(state, [])]
        nodes_explored = 0
        
        start_time = time.time()
        tracemalloc.start()
        
        while stack and time.time() - start_time < timeout:
            current_state, path = stack.pop()
            nodes_explored += 1
            
            if current_state in visited:
                continue
                
            visited.add(current_state)
            
            if current_state.is_goal():
                end_time = time.time()
                current_memory, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                return True, path, {
                    "time": end_time - start_time,
                    "nodes_explored": nodes_explored,
                    "path_length": len(path),
                    "memory_current": current_memory / 1024,
                    "memory_peak": peak_memory / 1024,
                    "solution_found": True
                }
                
            if current_state.is_deadlock():
                continue
                
            for successor in reversed(current_state.get_successors()):
                if successor not in visited:
                    direction = self.get_direction(current_state.player, successor.player)
                    if direction:
                        stack.append((successor, path + [direction]))
        
        end_time = time.time()
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return False, None, {
            "time": end_time - start_time,
            "nodes_explored": nodes_explored,
            "path_length": 0,
            "memory_current": current_memory / 1024,
            "memory_peak": peak_memory / 1024,
            "solution_found": False
        }

    def run_astar(self, state, timeout=10):
        """Run A* with performance tracking"""
        import heapq
        
        # Priority queue for A*
        open_set = []
        # Dictionary to store path to each state
        came_from = {}
        # Dictionary to store g_score for each state
        g_score = {state: 0}
        # Dictionary to store f_score for each state
        f_score = {state: self.heuristic(state)}
        
        # Add initial state to open set
        heapq.heappush(open_set, (f_score[state], id(state), state, []))
        
        nodes_explored = 0
        visited = set()
        
        start_time = time.time()
        tracemalloc.start()
        
        while open_set and time.time() - start_time < timeout:
            _, _, current, path = heapq.heappop(open_set)
            nodes_explored += 1
            
            if current in visited:
                continue
                
            visited.add(current)
            
            if current.is_goal():
                end_time = time.time()
                current_memory, peak_memory = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                return True, path, {
                    "time": end_time - start_time,
                    "nodes_explored": nodes_explored,
                    "path_length": len(path),
                    "memory_current": current_memory / 1024,
                    "memory_peak": peak_memory / 1024,
                    "solution_found": True
                }
                
            if current.is_deadlock():
                continue
                
            for successor in current.get_successors():
                if successor in visited:
                    continue
                    
                direction = self.get_direction(current.player, successor.player)
                if not direction:
                    continue
                    
                tentative_g_score = g_score[current] + 1
                
                if successor not in g_score or tentative_g_score < g_score[successor]:
                    # This path to successor is better than any previous one
                    g_score[successor] = tentative_g_score
                    f_score[successor] = tentative_g_score + self.heuristic(successor)
                    
                    # Add successor to open set
                    heapq.heappush(open_set, (f_score[successor], id(successor), successor, path + [direction]))
        
        end_time = time.time()
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return False, None, {
            "time": end_time - start_time,
            "nodes_explored": nodes_explored,
            "path_length": 0,
            "memory_current": current_memory / 1024,
            "memory_peak": peak_memory / 1024,
            "solution_found": False
        }

    def heuristic(self, state):
        """Simple Manhattan distance heuristic for A*"""
        targets = state.get_targets()
        boxes = state.boxes
        
        if len(boxes) == 0 or len(targets) == 0:
            return 0
            
        # Calculate total Manhattan distance from each box to its nearest target
        total_distance = 0
        for box in boxes:
            min_distance = float('inf')
            for target in targets:
                distance = abs(box[0] - target[0]) + abs(box[1] - target[1])
                min_distance = min(min_distance, distance)
            total_distance += min_distance
            
        return total_distance

    def get_direction(self, from_pos, to_pos):
        """Get direction character from position change"""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        if dx == -1 and dy == 0:
            return "U"
        elif dx == 1 and dy == 0:
            return "D"
        elif dx == 0 and dy == -1:
            return "L"
        elif dx == 0 and dy == 1:
            return "R"
        else:
            return None

    def compare_algorithms(self):
        """Compare all three algorithms on the current level"""
        if self.gui_init.game_completed or self.gui_init.solving or self.gui_init.animation_in_progress or self.gui_init.undo_animation_in_progress:
            return
            
        print("Comparing algorithms...")
        state = State.from_game(self.gui_init.game)
        
        # Run all three algorithms
        _, _, bfs_metrics = self.run_bfs(state)
        _, _, dfs_metrics = self.run_dfs(state)
        _, _, astar_metrics = self.run_astar(state)
        
        # Store results
        self.gui_init.comparison_results = {
            "BFS": bfs_metrics,
            "DFS": dfs_metrics,
            "A*": astar_metrics
        }
        
        # Print comparison results
        print("\n=== Algorithm Comparison ===")
        print(f"{'Algorithm':<10} {'Time (s)':<10} {'Nodes':<10} {'Path Length':<12} {'Memory (KB)':<12}")
        print("-" * 60)
        
        for algo, metrics in self.gui_init.comparison_results.items():
            path_length = metrics["path_length"] if metrics["solution_found"] else "N/A"
            print(f"{algo:<10} {metrics['time']:<10.4f} {metrics['nodes_explored']:<10} {path_length:<12} {metrics['memory_peak']:<12.2f}")
        
        # Set up display
        self.gui_init.comparing = True
        self.gui_init.comparison_start_time = pygame.time.get_ticks()
        self.gui_init.comparison_duration = 15000  # Display for 15 seconds
