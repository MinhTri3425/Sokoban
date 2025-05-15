
class State:
    def __init__(self, player_pos, boxes, map_data):
        self.player = player_pos  
        self.boxes = frozenset(boxes)  #Set [(x,y)] dung lam key
        self.map_data = map_data #2D list

        self.walls = set()
        for i, row in enumerate(map_data):
            for j, val in enumerate(row):
                if val == '#':
                    self.walls.add((i, j))
                    
    def is_goal(self):
        targets = self.get_targets()
        return all(pos in targets for pos in self.boxes)
    
    def get_targets(self):
        targets = set()
        for i, row in enumerate(self.map_data):
            for j, val in enumerate(row):
                if val == '.':
                    targets.add((i,j))
        return targets
    
    def __hash__(self):
        return hash((self.player, self.boxes))
    
    def __eq__(self, other):
        return self.player == other.player and self.boxes == other.boxes

    def get_successors(self):
        """Hàm sinh trạng thái kế tiếp"""
        successors = []
        directions = [(-1,0), (1,0), (0,-1), (0,1)] # Lên xuống trái phải
        rows = len(self.map_data)
        cols = len(self.map_data[0]) if rows > 0 else 0

        for dx, dy in directions:
            px, py = self.player
            new_px, new_py = px + dx, py + dy

            # Kiểm tra biên trước khi truy cập
            if new_px < 0 or new_px >= rows or new_py < 0 or new_py >= cols:
                continue

            # Nếu là tường thì bỏ qua
            if self.map_data[new_px][new_py] == '#':
                continue

            new_boxes = set(self.boxes)
            # Nếu ô tiếp theo là hộp
            if (new_px, new_py) in self.boxes:
                box_new_x, box_new_y = new_px + dx, new_py + dy
                
                # Kiểm tra biên cho hộp
                if (box_new_x < 0 or box_new_x >= rows or 
                    box_new_y < 0 or box_new_y >= cols):
                    continue
                    
                # Kiểm tra sau hộp là tường hoặc hộp khác
                if (self.map_data[box_new_x][box_new_y] == '#' or 
                    (box_new_x, box_new_y) in self.boxes):
                    continue

                new_boxes.remove((new_px, new_py))
                new_boxes.add((box_new_x, box_new_y))
                successors.append(State((new_px, new_py), new_boxes, self.map_data))  
            else:
                successors.append(State((new_px, new_py), new_boxes, self.map_data))

        return successors
    
    def is_deadlock(self):
        """Hàm kiểm tra trạng thái deadlock"""
        rows, cols = len(self.map_data), len(self.map_data[0])
        for (x, y) in self.boxes:
            if self.map_data[x][y] == '.':
                continue  # Không deadlock nếu box đang ở mục tiêu
            walls = ['#']
            # Kiểm tra biên trước khi truy cập
            top = self.map_data[x-1][y] if x > 0 else '#'
            bottom = self.map_data[x+1][y] if x < rows-1 else '#'
            left = self.map_data[x][y-1] if y > 0 else '#'
            right = self.map_data[x][y+1] if y < cols-1 else '#'

            neighbors = [
                (top, left), (top, right),
                (bottom, left), (bottom, right)
            ]
            for a, b in neighbors:
                if a in walls and b in walls:
                    return True  # Bị kẹt góc
        return False

    @staticmethod
    def from_game(game):
        """Ham lay du lieu tu class Game"""
        player = None
        boxes = set()
        map_data = []

        for i, row in enumerate(game.matrix):
            new_row = []
            for j, char in enumerate(row):
                if char == '@':
                    player = (i, j)
                    new_row.append(' ')
                elif char == '$':
                    boxes.add((i, j))
                    new_row.append(' ')
                elif char == '*':
                    boxes.add((i, j))
                    new_row.append('.')  # Box trên đích
                elif char == '+':
                    player = (i, j)
                    new_row.append('.')  # Worker trên đích
                else:
                    new_row.append(char)
            map_data.append(new_row)

        return State(player, boxes, map_data)
