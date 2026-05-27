"""ships_tab.py - Ship list and detail editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QEvent, QRect, Signal
from PySide6.QtGui import QFont
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

from src.ui.styles import ACTION_CLONE_COLOR, ACTION_REMOVE_COLOR, SHIP_TAB_SECTION_COLOR

if TYPE_CHECKING:
    from src.save_file import SaveFile, Ship

from src.ui.ship_map_widget import ShipMapWidget


class _ShipDelegate(QStyledItemDelegate):
    """Paints clone and remove action buttons on the right of each ship list
    entry and emits the corresponding signal when clicked.
    Section-header rows (UserRole == None) are painted as plain dividers."""

    remove_requested = Signal(int)
    clone_requested = Signal(int)
    _BTN_W = 24  # width per action button

    @staticmethod
    def _is_header(index) -> bool:
        return index.data(Qt.ItemDataRole.UserRole) is None

    def paint(self, painter, option, index) -> None:
        if self._is_header(index):
            # Draw the full-width header without action buttons
            super().paint(painter, option, index)
            return

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
        painter.setPen(ACTION_CLONE_COLOR)
        painter.drawText(clone_rect, Qt.AlignmentFlag.AlignCenter, "\u29c9")
        painter.setPen(ACTION_REMOVE_COLOR)
        painter.drawText(remove_rect, Qt.AlignmentFlag.AlignCenter, "\u2715")
        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:
        if self._is_header(index):
            return False
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
        if self._is_header(index):
            return False
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

        # Left panel: ship list
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

        # Right panel: ship details
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

        # Ship layout map
        map_group = QGroupBox("Ship Layout")
        map_group_layout = QVBoxLayout(map_group)
        map_group_layout.setContentsMargins(8, 12, 8, 8)
        self._ship_map = ShipMapWidget()
        self._ship_map.setMinimumHeight(180)
        map_group_layout.addWidget(self._ship_map)
        dv.addWidget(map_group)

        # Info (read-only)
        info_group = QGroupBox("Info")
        info_layout = QFormLayout(info_group)
        info_layout.setContentsMargins(16, 20, 16, 16)
        info_layout.setSpacing(10)

        self._info_sid = QLabel("—")
        self._info_sid.setObjectName("InfoValue")
        info_layout.addRow(QLabel("Ship ID:"), self._info_sid)

        self._info_location = QLabel("—")
        self._info_location.setObjectName("InfoValue")
        info_layout.addRow(QLabel("Location:"), self._info_location)

        self._info_crew = QLabel("—")
        self._info_crew.setObjectName("InfoValue")
        info_layout.addRow(QLabel("Crew members:"), self._info_crew)

        self._info_pos = QLabel("—")
        self._info_pos.setObjectName("InfoValue")
        info_layout.addRow(QLabel("Sector position:"), self._info_pos)

        self._info_size = QLabel("—")
        self._info_size.setObjectName("InfoValue")
        info_layout.addRow(QLabel("Grid size (WxH):"), self._info_size)

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
        self._rebuild_ship_list(select_first=True)

    def _rebuild_ship_list(
        self,
        selected_ship: Ship | None = None,
        *,
        select_first: bool = False,
    ) -> None:
        self._ship_list.blockSignals(True)
        self._ship_list.clear()

        active = [s for s in self._save.ships if s.in_game_file] if self._save else []
        stored = [s for s in self._save.ships if not s.in_game_file] if self._save else []

        if active:
            self._add_section_header("CURRENT SECTOR")
            for ship in active:
                item = QListWidgetItem(ship.name)
                item.setData(Qt.ItemDataRole.UserRole, ship)
                self._ship_list.addItem(item)

        if stored:
            self._add_section_header("STORED")
            for ship in stored:
                item = QListWidgetItem(ship.name)
                item.setData(Qt.ItemDataRole.UserRole, ship)
                self._ship_list.addItem(item)

        if not active and not stored and self._save is not None:
            for ship in self._save.ships:
                item = QListWidgetItem(ship.name)
                item.setData(Qt.ItemDataRole.UserRole, ship)
                self._ship_list.addItem(item)

        self._ship_list.blockSignals(False)

        row_to_select: int | None = None
        if selected_ship is not None:
            for i in range(self._ship_list.count()):
                item = self._ship_list.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) is selected_ship:
                    row_to_select = i
                    break
        elif select_first:
            for i in range(self._ship_list.count()):
                item = self._ship_list.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) is not None:
                    row_to_select = i
                    break

        if row_to_select is None:
            self._current_ship = None
            self._detail_widget.setVisible(False)
            self._placeholder.setVisible(True)
            self._ship_list.clearSelection()
        else:
            self._ship_list.setCurrentRow(row_to_select)

    def _add_section_header(self, label: str) -> None:
        """Insert a non-selectable section divider into the ship list."""
        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, None)  # sentinel: not a ship
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setForeground(SHIP_TAB_SECTION_COLOR)
        font = item.font()
        font.setPointSize(11)
        font.setBold(True)
        item.setFont(font)
        self._ship_list.addItem(item)

    def clear(self) -> None:
        self._save = None
        self._current_ship = None
        self._ship_list.clear()
        self._ship_map.clear()
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
        if ship is None:
            # Clicked a section header; clear selection without showing detail
            self._current_ship = None
            self._detail_widget.setVisible(False)
            self._placeholder.setVisible(True)
            self._ship_list.clearSelection()
            return
        self._current_ship = ship
        self._populate_ship(ship)
        self._detail_widget.setVisible(True)
        self._placeholder.setVisible(False)

    def _populate_ship(self, ship: Ship) -> None:
        self._name_edit.setText(ship.name)
        self._info_sid.setText(str(ship.sid))
        if ship.in_game_file:
            location_text = "Current Sector"
        else:
            fname = ship.external_path.name if ship.external_path else "Unknown"
            location_text = f"Stored ({fname})"
        self._info_location.setText(location_text)
        crew_count = sum(1 for c in self._save.characters if c.ship_sid == ship.sid)
        self._info_crew.setText(str(crew_count))
        self._info_pos.setText(f"({ship.ox}, {ship.oy})")
        w_sq = max(1, round(ship.sx / 28))
        h_sq = max(1, round(ship.sy / 28))
        self._info_size.setText(f"{w_sq} × {h_sq}")

        tiles = self._save.get_ship_tiles(ship)
        self._ship_map.set_tiles(tiles)

    def _on_ship_remove_requested(self, row: int) -> None:
        if self._save is None:
            return
        item = self._ship_list.item(row)
        if item is None:
            return
        ship = item.data(Qt.ItemDataRole.UserRole)
        if ship is None:
            return  # header row
        if len(self._save.ships) <= 1:
            QMessageBox.warning(self, "Remove Ship", "Cannot remove the last ship.")
            return
        self._save.remove_ship(ship)
        self._rebuild_ship_list(
            selected_ship=None if self._current_ship is ship else self._current_ship
        )
        self.status_message.emit(f'Ship "{ship.name}" removed (unsaved).')

    def _rename_ship(self) -> None:
        if self._save is None or self._current_ship is None:
            return
        name = self._name_edit.text().strip()
        if not name:
            return
        self._save.rename_ship(self._current_ship, name)
        self._rebuild_ship_list(selected_ship=self._current_ship)
        self.status_message.emit(f'Ship renamed to "{name}" (unsaved).')

    def _unique_copy_name(self, base_name: str) -> str:
        """Return a collision-free clone name based on *base_name*."""
        existing = {
            self._ship_list.item(i).text() for i in range(self._ship_list.count())
        }
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
        if source is None:
            return  # header row
        new_name = self._unique_copy_name(source.name)
        try:
            new_ship = self._save.add_ship(source, new_name)
        except ValueError as exc:
            # Handle "no space available" error
            QMessageBox.warning(
                self,
                "Cannot Duplicate Ship",
                f"Unable to find valid position for cloned ship:\n\n{exc}\n\n"
                "The sector may be too crowded or the ship is too large."
            )
            return
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Failed to clone ship:\n{exc}")
            return
        self._rebuild_ship_list(selected_ship=new_ship)
        self.status_message.emit(f'Ship "{new_name}" cloned (unsaved).')
