import pyxel

class Game:
    def __init__(self):
        pyxel.init(200, 150, title="Copilot's Game")
        self.player_x = 100
        self.player_y = 75
        self.player_size = 8
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x -= 2
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x += 2
        if pyxel.btn(pyxel.KEY_UP):
            self.player_y -= 2
        if pyxel.btn(pyxel.KEY_DOWN):
            self.player_y += 2
        
        # Boundary detection
        if self.player_x < self.player_size:
            self.player_x = self.player_size
        if self.player_x > 200 - self.player_size:
            self.player_x = 200 - self.player_size
        if self.player_y < self.player_size:
            self.player_y = self.player_size
        if self.player_y > 150 - self.player_size:
            self.player_y = 150 - self.player_size
    
    def draw(self):
        pyxel.cls(0)
        pyxel.rect(10, 10, 180, 130, 1)
        pyxel.circfill(self.player_x, self.player_y, self.player_size, 8)
        pyxel.text(20, 20, "Arrow Keys to Move", 7)

Game()