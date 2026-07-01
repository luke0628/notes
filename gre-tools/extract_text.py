#!/usr/bin/env python3
"""Extract plain text from HTML files, stripping tags."""
import html.parser
import os
import sys

class TextExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'head'):
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'head'):
            self.skip = False
        if tag in ('p', 'br', 'tr', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'):
            self.text_parts.append('\n')
    def handle_data(self, data):
        if not self.skip:
            self.text_parts.append(data)
    def handle_entityref(self, name):
        char = {'amp': '&', 'lt': '<', 'gt': '>', 'quot': '"', 'apos': "'"}
        self.text_parts.append(char.get(name, f'&{name};'))
    def get_text(self):
        txt = ''.join(self.text_parts)
        # collapse multiple newlines
        while '\n\n\n' in txt:
            txt = txt.replace('\n\n\n', '\n\n')
        return txt.strip()

srcdir = '/home/Lu'
outdir = '/home/Lu/extracted'
os.makedirs(outdir, exist_ok=True)

for fname in sorted(os.listdir(srcdir)):
    if not fname.endswith('.html'):
        continue
    fpath = os.path.join(srcdir, fname)
    try:
        with open(fpath, 'r', errors='replace') as f:
            raw = f.read()
    except Exception as e:
        print(f"SKIP {fname}: {e}", file=sys.stderr)
        continue
    ext = TextExtractor()
    try:
        ext.feed(raw)
    except Exception as e:
        print(f"PARSE ERROR {fname}: {e}", file=sys.stderr)
        txt = raw  # fallback
    else:
        txt = ext.get_text()
    outpath = os.path.join(outdir, fname.replace('.html', '.txt'))
    with open(outpath, 'w') as f:
        f.write(txt)
    print(f"OK: {fname} -> {len(txt)} chars")
