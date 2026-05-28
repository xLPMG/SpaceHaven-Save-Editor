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
            <feat eatAllowed="1">
              <inv>
                <s elementaryId="157" inStorage="100" onTheWayIn="0" onTheWayOut="0"/>
                <s elementaryId="158" inStorage="200" onTheWayIn="0" onTheWayOut="0"/>
                <s elementaryId="170" inStorage="0" onTheWayIn="0" onTheWayOut="0"/>
              </inv>
            </feat>
          </e>
          <e entId="1002" objId="9002">
            <feat eatAllowed="1">
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
# StorageTab - load / clear
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
# StorageTab - selection and filtering
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
# StorageTab - quantity editing
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
# StorageTab - add item
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
# StorageTab - remove item
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
# StorageTab - signal safety on lifecycle methods
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


# ===========================================================================
# StorageTab - container label formatting
# ===========================================================================

# Fixture with two named (differently-typed) containers
NAMED_MODULES_XML = textwrap.dedent(
    """\
    <game mode="Normal" seed="42">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="1" sname="ALPHA" sx="28" sy="28">
          <characters/>
          <e m="43"><wm><up m="82">
            <feat eatAllowed="1">
              <inv>
                <s elementaryId="157" inStorage="5" onTheWayIn="0" onTheWayOut="0"/>
              </inv>
            </feat>
          </up></wm></e>
          <e m="43"><wm><up m="789">
            <feat eatAllowed="1">
              <inv>
                <s elementaryId="158" inStorage="10" onTheWayIn="0" onTheWayOut="0"/>
                <s elementaryId="157" inStorage="20" onTheWayIn="0" onTheWayOut="0"/>
              </inv>
            </feat>
          </up></wm></e>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
"""
)

# Fixture with two containers of the same type (both Small Storage, m=82)
DUPLICATE_NAMES_XML = textwrap.dedent(
    """\
    <game mode="Normal" seed="42">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="1" sname="ALPHA" sx="28" sy="28">
          <characters/>
          <e m="43"><wm><up m="82">
            <feat eatAllowed="1">
              <inv>
                <s elementaryId="157" inStorage="3" onTheWayIn="0" onTheWayOut="0"/>
              </inv>
            </feat>
          </up></wm></e>
          <e m="43"><wm><up m="82">
            <feat eatAllowed="1">
              <inv>
                <s elementaryId="158" inStorage="7" onTheWayIn="0" onTheWayOut="0"/>
              </inv>
            </feat>
          </up></wm></e>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
"""
)


class TestStorageTabContainerLabels:
    """Verify the formatted text displayed for each container in the list."""

    def test_label_with_capacity_shows_em_dash_and_slash(self, qtbot):
        """Containers with a known capacity use the 'Name  —  n / max' format."""
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(make_save_from_xml(NAMED_MODULES_XML))
        # Sorted alphabetically: Large Storage (#0), Small Storage (#1)
        item0 = tab._container_list.item(0)
        item1 = tab._container_list.item(1)
        assert "Large Storage" in item0.text()
        assert "\u2014" in item0.text()  # em dash
        assert "2 / 250" in item0.text()
        assert "Small Storage" in item1.text()
        assert "1 / 50" in item1.text()

    def test_label_with_capacity_zero_uses_parens(self, qtbot):
        """Containers with capacity=0 (unknown/unlimited) use '(n)' format."""
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())  # MINIMAL_STORAGE_XML containers have capacity=0
        item0 = tab._container_list.item(0)
        assert "\u2014" not in item0.text()  # no em dash
        assert "(" in item0.text() and ")" in item0.text()

    def test_unique_names_have_no_number_suffix(self, qtbot):
        """When all containers have distinct type names, no '#N' is appended."""
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(make_save_from_xml(NAMED_MODULES_XML))
        for row in range(tab._container_list.count()):
            text = tab._container_list.item(row).text()
            assert "#" not in text

    def test_duplicate_names_get_sequential_number_suffix(self, qtbot):
        """When two containers share a type name, they get '#1' and '#2'."""
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(make_save_from_xml(DUPLICATE_NAMES_XML))
        texts = [tab._container_list.item(r).text() for r in range(tab._container_list.count())]
        assert any("#1" in t for t in texts)
        assert any("#2" in t for t in texts)

    def test_label_refreshes_after_add(self, qtbot):
        """Adding an item updates the count shown in the selected container label."""
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(make_save_from_xml(NAMED_MODULES_XML))
        # Select Small Storage (row 1, 1 item)
        tab._container_list.setCurrentRow(1)
        label_before = tab._container_list.item(1).text()
        assert "1 / 50" in label_before
        tab._add_item_combo.setCurrentIndex(tab._add_item_combo.findData(169))  # Noble Metals
        tab._add_qty_spin.setValue(1)
        tab._add_item()
        label_after = tab._container_list.item(1).text()
        assert "2 / 50" in label_after

    def test_label_refreshes_after_remove(self, qtbot):
        """Removing an item updates the count shown in the selected container label."""
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(make_save_from_xml(NAMED_MODULES_XML))
        # Select Large Storage (row 0, 2 items)
        tab._container_list.setCurrentRow(0)
        assert "2 / 250" in tab._container_list.item(0).text()
        tab._items_table.selectRow(0)
        tab._remove_item()
        assert "1 / 250" in tab._container_list.item(0).text()


# ===========================================================================
# StorageTab - capacity guard (add blocked at capacity)
# ===========================================================================


class TestStorageTabCapacityGuard:
    """Verify that adding a new item type is blocked when a container is full."""

    def _full_container_setup(self, qtbot):
        """Load MINIMAL_STORAGE_XML, force the current container to be exactly full."""
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        container = tab._current_container
        # Force capacity = current item count so the container is exactly full
        container.capacity = len(container.items)
        return tab, container

    def test_new_item_blocked_when_container_full(self, qtbot, monkeypatch):
        """Adding a brand-new item type to a full container shows a warning."""
        tab, container = self._full_container_setup(qtbot)
        warned = [False]
        monkeypatch.setattr(
            "src.ui.storage_tab.QMessageBox.warning",
            lambda *a, **k: warned.__setitem__(0, True),
        )
        # Noble Metals (169) is not in this container
        tab._add_item_combo.setCurrentIndex(tab._add_item_combo.findData(169))
        tab._add_item()
        assert warned[0]

    def test_new_item_blocked_does_not_add_row(self, qtbot, monkeypatch):
        """A blocked add must not insert a new row in the table."""
        tab, container = self._full_container_setup(qtbot)
        monkeypatch.setattr("src.ui.storage_tab.QMessageBox.warning", lambda *a, **k: None)
        rows_before = tab._items_table.rowCount()
        tab._add_item_combo.setCurrentIndex(tab._add_item_combo.findData(169))
        tab._add_item()
        assert tab._items_table.rowCount() == rows_before

    def test_stacking_existing_item_allowed_when_full(self, qtbot, monkeypatch):
        """Adding more of an item already present is allowed even at capacity."""
        tab, container = self._full_container_setup(qtbot)
        warned = [False]
        monkeypatch.setattr(
            "src.ui.storage_tab.QMessageBox.warning",
            lambda *a, **k: warned.__setitem__(0, True),
        )
        # Stack onto Base Metals (157) which is already in the container
        tab._add_item_combo.setCurrentIndex(tab._add_item_combo.findData(157))
        tab._add_item()
        assert not warned[0]

    def test_unlimited_container_never_blocked(self, qtbot, monkeypatch):
        """Containers with capacity=0 are unlimited and never trigger the guard."""
        tab = StorageTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        container = tab._current_container
        assert container.capacity == 0  # default from unknown module
        warned = [False]
        monkeypatch.setattr(
            "src.ui.storage_tab.QMessageBox.warning",
            lambda *a, **k: warned.__setitem__(0, True),
        )
        tab._add_item_combo.setCurrentIndex(tab._add_item_combo.findData(169))
        tab._add_item()
        assert not warned[0]

