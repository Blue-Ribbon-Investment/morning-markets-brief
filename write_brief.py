"""Write today's Morning Markets Brief by calling Claude's API directly.

Usage:  python3 -I -X utf8 write_brief.py <runs_dir> <date_label>
        e.g. python3 -I -X utf8 write_brief.py runs/2026-11-17 "Tuesday 17 November 2026"

Reads:
    <runs_dir>/numbers.txt   – market numbers with dates and IST quote times
    <runs_dir>/headlines.txt – recent headlines with links

Writes:
    <runs_dir>/content.html  – the seven-section brief ready for build_site.py

Requires ANTHROPIC_API_KEY in the environment (the brocode relay key).
The relay base URL is set via ANTHROPIC_BASE_URL (defaults to api.anthropic.com).
"""
import sys, os, json, urllib.request, urllib.error

if len(sys.argv) != 3:
    sys.exit('Usage: write_brief.py <runs_dir> <date_label>')

RUNS_DIR = sys.argv[1]
DATE_LABEL = sys.argv[2]
API_KEY = os.environ.get('ANTHROPIC_API_KEY', '').strip()
BASE_URL = os.environ.get('ANTHROPIC_BASE_URL', 'https://api.anthropic.com').rstrip('/')

if not API_KEY:
    sys.exit('ANTHROPIC_API_KEY is not set.')

# --- read fetched data ---
numbers_path = os.path.join(RUNS_DIR, 'numbers.txt')
headlines_path = os.path.join(RUNS_DIR, 'headlines.txt')

try:
    numbers = open(numbers_path, encoding='utf-8').read()
except FileNotFoundError:
    sys.exit(f'Missing {numbers_path} — run fetch_numbers.py first.')

try:
    headlines = open(headlines_path, encoding='utf-8').read()
except FileNotFoundError:
    headlines = '(no headlines fetched)'

# --- build the prompt ---
with open('WRITER_PROMPT.md', encoding='utf-8') as f:
    prompt_template = f.read()

prompt = (
    f'Today\'s edition date: {DATE_LABEL}\n\n'
    '## Market numbers\n'
    f'{numbers}\n\n'
    '## Headlines\n'
    f'{headlines}\n\n'
    '---\n\n'
    + prompt_template
)

# --- call Claude API ---
url = f'{BASE_URL}/v1/messages'
payload = json.dumps({
    'model': 'claude-sonnet-5-5',
    'max_tokens': 8192,
    'temperature': 0.3,
    'system': (
        'You are an equity research analyst writing a daily morning markets brief. '
        'You write in plain English with short sentences. India comes first, then global. '
        'Every number must come from the data provided or from articles you read with art_text.py. '
        'Never fill gaps from memory. Never give investment advice or stock tips. '
        'Use Indian number formats (₹, crore, lakh crore). Use a real minus sign (−) for negatives. '
        'Yield changes in bp. Every section ends with a Sources line with clickable links.'
    ),
    'messages': [{'role': 'user', 'content': prompt}],
}).encode('utf-8')

req = urllib.request.Request(
    url,
    data=payload,
    headers={
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
        'anthropic-version': '2023-06-01',
    },
    method='POST',
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', 'ignore')
    sys.exit(f'Claude API error {e.code}: {body}')
except Exception as e:
    sys.exit(f'Claude API request failed: {e}')

# --- extract text ---
text = ''
for block in result.get('content', []):
    if block.get('type') == 'text':
        text += block['text']

# --- write content.html ---
content_path = os.path.join(RUNS_DIR, 'content.html')
with open(content_path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f'Wrote {len(text):,} chars to {content_path}')
print(f'Input tokens: {result.get("usage", {}).get("input_tokens", "?")}  |  '
      f'Output tokens: {result.get("usage", {}).get("output_tokens", "?")}')
print(f'Stop reason: {result.get("stop_reason", "?")}')
print(f'Finish: {DATE_LABEL}')
