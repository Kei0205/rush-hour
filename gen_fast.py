import json
import random
import math
from collections import deque

def get_cars(board):
    cars = {}
    for i, c in enumerate(board):
        if c not in ('o', 'x'):
            if c not in cars:
                cars[c] = []
            cars[c].append(i)
    return cars

def get_moves(board):
    size = 6
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

def generate_from_seed(seed_board, target_moves, max_samples=5):
    # reverse BFS to find boards at specific depths
    q = deque([(seed_board, 0)])
    visited = {seed_board}
    results = []
    
    # Target car must not be solved
    # and we record states at depth D
    while q:
        curr, dist = q.popleft()
        
        if dist >= target_moves[0] and dist <= target_moves[1]:
            # verify it can't be solved in fewer moves
            # (since we did reverse BFS from a solved state, dist is the exact shortest path to this solved state)
            # but wait, is the initial state the ONLY solved state? 
            # In rush hour, the target car just needs to exit.
            pass
            
        if dist > target_moves[1]:
            break
            
        for nxt in get_moves(curr):
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, dist + 1))
                if target_moves[0] <= dist + 1 <= target_moves[1]:
                    # Quick check if target car is not already at exit
                    cars = get_cars(nxt)
                    if 'A' in cars and cars['A'][-1] % 6 != 5:
                        results.append((nxt, dist + 1))
                        if len(results) > 500:
                            q.clear()
                            break
    
    if results:
        return random.sample(results, min(max_samples, len(results)))
    return []

# Known solved state
# Let's just create some random boards, solve them to find their true depth, and pick ones in range
def solve(start):
    size = 6
    b = start.replace('.', 'o')
    target = 'A' if 'A' in b else 'X'
    if target not in b: return -1
    def is_solved(board):
        cars = get_cars(board)
        return cars[target][-1] % size == size - 1
    q = deque([(b, 0)])
    visited = {b}
    while q:
        curr, dist = q.popleft()
        if is_solved(curr): return dist
        for nxt in get_moves(curr):
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, dist + 1))
    return -1

# Instead of random generation, I'll use Fogleman's approach or mutate existing boards.
import sys
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
import re
m = re.search(r'const stages = (\[.*?\]);', html, flags=re.DOTALL)
stages = json.loads(m.group(1))

# We have 33 stages. Most are 50 moves. 
# Let's take a few 50 move stages, and do random walks from them, evaluating the new boards.
# Actually, random walk from a 50-move board might create a 15-move board.

new_stages = []
for s in stages:
    if s['moves'] < 50:
        new_stages.append(s)
    if len(new_stages) > 10:
        break

# I will just write a few classic Rush Hour boards manually.
classic = [
    # Card 1 (Beginner)
    ("AAoOooP.oOooP..BCC..oB.o..oDDd..oooo", 8),
    # Card 2 (Beginner)
    ("oAAo.o...o.o..BCCo..Bo.o..ooo.DDDo..", 8),
    # Card 9 (Intermediate)
    ("oBBBo..P..o..P.AA..P.CC..o..o..DDDo.", 14),
    # Card 13 (Intermediate)
    ("oooB..oooB..oAA.CD.E..CD.E..FF.E..GG", 15),
    # Card 21 (Advanced)
    ("oBBo....o...oAAo.o.C.Do..C.D..EEED..", 22),
    # Card 23 (Advanced)
    ("BBo...P....oP.AAo.P..C..oooC..oDDDo.", 24),
    # Card 32 (Expert)
    ("oBBBo.o..C.ooAA.C.oD.E..oD.E..FF.E..", 35),
    # Card 36 (Expert)
    (".BB.C..D..C..DAA...E..o...E..FFo..GG", 32),
]

for b, claimed in classic:
    b = b.replace('.', 'o').replace('d', 'D') # just fixing up
    board_str = b[:36]
    moves = solve(board_str)
    if moves > 0:
        new_stages.append({
            "board": board_str,
            "moves": moves,
            "name": "追加",
            "catchphrase": f"手数: {moves}",
            "exitRow": board_str.index('A') // 6
        })

print(f"Generated {len(new_stages)} stages.")
with open('new_stages.json', 'w', encoding='utf-8') as f:
    json.dump(new_stages, f, ensure_ascii=False, indent=2)
