#!/usr/bin/env python3
"""Build a clickable link-hub HTML page from a daily-digest markdown file.

Usage: python3 build.py <digest.md> <issue_no> <out.html>
"""
import re
import sys
import html as htmllib
from urllib.parse import urlparse

def esc(s):
    return htmllib.escape(s, quote=True)

def domain_of(url):
    try:
        d = urlparse(url).netloc
        return d[4:] if d.startswith("www.") else d
    except Exception:
        return url

def parse(md_lines):
    sections = []  # list of (emoji, title, [items])
    cur_items = None
    i = 0
    while i < len(md_lines):
        line = md_lines[i].rstrip("\n")
        if line.startswith("## "):
            text = line[3:].strip()
            m = re.match(r"^(\S+)\s+(.*)$", text)
            emoji, title = (m.group(1), m.group(2)) if m else ("", text)
            cur_items = []
            sections.append({"emoji": emoji, "title": title, "items": cur_items})
        elif line.startswith("### ") and cur_items is not None:
            item_title = line[4:].strip()
            body = ""
            url = ""
            j = i + 1
            while j < len(md_lines) and not md_lines[j].startswith("### ") and not md_lines[j].startswith("## "):
                l2 = md_lines[j].strip()
                if l2 and not l2.startswith("🔗") and l2 != "---":
                    if not body:
                        body = l2
                m = re.search(r"\[[^\]]+\]\((https?://[^\)]+)\)", l2)
                if m:
                    url = m.group(1)
                j += 1
            cur_items.append({"title": item_title, "body": body, "url": url})
            i = j - 1
        i += 1
    return sections

def build_html(sections, issue_no, date_str, total, series="每日一更", label="早报"):
    cards = []
    for sec in sections:
        items_html = []
        for it in sec["items"]:
            if not it["url"]:
                continue
            items_html.append(f'''
            <a class="card" href="{esc(it['url'])}" target="_blank" rel="noopener">
              <span class="card-title">{esc(it['title'])}</span>
              <span class="card-body">{esc(it['body'])}</span>
              <span class="card-domain">{esc(domain_of(it['url']))}</span>
            </a>''')
        cards.append(f'''
        <section class="cat">
          <h2><span class="cat-emoji">{esc(sec['emoji'])}</span>{esc(sec['title'])}</h2>
          <div class="cat-list">{"".join(items_html)}</div>
        </section>''')

    body = "\n".join(cards)

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{date_str} {label} · 链接索引</title>
<style>
:root {{
  --bg: #f6f4ee;
  --card-bg: #fffefa;
  --ink: #22201c;
  --muted: #6f6a5e;
  --accent: #1f4b3f;
  --accent-soft: #e4ebe7;
  --rule: #ddd7c8;
  --focus: #1f4b3f;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #17181a;
    --card-bg: #201f1c;
    --ink: #e9e6dd;
    --muted: #a19a89;
    --accent: #6fc9a3;
    --accent-soft: #22322c;
    --rule: #34332e;
    --focus: #6fc9a3;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #17181a; --card-bg: #201f1c; --ink: #e9e6dd; --muted: #a19a89;
  --accent: #6fc9a3; --accent-soft: #22322c; --rule: #34332e; --focus: #6fc9a3;
}}
:root[data-theme="light"] {{
  --bg: #f6f4ee; --card-bg: #fffefa; --ink: #22201c; --muted: #6f6a5e;
  --accent: #1f4b3f; --accent-soft: #e4ebe7; --rule: #ddd7c8; --focus: #1f4b3f;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--ink);
  font-family: Iowan Old Style, "Palatino Linotype", Georgia, "Noto Serif SC", serif;
  line-height: 1.5;
  overflow-x: hidden;
}}
.wrap {{
  max-width: 720px;
  margin: 0 auto;
  padding: 40px 20px 64px;
}}
.mast {{
  border-bottom: 3px double var(--rule);
  padding-bottom: 18px;
  margin-bottom: 30px;
}}
.mast-meta {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Noto Sans Mono CJK SC", monospace;
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}}
h1 {{
  font-size: clamp(28px, 6vw, 38px);
  font-weight: 700;
  margin: 0 0 8px;
  text-wrap: balance;
}}
.mast-sub {{
  color: var(--muted);
  font-size: 15px;
  margin: 0;
}}
.cat {{ margin-bottom: 8px; }}
.cat h2 {{
  font-size: 18px;
  font-weight: 700;
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin: 34px 0 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--rule);
}}
.cat-emoji {{ font-size: 16px; }}
.cat-list {{ display: flex; flex-direction: column; gap: 10px; }}
.card {{
  display: block;
  background: var(--card-bg);
  border: 1px solid var(--rule);
  border-radius: 10px;
  padding: 14px 16px;
  text-decoration: none;
  color: inherit;
  position: relative;
  transition: border-color 0.15s ease, transform 0.15s ease;
}}
.card:hover, .card:focus-visible {{
  border-color: var(--accent);
  transform: translateY(-1px);
}}
.card:focus-visible {{
  outline: 2px solid var(--focus);
  outline-offset: 2px;
}}
.card-title {{
  display: block;
  font-weight: 700;
  font-size: 15.5px;
  margin-bottom: 4px;
  text-wrap: balance;
}}
.card-body {{
  display: block;
  font-size: 13.5px;
  color: var(--muted);
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans SC", sans-serif;
  line-height: 1.6;
  margin-bottom: 8px;
}}
.card-domain {{
  display: inline-block;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Noto Sans Mono CJK SC", monospace;
  font-size: 11px;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.02em;
}}
.foot {{
  margin-top: 48px;
  padding-top: 18px;
  border-top: 1px solid var(--rule);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Noto Sans Mono CJK SC", monospace;
  font-size: 11.5px;
  color: var(--muted);
  text-align: center;
  letter-spacing: 0.03em;
}}
</style>
</head>
<body>
<div class="wrap">
  <div class="mast">
    <div class="mast-meta">
      <span>{series} · 第{issue_no:03d}期</span>
      <span>{date_str}</span>
    </div>
    <h1>{date_str} {label} · 链接索引</h1>
    <p class="mast-sub">公众号正文里的原文链接不能跳转（微信规则），共 {total} 条，点标题直达原文。</p>
  </div>
  {body}
  <div class="foot">{series} · 叶哥知远 · 本页由 daily-digest 自动生成</div>
</div>
</body>
</html>'''

if __name__ == "__main__":
    md_path, issue_no, out_path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()
    m = re.search(r"(\d{4}-\d{2}-\d{2})", md_path)
    date_str = m.group(1) if m else ""
    is_weekly = "weekly" in md_path.lower() or "周报" in md_path
    series, label = ("本周精选", "周报") if is_weekly else ("每日一更", "早报")
    sections = parse(lines)
    total = sum(1 for s in sections for it in s["items"] if it["url"])
    html_out = build_html(sections, issue_no, date_str, total, series=series, label=label)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"wrote {out_path}, {total} links, {len(sections)} sections")
