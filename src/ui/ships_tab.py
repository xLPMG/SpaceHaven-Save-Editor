"""ships_tab.py – Ship editor tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QEvent, QRect, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.save_file import SaveFile, Ship


class _ShipRemoveDelegate(QStyledItemDelegate):
    """Paints a ✕ glyph on the right of each ship list entry and emits
    *remove_requested(row)* when it is clicked."""

    remove_requested = Signal(int)
    _BTN_W = 22

    def paint(self, painter, option, index) -> None:
        text_opt = QStyleOptionViewItem(option)
        text_opt.rect = option.rect.adjusted(0, 0, -self._BTN_W, 0)
        super().paint(painter, text_opt, index)
        btn_rect = QRect(
            option.rect.right() - self._BTN_W,
            option.rect.top(),
            self._BTN_W,
            option.rect.height(),
        )
        painter.save()
        painter.setPen(QColor("#f38ba8"))
        f = QFont(painter.font())
        f.setPointSize(10)
        painter.setFont(f)
        painter.drawText(btn_rect, Qt.AlignmentFlag.AlignCenter, "\u2715")
        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:
        if event.type() == QEvent.Type.MouseButtonRelease:
            btn_rect = QRect(
                option.rect.right() - self._BTN_W,
                option.rect.top(),
                self._BTN_W,
                option.rect.height(),
            )
            if btn_rect.contains(event.position().toPoint()):
                self.remove_requested.emit(index.row())
                return True
        return super().editorEvent(event, model, option, index)


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
        left.setFixedWidth(200)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(10, 14, 10, 14)
        lv.setSpacing(8)

        ships_hdr = QLabel("SHIPS")
        ships_hdr.setObjectName("PanelSectionLabel")
        lv.addWidget(ships_hdr)

        self._ship_list = QListWidget()
        self._ship_list.setObjectName("CrewList")
        self._ship_list.currentRowChanged.connect(self._on_ship_selected)
        self._ship_delegate = _ShipRemoveDelegate(self._ship_list)
        self._ship_delegate.remove_requested.connect(self._on_ship_remove_requested)
        self._ship_list.setItemDelegate(self._ship_delegate)
        lv.addWidget(self._ship_list)

        add_ship_btn = QPushButton("+ Add Ship")
        add_ship_btn.setObjectName("InlineButton")
        add_ship_btn.clicked.connect(self._add_ship)
        lv.addWidget(add_ship_btn)

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
        name_layout.addRow("Name:", self._name_edit)

        rename_btn = QPushButton("Rename")
        rename_btn.setObjectName("InlineButton")
        rename_btn.setFixedWidth(100)
        rename_btn.clicked.connect(self._rename_ship)
        name_layout.addRow("", rename_btn)

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

        # Resize
        resize_group = QGroupBox("Resize Ship")
        resize_layout = QFormLayout(resize_group)
        resize_layout.setContentsMargins(16, 20, 16, 16)
        resize_layout.setSpacing(10)

        self._width_spin = QSpinBox()
        self._width_spin.setRange(1, 10)
        self._width_spin.setSuffix(" squares")
        resize_layout.addRow("Width:", self._width_spin)

        self._height_spin = QSpinBox()
        self._height_spin.setRange(1, 10)
        self._height_spin.setSuffix(" squares")
        resize_layout.addRow("Height:", self._height_spin)

        resize_note = QLabel("1 square ≈ 28 units • max 8×8")
        resize_note.setObjectName("StatCardDesc")
        resize_layout.addRow(resize_note)

        resize_btn = QPushButton("Apply Size")
        resize_btn.setObjectName("InlineButton")
        resize_btn.setFixedWidth(100)
        resize_btn.clicked.connect(self._resize_ship)
        resize_layout.addRow("", resize_btn)

        dv.addWidget(resize_group)
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
        self._info_pos.setText(f"({ship.sx}, {ship.sy})")
        w_sq = max(1, round(ship.sx / 28))
        h_sq = max(1, round(ship.sy / 28))
        self._info_size.setText(f"{w_sq} × {h_sq}")
        self._width_spin.setValue(w_sq)
        self._height_spin.setValue(h_sq)

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

    def _resize_ship(self) -> None:
        if self._save is None or self._current_ship is None:
            return
        w_sq = self._width_spin.value()
        h_sq = self._height_spin.value()
        new_sx = w_sq * 28
        new_sy = h_sq * 28
        ship = self._current_ship
        ship.sx = new_sx
        ship.sy = new_sy
        if ship.element is not None:
            ship.element.set("sx", str(new_sx))
            ship.element.set("sy", str(new_sy))
        self._info_size.setText(f"{w_sq} × {h_sq}")
        self.status_message.emit(
            f'Ship "{ship.name}" resized to {w_sq}×{h_sq} squares (unsaved).'
        )

    def _add_ship(self) -> None:
        if self._save is None or not self._save.ships:
            QMessageBox.warning(self, "No Save", "Open a save file first.")
            return

        # ── Dialog ──────────────────────────────────────────────────
        dlg = QDialog(self)
        dlg.setWindowTitle("Add New Ship")
        dlg.setMinimumWidth(360)
        form = QFormLayout(dlg)
        form.setContentsMargins(16, 16, 16, 16)
        form.setSpacing(12)

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("e.g. HSS PROMETHEUS")
        form.addRow("New ship name:", name_edit)

        clone_combo = QComboBox()
        for ship in self._save.ships:
            clone_combo.addItem(ship.name, ship)
        form.addRow("Clone layout from:", clone_combo)

        note = QLabel(
            "The new ship will be an identical copy of the chosen ship's\n"
            "layout and inventory, placed at the same sector position.\n"
            "Crew will not be copied."
        )
        note.setObjectName("StatCardDesc")
        note.setWordWrap(True)
        form.addRow(note)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        form.addRow(buttons)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new_name = name_edit.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Invalid Name", "Ship name cannot be empty.")
            return

        source_ship = clone_combo.currentData()

        # ── Create the ship ─────────────────────────────────────────
        try:
            new_ship = self._save.add_ship(source_ship, new_name)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Failed to add ship:\n{exc}")
            return

        # ── Update the list ─────────────────────────────────────────
        item = QListWidgetItem(new_ship.name)
        item.setData(Qt.ItemDataRole.UserRole, new_ship)
        # Insert in sorted position
        inserted = False
        for i in range(self._ship_list.count()):
            if self._ship_list.item(i).text() > new_ship.name:
                self._ship_list.insertItem(i, item)
                inserted = True
                break
        if not inserted:
            self._ship_list.addItem(item)

        self._ship_list.setCurrentItem(item)
        self.status_message.emit(f'Ship "{new_name}" added (unsaved).')

