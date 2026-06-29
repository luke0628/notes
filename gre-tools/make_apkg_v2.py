#!/usr/bin/env python3
"""Generate 10-word GRE sample .apkg with bold + sound + 护眼绿"""

import json, re, genanki, os, zipfile

# --- Read refined data ---
with open('/home/Lu/gre_sample_10_bold.json') as f:
    words = [json.loads(line) for line in f if line.strip()]
word_map = {w['name']: w for w in words}

# --- Read raw data for sound & phonetic ---
with open('/home/Lu/gre_sample_10_raw.json') as f:
    raw_list = json.load(f)
raw_map = {}
for r in raw_list:
    raw_map[r['name'].lower()] = r

# --- Extract sound files from apkg ---
apkg_path = '/home/Lu/Documents/GRE_3000_BrillliantZ.apkg'
snd_dir = '/home/Lu/gre_sounds'
os.makedirs(snd_dir, exist_ok=True)

sound_paths = {}

with zipfile.ZipFile(apkg_path) as zf:
    # media.json maps {number: filename}
    media_json = json.loads(zf.read('media'))  # it's 'media' not 'media.json'
    # media_json has {number: filename} mapping
    
    # Build reverse: {filename: number}
    num_to_name = {int(k): v for k, v in media_json.items()}
    
    for r in raw_list:
        snd_field = r.get('sound', '')
        m = re.search(r'\[sound:(.+?)\]', snd_field)
        if m:
            snd_name = m.group(1)
            # Find the number for this filename
            for num, fname in num_to_name.items():
                if fname == snd_name:
                    # Extract by number
                    data = zf.read(str(num))
                    out_path = os.path.join(snd_dir, snd_name)
                    with open(out_path, 'wb') as f:
                        f.write(data)
                    sound_paths[r['name'].lower()] = out_path
                    print(f"  Extracted: {snd_name} ({len(data)} bytes)")
                    break

print(f"\nSound files extracted: {len(sound_paths)}")
for k, v in sound_paths.items():
    print(f"  {k}: {v} ({os.path.getsize(v)} bytes)" if os.path.exists(v) else f"  {k}: MISSING")

# --- Build Anki model ---
CSS = """
.card {
 font-family: 'Noto Sans SC', 'Noto Sans', Arial, sans-serif;
 font-size: 18px;
 text-align: left;
 color: #333333;
 background-color: #C7EDCC;
 padding: 20px;
 line-height: 1.8;
}
.word {
 font-size: 28px;
 font-weight: bold;
 color: #2c3e50;
 margin-bottom: 4px;
}
.word-phonetic {
 font-size: 18px;
 color: #7f8c8d;
 margin-bottom: 12px;
}
.section-label {
 font-weight: bold;
 color: #2c3e50;
 margin-top: 10px;
 border-bottom: 1px solid #bdc3c7;
 padding-bottom: 2px;
}
.meaning-cn {
 font-size: 22px;
 color: #2980b9;
 margin: 8px 0;
 padding-left: 8px;
}
.memo {
 font-size: 18px;
 color: #8e44ad;
 margin: 6px 0;
 padding-left: 8px;
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
 padding-left: 8px;
}
.exam-tips {
 font-size: 17px;
 color: #c0392b;
 margin: 6px 0;
 padding-left: 8px;
}
b, strong {
 color: #d35400;
}
.sound-btn {
 margin-top: 6px;
}
"""

BACK_HTML = """
<div class='word'>{{name}}</div>
<div class='word-phonetic'>{{phonetic}}</div>
<div class='sound-btn'>{{sound_field}}</div>
<hr id='answer'>
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
<div class='sound-btn'>{{sound_field}}</div>
"""

model_id = 2025062703
model = genanki.Model(
    model_id,
    'GRE精修3000 v1',
    fields=[
        {'name': 'name', 'font': 'Noto Sans SC'},
        {'name': 'phonetic', 'font': 'Noto Sans SC'},
        {'name': 'meaning_cn', 'font': 'Noto Sans SC'},
        {'name': 'memo', 'font': 'Noto Sans SC'},
        {'name': 'example', 'font': 'Noto Sans SC'},
        {'name': 'changkao', 'font': 'Noto Sans SC'},
        {'name': 'exam_tips', 'font': 'Noto Sans SC'},
        {'name': 'sound_field', 'font': 'Noto Sans SC'},
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
deck = genanki.Deck(2025062704, 'GRE精修3000-样本')

# Media files list
media_files = list(sound_paths.values())

# Generate notes
for w in words:
    name = w['name']
    key = name.lower()
    
    # Get phonetic from raw data
    raw = raw_map.get(key, {})
    phonetic = raw.get('phonetic', '').strip('[]').strip()
    
    # Build sound field
    sound_field = ''
    if key in sound_paths:
        snd_name = os.path.basename(sound_paths[key])
        sound_field = f'[sound:{snd_name}]'
    
    fields = [
        name,
        phonetic,
        w.get('meaning_cn', ''),
        w.get('memo', ''),
        w.get('example', ''),
        w.get('changkao', ''),
        w.get('exam_tips', ''),
        sound_field,
    ]
    
    note = genanki.Note(model=model, fields=fields)
    deck.add_note(note)
    print(f"  Added note: {name}")

# --- Write .apkg ---
out_path = '/home/Lu/Documents/gre_sample_10_bold.apkg'
genanki.Package(deck, media_files=media_files).write_to_file(out_path)
print(f"\n✅ Written: {out_path}")
print(f"   Size: {os.path.getsize(out_path)} bytes ({os.path.getsize(out_path)/1024:.0f} KB)")
