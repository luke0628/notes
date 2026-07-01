import json
with open("/home/Lu/gre_1000_words.json", "r") as f:
    data = json.load(f)

for i in range(99, 150):
    w = data[i]
    m_count = len(w["meanings"])
    word = w["word"]
    phon = w["phonetic"]
    print(f"{i+1}. {word:20s} ({m_count} defs) phon={phon!r}")
    for m in w["meanings"]:
        meaning = m["meaning"][:70]
        pos = m["pos"]
        print(f"   [{pos}] {meaning}")
    print()
