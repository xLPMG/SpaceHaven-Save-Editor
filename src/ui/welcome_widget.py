"""welcome_widget.py - Welcome screen with drag-and-drop file loading."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PySide6.QtCore import QPoint, QSize, Qt, QTimer, Signal
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
    QApplication,
    QFileDialog,
    QFrame,
    QLabel,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.ui.styles import (
    WELCOME_AUTHOR_COLOR,
    WELCOME_BG_COLOR,
    WELCOME_DROP_BG,
    WELCOME_DROP_BORDER_COLOR,
    WELCOME_DROP_BORDER_HOVER_COLOR,
    WELCOME_DROP_CORNER_COLOR,
    WELCOME_DROP_HOVER_BG,
    WELCOME_LINK_COLOR,
    WELCOME_STAR_TINTS,
    WELCOME_SUBTITLE_COLOR,
    WELCOME_TITLE_COLOR,
    WELCOME_TIP_COLOR,
)

# Starfield background


class _StarfieldWidget(QWidget):
    """Lightweight animated starfield background for the welcome screen."""

    _N_STARS = 90  # total star count
    _FPS = 28  # target frame rate
    _LAYERS = [  # (size_px, speed_px_per_tick, base_alpha)
        (2, 0.12, 100),
        (2, 0.22, 140),
        (3, 0.35, 110),
    ]
    # Possible star tints: cool white, neutral white, warm white, faint amber, faint rose
    _TINTS = WELCOME_STAR_TINTS

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
        painter.fillRect(self.rect(), WELCOME_BG_COLOR)

        t = self._tick * 0.04  # slow twinkle phase
        for s in self._stars:
            phase = math.sin(t + s["twinkle_offset"])
            alpha = int(max(30, min(255, s["alpha"] + phase * 30)))
            color = QColor(s["tint"])
            color.setAlpha(alpha)
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


# Program title


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
        return QSize(600, 80)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self._font)
        painter.setPen(WELCOME_TITLE_COLOR)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)
        painter.end()


# Drop zone


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

        title = QLabel("Drop your save folder or game file here")
        tf = QFont()
        tf.setPointSize(15)
        tf.setWeight(QFont.Weight.DemiBold)
        title.setFont(tf)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("DropTitle")
        layout.addWidget(title)

        hint = QLabel(
            "The save folder is located inside the <b>savegames</b> folder in your Space Haven data directory. You may drop either the entire save folder, the folder inside named 'save' or the 'game' file inside the 'save' folder."
        )
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)
        hint.setTextFormat(Qt.TextFormat.RichText)
        hint.setObjectName("DropHint")
        layout.addWidget(hint)

        layout.addSpacing(8)

        self._browse_btn = QPushButton("Browse…")
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

        # Dark glass background; always present so text stays readable
        painter.setPen(Qt.PenStyle.NoPen)
        glass_path = QPainterPath()
        glass_path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), 16, 16)
        if self._hovered:
            painter.setBrush(WELCOME_DROP_HOVER_BG)
        else:
            painter.setBrush(WELCOME_DROP_BG)
        painter.drawPath(glass_path)

        # Pulsing dashed border
        phase = math.sin(self._pulse_tick / self._PULSE_STEPS * math.tau)
        if self._hovered:
            alpha = 200 + int(phase * 40)
        else:
            alpha = 80 + int(phase * 40)

        border_color = (
            WELCOME_DROP_BORDER_HOVER_COLOR
            if self._hovered
            else WELCOME_DROP_BORDER_COLOR
        )
        border_color = QColor(border_color)
        border_color.setAlpha(alpha)
        pen = QPen(border_color)
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        path = QPainterPath()
        path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), 16, 16)
        painter.drawPath(path)

        # Corner accent dots when hovered
        if self._hovered:
            painter.setBrush(WELCOME_DROP_CORNER_COLOR)
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
            self.update()
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._hovered = False
        self.update()

    def dropEvent(self, event: QDropEvent) -> None:
        self._hovered = False
        urls = event.mimeData().urls()
        if urls:
            self.file_dropped.emit(urls[0].toLocalFile())
            event.acceptProposedAction()
        else:
            event.ignore()
        self.update()


# Welcome widget


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
        program_title.setObjectName("WelcomeTitle")
        root.addWidget(program_title, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Mission Control for your save files")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setStyleSheet(f"color: {WELCOME_SUBTITLE_COLOR.name()};")
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
        tip_text.setStyleSheet(f"color: {WELCOME_TIP_COLOR.name()};")
        root.addWidget(tip_text)

        root.addSpacing(16)

        version = QApplication.applicationVersion()
        author_text = QLabel(
            f"v{version} &nbsp;·&nbsp; "
            f'<a href="https://github.com/xLPMG" style="color:{WELCOME_LINK_COLOR.name()};">xLPMG</a>'
        )
        author_text.setTextFormat(Qt.TextFormat.RichText)
        author_text.setOpenExternalLinks(True)
        author_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_text.setObjectName("WelcomeAuthor")
        author_text.setStyleSheet(f"color: {WELCOME_AUTHOR_COLOR.name()};")
        root.addWidget(author_text)

        self._overlay = overlay

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._starfield.setGeometry(self.rect())
        self._overlay.setGeometry(self.rect())
        super().resizeEvent(event)

    def _browse(self) -> None:
        menu = QMenu(self)
        folder_act = menu.addAction("Open Save Folder…")
        file_act = menu.addAction("Open game File…")
        chosen = menu.exec(
            self._drop_zone.browse_button.mapToGlobal(
                self._drop_zone.browse_button.rect().bottomLeft()
            )
        )
        if chosen is folder_act:
            path = QFileDialog.getExistingDirectory(
                self,
                "Open Space Haven Save Folder",
                str(Path.home()),
            )
            if path:
                self.file_selected.emit(path)
        elif chosen is file_act:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Space Haven Save File",
                str(Path.home()),
                "Space Haven Save (game);;All Files (*)",
            )
            if path:
                self.file_selected.emit(path)
