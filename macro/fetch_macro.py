"""Collect macro-relevant headlines into <outdir>/macro.txt (with links and times).

Usage:  python -I -X utf8 macro/fetch_macro.py <outdir> [hours_back=30]

Best-effort recall boost for Claude. Claude is the intelligence layer: it reads
this file, then verifies and expands with web search. A source that fails just
logs "FAILED" and Claude falls back on search.

Two source kinds:
  1. Google News RSS searches — fresh, cheap, cover the last ~48h well.
  2. ET / Mint economy feeds — Indian macro and data releases.
  3. RBI's monetary-policy archive page — the actual policy dates/tone when the
     fetch succeeds (an authority, not a lead).
"""
import sys, os, re, html, subprocess, datetime
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

OUT = sys.argv[1]
HOURS = float(sys.argv[2]) if len(sys.argv) > 2 else 30
os.makedirs(OUT, exist_ok=True)
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
now = datetime.datetime.now(IST)

GN = 'https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:en'

FEEDS = [
    ('ET Economy', 'https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms'),
    ('Mint Economy', 'https://www.livemint.com/rss/economy'),
]
# (label, query, locale, region)
QUERIES = [
    ('CPI / inflation India', 'CPI+inflation+India+when:1d', 'en-IN', 'IN'),
    ('India GDP / growth data', 'India+GDP+OR+growth+OR+%22IIM%22+when:1d', 'en-IN', 'IN'),
    ('RBI / SEBI policy', 'RBI+OR+%22SEBI%22+when:1d', 'en-IN', 'IN'),
    ('India inflation US CPI', 'US+CPI+OR+inflation+when:1d', 'en-US', 'US'),
    ('Central banks Fed/ECB/BOJ', '%22Federal+Reserve%22+OR+ECB+OR+%22Bank+of+Japan%22+OR+%22BoE%22+when:1d', 'en-US', 'US'),
    ('China macro', 'China+GDP+OR+CPI+OR+PPI+when:1d', 'en-US', 'US'),
    ('Tariffs / trade', 'tariffs+OR+%22trade+deal%22+OR+%22trade+wars%22+when:1d', 'en-US', 'US'),
    ('Geopolitics market impact', 'sanctions+OR+ceasefire+OR+missile+OR+%22Hormuz%22+when:1d', 'en-US', 'US'),
    ('Oil prices macro', 'oil+prices+Brent+WTI+when:1d', 'en-US', 'US'),
]
for name, q, hl, gl in QUERIES:
    FEEDS.append((name, GN.format(q=q, hl=hl, gl=gl)))

def fetch_text(url):
    r = subprocess.run(['curl', '-s', '-L', '-m', '30', '-A', UA, url],
                       capture_output=True, timeout=60)
    return r.stdout

def parse_rss(raw, source, filter_hours=True):
    root = ET.fromstring(raw)
    rows = []
    for it in root.findall('.//item'):
        t = html.unescape((it.findtext('title') or '').strip())
        link = (it.findtext('link') or '').strip()
        try:
            dt = parsedate_to_datetime(it.findtext('pubDate') or '').astimezone(IST)
        except Exception:
            dt = None
        if filter_hours and dt and (now - dt).total_seconds() > HOURS * 3600:
            continue
        desc = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html.unescape(it.findtext('description') or ''))).strip()
        rows.append((dt, t, '' if link.startswith('https://news.google.com') else desc[:180], link))
    rows.sort(key=lambda z: z[0] or now, reverse=True)
    return rows

out = [f'Macro headlines pulled {now:%a %d %b %Y %H:%M} IST, last {HOURS:g} hours.',
       'Format: [time IST] title | summary | link. Google News links cannot be read directly; '
       'use them only for the fact in the headline.']
out.append('')
for name, url in FEEDS:
    try:
        rows = parse_rss(fetch_text(url), name)
    except Exception as e:
        out.append(f'## {name}: FAILED ({e})')
        out.append('')
        continue
    out.append(f'## {name} ({len(rows)})')
    for dt, t, desc, link in rows[:15]:
        out.append(f"  [{dt:%d %b %H:%M}] {t}" + (f' | {desc}' if desc else '') + f' | {link}')
    out.append('')

# RBI monetary policy archive (an authority when it resolves)
try:
    raw = fetch_text('https://www.rbi.org.in/Scripts/DSViewPage.aspx?Src=MONPOLCY')
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', raw, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'\n\s*\n+', '\n', html.unescape(text)).strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    keep = [ln for ln in lines if re.search(r'20[12]\d|Monetary Policy|Review', ln)][:40]
    out.append('## RBI monetary policy archive (authority)')
    out.append('\n'.join(keep) if keep else '(page fetched but no policy lines found)')
    out.append('')
except Exception as e:
    out.append(f'## RBI monetary policy archive: FAILED ({e})')
    out.append('')

open(os.path.join(OUT, 'macro.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print(f'written {os.path.join(OUT, "macro.txt")} ({len(out)} lines)')
