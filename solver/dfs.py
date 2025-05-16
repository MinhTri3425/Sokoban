from collections import deque
from solver.utils import reconstruct_path
import time
import tracemalloc

def dfs(start_state):
    visited = set()
    stack = deque()
    parent = dict()
    node_count = 0

    tracemalloc.start()
    start_time = time.time()

    stack.append(start_state)
    visited.add(start_state)
    parent[start_state]  = None

    while stack:
        current = stack.pop()
        node_count+=1


        if current.is_goal():
            end_time = time.time()
            mem_current, mem_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            print("DFS Completed")
            print("Node count:", node_count)
            print("Execution time:", round(end_time - start_time, 4), "seconds")
            print("Memory used:", round(mem_current / 1024, 2), "KB")
            print("Memory peak:", round(mem_peak / 1024, 2), "KB")
            return reconstruct_path(current, parent)

        if current.is_deadlock():
            continue

        for next_state in current.get_successors(): 
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current
                stack.append(next_state)

    tracemalloc.stop()
    print("No solution found.")
    print("Node count:", node_count)
    return None
