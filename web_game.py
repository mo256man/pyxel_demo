"""
Pyxel に移植した自動再生の「ぷよぷよ」表示（単一ファイル）
- 非操作（見るだけ）
- 2個1組（ペア）で落ちてくる仕様
- ペアは横並びまたは縦並びでランダムに生成される
- 画面: 256x256 / グリッド: 16x16（元コードに合わせる）

起動:
    python web_game.py
または Pyxel Web Launcher:
    https://kitao.github.io/pyxel/wasm/launcher/?run=mo256man.pyxel_demo.web_game
"""

import random
import pyxel

# 元コードに合わせたサイズ / 設定
W = 16
H = 16
OWANIMO = 4   # 何個揃ったら消えるか（元は 4）
COLORS = 4    # 色数 (1..COLORS)

SCREEN_W = 256
SCREEN_H = 256

# 見た目の設定
MARGIN = 16
# セルサイズは画面にフィットするように自動計算
CELL = min((SCREEN_W - MARGIN * 2) // W, (SCREEN_H - MARGIN * 2) // H)
GRID_W_PIX = CELL * W
GRID_H_PIX = CELL * H
GRID_X = (SCREEN_W - GRID_W_PIX) // 2
GRID_Y = (SCREEN_H - GRID_H_PIX) // 2

# タイミング（フレーム数）
DROP_INTERVAL = 6         # 落下判定を行う間隔（フレーム）: 小さいほど速い
ERASE_ANIM_FRAMES = 18    # 消去演出のフレーム長
GEN_WAIT_FRAMES = 4       # 生成後に次の落下判定までの待ち（視認性向上）

# 色マッピング（pyxelカラーインデックス）
COLOR_MAP = {
    1: 11,  # yellow-like
    2: 9,   # red-like
    3: 10,  # green-like
    4: 12,  # blue-like
}
BG_COLOR = 0
GROUND_COLOR = 3

class Pair:
    """
    落下中の2個組（ペア）を表す簡易クラス。
    - orientation: 'H' (horizontal, same row, columns c and c+1)
                   'V' (vertical, same column, rows r and r+1)
    - r, c: top-left coordinate (for H it's row, left column; for V it's top row and column)
    - col_a, col_b: 色（1..COLORS）
    """
    def __init__(self, r, c, orientation, col_a, col_b):
        self.r = r
        self.c = c
        self.orientation = orientation
        self.col_a = col_a
        self.col_b = col_b

    def positions(self):
        if self.orientation == 'H':
            return [(self.r, self.c), (self.r, self.c + 1)]
        else:  # 'V'
            return [(self.r, self.c), (self.r + 1, self.c)]

class Field:
    def __init__(self):
        self.clear()
        self.is_generate = True
        self.rensa = 0
        # internal timers & state
        self.drop_timer = 0
        self.gen_wait = 0
        self.erase_anim_timer = 0
        self.to_clear = []  # positions to clear after erase animation
        self.current_pair = None  # Pair instance while dropping

    def clear(self):
        self.matrix = [[0] * W for _ in range(H)]

    def can_place_pair(self, orientation, c):
        """
        orientation 'H' expects to place at row 0, cols c and c+1 (c in 0..W-2)
        orientation 'V' expects to place at row 0 and 1, col c (c in 0..W-1)
        """
        if orientation == 'H':
            if c < 0 or c >= W - 1:
                return False
            return self.matrix[0][c] == 0 and self.matrix[0][c + 1] == 0
        else:  # V
            if c < 0 or c >= W:
                return False
            return self.matrix[0][c] == 0 and self.matrix[1][c] == 0

    def generate_drop(self):
        # Try to place a pair (horizontal or vertical) in a random valid spot.
        # If no valid spot exists for either orientation, perform erase_one_color().
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
                # colors for the two puyos (can be same)
                col_a = random.randint(1, COLORS)
                col_b = random.randint(1, COLORS)
                # spawn at top row(s)
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
            # Can't place any pair: clear one color as per original behavior
            self.erase_one_color()
            self.is_generate = False
            self.gen_wait = GEN_WAIT_FRAMES
            self.rensa = 0

    def pair_can_move_down(self):
        """
        Check whether the current_pair can move down by 1 as a unit.
        The pair stops if any block would collide with non-zero cell or exceed bottom.
        """
        if self.current_pair is None:
            return False
        for (r, c) in self.current_pair.positions():
            nr = r + 1
            nc = c
            # If exceeding bottom -> cannot move
            if nr >= H:
                return False
            # If cell below is occupied by something other than part of the pair at its current positions,
            # then cannot move. Because pair moves as unit, we should check target positions are empty
            # or currently occupied by the pair itself (which won't happen because pair isn't in matrix).
            if self.matrix[nr][nc] != 0:
                return False
        return True

    def lock_current_pair(self):
        """
        Place the current_pair into the matrix (freeze in place).
        """
        if self.current_pair is None:
            return
        pos = self.current_pair.positions()
        cols = [self.current_pair.col_a, self.current_pair.col_b]
        for (r, c), col in zip(pos, cols):
            # If out-of-bounds (spawned partly above screen), then this is game-over-like; just clear board
            if not (0 <= r < H and 0 <= c < W):
                # fallback: clear the field (consistent with original gameover behavior)
                self.clear()
                self.current_pair = None
                self.is_generate = True
                return
            self.matrix[r][c] = col
        self.current_pair = None

    def drop_step(self):
        """
        If there is a current_pair, attempt to move it down as a unit.
        Otherwise, perform single-cell drop (existing floating blocks falling) like original.
        Returns True if anything moved.
        """
        moved = False
        if self.current_pair is not None:
            if self.pair_can_move_down():
                # move pair down by incrementing r
                self.current_pair.r += 1
                moved = True
            else:
                # can't move: lock pair into matrix
                self.lock_current_pair()
                moved = True  # locking is a state change; treat as movement to trigger erase checks next
            return moved

        # No active pair: fall existing single cells by one row where possible
        # Iterate from bottom-2 up to 0, move downward if below empty.
        for r in range(H - 2, -1, -1):
            for c in range(W):
                if self.matrix[r][c] != 0 and self.matrix[r + 1][c] == 0:
                    self.matrix[r + 1][c] = self.matrix[r][c]
                    self.matrix[r][c] = 0
                    moved = True
        return moved

    def erase(self):
        # BFS でグループを見つけ、OWANIMO 以上なら消える（-1 でマーク）
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
            # mark for animation
            self.to_clear = []
            for group in found_groups:
                for r,c in group:
                    # mark as -1 for erase animation
                    self.matrix[r][c] = -1
                    self.to_clear.append((r,c))
            self.erase_anim_timer = ERASE_ANIM_FRAMES

        return is_erase

    def erase_one_color(self):
        # ランダムに1色を選んで消す
        color = random.randint(1, COLORS)
        for r in range(H):
            for c in range(W):
                if self.matrix[r][c] == color:
                    self.matrix[r][c] = 0

    def update(self):
        # Called every frame; we drive actions based on timers
        # If currently in erase animation, count down
        if self.erase_anim_timer > 0:
            self.erase_anim_timer -= 1
            if self.erase_anim_timer == 0:
                # actually clear the marked cells and proceed
                for (r,c) in self.to_clear:
                    self.matrix[r][c] = 0
                self.to_clear = []
            return

        # If waiting after generation, decrement wait
        if self.gen_wait > 0:
            self.gen_wait -= 1
            if self.gen_wait > 0:
                return

        # If need to generate a new puyo pair
        if self.is_generate and self.current_pair is None:
            self.generate_drop()
            return

        # Otherwise, do drop steps periodically
        self.drop_timer += 1
        if self.drop_timer >= DROP_INTERVAL:
            self.drop_timer = 0
            moved = self.drop_step()
            if not moved:
                # 落ちるものが無くなったら消去判定
                erased = self.erase()
                if erased:
                    # 連鎖カウント
                    self.rensa += 1
                else:
                    # 何も消えなければ次を生成
                    self.is_generate = True

    def draw(self):
        # Draw grid background
        for r in range(H):
            for c in range(W):
                x = GRID_X + c * CELL
                y = GRID_Y + r * CELL
                val = self.matrix[r][c]
                if val == 0:
                    # empty cell background
                    pyxel.rect(x, y, CELL, CELL, BG_COLOR)
                    # slight grid lines
                    pyxel.rectb(x, y, CELL, CELL, 1)
                elif val == -1:
                    # erase animation: blink or fade
                    col = 7 if (pyxel.frame_count // 3) % 2 == 0 else 8
                    pyxel.rect(x+1, y+1, CELL-2, CELL-2, col)
                else:
                    col = COLOR_MAP.get(val, 11)
                    pyxel.rect(x+1, y+1, CELL-2, CELL-2, col)
                    pyxel.rectb(x, y, CELL, CELL, 7)

        # Draw current dropping pair on top of matrix (not yet locked)
        if self.current_pair is not None:
            pos = self.current_pair.positions()
            cols = [self.current_pair.col_a, self.current_pair.col_b]
            for (r, c), col in zip(pos, cols):
                # skip drawing if position is out-of-bounds (partially above screen)
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
        # No user controls: the simulation advances automatically.
        # Allow Q/Escape to quit in local environment.
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        self.field.update()

    def draw(self):
        pyxel.cls(BG_COLOR)
        # frame around grid
        pyxel.rect(GRID_X-2, GRID_Y-2, GRID_W_PIX+4, GRID_H_PIX+4, 1)
        self.field.draw()
        # HUD: show rensa count (連鎖) when >0, else show status
        if self.field.rensa > 0:
            txt = f"{self.field.rensa} 連鎖 {'!' * min(self.field.rensa, 6)}"
            pyxel.text(8, 8, txt, 7)
        else:
            pyxel.text(8, 8, "見るだけ Puyo (自動再生)", 7)
        pyxel.text(8, 18, "操作: なし（表示専用）", 7)
        pyxel.text(8, 28, "Q/Esc で終了(ローカル実行時)", 7)

if __name__ == "__main__":
    App()
````markdown name=README.md
```markdown
# pyxel_demo — Web Pyxel single-file demo

This branch will contain a single-file Pyxel app that can be executed via the Pyxel Web Launcher.

Run (example):
https://kitao.github.io/pyxel/wasm/launcher/?run=mo256man.pyxel_demo.web_game

Notes:
- The entrypoint is `web_game.py` at the repository root.
- Screen size: 256×256.
- Controls: none (view-only automatic simulation).
- This is a single-file placeholder game. The final game specification will be provided later; further development will continue on the branch `web-pyxel-game`.

How to test locally (optional):
If you want to run locally with a Python environment and installed Pyxel:
1. Install pyxel in your Python environment.
2. Run: `python web_game.py`

(For browser execution, use the Pyxel Web Launcher URL above.)
