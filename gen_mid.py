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

def is_solved(board):
    cars = get_cars(board)
    target = 'A' if 'A' in board else 'X'
    return cars[target][-1] % 6 == 5

def solve(start):
    size = 6
    b = start.replace('.', 'o')
    target = 'A' if 'A' in b else 'X'
    if target not in b: return -1
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

import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
import re
m = re.search(r'const stages = (\[.*?\]);', html, flags=re.DOTALL)
stages = json.loads(m.group(1))

# Instead of random generation, let's mutate existing hard boards 
# by solving them, then recording all states along all shortest paths? No, that gives solved states.
# How about reverse BFS from a solved state?
solved_state = "ooIoooookoooAAkooLCCoDDLGHEEoLGHFFoo" # wait, target A must be at exit
solved_state = "ooIBBBooIKooAAoKoLCCoDDLGHEEoLGHFFoo"

# Fogleman's hard states:
hard1 = "BBIooMGHIoLMGHAALNGCCKoNooJKDDooJEEx"
hard2 = "ooIBBBooIKooAAJKoLCCJDDLGHEEoLGHFFoo"
hard3 = "xCCoLMooJoLMAAJoLNHIDDDNHIoKEExooKGG"

q = deque([(hard2, solve(hard2))])
visited = {hard2}

mid_level = []
targets = set(range(10, 40))

# Instead of random walk, just do forward BFS. 
# Any state reachable from a 50 move state that takes N moves to solve is just a state on the path!
# Since we have the hard state taking 50 moves, we can just do BFS towards the solution,
# and save one state for each distance N!
q = deque([(hard2, 0)]) # dist from hard2
parent = {hard2: None}

found_target = False
target_state = None
while q:
    curr, _ = q.popleft()
    if is_solved(curr):
        target_state = curr
        break
    for nxt in get_moves(curr):
        if nxt not in parent:
            parent[nxt] = curr
            q.append((nxt, 0))

# Trace back from target_state
path = []
curr = target_state
while curr:
    path.append(curr)
    curr = parent[curr]
path.reverse()

# path[0] is hard2 (50 moves)
# path[-1] is target_state (0 moves)
# A state at path[i] requires exactly len(path) - 1 - i moves to solve!

for i, state in enumerate(path):
    moves = len(path) - 1 - i
    if moves in [10, 15, 20, 25, 30, 35]:
        print(f"Moves {moves}: {state}")
        mid_level.append({
            "board": state,
            "moves": moves,
            "name": "中級～上級",
            "catchphrase": f"手数 {moves} の挑戦",
            "exitRow": state.index('A') // 6
        })

print(f"Generated {len(mid_level)} stages from path.")

# Do it for another hard board to get variety
def get_path_states(start_board):
    target = 'A' if 'A' in start_board else 'X'
    def is_solved_local(board):
        cars = get_cars(board)
        return cars[target][-1] % 6 == 5

    q = deque([(start_board, 0)])
    parent = {start_board: None}
    target_state = None
    while q:
        curr, _ = q.popleft()
        if is_solved_local(curr):
            target_state = curr
            break
        for nxt in get_moves(curr):
            if nxt not in parent:
                parent[nxt] = curr
                q.append((nxt, 0))
    path = []
    curr = target_state
    while curr:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path

path2 = get_path_states(hard3)
for i, state in enumerate(path2):
    moves = len(path2) - 1 - i
    if moves in [12, 18, 24, 28, 33, 38]:
        mid_level.append({
            "board": state,
            "moves": moves,
            "name": "中級～上級",
            "catchphrase": f"手数 {moves} の挑戦",
            "exitRow": state.index('A') // 6
        })

path3 = get_path_states(hard1)
for i, state in enumerate(path3):
    moves = len(path3) - 1 - i
    if moves in [14, 19, 23, 29, 34, 39]:
        mid_level.append({
            "board": state,
            "moves": moves,
            "name": "中級～上級",
            "catchphrase": f"手数 {moves} の挑戦",
            "exitRow": state.index('A') // 6
        })


with open('new_stages_mid.json', 'w', encoding='utf-8') as f:
    json.dump(mid_level, f, ensure_ascii=False, indent=2)

print("Saved.")
