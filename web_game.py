"""
Pyxel 自動ぷよ（ペア落下） — ランチャー互換モジュール（caption 非対応環境に対応）

このモジュールは run() をエクスポートし、モジュールの import だけで起動できるよう末尾で run() を呼びます。
- run() は冪等（複数回呼んでも二重起動しません）。
- pyxel.init の caption 未対応実装に対してフォールバックします。
"""

import random
import inspect

try:
    import pyxel
except Exception as e:
    raise ImportError(
        "このモジュールを実行するには pyxel が必要です。Pyxel Web Launcher 経由で実行するか、"
        "ローカルでテストする場合は pyxel をインストールしてください。"
        f"(元のエラー: {e})"
    )

# DIAG: inserted diagnostic prints to help identify which file and pyxel.init signature the launcher is actually using
try:
    try:
        print("DIAG: web_game __file__ =", __file__)
    except Exception:
        print("DIAG: __file__ not available")
    try:
        print("DIAG: pyxel.init obj =", getattr(pyxel, "init", None))
        try:
            sig = inspect.signature(pyxel.init)
            print("DIAG: pyxel.init signature:", sig)
        except Exception as e:
            print("DIAG: inspect.signature failed:", e)
    except Exception as e:
        print("DIAG: failed to inspect pyxel.init:", e)
except Exception:
    # keep diagnostics best-effort and never break import
    pass

# グリッド / ゲーム設定
W = 16
H = 16
OWANIMO = 4   # 消える個数の閾値
COLORS = 4    # 色数 (1..COLORS)

SCREEN_W = 256
SCREEN_H = 256

# レイアウト / 描画設定
MARGIN = 16
CELL = min((SCREEN_W - MARGIN * 2) // W, (SCREEN_H - MARGIN * 2) // H)
GRID_W_PIX = CELL * W
GRID_H_PIX = CELL * H
GRID_X = (SCREEN_W - GRID_W_PIX) // 2
GRID_Y = (SCREEN_H - GRID_H_PIX) // 2

# タイミング（フレーム数）
DROP_INTERVAL = 6
ERASE_ANIM_FRAMES = 18
GEN_WAIT_FRAMES = 4

# Pyxel のカラーマッピング（必要に応じて調整）
COLOR_MAP = {
    1: 11,
    2: 9,
    3: 10,
    4: 12,
}
BG_COLOR = 0

# run() を複数回呼んでも多重起動にならないようにするガード
_started = False

def _init_pyxel():
    """
    pyxel.init を呼び出す。caption 引数が使えない環境では自動でフォールバックする。
    inspect.signature で caption の有無を判定し、例外が出たら caption なしで再試行する。
    """
    try:
        sig = inspect.signature(pyxel.init)
        if 'caption' in sig.parameters:
            pyxel.init(SCREEN_W, SCREEN_H, caption="pyxel_demo - auto puyo (pair fall)")
        else:
            pyxel.init(SCREEN_W, SCREEN_H)
    except Exception:
        # inspect が利用できない実装や予期せぬ例外が出た場合は caption なしで再試行
        pyxel.init(SCREEN_W, SCREEN_H)

class Pair:
    def __init__(self, r, c, orientation, col_a, col_b):
        if orientation == 'H':
            self.blocks = [(r, c, col_a), (r, c+1, col_b)]
        else:
            self.blocks = [(r, c, col_a), (r+1, c, col_b)]

    def positions(self):
        return [(r, c) for r, c, _ in self.blocks]

    def move_down(self, field):
        new_blocks = []
        for r, c, col in self.blocks:
            if r + 1 >= H or field.matrix[r + 1][c] != 0:
                field.matrix[r][c] = col
            else:
                new_blocks.append((r + 1, c, col))
        self.blocks = new_blocks
        if not self.blocks:
            return True  # 全て固定
        return False

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
        # フィールドを空にする
        self.matrix = [[0] * W for _ in range(H)]

    def can_place_pair(self, orientation, c):
        # 指定位置にペアを配置できるか（上段の空きを確認）
        if orientation == 'H':
            if c < 0 or c >= W - 1:
                return False
            return self.matrix[0][c] == 0 and self.matrix[0][c + 1] == 0
        else:
            if c < 0 or c >= W:
                return False
            return self.matrix[0][c] == 0 and self.matrix[1][c] == 0

    def generate_drop(self):
        # 横向き／縦向きのどちらかでランダムにペアを生成して配置
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
            # 置けないときはランダムな色を一色消す（元仕様に準拠）
            self.erase_one_color()
            self.is_generate = False
            self.gen_wait = GEN_WAIT_FRAMES
            self.rensa = 0

    def lock_current_pair(self):
        # ペアを固定（マトリックスに書き込む）
        if self.current_pair is None:
            return
        pos = self.current_pair.positions()
        cols = [self.current_pair.col_a, self.current_pair.col_b]
        for (r, c), col in zip(pos, cols):
            # 範囲外になったらゲームオーバーに相当してフィールドをクリア
            if not (0 <= r < H and 0 <= c < W):
                self.clear()
                self.current_pair = None
                self.is_generate = True
                return
            self.matrix[r][c] = col
        self.current_pair = None

    def drop_step(self):
        # ペアがある場合はペアとして落下させ、それ以外は単体ブロックの落下処理
        moved = False
        if self.current_pair is not None:
            if self.current_pair.move_down(self):
                self.current_pair = None
            moved = True
            return moved

        # 単体ブロックの落下（下から順に1セルだけ落とす）
        for r in range(H - 2, -1, -1):
            for c in range(W):
                if self.matrix[r][c] != 0 and self.matrix[r + 1][c] == 0:
                    self.matrix[r + 1][c] = self.matrix[r][c]
                    self.matrix[r][c] = 0
                    moved = True
        return moved

    def erase(self):
        # BFS で同色のグループを見つけ、閾値以上なら消す（-1 でアニメーションマーク）
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
                    # 消去演出用に -1 でマーク
                    self.matrix[r][c] = -1
                    self.to_clear.append((r,c))
            self.erase_anim_timer = ERASE_ANIM_FRAMES

        return is_erase

    def erase_one_color(self):
        # ランダムに1色選んでフィールドから消す
        color = random.randint(1, COLORS)
        for r in range(H):
            for c in range(W):
                if self.matrix[r][c] == color:
                    self.matrix[r][c] = 0

    def update(self):
        # ゲームのフレーム処理（消去アニメ、生成待ち、落下、消去検出、連鎖処理）
        # 1) 消去アニメが進行中ならそれを処理
        if self.erase_anim_timer > 0:
            self.erase_anim_timer -= 1
            if self.erase_anim_timer == 0:
                # アニメ終了 → 実際に削除
                for (r,c) in self.to_clear:
                    self.matrix[r][c] = 0
                self.to_clear = []
                # 重力で落とす（安定するまで）
                moved = True
                while moved:
                    moved = self.drop_step()
                # 落下後に再度消去が起きれば連鎖継続
                if self.erase():
                    # 連鎖を継続
                    self.rensa += 1
                    # erase() が erase_anim_timer をセットする
                else:
                    # 連鎖終了
                    self.rensa = 0
                    self.is_generate = True
            return

        # 2) 生成待ち（ペアを置いた直後の短い待ち時間）
        if self.gen_wait > 0:
            self.gen_wait -= 1
            return

        # 3) もし生成フラグが立っているなら新しいペアを生成
        if self.is_generate and self.current_pair is None:
            self.generate_drop()
            return

        # 4) ペアが存在する場合の落下処理（タイマー制御）
        if self.current_pair is not None:
            self.drop_timer += 1
            if self.drop_timer >= DROP_INTERVAL:
                self.drop_timer = 0
                # drop_step は落下または固定を行う
                moved = self.drop_step()
                # 固定された場合は current_pair が None になるので検出して消去処理へ移行
                if self.current_pair is None:
                    if self.erase():
                        # 初回の消去が見つかったら連鎖カウントを 1 にする
                        self.rensa = 1
                        # erase() が erase_anim_timer をセットする
                    else:
                        # 消去なし → 次の生成へ
                        self.is_generate = True
            return

        # 5) ペアが無い状態で単体ブロックがある場合は時々重力処理を走らせる
        self.drop_timer += 1
        if self.drop_timer >= DROP_INTERVAL:
            self.drop_timer = 0
            moved = self.drop_step()
            if moved:
                # 落下が起きた後に消えるものがあれば処理
                if self.erase():
                    self.rensa = 1
            # 何もなければ次フレームへ

    def draw(self):
        # グリッドの各セルを描画
        for r in range(H):
            for c in range(W):
                x = GRID_X + c * CELL
                y = GRID_Y + r * CELL
                val = self.matrix[r][c]
                if val == 0:
                    pyxel.rect(x, y, CELL, CELL, BG_COLOR)
                    pyxel.rectb(x, y, CELL, CELL, 1)
                elif val == -1:
                    # 消去アニメの点滅描画
                    col = 7 if (pyxel.frame_count // 3) % 2 == 0 else 8
                    pyxel.rect(x+1, y+1, CELL-2, CELL-2, col)
                else:
                    col = COLOR_MAP.get(val, 11)
                    pyxel.rect(x+1, y+1, CELL-2, CELL-2, col)
                    pyxel.rectb(x, y, CELL, CELL, 7)

class App:
    def __init__(self):
        _init_pyxel()
        self.field = Field()
        pyxel.run(self.update, self.draw)

    def update(self):
        # ローカル実行時に終了できるように Q/Escape を許可
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        # フィールドの状態更新（自動再生ロジックを中に含む）
        self.field.update()

    def draw(self):
        pyxel.cls(BG_COLOR)
        # グリッド周りの枠描画
        pyxel.rect(GRID_X-2, GRID_Y-2, GRID_W_PIX+4, GRID_H_PIX+4, 1)
        # フィールド本体を描画
        self.field.draw()
        # 落下中のペアをマトリックス描画の上に重ねて描画
        if self.field.current_pair is not None:
            for r, c, col in self.field.current_pair.blocks:
                if not (0 <= r < H and 0 <= c < W):
                    continue
                x = GRID_X + c * CELL
                y = GRID_Y + r * CELL
                colidx = COLOR_MAP.get(col, 11)
                pyxel.rect(x+1, y+1, CELL-2, CELL-2, colidx)
                pyxel.rectb(x, y, CELL, CELL, 7)

        # HUD: 連鎖表示またはステータスメッセージ
        if self.field.rensa > 0:
            txt = f"{self.field.rensa} 連鎖 {'!' * min(self.field.rensa, 6)}"
            pyxel.text(8, 8, txt, 7)
        else:
            pyxel.text(8, 8, "見るだけ Puyo (自動再生)", 7)
        pyxel.text(8, 18, "操作: なし（表示専用）", 7)
        pyxel.text(8, 28, "Q/Esc で終了(ローカル実行時)", 7)

def run():
    """アプリを開始する。ランチャーや外部コードから呼び出せるようにしている。"""
    global _started
    if _started:
        return
    _started = True
    random.seed()
    App()

# モジュールがインポートされたときに自動起動を試みる（Pyxel Web Launcher が import するだけで実行する実装に対応）
# また `python web_game.py` で実行する場合にも動くようにしている。
run()

# JSDELIVR_CACHE_BUST: 2025-12-05T16:41:11Z
# CACHE_BUST: 2025-12-06T16:45Z
# AUTO_TRIGGER: 2025-12-06T01:30:00Z
