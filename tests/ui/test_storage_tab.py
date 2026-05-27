"""Tests for src/ui/storage_tab.py using pytest-qt and minimal SaveFile fixtures."""

from __future__ import annotations

import textwrap

from src.save_file import SaveFile
from src.ui.storage_tab import StorageTab
from tests.helpers import make_save_from_xml

# ---------------------------------------------------------------------------
# XML fixtures used by _make_save (imported from tests.helpers)
# ---------------------------------------------------------------------------

MINIMAL_STORAGE_XML = textwrap.dedent(
    """\
    <game mode="Normal" seed="42">
      <playerBank ca="1000" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="8"/>
      </questLines></questLines>
      <ships>
        <ship sid="10" sname="HSS ALPHA" sx="56" sy="56">
          <characters/>
          <e entId="1001" objId="9001">
            <feat eatAllowed="true">
              <inv>
                <s elementaryId="157" inStorage="100" onTheWayIn="0" onTheWayOut="0"/>
                <s elementaryId="158" inStorage="200" onTheWayIn="0" onTheWayOut="0"/>
                <s elementaryId="170" inStorage="0" onTheWayIn="0" onTheWayOut="0"/>
              </inv>
            </feat>
          </e>
          <e entId="1002" objId="9002">
            <feat eatAllowed="true">
              <inv>
                <s elementaryId="175" inStorage="50" onTheWayIn="0" onTheWayOut="0"/>
              </inv>
            </feat>
          </e>
        </ship>
        <ship sid="20" sname="HSS BETA" sx="28" sy="28">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
"""
)

EMPTY_SHIPS_XML = textwrap.dedent(
    """\
    <game mode="Normal" seed="99">
      <playerBank ca="1000" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="8"/>
      </questLines></questLines>
      <ships/>
      <research treeId="2535"><states/></research>
    </game>
"""
)


def _make_save(xml: str = MINIMAL_STORAGE_XML) -> SaveFile:
    return make_save_from_xml(xml)


def _row_for_item(tab: StorageTab, item_name: str) -> int:
    for row in range(tab._items_table.rowCount()):
        cell = tab._items_table.item(row, 0)
        if cell is not None and cell.text() == item_name:
            return row
    return -1


# ===========================================================================
# StorageTab – load / clear
# ===========================================================================


class TestStorageTabLoad:
    def test_initial_state_controls_disabled(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        assert not tab._filter_edit.isEnabled()
        assert not tab._items_table.isEnabled()
        assert not tab._add_item_combo.isEnabled()
        assert not tab._add_qty_spin.isEnabled()
        assert not tab._add_btn.isEnabled()
        assert not tab._remove_btn.isEnabled()

    def test_load_populates_ship_combo(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        assert tab._ship_combo.count() == 2

    def test_load_selects_first_container_and_populates_items(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        assert tab._container_list.count() == 2
        assert tab._container_list.currentRow() == 0
        assert tab._items_table.rowCount() == 2
        assert tab._current_container is not None

    def test_load_sets_container_info_summary(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        text = tab._container_info.text()
        assert "2 containers" in text
        assert "3 item types" in text

    def test_clear_resets_state(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab.clear()
        assert tab._save is None
        assert tab._current_ship is None
        assert tab._current_container is None
        assert tab._ship_combo.count() == 0
        assert tab._container_list.count() == 0
        assert tab._items_table.rowCount() == 0
        assert tab._container_info.text() == ""
        assert not tab._add_btn.isEnabled()
        assert not tab._remove_btn.isEnabled()

    def test_load_with_no_ships_clears_previous_ui(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        assert tab._items_table.rowCount() > 0
        tab.load(_make_save(EMPTY_SHIPS_XML))
        assert tab._ship_combo.count() == 0
        assert tab._container_list.count() == 0
        assert tab._items_table.rowCount() == 0
        assert tab._container_info.text() == ""
        assert not tab._items_table.isEnabled()


# ===========================================================================
# StorageTab – selection and filtering
# ===========================================================================


class TestStorageTabSelectionAndFilter:
    def test_switch_to_ship_without_containers_disables_right_panel(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._ship_combo.setCurrentIndex(1)  # HSS BETA
        assert tab._container_list.count() == 0
        assert tab._items_table.rowCount() == 0
        assert not tab._items_table.isEnabled()
        assert not tab._add_btn.isEnabled()
        assert not tab._remove_btn.isEnabled()

    def test_selecting_second_container_replaces_item_rows(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._container_list.setCurrentRow(1)
        assert tab._items_table.rowCount() == 1
        assert tab._items_table.item(0, 0).text() == "Plastics"

    def test_filter_hides_non_matching_rows(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._filter_edit.setText("base")
        visible_rows = [
            row
            for row in range(tab._items_table.rowCount())
            if not tab._items_table.isRowHidden(row)
        ]
        assert len(visible_rows) == 1
        assert tab._items_table.item(visible_rows[0], 0).text() == "Base Metals"

    def test_filter_hides_selected_row_disables_remove(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        row = _row_for_item(tab, "Energium")
        tab._items_table.selectRow(row)
        assert tab._remove_btn.isEnabled()
        tab._filter_edit.setText("base")
        assert not tab._remove_btn.isEnabled()


# ===========================================================================
# StorageTab – quantity editing
# ===========================================================================


class TestStorageTabQuantityEditing:
    def test_quantity_spin_persists_to_model(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)

        row = _row_for_item(tab, "Base Metals")
        spin = tab._items_table.cellWidget(row, 1)
        spin.setValue(321)

        container = sf.get_storage_containers(sf.ships[0])[0]
        item = next(i for i in container.items if i.name == "Base Metals")
        assert item.quantity == 321

    def test_quantity_spin_emits_status(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())

        row = _row_for_item(tab, "Energium")
        spin = tab._items_table.cellWidget(row, 1)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            spin.setValue(333)
        assert "unsaved" in blocker.args[0].lower()


# ===========================================================================
# StorageTab – add item
# ===========================================================================


class TestStorageTabAddItem:
    def test_add_new_item_adds_row_and_model(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)

        before_rows = tab._items_table.rowCount()
        tab._add_item_combo.setCurrentIndex(tab._add_item_combo.findData(169))
        tab._add_qty_spin.setValue(123)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._add_item()

        assert tab._items_table.rowCount() == before_rows + 1
        assert _row_for_item(tab, "Noble Metals") >= 0
        container = sf.get_storage_containers(sf.ships[0])[0]
        added = next(i for i in container.items if i.item_id == 169)
        assert added.quantity == 123
        assert "added" in blocker.args[0].lower()

    def test_add_existing_item_stacks_without_adding_row(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)

        before_rows = tab._items_table.rowCount()
        tab._add_item_combo.setCurrentIndex(tab._add_item_combo.findData(157))
        tab._add_qty_spin.setValue(5)
        tab._add_item()

        assert tab._items_table.rowCount() == before_rows
        row = _row_for_item(tab, "Base Metals")
        spin = tab._items_table.cellWidget(row, 1)
        assert spin.value() == 105
        container = sf.get_storage_containers(sf.ships[0])[0]
        item = next(i for i in container.items if i.item_id == 157)
        assert item.quantity == 105

    def test_add_surfaces_existing_zero_qty_item(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)

        assert _row_for_item(tab, "Carbon") == -1
        before_rows = tab._items_table.rowCount()
        tab._add_item_combo.setCurrentIndex(tab._add_item_combo.findData(170))
        tab._add_qty_spin.setValue(7)
        tab._add_item()

        assert tab._items_table.rowCount() == before_rows + 1
        row = _row_for_item(tab, "Carbon")
        assert row >= 0
        spin = tab._items_table.cellWidget(row, 1)
        assert spin.value() == 7
        container = sf.get_storage_containers(sf.ships[0])[0]
        item = next(i for i in container.items if i.item_id == 170)
        assert item.quantity == 7

    def test_add_invalid_selection_shows_warning(self, qtbot, monkeypatch):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())

        called = {"warned": False}

        def _warn(*_args, **_kwargs):
            called["warned"] = True

        monkeypatch.setattr("src.ui.storage_tab.QMessageBox.warning", _warn)
        tab._add_item_combo.setCurrentIndex(-1)
        tab._add_item()
        assert called["warned"]

    def test_add_noop_without_loaded_save(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab._add_item()  # no crash


# ===========================================================================
# StorageTab – remove item
# ===========================================================================


class TestStorageTabRemoveItem:
    def test_remove_selected_item_updates_ui_and_model(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)

        row = _row_for_item(tab, "Energium")
        tab._items_table.selectRow(row)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._remove_item()

        assert _row_for_item(tab, "Energium") == -1
        container = sf.get_storage_containers(sf.ships[0])[0]
        assert all(i.name != "Energium" for i in container.items)
        assert "removed" in blocker.args[0].lower()

    def test_remove_without_selection_shows_info(self, qtbot, monkeypatch):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())

        called = {"shown": False}

        def _info(*_args, **_kwargs):
            called["shown"] = True

        monkeypatch.setattr("src.ui.storage_tab.QMessageBox.information", _info)
        tab._items_table.clearSelection()
        tab._remove_item()
        assert called["shown"]

    def test_remove_noop_without_loaded_save(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab._remove_item()  # no crash


# ===========================================================================
# StorageTab – signal safety on lifecycle methods
# ===========================================================================


class TestStorageTabSignals:
    def test_load_does_not_emit_status(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        signal_received = False

        def _on_signal(_msg):
            nonlocal signal_received
            signal_received = True

        tab.status_message.connect(_on_signal)
        tab.load(_make_save())
        assert not signal_received

    def test_clear_does_not_emit_status(self, qtbot):
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        signal_received = False

        def _on_signal(_msg):
            nonlocal signal_received
            signal_received = True

        tab.status_message.connect(_on_signal)
        tab.clear()
        assert not signal_received
