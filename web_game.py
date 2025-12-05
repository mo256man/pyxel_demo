"""
Pyxel Web Game - Simple Platformer Demo
========================================
A minimal playable Pyxel game for the Pyxel Web Launcher.
Run URL: https://kitao.github.io/pyxel/wasm/launcher/?run=mo256man.pyxel_demo.web_game

Controls:
- Left/Right Arrow: Move player
- Space or Up Arrow: Jump

This is a placeholder game. The final game specification will be provided later.
"""

import pyxel


class Player:
    """Player character with movement, jumping, and ground collision."""

    def __init__(self, x: float, y: float):
        """Initialize player at given position."""
        self.x = x
        self.y = y
        self.vx = 0.0  # Horizontal velocity
        self.vy = 0.0  # Vertical velocity
        self.width = 8
        self.height = 8
        self.on_ground = False
        self.speed = 2.0
        self.jump_power = -5.0
        self.gravity = 0.3

    def update(self, ground_y: int):
        """Update player position based on input and physics."""
        # Horizontal movement
        self.vx = 0
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.vx = -self.speed
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.vx = self.speed

        # Jump (only when on ground)
        if self.on_ground:
            if (
                pyxel.btnp(pyxel.KEY_SPACE)
                or pyxel.btnp(pyxel.KEY_UP)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
            ):
                self.vy = self.jump_power
                self.on_ground = False
                # Play jump sound (beep)
                pyxel.play(0, 0)

        # Apply gravity
        self.vy += self.gravity

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Screen boundary collision (horizontal)
        if self.x < 0:
            self.x = 0
        if self.x > pyxel.width - self.width:
            self.x = pyxel.width - self.width

        # Ground collision
        if self.y >= ground_y - self.height:
            self.y = ground_y - self.height
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def draw(self):
        """Draw the player sprite as a simple rectangle with face."""
        # Player body (blue square)
        pyxel.rect(int(self.x), int(self.y), self.width, self.height, 12)
        # Eyes (white dots)
        pyxel.pset(int(self.x) + 2, int(self.y) + 2, 7)
        pyxel.pset(int(self.x) + 5, int(self.y) + 2, 7)
        # Mouth (simple line when on ground, different when jumping)
        if self.on_ground:
            pyxel.line(
                int(self.x) + 2, int(self.y) + 5, int(self.x) + 5, int(self.y) + 5, 7
            )
        else:
            # Open mouth when jumping
            pyxel.pset(int(self.x) + 3, int(self.y) + 5, 7)
            pyxel.pset(int(self.x) + 4, int(self.y) + 5, 7)


class Game:
    """Main game class managing game state, update, and rendering."""

    def __init__(self):
        """Initialize Pyxel and game state."""
        # Initialize Pyxel with 256x256 screen, no virtual gamepad
        pyxel.init(256, 256, title="Pyxel Web Game Demo")

        # Define ground level
        self.ground_y = 220

        # Create player at center of screen
        self.player = Player(124, self.ground_y - 8)

        # Define jump sound using minimal MML (Music Macro Language)
        # Sound 0: A short beep for jumping
        pyxel.sounds[0].set(
            notes="C3",  # Note
            tones="P",  # Pulse wave
            volumes="5",  # Volume
            effects="F",  # Fade out
            speed=10,  # Speed
        )

        # Start the game loop
        pyxel.run(self.update, self.draw)

    def update(self):
        """Update game state each frame."""
        # Quit on Q key
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # Update player
        self.player.update(self.ground_y)

    def draw(self):
        """Render the game each frame."""
        # Clear screen with dark blue background (sky)
        pyxel.cls(1)

        # Draw ground
        pyxel.rect(0, self.ground_y, 256, 256 - self.ground_y, 3)

        # Draw some simple scenery (grass tufts)
        for i in range(0, 256, 16):
            pyxel.line(i + 4, self.ground_y, i + 4, self.ground_y - 3, 11)
            pyxel.line(i + 8, self.ground_y, i + 8, self.ground_y - 4, 11)
            pyxel.line(i + 12, self.ground_y, i + 12, self.ground_y - 2, 11)

        # Draw player
        self.player.draw()

        # Draw HUD / Instructions
        self.draw_hud()

    def draw_hud(self):
        """Draw heads-up display with instructions."""
        # Title
        pyxel.text(80, 8, "PYXEL WEB GAME", 7)

        # Instructions
        pyxel.text(8, 240, "LEFT/RIGHT: Move  SPACE/UP: Jump  Q: Quit", 7)

        # Status info
        status = "JUMPING!" if not self.player.on_ground else "ON GROUND"
        pyxel.text(8, 20, f"Status: {status}", 10)


# Entry point for Pyxel Web Launcher
if __name__ == "__main__":
    Game()
