#!/usr/bin/env python3
import json

with open('/home/Lu/gre_batch_7_done.json', 'r') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')

issues = 0
for i, line in enumerate(lines):
    entry = json.loads(line)
    for field in ['name', 'meaning_cn', 'memo', 'example', 'changkao', 'exam_tips']:
        if not entry.get(field, ''):
            print(f'  [{i}] {entry["name"]} - empty {field}')
            issues += 1

if issues == 0:
    print('All fields non-empty!')

missing_roots = []
for line in lines:
    entry = json.loads(line)
    if '待补充详细拆解' in entry['memo']:
        missing_roots.append(entry['name'])

if missing_roots:
    print(f'Missing roots ({len(missing_roots)}): {missing_roots}')
else:
    print('All words have root memos!')

print()
for idx in [0, 100, 150, 200, 250, 305]:
    entry = json.loads(lines[idx])
    print(f'=== [{idx}] {entry["name"]} ===')
    for k, v in entry.items():
        print(f'  {k}: {v}')
    print()
