#!/usr/bin/env python3
"""Generate 10 GRE noun words .apkg with bold + sound + 护眼绿"""

import json, re, genanki, os, zipfile

# --- Read refined data ---
with open('/home/Lu/gre_noun10_refined.json') as f:
    words = [json.loads(line) for line in f if line.strip()]

with open('/home/Lu/gre_noun10_raw.json') as f:
    raw_list = json.load(f)
raw_map = {}
for r in raw_list:
    raw_map[r['name'].lower()] = r

# --- Extract sound files ---
apkg_path = '/home/Lu/Documents/GRE_3000_BrillliantZ.apkg'
snd_dir = '/home/Lu/gre_sounds_noun'
os.makedirs(snd_dir, exist_ok=True)

sound_paths = {}

with zipfile.ZipFile(apkg_path) as zf:
    media = json.loads(zf.read('media'))
    num_to_name = {int(k): v for k, v in media.items()}
    
    for r in raw_list:
        name = r['name'].lower()
        snd_field = r.get('sound', '')
        m = re.search(r'\[sound:(.+?)\]', snd_field)
        if m:
            snd_name = m.group(1)
            for num, fname in num_to_name.items():
                if fname == snd_name:
                    data = zf.read(str(num))
                    out_path = os.path.join(snd_dir, snd_name)
                    with open(out_path, 'wb') as f:
                        f.write(data)
                    sound_paths[name] = out_path
                    print(f"✓ {name} -> {snd_name} ({len(data)} bytes)")
                    break
            else:
                print(f"  {name}: sound not in media")
        else:
            print(f"  {name}: no sound field")

print(f"\nFound {len(sound_paths)} sound files")

# --- Build Anki model ---
CSS = """
.card {
 font-family: 'Noto Sans SC', 'Noto Sans', Arial, sans-serif;
 font-size: 18px;
 text-align: left;
 color: #1a1a2e;
 background-color: #C7EDCC;
 padding: 20px 24px;
 line-height: 1.8;
}
.word {
 font-size: 30px;
 font-weight: bold;
 color: #1a1a2e;
 margin-bottom: 2px;
}
.word-phonetic {
 font-size: 18px;
 color: #666;
 margin-bottom: 10px;
}
.section-label {
 font-weight: bold;
 color: #2c3e50;
 margin-top: 12px;
 font-size: 15px;
 border-bottom: 1px solid #a8d8a8;
 padding-bottom: 1px;
}
.meaning-cn {
 font-size: 22px;
 color: #2980b9;
 margin: 6px 0;
 padding-left: 6px;
}
.memo {
 font-size: 18px;
 color: #8e44ad;
 margin: 6px 0;
 padding-left: 6px;
}
.example {
 font-size: 18px;
 color: #2c3e50;
 margin: 8px 0;
 padding-left: 10px;
 border-left: 3px solid #27ae60;
}
.changkao {
 font-size: 17px;
 color: #e67e22;
 margin: 6px 0;
 padding-left: 6px;
}
.exam-tips {
 font-size: 17px;
 color: #c0392b;
 margin: 6px 0;
 padding-left: 6px;
}
b, strong {
 color: #d35400;
}
"""

BACK_HTML = """
<div class='word'>{{name}}</div>
<div class='word-phonetic'>{{phonetic}}</div>
<hr id='answer' style='border-color:#a8d8a8'>
<div class='section-label'>📖 释义</div>
<div class='meaning-cn'>{{meaning_cn}}</div>
<div class='section-label'>⭐ 词根</div>
<div class='memo'>{{memo}}</div>
<div class='section-label'>📝 例句</div>
<div class='example'>{{example}}</div>
<div class='changkao'>{{changkao}}</div>
<div class='exam-tips'>{{exam_tips}}</div>
"""

FRONT_HTML = """
<div class='word'>{{name}}</div>
<div class='word-phonetic'>{{phonetic}}</div>
"""

model_id = 2025062712
model = genanki.Model(
    model_id,
    'GRE精修3000 v1',
    fields=[
        {'name': 'name'},
        {'name': 'phonetic'},
        {'name': 'meaning_cn'},
        {'name': 'memo'},
        {'name': 'example'},
        {'name': 'changkao'},
        {'name': 'exam_tips'},
    ],
    templates=[
        {
            'name': 'GRE精修3000',
            'qfmt': FRONT_HTML,
            'afmt': BACK_HTML,
        },
    ],
    css=CSS,
)

# --- Build deck ---
deck = genanki.Deck(2025062713, 'GRE精修3000-名词样本')
media_files = list(sound_paths.values())

for w in words:
    name = w['name']
    key = name.lower()
    raw = raw_map.get(key, {})
    phonetic = raw.get('phonetic', '').strip('[]').strip()
    
    fields = [
        name,
        phonetic,
        w.get('meaning_cn', ''),
        w.get('memo', ''),
        w.get('example', ''),
        w.get('changkao', ''),
        w.get('exam_tips', ''),
    ]
    
    note = genanki.Note(model=model, fields=fields)
    deck.add_note(note)
    print(f"  Added: {name}")

out_path = '/home/Lu/Documents/gre_noun10.apkg'
genanki.Package(deck, media_files=media_files).write_to_file(out_path)
print(f"\n✅ Written: {out_path}")
print(f"   Size: {os.path.getsize(out_path)} bytes ({os.path.getsize(out_path)/1024:.0f} KB)")
