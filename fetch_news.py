"""Collect recent headlines from RSS feeds into <outdir>/headlines.txt (with links).

Usage:  python -I -X utf8 fetch_news.py <outdir> [hours_back=30]

Web search is poor for the last 48 hours; these feeds are fresh. Article links from ET, Mint,
Business Standard and CNBC are direct and can be read with art_text.py. Google News links redirect
in a browser (fine to cite) but cannot be read with art_text.py.
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

FEEDS = [
    ('ET Markets', 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms'),
    ('ET Stocks', 'https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms'),
    ('ET Bonds', 'https://economictimes.indiatimes.com/markets/bonds/rssfeeds/2146846.cms'),
    ('ET Forex', 'https://economictimes.indiatimes.com/markets/forex/rssfeeds/1150221130.cms'),
    ('ET Economy', 'https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms'),
    ('Mint Markets', 'https://www.livemint.com/rss/markets'),
    ('Mint Economy', 'https://www.livemint.com/rss/economy'),
    ('Business Standard Markets', 'https://www.business-standard.com/rss/markets-106.rss'),
    ('CNBC Top', 'https://www.cnbc.com/id/100003114/device/rss/rss.html'),
    ('CNBC World', 'https://www.cnbc.com/id/100727362/device/rss/rss.html'),
    ('CNBC Economy', 'https://www.cnbc.com/id/20910258/device/rss/rss.html'),
]
GN = 'https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:en'
QUERIES = [
    ('GN: GIFT Nifty', '%22GIFT+Nifty%22+when:1d', 'en-IN', 'IN'),
    ('GN: Sensex Nifty', 'Sensex+Nifty+when:1d', 'en-IN', 'IN'),
    ('GN: Wall Street', 'stocks+Wall+Street+close+when:1d', 'en-US', 'US'),
    ('GN: Asia markets', 'Asian+markets+Nikkei+Kospi+when:1d', 'en-US', 'US'),
    ('GN: Oil', 'oil+prices+Brent+when:1d', 'en-US', 'US'),
    ('GN: RBI SEBI', 'RBI+OR+SEBI+when:1d', 'en-IN', 'IN'),
    ('GN: India economy', 'India+economy+data+when:1d', 'en-IN', 'IN'),
    ('GN: Results India', 'Q2+results+net+profit+when:1d', 'en-IN', 'IN'),
    ('GN: Fed ECB BoJ', 'Federal+Reserve+OR+ECB+OR+%22Bank+of+Japan%22+when:1d', 'en-US', 'US'),
    ('GN: China economy', 'China+economy+when:1d', 'en-US', 'US'),
    ('GN: Geopolitics', 'sanctions+OR+ceasefire+OR+tariffs+OR+missile+when:1d', 'en-US', 'US'),
    ('GN: Middle East', 'Iran+OR+Houthi+OR+Hormuz+OR+Israel+when:1d', 'en-US', 'US'),
]
for name, q, hl, gl in QUERIES:
    FEEDS.append((name, GN.format(q=q, hl=hl, gl=gl)))

out = [f'Headlines pulled {now:%a %d %b %Y %H:%M} IST, last {HOURS:g} hours. Format: [time IST] title | summary | link', '']
for name, url in FEEDS:
    try:
        r = subprocess.run(['curl', '-s', '-L', '-m', '30', '-A', UA, url], capture_output=True, timeout=60)
        root = ET.fromstring(r.stdout)
    except Exception as e:
        out.append(f'## {name}: FAILED ({e})')
        continue
    rows = []
    for it in root.findall('.//item'):
        t = html.unescape((it.findtext('title') or '').strip())
        try:
            dt = parsedate_to_datetime(it.findtext('pubDate') or '').astimezone(IST)
        except Exception:
            dt = None
        if dt and (now - dt).total_seconds() > HOURS * 3600:
            continue
        desc = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html.unescape(it.findtext('description') or ''))).strip()
        rows.append((dt, t, '' if name.startswith('GN:') else desc[:220], (it.findtext('link') or '').strip()))
    rows.sort(key=lambda z: z[0] or now, reverse=True)
    out.append(f'## {name} ({len(rows)})')
    for dt, t, desc, link in rows[:25]:
        out.append(f"  [{dt:%d %b %H:%M}] {t}" + (f' | {desc}' if desc else '') + f' | {link}')
    out.append('')
open(os.path.join(OUT, 'headlines.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print(f'written {os.path.join(OUT, "headlines.txt")} ({len(out)} lines)')
