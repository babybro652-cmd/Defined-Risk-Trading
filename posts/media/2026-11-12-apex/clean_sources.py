"""Privacy/branding clean of Tim's 11/12 Apex screenshots.
chart.jpg: crop to the fills area (drops status bar, indicator tables incl. "Bias Short" and the
filter table, time axis, order ticket, nav), inpaint indicator labels (Entry/SL/A BUY/markers),
then redraw Tim's own fill labels.
orders.jpg: drop status bar and nav bar, cover account number, Update Time and Order ID values.
"""
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = sys.argv[1] if len(sys.argv) > 1 else "."
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---------- chart ----------
img = cv2.imread(f"{D}/src/chart.jpg")
src = img.copy()
OY = 495  # boxes below are in crop coords (crop starts at y=495)
RED = src[OY + 100, 40].copy()  # body of the red candle at the left edge

def rowfill(x0, y0, x1, y1, side):
    """Fill each row of the box with the pixel just outside it (left or right)."""
    for y in range(y0 + OY, y1 + OY):
        c = src[y, x0 - 3] if side == "L" else src[y, x1 + 3]
        img[y, x0:x1] = c

rowfill(62, 8, 446, 62, "R")
rowfill(130, 62, 446, 68, "R")      # fill labels row + grey indicator label
img[8 + OY:70 + OY, 28:62] = RED  # part of that row sitting on the red candle
rowfill(533, 116, 750, 180, "L")  # "Entry ..." indicator label
img[205 + OY:255 + OY, 166:288] = src[300 + OY, 175]  # "SL ..." label (zone colour)
rowfill(578, 309, 720, 349, "R")  # "SL ..." indicator label
rowfill(578, 341, 738, 380, "R")  # fill label 2 @ 7658.00 (redrawn)
img[341 + OY:380 + OY, 545:578] = RED
rowfill(250, 436, 406, 549, "R")
rowfill(130, 470, 250, 549, "L")  # "A BUY" label + fill label 4 @ 7662.50 (redrawn)
rowfill(418, 60, 448, 90, "L")    # indicator triangle
rowfill(316, 344, 346, 376, "L")  # indicator triangle
rowfill(648, 897, 840, 938, "L")  # fill label 4 @ 7651.75 (redrawn)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
im = Image.fromarray(img)
d = ImageDraw.Draw(im)
f = ImageFont.truetype(B, 27)
for txt, xy in [("2 @ 7,664.50", (32, 516)), ("2 @ 7,663.75", (238, 516)),
                ("2 @ 7,658.00", (548, 840)), ("4 @ 7,662.50", (136, 966)),
                ("4 @ 7,651.75", (650, 1398))]:
    d.text(xy, txt, font=f, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
im = im.crop((0, 495, 1080, 1540))
ImageDraw.Draw(im).rectangle([912, 0, 1080, 20], fill=im.getpixel((1000, 120)))
im.save(f"{D}/chart_clean.png")

# ---------- order log ----------
o = Image.open(f"{D}/src/orders.jpg").convert("RGB")
a = np.asarray(o).astype(int)
# separators: thin grey rule spanning x 60..1020
seps = []
for y in range(900, a.shape[0]):
    row = a[y, 60:1020]
    if row.mean() > 45 and row.mean() < 90 and row.std() < 6:
        if not seps or y - seps[-1] > 20:
            seps.append(y)
# last block ends at the nav bar border (mean ~31), not a grey rule
for y in range(seps[-1] + 300, a.shape[0]):
    if 25 < a[y, 60:1020].mean() < 40 and a[y, 60:1020].std() < 3:
        seps.append(y)
        break
d = ImageDraw.Draw(o)
d.rectangle([60, 262, 452, 338], fill=(0, 0, 0))  # account number
covered = 0
for s in seps:
    for off in (161, 103):  # Update Time, Order ID rows above each separator
        cy = s - off
        d.rectangle([405, cy - 26, 1060, cy + 26], fill=(0, 0, 0))
        covered += 1
o = o.crop((0, 100, 1080, seps[-1]))
o.save(f"{D}/orders_clean.png")
print("separators", seps, "rows covered", covered, "orders size", o.size)
