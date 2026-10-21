"""Wrap a day's content into the Morning Markets Brief page.

Usage:
  python -I -X utf8 build_page.py <content.html> <out.html> "<edition date label>" "<built-at label>" [notice.html]

<content.html> holds only the <section class="sec"> blocks (see example_content.html).
"""
import sys, os

here = os.path.dirname(os.path.abspath(__file__))
content_path, out_path, date_label, built_at = sys.argv[1:5]
notice_path = sys.argv[5] if len(sys.argv) > 5 else None

tpl = open(os.path.join(here, 'page_template.html'), encoding='utf-8').read()
content = open(content_path, encoding='utf-8').read()
notice = ''
if notice_path and os.path.exists(notice_path):
    notice = ('<div class="notice"><div class="wrap"><p>'
              + open(notice_path, encoding='utf-8').read().strip() + '</p></div></div>')

for bad in ('<html', '<head', '<body', '<!doctype', '<!DOCTYPE'):
    if bad in content:
        sys.exit(f'content.html must not contain {bad} tags')

page = (tpl.replace('{{EDITION_DATE}}', date_label)
           .replace('{{BUILT_AT}}', built_at)
           .replace('{{NOTICE}}', notice)
           .replace('{{CONTENT}}', content))
os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
open(out_path, 'w', encoding='utf-8').write(page)
print('written', out_path, len(page), 'chars')
