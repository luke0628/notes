import json

# Count ETYM_ROOTS entries from process_gre.py
from process_gre import ETYM_ROOTS
print(f'ETYM_ROOTS entries: {len(ETYM_ROOTS)}')

# How many unique words in raw data
with open('/home/Lu/gre_batch_10_raw.json') as f:
    raw = f.read()
if raw[0].isdigit() and '|' in raw[:5]:
    raw = raw.split('|', 1)[1]
data = json.loads(raw)
names = [w['name'] for w in data]
print(f'Total words: {len(names)}')

covered = sum(1 for n in names if n.lower() in ETYM_ROOTS)
print(f'Words with ETYM_ROOTS entry: {covered}')
print(f'Words without ETYM_ROOTS entry: {len(names) - covered}')

# Show uncovered
uncovered = [n for n in names if n.lower() not in ETYM_ROOTS]
print(f'\nFirst 20 uncovered:')
for n in uncovered[:20]:
    print(f'  {n}')
