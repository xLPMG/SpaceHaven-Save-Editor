"""Tests for src/ui/ships_tab.py using pytest-qt and a minimal SaveFile fixture."""

from __future__ import annotations

import textwrap
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from src.save_file import SaveFile
from src.ui.ships_tab import ShipsTab, _ShipDelegate
from tests.helpers import make_save_from_xml

# ---------------------------------------------------------------------------
# XML fixtures used by _make_save (imported from tests.helpers)
# ---------------------------------------------------------------------------

MINIMAL_XML = textwrap.dedent("""\
    <game mode="Normal" seed="42">
      <playerBank ca="1000" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="8"/>
      </questLines></questLines>
      <ships>
        <ship sid="10" sname="HSS ALPHA" sx="56" sy="56" ox="0" oy="0">
          <characters>
            <c entId="1" name="Alice" lname="Smith" cid="10">
              <props>
                <Health v="80"/><Food v="100"/><Rest v="90"/>
                <Comfort v="50"/><Mood v="70"/><Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr><a points="3" id="210"/></attr>
                <traits><t id="1046"/></traits>
                <conditions><c id="3307"/></conditions>
                <sociality><relationships>
                  <l targetId="2" friendship="20" attraction="-5" compatibility="60"/>
                </relationships></sociality>
                <skills>
                  <s sk="6" level="3" mxn="8" exp="0" expd="0"/>
                </skills>
              </pers>
            </c>
          </characters>
        </ship>
        <ship sid="20" sname="HSS BETA" sx="28" sy="28" ox="32" oy="16">
          <characters/>
        </ship>
        <ship sid="30" sname="HSS GAMMA" sx="28" sy="28" ox="64" oy="32">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")


ONE_SHIP_XML = textwrap.dedent("""\
    <game mode="Normal" seed="99">
      <playerBank ca="1000" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="8"/>
      </questLines></questLines>
      <ships>
        <ship sid="10" sname="ONLY SHIP" sx="56" sy="56" ox="0" oy="0">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")


def _make_save(xml: str = MINIMAL_XML) -> SaveFile:
    return make_save_from_xml(xml)


def _make_ship_fixture() -> SaveFile:
    sf = _make_save()
    stored_ship = sf.ships[2]
    stored_ship.in_game_file = False
    stored_ship.external_path = Path("/tmp/stored_ship.xml")
    return sf


def _section_names(tab: ShipsTab, header_text: str) -> list[str]:
    names: list[str] = []
    in_section = False
    for index in range(tab._ship_list.count()):
        item = tab._ship_list.item(index)
        if item.text() == header_text:
            in_section = True
            continue
        if in_section and item.data(Qt.ItemDataRole.UserRole) is None:
            break
        if in_section:
            names.append(item.text())
    return names


# ===========================================================================
# ShipsTab – construction, load, clear
# ===========================================================================


class TestShipsTabLoad:
    def test_initial_state(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        assert tab._save is None
        assert tab._current_ship is None
        assert tab._ship_list.count() == 0
        assert tab._detail_widget.isHidden()

    def test_delegate_is_installed(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        assert isinstance(tab._ship_list.itemDelegate(), _ShipDelegate)

    def test_load_populates_headers_and_selects_first_ship(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        tab.load(_make_ship_fixture())
        assert tab._ship_list.count() == 5
        assert tab._ship_list.item(0).text() == "CURRENT SECTOR"
        assert tab._ship_list.item(3).text() == "STORED"
        assert tab._current_ship is not None
        assert tab._current_ship.name == "HSS ALPHA"
        assert tab._info_location.text() == "Current Sector"
        assert tab._info_crew.text() == "1"
        assert tab._info_size.text() == "2 × 2"
        assert tab._detail_widget.isHidden() is False

    def test_load_selects_stored_ship_location(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        tab.load(_make_ship_fixture())
        tab._ship_list.setCurrentRow(4)
        assert tab._current_ship is not None
        assert tab._current_ship.name == "HSS GAMMA"
        assert tab._info_location.text() == "Stored (stored_ship.xml)"

    def test_header_selection_clears_detail(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        tab.load(_make_ship_fixture())
        tab._ship_list.setCurrentRow(0)
        assert tab._current_ship is None
        assert tab._detail_widget.isHidden()
        assert tab._placeholder.isHidden() is False

    def test_clear_resets_state(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        tab.load(_make_ship_fixture())
        tab.clear()
        assert tab._save is None
        assert tab._current_ship is None
        assert tab._ship_list.count() == 0
        assert tab._detail_widget.isHidden()
        assert tab._ship_map._tiles == []


# ===========================================================================
# ShipsTab – rename / clone / remove
# ===========================================================================


class TestShipsTabMutations:
    def test_rename_refreshes_model_and_keeps_selection(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        save = _make_ship_fixture()
        tab.load(save)
        tab._ship_list.setCurrentRow(1)
        tab._name_edit.setText("HSS ZETA")
        messages: list[str] = []
        tab.status_message.connect(messages.append)

        tab._rename_ship()

        assert save.ships[0].name == "HSS BETA"
        assert save.ships[1].name == "HSS GAMMA"
        assert save.ships[2].name == "HSS ZETA"
        assert tab._current_ship is not None
        assert tab._current_ship.name == "HSS ZETA"
        assert _section_names(tab, "CURRENT SECTOR") == ["HSS BETA", "HSS ZETA"]
        assert any("renamed" in msg.lower() for msg in messages)

    def test_clone_inserts_sorted_ship_and_selects_clone(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        save = _make_ship_fixture()
        tab.load(save)
        tab._ship_list.setCurrentRow(1)
        messages: list[str] = []
        tab.status_message.connect(messages.append)

        tab._clone_ship(1)

        assert len(save.ships) == 4
        assert tab._current_ship is not None
        assert "Copy" in tab._current_ship.name
        assert _section_names(tab, "CURRENT SECTOR") == [
            "HSS ALPHA",
            "HSS ALPHA - Copy",
            "HSS BETA",
        ]
        assert any("cloned" in msg.lower() for msg in messages)

    def test_remove_selected_ship_rebuilds_list(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        save = _make_ship_fixture()
        tab.load(save)
        tab._ship_list.setCurrentRow(1)
        messages: list[str] = []
        tab.status_message.connect(messages.append)

        tab._on_ship_remove_requested(1)

        assert all(ship.name != "HSS ALPHA" for ship in save.ships)
        assert tab._current_ship is None
        assert tab._detail_widget.isHidden()
        assert _section_names(tab, "CURRENT SECTOR") == ["HSS BETA"]
        assert any("removed" in msg.lower() for msg in messages)

    def test_remove_non_current_ship_keeps_current_selection(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        save = _make_ship_fixture()
        tab.load(save)
        tab._ship_list.setCurrentRow(1)
        current_ship = tab._current_ship

        tab._on_ship_remove_requested(2)

        assert tab._current_ship is current_ship
        assert tab._current_ship is not None
        assert tab._current_ship.name == "HSS ALPHA"
        assert _section_names(tab, "CURRENT SECTOR") == ["HSS ALPHA"]

    def test_last_ship_warning(self, qtbot, monkeypatch):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        save = _make_save(ONE_SHIP_XML)
        tab.load(save)
        shown: list[tuple[str, str]] = []

        class FakeMessageBox:
            @staticmethod
            def warning(_parent, title, message):
                shown.append((title, message))

        monkeypatch.setattr("src.ui.ships_tab.QMessageBox", FakeMessageBox)

        tab._on_ship_remove_requested(1)

        assert shown
        assert len(save.ships) == 1

    def test_rename_empty_name_noop(self, qtbot):
        tab = ShipsTab()
        qtbot.addWidget(tab)
        save = _make_ship_fixture()
        tab.load(save)
        tab._ship_list.setCurrentRow(1)
        original_name = tab._current_ship.name
        tab._name_edit.setText("   ")

        tab._rename_ship()

        assert tab._current_ship is not None
        assert tab._current_ship.name == original_name
