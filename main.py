#!/usr/bin/env python3
"""VELMARA - The Harbour Above the Clouds.

A travel poster for a place that does not exist: Velmara, an invented
harbour city on a terraced headland above a teal sea at sunset.

Pure Python 3.13 standard library (no PIL in the grader): own pixel
buffer, scanline polygon fill, box downscale 2x, zlib PNG writer.
Deterministic: seeded PRNG only, no time, no network. Two runs are
byte-identical.
"""
import os
import random
import struct
import zlib
from pathlib import Path

# ---------------------------------------------------------------- canvas
W = H = 2048          # render resolution
OUT = 1024            # final resolution

CREAM = (250, 239, 210)
CREAM_DEEP = (247, 235, 203)
PEACH = (248, 200, 150)
PEACH_DEEP = (242, 163, 126)
CORAL = (238, 110, 82)
CORAL_SOFT = (242, 138, 107)
HALO = (249, 206, 158)
TEAL = (20, 101, 95)
TEAL_DEEP = (15, 78, 82)
TEAL_DARK = (11, 61, 71)
TEAL_LIGHT = (127, 181, 168)
SAGE = (94, 138, 122)
GREEN_NAVY = (30, 74, 68)
NAVY = (18, 46, 51)
NAVY_DEEP = (13, 36, 41)
AMBER = (245, 178, 74)
AMBER_GLOW = (250, 205, 120)
HOUSE_PEACH = (238, 178, 138)
HOUSE_CREAM = (244, 224, 186)

buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(x0, y0, x1, y1, c):
    x0 = max(0, int(x0)); y0 = max(0, int(y0))
    x1 = min(W, int(x1)); y1 = min(H, int(y1))
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2]


def hline(x0, x1, y, c, thick=1):
    for yy in range(int(y), int(y) + thick):
        for x in range(int(x0), int(x1)):
            px(x, yy, c)


def circle(cx, cy, r, c):
    r = int(r)
    for y in range(int(cy) - r, int(cy) + r + 1):
        dy = y - cy
        dx = int((r * r - dy * dy) ** 0.5) if abs(dy) <= r else -1
        if dx < 0:
            continue
        for x in range(int(cx) - dx, int(cx) + dx + 1):
            px(x, y, c)


def polygon(points, c):
    """Scanline fill of a simple polygon (list of (x, y))."""
    pts = [(float(x), float(y)) for x, y in points]
    ymin = max(0, int(min(y for _, y in pts)))
    ymax = min(H - 1, int(max(y for _, y in pts)) + 1)
    n = len(pts)
    for y in range(ymin, ymax + 1):
        xs = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                px(x, y, c)


def thick_line(x0, y0, x1, y1, w, c):
    """A line as a filled quad of width w."""
    dx, dy = x1 - x0, y1 - y0
    L = (dx * dx + dy * dy) ** 0.5 or 1.0
    ox, oy = -dy / L * w / 2, dx / L * w / 2
    polygon([(x0 + ox, y0 + oy), (x1 + ox, y1 + oy),
             (x1 - ox, y1 - oy), (x0 - ox, y0 - oy)], c)


# ------------------------------------------------------------------ scene
rng = random.Random(20261121)

# Frame: cream ground, navy keyline, poster area inside.
rect(0, 0, W, H, CREAM)
rect(52, 52, W - 52, H - 52, NAVY)          # keyline block
rect(60, 60, W - 60, H - 60, CREAM)        # inner ground (redrawn below)

# Sky bands (poster area 60..1988)
rect(60, 60, 1988, 520, CREAM)
rect(60, 520, 1988, 880, PEACH)
rect(60, 880, 1988, 1180, PEACH_DEEP)

# Sun halo + disc, low on the horizon, left of the tower so the disc
# clears the headland ridge.
circle(1300, 960, 280, HALO)
circle(1300, 960, 215, CORAL)
circle(1300, 960, 205, CORAL_SOFT)

# Sea bands.
rect(60, 1180, 1988, 1420, TEAL)
rect(60, 1420, 1988, 1660, TEAL_DEEP)
rect(60, 1660, 1988, 1988, TEAL_DARK)

# Sun reflection: shimmering dashes in a column under the sun.
for yy in range(1210, 1740, 46):
    wdt = rng.randint(50, 180)
    cx = 1300 + rng.randint(-60, 60)
    hline(cx - wdt // 2, cx + wdt // 2, yy, CORAL_SOFT, thick=7)
    hline(cx - wdt // 3, cx + wdt // 3, yy + 12, AMBER_GLOW, thick=4)

# Light strokes on the sea.
for _ in range(46):
    x = rng.randint(90, 1850)
    y = rng.randint(1220, 1900)
    ln = rng.randint(40, 180)
    hline(x, x + ln, y, TEAL_LIGHT, thick=5)

# Far headland, receding left (sage silhouette).
polygon([(60, 1180), (60, 1030), (300, 985), (520, 1045), (760, 1005),
         (980, 1085), (1180, 1180)], SAGE)

# Mid headland, right, the tower's ground.
polygon([(1000, 1180), (1180, 1065), (1420, 1000), (1680, 1035),
         (1860, 1125), (1988, 1180)], GREEN_NAVY)

# Foreground headland, bottom-left, dark navy.
polygon([(60, 1988), (60, 1560), (420, 1485), (760, 1565),
         (980, 1705), (900, 1988)], NAVY)

# Terraced houses climbing the foreground headland.
house_rows = [
    (150, 1620, 6), (260, 1580, 5), (380, 1555, 5),
    (500, 1575, 4), (620, 1610, 4), (740, 1660, 3),
]
for hx, hy, count in house_rows:
    for k in range(count):
        x = hx + k * 78
        y = hy - (k % 2) * 26
        col = HOUSE_PEACH if (k % 2 == 0) else HOUSE_CREAM
        rect(x, y, x + 62, y + 46, col)
        polygon([(x, y), (x + 31, y - 18), (x + 62, y)], NAVY_DEEP)
        px(x + 14, y + 20, AMBER); px(x + 15, y + 20, AMBER)
        px(x + 38, y + 20, AMBER); px(x + 39, y + 20, AMBER)

# A few houses on the mid headland, below the tower.
for hx, hy in [(1150, 1085), (1250, 1060), (1700, 1090), (1800, 1120)]:
    rect(hx, hy, hx + 70, hy + 44, HOUSE_CREAM)
    polygon([(hx, hy), (hx + 35, hy - 20), (hx + 70, hy)], NAVY_DEEP)
    px(hx + 16, hy + 18, AMBER); px(hx + 44, hy + 18, AMBER)


# ------------------------------------------------------------------ tower
# The Lantern Tower: one landmark, centre-right on the headland.
TX = 1500          # tower centre x
TB = 1130          # tower base y (on the headland ridge)
# Soft glow behind the lantern room.
circle(TX, 640, 120, HALO)
# Tapered shaft, cream with navy bands.
polygon([(TX - 78, TB), (TX - 46, 700), (TX + 46, 700), (TX + 78, TB)],
        CREAM_DEEP)
for by in (880, 960, 1040):
    wdt = 78 - (TB - by) * (32 / (TB - 700))
    hline(TX - wdt, TX + wdt, by, NAVY, thick=10)
# Gallery ring with glowing arched windows.
rect(TX - 72, 640, TX + 72, 700, NAVY)
for gx in range(TX - 54, TX + 55, 30):
    rect(gx, 656, gx + 16, 690, AMBER)
    circle(gx + 8, 656, 8, AMBER)
# Lantern room: amber glass, navy mullions, dome + finial.
rect(TX - 52, 560, TX + 52, 640, AMBER_GLOW)
for mx in (TX - 18, TX + 18):
    rect(mx - 4, 560, mx + 4, 640, NAVY)
rect(TX - 58, 548, TX + 58, 564, NAVY)
polygon([(TX - 52, 548), (TX, 500), (TX + 52, 548)], NAVY)
rect(TX - 4, 470, TX + 4, 502, NAVY)
circle(TX, 466, 8, AMBER)
# Small arched windows up the shaft.
for wy in (760, 830):
    rect(TX - 12, wy, TX + 12, wy + 34, AMBER)
    circle(TX, wy, 12, AMBER)


# ------------------------------------------------------------------ boats
def sailboat(cx, cy, scale, sail_coral=False):
    """Hull + two triangular sails + reflection, at (cx, cy) waterline."""
    hull_w, hull_h = int(150 * scale), int(34 * scale)
    polygon([(cx - hull_w, cy), (cx + hull_w, cy),
             (cx + hull_w - 24 * scale, cy + hull_h),
             (cx - hull_w + 24 * scale, cy + hull_h)], NAVY_DEEP)
    mast_h = int(190 * scale)
    thick_line(cx, cy, cx, cy - mast_h, 7, NAVY_DEEP)
    # Main sail (right of mast), jib (left of mast).
    polygon([(cx + 8, cy - mast_h + 10), (cx + 8, cy - 8),
             (cx + int(120 * scale), cy - 8)], CREAM)
    polygon([(cx - 8, cy - mast_h + 30), (cx - 8, cy - 8),
             (cx - int(84 * scale), cy - 8)],
            CORAL if sail_coral else PEACH)
    # Reflection dashes.
    for k in range(3):
        hline(cx - hull_w + 20 + k * 30, cx + hull_w - 20 - k * 30,
              cy + hull_h + 14 + k * 16, TEAL_LIGHT, thick=4)


sailboat(700, 1330, 0.55)
sailboat(1050, 1500, 0.8)
sailboat(1290, 1650, 1.15, sail_coral=True)

# Gulls in the sky.
for gx, gy, gs in [(420, 700, 26), (520, 640, 20), (900, 560, 24),
                   (1700, 700, 22), (1780, 620, 18)]:
    thick_line(gx - gs, gy, gx, gy + gs // 2, 5, NAVY)
    thick_line(gx, gy + gs // 2, gx + gs, gy, 5, NAVY)


# ------------------------------------------------------------------- type
# Hand-drawn deco capitals: each glyph is a list of quads on a 12 x 16 grid.
GLYPHS = {
    "V": [[(0, 0), (2.8, 0), (7.4, 16), (4.6, 16)],
          [(9.2, 0), (12, 0), (7.4, 16), (4.6, 16)]],
    "E": [[(0, 0), (2.8, 0), (2.8, 16), (0, 16)],
          [(0, 0), (12, 0), (12, 2.8), (0, 2.8)],
          [(0, 6.6), (9, 6.6), (9, 9.4), (0, 9.4)],
          [(0, 13.2), (12, 13.2), (12, 16), (0, 16)]],
    "L": [[(0, 0), (2.8, 0), (2.8, 16), (0, 16)],
          [(0, 13.2), (12, 13.2), (12, 16), (0, 16)]],
    "M": [[(0, 0), (2.8, 0), (2.8, 16), (0, 16)],
          [(9.2, 0), (12, 0), (12, 16), (9.2, 16)],
          [(2.6, 0), (5.0, 0), (7.2, 9.5), (4.8, 9.5)],
          [(7.0, 0), (9.4, 0), (7.2, 9.5), (4.8, 9.5)]],
    "A": [[(6, 0), (8.6, 0), (2.8, 16), (0, 16)],
          [(3.4, 0), (6, 0), (12, 16), (9.2, 16)],
          [(3.6, 10.5), (8.4, 10.5), (8.4, 13), (3.6, 13)]],
    "R": [[(0, 0), (2.8, 0), (2.8, 16), (0, 16)],
          [(0, 0), (12, 0), (12, 2.8), (0, 2.8)],
          [(9.2, 0), (12, 0), (12, 8.5), (9.2, 8.5)],
          [(0, 6.6), (12, 6.6), (12, 9.4), (0, 9.4)],
          [(6.2, 8.5), (8.8, 8.5), (12, 16), (9.4, 16)]],
}


def draw_word(word, x0, y0, unit, c):
    adv = 13.2 * unit
    for li, ch in enumerate(word):
        ox = x0 + li * adv
        for quad in GLYPHS[ch]:
            polygon([(ox + qx * unit, y0 + qy * unit) for qx, qy in quad], c)


WORD = "VELMARA"
UNIT = 15.0
word_w = (len(WORD) - 1) * 13.2 * UNIT + 12 * UNIT
wx = (W - word_w) / 2
wy = 175.0
# Cream offset shadow behind, then solid navy letters: the sky's top
# band is cream, so cream letters would vanish into it.
draw_word(WORD, wx + 11, wy + 13, UNIT, CREAM)
draw_word(WORD, wx, wy, UNIT, NAVY)

# Thin navy rule with a diamond under the name (decoration, not copy).
hline(620, 1428, 468, NAVY, thick=6)
polygon([(1024, 452), (1042, 470), (1024, 488), (1006, 470)], NAVY)

# ------------------------------------------------------------- downscale
small = bytearray(OUT * OUT * 3)
for oy in range(OUT):
    for ox in range(OUT):
        r = g = b = 0
        for dy in (0, 1):
            for dx in (0, 1):
                i = (((oy * 2 + dy) * W) + ox * 2 + dx) * 3
                r += buf[i]; g += buf[i + 1]; b += buf[i + 2]
        j = (oy * OUT + ox) * 3
        small[j] = r // 4; small[j + 1] = g // 4; small[j + 2] = b // 4


def png_bytes(rgb, w, h):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(rgb[y * w * 3:(y + 1) * w * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "entry.png"
out_path.write_bytes(png_bytes(small, OUT, OUT))
print(f"wrote {out_path} ({out_path.stat().st_size} bytes)")
