#!/usr/bin/env python3
"""Build optimized GRE apkg from batch 1 optimized data"""
import json, zipfile, tempfile, sqlite3, os, struct, zlib, base64, shutil

def zlib_crc32(data):
    return struct.unpack('>i', struct.pack('>I', zlib.crc32(data) & 0xffffffff))[0]

# Read optimized data
with open('/home/Lu/gre_batch1_optimized.json', 'r') as f:
    optimized = json.load(f)

print(f"Loaded {len(optimized)} optimized words")

# Read original collection
with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as z:
    col_data = z.read('collection.anki21')
    orig_media = json.loads(z.read('media'))

tmp_orig = tempfile.NamedTemporaryFile(delete=False, suffix='.anki21')
tmp_orig.write(col_data)
tmp_orig.close()

orig = sqlite3.connect(tmp_orig.name)
cur = orig.cursor()

# Get the 1000 words with their ids, ordered by id
cur.execute('SELECT id, flds FROM notes ORDER BY id LIMIT 1000')
all_notes = cur.fetchall()

# Build mapping: word -> original flds
orig_flds_map = {}
for nid, flds in all_notes:
    fields = flds.split(chr(0x1f))
    word = fields[0].strip().lower()
    orig_flds_map[word] = (nid, fields)

# Get models and decks
cur.execute('SELECT models, decks, dconf, conf FROM col')
col_row = cur.fetchone()
orig.close()

print(f"Original notes available: {len(orig_flds_map)}")

# Build new flds for each optimized word
new_flds_list = []
new_note_ids = []
used_ids = set()

for opt in optimized:
    word = opt['word'].lower().strip()
    
    if word not in orig_flds_map:
        print(f"WARNING: '{word}' not found in original deck, skipping")
        continue
    
    nid, orig_fields = orig_flds_map[word]
    
    # Start with original fields (34 fields)
    new_fields = orig_fields.copy()
    while len(new_fields) < 34:
        new_fields.append('')
    
    # Clear all meaning fields first
    meaning_fields = list(range(1, 31))  # Fields 1-30
    for idx in meaning_fields:
        new_fields[idx] = ''
    
    # Fill in optimized meanings
    for i, m in enumerate(opt['meanings']):
        group_map = {
            0: (1, 2, 3, 4, 5, 6),
            1: (7, 8, 9, 10, 11, 12),
            2: (13, 14, 15, 16, 17, 18),
            3: (19, 20, 21, 22, 23, 24),
            4: (25, 26, 27, 28, 29, 30),
        }
        if i >= 5:
            print(f"  WARNING: {word} has >5 meanings, truncating")
            break
        
        pos_i, mean_i, syn_i, ant_i, ex_i, deriv_i = group_map[i]
        new_fields[pos_i] = m.get('pos', '')
        new_fields[mean_i] = m.get('meaning', '')
        new_fields[syn_i] = m.get('synonym', '')
        new_fields[ant_i] = m.get('antonym', '')
        new_fields[ex_i] = m.get('example', '')
        new_fields[deriv_i] = m.get('derivative', '')
    
    # Set memo field
    new_fields[33] = opt.get('memo', '')
    
    new_flds_list.append(chr(0x1f).join(new_fields))
    used_ids.add(nid)
    new_note_ids.append(nid)

print(f"Processed {len(new_flds_list)} words")

# Now build the apkg
build_dir = tempfile.mkdtemp()
build_col_path = os.path.join(build_dir, 'collection.anki21')
shutil.copy(tmp_orig.name, build_col_path)

conn = sqlite3.connect(build_col_path)
cur = conn.cursor()

# Delete all existing data
cur.execute('DELETE FROM notes')
cur.execute('DELETE FROM cards')
cur.execute('DELETE FROM revlog')
cur.execute('DELETE FROM graves')

# Rename deck to "gre 1000"
decks_data = json.loads(col_row[1])
gre_deck_id = 1781512684935
if str(gre_deck_id) in decks_data:
    decks_data[str(gre_deck_id)]['name'] = 'gre 1000'
cur.execute('UPDATE col SET decks = ?', (json.dumps(decks_data),))

mid = 1484878205360  # Model ID for brz-GRE3000
now = int(time.time())

# Insert notes
for i, opt_word in enumerate(optimized):
    word = opt_word['word'].lower().strip()
    if word not in orig_flds_map:
        continue
    
    nid = orig_flds_map[word][0]
    new_guid = base64.b64encode(os.urandom(8)).decode().rstrip('=').replace('/', '_')[:10]
    new_flds = new_flds_list[len([x for x in optimized[:i] if x['word'].lower().strip() in orig_flds_map])]
    
    # Wait, need proper index tracking
    # Let me just iterate through new_flds_list with proper alignment

conn.close()
shutil.rmtree(build_dir)
os.unlink(tmp_orig.name)
print("Phase 1 done - data prepared")
