#!/usr/bin/env python3
"""Build final apkg from optimized data files"""
import json, zipfile, tempfile, sqlite3, os, struct, zlib, base64, shutil, time

def zlib_crc32(data):
    return struct.unpack('>i', struct.pack('>I', zlib.crc32(data) & 0xffffffff))[0]

# Read all optimized words from all batch files
all_optimized = []

# Batch 1 (JSONL)
with open('/home/Lu/gre_batch1_optimized.json', 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                all_optimized.append(json.loads(line))
            except: pass

# Batch 2 (JSONL)
with open('/home/Lu/gre_batch2_optimized.json', 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                all_optimized.append(json.loads(line))
            except: pass

print(f"Total optimized words: {len(all_optimized)}")

# Read original apkg
with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as z:
    col_data = z.read('collection.anki21')
    orig_media = json.loads(z.read('media'))

tmp_orig = tempfile.NamedTemporaryFile(delete=False, suffix='.anki21')
tmp_orig.write(col_data)
tmp_orig.close()

orig = sqlite3.connect(tmp_orig.name)
cur = orig.cursor()

# Get first 1000 notes
cur.execute('SELECT id, flds FROM notes ORDER BY id LIMIT 1000')
all_notes = cur.fetchall()

# Get col data
cur.execute('SELECT models, decks, dconf, conf FROM col')
col_row = cur.fetchone()
models = json.loads(col_row[0])
decks = json.loads(col_row[1])
dconf = json.loads(col_row[2])
conf = json.loads(col_row[3])
orig.close()

# Build word map
word_map = {}
for nid, flds in all_notes:
    fields = flds.split(chr(0x1f))
    word = fields[0].strip().lower()
    word_map[word] = (nid, fields)

# Build new flds
new_flds_list = []
note_id_list = []

groups = [(1,2,3,4,5,6),(7,8,9,10,11,12),(13,14,15,16,17,18),(19,20,21,22,23,24),(25,26,27,28,29,30)]

for opt in all_optimized:
    word = opt['word'].lower().strip()
    if word not in word_map:
        print(f"WARNING: '{word}' not found")
        continue
    
    nid, orig_fields = word_map[word]
    new_fields = orig_fields.copy()
    while len(new_fields) < 34:
        new_fields.append('')
    
    # Clear meanings
    for idx in range(1, 31):
        new_fields[idx] = ''
    
    # Fill new meanings
    for i, m in enumerate(opt['meanings']):
        if i >= 5:
            break
        pos_i, mean_i, syn_i, ant_i, ex_i, deriv_i = groups[i]
        new_fields[pos_i] = m.get('pos', '')
        new_fields[mean_i] = m.get('meaning', '')
        new_fields[syn_i] = m.get('synonym', '')
        new_fields[ant_i] = m.get('antonym', '')
        new_fields[ex_i] = m.get('example', '')
        new_fields[deriv_i] = m.get('derivative', '')
    
    new_fields[33] = opt.get('memo', '')
    new_flds_list.append(chr(0x1f).join(new_fields))
    note_id_list.append(nid)

print(f"Processed {len(new_flds_list)} notes")

# Get cards
orig2 = sqlite3.connect(tmp_orig.name)
cur2 = orig2.cursor()
note_ids_set = set(note_id_list)
placeholders = ','.join('?' * len(note_ids_set))
cur2.execute(f'SELECT id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data FROM cards WHERE nid IN ({placeholders})', list(note_ids_set))
cards_rows = cur2.fetchall()
orig2.close()

card_map = {}
for card in cards_rows:
    nid = card[1]
    if nid not in card_map:
        card_map[nid] = []
    card_map[nid].append(card)

# Build new collection
build_dir = tempfile.mkdtemp()
build_col_path = os.path.join(build_dir, 'collection.anki21')
shutil.copy(tmp_orig.name, build_col_path)

conn = sqlite3.connect(build_col_path)
cur = conn.cursor()

cur.execute('DELETE FROM notes')
cur.execute('DELETE FROM cards')
cur.execute('DELETE FROM revlog')
cur.execute('DELETE FROM graves')

# Rename deck
gre_deck_id = 1781512684935
if str(gre_deck_id) in decks:
    decks[str(gre_deck_id)]['name'] = 'gre 1000'
cur.execute('UPDATE col SET decks = ?', (json.dumps(decks),))

now_ts = int(time.time())

# Insert notes
notes_added = 0
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
    notes_added += 1

# Insert cards
cards_added = 0
for nid in note_id_list:
    for card in card_map.get(nid, []):
        cid, _, did, ord_, mod, usn, type_, queue, due, ivl, factor, reps, lapses, left_, odue, odid, flags, data = card
        cur.execute('''
            INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cid, nid, gre_deck_id, ord_, now_ts, -1, type_, queue, due, ivl, factor, reps, lapses, left_, odue, odid, flags, data))
        cards_added += 1

conn.commit()
conn.close()

print(f"Notes: {notes_added}, Cards: {cards_added}")

# Handle media
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

print(f"Media files: {len(new_media)}")

# Write apkg
apkg_path = '/home/Lu/Documents/gre_1000.apkg'
with zipfile.ZipFile(apkg_path, 'w', zipfile.ZIP_DEFLATED) as zout:
    with open(build_col_path, 'rb') as f:
        zout.writestr('collection.anki21', f.read())
    zout.writestr('media', json.dumps(new_media))
    with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as zin:
        orig_fname_to_idx = {v: k for k, v in orig_media.items()}
        for new_idx_str, fname in new_media.items():
            if fname in orig_fname_to_idx:
                old_idx = orig_fname_to_idx[fname]
                data = zin.read(str(old_idx))
                zout.writestr(new_idx_str, data)

file_size = os.path.getsize(apkg_path)
print(f"\n✅ Written: {apkg_path}")
print(f"   Size: {file_size/1024:.1f} KB")
print(f"   Words: {notes_added}")

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
vcur.execute('SELECT COUNT(*) FROM cards')
vc = vcur.fetchone()[0]
vcur.execute('SELECT decks FROM col')
vd = json.loads(vcur.fetchone()[0])
deck_name = [d['name'] for d in vd.values() if d['name'] != 'Default'][0]
vconn.close()
os.unlink(tmp_v.name)
print(f"   Verified: {vn} notes, {vc} cards, deck='{deck_name}'")

shutil.rmtree(build_dir)
os.unlink(tmp_orig.name)
