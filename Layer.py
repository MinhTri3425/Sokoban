from enum import IntEnum, auto
# Hiển thị các lớp theo thứ tự 
class Layer(IntEnum):
    FLOOR = auto() # Sàn ở lớp cuối cùng
    DOCK = auto()
    WALL = auto()
    BOX = auto()
    BOX_DOCK = auto()
    WORKER = auto()# Nhân vật chính ở trên cùng của layer
    WORKER_DOCK = auto()