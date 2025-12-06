# pyxel_demo — Web Pyxel single-file demo

This branch will contain a single-file Pyxel app that can be executed via the Pyxel Web Launcher.

Run (example):
https://kitao.github.io/pyxel/wasm/launcher/?run=mo256man.pyxel_demo.web_game

## Commit-SHA CDN URLs

The launcher (`index.html`) uses **commit-SHA-addressed jsDelivr URLs** to ensure users always get the latest version of `web_game.py`.

### Why commit-SHA URLs?

jsDelivr edge caches can serve stale content even after a cache purge request. By including the commit SHA in the URL (e.g., `https://cdn.jsdelivr.net/gh/mo256man/pyxel_demo@<commit-sha>/web_game.py`), each new commit produces a unique, content-addressed URL that bypasses any cached versions.

### How it works

1. The launcher fetches the latest commit SHA from the GitHub API
2. The SHA is cached in `sessionStorage` for 5 minutes to reduce API calls
3. The jsDelivr CDN URL is built with `@<sha>` suffix
4. If the GitHub API is unavailable (rate limits, network issues), it falls back to `raw.githubusercontent.com`

### Rate limit mitigation

- The SHA is cached in `sessionStorage` with a 5-minute TTL
- Multiple page loads within the TTL window reuse the cached SHA
- Fallback to `raw.githubusercontent.com` ensures the app still works if API limits are hit

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
