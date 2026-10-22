"""Build the public website page and the email version from a day's content.html.

Usage:
  python3 -I -X utf8 build_site.py <content.html> <site_dir> <out_dir> "<edition date>" "<built at>" "<page url>"

Writes <site_dir>/index.html (full web page, light and dark themes) and <out_dir>/email.html
(email-safe version: plain CSS without variables, light theme only).
"""
import sys, os, re

here = os.path.dirname(os.path.abspath(__file__))
content_path, site_dir, out_dir, date_label, built_at, page_url = sys.argv[1:7]
content = open(content_path, encoding='utf-8').read()
for bad in ('<html', '<head', '<body', '<!doctype', '<!DOCTYPE'):
    if bad in content:
        sys.exit(f'content.html must not contain {bad} tags')

# ---------- website ----------
tpl = open(os.path.join(here, 'page_template.html'), encoding='utf-8').read()
split_at = tpl.index('<header class="mast">')
head_part, body_part = tpl[:split_at], tpl[split_at:]
body_part = (body_part.replace('{{EDITION_DATE}}', date_label)
                      .replace('{{BUILT_AT}}', built_at)
                      .replace('{{NOTICE}}', '')
                      .replace('{{CONTENT}}', content))
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head_part + '</head>\n<body>\n' + body_part + '\n</body>\n</html>\n')
os.makedirs(site_dir, exist_ok=True)
open(os.path.join(site_dir, 'index.html'), 'w', encoding='utf-8').write(page)

# ---------- email ----------
etpl = open(os.path.join(here, 'email_template.html'), encoding='utf-8').read()
email = (etpl.replace('{{EDITION_DATE}}', date_label)
             .replace('{{BUILT_AT}}', built_at)
             .replace('{{PAGE_URL}}', page_url)
             .replace('{{CONTENT}}', content))
os.makedirs(out_dir, exist_ok=True)
open(os.path.join(out_dir, 'email.html'), 'w', encoding='utf-8').write(email)
print('website', len(page), 'chars; email', len(email), 'chars')
