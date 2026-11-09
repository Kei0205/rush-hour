import json
import re

with open('hardest_50.json', 'r', encoding='utf-8') as f:
    levels = json.load(f)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

options = '    <select id="stageSelect" onchange="changeStage()">\n'
options += '      <option value="0">ステージ 1 (初級 - 15手)</option>\n'
options += '      <option value="1">ステージ 2 (中級 - 14手)</option>\n'
options += '      <option value="2">ステージ 3 (上級 - 30手)</option>\n'
options += '      <option value="3">ステージ 4 (激ムズ - 32手)</option>\n'
for i, level in enumerate(levels):
    options += f'      <option value="{i+4}">最高難易度 {i+1} ({level["moves"]}手)</option>\n'
options += '    </select>'

# Replace select element using simpler regex
html = re.sub(r'<select[^>]*>.*?</select>', options, html, flags=re.DOTALL)

stages_str = '[\n'
stages_str += '      "Y..G..Y..GOO.XXC....BCPP..BVVT..B..T", // Stage 1\n'
stages_str += '      "CCC.B..DDDBEAXX.BEAF.HHKAFG..K.FGII.", // Stage 2\n'
stages_str += '      "O.FFF.OCCC.HDJEXXHDJEBBH.JEAIIGGGA..", // Stage 3\n'
stages_str += '      ".DDDGBF...GBFCXXGBNCJJ..NCIEEEAAI.HH", // Stage 4\n'
for level in levels:
    stages_str += f'      "{level["board"]}",\n'
stages_str += '    ]'

# Replace stages array
html = re.sub(r'const stages = \[.*?\];', 'const stages = ' + stages_str + ';', html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Updated HTML successfully!')
