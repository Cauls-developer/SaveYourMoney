"""Entry point para o backend empacotado (PyInstaller)."""
from __future__ import annotations

import os

from backend.app import app


if __name__ == "__main__":
    debug_mode = os.environ.get("SAVEYOURMONEY_DEBUG") == "1"
    app.run(port=5000, debug=debug_mode, use_reloader=debug_mode)
