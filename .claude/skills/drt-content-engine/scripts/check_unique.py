#!/usr/bin/env python3
"""Fail if any two captions share a run of N+ consecutive words.

Usage: check_unique.py captions.json [--n 5]
captions.json: {"instagram": "...", "tiktok": "...", "facebook": "..."}
Links, hashtags, @mentions, and pure numbers/prices are ignored so that shared
trade figures (entry 7775.50, +$1,075) don't count as copied wording.
Exit code 0 = all unique, 1 = overlap found.
"""
import argparse
import itertools
import json
import re
import sys


def words(text):
    out = []
    text = re.sub(r"(https?://|www\.)\S+", " ", text)
    for tok in re.findall(r"[#@]?[\w$.,'%+-]+", text.lower()):
        if tok[0] in "#@":
            continue
        tok = tok.strip(".,'")
        if not tok or re.fullmatch(r"[$+\-]*[\d.,]+%?k?", tok):
            continue
        out.append(tok)
    return out


def ngrams(ws, n):
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--n", type=int, default=5)
    args = ap.parse_args()

    captions = json.load(open(args.path))
    grams = {k: ngrams(words(v), args.n) for k, v in captions.items()}
    failed = False
    for a, b in itertools.combinations(captions, 2):
        shared = grams[a] & grams[b]
        if shared:
            failed = True
            print(f"OVERLAP {a} <-> {b}:")
            for g in sorted(shared)[:5]:
                print("   ", " ".join(g))
    if not failed:
        print(f"OK: no {args.n}-word overlap across {', '.join(captions)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
