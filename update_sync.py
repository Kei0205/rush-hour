import re
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_syncLoad = '''
    async function syncLoad() {
      try {
        const [res, timeRes] = await Promise.all([
            fetch('/api/save'),
            fetch('/api/times')
        ]);
        const serverData = await res.json();
        const serverTimes = await timeRes.json();
        
        let updated = false;
        
        // Merge cleared stages
        for (let k in serverData) {
          if (!clearedStages[k] || (serverData[k].perfect && !clearedStages[k].perfect) || serverData[k].date !== clearedStages[k].date) {
            clearedStages[k] = serverData[k];
            updated = true;
          }
        }
        
        // Push local cleared stages that server doesn't have yet
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
        
        // Merge times (take max)
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
    
    async function syncTimes() {
        try {
            await fetch('/api/times', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(stageTotalTimes)
            });
        } catch(e) {}
    }
'''

start = html.find('async function syncLoad() {')
end = html.find('}', html.find("console.log('API sync failed'", start)) + 5

if start != -1 and end != -1:
    html = html[:start] + new_syncLoad + html[end:]
else:
    print("Could not find syncLoad")

html = html.replace('function showSelectScreen() {\n      clearInterval(timerInterval);', 'function showSelectScreen() {\n      syncTimes();\n      clearInterval(timerInterval);')
html = html.replace("fetch('/api/save', {", "syncTimes();\n            fetch('/api/save', {")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done!")
