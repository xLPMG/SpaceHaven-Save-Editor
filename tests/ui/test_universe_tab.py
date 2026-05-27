"""Tests for src/ui/universe_tab.py using pytest-qt and a minimal SaveFile fixture."""

from __future__ import annotations

import textwrap

from PySide6.QtCore import Qt

from src.save_file import SaveFile, Sector, TimelineEvent
from src.ui.universe_tab import UniverseTab, _ro_item
from tests.helpers import make_save_from_xml

# ---------------------------------------------------------------------------
# XML fixtures used by _make_save (imported from tests.helpers)
# ---------------------------------------------------------------------------

MINIMAL_XML = textwrap.dedent("""\
    <game mode="Normal" seed="42">
      <space sx="382" sy="382"/>
      <playerBank ca="1000" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="8"/>
      </questLines></questLines>
      <ships>
        <ship sid="10" sname="HSS ALPHA" sx="56" sy="56" ox="32" oy="16">
          <characters/>
        </ship>
        <ship sid="20" sname="HSS BETA" sx="28" sy="28" ox="64" oy="32">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")


def _make_save(xml: str = MINIMAL_XML) -> SaveFile:
    return make_save_from_xml(xml)


def _seed_universe_data(sf: SaveFile) -> None:
    sf.sectors = [
        Sector("sector240", 240, 56, 84, 7),
        Sector("sector271", 271, 28, 28, 2),
    ]
    sf.timeline_events = [
        TimelineEvent(1, "New Crew Member", 12, "Alice joined"),
        TimelineEvent(8, "Research Completed", 22, "2532"),
        TimelineEvent(99, "Event #99", 24, "mystery"),
    ]


# ===========================================================================
# Helpers
# ===========================================================================


def _table_text(table, row: int, col: int) -> str:
    item = table.item(row, col)
    assert item is not None
    return item.text()


# ===========================================================================
# _ro_item
# ===========================================================================


class TestReadOnlyItem:
    def test_item_is_not_editable(self):
        item = _ro_item("abc")
        assert item.text() == "abc"
        assert not (item.flags() & Qt.ItemFlag.ItemIsEditable)


# ===========================================================================
# UniverseTab - load / clear
# ===========================================================================


class TestUniverseTabLoad:
    def test_initial_state(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        assert tab._save is None
        assert tab._sectors_table.rowCount() == 0
        assert tab._timeline_table.rowCount() == 0
        assert not tab._sector_map.isHidden()
        assert tab._no_map_lbl.isHidden()

    def test_load_populates_map_sectors_timeline(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        _seed_universe_data(sf)

        tab.load(sf)

        assert tab._save is sf
        assert not tab._sector_map.isHidden()
        assert tab._no_map_lbl.isHidden()
        assert not tab._sectors_table.isHidden()
        assert tab._no_sectors_lbl.isHidden()
        assert not tab._timeline_table.isHidden()
        assert tab._no_timeline_lbl.isHidden()
        assert tab._sectors_table.rowCount() == 2
        assert tab._timeline_table.rowCount() == 3

    def test_load_with_only_stored_ships_shows_no_map_message(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        _seed_universe_data(sf)
        for ship in sf.ships:
            ship.in_game_file = False

        tab.load(sf)

        assert tab._sector_map.isHidden()
        assert not tab._no_map_lbl.isHidden()

    def test_load_without_sector_data_shows_placeholder(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.sectors = []
        sf.timeline_events = [TimelineEvent(1, "New Crew Member", 5, "x")]

        tab.load(sf)

        assert tab._sectors_table.isHidden()
        assert not tab._no_sectors_lbl.isHidden()

    def test_load_without_timeline_data_shows_placeholder(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.sectors = [Sector("sector240", 240, 56, 56, 1)]
        sf.timeline_events = []

        tab.load(sf)

        assert tab._timeline_table.isHidden()
        assert not tab._no_timeline_lbl.isHidden()

    def test_clear_resets_state(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        _seed_universe_data(sf)
        tab.load(sf)

        tab.clear()

        assert tab._save is None
        assert tab._sectors_table.rowCount() == 0
        assert tab._timeline_table.rowCount() == 0
        assert not tab._sector_map.isHidden()
        assert tab._no_map_lbl.isHidden()


# ===========================================================================
# UniverseTab - sectors table
# ===========================================================================


class TestUniverseTabSectors:
    def test_sector_rows_render_expected_values(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.sectors = [Sector("sector240", 240, 56, 84, 7)]
        sf.timeline_events = []

        tab.load(sf)

        assert _table_text(tab._sectors_table, 0, 0) == "sector240"
        assert _table_text(tab._sectors_table, 0, 1) == "2 × 3"
        assert _table_text(tab._sectors_table, 0, 2) == "7"


# ===========================================================================
# UniverseTab - timeline table
# ===========================================================================


class TestUniverseTabTimeline:
    def test_timeline_is_reverse_chronological(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.sectors = []
        sf.timeline_events = [
            TimelineEvent(1, "New Crew Member", 10, "first"),
            TimelineEvent(1, "New Crew Member", 15, "second"),
        ]

        tab.load(sf)

        assert _table_text(tab._timeline_table, 0, 0) == "Day 15"
        assert _table_text(tab._timeline_table, 1, 0) == "Day 10"

    def test_research_event_detail_uses_tech_name(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.sectors = []
        sf.timeline_events = [
            TimelineEvent(8, "Research Completed", 22, "2532"),
        ]

        tab.load(sf)

        assert _table_text(tab._timeline_table, 0, 2) == "Scanner"

    def test_unknown_event_type_uses_fallback_label(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.sectors = []
        sf.timeline_events = [
            TimelineEvent(99, "Event #99", 1, "mystery"),
        ]

        tab.load(sf)

        assert _table_text(tab._timeline_table, 0, 1).strip() == "Event #99"
        assert _table_text(tab._timeline_table, 0, 2) == "mystery"


# ===========================================================================
# UniverseTab - ship move persistence
# ===========================================================================


class TestUniverseTabShipMove:
    def test_ship_moved_updates_xml_and_emits_status(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.sectors = []
        sf.timeline_events = []
        tab.load(sf)

        ship = sf.ships[0]
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._on_ship_moved(ship, 111, 222)

        assert ship.element.get("ox") == "111"
        assert ship.element.get("oy") == "222"
        msg = blocker.args[0].lower()
        assert "moved" in msg
        assert "unsaved" in msg

    def test_ship_moved_without_loaded_save_is_noop(self, qtbot):
        tab = UniverseTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        ship = sf.ships[0]
        old_ox = ship.element.get("ox")
        old_oy = ship.element.get("oy")

        with qtbot.assertNotEmitted(tab.status_message):
            tab._on_ship_moved(ship, 999, 888)

        assert ship.element.get("ox") == old_ox
        assert ship.element.get("oy") == old_oy
