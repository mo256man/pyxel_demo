# pyxel_demo — Web Pyxel single-file demo

This branch will contain a single-file Pyxel app that can be executed via the Pyxel Web Launcher.

## Quick Start

**Recommended (cache-busted launcher):**
Open `index.html` in your browser or host it via GitHub Pages. The launcher fetches the latest commit SHA from the GitHub API and loads `web_game.py` via a content-addressed jsDelivr URL (`@<commit-sha>`), ensuring you always get the latest version.

**Direct URL (may serve stale cache):**
https://kitao.github.io/pyxel/wasm/launcher/?run=mo256man.pyxel_demo.web_game

## Cache-Busting Strategy

The `index.html` launcher implements a robust cache-busting strategy:

1. **Commit SHA Resolution**: On launch, it queries the GitHub API to get the latest commit SHA for the `main` branch.
2. **Content-Addressed URL**: Uses the SHA to construct a jsDelivr URL like `https://cdn.jsdelivr.net/gh/mo256man/pyxel_demo@<sha>/web_game.py`. Since each commit has a unique SHA, this guarantees fresh content.
3. **Session Caching**: The resolved SHA is cached in `sessionStorage` to avoid repeated API calls within the same browser session.
4. **Fallback**: If the GitHub API call fails (e.g., rate limiting), it falls back to `raw.githubusercontent.com` which doesn't use edge caching.

This approach eliminates stale-edge-cache issues that can occur when relying on CDN purge propagation.

## Notes

- The entrypoint is `web_game.py` at the repository root.
- Screen size: 256×256.
- Controls: none (view-only automatic simulation).
- This is a single-file placeholder game. The final game specification will be provided later; further development will continue on the branch `web-pyxel-game`.

## How to test locally (optional)

If you want to run locally with a Python environment and installed Pyxel:
1. Install pyxel in your Python environment.
2. Run: `python web_game.py`

(For browser execution, use the launcher via `index.html` as described above.)
