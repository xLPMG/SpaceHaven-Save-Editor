"""Generate assets/app.ico from app.svg (Windows CI).

Usage:
    python scripts/make_ico.py

Requires:
    PySide6  – already in requirements.txt (renders the SVG)
    Pillow   – for ICO assembly (pip install Pillow)
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
SVG = ROOT / "src" / "ui" / "icons" / "app.svg"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# ── Qt renderer ────────────────────────────────────────────────────────────

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

_app = QApplication.instance() or QApplication(sys.argv)


def render(size: int, path: str | Path) -> None:
    """Render the SVG at *size*×*size* and save to *path* as PNG."""
    renderer = QSvgRenderer(str(SVG))
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    image.save(str(path))


# ── Windows – .ico via Pillow ──────────────────────────────────────────────

def make_ico() -> None:
    try:
        from PIL import Image  # noqa: PLC0415
    except ImportError:
        print("Pillow is required: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    out = ASSETS / "app.ico"
    sizes = [16, 24, 32, 48, 64, 128, 256]

    with tempfile.TemporaryDirectory() as tmp:
        pil_images: list[Image.Image] = []
        for size in sizes:
            png = Path(tmp) / f"icon_{size}.png"
            render(size, png)
            pil_images.append(Image.open(png).copy())

        pil_images[0].save(
            str(out),
            format="ICO",
            sizes=[(s, s) for s in sizes],
            append_images=pil_images[1:],
        )
    print(f"Created {out}")


if __name__ == "__main__":
    make_ico()
