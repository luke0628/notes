#!/usr/bin/env python3
"""Merge all existing optimized JSON files, add batch3, rebuild apkg"""
import json, zipfile, tempfile, sqlite3, os, struct, zlib, base64, shutil, time

def zlib_crc32(data):
    return struct.unpack('>i', struct.pack('>I', zlib.crc32(data) & 0xffffffff))[0]

# Collect all optimized data
all_optimized = []

# Helper to read JSONL
def read_jsonl(path):
    items = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except: pass
    return items

# Helper to read JSON array
def read_json(path):
    with open(path, 'r') as f:
        return json.load(f)

# Batch 1: JSONL (49 words)
more = read_jsonl('/home/Lu/gre_batch1_optimized.json')
print(f"Batch 1: {len(more)} words")
all_optimized.extend(more)

# Batch 2: JSONL (50 words)
more = read_jsonl('/home/Lu/gre_batch2_optimized.json')
print(f"Batch 2: {len(more)} words")
all_optimized.extend(more)

# Batch 151-200: JSON (50 words)
if os.path.exists('/home/Lu/gre_vocab_151_200.json'):
    more = read_json('/home/Lu/gre_vocab_151_200.json')
    print(f"Batch 151-200: {len(more)} words")
    all_optimized.extend(more)

# Batch 201-250: JSON (50 words)
if os.path.exists('/home/Lu/gre_vocab_201_250.json'):
    more = read_json('/home/Lu/gre_vocab_201_250.json')
    print(f"Batch 201-250: {len(more)} words")
    all_optimized.extend(more)

print(f"\nTotal: {len(all_optimized)} words")

# Check for dupes
from collections import Counter
words = [w['word'].lower() for w in all_optimized if 'word' in w]
for w, c in Counter(words).items():
    if c > 1:
        print(f"  DUPE: {w} (x{c})")

# Dedupe: keep last occurrence
seen = {}
deduped = []
for item in all_optimized:
    if 'word' in item:
        w = item['word'].lower().strip()
        if w not in seen:
            seen[w] = len(deduped)
            deduped.append(item)
        else:
            # Replace
            deduped[seen[w]] = item
    else:
        deduped.append(item)

all_optimized = deduped
words = [w['word'].lower() for w in all_optimized if 'word' in w]
print(f"After dedupe: {len(set(words))} unique words")

# Save combined
with open('/home/Lu/gre_all_optimized.json', 'w') as f:
    json.dump(all_optimized, f, ensure_ascii=False)

print("Saved combined JSON")

# Now build the apkg
with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as z:
    col_data = z.read('collection.anki21')
    orig_media = json.loads(z.read('media'))

tmp_orig = tempfile.NamedTemporaryFile(delete=False, suffix='.anki21')
tmp_orig.write(col_data)
tmp_orig.close()

orig = sqlite3.connect(tmp_orig.name)
cur = orig.cursor()
cur.execute('SELECT id, flds FROM notes ORDER BY id LIMIT 1000')
all_notes = cur.fetchall()
cur.execute('SELECT models, decks, dconf, conf FROM col')
col_row = cur.fetchone()
models = json.loads(col_row[0])
decks = json.loads(col_row[1])
dconf = json.loads(col_row[2])
conf = json.loads(col_row[3])
orig.close()

word_map = {}
for nid, flds in all_notes:
    fields = flds.split(chr(0x1f))
    word = fields[0].strip().lower()
    word_map[word] = (nid, fields)

groups = [(1,2,3,4,5,6),(7,8,9,10,11,12),(13,14,15,16,17,18),(19,20,21,22,23,24),(25,26,27,28,29,30)]

new_flds_list = []
note_id_list = []
missing = []

for opt in all_optimized:
    if 'word' not in opt:
        continue
    word = opt['word'].lower().strip()
    if word not in word_map:
        missing.append(word)
        continue
    
    nid, orig_fields = word_map[word]
    new_fields = orig_fields.copy()
    while len(new_fields) < 34:
        new_fields.append('')
    
    for idx in range(1, 31):
        new_fields[idx] = ''
    
    if 'meanings' in opt:
        for i, m in enumerate(opt['meanings']):
            if i >= 5: break
            pos_i, mean_i, syn_i, ant_i, ex_i, deriv_i = groups[i]
            new_fields[pos_i] = m.get('pos', '')
            new_fields[mean_i] = m.get('meaning', '') or m.get('def', '')
            new_fields[syn_i] = m.get('synonym', '') or m.get('syn', '')
            new_fields[ant_i] = m.get('antonym', '') or m.get('ant', '')
            new_fields[ex_i] = m.get('example', '') or m.get('eg', '')
            new_fields[deriv_i] = m.get('derivative', '')
    elif 'def_cn' in opt:
        # Alternative format: {word, def_cn, pos, eg, syn, ant, memo}
        new_fields[1] = opt.get('pos', '')
        new_fields[2] = opt.get('def_cn', '')
        new_fields[3] = opt.get('syn', '')
        new_fields[4] = opt.get('ant', '')
        new_fields[5] = opt.get('eg', '')
    elif 'def' in opt:
        # {word, def, pos, eg, syn, ant, memo}
        pos = opt.get('pos', '')
        new_fields[1] = pos
        new_fields[2] = opt.get('def', '')
        new_fields[3] = opt.get('syn', '')
        new_fields[4] = opt.get('ant', '')
        new_fields[5] = opt.get('eg', '')
    
    new_fields[33] = opt.get('memo', '')
    
    new_flds_list.append(chr(0x1f).join(new_fields))
    note_id_list.append(nid)

if missing:
    print(f"Missing words ({len(missing)}): {missing[:10]}...")

print(f"Processed: {len(new_flds_list)} notes")

# Get cards
orig2 = sqlite3.connect(tmp_orig.name)
cur2 = orig2.cursor()
note_ids_set = set(note_id_list)
placeholders = ','.join('?' * len(note_ids_set))
cur2.execute(f'SELECT id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data FROM cards WHERE nid IN ({placeholders})', list(note_ids_set))
card_map = {}
for card in cur2.fetchall():
    nid = card[1]
    if nid not in card_map:
        card_map[nid] = []
    card_map[nid].append(card)
orig2.close()

# Build collection
build_dir = tempfile.mkdtemp()
build_col_path = os.path.join(build_dir, 'collection.anki21')
shutil.copy(tmp_orig.name, build_col_path)

conn = sqlite3.connect(build_col_path)
cur = conn.cursor()
cur.execute('DELETE FROM notes')
cur.execute('DELETE FROM cards')
cur.execute('DELETE FROM revlog')
cur.execute('DELETE FROM graves')

gre_deck_id = 1781512684935
if str(gre_deck_id) in decks:
    decks[str(gre_deck_id)]['name'] = 'gre 1000'
cur.execute('UPDATE col SET decks = ?', (json.dumps(decks),))

now_ts = int(time.time())

for i, nid in enumerate(note_id_list):
    flds = new_flds_list[i]
    first_field = flds.split(chr(0x1f))[0]
    new_guid = base64.b64encode(os.urandom(8)).decode().rstrip('=').replace('/', '_')[:10]
    sfld = first_field.lower().strip()
    csum = struct.unpack('>i', struct.pack('>I', zlib.crc32(sfld.encode()) & 0xffffffff))[0]
    
    cur.execute('''
        INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
        VALUES (?, ?, ?, ?, ?, '', ?, ?, ?, 0, '')
    ''', (nid, new_guid, 1484878205360, now_ts, -1, flds, sfld, csum))

for nid in note_id_list:
    for card in card_map.get(nid, []):
        cid, _, did, ord_, mod, usn, type_, queue, due, ivl, factor, reps, lapses, left_, odue, odid, flags, data = card
        cur.execute('''
            INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cid, nid, gre_deck_id, ord_, now_ts, -1, type_, queue, due, ivl, factor, reps, lapses, left_, odue, odid, flags, data))

conn.commit()
conn.close()

# Media
needed_sounds = set()
for flds_str in new_flds_list:
    flds = flds_str.split(chr(0x1f))
    if len(flds) > 32:
        sound = flds[32].strip()
        if sound and sound.startswith('[sound:'):
            fname = sound.replace('[sound:', '').rstrip(']')
            needed_sounds.add(fname)

filename_to_idx = {v: k for k, v in orig_media.items()}
new_media = {}
idx = 0
for fname in sorted(needed_sounds):
    if fname in filename_to_idx:
        new_media[str(idx)] = fname
        idx += 1

apkg_path = '/home/Lu/Documents/gre_1000.apkg'
with zipfile.ZipFile(apkg_path, 'w', zipfile.ZIP_DEFLATED) as zout:
    with open(build_col_path, 'rb') as f:
        zout.writestr('collection.anki21', f.read())
    zout.writestr('media', json.dumps(new_media))
    with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as zin:
        orig_fname_to_idx = {v: k for k, v in orig_media.items()}
        for new_idx_str, fname in new_media.items():
            if fname in orig_fname_to_idx:
                data = zin.read(str(orig_fname_to_idx[fname]))
                zout.writestr(new_idx_str, data)

file_size = os.path.getsize(apkg_path)
print(f"\n✅ {apkg_path}")
print(f"   Size: {file_size/1024:.1f} KB")
print(f"   Words: {len(note_id_list)}")

# Verify
with zipfile.ZipFile(apkg_path, 'r') as z:
    vdata = z.read('collection.anki21')
tmp_v = tempfile.NamedTemporaryFile(delete=False, suffix='.anki21')
tmp_v.write(vdata)
tmp_v.close()
vconn = sqlite3.connect(tmp_v.name)
vcur = vconn.cursor()
vcur.execute('SELECT COUNT(*) FROM notes')
vn = vcur.fetchone()[0]
vcur.execute('SELECT decks FROM col')
vd = json.loads(vcur.fetchone()[0])
deck_name = [d['name'] for d in vd.values() if d['name'] != 'Default']
vconn.close()
os.unlink(tmp_v.name)
print(f"   Verified: {vn} notes, deck={deck_name}")

shutil.rmtree(build_dir)
os.unlink(tmp_orig.name)
