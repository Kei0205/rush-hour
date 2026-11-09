import json
import re

with open('hardest_50.json') as f:
    levels = json.load(f)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace select options
options = '    <select id="stageSelect" onchange="changeStage()">\n'
options += '      <option value="0">ステージ 1 (初級 - 15手)</option>\n'
options += '      <option value="1">ステージ 2 (中級 - 14手)</option>\n'
options += '      <option value="2">ステージ 3 (上級 - 30手)</option>\n'
options += '      <option value="3">ステージ 4 (激ムズ - 32手)</option>\n'
for i, level in enumerate(levels):
    options += f'      <option value="{i+4}">最高難易度 {i+1} ({level["moves"]}手)</option>\n'
options += '    </select>'

html = re.sub(r'<select id="stageSelect" onchange="changeStage()">.*?</select>', options, html, flags=re.DOTALL)

# Replace stages array
stages_str = '[\n'
stages_str += '      "Y..G..Y..GOO.XXC....BCPP..BVVT..B..T", // Stage 1\n'
stages_str += '      "CCC.B..DDDBEAXX.BEAF.HHKAFG..K.FGII.", // Stage 2\n'
stages_str += '      "O.FFF.OCCC.HDJEXXHDJEBBH.JEAIIGGGA..", // Stage 3\n'
stages_str += '      ".DDDGBF...GBFCXXGBNCJJ..NCIEEEAAI.HH", // Stage 4\n'
for level in levels:
    stages_str += f'      "{level["board"]}",\n'
stages_str += '    ]'

html = re.sub(r'const stages = \[.*?\];', 'const stages = ' + stages_str + ';', html, flags=re.DOTALL)

# Replace parseGrid function
parse_grid_func = '''function parseGrid(gridString) {
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
    }'''

html = re.sub(r'function parseGrid\(gridString\) \{.*?return parsedVehicles;\n    \}', parse_grid_func, html, flags=re.DOTALL)

# Add isWall check in setupDrag
setup_drag_start = '''const onPointerDown = (e) => {
        if (isWon || vehicle.isWall) return;'''
html = re.sub(r'const onPointerDown = \(e\) => \{\s*if \(isWon\) return;', setup_drag_start, html)

# Fix wall styling in renderVehicles
render_mod = '''el.style.backgroundColor = v.color;
        if (v.isWall) {
          el.style.borderRadius = '2px';
          el.style.border = '2px solid #334155';
          el.style.boxShadow = 'none';
        }
        
        // Remove windows for walls
        if (v.isWall) {
            el.className = 'vehicle';
        }'''
html = html.replace('el.style.backgroundColor = v.color;', render_mod)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Updated HTML successfully!')
