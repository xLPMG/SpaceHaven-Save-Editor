"""Tests for src/ui/crew_tab.py using pytest-qt and a minimal SaveFile fixture."""

from __future__ import annotations

import io
import textwrap

from lxml import etree
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLineEdit, QSpinBox

from src.save_file import SaveFile
from src.ui.crew_tab import CrewTab, _pip_html, _AvatarLabel

# ---------------------------------------------------------------------------
# SaveFile fixture helpers  (shared with test_save_file.py pattern)
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
                  <s sk="14" level="5" mxn="7" exp="0" expd="0"/>
                </skills>
              </pers>
            </c>
            <c entId="2" name="Bob" lname="Jones" cid="10">
              <props>
                <Health v="100"/><Food v="90"/><Rest v="80"/>
                <Comfort v="60"/><Mood v="55"/><Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr/>
                <traits/>
                <conditions/>
                <sociality><relationships>
                  <l targetId="1" friendship="15" attraction="5" compatibility="40"/>
                </relationships></sociality>
                <skills>
                  <s sk="22" level="0" mxn="0" exp="0" expd="0"/>
                </skills>
              </pers>
            </c>
          </characters>
        </ship>
        <ship sid="20" sname="HSS BETA" sx="28" sy="28">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")

OVER_MAX_XML = textwrap.dedent("""\
    <game mode="Normal" seed="1">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="5" sname="TESTSHIP" sx="28" sy="28">
          <characters>
            <c entId="9" name="Over" lname="Max" cid="5">
              <props>
                <Health v="80"/><Food v="100"/><Rest v="90"/>
                <Comfort v="50"/><Mood v="70"/><Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr/>
                <traits/>
                <conditions/>
                <sociality><relationships/></sociality>
                <skills>
                  <s sk="6" level="15" mxn="20" exp="0" expd="0"/>
                </skills>
              </pers>
            </c>
          </characters>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")


OVER_MAX_ATTR_XML = textwrap.dedent("""\
    <game mode="Normal" seed="2">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="5" sname="TESTSHIP" sx="28" sy="28">
          <characters>
            <c entId="9" name="Over" lname="Attr" cid="5">
              <props>
                <Health v="80"/><Food v="100"/><Rest v="90"/>
                <Comfort v="50"/><Mood v="70"/><Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr><a points="15" id="210"/></attr>
                <traits/>
                <conditions/>
                <sociality><relationships/></sociality>
                <skills/>
              </pers>
            </c>
          </characters>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")

TWO_CREW_SHIPS_XML = textwrap.dedent("""\
    <game mode="Normal" seed="3">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="1" sname="SHIP ALPHA" sx="28" sy="28">
          <characters>
            <c entId="1" name="Alpha" lname="Crew" cid="1">
              <props>
                <Health v="80"/><Food v="100"/><Rest v="90"/>
                <Comfort v="50"/><Mood v="70"/><Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr/><traits/><conditions/>
                <sociality><relationships/></sociality>
                <skills/>
              </pers>
            </c>
          </characters>
        </ship>
        <ship sid="2" sname="SHIP BETA" sx="28" sy="28">
          <characters>
            <c entId="2" name="Beta" lname="Crew" cid="2">
              <props>
                <Health v="90"/><Food v="80"/><Rest v="70"/>
                <Comfort v="60"/><Mood v="50"/><Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr/><traits/><conditions/>
                <sociality><relationships/></sociality>
                <skills/>
              </pers>
            </c>
          </characters>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _crew_names(tab: CrewTab) -> list[str]:
    """Return the visible crew list item texts in order."""
    return [tab._crew_list.item(i).text() for i in range(tab._crew_list.count())]


# ===========================================================================
# _pip_html
# ===========================================================================


class TestPipHtml:
    def test_full_bar(self):
        html = _pip_html(3, 3)
        assert "●●●" in html
        assert "○" not in html

    def test_empty_bar(self):
        html = _pip_html(0, 5)
        assert "●" not in html
        assert "○○○○○" in html

    def test_mixed_bar(self):
        html = _pip_html(2, 5)
        assert "●●" in html
        assert "○○○" in html

    def test_zero_max(self):
        html = _pip_html(0, 0)
        assert "●" not in html
        assert "○" not in html


# ===========================================================================
# _AvatarLabel
# ===========================================================================


class TestAvatarLabel:
    def test_initials_from_names(self, qtbot):
        lbl = _AvatarLabel()
        qtbot.addWidget(lbl)
        lbl.set_character("Alice", "Smith")
        assert lbl._initials == "AS"

    def test_initials_first_only(self, qtbot):
        lbl = _AvatarLabel()
        qtbot.addWidget(lbl)
        lbl.set_character("Bob", "")
        assert lbl._initials == "B"

    def test_initials_empty_shows_question(self, qtbot):
        lbl = _AvatarLabel()
        qtbot.addWidget(lbl)
        lbl.set_character("", "")
        assert lbl._initials == "?"

    def test_color_is_deterministic(self, qtbot):
        lbl = _AvatarLabel()
        qtbot.addWidget(lbl)
        lbl.set_character("Alice", "Smith")
        color1 = lbl._color
        lbl.set_character("Alice", "Jones")
        assert lbl._color == color1  # same first letter → same color

    def test_different_first_letters_may_differ(self, qtbot):
        lbl = _AvatarLabel()
        qtbot.addWidget(lbl)
        lbl.set_character("Alice", "X")
        c_a = lbl._color
        lbl.set_character("Zoey", "X")
        c_z = lbl._color
        # A and Z are unlikely to map to the same palette slot; the test
        # is mainly that no exception is raised and both are valid strings.
        assert isinstance(c_a, str)
        assert isinstance(c_z, str)


# ===========================================================================
# CrewTab – load / clear
# ===========================================================================


class TestCrewTabLoad:
    def test_ship_combo_populated(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert tab._ship_combo.count() == 2

    def test_crew_list_populated_for_first_ship(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # First ship alphabetically is HSS ALPHA with 2 crew
        assert tab._crew_list.count() == 2

    def test_crew_list_sorted_alphabetically(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        names = _crew_names(tab)
        assert names == sorted(names)

    def test_crew_count_badge(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        assert tab._crew_count.text() == "2"

    def test_empty_ship_shows_no_crew(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Switch to HSS BETA (index 1) which has no crew
        tab._ship_combo.setCurrentIndex(1)
        assert tab._crew_list.count() == 0
        assert tab._crew_count.text() == "0"

    def test_first_character_panels_populated(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        # First crew member is "Alice Smith"
        assert tab._first_name_edit.text() == "Alice"
        assert tab._last_name_edit.text() == "Smith"

    def test_clear_resets_state(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab.clear()
        assert tab._ship_combo.count() == 0
        assert tab._crew_list.count() == 0
        assert tab._crew_count.text() == "0"
        assert tab._save is None
        assert tab._current_char is None

    def test_right_panel_disabled_before_load(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        assert not tab._first_name_edit.isEnabled()
        assert not tab._tabs.isEnabled()

    def test_right_panel_enabled_after_selection(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        assert tab._first_name_edit.isEnabled()
        assert tab._tabs.isEnabled()

    def test_ship_switch_between_two_populated_crews(self, qtbot):
        """Switching between two ships that both have crew must fully replace the list."""
        tab = CrewTab()
        qtbot.addWidget(tab)
        sf = _make_save(TWO_CREW_SHIPS_XML)
        tab.load(sf)
        assert tab._crew_list.count() == 1
        assert "Alpha" in tab._crew_list.item(0).text()
        tab._ship_combo.setCurrentIndex(1)
        assert tab._crew_list.count() == 1
        assert "Beta" in tab._crew_list.item(0).text()


# ===========================================================================
# CrewTab – character selection
# ===========================================================================


class TestCrewTabSelection:
    def test_selecting_crew_member_updates_name_fields(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(1)  # "Bob Jones"
        assert tab._first_name_edit.text() == "Bob"
        assert tab._last_name_edit.text() == "Jones"

    def test_selecting_crew_member_updates_avatar(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice Smith
        assert tab._avatar._initials == "AS"

    def test_selecting_crew_member_populates_stats(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice: Health=80
        assert tab._stats_spins["Health"].value() == 80

    def test_selecting_crew_member_populates_skills(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice has 2 skills
        assert tab._skills_table.rowCount() == 2

    def test_selecting_crew_member_populates_attributes(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice has 1 attribute
        assert tab._attr_table.rowCount() == 1

    def test_selecting_crew_member_populates_traits(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice has 1 trait
        assert tab._traits_list.count() == 1

    def test_selecting_crew_member_populates_conditions(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice has 1 condition
        assert tab._conditions_list.count() == 1

    def test_selecting_crew_member_populates_relationships(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        assert tab._rel_table.rowCount() == 1


# ===========================================================================
# CrewTab – rename character
# ===========================================================================


class TestRenameCharacter:
    def test_rename_updates_crew_list_item(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice Smith
        tab._first_name_edit.setText("Alicia")
        tab._rename_character()
        assert "Alicia Smith" in _crew_names(tab)

    def test_rename_removes_old_name(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        tab._first_name_edit.setText("Alicia")
        tab._rename_character()
        assert "Alice Smith" not in _crew_names(tab)

    def test_rename_no_duplicate_entries(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        tab._first_name_edit.setText("Alicia")
        tab._rename_character()
        # Total count must not change
        assert tab._crew_list.count() == 2

    def test_rename_list_stays_sorted(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice → ZZZ (should move to end)
        tab._first_name_edit.setText("ZZZ")
        tab._rename_character()
        names = _crew_names(tab)
        assert names == sorted(names)

    def test_rename_updates_avatar_initials(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice Smith → AS
        tab._first_name_edit.setText("Carol")
        tab._last_name_edit.setText("King")
        tab._rename_character()
        assert tab._avatar._initials == "CK"

    def test_rename_empty_first_name_rejected(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        monkeypatch.setattr("src.ui.crew_tab.QMessageBox.warning", lambda *a: None)
        original_name = tab._current_char.full_name
        tab._first_name_edit.setText("")
        tab._rename_character()
        assert tab._current_char.full_name == original_name

    def test_rename_emits_status_message(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        messages = []
        tab.status_message.connect(messages.append)
        tab._first_name_edit.setText("Renamed")
        tab._rename_character()
        assert any("renamed" in m.lower() for m in messages)

    def test_rename_called_twice_no_duplicate(self, qtbot):
        """Simulates Tab-then-Enter: editingFinished fires for both fields."""
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        tab._first_name_edit.setText("Twice")
        tab._rename_character()
        tab._rename_character()  # second call (simulated double-fire)
        assert tab._crew_list.count() == 2
        names = _crew_names(tab)
        assert len(set(names)) == len(names)  # no duplicates

    def test_rename_both_fields_sequential(self, qtbot):
        """Editing first name then last name produces correct final state."""
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice Smith
        # Simulate user tabbing: first name fires editingFinished first
        tab._first_name_edit.setText("Carol")
        tab._rename_character()  # intermediate: "Carol Smith"
        # Then user finishes editing last name
        tab._last_name_edit.setText("King")
        tab._rename_character()  # final: "Carol King"
        assert tab._current_char.full_name == "Carol King"
        assert "Carol King" in _crew_names(tab)
        assert tab._crew_list.count() == 2
        names = _crew_names(tab)
        assert len(set(names)) == len(names)


# ===========================================================================
# CrewTab – remove crew member
# ===========================================================================


class TestRemoveCrewMember:
    def test_remove_decrements_count(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        char = tab._crew_list.item(0).data(Qt.ItemDataRole.UserRole)
        tab._remove_crew_member_by_char(char)
        assert tab._crew_list.count() == 1
        assert tab._crew_count.text() == "1"

    def test_remove_current_char_selects_next(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        removed_char = tab._current_char
        tab._remove_crew_member_by_char(removed_char)
        # With another member remaining, Qt auto-selects them; the removed
        # char must no longer be current and the list must have shrunk.
        assert tab._current_char is not removed_char
        assert tab._crew_list.count() == 1

    def test_remove_non_current_char_keeps_selection(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(1)
        selected_char = tab._current_char
        other_char = tab._crew_list.item(0).data(Qt.ItemDataRole.UserRole)
        tab._remove_crew_member_by_char(other_char)
        assert tab._current_char is selected_char

    def test_remove_emits_status_message(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        messages = []
        tab.status_message.connect(messages.append)
        char = tab._crew_list.item(0).data(Qt.ItemDataRole.UserRole)
        tab._remove_crew_member_by_char(char)
        assert any("removed" in m.lower() for m in messages)


# ===========================================================================
# CrewTab – skill clamping on load
# ===========================================================================


class TestSkillClamping:
    def test_over_max_skill_is_clamped_on_view(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        sf = _make_save(OVER_MAX_XML)
        tab.load(sf)
        # level=15 mxn=20 → both clamped to 10
        assert tab._skills_table.rowCount() == 1
        level_spin: QSpinBox = tab._skills_table.cellWidget(0, 2)
        max_spin: QSpinBox = tab._skills_table.cellWidget(0, 3)
        assert max_spin.value() == 10
        assert level_spin.value() == 10

    def test_over_max_skill_persisted_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        sf = _make_save(OVER_MAX_XML)
        tab.load(sf)
        char = sf.characters[0]
        assert char.skills[0].max_level == 10
        assert char.skills[0].level == 10


# ===========================================================================
# CrewTab – attribute clamping on load
# ===========================================================================


class TestAttributeClamping:
    def test_over_max_attr_is_clamped_on_view(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        sf = _make_save(OVER_MAX_ATTR_XML)
        tab.load(sf)
        # points=15 → clamped to spin max of 10
        assert tab._attr_table.rowCount() == 1
        spin: QSpinBox = tab._attr_table.cellWidget(0, 2)
        assert spin.value() == 10

    def test_over_max_attr_persisted_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        sf = _make_save(OVER_MAX_ATTR_XML)
        tab.load(sf)
        char = sf.characters[0]
        assert char.attributes[0].points == 10


# ===========================================================================
# CrewTab – conditions
# ===========================================================================


class TestConditions:
    def test_remove_condition(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice has 1 condition
        assert tab._conditions_list.count() == 1
        tab._conditions_list.setCurrentRow(0)
        tab._remove_condition()
        assert tab._conditions_list.count() == 0

    def test_clear_all_conditions(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        tab._clear_conditions()
        assert tab._conditions_list.count() == 0

    def test_remove_condition_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        tab._conditions_list.setCurrentRow(0)
        messages = []
        tab.status_message.connect(messages.append)
        tab._remove_condition()
        assert messages

    def test_remove_condition_no_selection_is_noop(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice has 1 condition
        tab._conditions_list.clearSelection()  # nothing selected
        tab._remove_condition()  # must not raise or remove anything
        assert tab._conditions_list.count() == 1


# ===========================================================================
# CrewTab – _unique_crew_name (static, no Qt needed)
# ===========================================================================


class TestUniqueCrewName:
    def test_no_collision(self):
        first, last = CrewTab._unique_crew_name("Alice", "Smith", set())
        assert first == "Alice - Copy"
        assert last == "Smith"

    def test_collision_uses_n2(self):
        existing = {"Alice - Copy Smith"}
        first, last = CrewTab._unique_crew_name("Alice", "Smith", existing)
        assert first == "Alice - Copy 2"
        assert last == "Smith"

    def test_collision_increments(self):
        existing = {"Alice - Copy Smith", "Alice - Copy 2 Smith"}
        first, last = CrewTab._unique_crew_name("Alice", "Smith", existing)
        assert first == "Alice - Copy 3"

    def test_empty_last_name(self):
        first, last = CrewTab._unique_crew_name("Solo", "", set())
        assert first == "Solo - Copy"
        assert last == ""


# ===========================================================================
# Stats – edit / save-back
# ===========================================================================


class TestStatEditing:
    def test_stat_spin_persists_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice: Health=80
        char = tab._current_char
        health_stat = next(s for s in char.stats if s.tag == "Health")
        tab._stats_spins["Health"].setValue(99)
        assert health_stat.value == 99

    def test_stat_spin_all_tags_connected(self, qtbot):
        """Every stat tag must have its spin wired up after selection."""
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice
        char = tab._current_char
        stat_map = {s.tag: s for s in char.stats}
        for tag in ("Health", "Food", "Rest", "Comfort", "Mood", "Temperature"):
            stat = stat_map[tag]
            old = stat.value
            new_val = (old + 1) % 101
            tab._stats_spins[tag].setValue(new_val)
            assert stat.value == new_val

    def test_stat_spin_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        messages = []
        tab.status_message.connect(messages.append)
        tab._stats_spins["Health"].setValue(55)
        assert messages


# ===========================================================================
# Attributes – edit / save-back
# ===========================================================================


class TestAttributeEditing:
    def test_attribute_spin_persists_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice: 1 attribute with 3 points
        attr = tab._current_char.attributes[0]
        spin = tab._attr_table.cellWidget(0, 2)
        spin.setValue(7)
        assert attr.points == 7

    def test_attribute_pip_label_updates(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        lbl = tab._attr_table.cellWidget(0, 1)  # pip label (col 1)
        spin = tab._attr_table.cellWidget(0, 2)  # points spin (col 2)
        spin.setValue(0)
        assert "●" not in lbl.text()

    def test_attribute_spin_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        messages = []
        tab.status_message.connect(messages.append)
        spin = tab._attr_table.cellWidget(0, 2)
        spin.setValue(1)
        assert messages


# ===========================================================================
# Skills – edit / save-back
# ===========================================================================


class TestSkillEditing:
    def test_skill_level_spin_persists_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice: skill[0] level=3 mxn=8
        skill = tab._current_char.skills[0]
        level_spin = tab._skills_table.cellWidget(0, 2)
        level_spin.setValue(5)
        assert skill.level == 5

    def test_skill_max_spin_persists_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        skill = tab._current_char.skills[0]
        max_spin = tab._skills_table.cellWidget(0, 3)
        max_spin.setValue(6)
        assert skill.max_level == 6

    def test_skill_max_constrains_level_spin(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice: level=3, mxn=8
        level_spin = tab._skills_table.cellWidget(0, 2)
        max_spin = tab._skills_table.cellWidget(0, 3)
        max_spin.setValue(2)
        assert level_spin.maximum() == 2

    def test_skill_level_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        messages = []
        tab.status_message.connect(messages.append)
        level_spin = tab._skills_table.cellWidget(0, 2)
        level_spin.setValue(1)
        assert messages

    def test_skill_pip_label_updates_on_level_change(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice: skill[0] level=3 mxn=8
        pip_lbl = tab._skills_table.cellWidget(0, 1)
        level_spin = tab._skills_table.cellWidget(0, 2)
        level_spin.setValue(0)
        assert "●" not in pip_lbl.text()


# ===========================================================================
# Traits – add / remove
# ===========================================================================


class TestTraitEditing:
    @staticmethod
    def _select_trait(tab: CrewTab, trait_id: int) -> None:
        for i in range(tab._add_trait_combo.count()):
            if tab._add_trait_combo.itemData(i) == trait_id:
                tab._add_trait_combo.setCurrentIndex(i)
                return

    def test_add_trait_adds_to_list(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice has 1 trait (Confident 1046)
        self._select_trait(tab, 191)  # Hero – not yet present
        tab._add_trait()
        assert tab._traits_list.count() == 2

    def test_add_trait_persists_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        char = tab._current_char
        self._select_trait(tab, 191)
        tab._add_trait()
        assert any(t.trait_id == 191 for t in char.traits)

    def test_add_duplicate_trait_no_growth(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice already has Confident (1046)
        monkeypatch.setattr("src.ui.crew_tab.QMessageBox.information", lambda *a: None)
        self._select_trait(tab, 1046)
        tab._add_trait()
        assert tab._traits_list.count() == 1

    def test_add_trait_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        messages = []
        tab.status_message.connect(messages.append)
        self._select_trait(tab, 191)
        tab._add_trait()
        assert any("trait" in m.lower() for m in messages)

    def test_remove_trait_removes_from_list(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice has 1 trait
        tab._traits_list.setCurrentRow(0)
        tab._remove_trait()
        assert tab._traits_list.count() == 0

    def test_remove_trait_persists_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        char = tab._current_char
        tab._traits_list.setCurrentRow(0)
        tab._remove_trait()
        assert len(char.traits) == 0

    def test_remove_trait_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        tab._traits_list.setCurrentRow(0)
        messages = []
        tab.status_message.connect(messages.append)
        tab._remove_trait()
        assert messages

    def test_remove_trait_no_selection_shows_message(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice has 1 trait
        tab._traits_list.clearSelection()  # nothing selected
        shown = []
        monkeypatch.setattr(
            "src.ui.crew_tab.QMessageBox.information",
            lambda *a: shown.append(True),
        )
        tab._remove_trait()
        assert tab._traits_list.count() == 1  # unchanged
        assert shown  # user was informed


# ===========================================================================
# Relationships – edit / save-back
# ===========================================================================


class TestRelationshipEditing:
    def test_friendship_edit_persists_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice: friendship=20
        rel = tab._current_char.relationships[0]
        edit = tab._rel_table.cellWidget(0, 1)
        edit.setText("99")
        edit.editingFinished.emit()
        assert rel.friendship == 99

    def test_attraction_edit_persists_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice: attraction=-5
        rel = tab._current_char.relationships[0]
        edit = tab._rel_table.cellWidget(0, 2)
        edit.setText("10")
        edit.editingFinished.emit()
        assert rel.attraction == 10

    def test_compatibility_edit_persists_to_model(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice: compatibility=60
        rel = tab._current_char.relationships[0]
        edit = tab._rel_table.cellWidget(0, 3)
        edit.setText("75")
        edit.editingFinished.emit()
        assert rel.compatibility == 75

    def test_relationship_invalid_text_ignored(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        rel = tab._current_char.relationships[0]
        original = rel.friendship
        edit = tab._rel_table.cellWidget(0, 1)
        edit.setText("not-a-number")
        edit.editingFinished.emit()
        assert rel.friendship == original

    def test_relationship_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)
        messages = []
        tab.status_message.connect(messages.append)
        edit = tab._rel_table.cellWidget(0, 1)
        edit.setText("50")
        edit.editingFinished.emit()
        assert messages

    def test_relationship_target_name_displayed(self, qtbot):
        """Alice's relationship targets Bob (entId=2); column 0 must show his full name."""
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_list.setCurrentRow(0)  # Alice
        name_item = tab._rel_table.item(0, 0)
        assert name_item.text() == "Bob Jones"


# ===========================================================================
# Clone crew member
# ===========================================================================


class TestCloneCrewMember:
    def test_clone_adds_to_list(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._clone_crew_member(0)
        assert tab._crew_list.count() == 3

    def test_clone_uses_copy_name(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._clone_crew_member(0)
        assert any("Copy" in n for n in _crew_names(tab))

    def test_clone_updates_count_badge(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._clone_crew_member(0)
        assert tab._crew_count.text() == "3"

    def test_clone_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        messages = []
        tab.status_message.connect(messages.append)
        tab._clone_crew_member(0)
        assert any("cloned" in m.lower() for m in messages)

    def test_clone_list_stays_sorted(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._clone_crew_member(0)
        names = _crew_names(tab)
        assert names == sorted(names)

    def test_clone_copies_stats(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        source: Character = tab._crew_list.item(0).data(Qt.ItemDataRole.UserRole)
        source_health = next(s for s in source.stats if s.tag == "Health").value
        tab._clone_crew_member(0)
        clone = tab._current_char  # clone is auto-selected after cloning
        clone_health = next(s for s in clone.stats if s.tag == "Health").value
        assert clone_health == source_health

    def test_clone_copies_skills(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        source: Character = tab._crew_list.item(0).data(Qt.ItemDataRole.UserRole)
        source_skill_count = len(source.skills)
        tab._clone_crew_member(0)
        clone = tab._current_char
        assert len(clone.skills) == source_skill_count

    def test_clone_copies_traits(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        source: Character = tab._crew_list.item(0).data(Qt.ItemDataRole.UserRole)
        source_trait_count = len(source.traits)
        tab._clone_crew_member(0)
        clone = tab._current_char
        assert len(clone.traits) == source_trait_count


# ===========================================================================
# Delegate signals – clone ⧉ and remove ✕ icons
# ===========================================================================


class TestDelegateSignals:
    def test_remove_signal_removes_member(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_delegate.remove_requested.emit(0)
        assert tab._crew_list.count() == 1

    def test_remove_signal_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        messages = []
        tab.status_message.connect(messages.append)
        tab._crew_delegate.remove_requested.emit(0)
        assert any("removed" in m.lower() for m in messages)

    def test_clone_signal_clones_member(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        tab._crew_delegate.clone_requested.emit(0)
        assert tab._crew_list.count() == 3

    def test_clone_signal_emits_status(self, qtbot):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        messages = []
        tab.status_message.connect(messages.append)
        tab._crew_delegate.clone_requested.emit(0)
        assert any("cloned" in m.lower() for m in messages)


# ===========================================================================
# Add crew member (dialog path)
# ===========================================================================


class TestAddCrewMember:
    @staticmethod
    def _accept_dialog(first: str, last: str = ""):
        """Return a monkeypatch-compatible exec replacement that fills in names."""

        def _exec(dlg_self):
            for edit in dlg_self.findChildren(QLineEdit):
                if edit.placeholderText() == "First name":
                    edit.setText(first)
                elif edit.placeholderText() == "Last name":
                    edit.setText(last)
            return QDialog.DialogCode.Accepted

        return _exec

    def test_add_member_increases_count(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        monkeypatch.setattr(QDialog, "exec", self._accept_dialog("Carol", "King"))
        tab._add_crew_member()
        assert tab._crew_list.count() == 3

    def test_add_member_updates_count_badge(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        monkeypatch.setattr(QDialog, "exec", self._accept_dialog("Carol", "King"))
        tab._add_crew_member()
        assert tab._crew_count.text() == "3"

    def test_add_member_selects_new_member(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        monkeypatch.setattr(QDialog, "exec", self._accept_dialog("NewGuy", "Test"))
        tab._add_crew_member()
        assert tab._current_char is not None
        assert tab._current_char.first_name == "NewGuy"

    def test_add_member_list_stays_sorted(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        monkeypatch.setattr(QDialog, "exec", self._accept_dialog("Aaron", "Zzz"))
        tab._add_crew_member()
        names = _crew_names(tab)
        assert names == sorted(names)

    def test_add_member_cancel_is_noop(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        monkeypatch.setattr(QDialog, "exec", lambda s: QDialog.DialogCode.Rejected)
        tab._add_crew_member()
        assert tab._crew_list.count() == 2

    def test_add_member_empty_first_name_rejected(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        monkeypatch.setattr(QDialog, "exec", self._accept_dialog("", "Smith"))
        monkeypatch.setattr("src.ui.crew_tab.QMessageBox.warning", lambda *a: None)
        tab._add_crew_member()
        assert tab._crew_list.count() == 2  # unchanged

    def test_add_member_emits_status(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        monkeypatch.setattr(QDialog, "exec", self._accept_dialog("Status", "User"))
        messages = []
        tab.status_message.connect(messages.append)
        tab._add_crew_member()
        assert any("added" in m.lower() for m in messages)

    def test_add_member_right_panel_populated(self, qtbot, monkeypatch):
        tab = CrewTab()
        qtbot.addWidget(tab)
        tab.load(_make_save())
        monkeypatch.setattr(QDialog, "exec", self._accept_dialog("Fresh", "Start"))
        tab._add_crew_member()
        assert tab._first_name_edit.text() == "Fresh"
        assert tab._last_name_edit.text() == "Start"
