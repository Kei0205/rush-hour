import re
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# First remove the broken syncTimes calls
html = html.replace("syncTimes();\n            fetch", "fetch")
html = html.replace("syncTimes();\n      clearInterval", "clearInterval")

# Define the full new sync logic
new_syncLoad = '''
    async function syncTimes() {
        try {
            await fetch('/api/times', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(stageTotalTimes)
            });
        } catch(e) {}
    }

    async function syncLoad() {
      try {
        const [res, timeRes] = await Promise.all([
            fetch('/api/save'),
            fetch('/api/times')
        ]);
        const serverData = await res.json();
        const serverTimes = await timeRes.json();
        
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
        
        let timeUpdated = false;
        const toPushTimes = {};
        for (let k in serverTimes) {
          if (!stageTotalTimes[k] || serverTimes[k] > stageTotalTimes[k]) {
            stageTotalTimes[k] = serverTimes[k];
            timeUpdated = true;
          } else if (stageTotalTimes[k] > serverTimes[k]) {
            toPushTimes[k] = stageTotalTimes[k];
          }
        }
        for (let k in stageTotalTimes) {
          if (!serverTimes[k]) toPushTimes[k] = stageTotalTimes[k];
        }
        
        if (Object.keys(toPushTimes).length > 0) {
          await fetch('/api/times', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(toPushTimes)
          });
        }
        
        if (updated) {
          localStorage.setItem('rushhour_cleared_v2', JSON.stringify(clearedStages));
        }
        if (timeUpdated) {
          localStorage.setItem('rushhour_stage_total_times', JSON.stringify(stageTotalTimes));
        }
        if ((updated || timeUpdated) && screenSelect.style.display !== 'none') {
          renderLevelGrid();
        }
      } catch (e) {
        console.log('API sync failed, playing offline mode', e);
      }
    }
'''

# Find the entire old syncLoad using regex
html = re.sub(r'async function syncLoad\(\) \{.*?\n    \}', new_syncLoad, html, flags=re.DOTALL)

# Insert syncTimes() calls
html = html.replace('function showSelectScreen() {\n      clearInterval(timerInterval);', 'function showSelectScreen() {\n      syncTimes();\n      clearInterval(timerInterval);')
html = html.replace("fetch('/api/save', {", "syncTimes();\n            fetch('/api/save', {")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
