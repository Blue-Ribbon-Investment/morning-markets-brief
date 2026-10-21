"""Pull the day's market numbers into <outdir>/numbers.json and a readable <outdir>/numbers.txt.

Usage:  python -I -X utf8 fetch_numbers.py <outdir>

Every source is tried independently; a failure is recorded in the output instead of stopping the run.
Times are shown in IST. Uses the system curl (works where Python's own HTTP gets blocked by NSE).
"""
import sys, os, json, subprocess, datetime, csv, io

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
COOKIE = os.path.join(OUT, 'nse_cookies.txt')
result = {'built_at_ist': datetime.datetime.now(IST).strftime('%a %d %b %Y %H:%M'), 'errors': []}


def curl(url, referer=None, accept='application/json', cookie=False):
    cmd = ['curl', '-s', '-L', '-m', '40', '-A', UA, '-H', 'Accept: ' + accept,
           '-H', 'Accept-Language: en-US,en;q=0.9']
    if referer:
        cmd += ['-H', 'Referer: ' + referer]
    if cookie:
        cmd += ['-b', COOKIE, '-c', COOKIE]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, timeout=70)
    return r.stdout.decode('utf-8', 'ignore')


def getjson(url, **kw):
    t = curl(url, **kw)
    return json.loads(t)


# ---------------- NSE ----------------
try:
    curl('https://www.nseindia.com/', accept='text/html', cookie=True)
    ref = 'https://www.nseindia.com/market-data/live-market-indices'
    idx = getjson('https://www.nseindia.com/api/allIndices', referer=ref, cookie=True)
    want = ['NIFTY 50', 'NIFTY NEXT 50', 'NIFTY 500', 'NIFTY MIDCAP 150', 'NIFTY SMALLCAP 250', 'INDIA VIX',
            'NIFTY BANK', 'NIFTY PRIVATE BANK', 'NIFTY PSU BANK', 'NIFTY FINANCIAL SERVICES', 'NIFTY IT',
            'NIFTY AUTO', 'NIFTY PHARMA', 'NIFTY HEALTHCARE INDEX', 'NIFTY FMCG', 'NIFTY METAL', 'NIFTY REALTY',
            'NIFTY ENERGY', 'NIFTY OIL & GAS', 'NIFTY CONSUMER DURABLES', 'NIFTY MEDIA', 'NIFTY CHEMICALS',
            'NIFTY INDIA DEFENCE', 'NIFTY CAPITAL MARKETS', 'NIFTY INFRASTRUCTURE', 'NIFTY COMMODITIES', 'NIFTY CPSE']
    rows = []
    for x in idx.get('data', []):
        if x.get('index') in want:
            rows.append({k: x.get(k) for k in ('index', 'last', 'percentChange', 'variation', 'advances', 'declines',
                                                'pe', 'yearHigh', 'yearLow', 'perChange30d', 'perChange365d')})
    result['nse_indices'] = {'timestamp': idx.get('timestamp'), 'rows': rows}
except Exception as e:
    result['errors'].append(f'NSE indices: {e}')

for key, path, ref in [
    ('nse_fii_dii', 'fiidiiTradeReact', 'https://www.nseindia.com/reports/fii-dii'),
    ('nse_gainers', 'live-analysis-variations?index=gainers', 'https://www.nseindia.com/market-data/top-gainers-losers'),
    ('nse_losers', 'live-analysis-variations?index=loosers', 'https://www.nseindia.com/market-data/top-gainers-losers'),
    ('nse_large_deals', 'snapshot-capital-market-largedeal', 'https://www.nseindia.com/market-data/large-deals'),
]:
    try:
        d = getjson('https://www.nseindia.com/api/' + path, referer=ref, cookie=True)
        if key in ('nse_gainers', 'nse_losers'):
            d = {g: [{'symbol': r.get('symbol'), 'pct': r.get('perChange'), 'ltp': r.get('ltp')}
                     for r in (d.get(g, {}) or {}).get('data', [])[:10]]
                 for g in ('NIFTY', 'BANKNIFTY', 'NIFTYNEXT50', 'FOSec')}
        if key == 'nse_large_deals':
            deals = []
            for r in (d.get('BULK_DEALS_DATA') or []) + (d.get('BLOCK_DEALS_DATA') or []):
                try:
                    v = float(r['qty']) * float(r['watp']) / 1e7
                except Exception:
                    continue
                deals.append({'date': r.get('date'), 'symbol': r.get('symbol'), 'name': r.get('name'),
                              'side': r.get('buySell'), 'client': r.get('clientName'), 'value_cr': round(v, 1)})
            deals.sort(key=lambda z: -z['value_cr'])
            d = {'as_on': d.get('as_on_date'), 'top': deals[:25]}
        result[key] = d
    except Exception as e:
        result['errors'].append(f'{key}: {e}')

# ---------------- Yahoo Finance ----------------
YAHOO = [
    ('India', 'Sensex', '^BSESN'), ('India', 'Nifty 50', '^NSEI'), ('India', 'India VIX', '^INDIAVIX'),
    ('US', 'S&P 500', '^GSPC'), ('US', 'Nasdaq Composite', '^IXIC'), ('US', 'Dow Jones', '^DJI'),
    ('Europe', 'Stoxx 600', '^STOXX'), ('Europe', 'FTSE 100', '^FTSE'), ('Europe', 'DAX', '^GDAXI'), ('Europe', 'CAC 40', '^FCHI'),
    ('Asia', 'Nikkei 225', '^N225'), ('Asia', 'Kospi', '^KS11'), ('Asia', 'Hang Seng', '^HSI'),
    ('Asia', 'Shanghai Composite', '000001.SS'), ('Asia', 'Taiwan Weighted', '^TWII'),
    ('Bonds', 'US 10-year yield (Yahoo)', '^TNX'),
    ('Commodities', 'Brent crude ($/bbl)', 'BZ=F'), ('Commodities', 'WTI crude ($/bbl)', 'CL=F'),
    ('Commodities', 'Natural gas, US ($/MMBtu)', 'NG=F'), ('Commodities', 'Gold ($/oz)', 'GC=F'),
    ('Commodities', 'Silver ($/oz)', 'SI=F'), ('Commodities', 'Copper ($/lb)', 'HG=F'), ('Commodities', 'Aluminium ($/t)', 'ALI=F'),
    ('Currency', 'USD/INR', 'INR=X'), ('Currency', 'Dollar index', 'DX-Y.NYB'), ('Currency', 'EUR/USD', 'EURUSD=X'),
    ('Currency', 'USD/JPY', 'JPY=X'), ('Currency', 'USD/CNY', 'CNY=X'),
]
yrows = []
for grp, label, sym in YAHOO:
    try:
        q = sym.replace('^', '%5E').replace('=', '%3D')
        d = getjson(f'https://query1.finance.yahoo.com/v8/finance/chart/{q}?range=10d&interval=1d')
        r = d['chart']['result'][0]
        m = r['meta']
        off = datetime.timedelta(seconds=m.get('gmtoffset', 0))
        bars = [((datetime.datetime.utcfromtimestamp(t) + off).date(), c)
                for t, c in zip(r['timestamp'], r['indicators']['quote'][0]['close']) if c is not None]
        mkt_local = datetime.datetime.utcfromtimestamp(m['regularMarketTime']) + off
        mkt_ist = datetime.datetime.fromtimestamp(m['regularMarketTime'], IST)
        price = m.get('regularMarketPrice')
        if bars and mkt_local.date() > bars[-1][0]:
            last_date, last, prev_date, prev = mkt_local.date(), price, bars[-1][0], bars[-1][1]
        else:
            last_date, last = bars[-1]
            prev_date, prev = bars[-2] if len(bars) > 1 else (None, None)
            last = price if price is not None else last
        chg = (last / prev - 1) * 100 if prev else None
        yrows.append({'group': grp, 'label': label, 'symbol': sym, 'last': round(last, 4),
                      'last_date': last_date.strftime('%a %d %b'), 'prev': prev and round(prev, 4),
                      'prev_date': prev_date and prev_date.strftime('%a %d %b'),
                      'chg_pct': None if chg is None else round(chg, 2),
                      'quote_time_ist': mkt_ist.strftime('%a %d %b %H:%M')})
    except Exception as e:
        result['errors'].append(f'Yahoo {sym}: {e}')
result['yahoo'] = yrows

# ---------------- Official yields ----------------
year = datetime.datetime.now(IST).year
try:
    t = curl(f'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all'
             f'?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv', accept='text/csv')
    rows = list(csv.DictReader(io.StringIO(t)))
    result['us_treasury'] = [{k: r.get(k) for k in ('Date', '2 Yr', '10 Yr', '30 Yr')} for r in rows[:3]]
except Exception as e:
    result['errors'].append(f'US Treasury: {e}')
try:
    t = curl('https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZAR.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A'
             '?format=csv&lastNObservations=6&lang=en', accept='text/csv')
    obs = [l.split(',')[:2] for l in t.splitlines() if l[:4].isdigit() and ',.' not in l]
    result['bund_10y'] = obs[-3:]
except Exception as e:
    result['errors'].append(f'Bundesbank: {e}')
try:
    t = curl('https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv', accept='text/csv')
    lines = [l for l in t.splitlines() if l[:4].isdigit()]
    hdr = [l for l in t.splitlines() if l.startswith('Date')][0].split(',')
    i10 = hdr.index('10Y')
    result['jgb_10y'] = [[l.split(',')[0], l.split(',')[i10]] for l in lines[-3:]]
except Exception as e:
    result['errors'].append(f'Japan MoF: {e}')

json.dump(result, open(os.path.join(OUT, 'numbers.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

# ---------------- readable summary ----------------
L = [f"Numbers pulled {result['built_at_ist']} IST", '']
ni = result.get('nse_indices')
if ni:
    L.append(f"NSE indices (as of {ni['timestamp']}):")
    for r in ni['rows']:
        L.append(f"  {r['index']:<26} {r['last']:>12}  {r['percentChange']:>+6}%  adv {r['advances']} dec {r['declines']}")
if 'nse_fii_dii' in result:
    L.append('FII/DII (NSE provisional, Rs crore): ' + '; '.join(f"{x['category']} {x['date']} net {x['netValue']}" for x in result['nse_fii_dii']))
for k in ('nse_gainers', 'nse_losers'):
    if k in result:
        L.append(k + ' NIFTY: ' + ', '.join(f"{x['symbol']} {x['pct']}%" for x in result[k].get('NIFTY', [])))
        L.append(k + ' F&O: ' + ', '.join(f"{x['symbol']} {x['pct']}%" for x in result[k].get('FOSec', [])))
if 'nse_large_deals' in result:
    L.append(f"Largest bulk/block deals (as on {result['nse_large_deals']['as_on']}): " +
             '; '.join(f"{x['symbol']} {x['side']} Rs{x['value_cr']}cr {x['client']}" for x in result['nse_large_deals']['top'][:8]))
L.append('')
L.append('Yahoo Finance (last = latest quote; chg vs previous close):')
for r in yrows:
    L.append(f"  [{r['group']}] {r['label']:<28} {r['last']:>12}  {r['chg_pct'] if r['chg_pct'] is not None else '–':>6}%  "
             f"last {r['last_date']} vs {r['prev_date']}  quote {r['quote_time_ist']} IST")
L.append('')
L.append(f"US Treasury (official, latest first): {result.get('us_treasury')}")
L.append(f"Bund 10y (Bundesbank): {result.get('bund_10y')}")
L.append(f"JGB 10y (Japan MoF): {result.get('jgb_10y')}")
if result['errors']:
    L.append('')
    L.append('ERRORS: ' + ' | '.join(result['errors']))
open(os.path.join(OUT, 'numbers.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('\n'.join(L))
