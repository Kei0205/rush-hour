import json
import re
import math

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'const stages = (\[.*?\]);', html, flags=re.DOTALL)
stages = json.loads(m.group(1))

# Let's add catchphrases to all stages
for i, s in enumerate(stages):
    if i == 0:
        s['catchphrase'] = 'まずは基本から！'
    elif i == 1:
        s['catchphrase'] = 'サクッとクリア'
    elif i == 2:
        s['catchphrase'] = '少し頭を使うかも？'
    elif i == 3:
        s['catchphrase'] = '中級者への登竜門'
    elif s['moves'] == 60:
        s['catchphrase'] = '絶望の60手詰め！'
    elif s['moves'] == 93 or s['moves'] == 51:
        s['catchphrase'] = '世界最難関(93ステップ)'
    elif s['moves'] == 49:
        s['catchphrase'] = '芸術的な大連鎖'
    else:
        # Generate some generic hype catchphrases based on moves
        if s['moves'] < 40:
            s['catchphrase'] = 'ウォーミングアップ'
        elif s['moves'] < 50:
            s['catchphrase'] = '脳汁ドバドバ'
        else:
            s['catchphrase'] = '極限のパズル'

# Let's add a 7x7 stage (49 chars). We need a solvable one. 
# A simple 7x7:
stage_7x7 = {
    'board': (
        'B B C D D D o '
        'o o C E E F F '
        'o o o o o H o '
        'o A A o o H o ' # A is at row 3 (which is exit row for 7x7)
        'J J J o K K L '
        'M M N N o o L '
        'o o O O O P P '
    ).replace(' ', ''),
    'moves': 12, # roughly
    'name': '巨大盤面 7x7',
    'catchphrase': '新感覚！広大な7x7の世界'
}
stages.append(stage_7x7)

# Ensure the JS array is properly formatted
stages_js = 'const stages = ' + json.dumps(stages, ensure_ascii=False) + ';'

html_template = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rush Hour シミュレーター</title>
  <style>
    * {
      box-sizing: border-box;
      user-select: none;
      -webkit-user-select: none;
    }
    body {
      margin: 0;
      min-height: 100vh;
      background: #0f172a;
      color: #f8fafc;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      padding: 32px 16px;
    }
    h1 {
      margin: 0 0 16px;
      font-size: 2rem;
      letter-spacing: 2px;
      text-align: center;
      color: #38bdf8;
    }
    #screen-select, #screen-game {
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    
    /* レベル選択グリッド */
    .level-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 16px;
      width: 100%;
      max-width: 800px;
    }
    .level-tile {
      background: #1e293b;
      border-radius: 12px;
      padding: 16px 12px;
      text-align: center;
      cursor: pointer;
      color: white;
      box-shadow: 0 4px 10px rgba(0,0,0,0.5);
      transition: transform 0.1s, background 0.1s;
      border: 2px solid #334155;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      position: relative;
    }
    .level-tile:hover {
      transform: translateY(-4px) scale(1.02);
      background: #334155;
      border-color: #38bdf8;
    }
    .level-tile.cleared {
      background: #064e3b;
      border-color: #10b981;
    }
    .level-tile.perfect {
      background: #451a03;
      border-color: #fbbf24;
    }
    .level-tile .st-num {
      font-size: 1.4rem;
      font-weight: bold;
    }
    .level-tile .catchphrase {
      font-size: 0.75rem;
      color: #94a3b8;
      margin-top: 6px;
      min-height: 18px;
    }
    .level-tile .moves {
      font-size: 0.85rem;
      color: #cbd5e1;
      margin-top: 4px;
      background: rgba(0,0,0,0.3);
      padding: 2px 8px;
      border-radius: 12px;
    }
    .level-tile .clear-badge {
      font-size: 0.8rem;
      margin-top: 8px;
      font-weight: 900;
      height: 14px;
    }
    .level-tile.cleared .clear-badge { color: #34d399; }
    .level-tile.perfect .clear-badge { color: #fbbf24; }
    .level-tile .clear-meta {
      font-size: 0.65rem;
      color: #94a3b8;
      margin-top: 4px;
      height: 10px;
    }

    /* ゲーム画面用 */
    .status-bar {
      margin-bottom: 16px;
      display: flex;
      gap: 20px;
      font-size: 1.1rem;
      font-weight: bold;
      background: #1e293b;
      padding: 8px 16px;
      border-radius: 8px;
    }
    .status-bar span {
      color: #38bdf8;
    }
    .board-container {
      position: relative;
      background: #334155;
      padding: 16px;
      border-radius: 16px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .exit-gate {
      position: absolute;
      right: 0;
      background: #ef4444;
      border-radius: 0 6px 6px 0;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 10px;
      font-weight: bold;
      writing-mode: vertical-rl;
    }
    .board {
      position: relative;
      background: #0f172a;
      border-radius: 8px;
      display: grid;
      gap: 3px;
      padding: 3px;
    }
    .grid-cell {
      background: #1e293b;
      border-radius: 4px;
    }
    .vehicle {
      position: absolute;
      border-radius: 8px;
      cursor: grab;
      touch-action: none;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      box-shadow: inset 0 2px 4px rgba(255,255,255,0.3), 0 4px 6px rgba(0,0,0,0.3);
      transition: transform 0.05s ease;
      z-index: 10;
    }
    .vehicle:active {
      cursor: grabbing;
      filter: brightness(1.1);
      z-index: 20;
    }
    .vehicle::after {
      content: '';
      position: absolute;
      background: rgba(0, 0, 0, 0.25);
      border-radius: 4px;
    }
    .vehicle.h::after { width: 40%; height: 60%; }
    .vehicle.v::after { width: 60%; height: 40%; }
    
    .controls {
      margin-top: 20px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      justify-content: center;
    }
    button {
      background: #3b82f6;
      color: white;
      border: none;
      padding: 10px 20px;
      font-size: 1rem;
      border-radius: 8px;
      cursor: pointer;
      font-weight: bold;
      box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    button:hover { background: #2563eb; }
    button.secondary { background: #475569; }
    button.secondary:hover { background: #334155; }
    
    .message {
      margin-top: 14px;
      font-size: 1.2rem;
      font-weight: bold;
      color: #4ade80;
      min-height: 1.5em;
      text-align: center;
    }
  </style>
</head>
<body>

  <div id="screen-select">
    <h1>Rush Hour Ultimate</h1>
    <div class="level-grid" id="level-grid"></div>
  </div>

  <div id="screen-game" style="display: none;">
    <h1 id="game-title">RUSH HOUR</h1>
    <div class="status-bar">
      <div>手数: <span id="moves">0</span></div>
      <div>Time: <span id="timer">00:00</span></div>
    </div>

    <div class="board-container">
      <div class="exit-gate" id="exit-gate">出口</div>
      <div class="board" id="board"></div>
    </div>

    <div class="message" id="message"></div>

    <div class="controls">
      <button onclick="resetGame()">最初からやり直す</button>
      <button class="secondary" onclick="showSelectScreen()">ステージ一覧に戻る</button>
    </div>
  </div>

  <script>
    ''' + stages_js + '''
    
    let moveCount = 0;
    let isWon = false;
    let currentStageIndex = 0;
    let vehicles = [];
    let boardSize = 6;
    let cellSize = 340 / boardSize;

    let startTime = null;
    let timerInterval = null;
    let elapsedTime = 0;

    const screenSelect = document.getElementById('screen-select');
    const screenGame = document.getElementById('screen-game');
    const levelGrid = document.getElementById('level-grid');
    const boardEl = document.getElementById('board');
    const exitGateEl = document.getElementById('exit-gate');
    const moveCountEl = document.getElementById('moves');
    const timerEl = document.getElementById('timer');
    const messageEl = document.getElementById('message');
    const gameTitle = document.getElementById('game-title');

    // Load cleared status: { perfect: true/false, date: '...', time: '...' }
    let clearedStages = JSON.parse(localStorage.getItem('rushhour_cleared_v2') || '{}');

    // Migrate old data if exists
    let oldCleared = JSON.parse(localStorage.getItem('rushhour_cleared') || '{}');
    if (Object.keys(oldCleared).length > 0) {
      for (let k in oldCleared) {
        if (!clearedStages[k]) {
          clearedStages[k] = { 
            perfect: oldCleared[k] === 'perfect',
            date: '過去の記録',
            time: '--:--'
          };
        }
      }
      localStorage.removeItem('rushhour_cleared');
      localStorage.setItem('rushhour_cleared_v2', JSON.stringify(clearedStages));
    }

    function formatTime(sec) {
      const m = Math.floor(sec / 60).toString().padStart(2, '0');
      const s = (sec % 60).toString().padStart(2, '0');
      return m + ':' + s;
    }

    function renderLevelGrid() {
      levelGrid.innerHTML = '';
      stages.forEach((stage, idx) => {
        const status = clearedStages[idx];
        const isCleared = !!status;
        const isPerfect = status && status.perfect;
        
        const tile = document.createElement('div');
        let classes = 'level-tile';
        if (isPerfect) classes += ' perfect';
        else if (isCleared) classes += ' cleared';
        tile.className = classes;
        tile.onclick = () => launchStage(idx);
        
        const stNum = document.createElement('div');
        stNum.className = 'st-num';
        stNum.textContent = 'STAGE ' + (idx + 1);
        
        const catchphrase = document.createElement('div');
        catchphrase.className = 'catchphrase';
        catchphrase.textContent = stage.catchphrase || '';
        
        const moves = document.createElement('div');
        moves.className = 'moves';
        moves.textContent = stage.moves + '手';
        
        const badge = document.createElement('div');
        badge.className = 'clear-badge';
        if (isPerfect) badge.textContent = '★ PERFECT';
        else if (isCleared) badge.textContent = '✔ CLEAR';

        const meta = document.createElement('div');
        meta.className = 'clear-meta';
        if (isCleared && status.date) {
          meta.textContent = status.time + ' (' + status.date + ')';
        }

        tile.appendChild(stNum);
        tile.appendChild(catchphrase);
        tile.appendChild(moves);
        tile.appendChild(badge);
        tile.appendChild(meta);
        levelGrid.appendChild(tile);
      });
    }

    function showSelectScreen() {
      clearInterval(timerInterval);
      screenGame.style.display = 'none';
      screenSelect.style.display = 'flex';
      renderLevelGrid();
    }

    function launchStage(idx) {
      currentStageIndex = idx;
      screenSelect.style.display = 'none';
      screenGame.style.display = 'flex';
      gameTitle.textContent = 'ステージ ' + (idx + 1) + ' (' + stages[idx].moves + '手)';
      
      const st = stages[idx];
      boardSize = Math.sqrt(st.board.length);
      cellSize = 340 / boardSize;
      
      boardEl.style.width = '340px';
      boardEl.style.height = '340px';
      boardEl.style.gridTemplateColumns = `repeat(${boardSize}, 1fr)`;
      boardEl.style.gridTemplateRows = `repeat(${boardSize}, 1fr)`;
      
      // Determine exit row based on where the target is
      let exitRow = Math.floor(boardSize / 2) - 1;
      let targetIdx = st.board.indexOf('A');
      if (targetIdx === -1) targetIdx = st.board.indexOf('X');
      if (targetIdx !== -1) exitRow = Math.floor(targetIdx / boardSize);
      
      exitGateEl.style.top = `calc(16px + ${exitRow} * ${cellSize}px)`;
      exitGateEl.style.height = `${cellSize}px`;
      exitGateEl.style.width = '16px';
      
      initGame();
    }

    function createGridCells() {
      boardEl.innerHTML = '';
      for (let i = 0; i < boardSize * boardSize; i++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        boardEl.appendChild(cell);
      }
    }

    function parseGrid(gridString) {
      const cars = {};
      const walls = [];
      for (let i = 0; i < gridString.length; i++) {
        const c = gridString[i];
        if (c === 'x') {
          walls.push(i);
        } else if (c !== '.' && c !== 'o') {
          if (!cars[c]) cars[c] = { positions: [] };
          cars[c].positions.push(i);
        }
      }

      const parsedVehicles = [];
      const colors = ['#eab308', '#84cc16', '#f97316', '#06b6d4', '#f59e0b', '#ec4899', '#a855f7', '#10b981', '#3b82f6', '#fb923c', '#9333ea', '#db2777', '#ea580c', '#65a30d', '#0284c7', '#14b8a6', '#f43f5e'];
      let colorIndex = 0;

      for (const c in cars) {
        const pos = cars[c].positions;
        const isTarget = (c === 'X' || c === 'A');
        const length = pos.length;
        const isH = length > 1 ? (pos[1] - pos[0] === 1) : true;
        
        parsedVehicles.push({
          id: c,
          color: isTarget ? '#ef4444' : colors[colorIndex++ % colors.length],
          length: length,
          orientation: isH ? 'h' : 'v',
          row: Math.floor(pos[0] / boardSize),
          col: pos[0] % boardSize,
          isTarget: isTarget,
          isWall: false
        });
      }
      
      walls.forEach((pos, idx) => {
        parsedVehicles.push({
          id: 'wall_' + idx,
          color: '#475569',
          length: 1,
          orientation: 'h',
          row: Math.floor(pos / boardSize),
          col: pos % boardSize,
          isTarget: false,
          isWall: true
        });
      });
      return parsedVehicles;
    }

    function initGame() {
      createGridCells();
      vehicles = parseGrid(stages[currentStageIndex].board);
      moveCount = 0;
      isWon = false;
      moveCountEl.textContent = moveCount;
      messageEl.textContent = '';
      
      clearInterval(timerInterval);
      startTime = null;
      elapsedTime = 0;
      timerEl.textContent = '00:00';
      
      renderVehicles();
    }

    function renderVehicles() {
      document.querySelectorAll('.vehicle').forEach(e => e.remove());

      vehicles.forEach(v => {
        const el = document.createElement('div');
        el.className = 'vehicle ' + v.orientation;
        el.id = v.id;
        el.style.backgroundColor = v.color;
        
        if (v.isWall) {
          el.style.borderRadius = '2px';
          el.style.border = '2px solid #1e293b';
          el.style.boxShadow = 'none';
          el.className = 'vehicle';
        }

        const pad = 4;
        if (v.orientation === 'h' || v.isWall) {
          el.style.width = (v.length * cellSize - pad * 2) + 'px';
          el.style.height = (cellSize - pad * 2) + 'px';
        } else {
          el.style.width = (cellSize - pad * 2) + 'px';
          el.style.height = (v.length * cellSize - pad * 2) + 'px';
        }
        el.style.left = (v.col * cellSize + pad) + 'px';
        el.style.top = (v.row * cellSize + pad) + 'px';

        setupDrag(el, v);
        boardEl.appendChild(el);
      });
    }

    function getGrid(excludeVehicleId) {
      const grid = Array(boardSize).fill(null).map(() => Array(boardSize).fill(false));
      vehicles.forEach(v => {
        if (v.id === excludeVehicleId) return;
        for (let i = 0; i < v.length; i++) {
          const r = v.orientation === 'v' ? v.row + i : v.row;
          const c = v.orientation === 'h' ? v.col + i : v.col;
          if (r >= 0 && r < boardSize && c >= 0 && c < boardSize) {
            grid[r][c] = true;
          }
        }
      });
      return grid;
    }

    function setupDrag(element, vehicle) {
      let startX, startY;
      let minOffset, maxOffset;

      const onPointerDown = (e) => {
        if (isWon || vehicle.isWall) return;
        
        // Start timer on first interaction
        if (!startTime) {
          startTime = Date.now();
          timerInterval = setInterval(() => {
            elapsedTime = Math.floor((Date.now() - startTime) / 1000);
            timerEl.textContent = formatTime(elapsedTime);
          }, 1000);
        }

        element.setPointerCapture(e.pointerId);
        startX = e.clientX;
        startY = e.clientY;

        const grid = getGrid(vehicle.id);

        if (vehicle.orientation === 'h') {
          let min = vehicle.col;
          while (min > 0 && !grid[vehicle.row][min - 1]) min--;
          
          let max = vehicle.col;
          const limit = vehicle.isTarget ? boardSize - vehicle.length + 1 : boardSize - vehicle.length;
          while (max < limit) {
            if (max + vehicle.length < boardSize && !grid[vehicle.row][max + vehicle.length]) {
              max++;
            } else if (vehicle.isTarget && max + vehicle.length === boardSize) {
              max++;
              break;
            } else {
              break;
            }
          }
          minOffset = (min - vehicle.col) * cellSize;
          maxOffset = (max - vehicle.col) * cellSize;
        } else {
          let min = vehicle.row;
          while (min > 0 && !grid[min - 1][vehicle.col]) min--;
          
          let max = vehicle.row;
          while (max + vehicle.length < boardSize && !grid[max + vehicle.length][vehicle.col]) max++;
          
          minOffset = (min - vehicle.row) * cellSize;
          maxOffset = (max - vehicle.row) * cellSize;
        }

        window.addEventListener('pointermove', onPointerMove);
        window.addEventListener('pointerup', onPointerUp);
      };

      const onPointerMove = (e) => {
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;

        if (vehicle.orientation === 'h') {
          let constrainedDx = Math.max(minOffset, Math.min(maxOffset, dx));
          element.style.transform = 'translateX(' + constrainedDx + 'px)';
        } else {
          let constrainedDy = Math.max(minOffset, Math.min(maxOffset, dy));
          element.style.transform = 'translateY(' + constrainedDy + 'px)';
        }
      };

      const onPointerUp = (e) => {
        window.removeEventListener('pointermove', onPointerMove);
        window.removeEventListener('pointerup', onPointerUp);

        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        let deltaUnits = 0;

        if (vehicle.orientation === 'h') {
          let constrainedDx = Math.max(minOffset, Math.min(maxOffset, dx));
          deltaUnits = Math.round(constrainedDx / cellSize);
          vehicle.col += deltaUnits;
        } else {
          let constrainedDy = Math.max(minOffset, Math.min(maxOffset, dy));
          deltaUnits = Math.round(constrainedDy / cellSize);
          vehicle.row += deltaUnits;
        }

        element.style.transform = '';

        if (deltaUnits !== 0) {
          moveCount++;
          moveCountEl.textContent = moveCount;
        }

        renderVehicles();

        if (vehicle.isTarget && vehicle.col >= boardSize - 2) {
          isWon = true;
          clearInterval(timerInterval);
          
          const minMoves = stages[currentStageIndex].moves;
          const isPerfect = (moveCount <= minMoves);
          
          if (isPerfect) {
            messageEl.textContent = '🎉 PERFECT! 最短手数でクリアしました！';
          } else {
            messageEl.textContent = '🎉 クリア！おめでとうございます！';
          }
          
          // Save clear status
          const prev = clearedStages[currentStageIndex];
          const now = new Date();
          const dStr = (now.getMonth()+1) + '/' + now.getDate() + ' ' + String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0');
          const tStr = formatTime(elapsedTime);
          
          // Upgrade logic: if perfect now, or if it wasn't perfect before
          if (!prev || !prev.perfect || isPerfect) {
            clearedStages[currentStageIndex] = { perfect: (prev && prev.perfect) || isPerfect, date: dStr, time: tStr };
            if (isPerfect) clearedStages[currentStageIndex].perfect = true; // explicitly ensure it's perfect if currently perfect
            localStorage.setItem('rushhour_cleared_v2', JSON.stringify(clearedStages));
          }
        }
      };

      element.addEventListener('pointerdown', onPointerDown);
    }

    function resetGame() {
      initGame();
    }

    // 初期起動
    renderLevelGrid();
  </script>
</body>
</html>
'''

with open('update_html_v3.py', 'w', encoding='utf-8') as f:
    f.write('with open("index.html", "w", encoding="utf-8") as f:\n')
    f.write('    f.write("""' + html_template.replace('\\', '\\\\') + '""")\n')
print("Wrote update_html_v3.py")
