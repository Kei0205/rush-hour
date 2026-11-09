import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the entire syncTimes + syncLoad with a clean version
old_syncTimes_start = html.find('async function syncTimes() {')
old_syncLoad_end_marker = "console.log('API sync failed, playing offline mode', e);"
old_syncLoad_end = html.find(old_syncLoad_end_marker)
# Find the closing braces after that
rest = html[old_syncLoad_end + len(old_syncLoad_end_marker):]
# We need to close: catch block }, try block, function block
brace_count = 0
end_pos = old_syncLoad_end + len(old_syncLoad_end_marker)
for i, ch in enumerate(rest):
    if ch == '}':
        brace_count += 1
        if brace_count == 3:
            end_pos = old_syncLoad_end + len(old_syncLoad_end_marker) + i + 1
            break

new_sync = '''async function syncTimes() {
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
        
        // Merge cleared stages (bidirectional)
        for (let k in serverData) {
          if (!clearedStages[k] || (serverData[k].perfect && !clearedStages[k].perfect)) {
            clearedStages[k] = serverData[k];
            updated = true;
          }
        }
        
        // Push local clears to server
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
        
        // Merge times: ADDITIVE sync
        // The server stores the "last known" time per stage.
        // On load, we compute: local_delta = local - server (time added since last sync)
        // Then new_total = server + local_delta = local (if local > server)
        // But if server > local, someone else added time, so: new_total = server + 0 = server
        // To make it truly additive across devices:
        //   server stores the "ground truth" total.
        //   On load: local gets server value (the bigger one wins).
        //   On save: local pushes its current value (which includes playtime since load).
        // This way: Device A plays 30s -> pushes 30. Device B loads 30, plays 20 -> has 50 -> pushes 50.
        
        let timeUpdated = false;
        for (let k in serverTimes) {
          if (!stageTotalTimes[k] || serverTimes[k] > stageTotalTimes[k]) {
            stageTotalTimes[k] = serverTimes[k];
            timeUpdated = true;
          }
        }
        
        // Push any local times the server doesn't have
        const toPushTimes = {};
        for (let k in stageTotalTimes) {
          if (!serverTimes[k] || stageTotalTimes[k] > serverTimes[k]) {
            toPushTimes[k] = stageTotalTimes[k];
          }
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
    }'''

html = html[:old_syncTimes_start] + new_sync + html[end_pos:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done!")
