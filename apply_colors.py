import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We will replace the entire <style> block.
new_style = '''<style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
    body { margin: 0; min-height: 100vh; background: #FFFCF7; color: #544739; font-family: system-ui, -apple-system, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 32px 16px; }
    h1 { margin: 0 0 8px; font-size: 2rem; letter-spacing: 2px; text-align: center; color: #859A93; }
    #global-time { color: #544739; font-size: 1.1rem; margin-bottom: 24px; font-weight: bold; text-align: center; }
    #global-timer { color: #859A93; }
    #screen-select, #screen-game { width: 100%; display: flex; flex-direction: column; align-items: center; }
    
    .level-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 16px; width: 100%; max-width: 800px; }
    .level-tile { background: #ffffff; border-radius: 12px; padding: 16px 12px; text-align: center; cursor: pointer; color: #544739; box-shadow: 0 4px 10px rgba(84, 71, 57, 0.1); transition: transform 0.1s, background 0.1s; border: 2px solid #859A93; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }
    .level-tile:hover { transform: translateY(-4px) scale(1.02); background: #859A93; color: #FFFCF7; border-color: #544739; }
    .level-tile.cleared { background: #f2f7f5; border-color: #859A93; }
    .level-tile.perfect { background: #fdfaf3; border-color: #d97706; }
    .level-tile:hover.cleared, .level-tile:hover.perfect { background: #859A93; border-color: #544739; }
    
    .level-tile .st-num { font-size: 1.4rem; font-weight: bold; }
    .level-tile .catchphrase { font-size: 0.75rem; color: #859A93; margin-top: 6px; min-height: 18px; }
    .level-tile:hover .catchphrase { color: #FFFCF7; opacity: 0.9; }
    .level-tile .moves { font-size: 0.85rem; color: #544739; margin-top: 4px; background: rgba(133, 154, 147, 0.2); padding: 2px 8px; border-radius: 12px; }
    .level-tile:hover .moves { background: rgba(255, 255, 255, 0.3); color: #FFFCF7; }
    
    .level-tile .clear-badge { font-size: 0.8rem; margin-top: 8px; font-weight: 900; height: 14px; }
    .level-tile.cleared .clear-badge { color: #859A93; }
    .level-tile.perfect .clear-badge { color: #d97706; }
    .level-tile:hover .clear-badge { color: #FFFCF7; }
    
    .level-tile .clear-meta { font-size: 0.65rem; color: #859A93; margin-top: 4px; height: 10px; }
    .level-tile .total-meta { font-size: 0.65rem; color: #544739; margin-top: 4px; height: 10px; opacity: 0.8; }
    .level-tile:hover .clear-meta, .level-tile:hover .total-meta { color: #FFFCF7; opacity: 0.9; }

    .status-bar { margin-bottom: 16px; display: flex; gap: 16px; font-size: 1rem; font-weight: bold; background: #ffffff; padding: 8px 16px; border-radius: 8px; flex-wrap: wrap; justify-content: center; border: 2px solid #859A93; color: #544739; }
    .status-bar span { color: #859A93; }
    .board-container { position: relative; background: #e8e3dc; padding: 16px; border-radius: 16px; box-shadow: 0 10px 25px rgba(84, 71, 57, 0.15); }
    .exit-gate { position: absolute; right: 0; background: #d96c5b; border-radius: 0 6px 6px 0; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px; font-weight: bold; writing-mode: vertical-rl; }
    .board { position: relative; background: #544739; border-radius: 8px; display: grid; gap: 3px; padding: 3px; }
    .grid-cell { background: #FFFCF7; border-radius: 4px; }
    .vehicle { position: absolute; border-radius: 8px; cursor: grab; touch-action: none; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: inset 0 2px 4px rgba(255,255,255,0.4), 0 4px 6px rgba(84, 71, 57, 0.4); transition: transform 0.05s ease; z-index: 10; }
    .vehicle:active { cursor: grabbing; filter: brightness(1.1); z-index: 20; }
    .vehicle::after { content: ''; position: absolute; background: rgba(84, 71, 57, 0.15); border-radius: 4px; }
    .vehicle.h::after { width: 40%; height: 60%; }
    .vehicle.v::after { width: 60%; height: 40%; }
    
    .controls { margin-top: 20px; display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
    button { background: #859A93; color: #FFFCF7; border: none; padding: 10px 20px; font-size: 1rem; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(84, 71, 57, 0.2); }
    button:hover { background: #71857f; }
    button.secondary { background: #544739; }
    button.secondary:hover { background: #3e342a; }
    .message { margin-top: 14px; font-size: 1.2rem; font-weight: bold; color: #859A93; min-height: 1.5em; text-align: center; }
  </style>'''

html = re.sub(r'<style>.*?</style>', new_style, html, flags=re.DOTALL)

# Target car color and normal car colors inside parseGrid
html = html.replace("isTarget ? '#ef4444'", "isTarget ? '#d96c5b'")

# Fix tile dynamic inline styles from previous edits that override CSS
html = html.replace("tmeta.style.fontSize = '0.65rem';", "")
html = html.replace("tmeta.style.color = '#94a3b8';", "")
html = html.replace("tmeta.style.marginTop = '4px';", "")
html = html.replace('<span id="global-timer" style="color:#38bdf8">', '<span id="global-timer">')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Updated CSS color scheme!')
