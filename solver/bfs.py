from collections import deque
from solver.utils import reconstruct_path
from Game import Game
from State import State


def bfs(start_state):
    visited = set()
    queue = deque()
    parent = dict()

    queue.append(start_state)
    visited.add(start_state)
    parent[start_state]=None

    while queue:
        current = queue.popleft()

        if current.is_goal():
            return reconstruct_path(current, parent)
        
        if current.is_deadlock():
            continue #Bo qua trang thai bi ket
        
        for next_state in State.get_successors(current):
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current
                queue.append(next_state)
    return None
        





