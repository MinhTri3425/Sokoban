from collections import deque
from solver.utils import reconstruct_path
import time
import tracemalloc

def dfs(start_state, max_depth=None, timeout=None):
    visited = set()
    stack = deque([(start_state, None, 0)])  # (state, parent, depth)
    parent = dict()
    node_count = 0

    tracemalloc.start()
    start_time = time.time()

    while stack:
        current, prev, depth = stack.pop()

        # Timeout
        if timeout is not None and (time.time() - start_time) > timeout:
            print("Timeout exceeded.")
            break

        # Depth limit
        if max_depth is not None and depth > max_depth:
            continue

        if current in visited:
            continue
        visited.add(current)
        parent[current] = prev
        node_count += 1

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

        for next_state in reversed(current.get_successors()):  # DFS: duyệt ngược để đúng thứ tự
            if next_state not in visited:
                stack.append((next_state, current, depth + 1))

    tracemalloc.stop()
    print("No solution found.")
    print("Node count:", node_count)
    return None
