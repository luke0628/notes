#!/usr/bin/env python3
"""Build random10 apkg with: 释义→⭐词根→例句→·常考→💡同反义 + 发音"""
import json, zipfile, shutil, os, sqlite3, genanki

SRC = "/home/Lu/Documents/GRE_3000_BrillliantZ.apkg"
OUT = "/home/Lu/Documents/gre_random10.apkg"

# Load 10 optimized words
words = []
with open("/home/Lu/gre_random10.json") as f:
    for line in f:
        line = line.strip()
        if line:
            words.append(json.loads(line))

opt_map = {w["name"].lower(): w for w in words}

# Extract source
tmp = "/tmp/gre_random10"
shutil.rmtree(tmp, ignore_errors=True)
os.makedirs(tmp)
shutil.copy2(SRC, f"{tmp}/src.apkg")
with zipfile.ZipFile(f"{tmp}/src.apkg") as z:
    z.extractall(tmp)

media = [f for f in os.listdir(tmp) if os.path.isfile(os.path.join(tmp, f))
         and f not in ("meta", "collection.anki21", "collection.anki2", "src.apkg")]

conn = sqlite3.connect(f"{tmp}/collection.anki21")
conn.row_factory = sqlite3.Row

model = genanki.Model(
    1484878205361,
    "brz-GRE3000 (v3)",
    fields=[
        {"name": "name"}, {"name": "pos"}, {"name": "meaning_cn"},
        {"name": "memo"}, {"name": "example"}, {"name": "changkao"},
        {"name": "exam_tips"}, {"name": "phonetic"}, {"name": "sound"},
    ],
    templates=[{
        "name": "GRE Card",
        "qfmt": '<div style="font-size: 28px; text-align: center;">{{name}}<br><span style="font-size: 14px; color: #888;">{{phonetic}}</span><br>{{sound}}</div>',
        "afmt": """{{FrontSide}}<hr id="answer">
<div style="font-size: 16px; line-height: 1.8;">
<b style="font-size: 18px; color: #333;">{{meaning_cn}}</b><br><br>
<span style="color: #c7254e;">{{memo}}</span><br><br>
<i>{{example}}</i><br><br>
<span style="color: #2a7d2a;">{{changkao}}</span><br><br>
{{exam_tips}}
</div>""",
    }],
)

deck = genanki.Deck(100100102, "gre sample 10")

cur = conn.execute("SELECT flds FROM notes ORDER BY id")
matched = 0
for idx, row in enumerate(cur):
    flds = row["flds"].split(chr(0x1f))
    word_key = flds[0].strip().lower().split("[")[0].strip()
    opt = opt_map.get(word_key)
    if not opt:
        continue
    
    matched += 1
    # Build fields: name, pos, meaning_cn, memo, example, changkao, exam_tips, phonetic, sound
    nf = [""] * 9
    nf[0] = flds[0]  # name
    nf[1] = flds[1]  # pos
    nf[2] = opt.get("meaning_cn", "")
    nf[3] = opt.get("memo", "")
    nf[4] = opt.get("example", "")
    nf[5] = opt.get("changkao", "")
    nf[6] = opt.get("exam_tips", "")
    nf[7] = flds[31] if len(flds) > 31 and flds[31] else ""  # phonetic
    nf[8] = flds[32] if len(flds) > 32 and flds[32] else ""  # sound
    
    note = genanki.Note(model=model, fields=nf, guid=str(hash(word_key))[:8])
    deck.add_note(note)

print(f"Matched: {matched}/{len(words)}")

pkg = genanki.Package(deck)
mp = [os.path.join(tmp, mf) for mf in media if os.path.exists(os.path.join(tmp, mf))]
pkg.media_files = mp
pkg.write_to_file(OUT)
print(f"Saved: {OUT} ({os.path.getsize(OUT)/1024:.0f} KB)")

# Verify
z = zipfile.ZipFile(OUT)
z.extract("collection.anki2", tmp)
v = sqlite3.connect(f"{tmp}/collection.anki2")
for r in v.execute("SELECT flds FROM notes ORDER BY id"):
    f = r[0].split(chr(0x1f))
    snd = f[8] if len(f) > 8 and f[8] else "∅"
    pho = f[7] if len(f) > 7 and f[7] else "∅"
    print(f"  [{f[0]}] 发音={pho[:20]} 声音={snd[:20]}")
v.close()

conn.close()
print("Done!")
