# Pyxel Web Demo

This document describes how to run the Pyxel demo application in the browser using Pyxel's Web tools.

## Running via Pyxel Web Launcher

Click the following link to launch the app directly in your browser:

**[Launch Pyxel Web Demo](https://kitao.github.io/pyxel/wasm/launcher/?run=mo256man.pyxel_demo.wasm.app)**

```
https://kitao.github.io/pyxel/wasm/launcher/?run=mo256man.pyxel_demo.wasm.app
```

The Pyxel Web Launcher will automatically fetch and run the `wasm/app.py` script from this repository.

## Running via Pyxel Code Maker

You can also use the [Pyxel Code Maker](https://kitao.github.io/pyxel/wasm/code-maker/) to run or modify the app:

1. Open the Pyxel Code Maker: https://kitao.github.io/pyxel/wasm/code-maker/
2. Copy the contents of [`wasm/app.py`](../wasm/app.py) into the editor
3. Click the "Run" button to execute the app

Alternatively, use the launcher URL above to run the app directly without copying code.

## Controls

- **← / → (or A / D)**: Move left/right
- **Z / SPACE**: Jump
- **X**: Hold to increase score
- **Q**: Quit

## About

This is a minimal 256x256 Pyxel application designed to run in the browser via the Pyxel Web runtime (Pyodide-based). It uses only the `pyxel` module and core Python features for compatibility with the web runtime.

For more information about Pyxel Web, see the [Pyxel Web documentation](https://github.com/kitao/pyxel/blob/main/docs/pyxel-web-en.md).
