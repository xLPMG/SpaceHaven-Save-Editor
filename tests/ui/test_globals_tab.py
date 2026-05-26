"""Tests for src/ui/globals_tab.py using pytest-qt and a minimal SaveFile fixture."""

from __future__ import annotations

import io
import textwrap

from lxml import etree
from PySide6.QtCore import Qt

from src.save_file import SaveFile
from src.ui.globals_tab import GlobalsTab, _EditCard

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
                <Health v="50"/><Food v="90"/><Rest v="80"/>
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
                  <s sk="22" level="2" mxn="10" exp="0" expd="0"/>
                </skills>
              </pers>
            </c>
          </characters>
          <storage>
            <stacks>
              <stack itemId="1" amount="100"/>
              <stack itemId="2" amount="200"/>
            </stacks>
          </storage>
        </ship>
        <ship sid="20" sname="HSS BETA" sx="28" sy="28">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")

SANDBOX_XML = textwrap.dedent("""\
    <game mode="Normal" seed="99">
      <playerBank ca="5000" cr="0"/>
      <settings><diff sandbox="true"/></settings>
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
# _EditCard
# ===========================================================================


class TestEditCard:
    def test_label_displayed(self, qtbot):
        card = _EditCard("Test Label", "Test description")
        qtbot.addWidget(card)
        # Find the label widget by its ObjectName
        labels = card.findChildren(type(card).staticMetaObject.__class__)
        names = [
            w.text()
            for w in card.findChildren(card.layout().itemAt(0).widget().__class__)
        ]
        assert "Test Label" in names

    def test_spin_range_set(self, qtbot):
        card = _EditCard("Test", "Desc")
        qtbot.addWidget(card)
        assert card.spin.minimum() == 0
        assert card.spin.maximum() == 2_000_000_000

    def test_spin_accepts_value(self, qtbot):
        card = _EditCard("Test", "Desc")
        qtbot.addWidget(card)
        card.spin.setValue(12345)
        assert card.spin.value() == 12345


# ===========================================================================
# GlobalsTab – load / clear
# ===========================================================================


class TestGlobalsTabLoad:
    def test_initial_state_controls_disabled(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        assert not tab._credits_card.spin.isEnabled()
        assert not tab._prestige_card.spin.isEnabled()
        assert not tab._sandbox_check.isEnabled()
        assert not tab._heal_btn.isEnabled()
        assert not tab._skills_btn.isEnabled()
        assert not tab._conditions_btn.isEnabled()

    def test_load_enables_controls(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert tab._credits_card.spin.isEnabled()
        assert tab._prestige_card.spin.isEnabled()
        assert tab._sandbox_check.isEnabled()
        assert tab._heal_btn.isEnabled()
        assert tab._skills_btn.isEnabled()
        assert tab._conditions_btn.isEnabled()

    def test_load_populates_credits(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert tab._credits_card.spin.value() == 1000

    def test_load_populates_prestige(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert tab._prestige_card.spin.value() == 8

    def test_load_populates_sandbox_false(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert not tab._sandbox_check.isChecked()

    def test_load_populates_sandbox_true(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save(SANDBOX_XML)
        tab.load(sf)
        assert tab._sandbox_check.isChecked()

    def test_load_populates_info_labels(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert tab._info_labels["mode"].text() == "Normal"
        assert tab._info_labels["seed"].text() == "42"
        assert tab._info_labels["ships"].text() == "2"
        assert tab._info_labels["crew"].text() == "2"

    def test_load_gametime_shows_dash_if_no_info(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # No save_info in our minimal fixture, so it should show dash
        assert tab._info_labels["gametime"].text() == "—"

    def test_clear_resets_values(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab.clear()
        assert tab._credits_card.spin.value() == 0
        assert tab._prestige_card.spin.value() == 0
        assert not tab._sandbox_check.isChecked()

    def test_clear_disables_controls(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab.clear()
        assert not tab._credits_card.spin.isEnabled()
        assert not tab._prestige_card.spin.isEnabled()
        assert not tab._sandbox_check.isEnabled()
        assert not tab._heal_btn.isEnabled()
        assert not tab._skills_btn.isEnabled()
        assert not tab._conditions_btn.isEnabled()

    def test_clear_resets_info_labels(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab.clear()
        for key in [
            "mode",
            "seed",
            "ships",
            "crew",
            "gametime",
            "sectors",
            "savedate",
            "systems",
        ]:
            assert tab._info_labels[key].text() == "—"

    def test_clear_nullifies_save(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab.clear()
        assert tab._save is None


# ===========================================================================
# GlobalsTab – editing resources
# ===========================================================================


class TestGlobalsTabEditing:
    def test_credits_change_persists_to_model(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._credits_card.spin.setValue(5000)
        assert sf.get_credits() == 5000

    def test_prestige_change_persists_to_model(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._prestige_card.spin.setValue(200)
        assert sf.get_prestige() == 200

    def test_sandbox_change_persists_to_model(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._sandbox_check.setChecked(True)
        assert sf.get_sandbox() is True

    def test_credits_change_emits_status(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._credits_card.spin.setValue(9999)
        assert "unsaved" in blocker.args[0].lower()

    def test_prestige_change_emits_status(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._prestige_card.spin.setValue(150)
        assert "unsaved" in blocker.args[0].lower()

    def test_sandbox_change_emits_status(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._sandbox_check.setChecked(True)
        assert "unsaved" in blocker.args[0].lower()

    def test_no_signal_before_load(self, qtbot):
        """Changing values before load should not emit signals or crash."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        # These should not crash or emit signals
        tab._credits_card.spin.setValue(1000)
        tab._prestige_card.spin.setValue(50)
        tab._sandbox_check.setChecked(True)

    def test_load_does_not_trigger_signals(self, qtbot):
        """Loading a save should not emit status_message (uses blockSignals)."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        # We should NOT receive a signal during load
        signal_received = False

        def on_signal(msg):
            nonlocal signal_received
            signal_received = True

        tab.status_message.connect(on_signal)
        tab.load(sf)
        assert not signal_received

    def test_clear_does_not_trigger_signals(self, qtbot):
        """Clearing should not emit status_message (uses blockSignals)."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        signal_received = False

        def on_signal(msg):
            nonlocal signal_received
            signal_received = True

        tab.status_message.connect(on_signal)
        tab.clear()
        assert not signal_received


# ===========================================================================
# GlobalsTab – quick actions
# ===========================================================================


class TestGlobalsTabQuickActions:
    def test_heal_all_crew(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Bob has Health=50, should be healed to 100
        bob = sf.characters[1]
        health_stat = next(s for s in bob.stats if s.tag == "Health")
        assert health_stat.value == 50
        tab._heal_all_crew()
        assert health_stat.value == 100

    def test_heal_all_crew_emits_status(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._heal_all_crew()
        msg = blocker.args[0]
        assert "healed" in msg.lower()
        assert "2" in msg  # 2 crew members

    def test_max_all_skills(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Alice has skills at level 3 and 5
        alice = sf.characters[0]
        assert alice.skills[0].level == 3
        tab._max_all_skills()
        assert alice.skills[0].level == 20
        assert alice.skills[0].max_level == 20

    def test_max_all_skills_emits_status(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._max_all_skills()
        msg = blocker.args[0]
        assert "maxed" in msg.lower() or "skill" in msg.lower()

    def test_clear_all_conditions(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Alice has 1 condition
        assert len(sf.characters[0].conditions) == 1
        tab._clear_all_conditions()
        assert len(sf.characters[0].conditions) == 0

    def test_clear_all_conditions_emits_status(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._clear_all_conditions()
        msg = blocker.args[0]
        assert "cleared" in msg.lower() or "condition" in msg.lower()

    def test_fill_all_storage(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        # Storage has items with amount 100 and 200
        tab._fill_qty_spin.setValue(9999)
        tab._fill_all_storage()
        # Verify by checking the model
        containers = sf.get_storage_containers(sf.ships[0])
        for container in containers:
            for item in container.items:
                assert item.amount == 9999

    def test_fill_all_storage_emits_status(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._fill_qty_spin.setValue(5000)
        with qtbot.waitSignal(tab.status_message, timeout=1000) as blocker:
            tab._fill_all_storage()
        msg = blocker.args[0]
        assert "storage" in msg.lower()
        assert "5,000" in msg or "5000" in msg

    def test_fill_storage_with_custom_quantity(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        tab._fill_qty_spin.setValue(123)
        tab._fill_all_storage()
        # Verify by checking the model
        containers = sf.get_storage_containers(sf.ships[0])
        for container in containers:
            for item in container.items:
                assert item.amount == 123

    def test_quick_actions_no_crash_without_save(self, qtbot):
        """Quick actions should not crash when called without a loaded save."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        # These should not crash
        tab._heal_all_crew()
        tab._max_all_skills()
        tab._clear_all_conditions()
        tab._fill_all_storage()


# ===========================================================================
# GlobalsTab – fill storage spinbox
# ===========================================================================


class TestGlobalsTabFillStorage:
    def test_fill_qty_spin_default_value(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        assert tab._fill_qty_spin.value() == 9999

    def test_fill_qty_spin_range(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        assert tab._fill_qty_spin.minimum() == 1
        assert tab._fill_qty_spin.maximum() == 1_000_000

    def test_fill_qty_spin_disabled_initially(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        assert not tab._fill_qty_spin.isEnabled()

    def test_fill_qty_spin_enabled_after_load(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert tab._fill_qty_spin.isEnabled()

    def test_fill_btn_disabled_initially(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        assert not tab._fill_btn.isEnabled()

    def test_fill_btn_enabled_after_load(self, qtbot):
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        assert tab._fill_btn.isEnabled()


# ===========================================================================
# GlobalsTab – info labels with edge cases
# ===========================================================================


class TestGlobalsTabInfoLabels:
    def test_info_labels_are_selectable(self, qtbot):
        """Info labels should allow text selection."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        flags = tab._info_labels["seed"].textInteractionFlags()
        assert flags & Qt.TextInteractionFlag.TextSelectableByMouse

    def test_path_label_is_selectable(self, qtbot):
        """Path label should allow text selection."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        flags = tab._info_labels["path"].textInteractionFlags()
        assert flags & Qt.TextInteractionFlag.TextSelectableByMouse

    def test_no_sectors_shows_dash(self, qtbot):
        """When sectors is None or empty, show dash."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.sectors = None
        tab.load(sf)
        assert tab._info_labels["sectors"].text() == "—"

    def test_path_shows_folder_if_available(self, qtbot):
        """If folder is set, it should be shown instead of path."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.folder = "/test/folder"
        sf.path = "/test/path/file.xml"
        tab.load(sf)
        assert "/test/folder" in tab._info_labels["path"].text()

    def test_path_shows_path_if_no_folder(self, qtbot):
        """If folder is None but path exists, show path."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.folder = None
        sf.path = "/test/path/file.xml"
        tab.load(sf)
        assert "/test/path/file.xml" in tab._info_labels["path"].text()

    def test_path_shows_dash_if_neither(self, qtbot):
        """If both folder and path are None, show dash."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        sf.folder = None
        sf.path = None
        tab.load(sf)
        assert tab._info_labels["path"].text() == "—"


# ===========================================================================
# GlobalsTab – signal connections
# ===========================================================================


class TestGlobalsTabSignalConnections:
    def test_credits_spin_connected(self, qtbot):
        """Credits spin should trigger _apply_changes."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        signal_count = 0

        def on_signal(msg):
            nonlocal signal_count
            signal_count += 1

        tab.status_message.connect(on_signal)
        tab._credits_card.spin.setValue(2000)
        assert signal_count == 1

    def test_prestige_spin_connected(self, qtbot):
        """Prestige spin should trigger _apply_changes."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        signal_count = 0

        def on_signal(msg):
            nonlocal signal_count
            signal_count += 1

        tab.status_message.connect(on_signal)
        tab._prestige_card.spin.setValue(50)
        assert signal_count == 1

    def test_sandbox_check_connected(self, qtbot):
        """Sandbox checkbox should trigger _apply_changes."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        sf = _make_save()
        tab.load(sf)
        signal_count = 0

        def on_signal(msg):
            nonlocal signal_count
            signal_count += 1

        tab.status_message.connect(on_signal)
        tab._sandbox_check.setChecked(True)
        assert signal_count == 1


# ===========================================================================
# GlobalsTab – step values
# ===========================================================================


class TestGlobalsTabStepValues:
    def test_credits_spin_step(self, qtbot):
        """Credits should increment by 1000."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        assert tab._credits_card.spin.singleStep() == 1000

    def test_prestige_spin_step(self, qtbot):
        """Prestige should increment by 100."""
        tab = GlobalsTab()
        qtbot.addWidget(tab)
        assert tab._prestige_card.spin.singleStep() == 100
