import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_style = '''<style>
    * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
    body { margin: 0; min-height: 100vh; background: #1E182A; color: #FFF6CC; font-family: system-ui, -apple-system, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 32px 16px; }
    h1 { margin: 0 0 8px; font-size: 2rem; letter-spacing: 2px; text-align: center; color: #FFB3B3; }
    #global-time { color: #D6C7E7; font-size: 1.1rem; margin-bottom: 24px; font-weight: bold; text-align: center; }
    #global-timer { color: #FFD1A3; }
    #screen-select, #screen-game { width: 100%; display: flex; flex-direction: column; align-items: center; }
    
    .level-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 16px; width: 100%; max-width: 800px; }
    .level-tile { background: #2C2138; border-radius: 12px; padding: 16px 12px; text-align: center; cursor: pointer; color: #FFF6CC; box-shadow: 0 4px 10px rgba(0,0,0,0.4); transition: transform 0.1s, background 0.1s; border: 2px solid #D6C7E7; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }
    .level-tile:hover { transform: translateY(-4px) scale(1.02); background: #D6C7E7; color: #1E182A; border-color: #FFB3B3; }
    .level-tile.cleared { background: #3B2834; border-color: #FFB3B3; }
    .level-tile.perfect { background: #422D2D; border-color: #FFD1A3; }
    .level-tile:hover.cleared, .level-tile:hover.perfect { background: #FFB3B3; border-color: #1E182A; }
    
    .level-tile .st-num { font-size: 1.4rem; font-weight: bold; }
    .level-tile .catchphrase { font-size: 0.75rem; color: #FFB3B3; margin-top: 6px; min-height: 18px; }
    .level-tile:hover .catchphrase { color: #1E182A; opacity: 0.9; }
    .level-tile.cleared .catchphrase { color: #FFD1A3; }
    .level-tile.perfect .catchphrase { color: #FFF6CC; }
    
    .level-tile .moves { font-size: 0.85rem; color: #FFD1A3; margin-top: 4px; background: rgba(214, 199, 231, 0.15); padding: 2px 8px; border-radius: 12px; }
    .level-tile:hover .moves { background: rgba(30, 24, 42, 0.15); color: #1E182A; }
    
    .level-tile .clear-badge { font-size: 0.8rem; margin-top: 8px; font-weight: 900; height: 14px; }
    .level-tile.cleared .clear-badge { color: #FFB3B3; }
    .level-tile.perfect .clear-badge { color: #FFD1A3; }
    .level-tile:hover .clear-badge { color: #1E182A; }
    
    .level-tile .clear-meta { font-size: 0.65rem; color: #D6C7E7; margin-top: 4px; height: 10px; }
    .level-tile .total-meta { font-size: 0.65rem; color: #D6C7E7; margin-top: 4px; height: 10px; opacity: 0.8; }
    .level-tile:hover .clear-meta, .level-tile:hover .total-meta { color: #1E182A; opacity: 0.9; }

    .status-bar { margin-bottom: 16px; display: flex; gap: 16px; font-size: 1rem; font-weight: bold; background: #2C2138; padding: 8px 16px; border-radius: 8px; flex-wrap: wrap; justify-content: center; border: 2px solid #D6C7E7; color: #FFF6CC; }
    .status-bar span { color: #FFB3B3; }
    .board-container { position: relative; background: #2C2138; padding: 16px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
    .exit-gate { position: absolute; right: 0; background: #FFB3B3; border-radius: 0 6px 6px 0; display: flex; align-items: center; justify-content: center; color: #1E182A; font-size: 10px; font-weight: bold; writing-mode: vertical-rl; }
    .board { position: relative; background: #15101F; border-radius: 8px; display: grid; gap: 3px; padding: 3px; }
    .grid-cell { background: #392B47; border-radius: 4px; }
    .vehicle { position: absolute; border-radius: 8px; cursor: grab; touch-action: none; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: inset 0 2px 4px rgba(255,255,255,0.2), 0 4px 6px rgba(0,0,0,0.5); transition: transform 0.05s ease; z-index: 10; }
    .vehicle:active { cursor: grabbing; filter: brightness(1.2); z-index: 20; }
    .vehicle::after { content: ''; position: absolute; background: rgba(0, 0, 0, 0.3); border-radius: 4px; }
    .vehicle.h::after { width: 40%; height: 60%; }
    .vehicle.v::after { width: 60%; height: 40%; }
    
    .controls { margin-top: 20px; display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
    button { background: #D6C7E7; color: #1E182A; border: none; padding: 10px 20px; font-size: 1rem; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.4); }
    button:hover { background: #FFB3B3; }
    button.secondary { background: #4D3960; color: #FFF6CC; }
    button.secondary:hover { background: #3B2844; }
    .message { margin-top: 14px; font-size: 1.2rem; font-weight: bold; color: #FFD1A3; min-height: 1.5em; text-align: center; }
  </style>'''

html = re.sub(r'<style>.*?</style>', new_style, html, flags=re.DOTALL)

# Re-adjust target car to be salmon pink so it fits perfectly
html = html.replace("isTarget ? '#d96c5b'", "isTarget ? '#FFB3B3'")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
