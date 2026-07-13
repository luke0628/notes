#!/usr/bin/env python3
"""Extract readable text content from HTML files to clean Markdown."""
import re
import os

def extract_readable_text(html_content):
    """Extract clean readable text from SharePoint HTML export."""
    # Extract body content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
    body = body_match.group(1) if body_match else html_content

    # Remove scripts and styles
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)

    # Remove HTML comments
    body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)

    # Remove SVG blocks (often contain base64 data that leaks into text)
    body = re.sub(r'<svg[^>]*>.*?</svg>', '', body, flags=re.DOTALL)

    # Replace block-level tags with newlines
    for tag in ['br', '/p', '/div', '/li', '/tr', '/h1', '/h2', '/h3', '/h4', '/h5', '/h6',
                 '/th', '/td', '/pre', '/blockquote', '/ul', '/ol', '/dl', '/dd', '/dt',
                 '/section', '/article', '/nav', '/header', '/footer', '/aside',
                 '/figure', '/figcaption', '/details', '/summary']:
        # closing tag
        body = body.replace(f'<{tag}>', '\n')
        # opening/closing with attributes (e.g., <br style="...">)
        if not tag.startswith('/'):
            body = re.sub(rf'<{tag}\b[^>]*>', '\n', body)

    # Convert <br> variants
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'</br\s*>', '\n', body)
    body = re.sub(r'<br\b[^>]*>', '\n', body)

    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', body)

    # Decode HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ')
    text = text.replace('&#10;', '\n').replace('&#39;', "'").replace('&quot;', '"')
    text = text.replace('&#x27;', "'").replace('&#x2F;', '/').replace('&#x3D;', '=')
    # Decode numeric entities &#NNN;
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)

    # Split into lines
    lines = text.split('\n')

    cleaned_lines = []
    for l in lines:
        l = l.strip()
        # Skip: too short, pure punctuation/symbols, base64-like long strings,
        # SharePoint nav chrome, CSS-like selectors
        if len(l) < 2:
            continue
        # Skip lines that are just punctuation/symbols
        if re.match(r'^[\W_]+$', l):
            continue
        # Skip very long single words (base64 data chunks)
        words = l.split()
        if len(words) <= 2 and any(len(w) > 80 for w in words):
            continue
        # Skip lines that look like CSS selectors or JS
        if l.startswith('.') and '{' in l:
            continue
        if l.startswith('@') or l.startswith('var('):
            continue
        # Skip pure URL-only lines (leaked image sources)
        if re.match(r'^https?://\S+$', l):
            continue
        # Skip "data:" URIs
        if l.startswith('data:'):
            continue
        # Skip SharePoint chrome
        skip_phrases = [
            'Skip to main content', 'SharePoint', 'Sign in', 'DiscoverDiscover',
            'PublishPublish', 'BuildBuild', 'OneDriveOneDrive',
            'Add to favorites', 'Share', 'People read this next',
            'Views people read this next', 'Popular with your colleagues',
            'You may also be interested in',
        ]
        if any(l.strip() == p for p in skip_phrases):
            continue
        # Skip "" / "13448" etc. (icon characters + numbers)
        if re.match(r'^[\ue000-\uf8ff][\d]*$', l):
            continue
        if re.match(r'^[\ue000-\uf8ff]+\d+.*$', l):
            continue

        cleaned_lines.append(l)

    return '\n\n'.join(cleaned_lines)


# File mapping: (input_html, output_md)
files = [
    ("/home/Lu/802.1X.html",             os.path.expanduser("~/Documents/juniper_ref/8021X.md")),
    ("/home/Lu/Radius Authentication.html", os.path.expanduser("~/Documents/juniper_ref/Radius_Authentication.md")),
    ("/home/Lu/SNMP.html",                os.path.expanduser("~/Documents/juniper_ref/SNMP.md")),
    ("/home/Lu/CLI.html",                 os.path.expanduser("~/Documents/juniper_ref/CLI.md")),
    ("/home/Lu/Ansible.html",             os.path.expanduser("~/Documents/juniper_ref/Ansible.md")),
    ("/home/Lu/RPD - PCEP.html",          os.path.expanduser("~/Documents/juniper_ref/RPD_PCEP.md")),
    ("/home/Lu/PPPoE.html",               os.path.expanduser("~/Documents/juniper_ref/PPPoE.md")),
    ("/home/Lu/PEM_PSM.html",             os.path.expanduser("~/Documents/juniper_ref/PEM_PSM.md")),
    ("/home/Lu/PEM_PSM (1).html",         os.path.expanduser("~/Documents/juniper_ref/PEM_PSM_2.md")),
    ("/home/Lu/Telemetry.html",           os.path.expanduser("~/Documents/juniper_ref/Telemetry.md")),
]

for input_html, output_md in files:
    print(f"Processing: {os.path.basename(input_html)} -> {os.path.basename(output_md)}")

    with open(input_html, 'r', errors='replace') as f:
        content = f.read()

    result = extract_readable_text(content)

    # Write output
    out_dir = os.path.dirname(output_md)
    os.makedirs(out_dir, exist_ok=True)
    with open(output_md, 'w') as f:
        f.write(result)

    lines_count = len(result.split('\n'))
    # Filter empty lines for actual content count
    real_lines = [l for l in result.split('\n') if l.strip()]
    print(f"  -> {len(result):,} chars, {len(real_lines)} content lines")

print("\nDone! All 10 files extracted.")
