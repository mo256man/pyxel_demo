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

## SHA-based CDN URLs (Cache-busting)

### Why use commit SHA?

jsDelivr edge caches may return stale content even after purging. To prevent this, the launcher uses **commit SHA-based URLs** that guarantee unique paths for each commit:

```
https://cdn.jsdelivr.net/gh/mo256man/pyxel_demo@{commit-sha}/web_game.py
```

This approach ensures that each file version has a unique URL, eliminating cache staleness issues entirely.

### How it works

1. The launcher fetches the latest commit SHA from the GitHub API
2. The SHA is cached in `sessionStorage` to avoid repeated API calls
3. A unique jsDelivr URL is constructed using the commit SHA
4. If the GitHub API fails (e.g., rate limit), the launcher falls back to `raw.githubusercontent.com` with a timestamp parameter

### Fallback mechanism

If the GitHub API is unavailable or rate-limited, the launcher automatically falls back to:

```
https://raw.githubusercontent.com/mo256man/pyxel_demo/main/web_game.py?ts={timestamp}
```

### Manual cache bypass

To force a fresh load without using the cached SHA:

1. Clear your browser's sessionStorage for this site, or
2. Open Developer Tools → Application → Session Storage → Clear the `mo256man_pyxel_demo_main_sha` key

### manifest.json

A `manifest.json` file is automatically generated on each push to main, containing the latest commit SHA for diagnostic purposes:

```json
{
  "sha": "<commit-sha>",
  "path": "web_game.py",
  "timestamp": "<ISO-8601-timestamp>"
}
```
