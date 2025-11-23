import pyxel

class App:
    def __init__(self):
        pyxel.init(160, 120)
        self.x = 50
        self.y = 50
        self.speed = 2
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= self.speed
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += self.speed
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= self.speed
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += self.speed

    def draw(self):
        pyxel.cls(0)
        pyxel.circ(self.x, self.y, 5, 7)

App()