"""ships_tab.py – Ship editor tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QEvent, QRect, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.save_file import SaveFile, Ship


class _ShipDelegate(QStyledItemDelegate):
    """Paints clone (⧉) and remove (✕) action glyphs on the right of each
    ship list entry and emits the corresponding signal when clicked."""

    remove_requested = Signal(int)
    clone_requested = Signal(int)
    _BTN_W = 24  # width per action button

    def paint(self, painter, option, index) -> None:
        text_opt = QStyleOptionViewItem(option)
        text_opt.rect = option.rect.adjusted(0, 0, -self._BTN_W * 2, 0)
        super().paint(painter, text_opt, index)

        clone_rect = QRect(
            option.rect.right() - self._BTN_W * 2,
            option.rect.top(),
            self._BTN_W,
            option.rect.height(),
        )
        remove_rect = QRect(
            option.rect.right() - self._BTN_W,
            option.rect.top(),
            self._BTN_W,
            option.rect.height(),
        )

        painter.save()
        f = QFont(painter.font())
        f.setPointSize(13)
        painter.setFont(f)
        painter.setPen(QColor("#89dceb"))
        painter.drawText(clone_rect, Qt.AlignmentFlag.AlignCenter, "\u29c9")
        painter.setPen(QColor("#f38ba8"))
        painter.drawText(remove_rect, Qt.AlignmentFlag.AlignCenter, "\u2715")
        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:
        if event.type() == QEvent.Type.MouseButtonRelease:
            pos = event.position().toPoint()
            clone_rect = QRect(
                option.rect.right() - self._BTN_W * 2,
                option.rect.top(),
                self._BTN_W,
                option.rect.height(),
            )
            remove_rect = QRect(
                option.rect.right() - self._BTN_W,
                option.rect.top(),
                self._BTN_W,
                option.rect.height(),
            )
            if clone_rect.contains(pos):
                self.clone_requested.emit(index.row())
                return True
            if remove_rect.contains(pos):
                self.remove_requested.emit(index.row())
                return True
        return super().editorEvent(event, model, option, index)

    def helpEvent(self, event, view, option, index) -> bool:
        pos = event.pos()
        clone_rect = QRect(
            option.rect.right() - self._BTN_W * 2,
            option.rect.top(),
            self._BTN_W,
            option.rect.height(),
        )
        remove_rect = QRect(
            option.rect.right() - self._BTN_W,
            option.rect.top(),
            self._BTN_W,
            option.rect.height(),
        )
        if clone_rect.contains(pos):
            QToolTip.showText(event.globalPos(), "Duplicate ship", view)
            return True
        if remove_rect.contains(pos):
            QToolTip.showText(event.globalPos(), "Remove ship", view)
            return True
        return super().helpEvent(event, view, option, index)


class ShipsTab(QWidget):
    status_message = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._current_ship: Ship | None = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left panel: ship list ────────────────────────────────────
        left = QWidget()
        left.setObjectName("CrewLeftPanel")
        left.setFixedWidth(240)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(10, 14, 10, 14)
        lv.setSpacing(8)

        ships_hdr = QLabel("SHIPS")
        ships_hdr.setObjectName("PanelSectionLabel")
        lv.addWidget(ships_hdr)

        self._ship_list = QListWidget()
        self._ship_list.setObjectName("CrewList")
        self._ship_list.currentRowChanged.connect(self._on_ship_selected)
        self._ship_delegate = _ShipDelegate(self._ship_list)
        self._ship_delegate.remove_requested.connect(self._on_ship_remove_requested)
        self._ship_delegate.clone_requested.connect(self._clone_ship)
        self._ship_list.setItemDelegate(self._ship_delegate)
        lv.addWidget(self._ship_list)

        root.addWidget(left)

        # ── Right panel: ship details ────────────────────────────────
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(24, 24, 24, 24)
        rv.setSpacing(16)

        self._placeholder = QLabel("Select a ship to edit.")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setObjectName("StatCardDesc")
        rv.addWidget(self._placeholder, alignment=Qt.AlignmentFlag.AlignCenter)

        self._detail_widget = QWidget()
        self._detail_widget.setVisible(False)
        dv = QVBoxLayout(self._detail_widget)
        dv.setContentsMargins(0, 0, 0, 0)
        dv.setSpacing(16)

        # Name editing
        name_group = QGroupBox("Ship Identity")
        name_layout = QFormLayout(name_group)
        name_layout.setContentsMargins(16, 20, 16, 16)
        name_layout.setSpacing(10)

        self._name_edit = QLineEdit()
        self._name_edit.setObjectName("NameEdit")
        self._name_edit.setPlaceholderText("Ship name…")
        self._name_edit.editingFinished.connect(self._rename_ship)
        name_layout.addRow("Name:", self._name_edit)

        dv.addWidget(name_group)

        # Info (read-only)
        info_group = QGroupBox("Info")
        info_layout = QFormLayout(info_group)
        info_layout.setContentsMargins(16, 20, 16, 16)
        info_layout.setSpacing(10)

        self._info_sid = QLabel("—")
        self._info_sid.setObjectName("InfoValue")
        info_layout.addRow(QLabel("Ship ID:"), self._info_sid)

        self._info_crew = QLabel("—")
        self._info_crew.setObjectName("InfoValue")
        info_layout.addRow(QLabel("Crew members:"), self._info_crew)

        self._info_pos = QLabel("—")
        self._info_pos.setObjectName("InfoValue")
        info_layout.addRow(QLabel("Sector position:"), self._info_pos)

        self._info_size = QLabel("—")
        self._info_size.setObjectName("InfoValue")
        info_layout.addRow(QLabel("Grid size (WxH):" ), self._info_size)

        for lbl in info_group.findChildren(QLabel):
            lbl.setObjectName(lbl.objectName() or "InfoKey")

        dv.addWidget(info_group)

        dv.addStretch()
        rv.addWidget(self._detail_widget)
        rv.addStretch()

        root.addWidget(right)

    # ------------------------------------------------------------------
    # Load / Clear
    # ------------------------------------------------------------------

    def load(self, save: SaveFile) -> None:
        self._save = save
        self._current_ship = None
        self._ship_list.blockSignals(True)
        self._ship_list.clear()
        for ship in save.ships:
            item = QListWidgetItem(ship.name)
            item.setData(Qt.ItemDataRole.UserRole, ship)
            self._ship_list.addItem(item)
        self._ship_list.blockSignals(False)
        self._detail_widget.setVisible(False)
        self._placeholder.setVisible(True)
        if save.ships:
            self._ship_list.setCurrentRow(0)

    def clear(self) -> None:
        self._save = None
        self._current_ship = None
        self._ship_list.clear()
        self._detail_widget.setVisible(False)
        self._placeholder.setVisible(True)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_ship_selected(self, row: int) -> None:
        if row < 0 or self._save is None:
            self._current_ship = None
            self._detail_widget.setVisible(False)
            self._placeholder.setVisible(True)
            return
        item = self._ship_list.item(row)
        if item is None:
            return
        ship = item.data(Qt.ItemDataRole.UserRole)
        self._current_ship = ship
        self._populate_ship(ship)
        self._detail_widget.setVisible(True)
        self._placeholder.setVisible(False)

    def _populate_ship(self, ship: Ship) -> None:
        self._name_edit.setText(ship.name)
        self._info_sid.setText(str(ship.sid))
        crew_count = sum(1 for c in self._save.characters if c.ship_sid == ship.sid)
        self._info_crew.setText(str(crew_count))
        self._info_pos.setText(f"({ship.ox}, {ship.oy})")
        w_sq = max(1, round(ship.sx / 28))
        h_sq = max(1, round(ship.sy / 28))
        self._info_size.setText(f"{w_sq} × {h_sq}")

    def _on_ship_remove_requested(self, row: int) -> None:
        if self._save is None:
            return
        item = self._ship_list.item(row)
        if item is None:
            return
        ship = item.data(Qt.ItemDataRole.UserRole)
        if len(self._save.ships) <= 1:
            QMessageBox.warning(self, "Remove Ship", "Cannot remove the last ship.")
            return
        self._save.remove_ship(ship)
        self._ship_list.takeItem(row)
        if self._current_ship is ship:
            self._current_ship = None
            self._detail_widget.setVisible(False)
            self._placeholder.setVisible(True)
        self.status_message.emit(f'Ship "{ship.name}" removed (unsaved).')

    def _rename_ship(self) -> None:
        if self._save is None or self._current_ship is None:
            return
        name = self._name_edit.text().strip()
        if not name:
            return
        self._save.rename_ship(self._current_ship, name)
        # Refresh list item
        for i in range(self._ship_list.count()):
            item = self._ship_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) is self._current_ship:
                item.setText(name)
                break
        self.status_message.emit(f'Ship renamed to "{name}" (unsaved).')

    def _unique_copy_name(self, base_name: str) -> str:
        """Return a collision-free clone name based on *base_name*."""
        existing = {self._ship_list.item(i).text() for i in range(self._ship_list.count())}
        candidate = f"{base_name} - Copy"
        if candidate not in existing:
            return candidate
        n = 2
        while True:
            candidate = f"{base_name} - Copy {n}"
            if candidate not in existing:
                return candidate
            n += 1

    def _clone_ship(self, row: int) -> None:
        if self._save is None:
            return
        item = self._ship_list.item(row)
        if item is None:
            return
        source = item.data(Qt.ItemDataRole.UserRole)
        new_name = self._unique_copy_name(source.name)
        try:
            new_ship = self._save.add_ship(source, new_name)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Failed to clone ship:\n{exc}")
            return
        new_item = QListWidgetItem(new_ship.name)
        new_item.setData(Qt.ItemDataRole.UserRole, new_ship)
        self._ship_list.addItem(new_item)
        self._ship_list.setCurrentItem(new_item)
        self._ship_list.updateGeometry()
        self.status_message.emit(f'Ship "{new_name}" cloned (unsaved).')

