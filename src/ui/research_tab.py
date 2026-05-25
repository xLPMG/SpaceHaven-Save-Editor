"""research_tab.py – Technology research viewer and editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.save_file import ResearchEntry, SaveFile


# ---------------------------------------------------------------------------
# Custom item delegate – rich row rendering
# ---------------------------------------------------------------------------


class _TechDelegate(QStyledItemDelegate):
    """Paints each research entry as a styled row with accent strip + badge."""

    _DONE_COLOR = QColor("#04D912")
    _PROG_COLOR = QColor("#FF8800")
    _NONE_COLOR = QColor("#1A4A58")

    _BG_EVEN = QColor("#050A0B")
    _BG_ODD = QColor("#070E10")
    _BG_SEL = QColor("#071820")
    _SEP = QColor(0, 216, 240, 18)

    _TEXT_MAIN = QColor("#DDF0F5")
    _TEXT_DIM = QColor("#3BBECE")

    def sizeHint(self, option: QStyleOptionViewItem, index) -> QSize:  # noqa: N802
        return QSize(option.rect.width(), 48)

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index
    ) -> None:  # noqa: N802
        entry: ResearchEntry | None = index.data(Qt.ItemDataRole.UserRole)
        if entry is None:
            super().paint(painter, option, index)
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = option.rect
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)

        # Row background
        if selected:
            painter.fillRect(r, self._BG_SEL)
        elif hovered:
            painter.fillRect(r, QColor("#0A1618"))
        else:
            painter.fillRect(r, self._BG_EVEN if index.row() % 2 == 0 else self._BG_ODD)

        # Left accent strip (4 px)
        accent = (
            self._DONE_COLOR
            if entry.done
            else self._PROG_COLOR if entry.in_progress else self._NONE_COLOR
        )
        painter.fillRect(QRect(r.x(), r.y(), 4, r.height()), accent)

        # Tech name
        text_color = (
            self._TEXT_DIM
            if (not entry.done and not entry.in_progress)
            else self._TEXT_MAIN
        )
        font = painter.font()
        font.setPointSize(13)
        painter.setFont(font)
        painter.setPen(text_color)
        name_rect = QRect(r.x() + 16, r.y(), r.width() - 158, r.height())
        painter.drawText(
            name_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            entry.name,
        )

        # Status badge
        if entry.done:
            badge_txt = "COMPLETE"
            badge_fg = self._DONE_COLOR
            badge_bg = QColor(4, 217, 18, 28)
        elif entry.in_progress:
            badge_txt = "IN PROGRESS"
            badge_fg = self._PROG_COLOR
            badge_bg = QColor(255, 136, 0, 28)
        else:
            badge_txt = "NOT DONE"
            badge_fg = self._NONE_COLOR
            badge_bg = QColor(26, 74, 88, 20)

        bw, bh = 114, 24
        badge_rect = QRect(
            r.right() - bw - 12,
            r.y() + (r.height() - bh) // 2,
            bw,
            bh,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(badge_bg)
        painter.drawRoundedRect(badge_rect, 4, 4)

        bf = painter.font()
        bf.setPointSize(10)
        bf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        painter.setFont(bf)
        painter.setPen(badge_fg)
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, badge_txt)

        # Separator
        painter.setPen(self._SEP)
        painter.drawLine(r.x() + 16, r.bottom(), r.right(), r.bottom())

        painter.restore()


# ---------------------------------------------------------------------------
# Main tab widget
# ---------------------------------------------------------------------------


class ResearchTab(QWidget):
    status_message = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._all_entries: list[ResearchEntry] = []
        self._active_filter = "all"
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(14)

        # ── Stats banner ─────────────────────────────────────────────
        banner = QFrame()
        banner.setObjectName("ResearchBanner")
        banner.setFixedHeight(82)
        bl = QVBoxLayout(banner)
        bl.setContentsMargins(20, 12, 20, 12)
        bl.setSpacing(6)

        counts_row = QHBoxLayout()
        counts_row.setSpacing(0)

        self._count_done, w_done = self._make_stat_widget("0", "COMPLETE", "#04D912")
        self._count_progress, w_progress = self._make_stat_widget(
            "0", "IN PROGRESS", "#FF8800"
        )
        self._count_remain, w_remain = self._make_stat_widget(
            "0", "REMAINING", "#3BBECE"
        )
        self._count_total, w_total = self._make_stat_widget("0", "TOTAL", "#1A4A58")

        for w in (w_done, w_progress, w_remain, w_total):
            counts_row.addWidget(w)
            counts_row.addStretch(1)
        counts_row.addStretch(-1)
        bl.addLayout(counts_row)

        self._progress_bar = QProgressBar()
        self._progress_bar.setObjectName("ResearchProgress")
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(6)
        self._progress_bar.setRange(0, 1)
        self._progress_bar.setValue(0)
        bl.addWidget(self._progress_bar)

        root.addWidget(banner)

        # ── Filter + search ──────────────────────────────────────────
        filter_row = QHBoxLayout()
        filter_row.setSpacing(6)

        self._search = QLineEdit()
        self._search.setObjectName("NameEdit")
        self._search.setPlaceholderText("Filter technologies…")
        self._search.textChanged.connect(self._refresh_list)
        filter_row.addWidget(self._search, 1)

        filter_row.addSpacing(8)
        for label, attr in [
            ("All", "all"),
            ("Done", "done"),
            ("In Progress", "progress"),
            ("Not Done", "todo"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("FilterButton")
            btn.setCheckable(True)
            btn.setChecked(attr == "all")
            btn.setProperty("filterAttr", attr)
            btn.clicked.connect(lambda _, a=attr: self._set_filter(a))
            filter_row.addWidget(btn)

        root.addLayout(filter_row)

        # ── Tech list ────────────────────────────────────────────────
        self._list = QListWidget()
        self._list.setObjectName("TechList")
        self._list.setItemDelegate(_TechDelegate(self._list))
        self._list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._list.setMouseTracking(True)
        self._list.itemSelectionChanged.connect(self._on_selection_changed)
        root.addWidget(self._list)

        # ── Action buttons ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self._complete_sel_btn = QPushButton("Complete Selected")
        self._complete_sel_btn.setObjectName("CompleteButton")
        self._complete_sel_btn.setEnabled(False)
        self._complete_sel_btn.clicked.connect(self._complete_selected)
        btn_row.addWidget(self._complete_sel_btn)

        self._complete_all_btn = QPushButton("Complete All")
        self._complete_all_btn.setObjectName("CompleteButton")
        self._complete_all_btn.setEnabled(False)
        self._complete_all_btn.clicked.connect(self._complete_all)
        btn_row.addWidget(self._complete_all_btn)

        root.addLayout(btn_row)

    @staticmethod
    def _make_stat_widget(
        number: str, caption: str, color: str
    ) -> tuple[QLabel, QWidget]:
        """Return (num_label, container_widget) for the stats banner."""
        w = QWidget()
        w.setStyleSheet("background-color: transparent;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(1)
        num_lbl = QLabel(number)
        num_lbl.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
        cap_lbl = QLabel(caption)
        cap_lbl.setStyleSheet("color: #1A4A58; font-size: 9px; letter-spacing: 1px;")
        v.addWidget(num_lbl)
        v.addWidget(cap_lbl)
        return num_lbl, w

    # ------------------------------------------------------------------
    # Load / Clear
    # ------------------------------------------------------------------

    def load(self, save: SaveFile) -> None:
        self._save = save
        self._all_entries = list(save.research)
        self._complete_all_btn.setEnabled(True)
        self._search.setText("")
        self._active_filter = "all"
        for btn in self.findChildren(QPushButton):
            if btn.property("filterAttr") is not None:
                btn.setChecked(btn.property("filterAttr") == "all")
        self._refresh_list()

    def clear(self) -> None:
        self._save = None
        self._all_entries = []
        self._list.clear()
        self._complete_all_btn.setEnabled(False)
        self._complete_sel_btn.setEnabled(False)
        self._update_banner(0, 0, 0, 0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _refresh_list(self) -> None:
        query = self._search.text().strip().lower()
        self._list.blockSignals(True)
        self._list.clear()
        for entry in self._all_entries:
            if query and query not in entry.name.lower():
                continue
            if self._active_filter == "done" and not entry.done:
                continue
            if self._active_filter == "progress" and not entry.in_progress:
                continue
            if self._active_filter == "todo" and (entry.done or entry.in_progress):
                continue
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self._list.addItem(item)
        self._list.blockSignals(False)
        self._on_selection_changed()
        total = len(self._all_entries)
        done = sum(1 for e in self._all_entries if e.done)
        prog = sum(1 for e in self._all_entries if e.in_progress)
        self._update_banner(total, done, prog, total - done - prog)

    def _update_banner(self, total: int, done: int, prog: int, rem: int) -> None:
        self._count_done.setText(str(done))
        self._count_progress.setText(str(prog))
        self._count_remain.setText(str(rem))
        self._count_total.setText(str(total))
        self._progress_bar.setRange(0, max(total, 1))
        self._progress_bar.setValue(done)

    def _set_filter(self, attr: str) -> None:
        self._active_filter = attr
        for btn in self.findChildren(QPushButton):
            if btn.property("filterAttr") is not None:
                btn.setChecked(btn.property("filterAttr") == attr)
        self._refresh_list()

    def _on_selection_changed(self) -> None:
        selected = self._list.selectedItems()
        has_incomplete = any(
            not item.data(Qt.ItemDataRole.UserRole).done for item in selected
        )
        self._complete_sel_btn.setEnabled(bool(selected) and has_incomplete)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _complete_selected(self) -> None:
        if self._save is None:
            return
        count = 0
        for item in self._list.selectedItems():
            entry: ResearchEntry = item.data(Qt.ItemDataRole.UserRole)
            if not entry.done:
                self._save.complete_research(entry)
                count += 1
        if count:
            self._refresh_list()
            self.status_message.emit(f"Completed {count} research item(s) (unsaved).")

    def _complete_all(self) -> None:
        if self._save is None:
            return
        count = self._save.complete_all_research()
        self._refresh_list()
        if count:
            self.status_message.emit(
                f"Completed all {count} remaining research items (unsaved)."
            )
        else:
            self.status_message.emit("All research was already complete.")
