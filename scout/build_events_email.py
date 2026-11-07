"""Build the monthly academic-events email from a JSON report file.

Claude writes <events.json> with this shape:
{
  "title": "Academic Events — December 2026",
  "intro": "one or two plain-English sentences",
  "events": [
    {"date":"12–14 Dec 2026","title":"...","city":"Mumbai","org":"...",
     "type":"Conference","link":"https://...","note":"optional"}
  ],
  "sources_note": "optional line about how the list was compiled"
}

Usage:  python3 -I -X utf8 scout/build_events_email.py <events.json> out/email.html <edition_label>
"""
import sys, json, html, re, datetime

events_json, out_html, edition_label = sys.argv[1:4]
data = json.load(open(events_json, encoding='utf-8'))

events = data.get('events', [])
# sort: city → date (parse leading day number if possible, else alphabetical)
def sort_key(e):
    city = (e.get('city') or '').lower()
    d = e.get('date') or ''
    m = re.search(r'(\d{1,2})', d)
    day = int(m.group(1)) if m else 99
    return (city, day, d)
events = sorted(events, key=sort_key)

by_city = {}
for e in events:
    by_city.setdefault(e.get('city') or 'Other', []).append(e)
city_order = ['Ahmedabad', 'Pune', 'Mumbai']
other_cities = [c for c in by_city if c not in city_order]
ordered_cities = [c for c in city_order if c in by_city] + \
                 sorted([c for c in other_cities if c in by_city])

sections = []
for city in ordered_cities:
    evs = by_city[city]
    lis = []
    for e in evs:
        parts = [f'<strong>{html.escape(str(e.get("date","").strip()))}</strong> — '
                 f'<a href="{html.escape(e.get("link",""), quote=True)}">{html.escape(str(e.get("title","")).strip())}</a>']
        if e.get('org'):
            parts.append(f' · {html.escape(str(e["org"]))}')
        if e.get('type'):
            parts.append(f'<em>· {html.escape(str(e["type"]))}</em>')
        lis.append(f'<li>{"".join(parts)}'
                   + (f'<br><span class="fine">{html.escape(str(e["note"]))}</span>' if e.get('note') else '')
                   + '</li>')
    sections.append(
        f'<section class="sec"><h2>{html.escape(city)}</h2>'
        + (f'<ul>{"".join(lis)}</ul>' if lis else '<p class="fine">No matching events found this month.</p>')
        + '</section>')

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
.mast a {{ color:#fff; }}
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
    <p class="kicker">Academic Events Scout · India</p>
    <h1>{html.escape(edition_label)}</h1>
    <p class="sub">Conferences, seminars and research workshops · Ahmedabad, Pune, Mumbai</p>
  </div>
  <section class="sec"><h2>Overview</h2>
    <p>{html.escape(data.get('intro',''))} <strong>{len(events)}</strong> event(s) found across {len(by_city)} city(ies).</p>
  </section>
  {''.join(sections)}
  <div class="foot">
    <p class="fine">{html.escape(data.get('sources_note','Compiled automatically by the Academic Events Scout. Dates and registration deadlines should be verified on the linked pages before attending or registering.'))}</p>
  </div>
</div></body></html>"""

with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html_out)
print(f'Built {out_html}: {len(events)} events, {len(html_out)} chars.')
