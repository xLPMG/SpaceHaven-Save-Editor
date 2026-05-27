"""Generate assets/app.icns from app.svg (macOS CI).

Usage:
    python scripts/make_icns.py

Requires:
    PySide6
    iconutil
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
SVG = ROOT / "src" / "ui" / "icons" / "app.svg"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# Qt renderer

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


# macOS - .icns via iconutil

_ICONSET_SPECS: list[tuple[int, str]] = [
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


def make_icns() -> None:
    out = ASSETS / "app.icns"
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "app.iconset"
        iconset.mkdir()
        for size, name in _ICONSET_SPECS:
            render(size, iconset / name)
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(out)],
            check=True,
        )
    print(f"Created {out}")


if __name__ == "__main__":
    make_icns()
