import json
import re
from collections import deque
import math
import random
import sys

def solve(start):
    size = int(math.sqrt(len(start)))
    b = start.replace('.', 'o')
    target = 'A' if 'A' in b else 'X'
    if target not in b:
        return -1

    def get_cars(board):
        cars = {}
        for i, c in enumerate(board):
            if c not in ('o', 'x'):
                if c not in cars:
                    cars[c] = []
                cars[c].append(i)
        return cars

    def get_moves(board):
        moves = []
        cars = get_cars(board)
        for c, pos in cars.items():
            is_h = True if len(pos) == 1 else (pos[1] - pos[0] == 1)
            if is_h:
                steps = 1
                while pos[0] % size - steps >= 0 and board[pos[0] - steps] == 'o':
                    nb = list(board)
                    for p in pos: nb[p] = 'o'
                    for p in pos: nb[p - steps] = c
                    moves.append(''.join(nb))
                    steps += 1
                steps = 1
                while pos[-1] % size + steps < size and board[pos[-1] + steps] == 'o':
                    nb = list(board)
                    for p in pos: nb[p] = 'o'
                    for p in pos: nb[p + steps] = c
                    moves.append(''.join(nb))
                    steps += 1
            else:
                steps = 1
                while pos[0] // size - steps >= 0 and board[pos[0] - steps * size] == 'o':
                    nb = list(board)
                    for p in pos: nb[p] = 'o'
                    for p in pos: nb[p - steps * size] = c
                    moves.append(''.join(nb))
                    steps += 1
                steps = 1
                while pos[-1] // size + steps < size and board[pos[-1] + steps * size] == 'o':
                    nb = list(board)
                    for p in pos: nb[p] = 'o'
                    for p in pos: nb[p + steps * size] = c
                    moves.append(''.join(nb))
                    steps += 1
        return moves

    def is_solved(board):
        cars = get_cars(board)
        return cars[target][-1] % size == size - 1

    q = deque([(b, 0)])
    visited = {b}
    while q:
        curr, dist = q.popleft()
        if is_solved(curr):
            return dist
        for nxt in get_moves(curr):
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, dist + 1))
    return -1


def generate_puzzle(size=6, target_moves_range=(10, 35)):
    letters = 'BCDEFGHIJKLMNOPQRSTUVWYZ'
    target_row = 2
    
    grid = ['o'] * (size * size)
    
    # Place target car (A) at target_row, random col 0-2
    col = random.randint(0, 2)
    grid[target_row * size + col] = 'A'
    grid[target_row * size + col + 1] = 'A'
    
    num_vehicles = random.randint(7, 12)
    letter_idx = 0
    
    for _ in range(200):
        if letter_idx >= num_vehicles or letter_idx >= len(letters):
            break
        
        length = random.choices([2, 3], weights=[3, 1])[0]
        horizontal = random.choice([True, False])
        r = random.randint(0, size - 1)
        c = random.randint(0, size - 1)
        
        if horizontal:
            if c + length > size:
                continue
            positions = [(r, c + i) for i in range(length)]
        else:
            if r + length > size:
                continue
            positions = [(r + i, c) for i in range(length)]
        
        ok = True
        for pr, pc in positions:
            if grid[pr * size + pc] != 'o':
                ok = False
                break
        if not ok:
            continue
        
        ch = letters[letter_idx]
        for pr, pc in positions:
            grid[pr * size + pc] = ch
        letter_idx += 1
    
    if letter_idx < 4:
        return None, -1
    
    board = ''.join(grid)
    moves = solve(board)
    
    if target_moves_range[0] <= moves <= target_moves_range[1]:
        return board, moves
    return None, -1


results = []
targets = [
    (8, 15, 6),
    (14, 22, 6),
    (22, 35, 6),
    (30, 45, 6),
]

sys.stdout.reconfigure(line_buffering=True)

for min_m, max_m, count in targets:
    print(f"Generating {min_m}-{max_m} moves...", flush=True)
    found = 0
    seen = set()
    for attempt in range(100000):
        board, moves = generate_puzzle(target_moves_range=(min_m, max_m))
        if board and board not in seen:
            seen.add(board)
            idx = board.index('A')
            exit_row = idx // 6
            results.append({
                "board": board,
                "moves": moves,
                "exitRow": exit_row,
            })
            found += 1
            print(f"  [{found}/{count}] {moves} moves", flush=True)
            if found >= count:
                break
        if attempt % 10000 == 9999:
            print(f"  ...{attempt+1} attempts, {found} found so far", flush=True)
    print(f"  Done: {found}/{count}", flush=True)

results.sort(key=lambda x: x['moves'])

with open('generated_stages.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nTotal: {len(results)} puzzles generated", flush=True)
for r in results:
    print(f"  {r['moves']} moves: {r['board']}", flush=True)
