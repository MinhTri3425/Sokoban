def reconstruct_path(state, parent):
    """Hàm truy vết đường đi và in ra hướng di chuyển"""
    path = []
    directions = []
    
    # Truy vết đường đi từ goal về start
    while state is not None:
        path.append(state)
        state = parent[state]
    
    # Đảo ngược để có thứ tự từ start đến goal
    path.reverse()
    
    # Tính toán các hướng di chuyển
    for i in range(1, len(path)):
        prev_pos = path[i-1].player
        current_pos = path[i].player
        
        # Tính toán hướng di chuyển
        dx = current_pos[0] - prev_pos[0]
        dy = current_pos[1] - prev_pos[1]
        
        if dx == -1:
            directions.append("U")
        elif dx == 1:
            directions.append("D")
        elif dy == -1:
            directions.append("L")
        elif dy == 1:
            directions.append("R")
        else:
            directions.append("?")  
    
    # In ra kết quả
    print("Solution path:")
    print("".join(directions)) 
    print(f"Total steps: {len(directions)}")
    
    return path, directions


def reconstruct_a_star_path(goal_state, came_from, g_score):
    path = []
    directions = []

    current = goal_state
    while current is not None:
        path.append(current)
        current = came_from.get(current, None)

    path.reverse()

    for i in range(1, len(path)):
        prev_pos = path[i-1].player
        curr_pos = path[i].player
        dx = curr_pos[0] - prev_pos[0]
        dy = curr_pos[1] - prev_pos[1]

        if dx == -1:
            directions.append('U')
        elif dx == 1:
            directions.append('D')
        elif dy == -1:
            directions.append('L')
        elif dy == 1:
            directions.append('R')
        else:
            directions.append('?')

    # In kết quả
    print("Solution path:")
    print("".join(directions))
    print("Total steps:", len(directions))

    # In chi phí (g_score của goal_state)
    cost = g_score.get(goal_state, float('inf'))
    print("Total cost (g_score):", cost)

    return path, directions