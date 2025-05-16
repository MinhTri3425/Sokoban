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
        try:
            # Bắt đầu đo thời gian và bộ nhớ
            tracemalloc.start()
            start_time = time.time()
        
            # Gọi hàm BFS từ module solver
            result = bfs(state)
        
            # Kết thúc đo thời gian và bộ nhớ
            end_time = time.time()
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
        
            if result:
                path, directions = result
                return True, directions, {
                    "time": end_time - start_time,
                    "nodes_explored": len(path) if path else 0,
                    "path_length": len(directions) if directions else 0,
                    "memory_current": current_memory / 1024,
                    "memory_peak": peak_memory / 1024,
                    "solution_found": True
                }
        
            return False, None, {
                "time": end_time - start_time,
                "nodes_explored": 0,
                "path_length": 0,
                "memory_current": current_memory / 1024,
                "memory_peak": peak_memory / 1024,
                "solution_found": False
            }
        except Exception as e:
            print(f"Error in BFS: {e}")
            tracemalloc.stop()
            return False, None, {
                "time": 0,
                "nodes_explored": 0,
                "path_length": 0,
                "memory_current": 0,
                "memory_peak": 0,
                "solution_found": False
            }

    def run_dfs(self, state, timeout=10):
        """Run DFS with performance tracking"""
        try:
            # Bắt đầu đo thời gian và bộ nhớ
            tracemalloc.start()
            start_time = time.time()
        
            # Gọi hàm DFS từ module solver
            result = dfs(state)
        
            # Kết thúc đo thời gian và bộ nhớ
            end_time = time.time()
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
        
            if result:
                path, directions = result
                return True, directions, {
                    "time": end_time - start_time,
                    "nodes_explored": len(path) if path else 0,
                    "path_length": len(directions) if directions else 0,
                    "memory_current": current_memory / 1024,
                    "memory_peak": peak_memory / 1024,
                    "solution_found": True
                }
        
            return False, None, {
                "time": end_time - start_time,
                "nodes_explored": 0,
                "path_length": 0,
                "memory_current": current_memory / 1024,
                "memory_peak": peak_memory / 1024,
                "solution_found": False
            }
        except Exception as e:
            print(f"Error in DFS: {e}")
            tracemalloc.stop()
            return False, None, {
                "time": 0,
                "nodes_explored": 0,
                "path_length": 0,
                "memory_current": 0,
                "memory_peak": 0,
                "solution_found": False
            }

    def run_astar(self, state, timeout=10):
        """Run A* with performance tracking using a custom wrapper"""
        try:
            # Bắt đầu đo thời gian và bộ nhớ
            tracemalloc.start()
            start_time = time.time()
        
            # Tạo wrapper cho thuật toán A*
            result = self.astar_wrapper(state)
        
            # Kết thúc đo thời gian và bộ nhớ
            end_time = time.time()
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
        
            if result:
                path, directions = result
                return True, directions, {
                    "time": end_time - start_time,
                    "nodes_explored": len(path) if path else 0,
                    "path_length": len(directions) if directions else 0,
                    "memory_current": current_memory / 1024,
                    "memory_peak": peak_memory / 1024,
                    "solution_found": True
                }
        
            return False, None, {
                "time": end_time - start_time,
                "nodes_explored": 0,
                "path_length": 0,
                "memory_current": current_memory / 1024,
                "memory_peak": peak_memory / 1024,
                "solution_found": False
            }
        except Exception as e:
            print(f"Error in A*: {e}")
            tracemalloc.stop()
            return False, None, {
                "time": 0,
                "nodes_explored": 0,
                "path_length": 0,
                "memory_current": 0,
                "memory_peak": 0,
                "solution_found": False
            }

    def astar_wrapper(self, start_state):
        """Custom implementation of A* to avoid issues with the original implementation"""
        from collections import deque
        import heapq
        
        # Hàm heuristic
        def heuristic(state):
            targets = state.get_targets()
            boxes = state.boxes
            
            if len(boxes) == 0 or len(targets) == 0:
                return 0
                
            # Tính tổng khoảng cách Manhattan từ mỗi hộp đến mục tiêu gần nhất
            total_distance = 0
            for box in boxes:
                min_distance = float('inf')
                for target in targets:
                    distance = abs(box[0] - target[0]) + abs(box[1] - target[1])
                    min_distance = min(min_distance, distance)
                total_distance += min_distance
                
            return total_distance
        
        # Hàm lấy hướng di chuyển
        def get_direction(from_pos, to_pos):
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
        
        # Triển khai A*
        open_set = []
        closed_set = set()
        g_score = {start_state: 0}
        f_score = {start_state: heuristic(start_state)}
        came_from = {}
        path_directions = {}
        
        # Thêm trạng thái ban đầu vào open_set
        heapq.heappush(open_set, (f_score[start_state], id(start_state), start_state))
        
        while open_set:
            # Lấy trạng thái có f_score thấp nhất
            _, _, current = heapq.heappop(open_set)
            
            # Kiểm tra nếu đã đạt mục tiêu
            if current.is_goal():
                # Tạo đường đi
                path = []
                directions = []
                while current in came_from:
                    path.append(current)
                    directions.append(path_directions[current])
                    current = came_from[current]
                
                path.append(start_state)
                
                # Đảo ngược để có thứ tự từ start đến goal
                path.reverse()
                directions.reverse()
                
                return path, directions
            
            # Thêm vào closed_set
            closed_set.add(current)
            
            # Kiểm tra deadlock
            if current.is_deadlock():
                continue
            
            # Xem xét tất cả các trạng thái kế tiếp
            for next_state in current.get_successors():
                # Bỏ qua nếu đã xem xét
                if next_state in closed_set:
                    continue
                
                # Tính g_score mới
                tentative_g_score = g_score[current] + 1
                
                # Nếu trạng thái mới hoặc g_score tốt hơn
                if next_state not in g_score or tentative_g_score < g_score[next_state]:
                    # Lưu hướng di chuyển
                    direction = get_direction(current.player, next_state.player)
                    
                    # Cập nhật thông tin
                    came_from[next_state] = current
                    path_directions[next_state] = direction
                    g_score[next_state] = tentative_g_score
                    f_score[next_state] = tentative_g_score + heuristic(next_state)
                    
                    # Thêm vào open_set nếu chưa có
                    if next_state not in [item[2] for item in open_set]:
                        heapq.heappush(open_set, (f_score[next_state], id(next_state), next_state))
        
        # Không tìm thấy đường đi
        return None

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
