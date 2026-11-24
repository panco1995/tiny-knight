"""Pixel-art assets and the pre-rendered arena floor.

All graphics are drawn in code with the Pyxel 16-color palette, so the game
ships without any external image files and every asset is free to use.
"""

import math
import random

import pyxel

ARENA_W = 640
ARENA_H = 480
TS = 16

# A warmer, more natural palette than the default Pyxel one.
PALETTE = [
    0x0E1016,  # 0  black
    0x252A38,  # 1  outline / shadow
    0x5C3A73,  # 2  purple
    0x2E6B46,  # 3  grass
    0x7B4F2D,  # 4  dirt
    0x3B4655,  # 5  slate
    0x8FB8DE,  # 6  light blue
    0xF1EFE4,  # 7  white
    0xC8443C,  # 8  red
    0xD98A3D,  # 9  orange
    0xF2C94C,  # 10 yellow
    0x7FBF6A,  # 11 light green
    0x62C6D6,  # 12 cyan
    0x9AA0A0,  # 13 stone
    0xE08FA8,  # 14 pink
    0xF2C9A0,  # 15 peach
]

# --- Sprite sheet layout (16x16 cells unless noted) --------------------------
PLAYER_FRAMES = {
    "down": ((0, 0), (16, 0)),
    "up": ((32, 0), (48, 0)),
    "side": ((64, 0), (80, 0)),
    "side_l": ((96, 0), (112, 0)),
}
ENEMY_FRAMES = {
    "slime": ((0, 16), (16, 16)),
    "bat": ((32, 16), (48, 16)),
    "archer": ((64, 16), (80, 16)),
}
UI_SPRITES = {
    "heart": (96, 16, 8, 8),
    "heart_empty": (104, 16, 8, 8),
    "rock": (0, 32, 16, 16),
    "bush": (16, 32, 16, 16),
    "torch": (32, 32, 8, 16),
    "flower": (40, 32, 8, 8),
}

PLAYER_DOWN = [
    "................",
    ".......11.......",
    "......1881......",
    ".....188881.....",
    "....17777771....",
    "...1777777771...",
    "...1733333371...",
    "...1733333371...",
    "....15555551....",
    "....15755751....",
    "....15555551....",
    "...1677777761...",
    "...1677777761...",
    "...1644444661...",
    "....16666661....",
    ".....14..41.....",
]

PLAYER_DOWN_B = [
    "................",
    ".......11.......",
    "......1881......",
    ".....188881.....",
    "....17777771....",
    "...1777777771...",
    "...1733333371...",
    "...1733333371...",
    "....15555551....",
    "....15755751....",
    "....15555551....",
    "...1677777761...",
    "...1677777761...",
    "...1644444661...",
    "....16666661....",
    "....14....41....",
]

PLAYER_UP = [
    "................",
    ".......11.......",
    "......1881......",
    ".....188881.....",
    "....17777771....",
    "...1777777771...",
    "...1773333771...",
    "...1773333771...",
    "....13333331....",
    "....13333331....",
    "....13333331....",
    "...1666666661...",
    "..166666666661..",
    "..166666666661..",
    "...1666666661...",
    ".....11..11.....",
]

PLAYER_UP_B = [
    "................",
    ".......11.......",
    "......1881......",
    ".....188881.....",
    "....17777771....",
    "...1777777771...",
    "...1773333771...",
    "...1773333771...",
    "....13333331....",
    "....13333331....",
    "....13333331....",
    "...1666666661...",
    "..166666666661..",
    "..166666666661..",
    "...1666666661...",
    "....11....11....",
]

PLAYER_SIDE = [
    "................",
    "........11......",
    ".......1881.....",
    "......188881....",
    ".....17777771...",
    "....1777777771..",
    "....1733333371..",
    "....1733333371..",
    ".....15555551...",
    ".....15755751...",
    ".....15555551...",
    "...1677777761...",
    "...1677777761...",
    "...1644444661...",
    "....16666661....",
    ".....11.11......",
]

PLAYER_SIDE_B = [
    "................",
    "........11......",
    ".......1881.....",
    "......188881....",
    ".....17777771...",
    "....1777777771..",
    "....1733333371..",
    "....1733333371..",
    ".....15555551...",
    ".....15755751...",
    ".....15555551...",
    "...1677777761...",
    "...1677777761...",
    "...1644444661...",
    "....16666661....",
    "....11...11.....",
]

SLIME = [
    "................",
    "................",
    "................",
    "................",
    "................",
    ".....111111.....",
    "....1bbbbbb1....",
    "..1bbbbbbbbbb1..",
    "..1bb1bbbb1bb1..",
    "..1bbbbbbbbbb1..",
    "..1bbbb11bbbb1..",
    "..1bbbbbbbbbb1..",
    "..1b3bbbbbb3b1..",
    "...1bbbbbbbb1...",
    "....11111111....",
    "................",
]

SLIME_B = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    ".....111111.....",
    "...11bbbbbb11...",
    "..1bbbbbbbbbb1..",
    ".1bb1bbbb1bbbb1.",
    ".1bbbbbbbbbbbb1.",
    ".1b3bbbbbbbb3b1.",
    ".1bbbb11bbbbbb1.",
    "..1bbbbbbbbbb1..",
    "...1111111111...",
]

BAT = [
    "................",
    "................",
    "..11........11..",
    ".1221......1221.",
    "122221....122221",
    "1222221111122221",
    "1222221222122221",
    "1222221888122221",
    ".12222111112221.",
    "..1222222222221.",
    "...122222222221.",
    "....1222222221..",
    ".....11222211...",
    ".......1111.....",
    "................",
    "................",
]

BAT_B = [
    "................",
    "................",
    "................",
    "..11........11..",
    ".1221......1221.",
    "122221....122221",
    "1222221111122221",
    "1222221222122221",
    "1222221888122221",
    ".12222111112221.",
    "..1222222222221.",
    "...122222222221.",
    "....1222222221..",
    ".....11222211...",
    ".......1111.....",
    "................",
]

ARCHER = [
    "................",
    "......1111......",
    ".....155551.....",
    "....15555551....",
    "....15777751....",
    "....17888771....",
    "....17777771....",
    "....15555551....",
    "...1555555551...",
    "..155555555551..",
    "..155144415551..",
    "..155555555551..",
    ".15555555555551.",
    ".15555555555551.",
    ".11111111111111.",
    "................",
]

ARCHER_B = [
    "................",
    "......1111......",
    ".....155551.....",
    "....15555551....",
    "....15777751....",
    "....17888771....",
    "....17777771....",
    "....15555551....",
    "...1555555551...",
    "..155555555551..",
    "..155144415551..",
    "..155555555551..",
    ".15555555555551.",
    ".15555555555551.",
    ".11111111111111.",
    "................",
]

HEART = [
    "........",
    ".11..11.",
    "18811881",
    "18888881",
    "18888881",
    ".188881.",
    "..1881..",
    "...11...",
]

HEART_EMPTY = [
    "........",
    ".11..11.",
    "15511551",
    "15555551",
    "15555551",
    ".155551.",
    "..1551..",
    "...11...",
]

ROCK = [
    "................",
    "................",
    "................",
    "................",
    "......1111......",
    ".....133331.....",
    "....13733331....",
    "...1337333331...",
    "..133733333331..",
    "..133333333331..",
    ".13333333333331.",
    ".13333333333331.",
    ".13333333533331.",
    ".13333355533331.",
    "..111111111111..",
    "................",
]

BUSH = [
    "................",
    "................",
    "......1111......",
    "....11333311....",
    "...1333333331...",
    "..133113333331..",
    "..131333333331..",
    ".13333311333331.",
    ".13333113333331.",
    ".13333333333331.",
    ".13333333333331.",
    "..133333333331..",
    "..113333333311..",
    "....11111111....",
    "................",
    "................",
]

TORCH = [
    "........",
    "...11...",
    "..1991..",
    "..1891..",
    "..1881..",
    "...11...",
    "..1441..",
    "..1441..",
    "..1441..",
    "..1441..",
    "..1441..",
    "..1441..",
    "..1441..",
    "..1441..",
    "..1111..",
    "........",
]

FLOWER = [
    "........",
    "........",
    "..1..1..",
    ".181181.",
    "..1111..",
    "...33...",
    "...35...",
    "........",
]

# --- 3x5 bitmap font for chunky titles ---------------------------------------
FONT = {
    "A": ["010", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"],
    "D": ["110", "101", "101", "101", "110"],
    "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
    "G": ["011", "100", "101", "101", "011"],
    "H": ["101", "101", "111", "101", "101"],
    "I": ["111", "010", "010", "010", "111"],
    "J": ["001", "001", "001", "101", "010"],
    "K": ["101", "101", "110", "101", "101"],
    "L": ["100", "100", "100", "100", "111"],
    "M": ["101", "111", "111", "101", "101"],
    "N": ["101", "111", "111", "111", "101"],
    "O": ["010", "101", "101", "101", "010"],
    "P": ["110", "101", "110", "100", "100"],
    "Q": ["010", "101", "101", "110", "011"],
    "R": ["110", "101", "110", "101", "101"],
    "S": ["011", "100", "010", "001", "110"],
    "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "111"],
    "V": ["101", "101", "101", "101", "010"],
    "W": ["101", "101", "111", "111", "101"],
    "X": ["101", "101", "010", "101", "101"],
    "Y": ["101", "101", "010", "010", "010"],
    "Z": ["111", "001", "010", "100", "111"],
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["110", "001", "010", "100", "111"],
    "3": ["110", "001", "010", "001", "110"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "110", "001", "110"],
    "6": ["011", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "110"],
    " ": ["000", "000", "000", "000", "000"],
    "!": ["010", "010", "010", "000", "010"],
    "-": ["000", "000", "111", "000", "000"],
    "+": ["000", "010", "111", "010", "000"],
    ":": ["000", "010", "000", "010", "000"],
    ".": ["000", "000", "000", "000", "010"],
    "/": ["001", "001", "010", "100", "100"],
}


def draw_font(x, y, text, col, scale=3, shadow=None):
    """Draw text with the chunky 3x5 font; returns the drawn width."""
    text = text.upper()
    adv = 4 * scale
    if shadow is not None:
        _font_run(x + scale, y + scale, text, shadow, scale)
    _font_run(x, y, text, col, scale)
    return len(text) * adv - scale


def _font_run(x, y, text, col, scale):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    pyxel.rect(cx + gx * scale, y + gy * scale, scale, scale, col)
        cx += 4 * scale


def font_width(text, scale=3):
    return len(text) * 4 * scale - scale


class Art:
    """Loads the sprite sheet and bakes the arena floor once at startup."""

    def __init__(self):
        for i, col in enumerate(PALETTE):
            pyxel.colors[i] = col
        self.img = pyxel.Image(128, 64)
        self.flash = pyxel.Image(128, 64)
        self.floor = pyxel.Image(ARENA_W, ARENA_H)
        self.fireflies = [
            [pyxel.rndf(30, ARENA_W - 30), pyxel.rndf(30, ARENA_H - 30),
             pyxel.rndf(0, math.tau), pyxel.rndf(0.4, 1.1), pyxel.rndf(18, 40)]
            for _ in range(24)
        ]
        self.props = []
        self.torches = []
        self._load_sprites()
        self._build_floor()
        self._place_props()

    # -- sprites -------------------------------------------------------------
    def _put(self, data, u, v):
        for y, row in enumerate(data):
            for x, ch in enumerate(row):
                if ch != ".":
                    self.img.pset(u + x, v + y, int(ch, 16))

    def _mirror(self, u, v, du, dv, w=16, h=16):
        for y in range(h):
            for x in range(w):
                c = self.img.pget(u + x, v + y)
                if c:
                    self.img.pset(du + w - 1 - x, dv + y, c)

    def _flash_mask(self, u, v, w=16, h=16):
        for y in range(h):
            for x in range(w):
                if self.img.pget(u + x, v + y):
                    self.flash.pset(u + x, v + y, 7)

    def _load_sprites(self):
        self.img.cls(0)
        self.flash.cls(0)
        data = [
            (PLAYER_DOWN, 0, 0), (PLAYER_DOWN_B, 16, 0),
            (PLAYER_UP, 32, 0), (PLAYER_UP_B, 48, 0),
            (PLAYER_SIDE, 64, 0), (PLAYER_SIDE_B, 80, 0),
            (SLIME, 0, 16), (SLIME_B, 16, 16),
            (BAT, 32, 16), (BAT_B, 48, 16),
            (ARCHER, 64, 16), (ARCHER_B, 80, 16),
            (ROCK, 0, 32), (BUSH, 16, 32),
            (TORCH, 32, 32), (FLOWER, 40, 32),
        ]
        for rows, u, v in data:
            self._put(rows, u, v)
        self._mirror(64, 0, 96, 0)
        self._mirror(80, 0, 112, 0)
        # 8x8 UI art lives at the right end of the enemy row
        self._put(HEART, 96, 16)
        self._put(HEART_EMPTY, 104, 16)
        for u, v, w, h in (
            (0, 0, 16, 16), (16, 0, 16, 16), (32, 0, 16, 16),
            (48, 0, 16, 16), (64, 0, 16, 16), (80, 0, 16, 16),
            (0, 16, 16, 16), (16, 16, 16, 16), (32, 16, 16, 16),
            (48, 16, 16, 16), (64, 16, 16, 16), (80, 16, 16, 16),
            (0, 32, 16, 16), (16, 32, 16, 16),
        ):
            self._flash_mask(u, v, w, h)

    # -- floor ---------------------------------------------------------------
    def _grass_tile(self, x, y, rnd):
        f = self.floor
        f.rect(x, y, 16, 16, 3)
        for _ in range(7):
            f.pset(x + rnd.randrange(16), y + rnd.randrange(16), 11)
        for _ in range(4):
            f.pset(x + rnd.randrange(16), y + rnd.randrange(16), 5)
        if rnd.random() < 0.45:
            gx, gy = x + rnd.randrange(1, 14), y + rnd.randrange(3, 14)
            f.pset(gx, gy, 11)
            f.pset(gx + 1, gy, 11)
            f.pset(gx, gy - 1, 11)
            f.pset(gx, gy + 1, 5)

    def _dirt_tile(self, x, y, rnd):
        f = self.floor
        f.rect(x, y, 16, 16, 4)
        for _ in range(9):
            f.pset(x + rnd.randrange(16), y + rnd.randrange(16), 9)
        for _ in range(5):
            f.pset(x + rnd.randrange(16), y + rnd.randrange(16), 1)
        if rnd.random() < 0.3:
            sx, sy = x + rnd.randrange(2, 13), y + rnd.randrange(2, 13)
            f.rect(sx, sy, 2, 2, 13)
            f.pset(sx, sy, 7)

    def _stone_tile(self, x, y, rnd):
        f = self.floor
        f.rect(x, y, 16, 16, 13)
        # Large 32x32 flagstones: seams only on every other tile edge.
        if (y // 16) % 2 == 1:
            f.line(x, y + 15, x + 15, y + 15, 5)
        if (x // 16) % 2 == 1:
            f.line(x + 15, y, x + 15, y + 15, 5)
        if rnd.random() < 0.55:
            cx = x + rnd.randrange(2, 12)
            cy = y + rnd.randrange(3, 13)
            f.line(cx, cy, cx + rnd.randrange(1, 4), cy + rnd.randrange(1, 3), 5)
        for _ in range(rnd.randrange(1, 4)):
            f.pset(x + rnd.randrange(2, 14), y + rnd.randrange(2, 14), 5)
        if rnd.random() < 0.6:
            mx, my = x + rnd.randrange(1, 12), y + rnd.randrange(2, 15)
            f.pset(mx, my, 3)
            f.pset(mx + 1, my, 3)
            f.pset(mx, my - 1, 11)
            if rnd.random() < 0.5:
                f.pset(mx + 2, my + 1, 3)

    def _wall_tile(self, x, y, rnd):
        f = self.floor
        f.rect(x, y, 16, 16, 5)
        for _ in range(5):
            f.pset(x + rnd.randrange(16), y + rnd.randrange(16), 1)
        for _ in range(3):
            f.pset(x + rnd.randrange(16), y + rnd.randrange(16), 13)
        if rnd.random() < 0.35:
            cx = x + rnd.randrange(2, 12)
            cy = y + rnd.randrange(2, 12)
            f.line(cx, cy, cx + 2, cy + rnd.randrange(1, 4), 1)
        if rnd.random() < 0.55:
            mx, my = x + rnd.randrange(2, 13), y + rnd.randrange(2, 14)
            f.rect(mx, my, 2, 2, 3)
            f.pset(mx, my, 11)
        if rnd.random() < 0.25:
            vx = x + rnd.randrange(3, 13)
            vy = y + rnd.randrange(2, 12)
            f.pset(vx, vy, 3)
            f.pset(vx, vy + 1, 3)
            f.pset(vx + 1, vy + 2, 11)

    def _build_floor(self):
        f = self.floor
        rnd = random.Random(20240517)
        f.cls(3)
        cols, rows = ARENA_W // TS, ARENA_H // TS
        for ty in range(rows):
            for tx in range(cols):
                self._grass_tile(tx * TS, ty * TS, rnd)

        cx, cy = ARENA_W / 2, ARENA_H / 2
        # Worn dirt paths forming a cross between the plaza and the walls
        for ty in range(1, rows - 1):
            for tx in range(1, cols - 1):
                px, py = tx * TS + 8, ty * TS + 8
                wobble = math.sin(tx * 0.45 + ty * 0.8) * 6 + math.cos(ty * 0.6) * 3
                width = 21 + wobble
                vertical = abs(px - cx) < width and abs(py - cy) > 92
                horizontal = abs(py - cy) < width - 4 and abs(px - cx) > 120
                if vertical or horizontal:
                    self._dirt_tile(tx * TS, ty * TS, rnd)

        # Central stone plaza with a slightly irregular outline
        plaza = []
        for ty in range(rows):
            for tx in range(cols):
                px, py = tx * TS + 8, ty * TS + 8
                wobble = math.sin(tx * 0.9) * 0.035 + math.cos(ty * 1.1) * 0.035
                d = ((px - cx) / 122) ** 2 + ((py - cy) / 96) ** 2
                if d < 0.9 + wobble:
                    plaza.append((tx, ty, d))
                    self._stone_tile(tx * TS, ty * TS, rnd)
        for tx, ty, d in plaza:
            if d > 0.7:
                f.pset(tx * TS + rnd.randrange(16), ty * TS + rnd.randrange(16), 3)

        # Ruined wall ring
        for ty in range(rows):
            for tx in range(cols):
                if tx in (0, cols - 1) or ty in (0, rows - 1):
                    self._wall_tile(tx * TS, ty * TS, rnd)
        # Inner shadow so the walls read as raised
        f.rect(TS, TS, ARENA_W - 2 * TS, 4, 1)
        f.rect(TS, ARENA_H - TS - 4, ARENA_W - 2 * TS, 4, 1)
        f.rect(TS, TS, 4, ARENA_H - 2 * TS, 1)
        f.rect(ARENA_W - TS - 4, TS, 4, ARENA_H - 2 * TS, 1)
        f.rect(TS + 4, TS + 4, ARENA_W - 2 * TS - 8, 2, 5)
        f.rect(TS + 4, ARENA_H - TS - 6, ARENA_W - 2 * TS - 8, 2, 5)
        f.rect(TS + 4, TS + 4, 2, ARENA_H - 2 * TS - 8, 5)
        f.rect(ARENA_W - TS - 6, TS + 4, 2, ARENA_H - 2 * TS - 8, 5)
        f.line(TS, TS, TS, ARENA_H - TS - 1, 6)
        f.line(TS, TS, ARENA_W - TS - 1, TS, 6)
        f.line(ARENA_W - TS - 1, TS, ARENA_W - TS - 1, ARENA_H - TS - 1, 6)
        f.line(TS, ARENA_H - TS - 1, ARENA_W - TS - 1, ARENA_H - TS - 1, 6)

    def _place_props(self):
        rnd = random.Random(99)
        cx, cy = ARENA_W / 2, ARENA_H / 2
        self.torches = [
            (int(cx - 102), int(cy - 78)),
            (int(cx + 98), int(cy - 78)),
            (int(cx - 102), int(cy + 78)),
            (int(cx + 98), int(cy + 78)),
        ]
        for i in range(18):
            kind = "bush" if i % 3 else "rock"
            for _ in range(40):
                x = rnd.randrange(48, ARENA_W - 64)
                y = rnd.randrange(48, ARENA_H - 64)
                if ((x - cx) / 150) ** 2 + ((y - cy) / 120) ** 2 < 1:
                    continue
                self.props.append((kind, x, y))
                break
        for _ in range(30):
            x = rnd.randrange(40, ARENA_W - 48)
            y = rnd.randrange(40, ARENA_H - 48)
            if ((x - cx) / 150) ** 2 + ((y - cy) / 120) ** 2 < 1:
                continue
            self.props.append(("flower", x, y))

    # -- runtime drawing helpers --------------------------------------------
    def draw_floor(self, cam_x, cam_y):
        pyxel.blt(0, 0, self.floor, cam_x, cam_y, pyxel.width, pyxel.height)

    def draw_glows(self, cam_x, cam_y, t):
        pyxel.dither(0.28)
        for i, (tx, ty) in enumerate(self.torches):
            flicker = int(math.sin(t * 0.21 + i * 1.9) * 3)
            pyxel.circ(tx - cam_x, ty - 12 - cam_y, 18 + flicker, 9)
        pyxel.dither(1.0)

    def draw_prop(self, kind, x, y, cam_x, cam_y, t=0, index=0):
        u, v, w, h = UI_SPRITES[kind]
        pyxel.blt(x - cam_x, y - cam_y, self.img, u, v, w, h, 0)
        if kind == "torch":
            flicker = 1 if math.sin(t * 0.3 + index) > 0 else 0
            fx, fy = x - cam_x + 1, y - cam_y + 1
            pyxel.pset(fx + 2, fy + 4 - flicker, 10)
            pyxel.pset(fx + 5, fy + 3, 9)
            pyxel.pset(fx + 3, fy - 0 + flicker, 9)
            pyxel.pset(fx + 4, fy - 2, 10)
            pyxel.pset(fx + 3, fy - 1, 8)

    def update_fireflies(self, t):
        for f in self.fireflies:
            f[2] += 0.015 + f[3] * 0.004
            f[0] += math.cos(f[2]) * 0.25
            f[1] += math.sin(f[2] * 0.8) * 0.18

    def draw_fireflies(self, cam_x, cam_y, t):
        for i, f in enumerate(self.fireflies):
            x = (f[0] + math.cos(f[2]) * 8) % ARENA_W
            y = (f[1] + math.sin(f[2] * 0.7) * 6) % ARENA_H
            if -4 < x - cam_x < pyxel.width + 4 and -4 < y - cam_y < pyxel.height + 4:
                if math.sin(t * 0.09 + i * 1.3) > -0.2:
                    col = 10 if (t // 24 + i) % 3 else 11
                    pyxel.pset(x - cam_x, y - cam_y, col)

    def draw_sprite(self, frames, frame, x, y, cam_x, cam_y, flash=False):
        u, v = frames[frame % len(frames)]
        img = self.flash if flash else self.img
        pyxel.blt(x - cam_x, y - cam_y, img, u, v, 16, 16, 0)
