#!/usr/bin/env python3
"""5-gram check: 11/27 recap captions vs each other and all 11/20-11/27 captions/post files. Run from repo root."""
import json, glob, itertools, sys
sys.path.insert(0, ".claude/skills/drt-content-engine/scripts")
from check_unique import words, ngrams
D = "Education only. Not financial advice."
NEWF = "posts/media/2026-11-27-recap/captions.json"
new = {k: v.replace(D, "") for k, v in json.load(open(NEWF)).items()}
prior = {}
def walk(x, pre):
    if isinstance(x, dict):
        for k, v in x.items(): walk(v, pre + "." + k)
    elif isinstance(x, list):
        for i, v in enumerate(x): walk(v, pre + f"[{i}]")
    elif isinstance(x, str) and len(x) > 30: prior[pre] = x.replace(D, "")
for f in glob.glob("posts/media/2026-11-2[0-7]-*/*.json"):
    if f != NEWF: walk(json.load(open(f)), f)
for f in sorted(glob.glob("posts/2026-11-2[0-7]-*.md")):
    if "weekly-recap" not in f: prior[f] = open(f).read().replace(D, "")
ng = {k: ngrams(words(v), 5) for k, v in new.items()}; hits = 0
for a, b in itertools.combinations(new, 2):
    s = ng[a] & ng[b]
    if s: hits += 1; print("NEW-NEW", a, b, [" ".join(x) for x in s][:3])
for a in new:
    for b, t in prior.items():
        s = ng[a] & ngrams(words(t), 5)
        if s: hits += 1; print("PRIOR", a, b, [" ".join(x) for x in s][:3])
for k, v in new.items(): print(k, "chars before hashtags:", len(v.split("\n\n#")[0]))
print(f"{len(prior)} prior sources:", "OK" if not hits else "FAIL")
sys.exit(1 if hits else 0)
