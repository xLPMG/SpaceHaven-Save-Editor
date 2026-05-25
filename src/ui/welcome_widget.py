"""welcome_widget.py – Welcome screen with drag-and-drop file loading."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ── Palette tokens ─────────────────────────────────────────────────────────
_BG = QColor("#030709")
_ACCENT = QColor(0, 216, 240)
_TEXT = QColor("#DDF0F5")


# ── Starfield background ────────────────────────────────────────────────────


class _StarfieldWidget(QWidget):
    """Lightweight animated starfield background for the welcome screen."""

    _N_STARS = 90  # total star count
    _FPS = 28  # target frame rate
    _LAYERS = [  # (size_px, speed_px_per_tick, base_alpha)
        (1, 0.12, 100),
        (1, 0.22, 140),
        (2, 0.35, 110),
    ]
    # Possible star tints: cool white, neutral white, warm white, faint amber, faint rose
    _TINTS = [
        (220, 235, 255),  # cool blue-white
        (255, 255, 255),  # pure white
        (255, 252, 240),  # warm white
        (255, 240, 200),  # soft amber
        (255, 225, 215),  # faint rose
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self._stars: list[dict] = []
        self._tick = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000 // self._FPS)
        self._timer.timeout.connect(self._step)

    def showEvent(self, event) -> None:  # noqa: N802
        if not self._stars:
            self._seed_stars()
        self._timer.start()
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # noqa: N802
        self._timer.stop()
        super().hideEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._seed_stars()
        super().resizeEvent(event)

    def _seed_stars(self) -> None:
        w, h = max(self.width(), 1), max(self.height(), 1)
        self._stars = []
        per_layer = self._N_STARS // len(self._LAYERS)
        for size, speed, alpha in self._LAYERS:
            for _ in range(per_layer):
                self._stars.append(
                    {
                        "x": random.uniform(0, w),
                        "y": random.uniform(0, h),
                        "size": size,
                        "speed": speed * (0.7 + random.random() * 0.6),
                        "alpha": alpha + random.randint(-20, 20),
                        "twinkle_offset": random.uniform(0, math.tau),
                        "tint": random.choice(self._TINTS),
                    }
                )

    def _step(self) -> None:
        self._tick += 1
        h = self.height()
        w = self.width()
        for s in self._stars:
            s["y"] += s["speed"]
            if s["y"] > h + 2:
                s["y"] = -2
                s["x"] = random.uniform(0, w)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), _BG)

        t = self._tick * 0.04  # slow twinkle phase
        for s in self._stars:
            phase = math.sin(t + s["twinkle_offset"])
            alpha = int(max(30, min(255, s["alpha"] + phase * 30)))
            r, g, b = s["tint"]
            color = QColor(r, g, b, alpha)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            radius = s["size"] / 2
            painter.drawEllipse(
                int(s["x"] - radius),
                int(s["y"] - radius),
                s["size"],
                s["size"],
            )
        painter.end()


# ── Program Title ─────────────────────────────────────────────────────────────


class _TitleLabel(QWidget):

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._text = text
        self._font = QFont()
        self._font.setPointSize(28)
        self._font.setWeight(QFont.Weight.Bold)
        self._font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        self.setMinimumHeight(80)

    def sizeHint(self):  # noqa: N802
        from PySide6.QtCore import QSize

        return QSize(600, 80)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self._font)
        painter.setPen(QColor("#00D8F0"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)
        painter.end()


# ── Drop zone ──────────────────────────────────────────────────────────────


class DropZone(QFrame):
    """Area that accepts file drops."""

    file_dropped = Signal(str)

    _PULSE_STEPS = 60  # one full pulse cycle in ticks

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("DropZone")
        self._hovered = False
        self._pulse_tick = 0
        self._build_ui()

        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(30)
        self._pulse_timer.timeout.connect(self._on_pulse)

    def showEvent(self, event) -> None:  # noqa: N802
        self._pulse_timer.start()
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # noqa: N802
        self._pulse_timer.stop()
        super().hideEvent(event)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(44, 36, 44, 36)

        arrow = QLabel("↓")
        af = QFont()
        af.setPointSize(36)
        arrow.setFont(af)
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow.setObjectName("DropArrow")
        layout.addWidget(arrow)

        title = QLabel("Drop your save file here")
        tf = QFont()
        tf.setPointSize(15)
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

        layout.addSpacing(8)

        self._browse_btn = QPushButton("Browse files...")
        self._browse_btn.setObjectName("BrowseButton")
        self._browse_btn.setFixedWidth(200)
        self._browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self._browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    @property
    def browse_button(self) -> QPushButton:
        return self._browse_btn

    def _on_pulse(self) -> None:
        self._pulse_tick = (self._pulse_tick + 1) % self._PULSE_STEPS
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = self.rect().adjusted(2, 2, -2, -2)

        # Dark glass background — always present so text is readable
        painter.setPen(Qt.PenStyle.NoPen)
        glass_path = QPainterPath()
        glass_path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), 16, 16)
        if self._hovered:
            painter.setBrush(QColor(0, 216, 240, 18))
        else:
            painter.setBrush(QColor(3, 7, 9, 170))
        painter.drawPath(glass_path)

        # Pulsing dashed border
        phase = math.sin(self._pulse_tick / self._PULSE_STEPS * math.tau)
        if self._hovered:
            alpha = 200 + int(phase * 40)
        else:
            alpha = 80 + int(phase * 40)

        pen = QPen(QColor(0, 216, 240, alpha))
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        path = QPainterPath()
        path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), 16, 16)
        painter.drawPath(path)

        # Corner accent dots when hovered
        if self._hovered:
            dot_color = QColor(0, 216, 240, 200)
            painter.setBrush(dot_color)
            painter.setPen(Qt.PenStyle.NoPen)
            for cx, cy in [
                (r.x(), r.y()),
                (r.right(), r.y()),
                (r.x(), r.bottom()),
                (r.right(), r.bottom()),
            ]:
                painter.drawEllipse(QPoint(cx, cy), 4, 4)

        painter.end()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._hovered = True
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._hovered = False

    def dropEvent(self, event: QDropEvent) -> None:
        self._hovered = False
        urls = event.mimeData().urls()
        if urls:
            self.file_dropped.emit(urls[0].toLocalFile())


# ── Welcome widget ─────────────────────────────────────────────────────────


class WelcomeWidget(QWidget):
    """Shown at startup before any file is loaded."""

    file_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        # Starfield fills the whole widget
        self._starfield = _StarfieldWidget(self)

        # Foreground content layered on top via a transparent overlay widget
        overlay = QWidget(self)
        overlay.setObjectName("WelcomeOverlay")
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        overlay.setStyleSheet("QWidget#WelcomeOverlay { background: transparent; }")

        root = QVBoxLayout(overlay)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setContentsMargins(60, 48, 60, 48)
        root.setSpacing(0)

        program_title = _TitleLabel("SPACE HAVEN SAVE EDITOR")
        root.addWidget(program_title, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Mission Control for your save files")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("WelcomeSubtitle")
        root.addWidget(subtitle)

        root.addSpacing(36)

        # Drop zone
        self._drop_zone = DropZone()
        self._drop_zone.setMinimumSize(460, 300)
        self._drop_zone.setMaximumWidth(640)
        self._drop_zone.file_dropped.connect(self.file_selected)
        self._drop_zone.browse_button.clicked.connect(self._browse)
        root.addWidget(self._drop_zone, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addSpacing(28)

        tip_text = QLabel(
            "<b>Tip:</b> Always create a backup before editing your save file."
        )
        tip_text.setTextFormat(Qt.TextFormat.RichText)
        tip_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tip_text.setObjectName("WelcomeTip")
        root.addWidget(tip_text)

        root.addSpacing(16)

        from PySide6.QtWidgets import QApplication
        version = QApplication.applicationVersion()
        author_text = QLabel(
            f'v{version} &nbsp;·&nbsp; '
            '<a href="https://github.com/xLPMG" style="color:#00D8F0;">xLPMG</a>'
        )
        author_text.setTextFormat(Qt.TextFormat.RichText)
        author_text.setOpenExternalLinks(True)
        author_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_text.setObjectName("WelcomeAuthor")
        root.addWidget(author_text)

        self._overlay = overlay

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._starfield.setGeometry(self.rect())
        self._overlay.setGeometry(self.rect())
        super().resizeEvent(event)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Space Haven Save File",
            str(Path.home()),
            "Space Haven Save (game);;All Files (*)",
        )
        if path:
            self.file_selected.emit(path)
