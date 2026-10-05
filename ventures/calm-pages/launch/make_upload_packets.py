#!/usr/bin/env python3
"""Build launch/upload-packets.md (one copy-paste block per Payhip product) from editions/*/listings.md.

    python3 launch/make_upload_packets.py

Reads price, files, product name and description from each edition's listings.md, swaps the old Etsy
wording in Calm Wings for Payhip wording, and checks that every file and image exists in the repo.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO_REL = "ventures/calm-pages"
RAW = "https://github.com/babybro652-cmd/Defined-Risk-Trading/raw/main/" + REPO_REL + "/"
STORE = "payhip.com/PeaceByPage"

EDITIONS = [("calm-wings", "Calm Wings"), ("calm-petals", "Calm Petals"), ("calm-nights", "Calm Nights")]
FOLDERS = ["1-journal", "2-bundle", "3-coloring-pack", "4-sos-kit", "5-mood-tracker"]
PRICES = ["$11.99", "$16.99", "$4.99", "$3.99", "$2.99"]

# Calm Wings names were Etsy keyword titles; these match the Petals / Nights pattern.
WINGS_NAMES = [
    "Calm Wings 90-Day Anxiety Journal: Printable Guided Journal with CBT-Inspired Prompts, Mood Tracker and Coloring Pages",
    "Calm Wings Bundle: 90-Day Anxiety Journal + Butterfly Coloring Pack + Mood Butterfly Tracker (Printable PDF)",
    "Calm Wings Butterfly Coloring Pack: 18 Printable Butterfly Coloring Pages for Adults (PDF)",
    "Calm Wings SOS Calm-Down Kit: Printable Coping Skills Worksheets (Breathing, Grounding, Worry Tree, Thought Record)",
    "Calm Wings Mood Butterfly Tracker: 12-Month Undated Mood Coloring Tracker, Year in Pixels (Printable PDF)",
]
ETSY_SWAPS = [
    ("After checkout, find your files under You > Purchases and reviews, or use the link in your Etsy email.",
     "Your download link appears right after checkout and is emailed to you."),
    ("After checkout, find your files under You > Purchases and reviews.",
     "Your download link appears right after checkout and is emailed to you."),
    ("Find your files under You > Purchases and reviews.",
     "Your download link appears right after checkout and is emailed to you."),
]
FIXES = [("A 11-page", "An 11-page")]
SHORT = ["90-Day Anxiety Journal", "Complete Bundle", "Coloring Pack", "SOS Calm-Down Kit", "Mood Tracker"]
IMAGE_ALT = [
    None,  # image 1: from listings.md
    "{ed} {prod} printable pages fanned out to show the inside",
    "Inside look at four pages of the {ed} {prod}",
    "What's included in the {ed} {prod}, with page counts",
    "{ed} {prod}: instant digital download in US Letter and A4, how it works",
]


def sections(md):
    parts = re.split(r"\n## (\d)\. ", md)
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}


def block_after(sec, heading):
    m = re.search(re.escape(heading) + r"[^\n]*\n```\n(.*?)\n```", sec, re.S)
    return m.group(1).strip() if m else None


def field(sec, name):
    m = re.search(r"\*\*" + re.escape(name) + r"[^*]*\*\*\s*(.+)", sec)
    return m.group(1).strip() if m else None


def check(rel):
    if not os.path.exists(os.path.join(ROOT, rel)):
        sys.exit(f"MISSING: {rel}")
    return rel


def file_order(names):
    """Letter first, then A4, then How to Print."""
    def key(n):
        return (0 if "Letter" in n else 1 if "A4" in n else 2, n)
    return sorted(names, key=key)


def human_size(rel):
    b = os.path.getsize(os.path.join(ROOT, rel))
    return f"{b / 1e6:.1f} MB" if b >= 1e5 else f"{b / 1e3:.0f} KB"


def packet(slug, ed, n, sec, out):
    folder = FOLDERS[n - 1]
    name = WINGS_NAMES[n - 1] if slug == "calm-wings" else block_after(sec, "**Product name:**")
    desc = block_after(sec, "**Description:**")
    for a, b in ETSY_SWAPS + FIXES:
        desc = desc.replace(a, b)
    if "Etsy" in desc or "Purchases and reviews" in desc:
        sys.exit(f"Etsy wording left in {slug} {n}")
    price = field(sec, "Price:").split(" ")[0]
    assert price == PRICES[n - 1], (slug, n, price)
    alt1 = field(sec, "Image 1 alt text:") or field(sec, "Photo 1 alt text:")
    files_dir = f"editions/{slug}/files/{folder}"
    files = file_order(os.listdir(os.path.join(ROOT, files_dir)))
    imgs_dir = f"editions/{slug}/images/{folder}"
    imgs = sorted(os.listdir(os.path.join(ROOT, imgs_dir)))
    assert len(imgs) == 5, imgs
    code = f"{ed.split()[1][0]}{n}"
    out.append(f"## {code}. {ed} {SHORT[n - 1]}  ({price})\n")
    out.append(f"**Collection:** {ed}  \n**Price:** {price}  \n**Type:** Digital product\n")
    out.append("**Product name:**\n```\n" + name + "\n```\n")
    out.append("**Files to upload (in this order):**\n")
    for i, f in enumerate(files, 1):
        rel = check(f"{files_dir}/{f}")
        out.append(f"{i}. `{f}` ({human_size(rel)})  \n   Repo: `{REPO_REL}/{rel}`  \n   Download: {RAW}{rel}")
    out.append("")
    out.append("**Images (in this order; image 1 is the main one):**\n")
    prod = SHORT[n - 1].lower().replace("90-day", "90-day").replace("sos", "SOS")
    for i, f in enumerate(imgs):
        rel = check(f"{imgs_dir}/{f}")
        alt = alt1 if i == 0 else IMAGE_ALT[i].format(ed=ed, prod=prod)
        out.append(f"{i + 1}. `{f}`  \n   Download: {RAW}{rel}  \n   Alt text: {alt}")
    out.append("")
    out.append("**Description:**\n```\n" + desc + "\n```\n")
    out.append("---\n")
    return files, imgs


def sampler(out):
    out.append("## FREE. Peace by Page 7-Day Sampler  ($0)\n")
    out.append("**Collection:** none (or a \"Free\" collection)  \n**Price:** $0 (Payhip: set the price to 0 so "
               "it is free; turn on \"let customers pay what they want\" only if you want tips)  \n"
               "**Type:** Digital product. Use it as the email-list freebie.\n")
    out.append("**Product name:**\n```\nFree 7-Day Anxiety Journal Sampler: Printable Daily Pages, SOS Card "
               "and Coloring Page (PDF)\n```\n")
    out.append("**Files to upload (in this order):**\n")
    for f in ("PeaceByPage_7Day_Sampler_Letter.pdf", "PeaceByPage_7Day_Sampler_A4.pdf"):
        rel = check(f"editions/sampler/{f}")
        out.append(f"1. `{f}` ({human_size(rel)})  \n   Repo: `{REPO_REL}/{rel}`  \n   Download: {RAW}{rel}"
                   .replace("1. ", "2. " if "A4" in f else "1. ", 1))
    out.append("")
    out.append("**Images:** use the Calm Wings journal images 01 and 02 for now, or a page from the sampler. "
               "Alt text: Free printable 7-day anxiety journal sampler with butterfly line art\n")
    out.append("**Description:**\n```\n" + """Try a week of the Peace by Page journal, free. Seven daily pages, about five minutes each, to support calm daily reflection with CBT-inspired prompts.

WHAT'S INCLUDED
- 14-page printable PDF in US Letter AND A4
- 7 undated daily pages: mood ratings, three good things, one worry and a more balanced thought, one small step
- A week 1 review page
- 1 butterfly coloring page as your reward
- A cut-out pocket SOS card: breathe, ground, move or color, write, plus crisis lines on the back

WHAT YOU GET
An instant download. No physical item is shipped. Print at "Actual size" on plain paper.

PLEASE NOTE
This sampler is a self-reflection tool for general wellbeing. It is not medical advice, diagnosis or treatment, and it supports, not replaces, care from a licensed professional. If you are in crisis in the US, call or text 988 or text HOME to 741741. In an emergency, call 911 or your local emergency number. Outside the US, find a helpline at findahelpline.com.

Free for personal use. Please share the store link instead of the file.

Content and art created with AI assistance and reviewed by the seller.""" + "\n```\n")


def main():
    out = []
    out.append("# Peace by Page: Payhip upload packets\n")
    out.append(f"Store: {STORE}  \nOne block per product: 15 paid products (3 editions x 5) plus the free sampler. "
               "Copy each field into Payhip's product form. \"Download\" links fetch the file from GitHub, so "
               "you can save it to your phone and upload it from there.\n")
    out.append("""### Settings for every product
- Product type: **Digital product** (file download)
- Collections: create **Calm Wings**, **Calm Petals** and **Calm Nights** first, then add each product to its edition
- Files: upload all files listed, Letter first. Every file is under 5.5 MB.
- Images: all 5, in the order shown. Image 1 is the thumbnail.
- Quantity / shipping: unlimited / none
- Refund policy and terms: paste from `launch/policies.md` into Settings (once, not per product)
- Tax: Payhip collects US sales tax itself (since July 1, 2026). Under Advanced options, set the product tax category to the closest match for a downloadable book or printable (see `launch/sales-tax-nc.md`)
- Optional launch sale on journals: $8.99 for 2 weeks (Payhip coupon)
- Words we never use: treats, cures, heals, therapy, relief (as a promise), clinically proven

Product codes: W = Calm Wings, P = Calm Petals, N = Calm Nights; 1 journal, 2 bundle, 3 coloring pack, 4 SOS kit, 5 mood tracker.

---
""")
    count = 0
    for slug, ed in EDITIONS:
        secs = sections(open(os.path.join(ROOT, "editions", slug, "listings.md")).read())
        for n in range(1, 6):
            packet(slug, ed, n, secs[n], out)
            count += 1
    sampler(out)
    text = "\n".join(out)
    for bad in ("—", "Etsy"):
        if bad in text:
            sys.exit(f"found {bad!r} in packets")
    path = os.path.join(HERE, "upload-packets.md")
    open(path, "w").write(text)
    print(f"{path}: {count} products + sampler, {len(text)} chars")


if __name__ == "__main__":
    main()
