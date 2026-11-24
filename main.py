# title: Tiny Knight
# desc: A tiny top-down wave survival game made with Pyxel.
# version: 1.0

"""TINY KNIGHT - a tiny top-down arena action game built with Pyxel.

Controls
    WASD / Arrow keys ... move
    Space / Z / J ....... sword slash
    Shift / X / K ....... dash (brief invincibility)
    P ................... pause
    Esc ................. quit

All art and sound are generated in code, so there are no external assets.
"""

import math
import os
import random
import sys

import pyxel

from art import (
    ARENA_H,
    ARENA_W,
    ENEMY_FRAMES,
    PLAYER_FRAMES,
    UI_SPRITES,
    Art,
    draw_font,
    font_width,
)

W, H = 256, 224

STATE_TITLE = 0
STATE_PLAY = 1
STATE_PAUSE = 2
STATE_OVER = 3

MOVE_UP = (pyxel.KEY_UP, pyxel.KEY_W)
MOVE_DOWN = (pyxel.KEY_DOWN, pyxel.KEY_S)
MOVE_LEFT = (pyxel.KEY_LEFT, pyxel.KEY_A)
MOVE_RIGHT = (pyxel.KEY_RIGHT, pyxel.KEY_D)
ATTACK_KEYS = (pyxel.KEY_SPACE, pyxel.KEY_Z, pyxel.KEY_J)
DASH_KEYS = (pyxel.KEY_SHIFT, pyxel.KEY_X, pyxel.KEY_K)
START_KEYS = (pyxel.KEY_SPACE, pyxel.KEY_Z, pyxel.KEY_RETURN)

PLAYER_SPEED = 1.55
PLAYER_MAX_HP = 5
ATTACK_LEN = 16
ATTACK_CD = 22
ATTACK_RADIUS = 30
DASH_LEN = 12
DASH_CD = 46
DASH_SPEED = 3.9
IFRAMES_HURT = 72
IFRAMES_DASH = 18

ENEMY_INFO = {
    "slime": {"hp": 2, "radius": 8, "speed": 0.58, "score": 10, "color": 3},
    "bat": {"hp": 1, "radius": 7, "speed": 1.05, "score": 15, "color": 2},
    "archer": {"hp": 3, "radius": 8, "speed": 0.52, "score": 25, "color": 13},
}


def _high_score_path():
    """Use a user data folder when running from a packaged .pyxapp.

    Pyxel unpacks packaged apps into a temporary directory, so a score file
    next to the script would be lost on exit. Running from source keeps the
    simple highscore.txt beside main.py.
    """
    app_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isfile(os.path.join(app_dir, ".pyxapp_startup_script")):
        return os.path.join(app_dir, "highscore.txt")
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(
            os.path.expanduser("~"), ".local", "share"
        )
    return os.path.join(base, "TinyKnight", "highscore.txt")


HS_PATH = _high_score_path()


def clamp(v, low, high):
    return low if v < low else high if v > high else v


def clamp_arena(x, y):
    return clamp(x, 24, ARENA_W - 24), clamp(y, 26, ARENA_H - 26)


def any_btn(keys):
    return any(pyxel.btn(k) for k in keys)


def any_btnp(keys):
    return any(pyxel.btnp(k) for k in keys)


def load_high_score():
    try:
        with open(HS_PATH, "r", encoding="utf-8") as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def save_high_score(value):
    try:
        os.makedirs(os.path.dirname(HS_PATH), exist_ok=True)
        with open(HS_PATH, "w", encoding="utf-8") as f:
            f.write(str(value))
    except OSError:
        pass


def small_width(text):
    return len(text) * pyxel.FONT_WIDTH - 1


def draw_text_center(y, text, col):
    pyxel.text((W - small_width(text)) // 2, y, text, col)


def draw_panel(x, y, w, h, border=5):
    pyxel.dither(0.88)
    pyxel.rect(x, y, w, h, 0)
    pyxel.dither(1.0)
    pyxel.rectb(x, y, w, h, border)


def draw_big_center(y, text, col, scale=3, shadow=1):
    draw_font((W - font_width(text, scale)) // 2, y, text, col, scale, shadow)


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "col", "size", "grav")

    def __init__(self, x, y, vx, vy, col, life, size=1, grav=0.03):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.col = col
        self.life = life
        self.size = size
        self.grav = grav

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.grav
        self.vx *= 0.97
        self.vy *= 0.97
        self.life -= 1

    def draw(self, cam_x, cam_y):
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        if self.size > 1:
            pyxel.rect(sx, sy, self.size, self.size, self.col)
        else:
            pyxel.pset(sx, sy, self.col)


class Floater:
    def __init__(self, x, y, text, col=10, life=40):
        self.x = x
        self.y = y
        self.text = text
        self.col = col
        self.life = life

    def update(self):
        self.y -= 0.4
        self.life -= 1

    def draw(self, cam_x, cam_y):
        sx = int(self.x - cam_x) - small_width(self.text) // 2
        sy = int(self.y - cam_y)
        pyxel.text(sx + 1, sy + 1, self.text, 1)
        pyxel.text(sx, sy, self.text, self.col)


class HeartPickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.t = random.randrange(60)
        self.life = 540
        self.dead = False

    def update(self, game):
        self.t += 1
        self.life -= 1
        if self.life <= 0:
            self.dead = True
            return
        p = game.player
        if (
            p.hp < p.max_hp
            and math.hypot(p.x - self.x, p.y - self.y) < 14
        ):
            p.hp += 1
            self.dead = True
            game.play(4)
            game.burst(self.x, self.y, 12, 14, 1.2, -0.02)
            game.floaters.append(Floater(self.x, self.y - 12, "+1 HP", 14))

    def draw(self, game, cam_x, cam_y):
        if self.life < 100 and (self.life // 4) % 2 == 0:
            return
        bob = math.sin(self.t * 0.12) * 2
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y + bob)
        pyxel.dither(0.25)
        pyxel.circ(sx, sy, 9, 8)
        pyxel.dither(1.0)
        u, v, w, h = UI_SPRITES["heart"]
        pyxel.blt(sx - 4, sy - 4, game.art.img, u, v, w, h, 0)


class Arrow:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = 150
        self.dead = False

    def update(self, game):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0 or not (14 < self.x < ARENA_W - 14 and 14 < self.y < ARENA_H - 14):
            self.dead = True
            return
        p = game.player
        if math.hypot(p.x - self.x, p.y - self.y) < 8:
            p.hurt(1, self.x - self.vx * 6, self.y - self.vy * 6, game)
            self.dead = True

    def draw(self, cam_x, cam_y):
        sx, sy = self.x - cam_x, self.y - cam_y
        tx, ty = sx - self.vx * 2.6, sy - self.vy * 2.6
        pyxel.line(tx, ty, sx, sy, 4)
        pyxel.line(tx, ty, (tx + sx) / 2, (ty + sy) / 2, 9)
        pyxel.pset(sx, sy, 10)


class Spawner:
    def __init__(self, kind, x, y, delay):
        self.kind = kind
        self.x = x
        self.y = y
        self.timer = delay
        self.dead = False

    def update(self, game):
        self.timer -= 1
        if self.timer <= 0:
            game.spawn_enemy(self.kind, self.x, self.y)
            self.dead = True

    def draw(self, cam_x, cam_y, t):
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        if not (-20 < sx < W + 20 and -20 < sy < H + 20):
            return
        pulse = (t // 5) % 2
        r = 9 + pulse * 2
        pyxel.dither(0.6)
        pyxel.circ(sx, sy, r, 8)
        pyxel.dither(1.0)
        pyxel.circb(sx, sy, r, 10)
        pyxel.circb(sx, sy, r + 3, 8)
        pyxel.line(sx - 2, sy, sx + 2, sy, 10)
        pyxel.line(sx, sy - 2, sx, sy + 2, 10)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.fx = 0.0
        self.fy = 1.0
        self.anim_t = 0.0
        self.moving = False
        self.inv = 0
        self.hurt_t = 0
        self.attack_t = 0
        self.attack_cd = 0
        self.attack_fx = 0.0
        self.attack_fy = 1.0
        self.hit_ids = set()
        self.dash_t = 0
        self.dash_cd = 0
        self.dash_x = 0.0
        self.dash_y = 0.0
        self.kx = 0.0
        self.ky = 0.0
        self.dead = False

    # -- update --------------------------------------------------------------
    def update(self, game):
        self.inv = max(0, self.inv - 1)
        self.hurt_t = max(0, self.hurt_t - 1)
        self.attack_cd = max(0, self.attack_cd - 1)
        self.dash_cd = max(0, self.dash_cd - 1)
        if self.dead:
            return

        mx = (1 if any_btn(MOVE_RIGHT) else 0) - (1 if any_btn(MOVE_LEFT) else 0)
        my = (1 if any_btn(MOVE_DOWN) else 0) - (1 if any_btn(MOVE_UP) else 0)
        if mx or my:
            length = math.hypot(mx, my)
            mx, my = mx / length, my / length
            self.fx, self.fy = mx, my
            self.moving = True
        else:
            self.moving = False

        if any_btnp(DASH_KEYS) and self.dash_cd <= 0 and self.attack_t <= 0:
            if mx or my:
                self.dash_x, self.dash_y = mx, my
            else:
                self.dash_x, self.dash_y = self.fx, self.fy
            self.dash_t = DASH_LEN
            self.dash_cd = DASH_CD
            self.inv = max(self.inv, IFRAMES_DASH)
            game.play(3)
            game.burst(
                self.x, self.y + 5, 8, 6, 1.0, 0.06
            )

        if any_btnp(ATTACK_KEYS) and self.attack_t <= 0 and self.attack_cd <= 0 and self.dash_t <= 0:
            self.attack_t = ATTACK_LEN
            self.attack_cd = ATTACK_CD
            self.attack_fx, self.attack_fy = self.fx, self.fy
            self.hit_ids.clear()
            game.play(0)

        if self.dash_t > 0:
            self.dash_t -= 1
            self.x += self.dash_x * DASH_SPEED
            self.y += self.dash_y * DASH_SPEED
            if self.dash_t % 2 == 0:
                game.particles.append(
                    Particle(
                        self.x - self.dash_x * 4 + random.uniform(-3, 3),
                        self.y - self.dash_y * 4 + random.uniform(-2, 2),
                        random.uniform(-0.35, 0.35),
                        random.uniform(-0.25, 0.25),
                        7 if self.dash_t % 4 == 0 else 6,
                        random.randrange(10, 18),
                        1,
                        0.0,
                    )
                )
        else:
            speed = PLAYER_SPEED
            if self.attack_t > 0:
                speed *= 0.4
            if mx or my:
                self.x += mx * speed
                self.y += my * speed
                self.anim_t += speed
                if self.inv <= 0 and self.dash_t <= 0:
                    game.spawn_footstep()

        self.x += self.kx
        self.y += self.ky
        self.kx *= 0.8
        self.ky *= 0.8
        self.x, self.y = clamp_arena(self.x, self.y)

        if self.attack_t > 0:
            self.attack_t -= 1
            if 4 <= self.attack_t <= 11:
                self.resolve_attack(game)

    def resolve_attack(self, game):
        for enemy in game.enemies:
            if enemy.dead or enemy.spawn > 0 or enemy.id in self.hit_ids:
                continue
            dx, dy = enemy.x - self.x, enemy.y - self.y
            dist = math.hypot(dx, dy)
            if dist > ATTACK_RADIUS + enemy.radius * 0.4:
                continue
            dot = (dx * self.attack_fx + dy * self.attack_fy) / max(dist, 0.01)
            if dot < 0.2 and dist > 13:
                continue
            self.hit_ids.add(enemy.id)
            nx, ny = (dx / dist, dy / dist) if dist > 0.01 else (self.attack_fx, self.attack_fy)
            enemy.hurt_by(1, nx, ny, game)
            game.shake = max(game.shake, 2.5)
            game.hitstop = max(game.hitstop, 2)
            game.play(1)

    def hurt(self, damage, src_x, src_y, game):
        if self.inv > 0 or self.dead or self.dash_t > 0:
            return
        self.hp -= damage
        self.hurt_t = 12
        self.inv = IFRAMES_HURT
        dx, dy = self.x - src_x, self.y - src_y
        dist = math.hypot(dx, dy) or 1
        self.kx = dx / dist * 3.2
        self.ky = dy / dist * 3.2
        game.shake = 7
        game.hitstop = 5
        game.play(2)
        game.burst(self.x, self.y, 14, 8, 2.0, 0.05)
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            game.game_over()

    def draw(self, game, cam_x, cam_y):
        if self.dead:
            return
        if self.inv > 0 and self.hurt_t == 0 and (self.inv // 4) % 2 == 0:
            return
        if abs(self.fx) > abs(self.fy) + 0.2:
            view = "side" if self.fx > 0 else "side_l"
        elif self.fy < 0:
            view = "up"
        else:
            view = "down"
        frame = int(self.anim_t // 7) % 2 if self.moving else 0
        lunge = 0.0
        if self.attack_t > 0:
            lunge = math.sin((1 - self.attack_t / ATTACK_LEN) * math.pi) * 2.0
        lx = self.attack_fx * lunge
        ly = self.attack_fy * lunge

        pyxel.dither(0.35)
        pyxel.elli(int(self.x - cam_x) - 6, int(self.y - cam_y) + 5, 12, 5, 0)
        pyxel.dither(1.0)
        game.art.draw_sprite(
            PLAYER_FRAMES[view], frame, self.x + lx, self.y + ly,
            cam_x, cam_y, self.hurt_t > 0,
        )


class Enemy:
    _next_id = 1

    def __init__(self, kind, x, y, wave):
        info = ENEMY_INFO[kind]
        self.kind = kind
        self.x = x
        self.y = y
        self.max_hp = info["hp"]
        if kind == "archer":
            self.max_hp += min(2, wave // 6)
        self.hp = self.max_hp
        self.radius = info["radius"]
        self.speed = info["speed"] + min(0.35, wave * 0.018)
        if kind == "archer":
            self.speed = info["speed"]
        self.score = info["score"]
        self.color = info["color"]
        self.id = Enemy._next_id
        Enemy._next_id += 1
        self.t = random.randrange(120)
        self.phase = random.uniform(0, math.tau)
        self.spawn = 28
        self.hurt_t = 0
        self.frame = 0
        self.kbx = 0.0
        self.kby = 0.0
        self.fire_cd = random.randrange(70, 130)
        self.aim = 0
        self.dead = False

    def update(self, game):
        self.t += 1
        self.hurt_t = max(0, self.hurt_t - 1)
        if self.spawn > 0:
            self.spawn -= 1
        self.x += self.kbx
        self.y += self.kby
        self.kbx *= 0.8
        self.kby *= 0.8

        p = game.player
        dx, dy = p.x - self.x, p.y - self.y
        dist = math.hypot(dx, dy) or 1
        ux, uy = dx / dist, dy / dist

        if self.spawn <= 0:
            if self.kind == "slime":
                cycle = (self.t + int(self.phase * 10)) % 64
                if cycle < 42:
                    wobble = math.sin(self.t * 0.18) * 0.32
                    mx, my = ux - uy * wobble, uy + ux * wobble
                    norm = math.hypot(mx, my) or 1
                    self.x += mx / norm * self.speed
                    self.y += my / norm * self.speed
                self.frame = 0 if cycle < 34 else 1
            elif self.kind == "bat":
                wobble = math.sin(self.t * 0.2 + self.phase)
                mx, my = ux - uy * wobble * 0.8, uy + ux * wobble * 0.8
                norm = math.hypot(mx, my) or 1
                speed = self.speed * (1.0 + 0.22 * math.sin(self.t * 0.14))
                self.x += mx / norm * speed
                self.y += my / norm * speed
                self.frame = (self.t // 6) % 2
            else:
                self.update_archer(game, dist, ux, uy)
            if dist < self.radius + 8:
                p.hurt(1, self.x, self.y, game)

        self.x, self.y = clamp_arena(self.x, self.y)

    def update_archer(self, game, dist, ux, uy):
        if self.aim > 0:
            self.aim -= 1
            if self.aim == 0:
                p = game.player
                tx, ty = p.x - self.x, p.y - self.y
                length = math.hypot(tx, ty) or 1
                game.arrows.append(
                    Arrow(self.x, self.y - 3, tx / length * 2.35, ty / length * 2.35)
                )
                self.fire_cd = random.randrange(95, 150)
                game.play(8)
        else:
            self.fire_cd -= 1
            if self.fire_cd <= 0 and dist < 230:
                self.aim = 34
            strafe = 1.0 if self.id % 2 == 0 else -1.0
            if dist < 76:
                mx, my = -ux, -uy
            elif dist > 136:
                mx, my = ux, uy
            else:
                mx, my = -uy * strafe, ux * strafe
            self.x += mx * self.speed
            self.y += my * self.speed
        self.frame = (self.t // 12) % 2

    def hurt_by(self, damage, dir_x, dir_y, game):
        if self.dead or self.spawn > 0:
            return
        self.hp -= damage
        self.hurt_t = 5
        force = 1.1 if self.kind == "archer" else 2.2
        self.kbx += dir_x * force
        self.kby += dir_y * force
        game.burst(self.x, self.y, 6, self.color, 1.6, 0.04)
        if self.hp <= 0:
            self.die(game)

    def die(self, game):
        self.dead = True
        game.score += self.score
        game.kills += 1
        game.since_heart += 1
        game.burst(self.x, self.y, 14, self.color, 2.2, 0.06)
        game.burst(self.x, self.y, 6, 7, 1.4, 0.02)
        game.floaters.append(Floater(self.x, self.y - 10, f"+{self.score}", 10))
        game.play(6)
        if game.since_heart >= 9 or random.random() < 0.14:
            game.since_heart = 0
            game.hearts.append(HeartPickup(self.x, self.y))
        if self.kind == "archer":
            game.shake = max(game.shake, 2)

    def draw(self, game, cam_x, cam_y):
        if self.spawn > 0 and (self.spawn // 4) % 2 == 1:
            sx = int(self.x - cam_x)
            sy = int(self.y - cam_y)
            pyxel.circb(sx, sy, 11, 10)
        pyxel.dither(0.3)
        pyxel.elli(int(self.x - cam_x) - 6, int(self.y - cam_y) + 4, 12, 5, 0)
        pyxel.dither(1.0)
        frames = ENEMY_FRAMES[self.kind]
        bob = int(math.sin(self.t * 0.11) * 1.5) if self.kind == "archer" else 0
        game.art.draw_sprite(
            frames, self.frame, self.x, self.y + bob, cam_x, cam_y,
            self.hurt_t > 0,
        )
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        if self.aim > 0:
            p = game.player
            dx, dy = p.x - self.x, p.y - self.y
            length = math.hypot(dx, dy) or 1
            pyxel.dither(0.5)
            pyxel.line(sx, sy - 2, sx + dx / length * 26, sy - 2 + dy / length * 26, 8)
            pyxel.dither(1.0)
            pyxel.circ(sx, sy - 2, 1 + (self.aim < 10), 8)
        if self.max_hp > 2 and self.hp < self.max_hp:
            for i in range(self.max_hp):
                col = 8 if i < self.hp else 5
                pyxel.rect(sx - self.max_hp * 2 + i * 4, sy - 14, 2, 2, col)


class Game:
    def __init__(self):
        self.art = Art()
        self.frame = 0
        self.high_score = load_high_score()
        self.state = STATE_TITLE
        self.player = Player(ARENA_W / 2, ARENA_H / 2)
        self.enemies = []
        self.spawners = []
        self.arrows = []
        self.hearts = []
        self.particles = []
        self.floaters = []
        self.score = 0
        self.kills = 0
        self.since_heart = 0
        self.wave = 0
        self.phase = "idle"
        self.banner_timer = 0
        self.clear_timer = 0
        self.bonus = 0
        self.cam_x = ARENA_W / 2 - W / 2
        self.cam_y = ARENA_H / 2 - H / 2
        self.shake = 0.0
        self.hitstop = 0
        self.over_hold = 0
        self.new_best = False
        self.footstep_cd = 0
        self._setup_sounds()
        pyxel.mouse(False)

    # -- audio -------------------------------------------------------------
    def _setup_sounds(self):
        s = pyxel.sounds
        s[0].set("c4", "n", "4", "f", 6)          # slash
        s[1].set("c2g2", "s", "5", "f", 8)        # sword hit
        s[2].set("g2c2", "n", "6", "f", 14)       # player hurt
        s[3].set("c3", "n", "4", "f", 4)          # dash
        s[4].set("e3g3c4", "s", "5", "n", 7)      # pickup / heal
        s[5].set("c3e3g3c4", "s", "5", "n", 10)   # wave start
        s[6].set("c3g2c2", "s", "5", "f", 8)      # enemy down
        s[7].set("c3g2e2c2", "t", "6", "f", 18)   # game over
        s[8].set("g3c3", "p", "4", "f", 6)        # arrow shot

    def play(self, index):
        channel = {0: 0, 1: 0, 6: 0, 2: 1, 3: 1, 8: 1, 4: 2, 5: 2, 7: 3}[index]
        pyxel.play(channel, index)

    # -- flow --------------------------------------------------------------
    def start_game(self):
        self.player = Player(ARENA_W / 2, ARENA_H / 2)
        self.enemies = []
        self.spawners = []
        self.arrows = []
        self.hearts = []
        self.particles = []
        self.floaters = []
        self.score = 0
        self.kills = 0
        self.since_heart = 0
        self.wave = 0
        self.phase = "idle"
        self.shake = 0.0
        self.hitstop = 0
        self.new_best = False
        self.cam_x = clamp(self.player.x - W / 2, 0, ARENA_W - W)
        self.cam_y = clamp(self.player.y - H / 2, 0, ARENA_H - H)
        self.state = STATE_PLAY
        self.start_wave(1)

    def start_wave(self, wave):
        self.wave = wave
        self.phase = "banner"
        self.banner_timer = 80
        self.spawners = []
        self.play(5)

    def game_over(self):
        self.state = STATE_OVER
        self.over_hold = 30
        self.shake = 9
        self.burst(self.player.x, self.player.y, 26, 8, 2.6, 0.07)
        self.burst(self.player.x, self.player.y, 10, 10, 1.8, 0.04)
        self.play(7)
        if self.score > self.high_score:
            self.high_score = self.score
            self.new_best = True
            save_high_score(self.high_score)

    # -- helpers -----------------------------------------------------------
    def burst(self, x, y, count, col, speed=1.8, grav=0.04):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            mag = random.uniform(0.3, speed)
            self.particles.append(
                Particle(
                    x + random.uniform(-2, 2),
                    y + random.uniform(-2, 2),
                    math.cos(angle) * mag,
                    math.sin(angle) * mag - 0.4,
                    col if random.random() < 0.7 else 7,
                    random.randrange(16, 34),
                    2 if random.random() < 0.25 else 1,
                    grav,
                )
            )
        if len(self.particles) > 320:
            self.particles = self.particles[-320:]

    def spawn_footstep(self):
        self.footstep_cd -= 1
        if self.footstep_cd <= 0:
            self.footstep_cd = 10
            self.particles.append(
                Particle(
                    self.player.x + random.uniform(-3, 3),
                    self.player.y + 7,
                    random.uniform(-0.2, 0.2),
                    -random.uniform(0.05, 0.2),
                    7,
                    random.randrange(8, 14),
                    1,
                    0.0,
                )
            )

    def spawn_enemy(self, kind, x, y):
        self.enemies.append(Enemy(kind, x, y, self.wave))
        self.burst(x, y, 10, ENEMY_INFO[kind]["color"], 1.6, 0.04)

    def _spawn_position(self):
        p = self.player
        for _ in range(40):
            side = random.randrange(4)
            if side == 0:
                x, y = random.uniform(42, ARENA_W - 42), 44
            elif side == 1:
                x, y = random.uniform(42, ARENA_W - 42), ARENA_H - 50
            elif side == 2:
                x, y = 44, random.uniform(42, ARENA_H - 42)
            else:
                x, y = ARENA_W - 48, random.uniform(42, ARENA_H - 42)
            if math.hypot(x - p.x, y - p.y) > 110:
                return x, y
        return x, y

    def build_spawners(self):
        wave = self.wave
        slimes = min(3 + wave, 12)
        bats = 0 if wave < 2 else min(wave, 6)
        archers = 0 if wave < 3 else min((wave - 1) // 2, 4)
        kinds = ["slime"] * slimes + ["bat"] * bats + ["archer"] * archers
        random.shuffle(kinds)
        kinds.sort(key=lambda k: k != "archer")
        for i, kind in enumerate(kinds):
            x, y = self._spawn_position()
            self.spawners.append(Spawner(kind, x, y, 30 + i * 17))

    def separate_enemies(self):
        for i, a in enumerate(self.enemies):
            if a.dead:
                continue
            for b in self.enemies[i + 1:]:
                if b.dead:
                    continue
                dx, dy = b.x - a.x, b.y - a.y
                d2 = dx * dx + dy * dy
                min_d = (a.radius + b.radius) * 0.85
                if 0.01 < d2 < min_d * min_d:
                    dist = math.sqrt(d2)
                    push = (min_d - dist) * 0.5
                    nx, ny = dx / dist, dy / dist
                    a.x -= nx * push
                    a.y -= ny * push
                    b.x += nx * push
                    b.y += ny * push
        for e in self.enemies:
            e.x, e.y = clamp_arena(e.x, e.y)

    # -- update ------------------------------------------------------------
    def update(self):
        self.frame += 1
        self.art.update_fireflies(self.frame)

        if self.state == STATE_TITLE:
            if any_btnp(START_KEYS):
                self.start_game()
            return
        if self.state == STATE_PAUSE:
            if pyxel.btnp(pyxel.KEY_P):
                self.state = STATE_PLAY
            return
        if self.state == STATE_OVER:
            self.update_particles()
            if self.over_hold > 0:
                self.over_hold -= 1
            elif any_btnp(START_KEYS):
                self.start_game()
            return

        if pyxel.btnp(pyxel.KEY_P):
            self.state = STATE_PAUSE
            return
        self.update_world()

    def update_world(self):
        if self.hitstop > 0:
            self.hitstop -= 1
            self.update_particles()
            return

        self.player.update(self)
        if self.state != STATE_PLAY:
            return

        for enemy in self.enemies:
            enemy.update(self)
            if self.state != STATE_PLAY:
                return
        self.enemies = [e for e in self.enemies if not e.dead]
        self.separate_enemies()

        for spawner in self.spawners:
            spawner.update(self)
        self.spawners = [s for s in self.spawners if not s.dead]

        for arrow in self.arrows:
            arrow.update(self)
            if self.state != STATE_PLAY:
                return
        self.arrows = [a for a in self.arrows if not a.dead]

        for heart in self.hearts:
            heart.update(self)
        self.hearts = [h for h in self.hearts if not h.dead]

        self.update_particles()
        self.update_wave()
        self.update_camera()
        self.shake = max(0.0, self.shake - 0.35)

    def update_particles(self):
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]
        for floater in self.floaters:
            floater.update()
        self.floaters = [f for f in self.floaters if f.life > 0]

    def update_wave(self):
        if self.phase == "banner":
            self.banner_timer -= 1
            if self.banner_timer <= 0:
                self.build_spawners()
                self.phase = "fight"
        elif self.phase == "fight":
            if not self.enemies and not self.spawners:
                self.phase = "clear"
                self.clear_timer = 110
                self.bonus = 25 * self.wave
                self.score += self.bonus
                self.play(5)
                if self.player.hp < self.player.max_hp and self.wave % 2 == 0:
                    self.player.hp += 1
                    self.floaters.append(
                        Floater(self.player.x, self.player.y - 20, "+1 HP", 14)
                    )
        elif self.phase == "clear":
            self.clear_timer -= 1
            if self.clear_timer <= 0:
                self.start_wave(self.wave + 1)

    def update_camera(self):
        target_x = clamp(self.player.x - W / 2, 0, ARENA_W - W)
        target_y = clamp(self.player.y - H / 2, 0, ARENA_H - H)
        self.cam_x += (target_x - self.cam_x) * 0.12
        self.cam_y += (target_y - self.cam_y) * 0.12

    # -- drawing -----------------------------------------------------------
    def draw(self):
        if self.state == STATE_TITLE:
            self.draw_title()
            return

        shake_x = int(math.sin(self.frame * 2.3) * self.shake * 0.7)
        shake_y = int(math.cos(self.frame * 1.7) * self.shake * 0.7)
        cam_x = clamp(int(self.cam_x) + shake_x, 0, ARENA_W - W)
        cam_y = clamp(int(self.cam_y) + shake_y, 0, ARENA_H - H)

        self.art.draw_floor(cam_x, cam_y)
        self.art.draw_glows(cam_x, cam_y, self.frame)
        self.art.draw_fireflies(cam_x, cam_y, self.frame)

        for spawner in self.spawners:
            spawner.draw(cam_x, cam_y, self.frame)

        drawables = []
        for index, (kind, x, y) in enumerate(self.art.props):
            if -24 < x - cam_x < W + 24 and -32 < y - cam_y < H + 32:
                drawables.append((y, 0, kind, x, y, index))
        for index, (x, y) in enumerate(self.art.torches):
            if -24 < x - cam_x < W + 24 and -32 < y - cam_y < H + 32:
                drawables.append((y, 0, "torch", x, y, index))
        for enemy in self.enemies:
            if -24 < enemy.x - cam_x < W + 24 and -24 < enemy.y - cam_y < H + 24:
                drawables.append((enemy.y, 1, enemy))
        for heart in self.hearts:
            if -16 < heart.x - cam_x < W + 16 and -16 < heart.y - cam_y < H + 16:
                drawables.append((heart.y, 2, heart))
        drawables.append((self.player.y, 3, self.player))
        drawables.sort(key=lambda item: item[0])

        for item in drawables:
            if item[1] == 0:
                _, _, kind, x, y, index = item
                self.art.draw_prop(kind, x, y, cam_x, cam_y, self.frame, index)
            elif item[1] == 1:
                item[2].draw(self, cam_x, cam_y)
            elif item[1] == 2:
                item[2].draw(self, cam_x, cam_y)
            else:
                item[2].draw(self, cam_x, cam_y)

        for arrow in self.arrows:
            arrow.draw(cam_x, cam_y)
        for particle in self.particles:
            particle.draw(cam_x, cam_y)
        for floater in self.floaters:
            floater.draw(cam_x, cam_y)

        self.draw_attack(cam_x, cam_y)
        self.draw_hud()
        self.draw_wave_banner()

        if self.state == STATE_PAUSE:
            self.draw_pause()
        elif self.state == STATE_OVER:
            self.draw_over()

    def draw_attack(self, cam_x, cam_y):
        p = self.player
        if p.attack_t <= 0 or p.dead:
            return
        progress = 1 - p.attack_t / ATTACK_LEN
        base = math.atan2(p.attack_fy, p.attack_fx)
        sweep = -1.2 + 2.4 * clamp(progress * 1.3, 0, 1)
        px, py = p.x - cam_x, p.y - cam_y

        pyxel.dither(0.22)
        for i in range(6):
            a1 = base + sweep - i * 0.095
            a2 = a1 - 0.095
            pyxel.tri(
                px, py,
                px + math.cos(a1) * 31, py + math.sin(a1) * 31,
                px + math.cos(a2) * 31, py + math.sin(a2) * 31,
                6,
            )
        pyxel.dither(1.0)

        for i in range(9):
            angle = base + sweep - i * 0.08
            r1 = 16 + i * 0.6
            r2 = 28 - i * 0.5
            col = 12 if i < 3 else 7
            pyxel.line(
                px + math.cos(angle) * r1, py + math.sin(angle) * r1,
                px + math.cos(angle) * r2, py + math.sin(angle) * r2,
                col,
            )
        tip_x = px + math.cos(base + sweep) * 29
        tip_y = py + math.sin(base + sweep) * 29
        pyxel.circ(int(tip_x), int(tip_y), 2, 10)
        pyxel.circ(int(tip_x), int(tip_y), 1, 7)

    def draw_hud(self):
        pyxel.dither(0.78)
        pyxel.rect(0, 0, W, 14, 0)
        pyxel.dither(1.0)
        pyxel.line(0, 14, W - 1, 14, 5)

        for i in range(self.player.max_hp):
            key = "heart" if i < self.player.hp else "heart_empty"
            u, v, w, h = UI_SPRITES[key]
            pyxel.blt(6 + i * 9, 3, self.art.img, u, v, w, h, 0)

        score_text = f"{self.score:06d}"
        pyxel.text(W - 6 - small_width(score_text), 4, score_text, 7)

        wave_text = f"WAVE {self.wave}"
        pyxel.text((W - small_width(wave_text)) // 2, 4, wave_text, 10)

        bx, by = 6, H - 9
        pyxel.text(bx, H - 16, "DASH", 6)
        pyxel.rect(bx, by, 26, 4, 1)
        if self.player.dash_cd <= 0:
            fill = 24
            col = 12
        else:
            fill = int(24 * (1 - self.player.dash_cd / DASH_CD))
            col = 6
        if fill > 0:
            pyxel.rect(bx + 1, by + 1, fill, 2, col)

        if self.player.hp <= 2:
            pyxel.dither(0.2)
            pyxel.rect(0, 0, W, 4, 8)
            pyxel.rect(0, H - 4, W, 4, 8)
            pyxel.rect(0, 0, 4, H, 8)
            pyxel.rect(W - 4, 0, 4, H, 8)
            pyxel.dither(1.0)

    def draw_wave_banner(self):
        if self.phase == "banner":
            if self.banner_timer > 24 or (self.banner_timer // 4) % 2 == 0:
                draw_panel(34, 66, W - 68, 38, 5)
                draw_big_center(70, f"WAVE {self.wave}", 10, 3)
                draw_text_center(94, "GET READY", 7)
        elif self.phase == "clear":
            if self.clear_timer > 22 or (self.clear_timer // 4) % 2 == 0:
                draw_panel(24, 66, W - 48, 38, 5)
                draw_big_center(70, "WAVE CLEAR", 11, 3)
                draw_text_center(94, f"+{self.bonus} BONUS", 10)

    # -- full-screen states ------------------------------------------------
    def draw_title(self):
        t = self.frame
        cam_x = int(clamp(
            ARENA_W / 2 - W / 2 + math.sin(t * 0.006) * 52, 0, ARENA_W - W
        ))
        cam_y = int(clamp(
            ARENA_H / 2 - H / 2 + math.cos(t * 0.0045) * 24, 0, ARENA_H - H
        ))
        self.art.draw_floor(cam_x, cam_y)
        self.art.draw_glows(cam_x, cam_y, t)
        self.art.draw_fireflies(cam_x, cam_y, t)
        for kind, x, y in self.art.props[:12]:
            self.art.draw_prop(kind, x, y, cam_x, cam_y, t, 0)
        pyxel.dither(0.4)
        pyxel.rect(0, 0, W, H, 0)
        pyxel.dither(1.0)

        bob = int(math.sin(t * 0.045) * 2)
        pyxel.dither(0.45)
        pyxel.elli(104, 142 + bob, 36, 8, 1)
        pyxel.dither(1.0)
        pyxel.blt(104, 92 + bob, self.art.img, 0, 0, 16, 16, 0, scale=3)
        pyxel.blt(54, 116 + int(math.sin(t * 0.06) * 2), self.art.img, 0, 16, 16, 16, 0, scale=2)
        pyxel.blt(172, 112 + int(math.cos(t * 0.05) * 2), self.art.img, 32, 16, 16, 16, 0, scale=2)

        draw_panel(16, 10, W - 32, 62, 5)
        draw_big_center(16, "TINY KNIGHT", 10, 4)
        draw_text_center(48, "SURVIVE THE WAVES", 11)

        draw_panel(52, 158, W - 104, 14, 5)
        if (t // 30) % 2 == 0 or (t // 8) % 2 == 0:
            draw_text_center(162, "PRESS SPACE TO START", 7)
        draw_panel(36, 176, W - 72, 40, 5)
        draw_text_center(182, "WASD MOVE   SPACE ATTACK   SHIFT DASH", 7)
        draw_text_center(194, f"HIGH SCORE  {self.high_score:06d}", 10)
        draw_text_center(206, "MADE WITH PYXEL", 6)

    def draw_pause(self):
        pyxel.dither(0.55)
        pyxel.rect(0, 0, W, H, 0)
        pyxel.dither(1.0)
        draw_panel(44, 62, W - 88, 96, 5)
        draw_big_center(72, "PAUSED", 10, 3)
        draw_text_center(102, "PRESS P TO RESUME", 7)
        draw_text_center(122, "WASD MOVE   SPACE ATTACK", 6)
        draw_text_center(134, "SHIFT DASH", 6)

    def draw_over(self):
        pyxel.dither(0.55)
        pyxel.rect(0, 0, W, H, 0)
        pyxel.dither(1.0)
        draw_panel(28, 36, W - 56, 138, 8)
        draw_big_center(48, "GAME OVER", 8, 4)
        draw_text_center(82, f"SCORE  {self.score:06d}", 7)
        draw_text_center(94, f"WAVE   {self.wave}", 7)
        draw_text_center(108, f"BEST   {self.high_score:06d}", 10)
        if self.new_best:
            draw_text_center(120, "NEW BEST!", 10)
        if (self.frame // 30) % 2 == 0:
            draw_text_center(142, "PRESS SPACE TO RETRY", 10)
        draw_text_center(158, f"ENEMIES DEFEATED  {self.kills}", 13)

def main():
    pyxel.init(
        W,
        H,
        title="Tiny Knight",
        fps=60,
        display_scale=3,
        quit_key=pyxel.KEY_ESCAPE,
    )
    game = Game()
    pyxel.run(game.update, game.draw)


if __name__ == "__main__":
    main()
