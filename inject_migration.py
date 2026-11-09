import json
with open('mapping.json', 'r') as f:
    mapping = json.load(f)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

migration_js = f'''
    // Migration v3 for re-indexed stages
    if (!localStorage.getItem('rushhour_migration_v3')) {{
        const mapping = {json.dumps(mapping)};
        
        const newCleared = {{}};
        for (let k in clearedStages) {{
            if (mapping[k]) newCleared[mapping[k]] = clearedStages[k];
        }}
        clearedStages = newCleared;
        
        const newTotal = {{}};
        for (let k in stageTotalTimes) {{
            if (mapping[k]) newTotal[mapping[k]] = stageTotalTimes[k];
        }}
        stageTotalTimes = newTotal;
        
        localStorage.setItem('rushhour_cleared_v2', JSON.stringify(clearedStages));
        localStorage.setItem('rushhour_stage_total_times', JSON.stringify(stageTotalTimes));
        localStorage.setItem('rushhour_migration_v3', 'true');
    }}
'''

html = html.replace("let stageTotalTimes = JSON.parse(localStorage.getItem('rushhour_stage_total_times') || '{}');", "let stageTotalTimes = JSON.parse(localStorage.getItem('rushhour_stage_total_times') || '{}');\n" + migration_js)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
