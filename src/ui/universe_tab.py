"""universe_tab.py - Tab showing sector data and timeline events."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.save_file import SaveFile

from src.game_data import TECH_IDS, TIMELINE_EVENT_NAMES
from src.ui.sector_map_widget import SectorMapWidget

_ICONS_DIR = Path(__file__).parent / "icons"


def _icon(name: str) -> QIcon:
    path = _ICONS_DIR / f"{name}.svg"
    return QIcon(str(path)) if path.exists() else QIcon()


def _sep() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setObjectName("Separator")
    return line


# Map from timeline event type saveNr to icon filename (without extension)
_TYPE_ICON: dict[int, str] = {
    1: "tl_new_crew",  # New Crew Member
    2: "tl_crew_died",  # Crew Member Died
    3: "tl_derelict",  # Derelict Explored
    4: "tl_complete",  # Mission Completed
    5: "tl_trade",  # Trades Completed
    6: "universe",  # New Galaxy - reuse universe icon
    7: "tl_quest",  # Quest Completed
    8: "research",  # Research Completed - reuse research icon
}


class UniverseTab(QWidget):
    status_message = Signal(str)
    ship_position_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)
        root = QVBoxLayout(page)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(22)

        title = QLabel("Universe")
        title.setObjectName("TabTitle")
        root.addWidget(title)

        root.addWidget(_sep())

        # Interactive Sector Map
        self._map_group = QGroupBox("Current Sector Map")
        map_vbox = QVBoxLayout(self._map_group)
        map_vbox.setContentsMargins(16, 20, 16, 16)
        map_vbox.setSpacing(12)

        # Map widget
        self._sector_map = SectorMapWidget()
        self._sector_map.ship_moved.connect(self._on_ship_moved)
        self._sector_map.setFixedHeight(500)
        map_vbox.addWidget(self._sector_map)

        self._map_hint_lbl = QLabel("Tip: Drag ships on the map to move them.")
        self._map_hint_lbl.setObjectName("StatCardDesc")
        self._map_hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_vbox.addWidget(self._map_hint_lbl)

        self._no_map_lbl = QLabel("No ships found. Load a save file.")
        self._no_map_lbl.setObjectName("StatCardDesc")
        self._no_map_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_map_lbl.setVisible(False)
        map_vbox.addWidget(self._no_map_lbl)

        root.addWidget(self._map_group)

        root.addWidget(_sep())

        # Sectors table
        self._sectors_group = QGroupBox("Discovered Sectors")
        sectors_vbox = QVBoxLayout(self._sectors_group)
        sectors_vbox.setContentsMargins(16, 20, 16, 16)
        sectors_vbox.setSpacing(8)

        self._sectors_table = QTableWidget(0, 3)
        self._sectors_table.setHorizontalHeaderLabels(["Sector", "Size", "Entities"])
        self._sectors_table.horizontalHeader().setStretchLastSection(True)
        self._sectors_table.verticalHeader().setVisible(False)
        self._sectors_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._sectors_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._sectors_table.setAlternatingRowColors(True)
        self._sectors_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        sectors_vbox.addWidget(self._sectors_table)

        self._no_sectors_lbl = QLabel("No sector data found (load from a save folder).")
        self._no_sectors_lbl.setObjectName("StatCardDesc")
        self._no_sectors_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_sectors_lbl.setVisible(False)
        sectors_vbox.addWidget(self._no_sectors_lbl)

        root.addWidget(self._sectors_group)

        root.addWidget(_sep())

        # Timeline
        self._timeline_group = QGroupBox("Game Timeline")
        timeline_vbox = QVBoxLayout(self._timeline_group)
        timeline_vbox.setContentsMargins(16, 20, 16, 16)
        timeline_vbox.setSpacing(8)

        self._timeline_table = QTableWidget(0, 3)
        self._timeline_table.setHorizontalHeaderLabels(["Day", "Event", "Detail"])
        hh = self._timeline_table.horizontalHeader()
        hh.setStretchLastSection(True)
        self._timeline_table.verticalHeader().setVisible(False)
        self._timeline_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._timeline_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._timeline_table.setAlternatingRowColors(True)
        self._timeline_table.setIconSize(QSize(16, 16))
        self._timeline_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        timeline_vbox.addWidget(self._timeline_table)

        self._no_timeline_lbl = QLabel(
            "No timeline data found (load from a save folder)."
        )
        self._no_timeline_lbl.setObjectName("StatCardDesc")
        self._no_timeline_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_timeline_lbl.setVisible(False)
        timeline_vbox.addWidget(self._no_timeline_lbl)

        root.addWidget(self._timeline_group)
        root.addStretch()

    # ------------------------------------------------------------------
    # Load / Clear
    # ------------------------------------------------------------------

    def load(self, save: SaveFile) -> None:
        self._save = save
        self._load_sector_map(save)
        self._populate_sectors(save)
        self._populate_timeline(save)

    def clear(self) -> None:
        self._save = None
        self._sector_map.clear()
        self._sector_map.setVisible(True)
        self._map_hint_lbl.setVisible(True)
        self._no_map_lbl.setVisible(False)
        self._sectors_table.setRowCount(0)
        self._sectors_table.setVisible(True)
        self._no_sectors_lbl.setVisible(False)
        self._timeline_table.setRowCount(0)
        self._timeline_table.setVisible(True)
        self._no_timeline_lbl.setVisible(False)

    # ------------------------------------------------------------------
    # Populate helpers
    # ------------------------------------------------------------------

    def _load_sector_map(self, save: SaveFile) -> None:
        """Load the sector map with ships."""
        has_map_ships = any(ship.in_game_file for ship in save.ships)
        if not has_map_ships:
            self._sector_map.clear()
            self._sector_map.setVisible(False)
            self._map_hint_lbl.setVisible(False)
            self._no_map_lbl.setVisible(True)
            return

        self._sector_map.setVisible(True)
        self._map_hint_lbl.setVisible(True)
        self._no_map_lbl.setVisible(False)
        self._sector_map.load(save)

    def _on_ship_moved(self, ship, new_ox: int, new_oy: int) -> None:
        """Handle ship moved signal - persist the new position to the XML tree."""
        if self._save and ship.element is not None:
            ship.element.set("ox", str(new_ox))
            ship.element.set("oy", str(new_oy))
            ship.ox = new_ox
            ship.oy = new_oy
            self.ship_position_changed.emit()
            self.status_message.emit(
                f"Moved {ship.name} to ox={new_ox}, oy={new_oy} (unsaved)."
            )

    def _populate_sectors(self, save: SaveFile) -> None:
        sectors = save.sectors
        self._sectors_table.setRowCount(0)
        if not sectors:
            self._sectors_table.setVisible(False)
            self._no_sectors_lbl.setVisible(True)
            return
        self._sectors_table.setVisible(True)
        self._no_sectors_lbl.setVisible(False)
        self._sectors_table.setRowCount(len(sectors))
        for row, sector in enumerate(sectors):
            w = max(1, round(sector.sx / 28))
            h = max(1, round(sector.sy / 28))
            self._sectors_table.setItem(row, 0, _ro_item(sector.folder_name))
            self._sectors_table.setItem(row, 1, _ro_item(f"{w} × {h}"))
            self._sectors_table.setItem(row, 2, _ro_item(str(sector.entity_count)))
        self._sectors_table.resizeColumnsToContents()
        row_h = self._sectors_table.rowHeight(0) if sectors else 28
        header_h = self._sectors_table.horizontalHeader().height()
        max_rows_visible = min(len(sectors), 12)
        self._sectors_table.setFixedHeight(header_h + row_h * max_rows_visible + 4)

    def _populate_timeline(self, save: SaveFile) -> None:
        events = save.timeline_events
        self._timeline_table.setRowCount(0)
        if not events:
            self._timeline_table.setVisible(False)
            self._no_timeline_lbl.setVisible(True)
            return
        self._timeline_table.setVisible(True)
        self._no_timeline_lbl.setVisible(False)
        self._timeline_table.setRowCount(len(events))
        for row, ev in enumerate(reversed(events)):
            icon_name = _TYPE_ICON.get(ev.event_type, "")
            label = TIMELINE_EVENT_NAMES.get(ev.event_type, f"Event #{ev.event_type}")

            # Day column
            self._timeline_table.setItem(row, 0, _ro_item(f"Day {ev.day}"))

            # Event type column: icon + label text
            event_item = _ro_item(f"  {label}")
            if icon_name:
                event_item.setIcon(_icon(icon_name))
            self._timeline_table.setItem(row, 1, event_item)

            # Detail column: resolve IDs to names where possible
            detail = ev.text
            if ev.event_type == 8 and detail.isdigit():
                detail = TECH_IDS.get(int(detail), detail)
            self._timeline_table.setItem(row, 2, _ro_item(detail))

        self._timeline_table.resizeColumnsToContents()
        row_h = self._timeline_table.rowHeight(0) if events else 28
        header_h = self._timeline_table.horizontalHeader().height()
        max_rows_visible = min(len(events), 20)
        self._timeline_table.setFixedHeight(header_h + row_h * max_rows_visible + 4)


def _ro_item(text: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item
