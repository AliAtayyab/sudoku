from collections import deque
import copy
import time

EASY = [
    [5, 3, 0,  0, 7, 0,  0, 0, 0],
    [6, 0, 0,  1, 9, 5,  0, 0, 0],
    [0, 9, 8,  0, 0, 0,  0, 6, 0],
    [8, 0, 0,  0, 6, 0,  0, 0, 3],
    [4, 0, 0,  8, 0, 3,  0, 0, 1],
    [7, 0, 0,  0, 2, 0,  0, 0, 6],
    [0, 6, 0,  0, 0, 0,  2, 8, 0],
    [0, 0, 0,  4, 1, 9,  0, 0, 5],
    [0, 0, 0,  0, 8, 0,  0, 7, 9],
]

MEDIUM = [
    [0, 0, 0,  2, 6, 0,  7, 0, 1],
    [6, 8, 0,  0, 7, 0,  0, 9, 0],
    [1, 9, 0,  0, 0, 4,  5, 0, 0],
    [8, 2, 0,  1, 0, 0,  0, 4, 0],
    [0, 0, 4,  6, 0, 2,  9, 0, 0],
    [0, 5, 0,  0, 0, 3,  0, 2, 8],
    [0, 0, 9,  3, 0, 0,  0, 7, 4],
    [0, 4, 0,  0, 5, 0,  0, 3, 6],
    [7, 0, 3,  0, 1, 8,  0, 0, 0],
]

HARD = [
    [0, 0, 0,  0, 0, 0,  0, 0, 0],
    [0, 0, 0,  0, 0, 3,  0, 8, 5],
    [0, 0, 1,  0, 2, 0,  0, 0, 0],
    [0, 0, 0,  5, 0, 7,  0, 0, 0],
    [0, 0, 4,  0, 0, 0,  1, 0, 0],
    [0, 9, 0,  0, 0, 0,  0, 0, 0],
    [5, 0, 0,  0, 0, 0,  0, 7, 3],
    [0, 0, 2,  0, 1, 0,  0, 0, 0],
    [0, 0, 0,  0, 4, 0,  0, 0, 9],
]

VERY_HARD = [
    [8, 0, 0,  0, 0, 0,  0, 0, 0],
    [0, 0, 3,  6, 0, 0,  0, 0, 0],
    [0, 7, 0,  0, 9, 0,  2, 0, 0],
    [0, 5, 0,  0, 0, 7,  0, 0, 0],
    [0, 0, 0,  0, 4, 5,  7, 0, 0],
    [0, 0, 0,  1, 0, 0,  0, 3, 0],
    [0, 0, 1,  0, 0, 0,  0, 6, 8],
    [0, 0, 8,  5, 0, 0,  0, 1, 0],
    [0, 9, 0,  0, 0, 0,  4, 0, 0],
]

def print_board(board):
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("------+-------+------")
        row_str = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str += "| "
            val = board[r][c]
            row_str += (str(val) if val != 0 else ".") + " "
        print(row_str)
    print()

def get_peers(row, col):
    peers = set()
    for c in range(9):
        if c != col:
            peers.add((row, c))
    for r in range(9):
        if r != row:
            peers.add((r, col))
    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3
    for r in range(box_row_start, box_row_start + 3):
        for c in range(box_col_start, box_col_start + 3):
            if (r, c) != (row, col):
                peers.add((r, c))
    return peers

ALL_PEERS = {(r, c): get_peers(r, c) for r in range(9) for c in range(9)}

def build_domains(board):
    domains = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                domains[r][c] = {board[r][c]}
                for (pr, pc) in ALL_PEERS[(r, c)]:
                    domains[pr][pc].discard(board[r][c])
    return domains

def revise(domains, xi_r, xi_c, xj_r, xj_c):
    to_remove = set()
    for v in domains[xi_r][xi_c]:
        if domains[xj_r][xj_c] == {v}:
            to_remove.add(v)
    domains[xi_r][xi_c] -= to_remove
    return len(to_remove) > 0

def ac3(domains):
    queue = deque()
    for r in range(9):
        for c in range(9):
            for (pr, pc) in ALL_PEERS[(r, c)]:
                queue.append(((r, c), (pr, pc)))
    while queue:
        (xi_r, xi_c), (xj_r, xj_c) = queue.popleft()
        if revise(domains, xi_r, xi_c, xj_r, xj_c):
            if len(domains[xi_r][xi_c]) == 0:
                return False
            for (pr, pc) in ALL_PEERS[(xi_r, xi_c)]:
                if (pr, pc) != (xj_r, xj_c):
                    queue.append(((pr, pc), (xi_r, xi_c)))
    return True

def forward_check(domains, row, col, val):
    pruned = []
    for (pr, pc) in ALL_PEERS[(row, col)]:
        if val in domains[pr][pc]:
            domains[pr][pc].discard(val)
            pruned.append((pr, pc))
            if len(domains[pr][pc]) == 0:
                return False, pruned
    return True, pruned

def undo_pruning(domains, pruned, val):
    for (r, c) in pruned:
        domains[r][c].add(val)

def pick_next_cell(board, domains):
    best_cell = None
    best_size = 10
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                size = len(domains[r][c])
                if size < best_size:
                    best_size = size
                    best_cell = (r, c)
    return best_cell

def backtrack(board, domains):
    cell = pick_next_cell(board, domains)
    if cell is None:
        return True
    row, col = cell
    for val in sorted(domains[row][col]):
        board[row][col] = val
        saved_domain = set(domains[row][col])
        domains[row][col] = {val}
        ok, pruned = forward_check(domains, row, col, val)
        if ok:
            if backtrack(board, domains):
                return True
        board[row][col] = 0
        domains[row][col] = saved_domain
        undo_pruning(domains, pruned, val)
    return False

def solve(original_board, puzzle_name):
    print("=" * 45)
    print(f"  {puzzle_name}")
    print("=" * 45)
    print("Initial board:")
    print_board(original_board)
    board = copy.deepcopy(original_board)
    domains = build_domains(board)
    if not ac3(domains):
        print("AC-3 found a contradiction – no solution exists.\n")
        return
    start = time.time()
    solved = backtrack(board, domains)
    elapsed = time.time() - start
    if solved:
        print("Solution:")
        print_board(board)
        print(f"  Solved in {elapsed:.4f} seconds\n")
    else:
        print("No solution found.\n")

if __name__ == "__main__":
    solve(EASY,      "Figure 1 – Easy      (easy.txt)")
    solve(MEDIUM,    "Figure 2 – Medium    (medium.txt)")
    solve(HARD,      "Figure 3 – Hard      (hard.txt)")
    solve(VERY_HARD, "Figure 4 – Very Hard (veryhard.txt)")