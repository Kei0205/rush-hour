import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_code = '''          if (stageInfo && stageInfo.perfect) {
            statusHtml = `<div class="status-perfect">★ PERFECT</div>
                          <div class="status-time">${stageInfo.time} (${stageInfo.date})</div>`;
          } else if (stageInfo) {
            statusHtml = `<div class="status-clear">✓ CLEAR</div>
                          <div class="status-time">${stageInfo.time} (${stageInfo.date})</div>`;
          }'''

new_code = '''          const escapeHtml = (unsafe) => {
            if (typeof unsafe !== 'string') return '';
            return unsafe
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
          };

          if (stageInfo && stageInfo.perfect) {
            statusHtml = `<div class="status-perfect">★ PERFECT</div>
                          <div class="status-time">${escapeHtml(stageInfo.time)} (${escapeHtml(stageInfo.date)})</div>`;
          } else if (stageInfo) {
            statusHtml = `<div class="status-clear">✓ CLEAR</div>
                          <div class="status-time">${escapeHtml(stageInfo.time)} (${escapeHtml(stageInfo.date)})</div>`;
          }'''

html = html.replace(old_code, new_code)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
