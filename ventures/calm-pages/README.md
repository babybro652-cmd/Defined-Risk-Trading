# Peace by Page: 90-day anxiety journals

One engine, three themed editions of the same 90-day anxiety journal. **Peace by Page** is the
umbrella brand (chosen 10/2, was the working name Calm Pages Co.; `BRAND` in `themes.py`). Each edition is a
series title. The folder keeps the name `calm-pages` because Drive links and docs point to it.

| Edition | Theme | Folder |
|---|---|---|
| Calm Wings | butterflies (the original; gift for Sekora) | `editions/calm-wings/` |
| Calm Petals | botanical: sage, eucalyptus, blush; pressed-flower line art | `editions/calm-petals/` |
| Calm Nights | moon and stars, for anxious nights; lavender, gold, navy used sparingly | `editions/calm-nights/` |

Each edition folder has `files/<n-product>/` (upload these), `images/<n-product>/` (5 listing images,
2000x2000) and `listings.md` (copy, tags, prices, AI disclosure). Products per edition, all in Letter + A4,
each with a How to Print PDF: 1 journal, 2 bundle (zip), 3 coloring pack (18 designs), 4 SOS calm-down kit,
5 mood tracker (12 undated months).

Calm Wings also keeps its Etsy-era `shop-setup.md`, the personal Sekora PDF and the older 10/2 generic PDF.
Its files and listing text still mention Etsy; they were left unchanged on purpose. The new editions use
platform-neutral wording (store is moving to Payhip).

## Build
```
pip install reportlab pymupdf pillow
python3 build_products.py --theme petals      # all 5 products + images -> editions/calm-petals/ (~50 s)
python3 build_products.py --theme nights
python3 build_products.py --theme wings       # rebuilds Calm Wings byte-for-byte (with RL_invariant=1)
python3 build_products.py --all
python3 build_journal.py --theme wings --edition personal --name Sekora   # a personal copy
```
All three retail editions carry the Peace by Page mark (Calm Wings since 10/2). Personal copies never show it.
Sekora's copy (`editions/calm-wings/Calm_Wings_Sekora.pdf`) is frozen: don't rebuild or replace it.

## Code
- `build_journal.py`: page layouts (shared), CONFIG for geometry, fonts, `set_theme()`
- `build_products.py`: the 5 products, packs, How to Print page, bundle zips
- `mockups.py`: listing images rendered from the built PDFs
- `content.py`: all shared wording; themes override pieces (welcome, "how anxiety works" part 4, lines of the day...)
- `themes.py`: `Theme` class, `BRAND`, registry. One module per edition:
  - `theme_wings.py` + `butterfly_art.py` + `designs.py`
  - `theme_petals.py` + `botanical_art.py` + `botanical_designs.py`
  - `theme_nights.py` + `celestial_art.py`
- A theme sets: title, subtitle, file prefix, palette (+ listing-image colors), accent art, cover art, life-cycle strip,
  long-exhale trace shape, SOS / weekly / pack coloring pages, mood tracker cells, rating icon, flavor text,
  extra pages (Calm Nights adds a "mind won't switch off" SOS page and a night brain dump), listing-image wording.

## Layout (journal)
Cover, Before you begin, Start Here (6), SOS Toolkit (10; Nights 11), Days 1-90 with a 3-page weekly check-in
after every 7 days and 3 monthly pages after days 30, 60, 90, Building Confidence (8; Nights 9), Look Back (4),
back page. Wings and Petals 169 pages, Nights 171.

## Rules for the product
- Keep the "supports, not replaces, professional care" note and crisis resources (988). No medical claims.
- Light ink: line art plus small pastel accents, no full-color backgrounds.
- No em dashes or filler words in anything published.
- Fonts: Liberation Sans + FreeSerif Italic. Drop Quicksand / Caveat TTFs in `fonts/` to switch.
- Before selling: re-check the US resource numbers in `content.py`, and get a quick review from a licensed therapist.
- Future: fillable tablet version.

Market research (10/2): `MARKET_RESEARCH.md`.
