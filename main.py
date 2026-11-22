#!/usr/bin/env python3
"""The World in One Page - 22 November 2026.

Renders a cream broadsheet front page that sums up the world news of
Sunday 22 November 2026 and writes it to /output/entry.png.

Pure Python standard library: the picture is drawn pixel by pixel into
an RGB framebuffer with a small bitmap typeface defined below, then
encoded as a PNG with zlib. No network, no files read, deterministic.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 241, 227)
PANEL = (240, 232, 211)
INK = (24, 24, 38)
RED = (176, 32, 44)
GREY = (96, 90, 80)
FAINT = (214, 205, 182)

# ---------------------------------------------------------------------------
# A 5x7 bitmap typeface. Each glyph is seven rows of five pixels.
# ---------------------------------------------------------------------------

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#..##", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "*": (".....", "#.#.#", ".###.", "#.#.#", ".....", ".....", "....."),
}


def text_width(s, scale):
    """Pixel width of a string at a scale (6 units advance per glyph)."""
    if not s:
        return 0
    return (len(s) * 6 - 1) * scale


class Canvas:
    def __init__(self, w, h, colour):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(colour) * (w * h))

    def rect(self, x, y, rw, rh, colour):
        if rw <= 0 or rh <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + rw)
        y1 = min(self.h, y + rh)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.buf[off:off + len(row)] = row

    def frame(self, x, y, rw, rh, colour, thick=2):
        self.rect(x, y, rw, thick, colour)
        self.rect(x, y + rh - thick, rw, thick, colour)
        self.rect(x, y, thick, rh, colour)
        self.rect(x + rw - thick, y, thick, rh, colour)

    def text(self, x, y, s, scale, colour):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for r, row in enumerate(glyph):
                for c, bit in enumerate(row):
                    if bit == "#":
                        self.rect(cx + c * scale, y + r * scale, scale, scale, colour)
            cx += 6 * scale
        return cx

    def text_c(self, cx, y, s, scale, colour):
        return self.text(cx - text_width(s, scale) // 2, y, s, scale, colour)

    def wrap(self, s, scale, max_w):
        words = s.split()
        lines = []
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, colour, max_w, leading):
        for line in self.wrap(s, scale, max_w):
            self.text(x, y, line, scale, colour)
            y += leading
        return y


def save_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# The front page
# ---------------------------------------------------------------------------

MX = 36                      # side margin
CW = W - 2 * MX              # column width


def masthead(cv):
    y = 28
    cv.rect(MX, y, CW, 5, INK)
    y += 14
    cv.text_c(W // 2, y, "THE WORLD IN ONE PAGE", 4, INK)
    y += 36
    cv.rect(MX, y, CW, 2, INK)
    y += 10
    cv.text_c(W // 2, y, "22 NOVEMBER 2026", 9, INK)
    y += 71
    cv.text_c(W // 2, y, "S U N D A Y", 4, RED)
    y += 36
    cv.rect(MX, y, CW, 5, INK)
    return y + 14


def lead_story(cv, y):
    cv.text(MX, y, "UKRAINE WAR - NATO", 3, RED)
    y += 29
    cv.text(MX, y, "RUSSIAN MISSILES", 6, INK)
    y += 50
    cv.text(MX, y, "LAND IN POLAND", 6, INK)
    y += 56
    body = ("MOSCOW'S BIGGEST STRIKE OF NOVEMBER - 500+ MISSILES AND "
            "DRONES, THREE DOWN INSIDE POLAND. NATO VOWED TO DEFEND "
            "'EVERY INCH' OF POLISH SOIL.")
    y = cv.para(MX, y, body, 3, INK, CW, 27)
    return y + 4


def wide_box(cv, y):
    h = 130
    cv.rect(MX, y, CW, h, PANEL)
    cv.frame(MX, y, CW, h, INK, 2)
    x = MX + 18
    yy = y + 12
    cv.text(x, yy, "CLIMATE - ANTALYA, TURKEY", 3, RED)
    yy += 29
    cv.text(x, yy, "COP31 CLIMATE TALKS RUN INTO OVERTIME", 4, INK)
    yy += 36
    body = ("THE UN SUMMIT ENTERED A SECOND DAY OF OVERTIME AS COUNTRIES "
            "SPLIT OVER FOSSIL FUELS AND FINANCE.")
    cv.para(x, yy, body, 3, INK, CW - 36, 27)
    return y + h + 10


def story_box(cv, x, y, bw, bh, kicker, head, body):
    cv.frame(x, y, bw, bh, INK, 2)
    xx = x + 14
    yy = y + 9
    cv.text(xx, yy, kicker, 2, RED)
    yy += 17
    for line in cv.wrap(head, 3, bw - 28):
        cv.text(xx, yy, line, 3, INK)
        yy += 23
    yy += 1
    cv.para(xx, yy, body, 2, INK, bw - 28, 16)


def story_grid(cv, y):
    bw = (CW - 14) // 2
    bh = 104
    boxes = [
        ("MIDDLE EAST - HORMUZ", "TANKERS HIT IN HORMUZ; IRAN STRIKES BAHRAIN",
         "TEHRAN SAYS THE STRAIT MAY REOPEN ON FAIR TERMS. "
         "HOUTHIS FIRE AT RIYADH."),
        ("MEXICO - SINALOA", "CARTEL BOSS 'EL CHAPO ISIDRO' CAPTURED",
         "FAUSTO ISIDRO MEZA FLORES WAS ON THE FBI MOST "
         "WANTED LIST. 11 DIED."),
        ("MARKETS - NEW YORK", "AI SELL-OFF PUSHES STOCKS INTO CORRECTION",
         "CHIP AND AI SHARES TUMBLED; NVIDIA FACES A US "
         "ACCOUNTING PROBE REPORT."),
        ("WORLD COURT - THE HAGUE", "MYANMAR GUILTY OF ROHINGYA GENOCIDE",
         "THE TOP UN COURT FOUND MYANMAR RESPONSIBLE - "
         "A LANDMARK RULING."),
        ("NIGERIA - DISASTER", "BOAT CAPSIZES IN NIGERIA: 24 DEAD",
         "A BOAT CARRYING MOURNERS TO A FUNERAL CAPSIZED "
         "IN THE SOUTH."),
        ("GAZA - CONFLICT", "ISRAELI STRIKE HITS GAZA AID VEHICLE",
         "A STRIKE HIT A FOOD VEHICLE IN GAZA CITY, "
         "KILLING THREE."),
    ]
    for i, (kick, head, body) in enumerate(boxes):
        bx = MX + (i % 2) * (bw + 14)
        by = y + (i // 2) * (bh + 9)
        story_box(cv, bx, by, bw, bh, kick, head, body)
    rows = (len(boxes) + 1) // 2
    return y + rows * (bh + 9)


def numbers_strip(cv, y):
    cv.rect(MX, y, CW, 3, RED)
    y += 12
    cv.text_c(W // 2, y, "THE DAY IN NUMBERS", 2, INK)
    y += 24
    stats = [
        ("500+", "MISSILES AND DRONES"),
        ("24", "DEAD IN NIGERIA BOAT"),
        ("11", "KILLED IN SINALOA"),
        ("6.7", "EARTHQUAKE IN PERU"),
        ("$56K", "BITCOIN IN THE SELLOFF"),
    ]
    colw = CW // len(stats)
    for i, (num, cap) in enumerate(stats):
        cx = MX + i * colw + colw // 2
        cv.text_c(cx, y, num, 5, RED)
        lines = cv.wrap(cap, 2, colw - 12)
        ly = y + 44
        for line in lines:
            cv.text_c(cx, ly, line, 2, INK)
            ly += 17
    return y + 82


def footer(cv, y):
    cv.rect(MX, y, CW, 2, INK)
    y += 10
    cv.text_c(W // 2, y,
              "SUNDAY 22 NOVEMBER 2026 - THE DAY'S NEWS IN ONE PAGE", 2, GREY)
    return y + 18


def main():
    cv = Canvas(W, H, PAPER)
    y = masthead(cv)
    y = lead_story(cv, y)
    y = wide_box(cv, y)
    y = story_grid(cv, y)
    y = numbers_strip(cv, y)
    print("page ends at y =", y)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    size = save_png(cv, os.path.join(outdir, "entry.png"))
    print("wrote entry.png:", size, "bytes")


if __name__ == "__main__":
    main()
