"""
Pyxel Web Game - A simple platformer demo
Run via Pyxel Web Launcher:
https://kitao.github.io/pyxel/wasm/launcher/?run=mo256man.pyxel_demo.web_game
"""

import pyxel


class Player:
    """Simple player class with movement and jumping."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.vx = 0
        self.vy = 0
        self.speed = 2
        self.jump_power = -6
        self.gravity = 0.3
        self.on_ground = False

    def update(self, ground_y):
        # Horizontal movement
        self.vx = 0
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.vx = -self.speed
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.vx = self.speed

        # Jump
        if self.on_ground and (
            pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_UP)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
        ):
            self.vy = self.jump_power
            self.on_ground = False

        # Apply gravity
        self.vy += self.gravity

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Ground collision
        if self.y + self.height >= ground_y:
            self.y = ground_y - self.height
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Keep player on screen horizontally
        if self.x < 0:
            self.x = 0
        if self.x + self.width > pyxel.width:
            self.x = pyxel.width - self.width

    def draw(self):
        # Draw player as a simple colored rectangle with eyes
        pyxel.rect(self.x, self.y, self.width, self.height, 11)  # Light blue body
        # Eyes
        pyxel.pset(self.x + 2, self.y + 2, 7)  # White left eye
        pyxel.pset(self.x + 5, self.y + 2, 7)  # White right eye


class App:
    """Main application class."""

    def __init__(self):
        pyxel.init(256, 256, title="Pyxel Web Game Demo")

        # Game constants
        self.ground_y = 220

        # Create player at center of screen
        self.player = Player(124, self.ground_y - 8)

        # Start the game loop
        pyxel.run(self.update, self.draw)

    def update(self):
        # Quit on Q key (desktop only)
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # Update player
        self.player.update(self.ground_y)

    def draw(self):
        # Clear screen with dark blue
        pyxel.cls(1)

        # Draw sky gradient (simple)
        for i in range(0, 100, 10):
            pyxel.rect(0, i, 256, 10, 1 if i < 50 else 5)

        # Draw ground
        pyxel.rect(0, self.ground_y, 256, 256 - self.ground_y, 3)  # Dark green
        # Ground top line (grass)
        pyxel.rect(0, self.ground_y, 256, 2, 11)  # Light green grass line

        # Draw player
        self.player.draw()

        # Draw HUD instructions
        self.draw_hud()

    def draw_hud(self):
        # Title
        pyxel.text(85, 10, "PYXEL WEB GAME", 7)

        # Instructions
        pyxel.text(70, 30, "Arrow Keys: Move Left/Right", 6)
        pyxel.text(75, 40, "Space/Up: Jump", 6)
        pyxel.text(85, 50, "Q: Quit (Desktop)", 6)

        # Status
        status = "Jumping!" if not self.player.on_ground else "On Ground"
        pyxel.text(100, 240, status, 10)


# Run the app
App()
