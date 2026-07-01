#!/usr/bin/env python3
"""Build gre_100.apkg from v3 optimized files (释义→词根→例句→考点)."""
import json
import zipfile
import shutil
import os
import genanki

SRC_APKG = "/home/Lu/Documents/GRE_3000_BrillliantZ.apkg"
OUTPUT = "/home/Lu/Documents/gre_100.apkg"

# Read v3 optimizations - both are JSONL (one obj per line)
b1, b2 = [], []
for path in ["/home/Lu/gre_batch1_v3.json", "/home/Lu/gre_batch2_v3.json"]:
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                b1.append(json.loads(line))

# b1 is actually all 100 words from both files now
all_words = b1
print(f"Total optimized words: {len(all_words)}")

opt_map = {w["name"].lower(): w for w in all_words}

# Extract source apkg
tmp_dir = "/tmp/gre_build_100_v3"
os.makedirs(tmp_dir, exist_ok=True)

shutil.copy2(SRC_APKG, f"{tmp_dir}/source.apkg")
with zipfile.ZipFile(f"{tmp_dir}/source.apkg") as z:
    z.extractall(tmp_dir)

# Get media files
media_files = [f for f in os.listdir(tmp_dir) 
               if os.path.isfile(os.path.join(tmp_dir, f)) 
               and f not in ("meta", "collection.anki21", "collection.anki2")]
print(f"Media files: {len(media_files)}")

import sqlite3
conn = sqlite3.connect(f"{tmp_dir}/collection.anki21")
conn.row_factory = sqlite3.Row

model = genanki.Model(
    1484878205360,
    "brz-GRE3000",
    fields=[
        {"name": "name"}, {"name": "meaning1_partofspeech"}, {"name": "meaning1"},
        {"name": "meaning1_synonym"}, {"name": "meaning1_antonym"}, {"name": "meaning1_example"},
        {"name": "meaning1_derivative"}, {"name": "meaning2_partofspeech"}, {"name": "meaning2"},
        {"name": "meaning2_synonym"}, {"name": "meaning2_antonym"}, {"name": "meaning2_example"},
        {"name": "meaning2_derivative"}, {"name": "meaning3_partofspeech"}, {"name": "meaning3"},
        {"name": "meaning3_synonym"}, {"name": "meaning3_antonym"}, {"name": "meaning3_example"},
        {"name": "meaning3_derivative"}, {"name": "meaning4_partofspeech"}, {"name": "meaning4"},
        {"name": "meaning4_synonym"}, {"name": "meaning4_antonym"}, {"name": "meaning4_example"},
        {"name": "meaning4_derivative"}, {"name": "meaning5_partofspeech"}, {"name": "meaning5"},
        {"name": "meaning5_synonym"}, {"name": "meaning5_antonym"}, {"name": "meaning5_example"},
        {"name": "meaning5_derivative"}, {"name": "phonetic"}, {"name": "sound"}, {"name": "memo"},
    ],
    templates=[{
        "name": "GRE Card (v3)",
        "qfmt": '<div style="font-size: 28px; text-align: center;">{{name}}<br><span style="font-size: 14px; color: #888;">{{phonetic}}</span></div>',
        "afmt": """{{FrontSide}}<hr id="answer">
<div style="font-size: 16px; line-height: 1.8;">
{{meaning1}}<br><br>
<span style="color: #c7254e;">{{memo}}</span><br><br>
{{meaning1_example}}<br><br>
<span style="color: #2a7d2a;">{{meaning1_derivative}}</span>
</div>""",
    }],
)

deck = genanki.Deck(100100101, "gre 100")

cur = conn.execute("SELECT id, flds FROM notes ORDER BY id")
note_count = 0
matched = 0

for idx, row in enumerate(cur):
    if idx >= 100:
        break
    
    flds = row["flds"].split(chr(0x1f))
    word_key = flds[0].strip().lower().split("[")[0].strip()
    
    opt = opt_map.get(word_key)
    
    fields_data = [""] * 34
    for i in range(min(len(flds), 34)):
        fields_data[i] = flds[i] if flds[i] else ""
    
    if opt:
        matched += 1
        # Field 2 = meaning1 (meaning_cn)
        fields_data[2] = opt.get("meaning_cn", fields_data[2])
        # Field 5 = meaning1_example (example sentence)
        fields_data[5] = opt.get("example", fields_data[5])
        # Field 33 = memo (root etymology)
        fields_data[33] = opt.get("memo", "")
        # Field 6 = meaning1_derivative -> store exam_tips here
        fields_data[6] = opt.get("exam_tips", "")
    
    note = genanki.Note(
        model=model,
        fields=fields_data,
        guid=str(hash(word_key))[:8]
    )
    deck.add_note(note)
    note_count += 1

print(f"Notes: {note_count}, Matched: {matched}")

# Build apkg
package = genanki.Package(deck)
media_paths = [os.path.join(tmp_dir, mf) for mf in media_files 
               if os.path.exists(os.path.join(tmp_dir, mf))]
package.media_files = media_paths
package.write_to_file(OUTPUT)

size = os.path.getsize(OUTPUT)
print(f"Saved: {OUTPUT} ({size/1024:.0f} KB)")

# Verify a few entries
import sqlite3 as sql
z = zipfile.ZipFile(OUTPUT)
z.extract("collection.anki2", "/tmp/gre_check/")
v = sql.connect("/tmp/gre_check/collection.anki2")
v.row_factory = sql.Row
c = v.execute("SELECT flds FROM notes ORDER BY id LIMIT 3")
for r in c:
    f = r["flds"].split(chr(0x1f))
    print(f'\n  [{f[0]}]')
    print(f'  释义: {f[2][:40]}')
    print(f'  词根: {f[33][:40]}')
    print(f'  例句: {f[5][:60]}')
    print(f'  考点: {f[6][:80]}')
v.close()
os.unlink("/tmp/gre_check/collection.anki2")

conn.close()
print("\nDone!")
