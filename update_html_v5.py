import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add global-timer div to #screen-select
html = html.replace('<h1>Rush Hour Ultimate</h1>', '<h1>Rush Hour Ultimate</h1>\n    <div id="global-time" style="color: #cbd5e1; margin-bottom: 24px; font-size: 1.1rem; font-weight: bold; text-align: center;">全ステージ累計思考時間: <span id="global-timer" style="color:#38bdf8">00:00</span></div>')

# 2. Add total-timer to status-bar
html = html.replace('<div>Time: <span id="timer">00:00</span></div>', '<div>今回の記録: <span id="timer">00:00</span></div>\n      <div>累計思考時間: <span id="total-timer">00:00</span></div>')

# 3. Add globalTimerEl and totalTimerEl declarations
html = html.replace("const gameTitle = document.getElementById('game-title');", "const gameTitle = document.getElementById('game-title');\n    const globalTimerEl = document.getElementById('global-timer');\n    const totalTimerEl = document.getElementById('total-timer');")

# 4. Add currentStageTotalTime and currentAttemptTime
html = html.replace('let accumulatedTime = 0;', 'let currentAttemptTime = 0;\n    let currentStageTotalTime = 0;')

# 5. In renderLevelGrid, calculate global time
render_old = '''function renderLevelGrid() {
      levelGrid.innerHTML = '';
      stages.forEach((stage, idx) => {'''
render_new = '''function renderLevelGrid() {
      levelGrid.innerHTML = '';
      let globalTotal = 0;
      for (let k in stageTotalTimes) {
         globalTotal += (stageTotalTimes[k] || 0);
      }
      if (globalTimerEl) globalTimerEl.textContent = formatTime(globalTotal);
      
      stages.forEach((stage, idx) => {'''
html = html.replace(render_old, render_new)

# 6. Change tile meta logic to show total time
meta_old = '''const tmeta = document.createElement('div');
        tmeta.className = 'total-meta';'''
meta_new = '''const tmeta = document.createElement('div');
        tmeta.className = 'total-meta';
        tmeta.style.fontSize = '0.65rem';
        tmeta.style.color = '#94a3b8';
        tmeta.style.marginTop = '4px';'''
html = html.replace(meta_old, meta_new)

# 7. Update initGame to reset currentAttemptTime but NOT currentStageTotalTime
init_old = '''      if (!keepTime) {
        clearInterval(timerInterval);
        timerInterval = null;
        // accumulatedTime is set by launchStage, don't reset it here!
        timerEl.textContent = formatTime(accumulatedTime);
      }'''
init_new = '''      clearInterval(timerInterval);
      timerInterval = null;
      currentAttemptTime = 0;
      currentStageTotalTime = stageTotalTimes[currentStageIndex] || 0;
      timerEl.textContent = formatTime(currentAttemptTime);
      totalTimerEl.textContent = formatTime(currentStageTotalTime);'''
html = html.replace(init_old, init_new)

# 8. launchStage shouldn't set accumulatedTime anymore
html = re.sub(r'accumulatedTime = .*?;', '', html)
html = html.replace('timerEl.textContent = formatTime(accumulatedTime);', '')

# 9. Update setInterval
timer_old = '''            accumulatedTime = Math.floor((Date.now() - startTime) / 1000);
            timerEl.textContent = formatTime(accumulatedTime);
            if (!isWon) {
              stageTotalTimes[currentStageIndex] = accumulatedTime;
              localStorage.setItem('rushhour_stage_total_times', JSON.stringify(stageTotalTimes));
            }'''
timer_new = '''            currentAttemptTime++;
            currentStageTotalTime++;
            timerEl.textContent = formatTime(currentAttemptTime);
            totalTimerEl.textContent = formatTime(currentStageTotalTime);
            if (!isWon) {
              stageTotalTimes[currentStageIndex] = currentStageTotalTime;
              localStorage.setItem('rushhour_stage_total_times', JSON.stringify(stageTotalTimes));
            }'''
html = html.replace(timer_old, timer_new)

# 10. Update win logic to use currentAttemptTime
html = html.replace('const tStr = formatTime(accumulatedTime);', 'const tStr = formatTime(currentAttemptTime);')

# 12. Update formatTime to support hours
format_old = '''function formatTime(sec) {
      const m = Math.floor(sec / 60).toString().padStart(2, '0');
      const s = (sec % 60).toString().padStart(2, '0');
      return m + ':' + s;
    }'''
format_new = '''function formatTime(sec) {
      const h = Math.floor(sec / 3600);
      const m = Math.floor((sec % 3600) / 60).toString().padStart(2, '0');
      const s = (sec % 60).toString().padStart(2, '0');
      return h > 0 ? h + ':' + m + ':' + s : m + ':' + s;
    }'''
html = html.replace(format_old, format_new)

# Update resetGame to not pass true
html = html.replace('initGame(true)', 'initGame()')
html = html.replace('function initGame(keepTime = false) {', 'function initGame() {')

# Cleanup Date.now() logic
html = html.replace('startTime = Date.now() - (accumulatedTime * 1000);', '')
html = html.replace('let startTime = null;', '')
html = html.replace('if (!startTime) {', 'if (!timerInterval) {')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Done!')
