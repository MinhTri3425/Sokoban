from State import State
from solver.utils import reconstruct_a_star_path
from heapq import heappush, heappop
from itertools import count
import time



def heuristic(state):
    """Ước lượng chi phí từ trạng thái hiện tại đến trạng thái đích."""
    
    total = 0
    targets = state.get_targets()
    boxes = state.boxes

    # Tính tổng khoảng cách từ mỗi hộp đến mục tiêu gần nhất
    for box in boxes:
        if box in targets:
            continue  # Bỏ qua hộp đã ở mục tiêu

        # Tìm mục tiêu gần nhất
        min_dis = float('inf')
        for target in targets:
            dis = abs(box[0] - target[0]) + abs(box[1] - target[1])
            min_dis = min(min_dis, dis)
        total += min_dis  # Khoảng cách Manhattan cơ bản
  
    return total

def a_star(start_state):
    open_set = []  
    came_from = {}  
    g_score = {start_state: 0}  # Chi phí tính từ điểm bắt đầu đến trạng thái hiện tại
    f_score = {start_state: heuristic(start_state)}  # Chi phí ước tính từ điểm bắt đầu đến đích
    node_count = 0
    counter = count()  # Dùng để phân biệt các trạng thái có cùng f_score
    start = time.time()

    heappush(open_set, (f_score[start_state], next(counter), start_state))  # Đưa trạng thái bắt đầu vào open list

    

    while open_set:
        _, _, current = heappop(open_set)  # Lấy trạng thái có chi phí f_score thấp nhất
        node_count += 1
        # Nếu trạng thái hiện tại là trạng thái hoàn thành
        if current.is_goal():
            end = time.time()
            print("Processing A* ...")
            print("Node visited:", node_count)
            print("Execution time:", round(end - start, 4), "seconds")
            return reconstruct_a_star_path(current, came_from, g_score)

        # Duyệt qua tất cả các trạng thái kế tiếp
        for neighbor in current.get_successors():
            if neighbor.is_deadlock():  # Nếu trạng thái kế tiếp là deadlock thì bỏ qua
                continue
            
            tentative_g = g_score[current] + 1  # Tính toán chi phí đi qua trạng thái kế tiếp
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current  # Lưu lại trạng thái hiện tại là tiền thân của trạng thái kế tiếp
                g_score[neighbor] = tentative_g  # Cập nhật chi phí g_score cho trạng thái kế tiếp
                f_score[neighbor] = tentative_g + heuristic(neighbor)  # Tính f_score cho trạng thái kế tiếp
                heappush(open_set, (f_score[neighbor], next(counter), neighbor))  
                
                  

    
    return None  
