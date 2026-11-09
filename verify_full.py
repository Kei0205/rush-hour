import json
import re
from collections import deque
import math

def solve(start):
    size = int(math.sqrt(len(start)))
    b = start.replace('.', 'o')
    
    # Find target
    if 'X' in b and 'A' in b:
        # Check which is horizontal length-2
        xi = b.index('X')
        xp = [i for i, c in enumerate(b) if c == 'X']
        ap = [i for i, c in enumerate(b) if c == 'A']
        if len(xp) == 2 and xp[1] - xp[0] == 1:
            target = 'X'
        else:
            target = 'A'
    elif 'X' in b:
        target = 'X'
    else:
        target = 'A'
    
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

# Load stages
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'const stages = (\[.*?\]);', html, flags=re.DOTALL)
stages = json.loads(m.group(1))

print(f"Total stages: {len(stages)}")
print()

# Check for duplicate boards
boards = {}
for i, s in enumerate(stages):
    b = s['board']
    if b in boards:
        print(f"!!! DUPLICATE: Stage {i+1} is identical to Stage {boards[b]+1}")
    boards[b] = i

print()
print("--- BFS Verification ---")
mismatches = []
for i, s in enumerate(stages):
    claimed = s['moves']
    actual = solve(s['board'])
    status = "OK" if claimed == actual else "MISMATCH"
    if status == "MISMATCH":
        mismatches.append((i+1, claimed, actual))
    print(f"Stage {i+1:2d}: claimed={claimed:2d}  actual={actual:2d}  {status}  [{s.get('catchphrase','')}]")

print()
if mismatches:
    print(f"Found {len(mismatches)} mismatches:")
    for stg, claimed, actual in mismatches:
        print(f"  Stage {stg}: claimed {claimed} but actually {actual}")
else:
    print("All stages verified correct!")

# Count by move count
from collections import Counter
move_counts = Counter(s['moves'] for s in stages)
print()
print("--- Distribution ---")
for mc in sorted(move_counts):
    print(f"  {mc} moves: {move_counts[mc]} stages")
