import json
from collections import deque

board = "GBB.L.GHI.LMGHIAAMCCCK.M..JKDDEEJFF."

def get_cars(b):
    cars = {}
    for i, c in enumerate(b):
        if c != '.':
            if c not in cars:
                cars[c] = []
            cars[c].append(i)
    return cars

def get_moves(b):
    moves = []
    cars = get_cars(b)
    for c, pos in cars.items():
        is_h = (pos[1] - pos[0] == 1)
        length = len(pos)
        if is_h:
            # try left
            steps = 1
            while pos[0] % 6 - steps >= 0 and b[pos[0] - steps] == '.':
                nb = list(b)
                for p in pos: nb[p] = '.'
                for p in pos: nb[p - steps] = c
                moves.append((''.join(nb), c, 'LEFT', steps))
                steps += 1
            # try right
            steps = 1
            while pos[-1] % 6 + steps < 6 and b[pos[-1] + steps] == '.':
                nb = list(b)
                for p in pos: nb[p] = '.'
                for p in pos: nb[p + steps] = c
                moves.append((''.join(nb), c, 'RIGHT', steps))
                steps += 1
        else:
            # try up
            steps = 1
            while pos[0] // 6 - steps >= 0 and b[pos[0] - steps * 6] == '.':
                nb = list(b)
                for p in pos: nb[p] = '.'
                for p in pos: nb[p - steps * 6] = c
                moves.append((''.join(nb), c, 'UP', steps))
                steps += 1
            # try down
            steps = 1
            while pos[-1] // 6 + steps < 6 and b[pos[-1] + steps * 6] == '.':
                nb = list(b)
                for p in pos: nb[p] = '.'
                for p in pos: nb[p + steps * 6] = c
                moves.append((''.join(nb), c, 'DOWN', steps))
                steps += 1
    return moves

def solve(start):
    q = deque([(start, [])])
    visited = {start}
    
    while q:
        curr, path = q.popleft()
        
        # Check if A reached the exit (col 5)
        # A is at row 2, which is index 12..17. The rightmost index of A should be 17.
        cars = get_cars(curr)
        if cars['A'][-1] % 6 == 5:
            return path
            
        for nxt_board, piece, direction, spaces in get_moves(curr):
            if nxt_board not in visited:
                visited.add(nxt_board)
                q.append((nxt_board, path + [(piece, direction, spaces)]))
                
    return None

path = solve(board)

if path:
    solution_steps = []
    for i, (piece, direction, spaces) in enumerate(path):
        solution_steps.append({
            "step_number": i + 1,
            "piece": piece,
            "direction": direction,
            "spaces": spaces
        })
        
    result = {
        "difficulty_level": "51-moves-hardest",
        "total_moves": len(path),
        "solution_steps": solution_steps
    }
    
    with open('rushhour_solution.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Solved in {len(path)} moves. Saved to rushhour_solution.json.")
else:
    print("No solution found.")
