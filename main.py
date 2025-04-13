
#test thuật toán
# from Game import Game
# from State import State
# from solver.bfs import bfs

# def read_map_from_file(file_path):
#     map_data = []
#     with open(file_path, 'r') as file:
#         for line in file:
#             map_data.append(list(line))
#     return map_data

# def main():
#     file_path = 'Level/level1.txt'
#     map_data = read_map_from_file(file_path)
    
#     # Kiểm tra bản đồ đã đọc đúng chưa
#     print("Map data đã đọc từ file:")
#     for row in map_data:
#         print(' '.join(row))  # In ra mỗi dòng bản đồ

#     # Khởi tạo game
#     game = Game(map_data, [])
    
#     # Chuyển sang State để giải
#     start_state = State.from_game(game)
    
#     # # Kiểm tra xem trạng thái ban đầu đã hợp lệ chưa
#     # print("Trạng thái bắt đầu:", start_state)
    
#     # Chạy BFS
#     print("Đang tìm kiếm lời giải bằng BFS...")
#     solution = bfs(start_state)
    
#     # # Kiểm tra kết quả của BFS
#     # if solution:
#     #     print("Lời giải đã tìm thấy!")
#     #     # In ra lời giải
#     #     for state in solution:
#     #         print(state)  # In trạng thái hoặc thông tin bạn muốn
#     # else:
#     #     print("Không tìm thấy lời giải.")

# if __name__ == "__main__":
#     main()
