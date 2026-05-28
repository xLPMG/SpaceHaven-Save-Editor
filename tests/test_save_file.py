"""Unit tests for src/save_file.py using minimal XML fixtures."""

from __future__ import annotations

import textwrap

import pytest

from src.save_file import (
    Character,
    SaveFile,
    SKILL_HARD_MAX,
)
from src.game_data import STAT_TAGS, TRAIT_IDS
from tests.helpers import make_save_from_xml as _make_save_file

# Trait IDs resolved from TRAIT_IDS for use in mutation tests
_FAST_LEARNER_ID = next(k for k, v in TRAIT_IDS.items() if v == "Fast learner")
_CONFIDENT_ID = next(k for k, v in TRAIT_IDS.items() if v == "Confident")

# Minimal complete game XML mirroring the real save file structure
MINIMAL_XML = textwrap.dedent("""\
    <game mode="Normal" seed="42">
      <playerBank ca="767" cr="0"/>
      <settings>
        <diff sandbox="false"/>
      </settings>
      <questLines>
        <questLines>
          <l type="ExodusFleet" playerPrestigePoints="8"/>
        </questLines>
      </questLines>
      <ships>
        <ship sid="89" sname="HSS NEPHTHYS" sx="56" sy="56">
          <e entId="200" objId="storage1">
            <wm>
              <up>
                <feat eatAllowed="1" cp="0" cpa="0">
                  <inv>
                    <s elementaryId="16" inStorage="50" onTheWayIn="0" onTheWayOut="0"/>
                    <s elementaryId="63" inStorage="30" onTheWayIn="0" onTheWayOut="0"/>
                  </inv>
                </feat>
              </up>
            </wm>
          </e>
          <characters>
            <c entId="90" name="Jarvis" lname="Michael" cid="89">
              <props>
                <Health v="80"/>
                <Food v="100"/>
                <Rest v="94"/>
                <Comfort v="50"/>
                <Mood v="91"/>
                <Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr>
                  <a points="2" id="210"/>
                  <a points="5" id="213"/>
                </attr>
                <traits>
                  <t id="1046"/>
                </traits>
                <conditions>
                  <c id="3307"/>
                  <c id="1109"/>
                </conditions>
                <sociality>
                  <relationships>
                    <l targetId="91" friendship="20" attraction="-10" compatibility="62"/>
                  </relationships>
                </sociality>
                <skills>
                  <s sk="6" level="3" mxn="8" exp="0" expd="0"/>
                  <s sk="14" level="5" mxn="7" exp="0" expd="0"/>
                </skills>
              </pers>
            </c>
            <c entId="91" name="Airek" lname="McPherson" cid="89">
              <props>
                <Health v="150"/>
                <Food v="100"/>
                <Rest v="153"/>
                <Comfort v="50"/>
                <Mood v="22"/>
                <Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr>
                  <a points="1" id="212"/>
                </attr>
                <traits/>
                <conditions/>
                <sociality>
                  <relationships>
                    <l targetId="90" friendship="15" attraction="5" compatibility="40"/>
                  </relationships>
                </sociality>
                <skills>
                  <s sk="22" level="0" mxn="0" exp="0" expd="0"/>
                </skills>
              </pers>
            </c>
          </characters>
        </ship>
      </ships>
      <research treeId="2535">
        <states>
          <l techId="2532" paused="false" activeStageIndex="0">
            <stageStates>
              <l stage="1" done="false">
                <blocksDone level1="15" level2="0" level3="0"/>
              </l>
            </stageStates>
          </l>
          <l techId="2628" paused="false" activeStageIndex="1">
            <stageStates>
              <l stage="1" done="true">
                <blocksDone level1="140" level2="60" level3="20"/>
              </l>
            </stageStates>
          </l>
          <l techId="2533" paused="false" activeStageIndex="0">
            <stageStates>
              <l stage="1" done="false">
                <blocksDone level1="0" level2="0" level3="0"/>
              </l>
            </stageStates>
          </l>
        </states>
      </research>
    </game>
""")


# ---------------------------------------------------------------------------
# Dataclass tests
# ---------------------------------------------------------------------------


class TestDataclasses:
    def test_character_full_name(self):
        char = Character(
            ent_id=1, first_name="Jarvis", last_name="Michael", ship_sid=89
        )
        assert char.full_name == "Jarvis Michael"

    def test_character_full_name_no_last(self):
        char = Character(ent_id=2, first_name="Solo", last_name="", ship_sid=89)
        assert char.full_name == "Solo"


# ---------------------------------------------------------------------------
# SaveFile.load / root validation
# ---------------------------------------------------------------------------


class TestSaveFileLoad:
    def test_load_invalid_root_raises(self, tmp_path):
        p = tmp_path / "game"
        p.write_bytes(b"<notgame/>")
        sf = SaveFile()
        with pytest.raises(ValueError, match="root element must be <game>"):
            sf.load(str(p))

    def test_load_sets_path(self, tmp_path):
        p = tmp_path / "game"
        p.write_bytes(MINIMAL_XML.encode())
        sf = SaveFile()
        sf.load(str(p))
        assert sf.path == p


# ---------------------------------------------------------------------------
# Global getters / setters
# ---------------------------------------------------------------------------


class TestGlobalSettings:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)

    def test_get_game_mode(self):
        assert self.sf.get_game_mode() == "Normal"

    def test_get_seed(self):
        assert self.sf.get_seed() == "42"

    def test_get_credits(self):
        assert self.sf.get_credits() == 767

    def test_set_credits(self):
        self.sf.set_credits(9999)
        assert self.sf.get_credits() == 9999

    def test_set_credits_reflected_in_xml(self):
        self.sf.set_credits(1234)
        el = self.sf._root.find("playerBank")
        assert el.get("ca") == "1234"

    def test_get_sandbox_false(self):
        assert self.sf.get_sandbox() is False

    def test_set_sandbox_true(self):
        self.sf.set_sandbox(True)
        assert self.sf.get_sandbox() is True

    def test_set_sandbox_false(self):
        self.sf.set_sandbox(True)
        self.sf.set_sandbox(False)
        assert self.sf.get_sandbox() is False

    def test_get_prestige(self):
        assert self.sf.get_prestige() == 8

    def test_set_prestige(self):
        self.sf.set_prestige(100)
        assert self.sf.get_prestige() == 100


class TestGlobalSettingsMissing:
    """Graceful fallbacks when optional XML elements are absent."""

    def test_get_credits_no_playerbank(self):
        xml = b"<game mode='Normal' seed='0'/>"
        sf = _make_save_file(xml)
        assert sf.get_credits() == 0

    def test_get_sandbox_no_settings(self):
        xml = b"<game mode='Normal' seed='0'/>"
        sf = _make_save_file(xml)
        assert sf.get_sandbox() is False

    def test_get_prestige_no_questlines(self):
        xml = b"<game mode='Normal' seed='0'/>"
        sf = _make_save_file(xml)
        assert sf.get_prestige() == 0

    def test_get_game_mode_missing_attr(self):
        xml = b"<game seed='0'/>"
        sf = _make_save_file(xml)
        assert sf.get_game_mode() == "Normal"


# ---------------------------------------------------------------------------
# Ship parsing
# ---------------------------------------------------------------------------


class TestShipParsing:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)

    def test_one_ship_loaded(self):
        assert len(self.sf.ships) == 1

    def test_ship_attributes(self):
        ship = self.sf.ships[0]
        assert ship.sid == 89
        assert ship.name == "HSS NEPHTHYS"
        assert ship.sx == 56
        assert ship.sy == 56

    def test_ship_element_present(self):
        assert self.sf.ships[0].element is not None

    def test_no_ships_section(self):
        sf = _make_save_file(b"<game mode='Normal' seed='0'/>")
        assert sf.ships == []

    def test_duplicate_sid_skipped(self):
        xml = textwrap.dedent("""\
            <game mode="Normal" seed="0">
              <ships>
                <ship sid="1" sname="Alpha" sx="0" sy="0"/>
                <ship sid="1" sname="Duplicate" sx="0" sy="0"/>
              </ships>
            </game>
        """)
        sf = _make_save_file(xml.encode())
        assert len(sf.ships) == 1
        assert sf.ships[0].name == "Alpha"

    def test_ships_sorted_by_name(self):
        xml = textwrap.dedent("""\
            <game mode="Normal" seed="0">
              <ships>
                <ship sid="2" sname="Zebra" sx="0" sy="0"/>
                <ship sid="1" sname="Alpha" sx="0" sy="0"/>
              </ships>
            </game>
        """)
        sf = _make_save_file(xml.encode())
        assert [s.name for s in sf.ships] == ["Alpha", "Zebra"]

    def test_rename_ship(self):
        ship = self.sf.ships[0]
        self.sf.rename_ship(ship, "NEW NAME")
        assert ship.name == "NEW NAME"
        assert ship.element.get("sname") == "NEW NAME"


# ---------------------------------------------------------------------------
# Storage parsing and mutations
# ---------------------------------------------------------------------------


class TestStorageParsing:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)
        self.ship = self.sf.ships[0]
        self.containers = self.sf.get_storage_containers(self.ship)

    def test_one_container_found(self):
        assert len(self.containers) == 1

    def test_container_has_two_items(self):
        assert len(self.containers[0].items) == 2

    def test_item_names_resolved(self):
        names = {i.name for i in self.containers[0].items}
        assert "Water" in names
        assert "Oxygen" in names

    def test_item_quantities(self):
        water = next(i for i in self.containers[0].items if i.name == "Water")
        assert water.quantity == 50

    def test_items_sorted_by_name(self):
        names = [i.name for i in self.containers[0].items]
        assert names == sorted(names)


class TestStorageMutations:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)
        self.ship = self.sf.ships[0]
        self.container = self.sf.get_storage_containers(self.ship)[0]

    def test_set_storage_quantity(self):
        item = self.container.items[0]
        self.sf.set_storage_quantity(item, 999)
        assert item.quantity == 999
        assert item.element.get("inStorage") == "999"

    def test_add_new_storage_item(self):
        before = len(self.container.items)
        self.sf.add_storage_item(self.container, 157, 10)  # Base Metals
        assert len(self.container.items) == before + 1

    def test_add_existing_item_accumulates(self):
        water = next(i for i in self.container.items if i.item_id == 16)
        original_qty = water.quantity
        self.sf.add_storage_item(self.container, 16, 5)
        assert water.quantity == original_qty + 5

    def test_add_unknown_item_uses_fallback_name(self):
        self.sf.add_storage_item(self.container, 99999, 1)
        item = next(i for i in self.container.items if i.item_id == 99999)
        assert "99999" in item.name

    def test_remove_storage_item(self):
        item = self.container.items[0]
        before = len(self.container.items)
        self.sf.remove_storage_item(self.container, item)
        assert len(self.container.items) == before - 1
        assert item not in self.container.items

    def test_remove_storage_item_removes_xml_element(self):
        item = self.container.items[0]
        parent = item.element.getparent()
        self.sf.remove_storage_item(self.container, item)
        assert item.element not in parent

    def test_fill_all_storage(self):
        count = self.sf.fill_all_storage(999)
        # get_storage_containers is cached, so it returns the same objects
        containers = self.sf.get_storage_containers(self.ship)
        for item in containers[0].items:
            assert item.quantity == 999
        assert count == 2


# ---------------------------------------------------------------------------
# Character parsing
# ---------------------------------------------------------------------------


class TestCharacterParsing:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)

    def test_two_characters_loaded(self):
        assert len(self.sf.characters) == 2

    def test_character_names(self):
        names = {c.full_name for c in self.sf.characters}
        assert "Jarvis Michael" in names
        assert "Airek McPherson" in names

    def test_character_ship_sid(self):
        for c in self.sf.characters:
            assert c.ship_sid == 89

    def test_character_stats_parsed(self):
        jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")
        assert len(jarvis.stats) == len(STAT_TAGS)
        health = next(s for s in jarvis.stats if s.tag == "Health")
        assert health.value == 80

    def test_character_attributes_parsed(self):
        jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")
        assert len(jarvis.attributes) == 2
        bravery = next(a for a in jarvis.attributes if a.attr_id == 210)
        assert bravery.name == "Bravery"
        assert bravery.points == 2

    def test_character_skills_parsed(self):
        jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")
        assert len(jarvis.skills) == 2
        medical = next(s for s in jarvis.skills if s.skill_id == 6)
        assert medical.name == "Medical"
        assert medical.level == 3
        assert medical.max_level == 8

    def test_skills_sorted_by_name(self):
        jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")
        names = [s.name for s in jarvis.skills]
        assert names == sorted(names)

    def test_character_traits_parsed(self):
        jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")
        assert len(jarvis.traits) == 1
        assert jarvis.traits[0].trait_id == 1046
        assert jarvis.traits[0].name == "Confident"

    def test_character_conditions_parsed(self):
        jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")
        cond_ids = {c.cond_id for c in jarvis.conditions}
        assert 3307 in cond_ids
        assert 1109 in cond_ids

    def test_character_relationships_parsed(self):
        jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")
        assert len(jarvis.relationships) == 1
        rel = jarvis.relationships[0]
        assert rel.target_id == 91
        assert rel.friendship == 20
        assert rel.attraction == -10
        assert rel.compatibility == 62

    def test_relationship_names_resolved(self):
        jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")
        rel = jarvis.relationships[0]
        assert rel.target_name == "Airek McPherson"

    def test_duplicate_entid_skipped(self):
        xml = textwrap.dedent("""\
            <game mode="Normal" seed="0">
              <ships>
                <ship sid="1" sname="Alpha" sx="0" sy="0">
                  <characters>
                    <c entId="10" name="First" lname=""/>
                    <c entId="10" name="Duplicate" lname=""/>
                  </characters>
                </ship>
              </ships>
            </game>
        """)
        sf = _make_save_file(xml.encode())
        assert len(sf.characters) == 1
        assert sf.characters[0].first_name == "First"


# ---------------------------------------------------------------------------
# Character mutations
# ---------------------------------------------------------------------------


class TestCharacterMutations:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)
        self.jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")

    def test_set_stat(self):
        health = next(s for s in self.jarvis.stats if s.tag == "Health")
        self.sf.set_stat(health, 100)
        assert health.value == 100
        assert health.element.get("v") == "100"

    def test_set_attribute(self):
        bravery = next(a for a in self.jarvis.attributes if a.attr_id == 210)
        self.sf.set_attribute(bravery, 10)
        assert bravery.points == 10
        assert bravery.element.get("points") == "10"

    def test_set_skill_level(self):
        medical = next(s for s in self.jarvis.skills if s.skill_id == 6)
        self.sf.set_skill_level(medical, 20)
        assert medical.level == 20
        assert medical.element.get("level") == "20"

    def test_set_skill_max(self):
        medical = next(s for s in self.jarvis.skills if s.skill_id == 6)
        self.sf.set_skill_max(medical, 20)
        assert medical.max_level == 20
        assert medical.element.get("mxn") == "20"

    def test_rename_character(self):
        self.sf.rename_character(self.jarvis, "John", "Doe")
        assert self.jarvis.first_name == "John"
        assert self.jarvis.last_name == "Doe"
        assert self.jarvis.element.get("name") == "John"
        assert self.jarvis.element.get("lname") == "Doe"

    def test_add_trait(self):
        trait = self.sf.add_trait(self.jarvis, _FAST_LEARNER_ID)  # Fast learner
        assert trait is not None
        assert any(t.trait_id == _FAST_LEARNER_ID for t in self.jarvis.traits)

    def test_add_trait_no_duplicate(self):
        self.sf.add_trait(self.jarvis, _FAST_LEARNER_ID)
        result = self.sf.add_trait(self.jarvis, _FAST_LEARNER_ID)
        assert result is None
        assert sum(1 for t in self.jarvis.traits if t.trait_id == _FAST_LEARNER_ID) == 1

    def test_add_unknown_trait_uses_fallback_name(self):
        trait = self.sf.add_trait(self.jarvis, 99999)
        assert "99999" in trait.name

    def test_remove_trait(self):
        trait = self.jarvis.traits[0]
        self.sf.remove_trait(self.jarvis, trait)
        assert trait not in self.jarvis.traits

    def test_remove_trait_removes_xml(self):
        trait = self.jarvis.traits[0]
        parent = trait.element.getparent()
        self.sf.remove_trait(self.jarvis, trait)
        assert trait.element not in parent

    def test_remove_condition(self):
        cond = self.jarvis.conditions[0]
        before = len(self.jarvis.conditions)
        self.sf.remove_condition(self.jarvis, cond)
        assert len(self.jarvis.conditions) == before - 1

    def test_clear_conditions(self):
        self.sf.clear_conditions(self.jarvis)
        assert self.jarvis.conditions == []

    def test_clear_conditions_removes_xml_children(self):
        self.sf.clear_conditions(self.jarvis)
        conds_el = self.jarvis.pers_element.find("conditions")
        assert len(conds_el.findall("c")) == 0


# ---------------------------------------------------------------------------
# Batch operations
# ---------------------------------------------------------------------------


class TestBatchOperations:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)

    def test_heal_all_crew(self):
        count = self.sf.heal_all_crew()
        assert count == 2
        for char in self.sf.characters:
            for stat in char.stats:
                assert stat.value == 100

    def test_heal_all_crew_updates_xml(self):
        self.sf.heal_all_crew()
        for char in self.sf.characters:
            for stat in char.stats:
                assert stat.element.get("v") == "100"

    def test_max_all_skills(self):
        count = self.sf.max_all_skills()
        assert count > 0
        for char in self.sf.characters:
            for skill in char.skills:
                assert skill.level == SKILL_HARD_MAX
                assert skill.max_level == SKILL_HARD_MAX

    def test_clear_all_conditions(self):
        # Count characters with at least one condition before clearing.
        expected = sum(1 for c in self.sf.characters if c.conditions)
        count = self.sf.clear_all_conditions()
        assert count == expected
        for char in self.sf.characters:
            assert char.conditions == []

    def test_clear_all_conditions_idempotent(self):
        self.sf.clear_all_conditions()
        count = self.sf.clear_all_conditions()  # second call: nothing left to clear
        assert count == 0


# ---------------------------------------------------------------------------
# Research
# ---------------------------------------------------------------------------


class TestResearchParsing:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)

    def test_research_entries_loaded(self):
        assert len(self.sf.research) == 3

    def test_research_sorted_by_name(self):
        names = [r.name for r in self.sf.research]
        assert names == sorted(names)

    def test_done_entry_detected(self):
        done = [r for r in self.sf.research if r.done]
        assert len(done) == 1
        # techId 2628 maps to a known tech; just verify done=True
        assert done[0].done is True

    def test_in_progress_entry_detected(self):
        # techId 2532 has level1=15 (partial), not done
        scanner = next(r for r in self.sf.research if r.tech_id == 2532)
        assert scanner.in_progress is True
        assert scanner.done is False

    def test_not_started_entry(self):
        # techId 2533 has all zeros
        shield_gen = next(r for r in self.sf.research if r.tech_id == 2533)
        assert shield_gen.in_progress is False
        assert shield_gen.done is False


class TestResearchMutations:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)

    def test_complete_research(self):
        scanner = next(r for r in self.sf.research if r.tech_id == 2532)
        self.sf.complete_research(scanner)
        assert scanner.done is True
        assert scanner.in_progress is False

    def test_complete_research_sets_xml(self):
        scanner = next(r for r in self.sf.research if r.tech_id == 2532)
        self.sf.complete_research(scanner)
        for stage_el in scanner.element.find("stageStates").findall("l"):
            assert stage_el.get("done") == "true"

    def test_complete_all_research(self):
        count = self.sf.complete_all_research()
        # 2 entries are not done (2532 in-progress, 2533 not started)
        assert count == 2
        for entry in self.sf.research:
            assert entry.done is True

    def test_complete_all_research_idempotent(self):
        self.sf.complete_all_research()
        count = self.sf.complete_all_research()
        assert count == 0


# ---------------------------------------------------------------------------
# Save / backup
# ---------------------------------------------------------------------------


class TestSaveAndBackup:
    def test_save_reflects_mutations(self, tmp_path):
        p = tmp_path / "game"
        p.write_bytes(MINIMAL_XML.encode())
        sf = SaveFile()
        sf.load(str(p))
        sf.set_credits(5000)
        sf.save()

        # Re-load from disk to confirm the mutation was actually written.
        sf2 = SaveFile()
        sf2.load(str(p))
        assert sf2.get_credits() == 5000

    def test_save_no_path_raises(self):
        sf = SaveFile()
        with pytest.raises(ValueError, match="No save path"):
            sf.save()

    def test_backup_creates_file(self, tmp_path):
        p = tmp_path / "game"
        p.write_bytes(MINIMAL_XML.encode())
        sf = SaveFile()
        sf.load(str(p))

        backup_path = sf.backup()
        assert backup_path.exists()
        assert backup_path.read_bytes() == MINIMAL_XML.encode()

    def test_backup_filename_contains_timestamp(self, tmp_path):
        p = tmp_path / "game"
        p.write_bytes(MINIMAL_XML.encode())
        sf = SaveFile()
        sf.load(str(p))

        backup_path = sf.backup()
        assert backup_path.name.startswith("game.backup.")

    def test_backup_no_path_raises(self):
        """backup() must raise ValueError when no file has been loaded."""
        sf = SaveFile()
        with pytest.raises(ValueError, match="No file loaded"):
            sf.backup()


# ---------------------------------------------------------------------------
# Relationship setters
# ---------------------------------------------------------------------------


class TestRelationshipMutations:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)
        self.jarvis = next(c for c in self.sf.characters if c.first_name == "Jarvis")
        self.rel = self.jarvis.relationships[0]

    def test_set_friendship(self):
        self.sf.set_friendship(self.rel, 80)
        assert self.rel.friendship == 80
        assert self.rel.element.get("friendship") == "80"

    def test_set_friendship_negative(self):
        self.sf.set_friendship(self.rel, -50)
        assert self.rel.friendship == -50
        assert self.rel.element.get("friendship") == "-50"

    def test_set_attraction(self):
        self.sf.set_attraction(self.rel, 30)
        assert self.rel.attraction == 30
        assert self.rel.element.get("attraction") == "30"

    def test_set_compatibility(self):
        self.sf.set_compatibility(self.rel, 99)
        assert self.rel.compatibility == 99
        assert self.rel.element.get("compatibility") == "99"


# ---------------------------------------------------------------------------
# add_character / remove_character
# ---------------------------------------------------------------------------


class TestAddRemoveCharacter:
    def setup_method(self):
        self.sf = _make_save_file(MINIMAL_XML)
        self.ship = self.sf.ships[0]

    def test_add_character_increases_count(self):
        before = len(self.sf.characters)
        self.sf.add_character(self.ship, "New", "Crew")
        assert len(self.sf.characters) == before + 1

    def test_add_character_name(self):
        char = self.sf.add_character(self.ship, "Alan", "Shepard")
        assert char.first_name == "Alan"
        assert char.last_name == "Shepard"
        assert char.full_name == "Alan Shepard"

    def test_add_character_gets_unique_id(self):
        ids_before = {c.ent_id for c in self.sf.characters}
        char = self.sf.add_character(self.ship, "Unique", "")
        assert char.ent_id not in ids_before

    def test_add_character_has_cid_attribute(self):
        char = self.sf.add_character(self.ship, "Test", "Cid")
        assert char.element.get("cid") == "89"

    def test_add_character_has_default_schedule_masks(self):
        char = self.sf.add_character(self.ship, "Schedule", "Mask")
        sched = char.pers_element.find("schedule")
        assert sched is not None
        assert sched.get("p0") == "1188386"
        assert sched.get("p1") == "0"
        assert sched.get("p2") == "285212672"

    def test_add_character_has_default_sec_masks(self):
        char = self.sf.add_character(self.ship, "Section", "Mask")
        sec = char.pers_element.find("sec")
        assert sec is not None
        assert sec.get("s0") == "0"
        assert sec.get("s1") == "286331153"
        assert sec.get("s2") == "4369"

    def test_add_character_has_all_stats(self):
        char = self.sf.add_character(self.ship, "Stats", "Check")
        stat_tags = {s.tag for s in char.stats}
        assert stat_tags == set(STAT_TAGS)

    def test_add_character_stats_default_to_100(self):
        char = self.sf.add_character(self.ship, "Healthy", "")
        expected_defaults = {"Comfort": 0, "Oxygen": 0}
        for stat in char.stats:
            expected = expected_defaults.get(stat.tag, 100)
            assert stat.value == expected, (
                f"{stat.tag} expected {expected}, got {stat.value}"
            )

    def test_add_character_has_skills(self):
        char = self.sf.add_character(self.ship, "Skilled", "")
        assert len(char.skills) > 0

    def test_add_character_skill_elements_have_exp_attributes(self):
        char = self.sf.add_character(self.ship, "Exp", "Check")
        skills_el = char.pers_element.find("skills")
        for s_el in skills_el.findall("s"):
            assert s_el.get("exp") is not None, "skill element missing 'exp' attribute"
            assert (
                s_el.get("expd") is not None
            ), "skill element missing 'expd' attribute"

    def test_add_character_has_attributes(self):
        char = self.sf.add_character(self.ship, "Attr", "Check")
        assert len(char.attributes) > 0

    def test_add_character_in_xml(self):
        char = self.sf.add_character(self.ship, "Xml", "Check")
        chars_el = self.ship.element.find("characters")
        ent_ids = [el.get("entId") for el in chars_el.findall("c")]
        assert str(char.ent_id) in ent_ids

    def test_add_character_ship_sid_set(self):
        char = self.sf.add_character(self.ship, "Ship", "Ref")
        assert char.ship_sid == self.ship.sid

    def test_remove_character_decreases_count(self):
        char = self.sf.characters[0]
        before = len(self.sf.characters)
        self.sf.remove_character(char)
        assert len(self.sf.characters) == before - 1

    def test_remove_character_not_in_list(self):
        char = self.sf.characters[0]
        self.sf.remove_character(char)
        assert char not in self.sf.characters

    def test_remove_character_removes_xml_element(self):
        char = self.sf.characters[0]
        parent = char.element.getparent()
        self.sf.remove_character(char)
        assert char.element not in parent

    def test_remove_then_add_character(self):
        """Remove a character and add a fresh one; no duplicate IDs."""
        removed = self.sf.characters[0]
        self.sf.remove_character(removed)
        new_char = self.sf.add_character(self.ship, "Phoenix", "")
        assert new_char.ent_id != removed.ent_id
        assert new_char in self.sf.characters


# ---------------------------------------------------------------------------
# Storage edge cases
# ---------------------------------------------------------------------------


class TestStorageEdgeCases:
    """Covers scenarios not exercised by TestStorageMutations."""

    def _xml_with_zero_qty_item(self) -> bytes:
        """Same as MINIMAL_XML but the Water item has inStorage='0'."""
        return MINIMAL_XML.replace(
            'elementaryId="16" inStorage="50"',
            'elementaryId="16" inStorage="0"',
        ).encode()

    def test_zero_qty_item_not_in_memory_on_parse(self):
        sf = _make_save_file(self._xml_with_zero_qty_item())
        ship = sf.ships[0]
        containers = sf.get_storage_containers(ship)
        item_ids = {i.item_id for i in containers[0].items}
        assert 16 not in item_ids  # was zero, should be filtered

    def test_add_item_surfaces_zero_qty_xml_entry(self):
        """Adding to an item that exists in XML with qty=0 must surface it in memory."""
        sf = _make_save_file(self._xml_with_zero_qty_item())
        ship = sf.ships[0]
        container = sf.get_storage_containers(ship)[0]
        result = sf.add_storage_item(container, 16, 25)
        # The item must now appear in the in-memory list
        assert result is not None
        assert any(i.item_id == 16 for i in container.items)
        water = next(i for i in container.items if i.item_id == 16)
        assert water.quantity == 25  # 0 + 25

    def test_add_item_surfaces_zero_qty_xml_element(self):
        """The XML element for a previously-zero item must be updated."""
        sf = _make_save_file(self._xml_with_zero_qty_item())
        ship = sf.ships[0]
        container = sf.get_storage_containers(ship)[0]
        result = sf.add_storage_item(container, 16, 10)
        assert result is not None
        assert result.element.get("inStorage") == "10"

    def test_set_storage_quantity_to_zero(self):
        """set_storage_quantity(0) must update both in-memory and XML."""
        sf = _make_save_file(MINIMAL_XML)
        ship = sf.ships[0]
        container = sf.get_storage_containers(ship)[0]
        item = next(i for i in container.items if i.item_id == 16)
        sf.set_storage_quantity(item, 0)
        assert item.quantity == 0
        assert item.element.get("inStorage") == "0"

    def test_missing_setter_no_crash_set_credits(self):
        """set_credits silently does nothing when playerBank is absent."""
        sf = _make_save_file(b"<game mode='Normal' seed='0'/>")
        sf.set_credits(9999)  # must not raise
        assert sf.get_credits() == 0

    def test_missing_setter_no_crash_set_prestige(self):
        """set_prestige silently does nothing when questLines is absent."""
        sf = _make_save_file(b"<game mode='Normal' seed='0'/>")
        sf.set_prestige(100)  # must not raise
        assert sf.get_prestige() == 0

    def test_missing_setter_no_crash_set_sandbox(self):
        """set_sandbox silently does nothing when settings is absent."""
        sf = _make_save_file(b"<game mode='Normal' seed='0'/>")
        sf.set_sandbox(True)  # must not raise
        assert sf.get_sandbox() is False


# ---------------------------------------------------------------------------
# Metadata accessors: get_game_time_str / get_star_system_count / get_ship_tiles
# ---------------------------------------------------------------------------


class TestMetadataAccessors:
    def test_get_game_time_str_no_clock(self):
        sf = _make_save_file(MINIMAL_XML)  # MINIMAL_XML has no <clock>
        assert sf.get_game_time_str() == "—"

    def test_get_game_time_str_with_clock(self):
        xml = textwrap.dedent("""\
            <game mode="Normal" seed="0">
              <clock days="5" hours="14" minutes="30"/>
            </game>
        """)
        sf = _make_save_file(xml.encode())
        assert sf.get_game_time_str() == "Day 5, 14:30"

    def test_get_game_time_str_pads_single_digit_hours(self):
        xml = textwrap.dedent("""\
            <game mode="Normal" seed="0">
              <clock days="1" hours="3" minutes="5"/>
            </game>
        """)
        sf = _make_save_file(xml.encode())
        assert sf.get_game_time_str() == "Day 1, 03:05"

    def test_get_game_time_str_bad_values(self):
        xml = textwrap.dedent("""\
            <game mode="Normal" seed="0">
              <clock days="x" hours="y" minutes="z"/>
            </game>
        """)
        sf = _make_save_file(xml.encode())
        assert sf.get_game_time_str() == "—"

    def test_get_star_system_count_no_starmap(self):
        sf = _make_save_file(MINIMAL_XML)
        assert sf.get_star_system_count() == 0

    def test_get_star_system_count_with_systems(self):
        xml = textwrap.dedent("""\
            <game mode="Normal" seed="0">
              <starmap>
                <systems>
                  <sys id="1"/>
                  <sys id="2"/>
                  <sys id="3"/>
                </systems>
              </starmap>
            </game>
        """)
        sf = _make_save_file(xml.encode())
        assert sf.get_star_system_count() == 3

    def test_get_ship_tiles_filters_elements_without_m(self):
        xml = textwrap.dedent("""\
            <game mode="Normal" seed="0">
              <ships>
                <ship sid="1" sname="Test" sx="10" sy="10">
                  <e x="0" y="0" m="100"/>
                  <e x="1" y="1"/>
                  <e x="2" y="2" m="200"/>
                </ship>
              </ships>
            </game>
        """)
        sf = _make_save_file(xml.encode())
        tiles = sf.get_ship_tiles(sf.ships[0])
        assert len(tiles) == 2
        assert (0, 0, "100") in tiles
        assert (2, 2, "200") in tiles

    def test_get_ship_tiles_empty_ship(self):
        sf = _make_save_file(MINIMAL_XML)
        # The ship in MINIMAL_XML has no <e m=...> elements
        tiles = sf.get_ship_tiles(sf.ships[0])
        assert isinstance(tiles, list)

    def test_get_ship_tiles_no_element(self):
        from src.save_file import Ship

        ship = Ship(sid=1, name="Ghost", sx=10, sy=10)
        sf = _make_save_file(MINIMAL_XML)
        assert sf.get_ship_tiles(ship) == []


# ---------------------------------------------------------------------------
# clone_character
# ---------------------------------------------------------------------------


_MASTER_XML = textwrap.dedent("""\
    <game mode="Normal" seed="0">
      <masterData idCounter="200"/>
      <ships>
        <ship sid="1" sname="Alpha" sx="10" sy="10">
          <characters>
            <c entId="90" name="Source" lname="Crew" cid="1">
              <props>
                <Health v="80"/><Food v="90"/><Rest v="70"/>
                <Comfort v="60"/><Mood v="50"/><Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr><a points="3" id="210"/></attr>
                <skills><s sk="6" level="5" mxn="10" exp="0" expd="0"/></skills>
                <traits><t id="1046"/></traits>
                <conditions><c id="1109"/></conditions>
                <sociality><relationships/></sociality>
              </pers>
            </c>
          </characters>
        </ship>
      </ships>
    </game>
""")


class TestCloneCharacter:
    def setup_method(self):
        self.sf = _make_save_file(_MASTER_XML.encode())
        self.source = self.sf.characters[0]
        self.ship = self.sf.ships[0]

    def test_clone_increases_character_count(self):
        before = len(self.sf.characters)
        self.sf.clone_character(self.source, self.ship, "Clone", "A")
        assert len(self.sf.characters) == before + 1

    def test_clone_gets_new_unique_id(self):
        clone = self.sf.clone_character(self.source, self.ship, "Clone", "B")
        assert clone.ent_id != self.source.ent_id
        ids = [c.ent_id for c in self.sf.characters]
        assert len(ids) == len(set(ids))

    def test_clone_has_correct_name(self):
        clone = self.sf.clone_character(self.source, self.ship, "New", "Person")
        assert clone.first_name == "New"
        assert clone.last_name == "Person"

    def test_clone_inherits_stats(self):
        clone = self.sf.clone_character(self.source, self.ship, "Clone", "C")
        health = next(s for s in clone.stats if s.tag == "Health")
        assert health.value == 80

    def test_clone_inherits_skills(self):
        clone = self.sf.clone_character(self.source, self.ship, "Clone", "D")
        assert len(clone.skills) == 1
        assert clone.skills[0].skill_id == 6
        assert clone.skills[0].level == 5

    def test_clone_inherits_traits(self):
        clone = self.sf.clone_character(self.source, self.ship, "Clone", "E")
        assert len(clone.traits) == 1
        assert clone.traits[0].trait_id == 1046

    def test_clone_in_xml(self):
        clone = self.sf.clone_character(self.source, self.ship, "Clone", "F")
        chars_el = self.ship.element.find("characters")
        ent_ids = [el.get("entId") for el in chars_el.findall("c")]
        assert str(clone.ent_id) in ent_ids

    def test_clone_ship_sid_matches(self):
        clone = self.sf.clone_character(self.source, self.ship, "Clone", "G")
        assert clone.ship_sid == self.ship.sid


# ---------------------------------------------------------------------------
# Folder-level parsing
# ---------------------------------------------------------------------------


class TestFolderParsing:
    def _write_folder_save(self, tmp_path) -> "Path":
        """Write a minimal multi-file save folder and return its path."""
        from pathlib import Path

        folder = tmp_path / "save"
        folder.mkdir()
        (folder / "game").write_bytes(MINIMAL_XML.encode())
        (folder / "info").write_bytes(
            b'<info version="42" date="1000" realTimeDate="1748304000000"/>'
        )
        timeline = textwrap.dedent("""\
            <timeline>
              <e type="1" day="5"><p>Alice joined</p></e>
              <e type="8" day="10"><p>Research done</p></e>
            </timeline>
        """)
        (folder / "timeline.xml").write_bytes(timeline.encode())
        sector_dir = folder / "sector240"
        sector_dir.mkdir()
        (sector_dir / "space").write_bytes(
            b'<space sx="56" sy="84"><e/><e/><e/></space>'
        )
        ships_dir = folder / "ships"
        ships_dir.mkdir()
        (ships_dir / "ship999").write_bytes(
            b'<ship sid="999" sname="Stored Ship" sx="28" sy="28"/>'
        )
        return folder

    def test_load_from_folder_sets_folder_attribute(self, tmp_path):
        folder = self._write_folder_save(tmp_path)
        sf = SaveFile()
        sf.load(str(folder))
        assert sf.folder == folder

    def test_load_from_folder_parses_save_info(self, tmp_path):
        folder = self._write_folder_save(tmp_path)
        sf = SaveFile()
        sf.load(str(folder))
        assert sf.save_info is not None
        assert sf.save_info.version == 42
        assert sf.save_info.game_date == 1000

    def test_load_from_folder_parses_real_date(self, tmp_path):
        folder = self._write_folder_save(tmp_path)
        sf = SaveFile()
        sf.load(str(folder))
        result = sf.get_real_date_str()
        # Should be a formatted date string, not the dash fallback
        assert result != "-"
        assert "-" in result  # e.g. "2025-05-26  …"

    def test_load_from_folder_parses_sectors(self, tmp_path):
        folder = self._write_folder_save(tmp_path)
        sf = SaveFile()
        sf.load(str(folder))
        assert len(sf.sectors) == 1
        assert sf.sectors[0].sector_id == 240
        assert sf.sectors[0].entity_count == 3

    def test_load_from_folder_parses_timeline(self, tmp_path):
        folder = self._write_folder_save(tmp_path)
        sf = SaveFile()
        sf.load(str(folder))
        assert len(sf.timeline_events) == 2
        assert sf.timeline_events[0].day == 5
        assert sf.timeline_events[0].text == "Alice joined"

    def test_load_from_folder_loads_external_ships(self, tmp_path):
        folder = self._write_folder_save(tmp_path)
        sf = SaveFile()
        sf.load(str(folder))
        sids = {s.sid for s in sf.ships}
        assert 999 in sids
        external = next(s for s in sf.ships if s.sid == 999)
        assert external.in_game_file is False
        assert external.name == "Stored Ship"

    def test_load_outer_slot_folder(self, tmp_path):
        """Loading the outer slot directory (contains save/) must work."""
        slot = tmp_path / "slot0"
        slot.mkdir()
        self._write_folder_save(slot)  # writes to slot/save/
        sf = SaveFile()
        sf.load(str(slot))
        assert sf.folder == slot / "save"

    def test_info_file_missing_does_not_crash(self, tmp_path):
        folder = tmp_path / "save"
        folder.mkdir()
        (folder / "game").write_bytes(MINIMAL_XML.encode())
        sf = SaveFile()
        sf.load(str(folder))
        assert sf.save_info is None

    def test_malformed_sector_file_is_skipped(self, tmp_path):
        folder = tmp_path / "save"
        folder.mkdir()
        (folder / "game").write_bytes(MINIMAL_XML.encode())
        sec = folder / "sector999"
        sec.mkdir()
        (sec / "space").write_bytes(b"not xml <<<<<")
        sf = SaveFile()
        sf.load(str(folder))  # must not raise
        assert all(s.sector_id != 999 for s in sf.sectors)


# ---------------------------------------------------------------------------
# Storage module name / capacity resolution
# ---------------------------------------------------------------------------

# Ship with a named storage module (m=82 -> Small Storage, cap=50)
_NAMED_MODULE_XML = textwrap.dedent("""\
    <game mode="Normal" seed="42">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="1" sname="TEST" sx="28" sy="28">
          <characters/>
          <e m="43">
            <wm>
              <up m="82">
                <feat eatAllowed="1">
                  <inv>
                    <s elementaryId="157" inStorage="10" onTheWayIn="0" onTheWayOut="0"/>
                  </inv>
                </feat>
              </up>
            </wm>
          </e>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")

# Ship with a composite room (m=632 -> Large Storage room, linked index 3 -> m=789)
_COMPOSITE_ROOM_XML = textwrap.dedent("""\
    <game mode="Normal" seed="42">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="1" sname="TEST" sx="28" sy="28">
          <characters/>
          <e m="632">
            <l ind="3">
              <feat eatAllowed="1">
                <inv>
                  <s elementaryId="157" inStorage="5" onTheWayIn="0" onTheWayOut="0"/>
                </inv>
              </feat>
            </l>
          </e>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")

# Ship with an unknown module ID (no entry in STORAGE_MODULE_NAMES)
_UNKNOWN_MODULE_XML = textwrap.dedent("""\
    <game mode="Normal" seed="42">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="1" sname="TEST" sx="28" sy="28">
          <characters/>
          <e m="43">
            <wm>
              <up m="9999">
                <feat eatAllowed="1">
                  <inv>
                    <s elementaryId="157" inStorage="3" onTheWayIn="0" onTheWayOut="0"/>
                  </inv>
                </feat>
              </up>
            </wm>
          </e>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")

# Ship with the unlimited starter storage (m=912, capacity=0)
_UNLIMITED_MODULE_XML = textwrap.dedent("""\
    <game mode="Normal" seed="42">
      <playerBank ca="0" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="0"/>
      </questLines></questLines>
      <ships>
        <ship sid="1" sname="TEST" sx="28" sy="28">
          <characters/>
          <e m="43">
            <wm>
              <up m="912">
                <feat eatAllowed="1">
                  <inv>
                    <s elementaryId="157" inStorage="1" onTheWayIn="0" onTheWayOut="0"/>
                  </inv>
                </feat>
              </up>
            </wm>
          </e>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")


class TestStorageModuleResolution:
    """Tests for display_name and capacity derived from module type IDs."""

    def test_named_module_display_name(self):
        """A container whose parent element has m=82 gets display_name 'Small Storage'."""
        sf = _make_save_file(_NAMED_MODULE_XML)
        containers = sf.get_storage_containers(sf.ships[0])
        assert len(containers) == 1
        assert containers[0].display_name == "Small Storage"

    def test_named_module_capacity(self):
        """m=82 maps to capacity 50 from STORAGE_MODULE_CAPACITIES."""
        sf = _make_save_file(_NAMED_MODULE_XML)
        containers = sf.get_storage_containers(sf.ships[0])
        assert containers[0].capacity == 50

    def test_composite_room_display_name(self):
        """A feat inside <l ind=3> of <e m=632> resolves to 'Large Storage'."""
        sf = _make_save_file(_COMPOSITE_ROOM_XML)
        containers = sf.get_storage_containers(sf.ships[0])
        assert len(containers) == 1
        assert containers[0].display_name == "Large Storage"

    def test_composite_room_capacity(self):
        """Composite room m=632, linked index 3 -> inner module m=789 -> capacity 250."""
        sf = _make_save_file(_COMPOSITE_ROOM_XML)
        containers = sf.get_storage_containers(sf.ships[0])
        assert containers[0].capacity == 250

    def test_unknown_module_fallback_display_name(self):
        """An unrecognised module ID falls back to 'Storage Bay'."""
        sf = _make_save_file(_UNKNOWN_MODULE_XML)
        containers = sf.get_storage_containers(sf.ships[0])
        assert containers[0].display_name == "Storage Bay"

    def test_unknown_module_fallback_capacity(self):
        """An unrecognised module ID has capacity 0 (unknown / unlimited)."""
        sf = _make_save_file(_UNKNOWN_MODULE_XML)
        containers = sf.get_storage_containers(sf.ships[0])
        assert containers[0].capacity == 0

    def test_unlimited_module_capacity_is_zero(self):
        """m=912 (Starter Storage) has capacity 0, meaning unlimited."""
        sf = _make_save_file(_UNLIMITED_MODULE_XML)
        containers = sf.get_storage_containers(sf.ships[0])
        assert containers[0].capacity == 0
        assert containers[0].display_name == "Starter Storage"

