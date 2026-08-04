#!/usr/bin/env python3
"""Extract all GRE words from gre-asked-words*.md into gre-words.json."""
import re
import json
from pathlib import Path

DOCS = Path.home() / "Documents"
OUTPUT = Path.home() / "workspace/gre/gre-words.json"

files = sorted(DOCS.glob("gre-asked-words*.md"))
words = []

for fp in files:
    text = fp.read_text()
    # Split by "## word" sections (including compound sections like "## a / b / c")
    sections = re.split(r"\n(?=## )", text)
    for sec in sections:
        m = re.match(r"^## (.+)", sec)
        if not m:
            continue
        word = m.group(1).strip()
        # Extract first definition line for preview
        def_match = re.search(r"\*\*释义[：:]\*\*\s*(.+?)(?=\n\*\*|\n\n)", sec)
        preview = def_match.group(1).strip() if def_match else ""
        # Store full entry (without the leading "## word" line)
        body = re.sub(r"^## .+\n", "", sec).strip()
        words.append({
            "word": word,
            "preview": preview,
            "file": fp.name,
            "body": body
        })

OUTPUT.write_text(json.dumps(words, ensure_ascii=False, indent=2))
print(f"Extracted {len(words)} words → {OUTPUT}")
