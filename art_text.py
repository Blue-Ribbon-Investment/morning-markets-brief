"""Fetch article pages and print their text (for checking facts behind headlines).

Usage:  python -I -X utf8 art_text.py <outdir> <url1> [url2 ...]
Writes <outdir>/articles.txt (appends) and prints the same. ~2,500 characters per article.
Works for ET, Mint, Business Standard and CNBC links (WebFetch is blocked on several of them).
"""
import sys, os, re, json, html, subprocess

OUT, urls = sys.argv[1], sys.argv[2:]
os.makedirs(OUT, exist_ok=True)
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')
LIMIT = 2500


def body_ld(h):
    best = ''
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S | re.I):
        try:
            data = json.loads(m.group(1).strip())
        except Exception:
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                b = x.get('articleBody')
                if isinstance(b, str) and len(b) > len(best):
                    best = b
                stack.extend(v for v in x.values() if isinstance(v, (dict, list)))
            elif isinstance(x, list):
                stack.extend(x)
    return best


def body_p(h):
    h = re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>', ' ', h, flags=re.S | re.I)
    ps = [re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', p))).strip()
          for p in re.findall(r'<p[^>]*>(.*?)</p>', h, re.S | re.I)]
    return ' '.join(p for p in ps if len(p) > 60 and 'cookie' not in p.lower())


chunks = []
for u in urls:
    try:
        r = subprocess.run(['curl', '-s', '-L', '-m', '30', '-A', UA, '-H', 'Accept: text/html', u],
                           capture_output=True, timeout=60)
        h = r.stdout.decode('utf-8', 'ignore')
        title = re.search(r'<title>(.*?)</title>', h, re.S | re.I)
        title = html.unescape(title.group(1).strip()) if title else ''
        b = body_ld(h)
        if len(b) < 400:
            b = body_p(h)
        b = re.sub(r'\s+', ' ', html.unescape(b))
        chunks.append(f'===== {title[:150]}\n{u}\n{b[:LIMIT] or "(no text extracted)"}\n')
    except Exception as e:
        chunks.append(f'===== FAILED {u}: {e}\n')
text = '\n'.join(chunks)
with open(os.path.join(OUT, 'articles.txt'), 'a', encoding='utf-8') as f:
    f.write(text + '\n')
print(text)
