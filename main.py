"""Space Haven Save Editor – entry point."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.styles import apply_theme


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Space Haven Save Editor")
    app.setApplicationVersion("1.0.0")
    apply_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
