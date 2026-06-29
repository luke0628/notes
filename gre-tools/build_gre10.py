#!/usr/bin/env python3
"""
Build a stand-alone .apkg with only 10 optimized GRE words.
Uses genanki for the apkg, mirrors the original model (brz-GRE3000) exactly.
"""
import zipfile, json, tempfile, os, sqlite3, shutil, hashlib, struct, io

# ── Step 1: Clone the original collection, extract only 10 notes ──

with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as z:
    col_data = z.read('collection.anki21')

tmp_orig = tempfile.NamedTemporaryFile(delete=False, suffix='.anki21')
tmp_orig.write(col_data)
tmp_orig.close()

orig = sqlite3.connect(tmp_orig.name)
cur = orig.cursor()

# Get the col config
cur.execute('SELECT models, decks, dconf, conf FROM col')
col_row = cur.fetchone()
models = json.loads(col_row[0])
decks = json.loads(col_row[1])
dconf = json.loads(col_row[2])
conf = json.loads(col_row[3])

# Get the first 10 notes as they appear in the original (sorted by id)
cur.execute('SELECT id, guid, mid, flds, sfld, csum, tags FROM notes ORDER BY id LIMIT 10')
notes_rows = cur.fetchall()

# Get cards for those 10 notes (one card per note usually)
note_ids = [r[0] for r in notes_rows]
placeholders = ','.join('?' * len(note_ids))
cur.execute(f'SELECT id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data FROM cards WHERE nid IN ({placeholders})', note_ids)
cards_rows = cur.fetchall()

# Get the deck id for GRE_3000_BrillliantZ
gre_deck_id = 1781512684935

orig.close()

print(f"Extracted {len(notes_rows)} notes, {len(cards_rows)} cards")

# ── Step 2: Optimize the content (field data) ──

# Build optimized field arrays for each word
# Each entry: [name, pos1, meaning1, syn1, ant1, ex1, deriv1, ... rest empty, phonetic, sound, memo]
# We'll keep the 34-field structure but only fill the relevant ones

# First, extract original flds for each note
notes_original_flds = []
for row in notes_rows:
    notes_original_flds.append(row[3].split(chr(0x1f)))

# Now apply optimizations
optimizations = {
    # abandon
    0: {
        # Keep only the core GRE meanings: 放纵(n) + 放弃(v)
        # Remove: 停止(v)
        # Add roots/mnemonic + GRE tips to memo field[33]
        # Replace weak examples with GRE-level ones
        'field_overrides': {
            2: '放纵(n): 完全放任，毫无约束',  # meaning1 - core
            3: 'unconstraint, unrestraint, recklessness',
            4: 'restraint, constraint, self-control',
            5: 'The children shouted and sang with joyful abandon at the amusement park.',
            8: '放弃(v): 彻底抛弃/放弃',  # meaning2 - core
            9: 'relinquish, renounce, forswear, desert',
            10: 'retain, keep, maintain, reclaim',
            11: 'They had to abandon their research after funding was withdrawn.',
            20: '', 21: '', 22: '', 23: '',  # Remove meaning4 (stop doing)
            33: '⚡ab-离开+band-命令/控制 | 考点: abandon oneself to(沉溺于), with abandon(纵情地). NOT "停止做某事"(GRE不考). 同根: ban(禁止)'
        }
    },
    # abase
    1: {
        'field_overrides': {
            2: '贬低，降低(地位威望尊严)',
            3: 'degrade, debase, demean, humiliate, belittle',
            4: 'exalt, elevate, extol, praise',
            5: 'The journalist refused to abase herself by writing tabloid gossip.',
            8: '', 9: '', 10: '', 11: '',  # Remove second meaning if any (none in original)
            33: '⚡a-使+basse-低→使低→贬低 | 考点: abase oneself(贬低自己), abase≠abash(使尴尬,短暂). 同根: bass(低), base(基础)'
        }
    },
    # abash
    2: {
        'field_overrides': {
            2: '使尴尬，使羞愧(失去镇定)',
            3: 'disconcert, discomfit, fluster, mortify, embarrass',
            4: 'embolden, reassure, compose',
            5: 'The experienced lecturer was not at all abashed by the technical glitch.',
            33: '⚡源自古法语 esbair(使惊讶) → 尴尬 | 考点: not abashed(毫不尴尬,常考题眼). abash 是短暂尴尬≠abase(长期贬低). 同义: disconcert'
        }
    },
    # abate
    3: {
        'field_overrides': {
            2: '减轻减弱，减少(程度或数量)',
            3: 'subside, wane, recede, taper, diminish, ebb',
            4: 'intensify, escalate, surge, augment',
            5: 'The storm finally abated after three days of relentless wind and rain.',
            14: '', 15: '', 17: '',  # Remove meaning3 (stop/撤销 - not core GRE)
            33: '⚡a-使+battre-打击→反复打击→使减弱 | 考点: 常考自然现象(暴风雨/疼痛)减弱. 同义辨析: abate(渐进减弱)≠subside(很快平息). NOT "停止/废除"(法律义GRE不考)'
        }
    },
    # abbreviate
    4: {
        'field_overrides': {
            2: '缩写，缩短',
            3: 'abridge, curtail, truncate, condense, shorten',
            4: 'extend, elongate, protract, prolong',
            5: 'The professor abbreviated the lecture to allow time for discussion.',
            33: '⚡ab-加强+brevi-短+ate动词→弄短→缩写 | 考点: abridge(同义常互换). 同根: brief(简短的), brevity(简洁)'
        }
    },
    # abdicate
    5: {
        'field_overrides': {
            2: '正式放弃(权力/王位/责任)',
            3: 'renounce, relinquish, cede, resign, step down',
            4: 'usurp, assume, seize, retain',
            5: 'The CEO abdicated all responsibility for the company\'s ethical violations.',
            33: '⚡ab-离开+dic-说+ate→宣告离开→退位/放弃 | 考点: abdicate the throne(退位), abdicate responsibility(推卸责任). 同根: dictate(口述), predict(预言)'
        }
    },
    # aberrant
    6: {
        'field_overrides': {
            2: '异常的，脱离常规的',
            3: 'abnormal, anomalous, deviant, atypical, irregular',
            4: 'normal, typical, standard, customary',
            5: 'The patient\'s aberrant test results warranted further investigation.',
            33: '⚡ab-偏离+err-错误→偏离正轨→异常 | 考点: 强调偏离正常标准,常用于科学/统计语境. 同根: err(犯错), error(错误)'
        }
    },
    # abet
    7: {
        'field_overrides': {
            8: '', 9: '', 10: '', 11: '',  # Remove all but meaning1
            2: '怂恿，教唆(帮助做坏事)',
            3: 'instigate, foment, incite, provoke, ferment',
            4: 'hinder, impede, deter, dissuade',
            5: 'The hacker was charged with aiding and abetting the cyberattack.',
            33: '⚡源自古法语 abeter(引诱狗去咬) → 怂恿 | 考点: aid and abet(法律术语"协助教唆",GRE常考短语). 同根: bait(诱饵)'
        }
    },
    # abeyance
    8: {
        'field_overrides': {
            2: '中止，暂时搁置',
            3: 'suspension, dormancy, latency, moratorium, quiescence',
            4: 'continuation, resumption, fulfillment',
            5: 'Legal proceedings were held in abeyance pending new evidence.',
            33: '⚡源自古法语 abeance(期待,张口等待) → 搁置等待 | 考点: in abeyance(搁置中,常考短语). 同义: suspension(更正式), dormancy(休眠)'
        }
    },
    # abhor
    9: {
        'field_overrides': {
            2: '深恶痛绝，极度厌恶',
            3: 'detest, loathe, abominate, execrate, despise',
            4: 'adore, cherish, revere, esteem',
            5: 'The environmentalist abhors the practice of unnecessary deforestation.',
            33: '⚡ab-离开+hor-颤抖→吓得发抖→厌恶 | 考点: abhor程度>hate>dislike. 同根: horrible(可怕的), horror(恐惧). 常考对比: abhor≠abhore(拼写陷阱)'
        }
    }
}

# Build new flds strings
new_flds_list = []
for i, row in enumerate(notes_rows):
    # Start with original fields
    flds = notes_original_flds[i].copy()
    # Ensure 34 fields (pad if original is shorter)
    while len(flds) < 34:
        flds.append('')
    
    opt = optimizations.get(i, {})
    overrides = opt.get('field_overrides', {})
    for field_idx, val in overrides.items():
        flds[field_idx] = val
    
    # Join back with field separator
    new_flds_list.append(chr(0x1f).join(flds))

# ── Step 3: Build the new apkg ──

# Create a new collection in a temp dir
tmp_dir = tempfile.mkdtemp()
new_col_path = os.path.join(tmp_dir, 'collection.anki21')

# Copy the original collection as base, then modify
shutil.copy(tmp_orig.name, new_col_path)

new_conn = sqlite3.connect(new_col_path)
new_cur = new_conn.cursor()

# 3a. Delete all existing notes and cards
new_cur.execute('DELETE FROM notes')
new_cur.execute('DELETE FROM cards')
new_cur.execute('DELETE FROM revlog')
new_cur.execute('DELETE FROM graves')

# 3b. Update decks - rename to "gre 10"
new_decks = json.loads(col_row[1])  # fresh copy
if str(gre_deck_id) in new_decks:
    new_decks[str(gre_deck_id)]['name'] = 'gre 10'
new_cur.execute('UPDATE col SET decks = ?', (json.dumps(new_decks),))

# 3c. Insert the 10 notes with new GUIDs (to not conflict with existing)
import random, time, base64
now_ts = int(time.time() * 1000)

for i, row in enumerate(notes_rows):
    old_id, old_guid, mid, old_flds, sfld, csum, tags = row
    
    # Generate new GUID
    new_guid = base64.b64encode(os.urandom(8)).decode().rstrip('=').replace('/', '_')[:10]
    
    new_flds = new_flds_list[i]
    
    # Compute new sfld (sort field = first field)
    first_field = new_flds.split(chr(0x1f))[0]
    new_sfld = first_field.lower()
    
    # Compute csum (checksum of sort field)
    new_csum = zlib_crc32(new_sfld.encode())
    
    new_cur.execute('''
        INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '')
    ''', (old_id, new_guid, mid, now_ts // 1000, -1, '', new_flds, new_sfld, new_csum))

# 3d. Insert cards - one per note, pointing to gre 10 deck
for i, row in enumerate(cards_rows):
    cid, nid, did, ord_, mod, usn, type_, queue, due, ivl, factor, reps, lapses, left_, odue, odid, flags, data = row
    
    new_cur.execute('''
        INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cid + 1000000, old_id := next(r[0] for r in notes_rows if r[0] == nid), gre_deck_id, ord_, now_ts // 1000, -1, type_, queue, due + i*100, ivl, factor, reps, lapses, left_, odue, odid, flags, data))

    # Hmm, I need to track note_id mapping - let me redo this properly

new_conn.commit()
new_conn.close()

# Let me redo this more carefully
shutil.rmtree(tmp_dir)

print("Phase 2: Building final apkg...")

# ── Cleaner approach ──

def zlib_crc32(data):
    return struct.unpack('>i', struct.pack('>I', zlib.crc32(data) & 0xffffffff))[0]

import zlib

def zlib_crc32(data):
    return struct.unpack('>i', struct.pack('>I', zlib.crc32(data) & 0xffffffff))[0]

# Work in a temp directory
build_dir = tempfile.mkdtemp()
build_col_path = os.path.join(build_dir, 'collection.anki21')

# Copy original col data
shutil.copy(tmp_orig.name, build_col_path)

conn = sqlite3.connect(build_col_path)
cur = conn.cursor()

# Delete existing data
cur.execute('DELETE FROM notes')
cur.execute('DELETE FROM cards')
cur.execute('DELETE FROM revlog')
cur.execute('DELETE FROM graves')

# Rename deck
decks_data = json.loads(col_row[1])
if str(gre_deck_id) in decks_data:
    decks_data[str(gre_deck_id)]['name'] = 'gre 10'
cur.execute('UPDATE col SET decks = ?', (json.dumps(decks_data),))

# Update mod time
cur.execute('UPDATE col SET mod = ?', (now_ts // 1000,))

# Also update deck config references if needed
# Re-read col to get current dconf
cur.execute('SELECT dconf FROM col')
dconf_data = json.loads(cur.fetchone()[0])
# Ensure gre_deck_id has a conf
if str(gre_deck_id) in decks_data:
    did_str = str(gre_deck_id)
    decks_data[did_str]['conf'] = 1  # point to Default config

cur.execute('UPDATE col SET decks = ?', (json.dumps(decks_data),))

# Add notes and cards
now = int(time.time())
for i, old_note_row in enumerate(notes_rows):
    old_id, old_guid, mid, old_flds, old_sfld, old_csum, tags = old_note_row
    new_guid = base64.b64encode(os.urandom(8)).decode().rstrip('=').replace('/', '_')[:10]
    
    new_flds = new_flds_list[i]
    first_field = new_flds.split(chr(0x1f))[0]
    new_sfld = first_field.lower()
    new_csum = zlib_crc32(new_sfld.encode())
    
    # Use original note id for consistency
    cur.execute('''
        INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '')
    ''', (old_id, new_guid, mid, now, -1, '', new_flds, new_sfld, new_csum))

# Cards - one per note
for i, old_card_row in enumerate(cards_rows):
    cid, nid, did, ord_, mod, usn, type_, queue, due, ivl, factor, reps, lapses, left_, odue, odid, flags, data = old_card_row
    
    # New card id (keep unique)
    new_cid = cid
    # New note id (must match the note we inserted)
    new_nid = note_ids[i]
    
    cur.execute('''
        INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (new_cid, new_nid, gre_deck_id, ord_, now, -1, type_, queue, i*10, ivl, factor, reps, lapses, left_, odue, odid, flags, data))

conn.commit()

# Verify
cur.execute('SELECT COUNT(*) FROM notes')
print(f"Notes in new collection: {cur.fetchone()[0]}")
cur.execute('SELECT COUNT(*) FROM cards')
print(f"Cards in new collection: {cur.fetchone()[0]}")

conn.close()

# ── Step 4: Package as apkg ──
# Follow Anki 2.1 apkg format: collection.anki21 + media map + optional media files

# Get media from original
with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as z:
    media_map = json.loads(z.read('media'))

# Build media map for sounds we actually need
# Extract the sound filenames from the optimized flds
needed_sounds = set()
for flds_str in new_flds_list:
    flds = flds_str.split(chr(0x1f))
    sound_field = flds[32]  # Field[32] = sound
    if sound_field and sound_field.startswith('[sound:'):
        fname = sound_field.replace('[sound:', '').rstrip(']')
        needed_sounds.add(fname)

print(f"Needed sounds: {len(needed_sounds)}")

# Build new media map
new_media = {}
new_media_idx = 0
with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as z:
    all_media = json.loads(z.read('media'))
    # Reverse map: filename -> idx
    filename_to_idx = {v: k for k, v in all_media.items()}
    
    for fname in needed_sounds:
        if fname in filename_to_idx:
            new_media[str(new_media_idx)] = fname
            new_media_idx += 1

print(f"Media files: {len(new_media)}")

# Write the apkg
apkg_path = '/home/Lu/Documents/gre_10.apkg'
with zipfile.ZipFile(apkg_path, 'w', zipfile.ZIP_DEFLATED) as zout:
    # Write collection
    with open(build_col_path, 'rb') as f:
        zout.writestr('collection.anki21', f.read())
    
    # Write media map
    zout.writestr('media', json.dumps(new_media))
    
    # Copy needed media files from original
    with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as zin:
        filename_to_idx = {v: k for k, v in all_media.items()}
        for fname in needed_sounds:
            if fname in filename_to_idx:
                idx = filename_to_idx[fname]
                data = zin.read(str(idx))
                zout.writestr(str(new_media_idx), data)  # Hmm, need proper index

# Let me redo media handling
# Actually, for the final apkg, the media files need to be stored with the index matching new_media keys

apkg_path = '/home/Lu/Documents/gre_10.apkg'
with zipfile.ZipFile(apkg_path, 'w', zipfile.ZIP_DEFLATED) as zout:
    # Write collection
    with open(build_col_path, 'rb') as f:
        zout.writestr('collection.anki21', f.read())
    
    # Write media map
    zout.writestr('media', json.dumps(new_media))
    
    # Copy needed media files
    with zipfile.ZipFile('/home/Lu/Documents/GRE_3000_BrillliantZ.apkg', 'r') as zin:
        orig_media = json.loads(zin.read('media'))
        orig_fname_to_idx = {v: k for k, v in orig_media.items()}
        
        for new_idx_str, fname in new_media.items():
            if fname in orig_fname_to_idx:
                old_idx = orig_fname_to_idx[fname]
                data = zin.read(str(old_idx))
                # Write with the NEW index
                zout.writestr(new_idx_str, data)
                print(f"  Copied {fname} (idx {old_idx} -> {new_idx_str})")

file_size = os.path.getsize(apkg_path)
print(f"\n✅ apkg written: {apkg_path} ({file_size / 1024:.1f} KB)")

# ── Cleanup ──
shutil.rmtree(build_dir)
os.unlink(tmp_orig.name)
