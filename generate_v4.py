import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'const stages = (\[.*?\]);', html, flags=re.DOTALL)
stages = json.loads(m.group(1))
stages_js = 'const stages = ' + json.dumps(stages, ensure_ascii=False) + ';'

html_template = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rush Hour シミュレーター</title>
  <style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
    body { margin: 0; min-height: 100vh; background: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 32px 16px; }
    h1 { margin: 0 0 8px; font-size: 2rem; letter-spacing: 2px; text-align: center; color: #38bdf8; }
    #global-time { color: #94a3b8; font-size: 1.1rem; margin-bottom: 24px; font-weight: bold; }
    #screen-select, #screen-game { width: 100%; display: flex; flex-direction: column; align-items: center; }
    
    .level-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 16px; width: 100%; max-width: 800px; }
    .level-tile { background: #1e293b; border-radius: 12px; padding: 16px 12px; text-align: center; cursor: pointer; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: transform 0.1s, background 0.1s; border: 2px solid #334155; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }
    .level-tile:hover { transform: translateY(-4px) scale(1.02); background: #334155; border-color: #38bdf8; }
    .level-tile.cleared { background: #064e3b; border-color: #10b981; }
    .level-tile.perfect { background: #451a03; border-color: #fbbf24; }
    .level-tile .st-num { font-size: 1.4rem; font-weight: bold; }
    .level-tile .catchphrase { font-size: 0.75rem; color: #94a3b8; margin-top: 6px; min-height: 18px; }
    .level-tile .moves { font-size: 0.85rem; color: #cbd5e1; margin-top: 4px; background: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 12px; }
    .level-tile .clear-badge { font-size: 0.8rem; margin-top: 8px; font-weight: 900; height: 14px; }
    .level-tile.cleared .clear-badge { color: #34d399; }
    .level-tile.perfect .clear-badge { color: #fbbf24; }
    .level-tile .clear-meta { font-size: 0.65rem; color: #94a3b8; margin-top: 4px; height: 10px; }
    .level-tile .total-meta { font-size: 0.65rem; color: #64748b; margin-top: 4px; height: 10px; }

    .status-bar { margin-bottom: 16px; display: flex; gap: 16px; font-size: 1rem; font-weight: bold; background: #1e293b; padding: 8px 16px; border-radius: 8px; flex-wrap: wrap; justify-content: center; }
    .status-bar span { color: #38bdf8; }
    .board-container { position: relative; background: #334155; padding: 16px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
    .exit-gate { position: absolute; right: 0; background: #ef4444; border-radius: 0 6px 6px 0; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px; font-weight: bold; writing-mode: vertical-rl; }
    .board { position: relative; background: #0f172a; border-radius: 8px; display: grid; gap: 3px; padding: 3px; }
    .grid-cell { background: #1e293b; border-radius: 4px; }
    .vehicle { position: absolute; border-radius: 8px; cursor: grab; touch-action: none; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: inset 0 2px 4px rgba(255,255,255,0.3), 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.05s ease; z-index: 10; }
    .vehicle:active { cursor: grabbing; filter: brightness(1.1); z-index: 20; }
    .vehicle::after { content: ''; position: absolute; background: rgba(0, 0, 0, 0.25); border-radius: 4px; }
    .vehicle.h::after { width: 40%; height: 60%; }
    .vehicle.v::after { width: 60%; height: 40%; }
    
    .controls { margin-top: 20px; display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
    button { background: #3b82f6; color: white; border: none; padding: 10px 20px; font-size: 1rem; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
    button:hover { background: #2563eb; }
    button.secondary { background: #475569; }
    button.secondary:hover { background: #334155; }
    .message { margin-top: 14px; font-size: 1.2rem; font-weight: bold; color: #4ade80; min-height: 1.5em; text-align: center; }
  </style>
</head>
<body>

  <div id="screen-select">
    <h1>Rush Hour Ultimate</h1>
    <div id="global-time">全ステージ累計思考時間: <span id="global-timer" style="color:#38bdf8">00:00</span></div>
    <div class="level-grid" id="level-grid"></div>
  </div>

  <div id="screen-game" style="display: none;">
    <h1 id="game-title">RUSH HOUR</h1>
    <div class="status-bar">
      <div>手数: <span id="moves">0</span></div>
      <div>今回の記録: <span id="timer">00:00</span></div>
      <div>累計思考時間: <span id="total-timer">00:00</span></div>
    </div>

    <div class="board-container">
      <div class="exit-gate" id="exit-gate">出口</div>
      <div class="board" id="board"></div>
    </div>

    <div class="message" id="message"></div>

    <div class="controls">
      <button onclick="resetGame()">最初からやり直す (タイムリセット)</button>
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

    let timerInterval = null;
    let currentAttemptTime = 0; // Resets on restart
    let currentStageTotalTime = 0; // Accumulated for the stage

    const screenSelect = document.getElementById('screen-select');
    const screenGame = document.getElementById('screen-game');
    const levelGrid = document.getElementById('level-grid');
    const boardEl = document.getElementById('board');
    const exitGateEl = document.getElementById('exit-gate');
    const moveCountEl = document.getElementById('moves');
    const timerEl = document.getElementById('timer');
    const totalTimerEl = document.getElementById('total-timer');
    const messageEl = document.getElementById('message');
    const gameTitle = document.getElementById('game-title');
    const globalTimerEl = document.getElementById('global-timer');

    let clearedStages = JSON.parse(localStorage.getItem('rushhour_cleared_v2') || '{}');
    let stageTotalTimes = JSON.parse(localStorage.getItem('rushhour_stage_total_times') || '{}');

    // Migration from old stageTimes logic
    let oldStageTimes = JSON.parse(localStorage.getItem('rushhour_stage_times') || '{}');
    if (Object.keys(oldStageTimes).length > 0) {
       for (let k in oldStageTimes) {
         if (!stageTotalTimes[k]) stageTotalTimes[k] = oldStageTimes[k];
       }
       localStorage.removeItem('rushhour_stage_times');
       localStorage.setItem('rushhour_stage_total_times', JSON.stringify(stageTotalTimes));
    }

    async function syncLoad() {
      try {
        const res = await fetch('/api/save');
        const serverData = await res.json();
        let updated = false;
        
        for (let k in serverData) {
          if (!clearedStages[k] || (serverData[k].perfect && !clearedStages[k].perfect) || serverData[k].date !== clearedStages[k].date) {
            clearedStages[k] = serverData[k];
            updated = true;
          }
        }
        
        const toPush = {};
        for (let k in clearedStages) {
          if (!serverData[k]) {
            toPush[k] = clearedStages[k];
          }
        }
        if (Object.keys(toPush).length > 0) {
          await fetch('/api/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(toPush)
          });
        }
        
        if (updated) {
          localStorage.setItem('rushhour_cleared_v2', JSON.stringify(clearedStages));
          if (screenSelect.style.display !== 'none') {
            renderLevelGrid();
          }
        }
      } catch (e) {
        console.log('API sync failed, playing offline mode');
      }
    }

    function formatTime(sec) {
      const h = Math.floor(sec / 3600);
      const m = Math.floor((sec % 3600) / 60).toString().padStart(2, '0');
      const s = (sec % 60).toString().padStart(2, '0');
      return h > 0 ? `${h}:${m}:${s}` : `${m}:${s}`;
    }

    function renderLevelGrid() {
      levelGrid.innerHTML = '';
      let globalTotal = 0;
      
      // Calculate global time
      for (let k in stageTotalTimes) {
         globalTotal += (stageTotalTimes[k] || 0);
      }
      globalTimerEl.textContent = formatTime(globalTotal);

      stages.forEach((stage, idx) => {
        const status = clearedStages[idx];
        const isCleared = !!status;
        const isPerfect = status && status.perfect;
        const tot = stageTotalTimes[idx] || 0;
        
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

        const tmeta = document.createElement('div');
        tmeta.className = 'total-meta';
        if (tot > 0) tmeta.textContent = '累計: ' + formatTime(tot);

        tile.appendChild(stNum);
        tile.appendChild(catchphrase);
        tile.appendChild(moves);
        tile.appendChild(badge);
        tile.appendChild(meta);
        tile.appendChild(tmeta);
        levelGrid.appendChild(tile);
      });
    }

    function showSelectScreen() {
      clearInterval(timerInterval);
      timerInterval = null;
      screenGame.style.display = 'none';
      screenSelect.style.display = 'flex';
      renderLevelGrid();
    }

    function launchStage(idx) {
      currentStageIndex = idx;
      screenSelect.style.display = 'none';
      screenGame.style.display = 'flex';
      gameTitle.textContent = 'ステージ ' + (idx + 1) + ' (' + stages[idx].moves + '手)';
      
      boardSize = Math.sqrt(stages[idx].board.length);
      cellSize = 340 / boardSize;
      boardEl.style.width = '340px';
      boardEl.style.height = '340px';
      boardEl.style.gridTemplateColumns = `repeat(${boardSize}, 1fr)`;
      boardEl.style.gridTemplateRows = `repeat(${boardSize}, 1fr)`;
      
      let exitRow = stages[idx].exitRow !== undefined ? stages[idx].exitRow : Math.floor(boardSize / 2) - 1;
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

      let targetChar = 'A';
      if (gridString.indexOf('X') !== -1 && gridString.indexOf('A') !== -1) {
         const xPos = cars['X'] ? cars['X'].positions : [];
         const aPos = cars['A'] ? cars['A'].positions : [];
         if (xPos.length === 2 && xPos[1] - xPos[0] === 1) targetChar = 'X';
         else targetChar = 'A';
      } else if (gridString.indexOf('X') !== -1) {
         targetChar = 'X';
      }

      const parsedVehicles = [];
      const colors = ['#eab308', '#84cc16', '#f97316', '#06b6d4', '#f59e0b', '#ec4899', '#a855f7', '#10b981', '#3b82f6', '#fb923c', '#9333ea', '#db2777', '#ea580c', '#65a30d', '#0284c7', '#14b8a6', '#f43f5e'];
      let colorIndex = 0;

      for (const c in cars) {
        const pos = cars[c].positions;
        const isTarget = (c === targetChar);
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
      timerInterval = null;
      currentAttemptTime = 0;
      currentStageTotalTime = stageTotalTimes[currentStageIndex] || 0;
      
      timerEl.textContent = formatTime(currentAttemptTime);
      totalTimerEl.textContent = formatTime(currentStageTotalTime);
      
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
      let startX, startY, minOffset, maxOffset;

      const onPointerDown = (e) => {
        if (isWon || vehicle.isWall) return;
        
        if (!timerInterval) {
          timerInterval = setInterval(() => {
            currentAttemptTime++;
            currentStageTotalTime++;
            timerEl.textContent = formatTime(currentAttemptTime);
            totalTimerEl.textContent = formatTime(currentStageTotalTime);
            
            stageTotalTimes[currentStageIndex] = currentStageTotalTime;
            localStorage.setItem('rushhour_stage_total_times', JSON.stringify(stageTotalTimes));
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
            if (max + vehicle.length < boardSize && !grid[vehicle.row][max + vehicle.length]) max++;
            else if (vehicle.isTarget && max + vehicle.length === boardSize) { max++; break; }
            else break;
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
          element.style.transform = 'translateX(' + Math.max(minOffset, Math.min(maxOffset, dx)) + 'px)';
        } else {
          element.style.transform = 'translateY(' + Math.max(minOffset, Math.min(maxOffset, dy)) + 'px)';
        }
      };

      const onPointerUp = (e) => {
        window.removeEventListener('pointermove', onPointerMove);
        window.removeEventListener('pointerup', onPointerUp);

        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        let deltaUnits = 0;

        if (vehicle.orientation === 'h') {
          deltaUnits = Math.round(Math.max(minOffset, Math.min(maxOffset, dx)) / cellSize);
          vehicle.col += deltaUnits;
        } else {
          deltaUnits = Math.round(Math.max(minOffset, Math.min(maxOffset, dy)) / cellSize);
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
          timerInterval = null;
          
          const minMoves = stages[currentStageIndex].moves;
          const isPerfect = (moveCount <= minMoves);
          
          if (isPerfect) messageEl.textContent = '🎉 PERFECT! 最短手数でクリアしました！';
          else messageEl.textContent = '🎉 クリア！おめでとうございます！';
          
          const prev = clearedStages[currentStageIndex];
          const now = new Date();
          const dStr = (now.getMonth()+1) + '/' + now.getDate() + ' ' + String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0');
          const tStr = formatTime(currentAttemptTime);
          
          if (!prev || !prev.perfect || isPerfect) {
            clearedStages[currentStageIndex] = { perfect: (prev && prev.perfect) || isPerfect, date: dStr, time: tStr };
            if (isPerfect) clearedStages[currentStageIndex].perfect = true; 
            localStorage.setItem('rushhour_cleared_v2', JSON.stringify(clearedStages));
            
            fetch('/api/save', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({ [currentStageIndex]: clearedStages[currentStageIndex] })
            }).catch(e => console.log('Save sync error', e));
          }
        }
      };
      element.addEventListener('pointerdown', onPointerDown);
    }

    function resetGame() {
      initGame();
    }

    renderLevelGrid();
    syncLoad();
  </script>
</body>
</html>
'''

with open('update_html_v4.py', 'w', encoding='utf-8') as f:
    f.write('with open("index.html", "w", encoding="utf-8") as f:\\n')
    f.write('    f.write("""' + html_template.replace('\\\\', '\\\\\\\\') + '""")\\n')
"
