#!/usr/bin/env python3
"""Build gre_100.apkg from optimized v2 files + source apkg for sound."""
import json
import zipfile
import shutil
import os
import genanki

SRC_APKG = "/home/Lu/Documents/GRE_3000_BrillliantZ.apkg"
OUTPUT = "/home/Lu/Documents/gre_100.apkg"

# Read optimizations - batch1 is JSON array, batch2 is jsonl
with open("/home/Lu/gre_batch1_optimized.json") as f:
    b1 = json.load(f)

b2 = []
with open("/home/Lu/gre_batch2_optimized_v2.json") as f:
    for line in f:
        line = line.strip()
        if line:
            b2.append(json.loads(line))

all_words = b1 + b2
print(f"Total optimized words: {len(all_words)}")

# Build name -> opt lookup
opt_map = {w["name"].lower(): w for w in all_words}

# Extract source data
tmp_dir = "/tmp/gre_build_100"
os.makedirs(tmp_dir, exist_ok=True)

shutil.copy2(SRC_APKG, f"{tmp_dir}/source.apkg")
with zipfile.ZipFile(f"{tmp_dir}/source.apkg") as z:
    z.extractall(tmp_dir)

# Get media files
media_files = []
for fname in sorted(os.listdir(tmp_dir)):
    fpath = os.path.join(tmp_dir, fname)
    if os.path.isfile(fpath) and fname not in ("meta", "collection.anki21", "collection.anki2"):
        media_files.append(fname)

print(f"Media files: {len(media_files)}")

import sqlite3
conn = sqlite3.connect(f"{tmp_dir}/collection.anki21")
conn.row_factory = sqlite3.Row
cur = conn.execute("SELECT id, flds FROM notes ORDER BY id")

# Build notes for genanki
model = genanki.Model(
    1484878205360,
    "brz-GRE3000",
    fields=[
        {"name": "name"},
        {"name": "meaning1_partofspeech"},
        {"name": "meaning1"},
        {"name": "meaning1_synonym"},
        {"name": "meaning1_antonym"},
        {"name": "meaning1_example"},
        {"name": "meaning1_derivative"},
        {"name": "meaning2_partofspeech"},
        {"name": "meaning2"},
        {"name": "meaning2_synonym"},
        {"name": "meaning2_antonym"},
        {"name": "meaning2_example"},
        {"name": "meaning2_derivative"},
        {"name": "meaning3_partofspeech"},
        {"name": "meaning3"},
        {"name": "meaning3_synonym"},
        {"name": "meaning3_antonym"},
        {"name": "meaning3_example"},
        {"name": "meaning3_derivative"},
        {"name": "meaning4_partofspeech"},
        {"name": "meaning4"},
        {"name": "meaning4_synonym"},
        {"name": "meaning4_antonym"},
        {"name": "meaning4_example"},
        {"name": "meaning4_derivative"},
        {"name": "meaning5_partofspeech"},
        {"name": "meaning5"},
        {"name": "meaning5_synonym"},
        {"name": "meaning5_antonym"},
        {"name": "meaning5_example"},
        {"name": "meaning5_derivative"},
        {"name": "phonetic"},
        {"name": "sound"},
        {"name": "memo"},
    ],
    templates=[
        {
            "name": "GRE Card",
            "qfmt": '<div style="font-size: 28px; text-align: center;">{{name}}</div>',
            "afmt": '{{FrontSide}}<hr id="answer"><div style="font-size: 16px;">{{meaning1}}<br><br>{{memo}}<br><br>{{meaning1_example}}</div>',
        }
    ],
)

deck = genanki.Deck(100100100, "gre 100")
media_dir = tmp_dir

note_count = 0
matched = 0
unmatched_words = []

for idx, row in enumerate(cur):
    if idx >= 100:
        break
    
    flds = row["flds"].split(chr(0x1f))
    word_name = flds[0].strip()
    word_key = word_name.lower().split("[")[0].strip()  # strip embedded [sound:...
    
    opt = opt_map.get(word_key)
    if not opt and word_key in opt_map:
        opt = opt_map[word_key]
    
    fields_data = [""] * 34
    
    if opt:
        matched += 1
        # Keep original fields except modify meaning1, example1, memo
        for i in range(min(len(flds), 34)):
            fields_data[i] = flds[i] if flds[i] else ""
        
        # Replace meaning1 (field 2) with Chinese
        fields_data[2] = opt.get("meaning_cn", fields_data[2])
        # Replace example1 (field 5) with new example
        fields_data[5] = opt.get("example", fields_data[5])
        # Replace memo (field 33)
        fields_data[33] = opt.get("memo", "")
    else:
        unmatched_words.append(word_name)
        # Keep original
        for i in range(min(len(flds), 34)):
            fields_data[i] = flds[i] if flds[i] else ""
    
    note = genanki.Note(
        model=model,
        fields=fields_data,
        guid=str(hash(word_name))[:8]
    )
    deck.add_note(note)
    note_count += 1

print(f"\nNotes created: {note_count}")
print(f"Matched with optimization: {matched}")
if unmatched_words:
    print(f"Unmatched: {len(unmatched_words)}: {', '.join(unmatched_words[:10])}")

# Package
package = genanki.Package(deck)
package.media_files = [os.path.join(tmp_dir, mf) for mf in media_files if os.path.exists(os.path.join(tmp_dir, mf))]
package.write_to_file(OUTPUT)

print(f"\nSaved: {OUTPUT}")
print(f"Size: {os.path.getsize(OUTPUT) / 1024:.0f} KB")

conn.close()
