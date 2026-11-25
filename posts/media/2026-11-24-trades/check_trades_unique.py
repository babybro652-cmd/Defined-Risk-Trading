#!/usr/bin/env python3
"""5-gram check: new 11/24-11/25 trade captions vs each other and vs all 11/20-11/25 captions/post files.
Run from repo root. YouTube disclaimer line stripped first."""
import json, glob, itertools, sys
sys.path.insert(0, ".claude/skills/drt-content-engine/scripts")
from check_unique import words, ngrams
D = "Education only. Not financial advice."
NEWF = ["posts/media/2026-11-24-trades/captions.json", "posts/media/2026-11-25-trades/captions.json"]
new = {}
for f in NEWF:
    for k, c in json.load(open(f)).items():
        for p, t in c.items():
            new[f"{k}.{p}"] = t.replace(D, "")
prior = {}
def walk(x, pre):
    if isinstance(x, dict):
        for k, v in x.items(): walk(v, pre + "." + k)
    elif isinstance(x, list):
        for i, v in enumerate(x): walk(v, pre + f"[{i}]")
    elif isinstance(x, str) and len(x) > 30:
        prior[pre] = x.replace(D, "")
for f in glob.glob("posts/media/2026-11-2[0-5]-*/*.json"):
    if f not in NEWF: walk(json.load(open(f)), f)
for f in sorted(glob.glob("posts/2026-11-2[0-5]-*.md")):
    if "-trades.md" not in f: prior[f] = open(f).read().replace(D, "")
ng = {k: ngrams(words(v), 5) for k, v in new.items()}
hits = 0
for a, b in itertools.combinations(new, 2):
    s = ng[a] & ng[b]
    if s: hits += 1; print("NEW-NEW", a, b, [" ".join(x) for x in s][:3])
for a in new:
    for b, t in prior.items():
        s = ng[a] & ngrams(words(t), 5)
        if s: hits += 1; print("PRIOR", a, b, [" ".join(x) for x in s][:3])
print(f"{len(new)} new captions vs {len(prior)} prior sources: {hits} overlaps")
sys.exit(1 if hits else 0)
