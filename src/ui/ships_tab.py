"""ships_tab.py – Ship editor tab."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.save_file import SaveFile, Ship


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
        self._info_pos.setText(f"({ship.sx}, {ship.sy})")

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
        self.status_message.emit(f"Ship renamed to \"{name}\" (unsaved).")
