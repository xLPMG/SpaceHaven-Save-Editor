"""Generate platform-specific icon files from app.svg.

Usage:
    python scripts/make_icons.py

Outputs:
    assets/app.icns  (macOS)
    assets/app.ico   (Windows)

Requires:
    PySide6          – already in requirements.txt (renders the SVG)
    Pillow           – Windows only, for ICO assembly (pip install Pillow)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
SVG = ROOT / "src" / "ui" / "icons" / "app.svg"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# ── Qt renderer ────────────────────────────────────────────────────────────

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
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


# ── macOS – .icns via iconutil ─────────────────────────────────────────────

def make_icns() -> None:
    out = ASSETS / "app.icns"
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "app.iconset"
        iconset.mkdir()

        specs: list[tuple[int, str]] = [
            (16,   "icon_16x16.png"),
            (32,   "icon_16x16@2x.png"),
            (32,   "icon_32x32.png"),
            (64,   "icon_32x32@2x.png"),
            (128,  "icon_128x128.png"),
            (256,  "icon_128x128@2x.png"),
            (256,  "icon_256x256.png"),
            (512,  "icon_256x256@2x.png"),
            (512,  "icon_512x512.png"),
            (1024, "icon_512x512@2x.png"),
        ]
        for size, name in specs:
            render(size, iconset / name)

        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(out)],
            check=True,
        )
    print(f"Created {out}")


# ── Windows – .ico via Pillow ──────────────────────────────────────────────

def make_ico() -> None:
    try:
        from PIL import Image  # noqa: PLC0415
    except ImportError:
        print("Pillow is required for ICO generation: pip install Pillow", file=sys.stderr)
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


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if sys.platform == "darwin":
        make_icns()
    elif sys.platform == "win32":
        make_ico()
    else:
        print(f"Unsupported platform: {sys.platform}", file=sys.stderr)
        sys.exit(1)
