from collections import deque
from solver.utils import reconstruct_path
from Game import Game
from State import State

def dfs(start_state):
    visited = set()
    stack = deque()
    parent = dict()

    stack.append(start_state)
    visited.add(start_state)
    parent[start_state]  = None

    while stack:
        current = stack.pop()
        
        if current.is_goal():
            return reconstruct_path(current, parent)
        
        if current.is_deadlock():
            continue

        for next_state in State.get_successors(current): 
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current
                stack.append(next_state)
    return None