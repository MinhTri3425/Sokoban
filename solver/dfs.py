from collections import deque
from solver.utils import reconstruct_path
from Game import Game
from State import State
import time
def dfs(start_state):
    visited = set()
    stack = deque()
    parent = dict()
    node_count = 0

    stack.append(start_state)
    visited.add(start_state)
    parent[start_state]  = None

    start = time.time()

    while stack:
        current = stack.pop()
        node_count+=1

        if current.is_goal():
            end = time.time()
            print("Processing DFS ...")
            print("Node count:", node_count)
            print("Execution time:", round(end - start, 4), "seconds")
            return reconstruct_path(current, parent)
        
        if current.is_deadlock():
            continue

        for next_state in current.get_successors(): 
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current
                stack.append(next_state)
    return None