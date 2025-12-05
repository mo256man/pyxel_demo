import pyxel

class App:
    def __init__(self):
        pyxel.init(256, 256, caption="Pyxel Web Demo")
        self.x = 128
        self.y = 200
        self.vx = 0
        self.vy = 0
        self.on_ground = True
        self.score = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        # Basic left/right movement
        self.vx = 0
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.vx = -2
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.vx = 2

        # Jump
        if (pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_SPACE)) and self.on_ground:
            self.vy = -6
            self.on_ground = False

        # Gravity and motion
        self.vy += 0.3
        self.x += self.vx
        self.y += self.vy

        # Simple ground collision
        ground_y = 240
        if self.y >= ground_y:
            self.y = ground_y
            self.vy = 0
            self.on_ground = True

        # Keep player in screen
        self.x = max(8, min(248, self.x))

        # Simple scoring: hold X to increase score
        if pyxel.btn(pyxel.KEY_X):
            self.score += 1

        # Quit with Q
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        # ground
        pyxel.rect(0, 248, 256, 8, 3)
        # player
        pyxel.rect(int(self.x)-4, int(self.y)-4, 8, 8, 11)
        # HUD
        pyxel.text(4, 4, "Use ← → (A/D) to move, Z/SPACE to jump", 7)
        pyxel.text(4, 12, "Hold X to increase score. Q to quit.", 7)
        pyxel.text(4, 20, f"Score: {self.score}", 7)


App()
