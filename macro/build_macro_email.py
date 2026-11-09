"""Build the daily macro email from a JSON brief file.

Claude writes <macro.json> with this shape:
{
  "title": "Daily Macro Brief — 9 November 2026",
  "intro": "one or two plain-English sentences on the macro situation",
  "top": [ {"heading":"...","why":"...","link":"https://..."} ],
  "sections": [
     {"heading":"Global data and central banks","items":[{"heading":"...","why":"...","link":"https://..."}]},
     {"heading":"India","items":[ ... ]},
     {"heading":"Global","items":[ ... ]}
  ],
  "sources_note": "optional line about how the brief was compiled"
}

Usage:  python3 -I -X utf8 macro/build_macro_email.py <macro.json> out/macro_email.html <edition_label>
"""
import sys, json, html, re

macro_json, out_html, edition_label = sys.argv[1:4]
data = json.load(open(macro_json, encoding='utf-8-sig'))

def item_html(item, bold=True):
    head = item.get('heading', '').strip()
    why = item.get('why', '').strip()
    link = item.get('link', '').strip()
    h = re.sub(r'<[^>]+>', '', head)
    parts = []
    if link:
        parts.append(f'<a href="{html.escape(link, quote=True)}"><strong>{html.escape(h)}</strong></a>')
    else:
        parts.append(f'<strong>{html.escape(head)}</strong>')
    if why:
        parts.append(f' — {html.escape(why)}')
    return f'<li>{"".join(parts)}</li>'

top = data.get('top', [])
sections = data.get('sections', [])

sec_html = []
if top:
    sec_html.append('<section class="sec"><h2>What matters most today</h2>'
                     f'<ul>{"".join(item_html(x) for x in top)}</ul></section>')
for s in sections:
    items = s.get('items', [])
    body = (f'<ul>{"".join(item_html(x) for x in items)}</ul>'
            if items else '<p class="fine">Nothing major here today.</p>')
    sec_html.append(f'<section class="sec"><h2>{html.escape(str(s.get("heading","")).strip())}</h2>{body}</section>')

html_out = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(data.get('title', edition_label))}</title>
<style>
body {{ margin:0; padding:0; background:#EDF0F4; color:#18212F;
  font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif; font-size:16px; line-height:1.6; }}
a {{ color:#1E4F9E; }}
.wrap {{ max-width:720px; margin:0 auto; padding:12px; }}
.mast {{ background:#14284B; color:#fff; border-radius:10px; padding:20px 18px; }}
.mast .kicker {{ color:#C5D3E8; margin:0; font-size:11px; letter-spacing:0.12em;
  text-transform:uppercase; font-weight:700; }}
.mast h1 {{ font-size:24px; line-height:1.2; margin:6px 0 4px; color:#fff; }}
.mast .sub {{ margin:0; color:#C5D3E8; font-size:13px; }}
.sec {{ background:#fff; border-radius:10px; padding:18px; margin:12px 0; }}
.sec h2 {{ font-size:20px; line-height:1.25; margin:2px 0 8px; color:#14284B; }}
.sec p {{ margin:8px 0; }}
.sec ul {{ margin:6px 0 4px; padding-left:20px; }}
.sec li {{ margin:0 0 10px; }}
.fine {{ font-size:12px; color:#586273; }}
.foot {{ font-size:12px; color:#586273; padding:4px 6px 20px; }}
</style></head>
<body><div class="wrap">
  <div class="mast">
    <p class="kicker">Daily Macro Brief</p>
    <h1>{html.escape(edition_label)}</h1>
    <p class="sub">Economic data, central banks, tariffs and geopolitics · why it matters</p>
  </div>
  <section class="sec"><h2>Overview</h2>
    <p>{html.escape(data.get('intro',''))}</p>
  </section>
  {''.join(sec_html)}
  <div class="foot">
    <p class="fine">{html.escape(data.get('sources_note','Compiled automatically by the Daily Macro Brief. Headlines and figures should be verified on the linked sources before use. This is not investment advice.'))}</p>
  </div>
</div></body></html>"""

with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html_out)
print(f'Built {out_html}: {len(top)} top + {sum(len(s.get("items",[])) for s in sections)} items, {len(html_out)} chars.')
