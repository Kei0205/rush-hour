import json
from collections import deque
import time

def get_cars(b):
    cars = {}
    for i, c in enumerate(b):
        if c not in ('.', 'o', 'x'):
            if c not in cars:
                cars[c] = []
            cars[c].append(i)
    return cars

def get_moves(b, walls):
    moves = []
    cars = get_cars(b)
    
    for c, pos in cars.items():
        is_h = (pos[1] - pos[0] == 1) if len(pos) > 1 else True # default for len 1? cars are len 2 or 3.
        # Actually in Rush Hour cars are always 2 or 3. If there is a length 1 car, let's just assume horizontal for now?
        # Wait, the user mentioned A is a target.
        if len(pos) == 1:
             is_h = True # Just a fallback
             
        if is_h:
            # try left
            steps = 1
            while pos[0] % 6 - steps >= 0 and b[pos[0] - steps] in ('.', 'o'):
                nb = list(b)
                for p in pos: nb[p] = 'o'
                for p in pos: nb[p - steps] = c
                moves.append((''.join(nb), c, 'LEFT', steps))
                steps += 1
            # try right
            steps = 1
            while pos[-1] % 6 + steps < 6 and b[pos[-1] + steps] in ('.', 'o'):
                nb = list(b)
                for p in pos: nb[p] = 'o'
                for p in pos: nb[p + steps] = c
                moves.append((''.join(nb), c, 'RIGHT', steps))
                steps += 1
        else:
            # try up
            steps = 1
            while pos[0] // 6 - steps >= 0 and b[pos[0] - steps * 6] in ('.', 'o'):
                nb = list(b)
                for p in pos: nb[p] = 'o'
                for p in pos: nb[p - steps * 6] = c
                moves.append((''.join(nb), c, 'UP', steps))
                steps += 1
            # try down
            steps = 1
            while pos[-1] // 6 + steps < 6 and b[pos[-1] + steps * 6] in ('.', 'o'):
                nb = list(b)
                for p in pos: nb[p] = 'o'
                for p in pos: nb[p + steps * 6] = c
                moves.append((''.join(nb), c, 'DOWN', steps))
                steps += 1
    return moves

def solve(start):
    b = start.replace('.', 'o')
    
    # Identify target car 'A' or 'X'
    target = 'A' if 'A' in b else 'X'
    if target not in b:
        return -1 # No target
        
    q = deque([(b, 0)])
    visited = {b}
    
    while q:
        curr, dist = q.popleft()
        
        cars = get_cars(curr)
        target_pos = cars[target][-1]
        
        # Check if won (target car is at rightmost column)
        if target_pos % 6 >= 4:
            # Wait, the winning condition in HTML is `vehicle.col >= 4`.
            # So index % 6 >= 4
            return dist
            
        for nxt_board, piece, direction, spaces in get_moves(curr, None):
            if nxt_board not in visited:
                visited.add(nxt_board)
                q.append((nxt_board, dist + 1))
                
    return -1

with open('hardest_50.json', 'r', encoding='utf-8') as f:
    levels = json.load(f)

stages = []
stages.append({'board': 'CCC.B..DDDBEAXX.BEAF.HHKAFG..K.FGII.', 'moves': 14, 'name': '中級'})
stages.append({'board': 'Y..G..Y..GOO.XXC....BCPP..BVVT..B..T', 'moves': 15, 'name': '初級'})
stages.append({'board': 'O.FFF.OCCC.HDJEXXHDJEBBH.JEAIIGGGA..', 'moves': 30, 'name': '上級'})
stages.append({'board': '.DDDGBF...GBFCXXGBNCJJ..NCIEEEAAI.HH', 'moves': 32, 'name': '激ムズ'})

for lvl in levels:
    stages.append({'board': lvl['board'], 'moves': lvl['moves'], 'name': '最高難易度'})

# We shouldn't sort them here to keep track of original indices, or we can sort them to match the UI.
stages.sort(key=lambda x: x['moves'])

print("Verifying 54 stages...")
for i, stage in enumerate(stages):
    start_time = time.time()
    res = solve(stage['board'])
    elapsed = time.time() - start_time
    status = f"Solved in {res} moves" if res != -1 else "UNSOLVABLE!"
    expected = stage['moves']
    print(f"Stage {i+1} (Expected {expected}): {status} ({elapsed:.2f}s)")
