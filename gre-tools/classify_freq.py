#!/usr/bin/env python3
"""Classify GRE words into high/medium/low frequency based on multiple signals"""

import json, math

# Load all processed words
with open('/home/Lu/gre_all_done.json') as f:
    words = [json.loads(line) for line in f if line.strip()]

# Load raw data for frequency signals
with open('/home/Lu/gre_full_raw.json') as f:
    raw_list = json.load(f)
raw_map = {}
for r in raw_list:
    raw_map[r['name'].lower()] = r

def calc_freq_score(w):
    """Calculate a frequency score (higher = more frequent in GRE)"""
    raw = raw_map.get(w['name'].lower(), {})
    score = 0
    
    # Signal 1: Number of POS/meanings (more meanings = more tested)
    meanings_count = 0
    for i in range(1, 5):
        if raw.get(f'pos{i}', '') and raw.get(f'meaning{i}', ''):
            meanings_count += 1
    score += meanings_count * 5
    
    # Signal 2: Number of synonyms listed
    syn_count = len(raw.get('syn1', '').split(',')) if raw.get('syn1', '') else 0
    score += min(syn_count, 15)
    
    # Signal 3: Has antonym (controversy words are tested more)
    if raw.get('ant1', ''):
        score += 5
    
    # Signal 4: Word length (shorter words tend to be more common)
    word_len = len(w['name'])
    if word_len <= 5:
        score += 10
    elif word_len <= 8:
        score += 5
    elif word_len >= 12:
        score -= 3
    
    # Signal 5: Number of examples (more examples = more common)
    eg_count = 0
    for i in range(1, 5):
        if raw.get(f'eg{i}', ''):
            eg_count += 1
    score += eg_count * 3
    
    # Signal 6: Whether memo exists in original data
    if raw.get('memo', ''):
        score += 3
    
    # Signal 7: Known GRE high-frequency prefixes/topics
    high_freq_topics = ['ac', 'ad', 'al', 'an', 'ap', 'ar', 'as', 'at',
                        'be', 'co', 'com', 'con', 'col', 'cor',
                        'de', 'dis', 'ex', 'im', 'in', 'ir',
                        'ob', 'op', 'per', 'pre', 'pro', 're', 'sub', 'trans', 'un']
    for prefix in high_freq_topics:
        if w['name'].lower().startswith(prefix):
            score += 2
            break
    
    return score

# Score all words
scored = []
for w in words:
    score = calc_freq_score(w)
    scored.append((score, w))

# Sort by score descending
scored.sort(key=lambda x: -x[0])

# Split into 3 groups: high (~1000), medium (~1000), low (~1059)
total = len(scored)
high_cut = total // 3
med_cut = 2 * total // 3

high = [w for _, w in scored[:high_cut]]
med = [w for _, w in scored[high_cut:med_cut]]
low = [w for _, w in scored[med_cut:]]

print(f"High frequency: {len(high)} words (score {scored[0][0]} ~ {scored[high_cut-1][0]})")
print(f"Medium frequency: {len(med)} words (score {scored[high_cut][0]} ~ {scored[med_cut-1][0]})")  
print(f"Low frequency: {len(low)} words (score {scored[med_cut][0]} ~ {scored[-1][0]})")

# Show top 10 and bottom 10 of high
print("\n=== High Frequency Top 10 ===")
for s, w in scored[:10]:
    print(f"  {w['name']:20s} score={s}")

print("\n=== High Frequency Bottom 5 ===")
for s, w in scored[high_cut-5:high_cut]:
    print(f"  {w['name']:20s} score={s}")

print("\n=== Low Frequency Top 5 ===")
for s, w in scored[med_cut:med_cut+5]:
    print(f"  {w['name']:20s} score={s}")

print("\n=== Low Frequency Bottom 5 ===")
for s, w in scored[-5:]:
    print(f"  {w['name']:20s} score={s}")

# Save classified files
with open('/home/Lu/gre_high_done.json', 'w') as f:
    for w in high:
        f.write(json.dumps(w, ensure_ascii=False) + '\n')
with open('/home/Lu/gre_med_done.json', 'w') as f:
    for w in med:
        f.write(json.dumps(w, ensure_ascii=False) + '\n')
with open('/home/Lu/gre_low_done.json', 'w') as f:
    for w in low:
        f.write(json.dumps(w, ensure_ascii=False) + '\n')

print(f"\n✅ High: {len(high)} -> /home/Lu/gre_high_done.json")
print(f"✅ Medium: {len(med)} -> /home/Lu/gre_med_done.json")
print(f"✅ Low: {len(low)} -> /home/Lu/gre_low_done.json")
