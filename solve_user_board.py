from collections import deque
import json

def get_cars(b):
    cars = {}
    for i, c in enumerate(b):
        if c not in ('.', 'o', 'x'):
            if c not in cars:
                cars[c] = []
            cars[c].append(i)
    return cars

def get_moves(b):
    moves = []
    cars = get_cars(b)
    for c, pos in cars.items():
        is_h = True if len(pos)==1 else (pos[1] - pos[0] == 1)
        if is_h:
            steps = 1
            while pos[0] % 6 - steps >= 0 and b[pos[0] - steps] in ('.', 'o'):
                nb = list(b)
                for p in pos: nb[p] = 'o'
                for p in pos: nb[p - steps] = c
                moves.append((''.join(nb), c, 'LEFT', steps))
                steps += 1
            steps = 1
            while pos[-1] % 6 + steps < 6 and b[pos[-1] + steps] in ('.', 'o'):
                nb = list(b)
                for p in pos: nb[p] = 'o'
                for p in pos: nb[p + steps] = c
                moves.append((''.join(nb), c, 'RIGHT', steps))
                steps += 1
        else:
            steps = 1
            while pos[0] // 6 - steps >= 0 and b[pos[0] - steps * 6] in ('.', 'o'):
                nb = list(b)
                for p in pos: nb[p] = 'o'
                for p in pos: nb[p - steps * 6] = c
                moves.append((''.join(nb), c, 'UP', steps))
                steps += 1
            steps = 1
            while pos[-1] // 6 + steps < 6 and b[pos[-1] + steps * 6] in ('.', 'o'):
                nb = list(b)
                for p in pos: nb[p] = 'o'
                for p in pos: nb[p + steps * 6] = c
                moves.append((''.join(nb), c, 'DOWN', steps))
                steps += 1
    return moves

start = 'BBKxooDDKoooJooAAMJEELoMFFoLoMGGoHHH'

q = deque([(start, [])])
visited = {start}
while q:
    curr, path = q.popleft()
    cars = get_cars(curr)
    if 'A' in cars and cars['A'][-1] % 6 == 5:
        print('Solved in', len(path))
        print(path)
        break
    for nxt, piece, d, s in get_moves(curr):
        if nxt not in visited:
            visited.add(nxt)
            q.append((nxt, path + [(piece, d, s)]))
