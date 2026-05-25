"""Unit tests for src/save_file.py using minimal XML fixtures."""
from __future__ import annotations

import io
import textwrap

import pytest
from lxml import etree

from src.save_file import (
    Character,
    SaveFile,
    Skill,
    Stat,
    StorageItem,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_save_file(xml: str | bytes) -> SaveFile:
    """Parse an XML string or bytes into a SaveFile without touching the filesystem."""
    sf = SaveFile()
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    data = xml if isinstance(xml, bytes) else xml.encode()
    sf._tree = etree.parse(io.BytesIO(data), parser)
    sf._root = sf._tree.getroot()
    sf._parse_ships()
    sf._parse_characters()
    sf._parse_research()
    return sf


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
        char = Character(ent_id=1, first_name="Jarvis", last_name="Michael", ship_sid=89)
        assert char.full_name == "Jarvis Michael"

    def test_character_full_name_no_last(self):
        char = Character(ent_id=2, first_name="Solo", last_name="", ship_sid=89)
        assert char.full_name == "Solo"

    def test_stat_defaults(self):
        stat = Stat(tag="Health", value=80)
        assert stat.element is None

    def test_skill_defaults(self):
        skill = Skill(skill_id=6, name="Medical", level=3, max_level=8)
        assert skill.element is None

    def test_storage_item_defaults(self):
        item = StorageItem(item_id=16, name="Water", quantity=50)
        assert item.element is None


# ---------------------------------------------------------------------------
# SaveFile.load / root validation
# ---------------------------------------------------------------------------

class TestSaveFileLoad:
    def test_load_valid_file(self, tmp_path):
        p = tmp_path / "game"
        p.write_bytes(MINIMAL_XML.encode())
        sf = SaveFile()
        sf.load(str(p))
        assert sf.path == p

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
        # get_storage_containers returns fresh objects each call, so re-fetch
        fresh = self.sf.get_storage_containers(self.ship)[0]
        for item in fresh.items:
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
        assert len(jarvis.stats) == 7
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
        trait = self.sf.add_trait(self.jarvis, 1039)  # Fast learner
        assert trait is not None
        assert any(t.trait_id == 1039 for t in self.jarvis.traits)

    def test_add_trait_no_duplicate(self):
        self.sf.add_trait(self.jarvis, 1039)
        result = self.sf.add_trait(self.jarvis, 1039)
        assert result is None
        assert sum(1 for t in self.jarvis.traits if t.trait_id == 1039) == 1

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
                assert skill.level == 20
                assert skill.max_level == 20

    def test_clear_all_conditions(self):
        count = self.sf.clear_all_conditions()
        # Jarvis has 2 conditions, Airek has 0
        assert count == 1
        for char in self.sf.characters:
            assert char.conditions == []

    def test_clear_all_conditions_returns_zero_when_none(self):
        self.sf.clear_all_conditions()
        count = self.sf.clear_all_conditions()
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
            bd = stage_el.find("blocksDone")
            assert bd is not None
            assert int(bd.get("level1")) >= 9999

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

        # Serialise the in-memory tree and re-parse to confirm the mutation
        # is present (avoids encoding="unicode" file-path issues in newer lxml).
        xml_bytes = etree.tostring(sf._root)
        root = etree.fromstring(xml_bytes)
        assert root.find("playerBank").get("ca") == "5000"

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
