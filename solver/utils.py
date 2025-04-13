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
            directions.append("UNKNOWN")  # Trường hợp đặc biệt
    
    # In ra kết quả
    print("Solution path:")
    print("".join(directions)) 
    print(f"Total steps: {len(directions)}")
    
    return path, directions