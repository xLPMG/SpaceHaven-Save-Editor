"""storage_tab.py – Ship inventory / storage editor tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

from collections import Counter

from PySide6.QtCore import QEvent, Qt, Signal
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

from src.game_data import STORAGE_DATA
from src.texts_loader import game_texts
from src.ui.styles import STORAGE_FILTER_ICON_COLOR


class StorageTab(QWidget):
    status_message = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._current_ship: Ship | None = None
        self._current_container: StorageContainer | None = None
        self._container_base_labels: dict[int, str] = {}
        self._build_ui()
        game_texts.on_lang_changed(self._on_lang_changed)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        # Left panel
        left = QWidget()
        left.setObjectName("CrewLeftPanel")
        left.setMinimumWidth(210)
        left.setMaximumWidth(290)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(14, 14, 8, 14)
        lv.setSpacing(8)

        self._ship_lbl = QLabel()
        self._ship_lbl.setObjectName("PanelSectionLabel")
        lv.addWidget(self._ship_lbl)

        self._ship_combo = QComboBox()
        self._ship_combo.currentIndexChanged.connect(self._on_ship_changed)
        lv.addWidget(self._ship_combo)

        self._containers_lbl = QLabel()
        self._containers_lbl.setObjectName("PanelSectionLabel")
        lv.addSpacing(4)
        lv.addWidget(self._containers_lbl)

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

        # Right panel
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(8, 14, 14, 14)
        rv.setSpacing(8)

        # Search/filter bar
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        filter_icon = QLabel("⌕")
        filter_icon.setObjectName("StorageFilterIcon")
        filter_icon.setStyleSheet(f"color: {STORAGE_FILTER_ICON_COLOR.name()};")
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
        self._items_table.setHorizontalHeaderLabels(["", ""])
        hdr = self._items_table.horizontalHeader()
        hdr.setSectionResizeMode(0, hdr.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, hdr.ResizeMode.Fixed)
        self._items_table.setColumnWidth(1, 120)
        self._items_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._items_table.verticalHeader().setVisible(False)
        self._items_table.verticalHeader().setDefaultSectionSize(42)
        self._items_table.itemSelectionChanged.connect(self._sync_remove_enabled)
        rv.addWidget(self._items_table)

        # Toolbar: remove
        qty_row = QHBoxLayout()
        qty_row.setSpacing(8)
        self._remove_btn = QPushButton()
        self._remove_btn.setObjectName("DangerButton")
        self._remove_btn.setEnabled(False)
        self._remove_btn.clicked.connect(self._remove_item)
        qty_row.addWidget(self._remove_btn)
        qty_row.addStretch()
        rv.addLayout(qty_row)

        # Add item row
        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        self._add_label = QLabel()
        self._add_label.setObjectName("PanelSectionLabel")
        add_row.addWidget(self._add_label)

        self._add_item_combo = QComboBox()
        self._add_item_combo.setEditable(True)
        self._add_item_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        for item_id, (en_name, item_tid) in sorted(
            STORAGE_DATA.items(),
            key=lambda x: game_texts.get(x[1][1], x[1][0]),
        ):
            self._add_item_combo.addItem(
                game_texts.get(item_tid, en_name), item_id
            )
        add_row.addWidget(self._add_item_combo)

        self._add_qty_spin = QSpinBox()
        self._add_qty_spin.setRange(1, 1_000_000)
        self._add_qty_spin.setValue(100)
        self._add_qty_spin.setFixedWidth(90)
        add_row.addWidget(self._add_qty_spin)

        self._add_btn = QPushButton()
        self._add_btn.setFixedWidth(60)
        self._add_btn.clicked.connect(self._add_item)
        add_row.addWidget(self._add_btn)

        rv.addLayout(add_row)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self._set_right_enabled(False)
        self.retranslate_ui()

    # ------------------------------------------------------------------
    # Retranslation
    # ------------------------------------------------------------------

    def retranslate_ui(self) -> None:
        """Update all static labels on language change."""
        self._ship_lbl.setText(self.tr("Ship"))
        self._containers_lbl.setText(self.tr("Storage Containers"))
        self._filter_edit.setPlaceholderText(self.tr("Filter items…"))
        self._items_table.setHorizontalHeaderLabels([
            self.tr("Item"),
            self.tr("Quantity"),
        ])
        self._remove_btn.setText(self.tr("Remove Selected"))
        self._add_label.setText(self.tr("Add item:"))
        self._add_btn.setText(self.tr("Add"))

    # ------------------------------------------------------------------
    # Load / Clear
    # ------------------------------------------------------------------

    def load(self, save: SaveFile) -> None:
        self._save = save
        self._current_ship = None
        self._current_container = None
        self._container_list.clear()
        self._container_info.setText("")
        self._items_table.setRowCount(0)
        self._filter_edit.clear()
        self._set_right_enabled(False)

        self._ship_combo.blockSignals(True)
        self._ship_combo.clear()
        for ship in save.ships:
            self._ship_combo.addItem(ship.name, ship)
        self._ship_combo.blockSignals(False)

        if save.ships:
            self._ship_combo.blockSignals(True)
            self._ship_combo.setCurrentIndex(0)
            self._ship_combo.blockSignals(False)
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
            self._current_ship = None
            self._current_container = None
            self._container_list.clear()
            self._container_info.setText("")
            self._items_table.setRowCount(0)
            self._set_right_enabled(False)
            return
        ship: Ship = self._ship_combo.itemData(index)
        if ship is None:
            self._current_ship = None
            self._current_container = None
            self._container_list.clear()
            self._container_info.setText("")
            self._items_table.setRowCount(0)
            self._set_right_enabled(False)
            return
        self._current_ship = ship
        self._current_container = None

        containers = self._save.get_storage_containers(ship)

        # Assign per-type sequential numbers only when the same name appears more than once
        sorted_containers = sorted(containers, key=lambda c: c.display_name)
        name_counts = Counter(c.display_name for c in sorted_containers)
        name_seen: dict[str, int] = {}
        self._container_base_labels = {}
        for container in sorted_containers:
            name = (game_texts.get(container.text_id, container.display_name)
                    if container.text_id else self.tr(container.display_name))
            if name_counts[container.display_name] > 1:
                name_seen[name] = name_seen.get(name, 0) + 1
                self._container_base_labels[id(container)] = f"{name} #{name_seen[name]}"
            else:
                self._container_base_labels[id(container)] = name

        self._container_list.blockSignals(True)
        self._container_list.clear()
        for container in sorted_containers:
            item = QListWidgetItem(self._container_label(container))
            item.setData(Qt.ItemDataRole.UserRole, container)
            self._container_list.addItem(item)
        self._container_list.blockSignals(False)

        self._items_table.setRowCount(0)
        total = sum(len(c.items) for c in containers)
        self._container_info.setText(
            f"{len(containers)} containers  •  {total} item types"
        )
        if containers:
            self._container_list.setCurrentRow(0)
        else:
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
            self._insert_item_row(storage_item)
        self._sync_remove_enabled()

    def refresh_current_container(self) -> None:
        """Re-populate the items table for the currently selected container."""
        if self._current_container is not None:
            self._populate_items(self._current_container)

    def _insert_item_row(self, storage_item: StorageItem) -> int:
        """Append one row for storage_item and return its row index."""
        row = self._items_table.rowCount()
        self._items_table.insertRow(row)

        name_cell = QTableWidgetItem(
            game_texts.get(STORAGE_DATA.get(storage_item.item_id, (storage_item.name, 0))[1], storage_item.name)
        )
        name_cell.setFlags(name_cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
        name_cell.setData(Qt.ItemDataRole.UserRole, storage_item)
        self._items_table.setItem(row, 0, name_cell)

        qty_spin = QSpinBox()
        qty_spin.setRange(1, 1_000_000)
        qty_spin.setValue(storage_item.quantity)
        qty_spin.valueChanged.connect(
            lambda v, item=storage_item: self._on_quantity_changed(item, v)
        )
        self._items_table.setCellWidget(row, 1, qty_spin)
        return row

    def _on_quantity_changed(self, item: StorageItem, value: int) -> None:
        if self._save is None:
            return
        self._save.set_storage_quantity(item, value)
        self._refresh_container_label()
        self.status_message.emit("Quantities applied (unsaved).")

    # ------------------------------------------------------------------
    # Apply / Add / Remove
    # ------------------------------------------------------------------

    def _add_item(self) -> None:
        if self._save is None or self._current_container is None:
            return
        item_id: int = self._add_item_combo.currentData()
        qty = self._add_qty_spin.value()
        if item_id is None:
            QMessageBox.warning(self, "Add Item", "Please select a valid item.")
            return
        container = self._current_container
        already_present = any(i.item_id == item_id for i in container.items)
        if (
            not already_present
            and container.capacity > 0
            and sum(i.quantity for i in container.items) + qty > container.capacity
        ):
            QMessageBox.warning(
                self,
                "Storage Full",
                f"Adding {qty} would exceed this container's capacity of {container.capacity}.\n"
                "Reduce the quantity or remove some items first.",
            )
            return
        self._save.add_storage_item(self._current_container, item_id, qty)
        # Always rebuild the table so sort order and spinbox values are correct
        # regardless of whether the item was new or stacked onto an existing one.
        self._populate_items(self._current_container)
        self._refresh_container_label()
        self.status_message.emit(
            f"Added {qty}x {game_texts.get(STORAGE_DATA.get(item_id, (str(item_id), 0))[1], STORAGE_DATA.get(item_id, (str(item_id), 0))[0])} (unsaved)."
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
        if row < 0:
            return
        name_cell = self._items_table.item(row, 0)
        if name_cell is None:
            return
        storage_item: StorageItem = name_cell.data(Qt.ItemDataRole.UserRole)
        self._save.remove_storage_item(self._current_container, storage_item)
        self._items_table.removeRow(row)
        self._sync_remove_enabled()
        self._refresh_container_label()
        self.status_message.emit(f"Removed {game_texts.get(STORAGE_DATA.get(storage_item.item_id, (storage_item.name, 0))[1], storage_item.name)} (unsaved).")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _container_label(self, container: StorageContainer) -> str:
        """Return the list display string for a container."""
        base = self._container_base_labels.get(id(container), container.display_name)
        if container.capacity > 0:
            total_qty = sum(i.quantity for i in container.items)
            return f"{base}  —  {total_qty} / {container.capacity}"
        return base

    def _refresh_container_label(self) -> None:
        """Update the list item text for the currently selected container."""
        row = self._container_list.currentRow()
        if row < 0 or self._current_container is None:
            return
        list_item = self._container_list.item(row)
        if list_item is not None:
            list_item.setText(self._container_label(self._current_container))

    def _apply_filter(self, text: str) -> None:
        query = text.strip().lower()
        for row in range(self._items_table.rowCount()):
            item = self._items_table.item(row, 0)
            match = query == "" or (item is not None and query in item.text().lower())
            self._items_table.setRowHidden(row, not match)
        self._sync_remove_enabled()

    def _sync_remove_enabled(self) -> None:
        if not self._items_table.isEnabled():
            self._remove_btn.setEnabled(False)
            return
        for row in range(self._items_table.rowCount()):
            if self._items_table.isRowHidden(row):
                continue
            item = self._items_table.item(row, 0)
            if item is not None and item.isSelected():
                self._remove_btn.setEnabled(True)
                return
        self._remove_btn.setEnabled(False)

    def _on_lang_changed(self, _lang: str) -> None:
        """Re-populate the add-item combo and refresh the items table."""
        # Rebuild container base labels using the now-updated game_texts
        if self._current_ship is not None:
            sorted_containers = [
                self._container_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self._container_list.count())
            ]
            name_counts = Counter(c.display_name for c in sorted_containers)
            name_seen: dict[str, int] = {}
            self._container_base_labels = {}
            for container in sorted_containers:
                name = (game_texts.get(container.text_id, container.display_name)
                        if container.text_id else self.tr(container.display_name))
                if name_counts[container.display_name] > 1:
                    name_seen[name] = name_seen.get(name, 0) + 1
                    self._container_base_labels[id(container)] = f"{name} #{name_seen[name]}"
                else:
                    self._container_base_labels[id(container)] = name
            for i in range(self._container_list.count()):
                list_item = self._container_list.item(i)
                container = list_item.data(Qt.ItemDataRole.UserRole)
                list_item.setText(self._container_label(container))
        current_data = self._add_item_combo.currentData()
        self._add_item_combo.blockSignals(True)
        self._add_item_combo.clear()
        for item_id, (en_name, item_tid) in sorted(
            STORAGE_DATA.items(),
            key=lambda x: game_texts.get(x[1][1], x[1][0]),
        ):
            self._add_item_combo.addItem(
                game_texts.get(item_tid, en_name), item_id
            )
        if current_data is not None:
            idx = next(
                (i for i in range(self._add_item_combo.count())
                 if self._add_item_combo.itemData(i) == current_data),
                0,
            )
            self._add_item_combo.setCurrentIndex(idx)
        self._add_item_combo.blockSignals(False)
        if self._current_container is not None:
            self._populate_items(self._current_container)

    def _set_right_enabled(self, enabled: bool) -> None:
        self._filter_edit.setEnabled(enabled)
        self._items_table.setEnabled(enabled)
        self._add_item_combo.setEnabled(enabled)
        self._add_qty_spin.setEnabled(enabled)
        self._add_btn.setEnabled(enabled)
        if not enabled:
            self._remove_btn.setEnabled(False)
        else:
            self._sync_remove_enabled()
