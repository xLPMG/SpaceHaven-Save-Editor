"""welcome_widget.py – Welcome screen with drag-and-drop file loading."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DropZone(QFrame):
    """Area that accepts file drops."""

    file_dropped = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("DropZone")
        self._hovered = False
        self._build_ui()
        self._update_drop_style()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 32, 40, 32)

        arrow = QLabel("↓")
        af = QFont()
        af.setPointSize(40)
        arrow.setFont(af)
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow.setObjectName("DropArrow")
        layout.addWidget(arrow)

        title = QLabel("Drop your save file here")
        tf = QFont()
        tf.setPointSize(16)
        tf.setWeight(QFont.Weight.DemiBold)
        title.setFont(tf)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("DropTitle")
        layout.addWidget(title)

        hint = QLabel(
            "The Space Haven save file is typically named <b>game</b> "
            "and found inside your Space Haven saves directory."
        )
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)
        hint.setTextFormat(Qt.TextFormat.RichText)
        hint.setObjectName("DropHint")
        layout.addWidget(hint)

        layout.addSpacing(6)

        self._browse_btn = QPushButton("Browse for file…")
        self._browse_btn.setObjectName("BrowseButton")
        self._browse_btn.setFixedWidth(190)
        self._browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self._browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    @property
    def browse_button(self) -> QPushButton:
        return self._browse_btn

    def _update_drop_style(self) -> None:
        if self._hovered:
            border = "#00D8F0"
            bg = "rgba(0,216,240,0.06)"
        else:
            border = "rgba(0,216,240,0.25)"
            bg = "transparent"
        self.setStyleSheet(
            f"""
            QFrame#DropZone {{
                border: 2px dashed {border};
                border-radius: 18px;
                background-color: {bg};
            }}
            """
        )

    # ── Drag & drop ───────────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._hovered = True
            self._update_drop_style()
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._hovered = False
        self._update_drop_style()

    def dropEvent(self, event: QDropEvent) -> None:
        self._hovered = False
        self._update_drop_style()
        urls = event.mimeData().urls()
        if urls:
            self.file_dropped.emit(urls[0].toLocalFile())


class WelcomeWidget(QWidget):
    """Shown at startup before any file is loaded."""

    file_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setContentsMargins(60, 48, 60, 48)
        root.setSpacing(0)

        # App title
        title = QLabel("Space Haven Save Editor")
        tf = QFont()
        tf.setPointSize(26)
        tf.setWeight(QFont.Weight.Bold)
        title.setFont(tf)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("WelcomeTitle")
        root.addWidget(title)
        root.addSpacing(32)

        # Drop zone
        self._drop_zone = DropZone()
        self._drop_zone.setMinimumSize(480, 320)
        self._drop_zone.setMaximumWidth(640)
        self._drop_zone.file_dropped.connect(self.file_selected)
        self._drop_zone.browse_button.clicked.connect(self._browse)
        root.addWidget(self._drop_zone, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addSpacing(28)

        # Tip row
        tip_row = QHBoxLayout()
        tip_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tip_text = QLabel("<b>Tip:</b> Always create a backup before editing your save file.")
        tip_text.setTextFormat(Qt.TextFormat.RichText)
        tip_text.setObjectName("WelcomeTip")
        tip_row.addWidget(tip_text)
        root.addLayout(tip_row)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Space Haven Save File",
            str(Path.home()),
            "Space Haven Save (game);;All Files (*)",
        )
        if path:
            self.file_selected.emit(path)
