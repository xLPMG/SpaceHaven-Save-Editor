"""Tests for src/ui/research_tab.py using pytest-qt and a minimal SaveFile fixture."""

from __future__ import annotations

import io
import textwrap

from lxml import etree
from PySide6.QtCore import Qt

from src.save_file import SaveFile
from src.ui.research_tab import ResearchTab, _TechDelegate

# ---------------------------------------------------------------------------
# SaveFile fixture helpers
# ---------------------------------------------------------------------------

MINIMAL_XML = textwrap.dedent("""\
    <game mode="Normal" seed="42">
      <playerBank ca="1000" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="8"/>
      </questLines></questLines>
      <ships>
        <ship sid="10" sname="HSS ALPHA" sx="56" sy="56">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535">
        <states>
          <l techId="2536">
            <stageStates>
              <l done="true"><blocksDone level1="0" level2="0" level3="0"/></l>
              <l done="true"><blocksDone level1="0" level2="0" level3="0"/></l>
            </stageStates>
          </l>
          <l techId="2537">
            <stageStates>
              <l done="false"><blocksDone level1="5" level2="0" level3="0"/></l>
              <l done="false"><blocksDone level1="0" level2="0" level3="0"/></l>
            </stageStates>
          </l>
          <l techId="2538">
            <stageStates>
              <l done="false"><blocksDone level1="0" level2="0" level3="0"/></l>
            </stageStates>
          </l>
        </states>
      </research>
    </game>
""")

NO_RESEARCH_XML = textwrap.dedent("""\
    <game mode="Normal" seed="99">
      <playerBank ca="5000" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="100"/>
      </questLines></questLines>
      <ships>
        <ship sid="10" sname="TEST" sx="28" sy="28">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")

ALL_DONE_XML = textwrap.dedent("""\
    <game mode="Normal" seed="1">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="5" sname="TESTSHIP" sx="28" sy="28">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535">
        <states>
          <l techId="2536">
            <stageStates>
              <l done="true"><blocksDone level1="0" level2="0" level3="0"/></l>
              <l done="true"><blocksDone level1="0" level2="0" level3="0"/></l>
            </stageStates>
          </l>
          <l techId="2537">
            <stageStates>
              <l done="true"><blocksDone level1="0" level2="0" level3="0"/></l>
              <l done="true"><blocksDone level1="0" level2="0" level3="0"/></l>
            </stageStates>
          </l>
        </states>
      </research>
    </game>
""")

MANY_RESEARCH_XML = textwrap.dedent("""\
    <game mode="Normal" seed="2">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="5" sname="TESTSHIP" sx="28" sy="28">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535">
        <states>
          <l techId="2536">
            <stageStates>
              <l done="true"><blocksDone level1="0" level2="0" level3="0"/></l>
            </stageStates>
          </l>
          <l techId="2537">
            <stageStates>
              <l done="false"><blocksDone level1="5" level2="0" level3="0"/></l>
            </stageStates>
          </l>
          <l techId="2538">
            <stageStates>
              <l done="false"><blocksDone level1="0" level2="0" level3="0"/></l>
            </stageStates>
          </l>
          <l techId="2539">
            <stageStates>
              <l done="false"><blocksDone level1="0" level2="0" level3="0"/></l>
            </stageStates>
          </l>
          <l techId="2540">
            <stageStates>
              <l done="false"><blocksDone level1="0" level2="0" level3="0"/></l>
            </stageStates>
          </l>
        </states>
      </research>
    </game>
""")


def _make_save(xml: str = MINIMAL_XML) -> SaveFile:
    sf = SaveFile()
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    sf._tree = etree.parse(io.BytesIO(xml.encode()), parser)
    sf._root = sf._tree.getroot()
    sf._parse_ships()
    sf._parse_characters()
    sf._parse_research()
    return sf


# ===========================================================================
# _TechDelegate
# ===========================================================================


class TestTechDelegate:
    def test_delegate_exists(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        delegate = tab._list.itemDelegate()
        assert isinstance(delegate, _TechDelegate)

    def test_size_hint_returns_fixed_height(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        delegate = tab._list.itemDelegate()
        from PySide6.QtWidgets import QStyleOptionViewItem

        option = QStyleOptionViewItem()
        option.rect.setWidth(500)
        size = delegate.sizeHint(option, tab._list.model().index(0, 0))
        assert size.height() == 48


# ===========================================================================
# ResearchTab – load / clear
# ===========================================================================


class TestResearchTabLoad:
    def test_initial_state_buttons_disabled(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        assert not tab._complete_sel_btn.isEnabled()
        assert not tab._complete_all_btn.isEnabled()

    def test_load_enables_complete_all_button(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert tab._complete_all_btn.isEnabled()

    def test_load_populates_list(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert tab._list.count() == 3

    def test_load_populates_banner_stats(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # MINIMAL_XML has 1 done, 1 in_progress, 1 not done = 3 total
        assert tab._count_total.text() == "3"
        assert tab._count_done.text() == "1"
        assert tab._count_progress.text() == "1"
        assert tab._count_remain.text() == "1"

    def test_load_sets_progress_bar(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # 1 done out of 3 total
        assert tab._progress_bar.value() == 1
        assert tab._progress_bar.maximum() == 3

    def test_load_no_research(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(NO_RESEARCH_XML)
        tab.load(sf)
        assert tab._list.count() == 0
        assert tab._count_total.text() == "0"
        assert tab._count_done.text() == "0"

    def test_load_all_done(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(ALL_DONE_XML)
        tab.load(sf)
        assert tab._count_done.text() == "2"
        assert tab._count_progress.text() == "0"
        assert tab._count_remain.text() == "0"

    def test_clear_resets_list(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab.clear()
        assert tab._list.count() == 0

    def test_clear_resets_banner_stats(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab.clear()
        assert tab._count_total.text() == "0"
        assert tab._count_done.text() == "0"
        assert tab._count_progress.text() == "0"
        assert tab._count_remain.text() == "0"

    def test_clear_disables_buttons(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab.clear()
        assert not tab._complete_sel_btn.isEnabled()
        assert not tab._complete_all_btn.isEnabled()

    def test_clear_resets_progress_bar(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab.clear()
        assert tab._progress_bar.value() == 0

    def test_load_resets_filter(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Change filter to "done"
        tab._set_filter("done")
        assert tab._active_filter == "done"
        # Load again should reset to "all"
        tab.load(sf)
        assert tab._active_filter == "all"

    def test_load_clears_search(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._search.setText("test")
        tab.load(sf)
        assert tab._search.text() == ""


# ===========================================================================
# ResearchTab – filtering
# ===========================================================================


class TestResearchTabFiltering:
    def test_filter_all_shows_all(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._set_filter("all")
        assert tab._list.count() == 3

    def test_filter_done(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._set_filter("done")
        assert tab._list.count() == 1
        entry = tab._list.item(0).data(Qt.ItemDataRole.UserRole)
        assert entry.done

    def test_filter_progress(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._set_filter("progress")
        assert tab._list.count() == 1
        entry = tab._list.item(0).data(Qt.ItemDataRole.UserRole)
        assert entry.in_progress

    def test_filter_todo(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._set_filter("todo")
        assert tab._list.count() == 1
        entry = tab._list.item(0).data(Qt.ItemDataRole.UserRole)
        assert not entry.done
        assert not entry.in_progress

    def test_filter_buttons_checked_state(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Initially "all" should be checked
        buttons = tab.findChildren(tab._complete_sel_btn.__class__)
        all_btn = next(b for b in buttons if b.property("filterAttr") == "all")
        assert all_btn.isChecked()
        # Switch to "done"
        tab._set_filter("done")
        done_btn = next(b for b in buttons if b.property("filterAttr") == "done")
        assert done_btn.isChecked()
        assert not all_btn.isChecked()

    def test_filter_updates_on_button_click(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        buttons = tab.findChildren(tab._complete_sel_btn.__class__)
        done_btn = next(b for b in buttons if b.property("filterAttr") == "done")
        done_btn.click()
        assert tab._active_filter == "done"
        assert tab._list.count() == 1

    def test_banner_stats_unchanged_by_filter(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        original_total = tab._count_total.text()
        original_done = tab._count_done.text()
        tab._set_filter("done")
        # Banner should show total stats, not filtered stats
        assert tab._count_total.text() == original_total
        assert tab._count_done.text() == original_done


# ===========================================================================
# ResearchTab – search
# ===========================================================================


class TestResearchTabSearch:
    def test_search_filters_by_name(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(MANY_RESEARCH_XML)
        tab.load(sf)
        initial_count = tab._list.count()
        # Type partial tech name (assuming tech names contain numbers)
        tab._search.setText("2536")
        qtbot.wait(10)
        assert tab._list.count() < initial_count

    def test_search_case_insensitive(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Get first entry name
        entry = tab._list.item(0).data(Qt.ItemDataRole.UserRole)
        name_part = entry.name[:4].upper()
        tab._search.setText(name_part)
        qtbot.wait(10)
        # Should still find it
        assert tab._list.count() >= 1

    def test_search_no_match(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._search.setText("XYZNONEXISTENT")
        qtbot.wait(10)
        assert tab._list.count() == 0

    def test_search_combines_with_filter(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(MANY_RESEARCH_XML)
        tab.load(sf)
        # Set filter to "todo" and search
        tab._set_filter("todo")
        todo_count = tab._list.count()
        entry = tab._list.item(0).data(Qt.ItemDataRole.UserRole)
        tab._search.setText(entry.name[:4])
        qtbot.wait(10)
        # Should show fewer results (filtered by both)
        assert tab._list.count() <= todo_count

    def test_search_clears(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        original_count = tab._list.count()
        tab._search.setText("test")
        qtbot.wait(10)
        tab._search.setText("")
        qtbot.wait(10)
        assert tab._list.count() == original_count


# ===========================================================================
# ResearchTab – selection
# ===========================================================================


class TestResearchTabSelection:
    def test_no_selection_disables_complete_button(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._list.clearSelection()
        assert not tab._complete_sel_btn.isEnabled()

    def test_selecting_incomplete_enables_complete_button(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Find an incomplete item
        for i in range(tab._list.count()):
            entry = tab._list.item(i).data(Qt.ItemDataRole.UserRole)
            if not entry.done:
                tab._list.setCurrentRow(i)
                break
        assert tab._complete_sel_btn.isEnabled()

    def test_selecting_complete_disables_complete_button(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Find a completed item
        for i in range(tab._list.count()):
            entry = tab._list.item(i).data(Qt.ItemDataRole.UserRole)
            if entry.done:
                tab._list.setCurrentRow(i)
                break
        assert not tab._complete_sel_btn.isEnabled()

    def test_multi_selection_with_incomplete_enables_button(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(MANY_RESEARCH_XML)
        tab.load(sf)
        # Select multiple items including incomplete
        incomplete_indices = []
        for i in range(tab._list.count()):
            entry = tab._list.item(i).data(Qt.ItemDataRole.UserRole)
            if not entry.done:
                incomplete_indices.append(i)
                if len(incomplete_indices) >= 2:
                    break
        for idx in incomplete_indices:
            tab._list.item(idx).setSelected(True)
        assert tab._complete_sel_btn.isEnabled()

    def test_multi_selection_all_complete_disables_button(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(ALL_DONE_XML)
        tab.load(sf)
        # Select all (which are all complete)
        tab._list.selectAll()
        assert not tab._complete_sel_btn.isEnabled()


# ===========================================================================
# ResearchTab – actions
# ===========================================================================


class TestResearchTabActions:
    def test_complete_selected_marks_research_done(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Find incomplete research
        for i in range(tab._list.count()):
            entry = tab._list.item(i).data(Qt.ItemDataRole.UserRole)
            if not entry.done:
                tab._list.setCurrentRow(i)
                initial_done = entry.done
                tab._complete_selected()
                assert entry.done != initial_done
                break

    def test_complete_selected_updates_banner(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        initial_done = int(tab._count_done.text())
        # Find and complete incomplete research
        for i in range(tab._list.count()):
            entry = tab._list.item(i).data(Qt.ItemDataRole.UserRole)
            if not entry.done:
                tab._list.setCurrentRow(i)
                tab._complete_selected()
                break
        assert int(tab._count_done.text()) > initial_done

    def test_complete_selected_emits_status(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Connect signal
        messages = []
        tab.status_message.connect(messages.append)
        # Find and complete incomplete research
        for i in range(tab._list.count()):
            entry = tab._list.item(i).data(Qt.ItemDataRole.UserRole)
            if not entry.done:
                tab._list.setCurrentRow(i)
                tab._complete_selected()
                break
        assert len(messages) == 1
        assert "Completed" in messages[0]
        assert "unsaved" in messages[0]

    def test_complete_all_completes_everything(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._complete_all()
        # All should be done
        assert int(tab._count_done.text()) == int(tab._count_total.text())
        assert tab._count_progress.text() == "0"
        assert tab._count_remain.text() == "0"

    def test_complete_all_updates_progress_bar(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._complete_all()
        assert tab._progress_bar.value() == tab._progress_bar.maximum()

    def test_complete_all_emits_status(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        messages = []
        tab.status_message.connect(messages.append)
        tab._complete_all()
        assert len(messages) == 1
        assert "Completed all" in messages[0]

    def test_complete_all_when_already_complete(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(ALL_DONE_XML)
        tab.load(sf)
        messages = []
        tab.status_message.connect(messages.append)
        tab._complete_all()
        assert len(messages) == 1
        assert "already complete" in messages[0]

    def test_complete_selected_multiple_items(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(MANY_RESEARCH_XML)
        tab.load(sf)
        initial_done = int(tab._count_done.text())
        # Select multiple incomplete items
        incomplete_count = 0
        for i in range(tab._list.count()):
            entry = tab._list.item(i).data(Qt.ItemDataRole.UserRole)
            if not entry.done and incomplete_count < 3:
                tab._list.item(i).setSelected(True)
                incomplete_count += 1
        tab._complete_selected()
        assert int(tab._count_done.text()) == initial_done + incomplete_count

    def test_complete_selected_does_nothing_when_all_done(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(ALL_DONE_XML)
        tab.load(sf)
        initial_done = int(tab._count_done.text())
        tab._list.selectAll()
        messages = []
        tab.status_message.connect(messages.append)
        tab._complete_selected()
        # Should not emit status (no items to complete)
        assert len(messages) == 0
        assert int(tab._count_done.text()) == initial_done

    def test_complete_actions_work_with_no_save(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        # No crash when calling without load
        tab._complete_all()
        tab._complete_selected()


# ===========================================================================
# ResearchTab – edge cases
# ===========================================================================


class TestResearchTabEdgeCases:
    def test_progress_bar_handles_zero_total(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(NO_RESEARCH_XML)
        tab.load(sf)
        # Should not crash, range should be at least 1
        assert tab._progress_bar.maximum() >= 1

    def test_list_items_have_user_data(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        for i in range(tab._list.count()):
            entry = tab._list.item(i).data(Qt.ItemDataRole.UserRole)
            assert entry is not None
            assert hasattr(entry, "tech_id")
            assert hasattr(entry, "name")
            assert hasattr(entry, "done")
            assert hasattr(entry, "in_progress")

    def test_selection_changed_handles_none_data(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Manually create an item with None data to test robustness
        from PySide6.QtWidgets import QListWidgetItem

        bad_item = QListWidgetItem("Bad Item")
        bad_item.setData(Qt.ItemDataRole.UserRole, None)
        tab._list.addItem(bad_item)
        bad_item.setSelected(True)
        # Should not crash
        tab._on_selection_changed()

    def test_filter_persists_across_searches(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(MANY_RESEARCH_XML)
        tab.load(sf)
        tab._set_filter("done")
        assert tab._active_filter == "done"
        tab._search.setText("test")
        qtbot.wait(10)
        tab._search.setText("")
        qtbot.wait(10)
        assert tab._active_filter == "done"

    def test_load_sorts_research_by_name(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        sf = _make_save(MANY_RESEARCH_XML)
        tab.load(sf)
        # Get all entry names
        names = []
        for i in range(tab._list.count()):
            entry = tab._list.item(i).data(Qt.ItemDataRole.UserRole)
            names.append(entry.name)
        # Should be sorted
        assert names == sorted(names)

    def test_search_placeholder_text(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        assert tab._search.placeholderText() == "Filter technologies…"

    def test_list_uses_extended_selection_mode(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        from PySide6.QtWidgets import QListWidget

        assert tab._list.selectionMode() == QListWidget.SelectionMode.ExtendedSelection

    def test_list_has_mouse_tracking(self, qtbot):
        tab = ResearchTab()
        qtbot.addWidget(tab)
        assert tab._list.hasMouseTracking()
