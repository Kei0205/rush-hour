import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

migration_v4_js = '''
    // Migration v4 for cleaning up corrupt indices
    if (!localStorage.getItem('rushhour_migration_v4')) {
        if (clearedStages['32'] && clearedStages['32'].time === '00:01') {
            delete clearedStages['32'];
            delete stageTotalTimes['32'];
        }
        if (clearedStages['33'] && clearedStages['33'].time === '00:01') {
            delete clearedStages['33'];
            delete stageTotalTimes['33'];
        }
        localStorage.setItem('rushhour_cleared_v2', JSON.stringify(clearedStages));
        localStorage.setItem('rushhour_stage_total_times', JSON.stringify(stageTotalTimes));
        localStorage.setItem('rushhour_migration_v4', 'true');
    }
'''

html = html.replace("localStorage.setItem('rushhour_migration_v3', 'true');\n    }", "localStorage.setItem('rushhour_migration_v3', 'true');\n    }\n" + migration_v4_js)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
