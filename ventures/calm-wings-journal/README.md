# Calm Wings: 90-day anxiety journal

A printable, butterfly-themed anxiety journal. First made as a personal gift for Sekora;
built so it can become a product Tim sells.

## Files
- `Calm_Wings_Sekora.pdf`: personal edition (cover says "A 90-Day Journal for Sekora", welcome says "Dear Sekora,")
- `Calm_Wings_90_Day_Anxiety_Journal.pdf`: generic edition (no name, "This journal belongs to" line on the cover)
- `build_journal.py`: page layouts + CONFIG / PALETTE / fonts at the top
- `content.py`: every piece of wording (edit text here, not in the layout code)
- `designs.py`: full-page coloring designs (mandala, geometric, 13 weekly rewards, mood butterfly cells)
- `butterfly_art.py`: vector butterfly engine (symmetric wings, bands, veins, spots, eyespots)

## Rebuild
```
pip install reportlab
python3 build_journal.py                                  # both editions
python3 build_journal.py --edition personal --name Maya   # a personal copy for anyone
python3 build_journal.py --edition generic
python3 build_journal.py --out /some/folder
```
168 pages, US Letter portrait, about 7 MB each. Margins 0.6" plus 0.25" on the binding edge
(alternates for double-sided printing; set `"duplex": False` in CONFIG for single-sided).

## Layout
Cover, Start Here (6), SOS Toolkit (10), Days 1-90 with a 3-page weekly check-in after every
7 days (review, "I handled it" log, reward coloring page) and 3 monthly pages after days 30,
60 and 90 (mood butterfly, habit tracker, kind letter), Building Confidence (8), Look Back (4),
back page.

## Print notes
- Print double-sided, then spiral-bind on the left edge. Colored pencils work best; markers may bleed on thin paper.
- Light ink: line art plus small pastel accents, no full-color backgrounds.

## Product notes
- Rebrand: change `CONFIG` (title, subtitles, file names) and `PALETTE` at the top of `build_journal.py`.
- Fonts: uses system Liberation Sans + FreeSerif Italic (both embeddable). To use Quicksand / Nunito / Caveat,
  drop their static TTFs in `fonts/` (e.g. `fonts/Quicksand-Regular.ttf`, `fonts/Caveat-Regular.ttf`); the script picks them up.
- PMR page has a placeholder box "QR code: guided audio (add link)". Record or license audio first, then add a real QR.
- Before selling: re-check the US resource numbers in `content.py` (988, 741741, NAMI, SAMHSA), get a quick review
  from a licensed therapist, and keep the "supports, not replaces, care from a professional" note.
- Possible listings: Etsy digital download, Shopify digital product, or Amazon KDP (KDP needs bleed/trim settings changed).
- Future idea: fillable PDF version for tablets (GoodNotes / Notability), with tappable rating circles and checkboxes.
