#!/usr/bin/env python3
"""Sum up Wednesday 25 November 2026 in one image.

Draws a 1024x1024 broadsheet-style poster with a pure-stdlib PNG
encoder: fixed palette, fixed geometry, no randomness, no clock, no
network, so two runs write byte-identical files.
"""

import os
import struct
import zlib
from math import isqrt

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
NAVY = (16, 30, 46)
NAVY_DARK = (11, 21, 33)
INK = (20, 28, 38)
PAPER = (244, 237, 222)
PAPER2 = (233, 227, 209)
CRIMSON = (176, 30, 36)
CRIMSON_DK = (140, 22, 28)
GOLD = (212, 164, 60)
GOLD_LT = (232, 196, 110)
SKY = (26, 46, 68)
SEA = (29, 95, 122)
SEA_DK = (20, 66, 88)
WHITE = (246, 247, 240)
GREY = (140, 150, 160)
GREY_DK = (96, 104, 112)
ORANGE = (232, 110, 28)
FLAME = (244, 178, 44)
RED2 = (196, 52, 44)
PANEL_DK = (18, 42, 66)
PANEL_EARTH = (36, 22, 17)
GREEN_SMOKE = (112, 128, 104)

# --- 5x7 bitmap font, 7 rows of 5 columns each ---------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "00110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
}


class Canvas:
    """A plain RGB pixel buffer with small filled-shape helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def hline(self, x, y, length, color, thick=1):
        for t in range(thick):
            yy = y + t
            if 0 <= yy < self.h:
                x0 = max(0, x)
                x1 = min(self.w, x + length)
                if x1 > x0:
                    i = (yy * self.w + x0) * 3
                    self.buf[i:i + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def vline(self, x, y, length, color, thick=1):
        for t in range(thick):
            xx = x + t
            for yy in range(y, y + length):
                self.set(xx, yy, color)

    def fill_rect(self, x, y, w, h, color):
        row = bytes(color) * w
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                x0 = max(0, x)
                x1 = min(self.w, x + w)
                if x1 > x0:
                    i = (yy * self.w + x0) * 3
                    self.buf[i:i + (x1 - x0) * 3] = row[: (x1 - x0) * 3]

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = isqrt(max(0, r * r - dy * dy))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for dy in range(-r, r + 1):
            outer = isqrt(max(0, r * r - dy * dy))
            inner = isqrt(max(0, (r - thick) * (r - thick) - dy * dy))
            self.hline(cx - outer, cy + dy, outer - inner, color)
            self.hline(cx + inner, cy + dy, outer - inner + 1, color)

    def fill_poly(self, points, color):
        """Scanline polygon fill (even-odd rule), integer coordinates."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(round(xs[i])), y, int(round(xs[i + 1])) - int(round(xs[i])), color)

    def burst(self, cx, cy, r_out, r_in, spikes, color):
        pts = []
        for i in range(spikes * 2):
            ang = 3.141592653589793 * i / spikes
            r = r_out if i % 2 == 0 else r_in
            import math
            pts.append((int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))))
        self.fill_poly(pts, color)


def write_png(path, w, h, buf):
    """Minimal deterministic PNG: no ancillary chunks, fixed settings."""
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)

# --- text ---------------------------------------------------------------
def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    for ci, ch in enumerate(text):
        glyph = FONT.get(ch.upper(), FONT[" "])
        ox = x + ci * 6 * scale
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill_rect(ox + col * scale, y + row * scale, scale, scale, color)
    return x + text_width(text, scale)


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --- scene pieces -------------------------------------------------------
def draw_tanker(cv, x, y, scale, hull, deck):
    """A small oil tanker silhouette. (x, y) is the hull's top-left."""
    w = 300 * scale // 2
    h = 34 * scale // 2
    hull_pts = [(x, y), (x + w, y), (x + w - 18 * scale // 2, y + h),
                (x + 14 * scale // 2, y + h)]
    cv.fill_poly(hull_pts, hull)
    cv.fill_rect(x + 30 * scale // 2, y - 16 * scale // 2, 120 * scale // 2, 16 * scale // 2, deck)
    cv.fill_rect(x + 190 * scale // 2, y - 30 * scale // 2, 26 * scale // 2, 30 * scale // 2, deck)
    cv.fill_rect(x + 196 * scale // 2, y - 38 * scale // 2, 14 * scale // 2, 8 * scale // 2, CRIMSON)
    cv.vline(x + 60 * scale // 2, y - 34 * scale // 2, 34 * scale // 2, deck, 2)


def draw_mine(cv, cx, cy, r, body):
    for k in range(8):
        import math
        ang = 3.141592653589793 * k / 4
        x1 = int(cx + (r - 3) * math.cos(ang))
        y1 = int(cy + (r - 3) * math.sin(ang))
        x2 = int(cx + (r + 9) * math.cos(ang))
        y2 = int(cy + (r + 9) * math.sin(ang))
        cv.line(x1, y1, x2, y2, body, 3)
        cv.disc(x2, y2, 3, body)
    cv.disc(cx, cy, r, body)
    cv.disc(cx - r // 3, cy - r // 3, r // 4, GREY)


def draw_rocket(cv, cx, y, scale, body, accent):
    """A simple upright rocket, nose at y, body height ~120*scale/2."""
    w = 34 * scale // 2
    h = 84 * scale // 2
    nose = 30 * scale // 2
    body_pts = [(cx - w // 2, y + nose), (cx + w // 2, y + nose),
                (cx + w // 2, y + nose + h), (cx - w // 2, y + nose + h)]
    cv.fill_poly(body_pts, body)
    cv.fill_poly([(cx, y), (cx - w // 2, y + nose), (cx + w // 2, y + nose)], accent)
    cv.disc(cx, y + nose + h // 3, 7 * scale // 2, SKY)
    cv.ring(cx, y + nose + h // 3, 7 * scale // 2, accent, 2)
    cv.fill_poly([(cx - w // 2, y + nose + h - 18 * scale // 2),
                  (cx - w // 2 - 16 * scale // 2, y + nose + h),
                  (cx - w // 2, y + nose + h)], accent)
    cv.fill_poly([(cx + w // 2, y + nose + h - 18 * scale // 2),
                  (cx + w // 2 + 16 * scale // 2, y + nose + h),
                  (cx + w // 2, y + nose + h)], accent)
    cv.burst(cx, y + nose + h + 22 * scale // 2, 20 * scale // 2, 9 * scale // 2, 8, ORANGE)
    cv.burst(cx, y + nose + h + 20 * scale // 2, 11 * scale // 2, 5 * scale // 2, 8, FLAME)


def draw_bars(cv, x, y, w, h, color_down, color_bar):
    """Three falling bars with a down arrow."""
    bw = w // 4
    heights = [h, int(h * 0.68), int(h * 0.38)]
    for i, bh in enumerate(heights):
        bx = x + i * (bw + 8)
        cv.fill_rect(bx, y + h - bh, bw, bh, color_bar)
    cv.line(x - 6, y - 8, x + w + 4, y + h - 6, color_down, 4)
    cv.fill_poly([(x + w + 4, y + h - 6), (x + w - 12, y + h - 14),
                  (x + w - 6, y + h + 6)], color_down)


def draw_flame(cv, cx, cy, r, core):
    cv.burst(cx, cy, r, r // 2, 10, ORANGE)
    cv.burst(cx, cy, int(r * 0.62), r // 3, 8, FLAME)
    cv.disc(cx, cy, r // 3, core)

# --- layout -------------------------------------------------------------
def draw_masthead(cv):
    cv.fill_rect(0, 0, W, 44, CRIMSON)
    draw_text_centered(cv, W // 2, 11, "THE WORLD IN ONE DAY", 3, WHITE)
    cv.fill_rect(0, 44, W, 88, PAPER)
    draw_text_centered(cv, W // 2, 54, "WEDNESDAY", 3, INK)
    draw_text_centered(cv, W // 2, 78, "25 NOVEMBER 2026", 7, INK)
    cv.hline(0, 132, W, INK, 2)


def draw_hero(cv):
    # Sea scene on the left.
    cv.fill_rect(0, 134, 470, 166, SKY)
    cv.fill_rect(0, 300, 470, 140, SEA)
    cv.hline(0, 300, 470, SEA_DK, 3)
    for sx, sy in ((36, 168), (120, 210), (210, 156), (300, 196), (392, 168), (448, 226), (70, 256), (258, 262)):
        cv.disc(sx, sy, 2, WHITE)
    draw_tanker(cv, 56, 330, 2, INK, INK)
    draw_mine(cv, 420, 356, 18, INK)
    for wx, wy, wl in ((24, 384, 90), (150, 402, 120), (300, 388, 80), (60, 420, 130), (240, 424, 90), (380, 408, 60)):
        cv.hline(wx, wy, wl, WHITE, 2)
    draw_flame(cv, 402, 246, 44, GOLD_LT)
    cv.disc(356, 214, 12, GREY)
    cv.disc(336, 200, 8, GREY_DK)
    cv.disc(376, 198, 7, GREY_DK)
    # Headline block on the right.
    cv.fill_rect(470, 134, W - 470, 306, PAPER)
    cv.vline(468, 134, 306, INK, 2)
    cv.fill_rect(496, 158, 64, 5, GOLD)
    draw_text(cv, 496, 176, "MIDDLE EAST / ENERGY", 2, CRIMSON)
    draw_text(cv, 496, 206, "TANKERS HIT", 6, INK)
    draw_text(cv, 496, 254, "MINES IN", 6, INK)
    draw_text(cv, 496, 302, "HORMUZ", 6, CRIMSON)
    caption = ("IRAN SAYS NAVAL MINES STRUCK TANKERS IN THE STRAIT. "
               "THE U.S. MILITARY DISPUTES THE CLAIM.")
    for i, line in enumerate(wrap_text(caption, 2, 500)):
        draw_text(cv, 496, 362 + i * 18, line, 2, INK)
    cv.hline(0, 440, W, INK, 2)


def draw_panel(cv, x, y, w, h, bg, kicker, kicker_color, lines, caption,
              caption_color):
    cv.fill_rect(x, y, w, h, bg)
    cv.hline(x, y, w, GOLD, 4)
    tx = x + 132
    tw = x + w - 14 - tx
    draw_text(cv, tx, y + 18, kicker, 2, kicker_color)
    for i, line in enumerate(lines):
        draw_text(cv, tx, y + 46 + i * 34, line, 4, WHITE if bg in (PANEL_DK, PANEL_EARTH) else INK)
    cy = y + 46 + len(lines) * 34 + 6
    for i, line in enumerate(wrap_text(caption, 2, tw)):
        draw_text(cv, tx, cy + i * 18, line, 2, caption_color)


def _icon_space(cv):
    draw_rocket(cv, 66, 456, 2, WHITE, CRIMSON)
    for sx, sy in ((16, 462), (112, 470), (24, 560), (104, 590), (46, 600)):
        cv.disc(sx, sy, 2, WHITE)


def _icon_tariffs(cv):
    draw_bars(cv, 548, 500, 84, 72, RED2, INK)


def _icon_gas(cv):
    draw_text(cv, 30, 656, "34", 7, INK)
    cv.disc(52, 748, 16, GREEN_SMOKE)
    cv.disc(84, 756, 11, GREEN_SMOKE)
    cv.disc(28, 758, 9, GREEN_SMOKE)


def _icon_fire(cv):
    draw_flame(cv, 582, 700, 40, GOLD_LT)
    cv.fill_rect(540, 762, 100, 8, GREY_DK)
    cv.hline(540, 765, 100, WHITE, 2)


# (x, y, background, kicker, kicker color, headline lines, caption,
#  caption color, icon painter)
PANELS = [
    (0, 448, PANEL_DK, "SPACE / ASIA", GOLD,
     ["PAKISTAN'S FIRST", "ASTRONAUT"],
     "SHENZHOU-24 CARRIES ALI TO CHINA'S TIANGONG STATION.", GOLD_LT,
     _icon_space),
    (516, 448, PAPER, "ECONOMY / U.S.", CRIMSON,
     ["NEW U.S. TARIFFS", "FOR 14 PARTNERS"],
     "DUTIES PROPOSED ON 14 TRADING PARTNERS; STOCKS SLIDE.", INK,
     _icon_tariffs),
    (0, 624, PAPER2, "EUROPE / DIPLOMACY", CRIMSON,
     ["34 NATIONS SAY:", "END GAS ATTACKS"],
     "JOINT CALL ON RUSSIA AS TEAR GAS IS CONFIRMED IN UKRAINE.", INK,
     _icon_gas),
    (516, 624, PANEL_EARTH, "EGYPT / DISASTER", GOLD,
     ["DEADLY CAIRO", "TANKER FIRE"],
     "FUEL TANKER OVERTURNS ON THE RING ROAD; AT LEAST 30 DEAD.", GOLD_LT,
     _icon_fire),
]


def draw_grid(cv):
    for x, y, bg, kicker, kcolor, lines, caption, ccolor, icon in PANELS:
        draw_panel(cv, x, y, 508, 168, bg, kicker, kcolor, lines, caption, ccolor)
        icon(cv)


def draw_strips(cv):
    cv.fill_rect(0, 800, W, 96, NAVY_DARK)
    draw_text(cv, 24, 812, "ALSO ON 25 NOVEMBER", 3, GOLD)
    items = [
        "SUDAN: RSF DRONE STRIKES KILL 19 CIVILIANS, RIGHTS GROUP SAYS",
        "SOLOMON ISLANDS, AUSTRALIA SIGN PACT BARRING FOREIGN BASES",
        "HOUTHIS CLAIM STRIKE ON SAUDI RAS TANURA REFINERY; OIL RISES",
    ]
    for i, item in enumerate(items):
        yy = 842 + i * 18
        cv.fill_rect(24, yy + 4, 8, 8, GOLD)
        draw_text(cv, 44, yy, item, 2, WHITE)
    cv.fill_rect(0, 896, W, 128, PAPER)
    draw_text(cv, 24, 910, "REPORTED EARLIER - NOT 25 NOVEMBER NEWS:", 2, CRIMSON)
    draw_text(cv, 24, 934, "24 NOV: U.S. JURY CONVICTS HUAWEI ON 10 OF 12 COUNTS", 2, INK)
    draw_text(cv, 24, 954, "24 NOV: RIYADH TOWER STRIKE WOUNDS 11", 2, INK)
    cv.hline(24, 982, W - 48, GOLD, 2)
    draw_text_centered(cv, W // 2, 992,
                       "DRAWN FROM WIRE REPORTS. ALL EVENTS FIRST REPORTED 25 NOV 2026 UNLESS NOTED.",
                       2, INK)
    cv.fill_rect(0, 1016, W, 8, CRIMSON)
    cv.hline(0, 0, W, GOLD, 3)
    cv.hline(0, H - 3, W, GOLD, 3)
    cv.vline(0, 0, H, GOLD, 3)
    cv.vline(W - 3, 0, H, GOLD, 3)


def draw():
    cv = Canvas(W, H, NAVY)
    draw_masthead(cv)
    draw_hero(cv)
    draw_grid(cv)
    draw_strips(cv)
    return cv.buf


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    write_png(os.path.join(out, "entry.png"), W, H, draw())


if __name__ == "__main__":
    main()
