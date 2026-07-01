#!/usr/bin/env python3
"""MERGE ALL BATCHES → final gre_1000.apkg"""
import json, zipfile, tempfile, sqlite3, os, struct, zlib, base64, shutil, time

def _s(v, default=''):
    """Convert value to string, handling lists"""
    if isinstance(v, list):
        return ', '.join(str(x) for x in v if x)
    return str(v) if v else default

def r_jsonl(path):
    items = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s:
                try: items.append(json.loads(s))
                except: pass
    return items

def r_json(path):
    with open(path) as f:
        return json.load(f)

# Load all batches
BATCHES = {
    'gre_batch1_optimized.json':          (1, r_jsonl),      # 1-49
    'gre_batch2_optimized.json':          (2, r_jsonl),      # 50-99
    'gre_words_101_150.json':             (3, r_json),       # 101-150
    'gre_vocab_151_200.json':             (4, r_json),       # 151-200
    'gre_vocab_201_250.json':             (5, r_json),       # 201-250
    'gre_251-300.json':                   (6, r_jsonl),      # 251-300
    'gre_vocab_301_350.json':             (7, r_json),       # 301-350
    'gre_vocab_351-400.json':             (8, r_json),       # 351-400
    'gre_401_450.json':                   (9, r_jsonl),      # 401-450
}

all_optimized = []
for fname, (bid, reader) in sorted(BATCHES.items(), key=lambda x: x[1][0]):
    try:
        items = reader(f'/home/Lu/{fname}')
        print(f"Batch {bid} ({fname}): {len(items)} items")
        all_optimized.extend(items)
    except FileNotFoundError:
        print(f"Batch {bid} ({fname}): NOT FOUND")

print(f"\nTotal: {len(all_optimized)} items")

# Dedupe by word
seen = {}
deduped = []
for item in all_optimized:
    if isinstance(item, dict) and 'word' in item:
        w = item['word'].lower().strip()
        if w not in seen:
            seen[w] = len(deduped)
            deduped.append(item)
        else:
            deduped[seen[w]] = item
    else:
        deduped.append(item)

all_optimized = deduped
print(f"Unique words: {len(seen)}")

# Read source data
with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg') as z:
    col_data = z.read('collection.anki21')
    orig_media = json.loads(z.read('media'))

tmp_orig = tempfile.NamedTemporaryFile(delete=False, suffix='.anki21')
tmp_orig.write(col_data); tmp_orig.close()

orig = sqlite3.connect(tmp_orig.name)
cur = orig.cursor()
cur.execute('SELECT id, flds FROM notes ORDER BY id LIMIT 1000')
all_notes = cur.fetchall()
cur.execute('SELECT models, decks, dconf, conf FROM col')
col_row = cur.fetchone()
decks = json.loads(col_row[1])
orig.close()

word_map = {}
for nid, flds in all_notes:
    fields = flds.split(chr(0x1f))
    word_map[fields[0].strip().lower()] = (nid, fields)

groups = [(1,2,3,4,5,6),(7,8,9,10,11,12),(13,14,15,16,17,18),(19,20,21,22,23,24),(25,26,27,28,29,30)]

new_flds_list = []
note_id_list = []
missing = []

for opt in all_optimized:
    word = opt.get('word', '').lower().strip()
    if word not in word_map:
        missing.append(word)
        continue
    
    nid, orig_fields = word_map[word]
    new_f = orig_fields.copy()
    while len(new_f) < 34: new_f.append('')
    for idx in range(1, 31): new_f[idx] = ''
    
    if 'meanings' in opt:
        for i, m in enumerate(opt['meanings']):
            if i >= 5: break
            pi, mi, si, ai, ei, di = groups[i]
            new_f[pi] = m.get('pos', '')
            new_f[mi] = m.get('meaning', '') or m.get('def', '')
            new_f[si] = m.get('synonym', '') or m.get('syn', '')
            new_f[ai] = m.get('antonym', '') or m.get('ant', '')
            new_f[ei] = m.get('example', '') or m.get('eg', '')
            new_f[di] = m.get('derivative', '')
    elif 'def_cn' in opt:
        new_f[1] = opt.get('pos', '')
        new_f[2] = opt.get('def_cn', '')
        new_f[3] = _s(opt.get('syn', ''))
        new_f[4] = _s(opt.get('ant', ''))
        new_f[5] = opt.get('eg', '')
    elif 'definition' in opt:
        new_f[1] = opt.get('pos', opt.get('part_of_speech', ''))
        new_f[2] = opt.get('definition', '')
        new_f[3] = _s(opt.get('synonym', '')) or _s(opt.get('syn', ''))
        new_f[4] = _s(opt.get('antonym', '')) or _s(opt.get('ant', ''))
        new_f[5] = opt.get('example', '') or opt.get('eg', '')
    elif 'def' in opt:
        new_f[1] = opt.get('pos', '')
        new_f[2] = opt.get('def', '')
        new_f[3] = _s(opt.get('syn', ''))
        new_f[4] = _s(opt.get('ant', ''))
        new_f[5] = opt.get('eg', '')
    
    new_f[33] = opt.get('memo', '')
    new_flds_list.append(chr(0x1f).join(new_f))
    note_id_list.append(nid)

print(f"Processed: {len(note_id_list)} notes")
if missing:
    print(f"Missing: {len(missing)} — {missing[:5]}...")

# Cards
orig2 = sqlite3.connect(tmp_orig.name)
cur2 = orig2.cursor()
nids = set(note_id_list)
phs = ','.join('?' * len(nids))
cur2.execute(f'SELECT id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data FROM cards WHERE nid IN ({phs})', list(nids))
card_map = {}
for c in cur2.fetchall():
    card_map.setdefault(c[1], []).append(c)
orig2.close()

# Build
bd = tempfile.mkdtemp()
bcp = os.path.join(bd, 'collection.anki21')
shutil.copy(tmp_orig.name, bcp)

conn = sqlite3.connect(bcp)
cur = conn.cursor()
for t in ['notes','cards','revlog','graves']: cur.execute(f'DELETE FROM {t}')

gid = 1781512684935
if str(gid) in decks: decks[str(gid)]['name'] = 'gre 1000'
cur.execute('UPDATE col SET decks = ?', (json.dumps(decks),))
cur.execute('UPDATE col SET mod = ?', (int(time.time()),))

now = int(time.time())
for i, nid in enumerate(note_id_list):
    f = new_flds_list[i]
    sf = f.split(chr(0x1f))[0].lower().strip()
    guid = base64.b64encode(os.urandom(8)).decode().rstrip('=').replace('/','_')[:10]
    cs = struct.unpack('>i', struct.pack('>I', zlib.crc32(sf.encode()) & 0xffffffff))[0]
    cur.execute('INSERT INTO notes(id,guid,mid,mod,usn,tags,flds,sfld,csum,flags,data) VALUES(?,?,?,?,?,?,?,?,?,0,?)',
                (nid, guid, 1484878205360, now, -1, '', f, sf, cs, ''))

for nid in note_id_list:
    for c in card_map.get(nid, []):
        cur.execute('INSERT INTO cards(id,nid,did,ord,mod,usn,type,queue,due,ivl,factor,reps,lapses,left,odue,odid,flags,data) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (c[0], nid, gid, c[3], now, -1, c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13], c[14], c[15], c[16], c[17]))

conn.commit(); conn.close()

# Media
needed = set()
for f in new_flds_list:
    fs = f.split(chr(0x1f))
    if len(fs) > 32:
        s = fs[32].strip()
        if s.startswith('[sound:'): needed.add(s.replace('[sound:','').rstrip(']'))

fn2i = {v:k for k,v in orig_media.items()}
nm = {}
ix = 0
for fn in sorted(needed):
    if fn in fn2i: nm[str(ix)] = fn; ix += 1

ap = '/home/Lu/Documents/gre_1000.apkg'
with zipfile.ZipFile(ap, 'w', zipfile.ZIP_DEFLATED) as zo:
    with open(bcp, 'rb') as f: zo.writestr('collection.anki21', f.read())
    zo.writestr('media', json.dumps(nm))
    ofn2i = {v:k for k,v in orig_media.items()}
    with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg') as zi:
        for ni, fn in nm.items():
            if fn in ofn2i: zo.writestr(ni, zi.read(str(ofn2i[fn])))

fs = os.path.getsize(ap)
print(f"\n✅ {ap}")
print(f"   Size: {fs/1024:.1f} KB")
print(f"   Words: {len(note_id_list)}")

# Verify
with zipfile.ZipFile(ap) as z:
    vd = z.read('collection.anki21')
tv = tempfile.NamedTemporaryFile(delete=False, suffix='.anki21')
tv.write(vd); tv.close()
vc = sqlite3.connect(tv.name)
vcur = vc.cursor()
vcur.execute('SELECT COUNT(*) FROM notes')
print(f"   Verified: {vcur.fetchone()[0]} notes")
vcur.execute('SELECT decks FROM col')
vdks = json.loads(vcur.fetchone()[0])
print(f"   Deck: {[d['name'] for d in vdks.values() if d['name']!='Default']}")
vc.close(); os.unlink(tv.name)

shutil.rmtree(bd); os.unlink(tmp_orig.name)
