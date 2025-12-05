"""
Pyxel auto-Puyo (pair fall) — launcher-compatible module

This file is written so the Pyxel Web Launcher can import the module and start the app.
It exposes a run() function and also starts automatically when the module is imported,
so the launcher can simply import mo256man.pyxel_demo.web_game.

Notes:
- Screen: 256x256
- View-only automatic simulation (no player input required)
- Pairs (2-block pieces) fall either horizontally or vertically
- No external assets
"""

import random
import pyxel

# Grid / game settings
W = 16
H = 16
OWANIMO = 4   # 消える個数閾値
COLORS = 4    # 色数 (1..COLORS)

SCREEN_W = 256
SCREEN_H = 256

# Layout / rendering
MARGIN = 16
CELL = min((SCREEN_W - MARGIN * 2) // W, (SCREEN_H - MARGIN * 2) // H)
GRID_W_PIX = CELL * W
GRID_H_PIX = CELL * H
GRID_X = (SCREEN_W - GRID_W_PIX) // 2
GRID_Y = (SCREEN_H - GRID_H_PIX) // 2

# Timing (frames)
DROP_INTERVAL = 6
ERASE_ANIM_FRAMES = 18
GEN_WAIT_FRAMES = 4

# Pyxel color mapping (tweak as necessary)
COLOR_MAP = {
    1: 11,
    2: 9,
    3: 10,
    4: 12,
}
BG_COLOR = 0

class Pair:
    def __init__(self, r, c, orientation, col_a, col_b):
        self.r = r
        self.c = c
        self.orientation = orientation  # 'H' or 'V'
        self.col_a = col_a
        self.col_b = col_b

    def positions(self):
        if self.orientation == 'H':
            return [(self.r, self.c), (self.r, self.c + 1)]
        else:
            return [(self.r, self.c), (self.r + 1, self.c)]

class Field:
    def __init__(self):
        self.clear()
        self.is_generate = True
        self.rensa = 0
        self.drop_timer = 0
        self.gen_wait = 0
        self.erase_anim_timer = 0
        self.to_clear = []
        self.current_pair = None

    def clear(self):
        self.matrix = [[0] * W for _ in range(H)]

    def can_place_pair(self, orientation, c):
        if orientation == 'H':
            if c < 0 or c >= W - 1:
                return False
            return self.matrix[0][c] == 0 and self.matrix[0][c + 1] == 0
        else:
            if c < 0 or c >= W:
                return False
            return self.matrix[0][c] == 0 and self.matrix[1][c] == 0

    def generate_drop(self):
        orientations = ['H', 'V']
        random.shuffle(orientations)
        placed = False

        for ori in orientations:
            if ori == 'H':
                candidates = [c for c in range(W - 1) if self.can_place_pair('H', c)]
            else:
                candidates = [c for c in range(W) if self.can_place_pair('V', c)]
            if candidates:
                c = random.choice(candidates)
                col_a = random.randint(1, COLORS)
                col_b = random.randint(1, COLORS)
                if ori == 'H':
                    p = Pair(0, c, 'H', col_a, col_b)
                else:
                    p = Pair(0, c, 'V', col_a, col_b)
                self.current_pair = p
                self.is_generate = False
                self.gen_wait = GEN_WAIT_FRAMES
                placed = True
                self.rensa = 0
                break

        if not placed:
            self.erase_one_color()
            self.is_generate = False
            self.gen_wait = GEN_WAIT_FRAMES
            self.rensa = 0

    def pair_can_move_down(self):
        if self.current_pair is None:
            return False
        for (r, c) in self.current_pair.positions():
            nr = r + 1
            if nr >= H:
                return False
            if self.matrix[nr][c] != 0:
                return False
        return True

    def lock_current_pair(self):
        if self.current_pair is None:
            return
        pos = self.current_pair.positions()
        cols = [self.current_pair.col_a, self.current_pair.col_b]
        for (r, c), col in zip(pos, cols):
            if not (0 <= r < H and 0 <= c < W):
                self.clear()
                self.current_pair = None
                self.is_generate = True
                return
            self.matrix[r][c] = col
        self.current_pair = None

    def drop_step(self):
        moved = False
        if self.current_pair is not None:
            if self.pair_can_move_down():
                self.current_pair.r += 1
                moved = True
            else:
                self.lock_current_pair()
                moved = True
            return moved

        for r in range(H - 2, -1, -1):
            for c in range(W):
                if self.matrix[r][c] != 0 and self.matrix[r + 1][c] == 0:
                    self.matrix[r + 1][c] = self.matrix[r][c]
                    self.matrix[r][c] = 0
                    moved = True
        return moved

    def erase(self):
        checked = [[False] * W for _ in range(H)]
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        found_groups = []

        def bfs(sr, sc, val):
            queue = [(sr, sc)]
            group = [(sr, sc)]
            checked[sr][sc] = True
            qi = 0
            while qi < len(queue):
                x, y = queue[qi]; qi += 1
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < H and 0 <= ny < W and not checked[nx][ny] and self.matrix[nx][ny] == val:
                        checked[nx][ny] = True
                        queue.append((nx, ny))
                        group.append((nx, ny))
            return group

        is_erase = False
        for r in range(H):
            for c in range(W):
                if self.matrix[r][c] != 0 and self.matrix[r][c] != -1 and not checked[r][c]:
                    group = bfs(r, c, self.matrix[r][c])
                    if len(group) >= OWANIMO:
                        found_groups.append(group)
                        is_erase = True

        if is_erase:
            self.to_clear = []
            for group in found_groups:
                for r,c in group:
                    self.matrix[r][c] = -1
                    self.to_clear.append((r,c))
            self.erase_anim_timer = ERASE_ANIM_FRAMES

        return is_erase

    def erase_one_color(self):
        color = random.randint(1, COLORS)
        for r in range(H):
            for c in range(W):
                if self.matrix[r][c] == color:
                    self.matrix[r][c] = 0

    def update(self):
        # erase animation
        if self.erase_anim_timer > 0:
            self.erase_anim_timer -= 1
            if self.erase_anim_timer == 0:
                for (r,c) in self.to_clear:
                    self.matrix[r][c] = 0
                self.to_clear = []
            return

        if self.gen_wait > 0:
            self.gen_wait -= 1
            if self.gen_wait > 0:
                return

        if self.is_generate and self.current_pair is None:
            self.generate_drop()
            return

        self.drop_timer += 1
        if self.drop_timer >= DROP_INTERVAL:
            self.drop_timer = 0
            moved = self.drop_step()
            if not moved:
                erased = self.erase()
                if erased:
                    self.rensa += 1
                else:
                    self.is_generate = True

    def draw(self):
        for r in range(H):
            for c in range(W):
                x = GRID_X + c * CELL
                y = GRID_Y + r * CELL
                val = self.matrix[r][c]
                if val == 0:
                    pyxel.rect(x, y, CELL, CELL, BG_COLOR)
                    pyxel.rectb(x, y, CELL, CELL, 1)
                elif val == -1:
                    col = 7 if (pyxel.frame_count // 3) % 2 == 0 else 8
                    pyxel.rect(x+1, y+1, CELL-2, CELL-2, col)
                else:
                    col = COLOR_MAP.get(val, 11)
                    pyxel.rect(x+1, y+1, CELL-2, CELL-2, col)
                    pyxel.rectb(x, y, CELL, CELL, 7)

        # draw dropping pair on top
        if self.current_pair is not None:
            pos = self.current_pair.positions()
            cols = [self.current_pair.col_a, self.current_pair.col_b]
            for (r, c), col in zip(pos, cols):
                if not (0 <= r < H and 0 <= c < W):
                    continue
                x = GRID_X + c * CELL
                y = GRID_Y + r * CELL
                colidx = COLOR_MAP.get(col, 11)
                pyxel.rect(x+1, y+1, CELL-2, CELL-2, colidx)
                pyxel.rectb(x, y, CELL, CELL, 7)

class App:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, caption="pyxel_demo - auto puyo (pair fall)")
        self.field = Field()
        random.seed()
        pyxel.run(self.update, self.draw)

    def update(self):
        # allow quit locally
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        self.field.update()

    def draw(self):
        pyxel.cls(BG_COLOR)
        pyxel.rect(GRID_X-2, GRID_Y-2, GRID_W_PIX+4, GRID_H_PIX+4, 1)
        self.field.draw()
        if self.field.rensa > 0:
            txt = f"{self.field.rensa} 連鎖 {'!' * min(self.field.rensa, 6)}"
            pyxel.text(8, 8, txt, 7)
        else:
            pyxel.text(8, 8, "見るだけ Puyo (自動再生)", 7)
        pyxel.text(8, 18, "操作: なし（表示専用）", 7)
        pyxel.text(8, 28, "Q/Esc で終了(ローカル実行時)", 7)

def run():
    """Start the App. Exported so launcher or other code can call explicitly."""
    App()

# Start automatically on import so Pyxel Web Launcher (which imports the module) runs it.
# Also makes `python web_game.py` work.
run()
