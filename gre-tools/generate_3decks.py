#!/usr/bin/env python3
"""Generate 3 GRE frequency-based Anki decks (High/Medium/Low) with sound files"""

import json, re, genanki, os, zipfile

# --- Paths ---
apkg_source = '/home/Lu/Documents/GRE_3000_BrillliantZ.apkg'
out_dir = '/home/Lu/Documents/'
snd_dir = '/home/Lu/gre_all_sounds'
os.makedirs(snd_dir, exist_ok=True)

# --- Load classified word data ---
categories = {
    'GRE-高频': '/home/Lu/gre_high_done.json',
    'GRE-中频': '/home/Lu/gre_med_done.json',
    'GRE-低频': '/home/Lu/gre_low_done.json',
}

# Load raw data for sound/phonetic
with open('/home/Lu/gre_full_raw.json') as f:
    raw_list = json.load(f)
raw_map = {}
for r in raw_list:
    raw_map[r['name'].lower()] = r

# --- Extract ALL sound files from source apkg ---
print("Extracting sound files from source apkg...")
sound_paths = {}  # word -> local file path
missing_sounds = []

with zipfile.ZipFile(apkg_source) as zf:
    media = json.loads(zf.read('media'))
    num_to_name = {int(k): v for k, v in media.items()}
    
    # Collect all sound filenames we need across all categories
    needed_sounds = set()
    for fname in categories.values():
        with open(fname) as f:
            for line in f:
                if line.strip():
                    w = json.loads(line)
                    key = w['name'].lower()
                    raw = raw_map.get(key, {})
                    snd = raw.get('sound', '')
                    m = re.search(r'\[sound:(.+?)\]', snd)
                    if m:
                        needed_sounds.add(m.group(1))
    
    print(f"Need {len(needed_sounds)} sound files total")
    
    # Extract them
    count = 0
    for snd_name in needed_sounds:
        for num, fname in num_to_name.items():
            if fname == snd_name:
                data = zf.read(str(num))
                out_path = os.path.join(snd_dir, snd_name)
                with open(out_path, 'wb') as f:
                    f.write(data)
                count += 1
                if count % 200 == 0:
                    print(f"  Extracted {count}/{len(needed_sounds)}...")
                break
    
    print(f"Extracted {count} sound files to {snd_dir}")

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

# Model shared across all 3 decks
model_id = 2025062750
model = genanki.Model(
    model_id,
    'GRE精修3000',
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

# --- Generate 3 decks ---
for deck_name, json_file in categories.items():
    short = deck_name.split('-')[1]  # 高频, 中频, 低频
    print(f"\n=== Generating {deck_name} ===")
    
    deck = genanki.Deck(hash(deck_name) % (2**31), deck_name)
    media_files = []
    
    with open(json_file) as f:
        count = 0
        for line in f:
            if not line.strip():
                continue
            w = json.loads(line)
            key = w['name'].lower()
            
            # Get phonetic from raw data
            raw = raw_map.get(key, {})
            phonetic = raw.get('phonetic', '').strip('[]').strip()
            
            # Get sound field
            sound_field = raw.get('sound', '')
            
            fields = [
                w['name'],
                phonetic,
                w.get('meaning_cn', ''),
                w.get('memo', ''),
                w.get('example', ''),
                w.get('changkao', ''),
                w.get('exam_tips', ''),
            ]
            
            note = genanki.Note(model=model, fields=fields)
            deck.add_note(note)
            count += 1
    
    # Collect media files (all extracted sounds in snd_dir)
    all_sounds = [os.path.join(snd_dir, f) for f in os.listdir(snd_dir) 
                  if f.endswith('.mp3')]
    
    out_path = os.path.join(out_dir, f'GRE_{short}.apkg')
    genanki.Package(deck, media_files=all_sounds).write_to_file(out_path)
    size_kb = os.path.getsize(out_path) / 1024
    
    print(f"  {count} words, {len(all_sounds)} sound files")
    print(f"  Written: {out_path}")
    print(f"  Size: {size_kb:.0f} KB ({size_kb/1024:.1f} MB)")

print("\n✅ All 3 decks generated!")
