from State import State
from solver.utils import reconstruct_a_star_path
from heapq import heappush, heappop
from itertools import count
import time



def worker_toBox(state):
    """Tính khoảng cách Manhattan từ người chơi đến thùng gần nhất."""
    player = state.player
    boxes = state.boxes
    min_dist = float('inf')
    for box in boxes:
        dist = abs(player[0] - box[0]) + abs(player[1] - box[1])
        min_dist = min(min_dist, dist)
    return min_dist if min_dist != float('inf') else 0

def box_toDock(state):
    """Tính tổng khoảng cách Manhattan từ mỗi thùng đến đích gần nhất."""
    total = 0
    targets = state.get_targets()
    boxes = state.boxes
    for box in boxes:
        if box in targets:
            continue
        min_dis = float('inf')
        for target in targets:
            dis = abs(box[0] - target[0]) + abs(box[1] - target[1])
            min_dis = min(min_dis, dis)
        total += min_dis
    return total

def heuristic(state):
    """Heuristic kết hợp worker_toBox và box_toDock."""
    return worker_toBox(state) + box_toDock(state)

def a_star(start_state):
    open_set = []  # Danh sách mở: các trạng thái cần khám phá
    closed_set = set()  # Danh sách đóng: các trạng thái đã xử lý
    came_from = {}  # Lưu trạng thái cha
    g_score = {start_state: 0}  # Chi phí từ start đến trạng thái
    f_score = {start_state: heuristic(start_state)}  # Chi phí ước tính tổng
    node_count = 0  # Đếm số node đã xử lý
    counter = count()  # Phân biệt trạng thái có cùng f_score
    start = time.time()

    heappush(open_set, (f_score[start_state], next(counter), start_state))

    while open_set:
        _, _, current = heappop(open_set)  # Lấy trạng thái có f_score thấp nhất
        if current in closed_set:  # Bỏ qua nếu đã xử lý
            continue
        closed_set.add(current)  # Thêm vào closed_set
        node_count += 1

        if current.is_goal():  # Kiểm tra mục tiêu
            end = time.time()
            print("Processing A* ...")
            print("Node visited:", node_count)
            print("Execution time:", round(end - start, 4), "seconds")
            return reconstruct_a_star_path(current, came_from, g_score)

        for neighbor in current.get_successors():  # Kiểm tra các trạng thái con
            if neighbor.is_deadlock() or neighbor in closed_set:  # Bỏ qua nếu kẹt hoặc đã xử lý
                continue
            tentative_g = g_score[current] + 1  # Chi phí đến neighbor qua current
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                heappush(open_set, (f_score[neighbor], next(counter), neighbor))

    return None 
