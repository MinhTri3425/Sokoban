from State import State
from solver.utils import reconstruct_a_star_path
from heapq import heappush, heappop
from itertools import count
import time

# === Caching ===
heuristic_cache = {}
visited_states = set()

# === Deadlock cố định (góc) ===
def is_corner_deadlock(pos, walls, targets):
    if pos in targets:
        return False  # không phải deadlock nếu là đích
    x, y = pos
    # Kiểm tra 4 góc
    return ((x - 1, y) in walls and (x, y - 1) in walls) or \
           ((x - 1, y) in walls and (x, y + 1) in walls) or \
           ((x + 1, y) in walls and (x, y - 1) in walls) or \
           ((x + 1, y) in walls and (x, y + 1) in walls)

# === Heuristic cải tiến ===
def worker_toBox(state):
    player = state.player
    min_dist = float('inf')
    for box in state.boxes:
        dist = abs(player[0] - box[0]) + abs(player[1] - box[1])
        min_dist = min(min_dist, dist)
    return min_dist if min_dist != float('inf') else 0

def box_toDock(state):
    total = 0
    targets = state.get_targets()
    boxes = state.boxes
    walls = state.walls
    for box in boxes:
        if box in targets:
            continue
        if is_corner_deadlock(box, walls, targets):
            return float('inf')  # Không thể giải được
        min_dis = float('inf')
        for target in targets:
            dis = abs(box[0] - target[0]) + abs(box[1] - target[1])
            min_dis = min(min_dis, dis)
        total += min_dis
    return total

def count_correct_boxes(state):
    return sum(1 for box in state.boxes if box in state.get_targets())

def heuristic(state):
    if state in heuristic_cache:
        return heuristic_cache[state]
    h = worker_toBox(state) + box_toDock(state)
    bonus = count_correct_boxes(state) * 2
    h -= bonus
    heuristic_cache[state] = h
    return h

# === A* cải tiến ===
def a_star(start_state):
    open_set = []
    closed_set = set()
    came_from = {}
    g_score = {start_state: 0}
    f_score = {start_state: heuristic(start_state)}
    node_count = 0
    counter = count()
    start_time = time.time()

    heappush(open_set, (f_score[start_state], 0, next(counter), start_state))

    while open_set:
        _, _, _, current = heappop(open_set)
        if current in closed_set:
            continue
        closed_set.add(current)
        visited_states.add(current)
        node_count += 1

        if current.is_goal():
            end_time = time.time()
            print("✅ A* Success")
            print("🔢 Node count:", node_count)
            print("⏱️ Time:", round(end_time - start_time, 4), "s")
            print("📏 Path length:", g_score[current])
            return reconstruct_a_star_path(current, came_from, g_score)

        for neighbor in current.get_successors():
            if neighbor in visited_states or neighbor in closed_set:
                continue
            if neighbor.is_deadlock() or box_toDock(neighbor) == float('inf'):
                continue

            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                heappush(open_set, (f_score[neighbor], -count_correct_boxes(neighbor), next(counter), neighbor))

    print("❌ A* failed: no solution found.")
    return None
