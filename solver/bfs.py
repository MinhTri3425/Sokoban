from collections import deque
from solver.utils import reconstruct_path
import time
import tracemalloc  # Thư viện đo bộ nhớ

def bfs(start_state, max_depth=None, timeout=None):
    visited = set()
    queue = deque([(start_state, None, 0)])  # Thêm depth vào hàng đợi
    parent = dict()
    node_count = 0

    tracemalloc.start()
    start_time = time.time()

    while queue:
        current, prev, depth = queue.popleft()

        # Check timeout
        if timeout is not None and (time.time() - start_time) > timeout:
            print("Timeout exceeded.")
            break

        #Check depth limit
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
            print("BFS Completed")
            print("Node count:", node_count)
            print("Execution time:", round(end_time - start_time, 4), "seconds")
            print("Memory used:", round(mem_current / 1024, 2), "KB")
            print("Memory peak:", round(mem_peak / 1024, 2), "KB")
            return reconstruct_path(current, parent)

        if current.is_deadlock():
            continue

        for next_state in current.get_successors():
            if next_state not in visited:
                queue.append((next_state, current, depth + 1))

    tracemalloc.stop()
    print("No solution found.")
    print("Node count:", node_count)
    return None
