"""Space Haven Save Editor – entry point."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from importlib.metadata import version as _pkg_version
    _APP_VERSION = _pkg_version("spacehaven-save-editor")
except Exception:
    _APP_VERSION = "1.0.0"

from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.styles import apply_theme

_ICONS_DIR = Path(__file__).parent / "src" / "ui" / "icons"
_FONTS_DIR = Path(__file__).parent / "src" / "ui" / "fonts"


def main() -> None:
    app = QApplication(sys.argv)
    for font_file in sorted(_FONTS_DIR.glob("*.otf")) + sorted(_FONTS_DIR.glob("*.ttf")):
        QFontDatabase.addApplicationFont(str(font_file))
    app.setApplicationName("Space Haven Save Editor")
    app.setApplicationVersion(_APP_VERSION)
    app.setWindowIcon(QIcon(str(_ICONS_DIR / "app.svg")))
    apply_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
