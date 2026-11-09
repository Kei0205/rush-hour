import json
import re

with open('hardest_50.json', 'r', encoding='utf-8') as f:
    levels = json.load(f)

stages = []
stages.append({'board': 'CCC.B..DDDBEAXX.BEAF.HHKAFG..K.FGII.', 'moves': 14, 'name': '中級'})
stages.append({'board': 'Y..G..Y..GOO.XXC....BCPP..BVVT..B..T', 'moves': 15, 'name': '初級'})
stages.append({'board': 'O.FFF.OCCC.HDJEXXHDJEBBH.JEAIIGGGA..', 'moves': 30, 'name': '上級'})
stages.append({'board': '.DDDGBF...GBFCXXGBNCJJ..NCIEEEAAI.HH', 'moves': 32, 'name': '激ムズ'})

for lvl in levels:
    stages.append({'board': lvl['board'], 'moves': lvl['moves'], 'name': '最高難易度'})

# Sort by moves
stages.sort(key=lambda x: x['moves'])

html = '''<!DOCTYPE html>
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
      background: #1e293b;
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
      grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
      gap: 12px;
      width: 100%;
      max-width: 600px;
    }
    .level-tile {
      background: #334155;
      border-radius: 8px;
      padding: 16px 8px;
      text-align: center;
      cursor: pointer;
      font-weight: bold;
      color: white;
      box-shadow: 0 4px 6px rgba(0,0,0,0.3);
      transition: transform 0.1s, background 0.1s;
      border: 2px solid transparent;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
    .level-tile:hover {
      transform: scale(1.05);
      background: #475569;
    }
    .level-tile.cleared {
      background: #064e3b;
      border-color: #10b981;
    }
    .level-tile .st-num {
      font-size: 1.2rem;
    }
    .level-tile .moves {
      font-size: 0.75rem;
      opacity: 0.7;
      margin-top: 6px;
    }
    .level-tile .clear-badge {
      font-size: 0.7rem;
      color: #34d399;
      margin-top: 4px;
      height: 12px;
    }

    /* ゲーム画面用 */
    .status-bar {
      margin-bottom: 16px;
      display: flex;
      gap: 20px;
      font-size: 1.1rem;
      font-weight: bold;
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
      top: calc(16px + 2 * (340px / 6));
      height: calc(340px / 6);
      width: 16px;
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
      width: 340px;
      height: 340px;
      background: #0f172a;
      border-radius: 8px;
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      grid-template-rows: repeat(6, 1fr);
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
    button:hover {
      background: #2563eb;
    }
    button.secondary {
      background: #475569;
    }
    button.secondary:hover {
      background: #334155;
    }
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
    <h1>ステージ選択</h1>
    <div class="level-grid" id="level-grid"></div>
  </div>

  <div id="screen-game" style="display: none;">
    <h1 id="game-title">RUSH HOUR</h1>
    <div class="status-bar">
      <div>手手数: <span id="moves">0</span></div>
    </div>

    <div class="board-container">
      <div class="exit-gate">出口</div>
      <div class="board" id="board">
        <!-- グリッド背景マス (6x6) -->
      </div>
    </div>

    <div class="message" id="message"></div>

    <div class="controls">
      <button onclick="resetGame()">最初からやり直す</button>
      <button class="secondary" onclick="showSelectScreen()">ステージ一覧に戻る</button>
    </div>
  </div>

  <script>
    const stages = ''' + json.dumps(stages, ensure_ascii=False) + ''';
    
    const BOARD_SIZE = 6;
    const CELL_SIZE = 340 / BOARD_SIZE;
    let moveCount = 0;
    let isWon = false;
    let currentStageIndex = 0;
    let vehicles = [];

    const screenSelect = document.getElementById('screen-select');
    const screenGame = document.getElementById('screen-game');
    const levelGrid = document.getElementById('level-grid');
    const boardEl = document.getElementById('board');
    const moveCountEl = document.getElementById('moves');
    const messageEl = document.getElementById('message');
    const gameTitle = document.getElementById('game-title');

    // Load cleared status
    let clearedStages = JSON.parse(localStorage.getItem('rushhour_cleared') || '{}');

    function renderLevelGrid() {
      levelGrid.innerHTML = '';
      stages.forEach((stage, idx) => {
        const isCleared = !!clearedStages[idx];
        
        const tile = document.createElement('div');
        tile.className = 'level-tile' + (isCleared ? ' cleared' : '');
        tile.onclick = () => launchStage(idx);
        
        const stNum = document.createElement('div');
        stNum.className = 'st-num';
        stNum.textContent = idx + 1;
        
        const moves = document.createElement('div');
        moves.className = 'moves';
        moves.textContent = stage.moves + '手';
        
        const badge = document.createElement('div');
        badge.className = 'clear-badge';
        badge.textContent = isCleared ? '★ CLEAR' : '';

        tile.appendChild(stNum);
        tile.appendChild(moves);
        tile.appendChild(badge);
        levelGrid.appendChild(tile);
      });
    }

    function showSelectScreen() {
      screenGame.style.display = 'none';
      screenSelect.style.display = 'flex';
      renderLevelGrid();
    }

    function launchStage(idx) {
      currentStageIndex = idx;
      screenSelect.style.display = 'none';
      screenGame.style.display = 'flex';
      gameTitle.textContent = 'ステージ ' + (idx + 1) + ' (' + stages[idx].moves + '手)';
      initGame();
    }

    function createGridCells() {
      for (let i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        boardEl.appendChild(cell);
      }
    }

    function parseGrid(gridString) {
      const cars = {};
      const walls = [];
      for (let i = 0; i < 36; i++) {
        const c = gridString[i];
        if (c === 'x') {
          walls.push(i);
        } else if (c !== '.' && c !== 'o') {
          if (!cars[c]) {
            cars[c] = { positions: [] };
          }
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
          row: Math.floor(pos[0] / 6),
          col: pos[0] % 6,
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
          row: Math.floor(pos / 6),
          col: pos % 6,
          isTarget: false,
          isWall: true
        });
      });
      return parsedVehicles;
    }

    function initGame() {
      vehicles = parseGrid(stages[currentStageIndex].board);
      moveCount = 0;
      isWon = false;
      moveCountEl.textContent = moveCount;
      messageEl.textContent = '';
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
          el.style.width = (v.length * CELL_SIZE - pad * 2) + 'px';
          el.style.height = (CELL_SIZE - pad * 2) + 'px';
        } else {
          el.style.width = (CELL_SIZE - pad * 2) + 'px';
          el.style.height = (v.length * CELL_SIZE - pad * 2) + 'px';
        }
        el.style.left = (v.col * CELL_SIZE + pad) + 'px';
        el.style.top = (v.row * CELL_SIZE + pad) + 'px';

        setupDrag(el, v);
        boardEl.appendChild(el);
      });
    }

    function getGrid(excludeVehicleId) {
      const grid = Array(6).fill(null).map(() => Array(6).fill(false));
      vehicles.forEach(v => {
        if (v.id === excludeVehicleId) return;
        for (let i = 0; i < v.length; i++) {
          const r = v.orientation === 'v' ? v.row + i : v.row;
          const c = v.orientation === 'h' ? v.col + i : v.col;
          if (r >= 0 && r < 6 && c >= 0 && c < 6) {
            grid[r][c] = true;
          }
        }
      });
      return grid;
    }

    function setupDrag(element, vehicle) {
      let startX, startY;
      let initialPos;
      let minOffset, maxOffset;

      const onPointerDown = (e) => {
        if (isWon || vehicle.isWall) return;
        element.setPointerCapture(e.pointerId);
        startX = e.clientX;
        startY = e.clientY;

        const grid = getGrid(vehicle.id);

        if (vehicle.orientation === 'h') {
          initialPos = vehicle.col;
          let min = vehicle.col;
          while (min > 0 && !grid[vehicle.row][min - 1]) min--;
          
          let max = vehicle.col;
          const limit = vehicle.isTarget ? BOARD_SIZE - vehicle.length + 1 : BOARD_SIZE - vehicle.length;
          while (max < limit) {
            if (max + vehicle.length < BOARD_SIZE && !grid[vehicle.row][max + vehicle.length]) {
              max++;
            } else if (vehicle.isTarget && max + vehicle.length === BOARD_SIZE) {
              max++;
              break;
            } else {
              break;
            }
          }
          minOffset = (min - vehicle.col) * CELL_SIZE;
          maxOffset = (max - vehicle.col) * CELL_SIZE;
        } else {
          initialPos = vehicle.row;
          let min = vehicle.row;
          while (min > 0 && !grid[min - 1][vehicle.col]) min--;
          
          let max = vehicle.row;
          while (max + vehicle.length < BOARD_SIZE && !grid[max + vehicle.length][vehicle.col]) max++;
          
          minOffset = (min - vehicle.row) * CELL_SIZE;
          maxOffset = (max - vehicle.row) * CELL_SIZE;
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
          deltaUnits = Math.round(constrainedDx / CELL_SIZE);
          vehicle.col += deltaUnits;
        } else {
          let constrainedDy = Math.max(minOffset, Math.min(maxOffset, dy));
          deltaUnits = Math.round(constrainedDy / CELL_SIZE);
          vehicle.row += deltaUnits;
        }

        element.style.transform = '';

        if (deltaUnits !== 0) {
          moveCount++;
          moveCountEl.textContent = moveCount;
        }

        renderVehicles();

        if (vehicle.isTarget && vehicle.col >= 4) {
          isWon = true;
          messageEl.textContent = '🎉 クリア！おめでとうございます！';
          
          // Save clear status
          clearedStages[currentStageIndex] = true;
          localStorage.setItem('rushhour_cleared', JSON.stringify(clearedStages));
        }
      };

      element.addEventListener('pointerdown', onPointerDown);
    }

    function resetGame() {
      initGame();
    }

    // 初期起動
    createGridCells();
    renderLevelGrid();
  </script>
</body>
</html>
'''
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Complete HTML replaced.')
