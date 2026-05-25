"""storage_tab.py – Ship inventory / storage editor tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.save_file import SaveFile, Ship, StorageContainer, StorageItem

from src.game_data import STORAGE_IDS


class StorageTab(QWidget):
    status_message = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._current_ship: Ship | None = None
        self._current_container: StorageContainer | None = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        # ── Left panel ──────────────────────────────────────────────
        left = QWidget()
        left.setObjectName("CrewLeftPanel")
        left.setMinimumWidth(210)
        left.setMaximumWidth(290)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(14, 14, 8, 14)
        lv.setSpacing(8)

        ship_lbl = QLabel("Ship")
        ship_lbl.setObjectName("PanelSectionLabel")
        lv.addWidget(ship_lbl)

        self._ship_combo = QComboBox()
        self._ship_combo.currentIndexChanged.connect(self._on_ship_changed)
        lv.addWidget(self._ship_combo)

        containers_lbl = QLabel("Storage Containers")
        containers_lbl.setObjectName("PanelSectionLabel")
        lv.addSpacing(4)
        lv.addWidget(containers_lbl)

        self._container_list = QListWidget()
        self._container_list.setObjectName("CrewList")
        self._container_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._container_list.currentRowChanged.connect(self._on_container_selected)
        lv.addWidget(self._container_list)

        self._container_info = QLabel("")
        self._container_info.setObjectName("StatCardDesc")
        self._container_info.setWordWrap(True)
        lv.addWidget(self._container_info)

        splitter.addWidget(left)

        # ── Right panel ─────────────────────────────────────────────
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(8, 14, 14, 14)
        rv.setSpacing(8)

        # Search/filter bar
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        filter_icon = QLabel("🔍")
        filter_row.addWidget(filter_icon)
        self._filter_edit = QLineEdit()
        self._filter_edit.setObjectName("FilterEdit")
        self._filter_edit.setPlaceholderText("Filter items…")
        self._filter_edit.setClearButtonEnabled(True)
        self._filter_edit.textChanged.connect(self._apply_filter)
        filter_row.addWidget(self._filter_edit)
        rv.addLayout(filter_row)

        # Item table
        self._items_table = QTableWidget(0, 2)
        self._items_table.setHorizontalHeaderLabels(["Item", "Quantity"])
        hdr = self._items_table.horizontalHeader()
        hdr.setSectionResizeMode(0, hdr.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, hdr.ResizeMode.Fixed)
        self._items_table.setColumnWidth(1, 120)
        self._items_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._items_table.verticalHeader().setVisible(False)
        rv.addWidget(self._items_table)

        # Toolbar: remove
        qty_row = QHBoxLayout()
        qty_row.setSpacing(8)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setObjectName("DangerButton")
        remove_btn.clicked.connect(self._remove_item)
        qty_row.addWidget(remove_btn)
        qty_row.addStretch()
        rv.addLayout(qty_row)

        # Add item row
        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        add_label = QLabel("Add item:")
        add_label.setObjectName("PanelSectionLabel")
        add_row.addWidget(add_label)

        self._add_item_combo = QComboBox()
        self._add_item_combo.setEditable(True)
        self._add_item_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        for name, item_id in sorted((v, k) for k, v in STORAGE_IDS.items()):
            self._add_item_combo.addItem(f"{name}  [{item_id}]", item_id)
        add_row.addWidget(self._add_item_combo)

        self._add_qty_spin = QSpinBox()
        self._add_qty_spin.setRange(1, 1_000_000)
        self._add_qty_spin.setValue(100)
        self._add_qty_spin.setFixedWidth(90)
        add_row.addWidget(self._add_qty_spin)

        add_btn = QPushButton("Add")
        add_btn.setFixedWidth(60)
        add_btn.clicked.connect(self._add_item)
        add_row.addWidget(add_btn)

        rv.addLayout(add_row)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self._set_right_enabled(False)

    # ------------------------------------------------------------------
    # Load / Clear
    # ------------------------------------------------------------------

    def load(self, save: SaveFile) -> None:
        self._save = save
        self._current_ship = None
        self._current_container = None

        self._ship_combo.blockSignals(True)
        self._ship_combo.clear()
        for ship in save.ships:
            self._ship_combo.addItem(ship.name, ship)
        self._ship_combo.blockSignals(False)

        if save.ships:
            self._ship_combo.setCurrentIndex(0)
            self._on_ship_changed(0)

    def clear(self) -> None:
        self._save = None
        self._current_ship = None
        self._current_container = None
        self._ship_combo.blockSignals(True)
        self._ship_combo.clear()
        self._ship_combo.blockSignals(False)
        self._container_list.clear()
        self._container_info.setText("")
        self._items_table.setRowCount(0)
        self._set_right_enabled(False)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_ship_changed(self, index: int) -> None:
        if self._save is None or index < 0:
            return
        ship: Ship = self._ship_combo.itemData(index)
        self._current_ship = ship
        self._current_container = None

        containers = self._save.get_storage_containers(ship)

        self._container_list.blockSignals(True)
        self._container_list.clear()
        for container in sorted(containers, key=lambda c: c.display_name):
            item = QListWidgetItem(container.display_name)
            item.setData(Qt.ItemDataRole.UserRole, container)
            self._container_list.addItem(item)
        self._container_list.blockSignals(False)

        self._items_table.setRowCount(0)
        total = sum(len(c.items) for c in containers)
        self._container_info.setText(
            f"{len(containers)} containers  •  {total} item types"
        )
        self._set_right_enabled(False)

    def _on_container_selected(self, row: int) -> None:
        if row < 0:
            self._current_container = None
            self._items_table.setRowCount(0)
            self._set_right_enabled(False)
            return
        item = self._container_list.item(row)
        if item is None:
            return
        container: StorageContainer = item.data(Qt.ItemDataRole.UserRole)
        self._current_container = container
        self._populate_items(container)
        self._set_right_enabled(True)

    # ------------------------------------------------------------------
    # Populate
    # ------------------------------------------------------------------

    def _populate_items(self, container: StorageContainer) -> None:
        self._filter_edit.clear()
        self._items_table.setRowCount(0)
        for storage_item in container.items:
            row = self._items_table.rowCount()
            self._items_table.insertRow(row)

            name_cell = QTableWidgetItem(storage_item.name)
            name_cell.setFlags(name_cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_cell.setData(Qt.ItemDataRole.UserRole, storage_item)
            self._items_table.setItem(row, 0, name_cell)

            qty_spin = QSpinBox()
            qty_spin.setRange(1, 1_000_000)
            qty_spin.setValue(storage_item.quantity)
            qty_spin.valueChanged.connect(self._apply_quantities)
            self._items_table.setCellWidget(row, 1, qty_spin)

    # ------------------------------------------------------------------
    # Apply / Add / Remove
    # ------------------------------------------------------------------

    def _apply_quantities(self) -> None:
        if self._save is None or self._current_container is None:
            return
        for row in range(self._items_table.rowCount()):
            storage_item: StorageItem = self._items_table.item(row, 0).data(
                Qt.ItemDataRole.UserRole
            )
            spin: QSpinBox = self._items_table.cellWidget(row, 1)
            self._save.set_storage_quantity(storage_item, spin.value())
        self.status_message.emit("Quantities applied (unsaved).")

    def _add_item(self) -> None:
        if self._save is None or self._current_container is None:
            return
        item_id: int = self._add_item_combo.currentData()
        qty = self._add_qty_spin.value()
        if item_id is None:
            QMessageBox.warning(self, "Add Item", "Please select a valid item.")
            return
        self._save.add_storage_item(self._current_container, item_id, qty)
        self._populate_items(self._current_container)
        self.status_message.emit(
            f"Added {qty}x {STORAGE_IDS.get(item_id, str(item_id))} (unsaved)."
        )

    def _remove_item(self) -> None:
        if self._save is None or self._current_container is None:
            return
        selected = self._items_table.selectedItems()
        if not selected:
            QMessageBox.information(
                self, "Remove Item", "Select an item row to remove."
            )
            return
        row = self._items_table.currentRow()
        storage_item: StorageItem = self._items_table.item(row, 0).data(
            Qt.ItemDataRole.UserRole
        )
        self._save.remove_storage_item(self._current_container, storage_item)
        self._items_table.removeRow(row)
        self.status_message.emit(f"Removed {storage_item.name} (unsaved).")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _apply_filter(self, text: str) -> None:
        query = text.strip().lower()
        for row in range(self._items_table.rowCount()):
            item = self._items_table.item(row, 0)
            match = query == "" or (item is not None and query in item.text().lower())
            self._items_table.setRowHidden(row, not match)

    def _set_right_enabled(self, enabled: bool) -> None:
        self._filter_edit.setEnabled(enabled)
        self._items_table.setEnabled(enabled)
        self._add_item_combo.setEnabled(enabled)
        self._add_qty_spin.setEnabled(enabled)
