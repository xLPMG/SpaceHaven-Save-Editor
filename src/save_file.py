"""
save_file.py – Parses and writes Space Haven 'game' save files.

The save file is XML.  We use lxml so the output stays close to the original
(attribute order preserved, no unwanted namespace declarations injected).
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from lxml import etree

from src.game_data import (
    ATTRIBUTE_IDS,
    CONDITION_IDS,
    SKILL_IDS,
    STORAGE_IDS,
    TECH_IDS,
    TRAIT_IDS,
)


# ---------------------------------------------------------------------------
# Data-model classes (plain Python – no Qt dependency)
# ---------------------------------------------------------------------------

@dataclass
class Stat:
    tag: str       # XML element name, e.g. "Health"
    value: int     # current value (attribute "v")
    element: object = field(repr=False, default=None)  # lxml element


@dataclass
class Attribute:
    attr_id: int
    name: str
    points: int
    element: object = field(repr=False, default=None)


@dataclass
class Skill:
    skill_id: int
    name: str
    level: int
    max_level: int
    element: object = field(repr=False, default=None)


@dataclass
class Trait:
    trait_id: int
    name: str
    element: object = field(repr=False, default=None)


@dataclass
class Condition:
    cond_id: int
    name: str
    element: object = field(repr=False, default=None)


@dataclass
class Relationship:
    target_id: int
    target_name: str
    friendship: int
    attraction: int
    compatibility: int


@dataclass
class Character:
    ent_id: int
    first_name: str
    last_name: str
    ship_sid: int
    stats: list[Stat] = field(default_factory=list)
    attributes: list[Attribute] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    traits: list[Trait] = field(default_factory=list)
    conditions: list[Condition] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    element: object = field(repr=False, default=None)   # <c> element
    pers_element: object = field(repr=False, default=None)  # <pers> element

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class StorageItem:
    item_id: int
    name: str
    quantity: int
    element: object = field(repr=False, default=None)  # <s> element


@dataclass
class StorageContainer:
    display_name: str
    items: list[StorageItem] = field(default_factory=list)
    feat_element: object = field(repr=False, default=None)  # <feat> element
    inv_element: object = field(repr=False, default=None)   # <inv> element


@dataclass
class Ship:
    sid: int
    name: str
    sx: int
    sy: int
    element: object = field(repr=False, default=None)  # <ship> element


@dataclass
class ResearchEntry:
    tech_id: int
    name: str
    done: bool          # True if all stages completed
    in_progress: bool   # True if any stage has partial progress
    element: object = field(repr=False, default=None)  # <l techId=...> element


# ---------------------------------------------------------------------------
# Main save-file class
# ---------------------------------------------------------------------------

class SaveFile:
    """Loads, exposes, and saves a Space Haven XML save file."""

    STAT_TAGS = ("Health", "Food", "Rest", "Comfort", "Mood", "Oxygen", "Temperature")

    def __init__(self) -> None:
        self._tree: Optional[etree._ElementTree] = None
        self._root: Optional[etree._Element] = None
        self.path: Optional[Path] = None
        self.ships: list[Ship] = []
        self.characters: list[Character] = []
        self.research: list[ResearchEntry] = []

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------

    def load(self, path: str | Path) -> None:
        self.path = Path(path)
        parser = etree.XMLParser(remove_blank_text=False, recover=True)
        self._tree = etree.parse(str(self.path), parser)
        self._root = self._tree.getroot()

        if self._root is None or self._root.tag != "game":
            raise ValueError("Not a valid Space Haven save file (root element must be <game>).")

        self._parse_ships()
        self._parse_characters()
        self._parse_research()

    def save(self, path: str | Path | None = None) -> None:
        dest = Path(path) if path else self.path
        if dest is None:
            raise ValueError("No save path specified.")
        self._tree.write(
            str(dest),
            pretty_print=True,
            xml_declaration=False,
            encoding="unicode",
        )

    def backup(self) -> Path:
        """Create a timestamped backup next to the save file."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.path.parent / f"game.backup.{ts}"
        shutil.copy2(str(self.path), str(backup_path))
        return backup_path

    # ------------------------------------------------------------------
    # Global settings
    # ------------------------------------------------------------------

    def get_game_mode(self) -> str:
        return self._root.get("mode", "Normal")

    def get_seed(self) -> str:
        return self._root.get("seed", "0")

    def get_credits(self) -> int:
        el = self._root.find("playerBank")
        if el is not None:
            try:
                return int(float(el.get("ca", "0")))
            except ValueError:
                return 0
        return 0

    def set_credits(self, value: int) -> None:
        el = self._root.find("playerBank")
        if el is not None:
            el.set("ca", str(value))

    def get_sandbox(self) -> bool:
        settings = self._root.find("settings")
        if settings is not None:
            diff = settings.find("diff")
            if diff is not None:
                return diff.get("sandbox", "false").lower() == "true"
        return False

    def set_sandbox(self, enabled: bool) -> None:
        settings = self._root.find("settings")
        if settings is not None:
            diff = settings.find("diff")
            if diff is not None:
                diff.set("sandbox", "true" if enabled else "false")

    def get_prestige(self) -> int:
        ql1 = self._root.find("questLines")
        if ql1 is None:
            return 0
        ql2 = ql1.find("questLines")
        if ql2 is None:
            return 0
        for el in ql2.findall("l"):
            if el.get("type") == "ExodusFleet":
                try:
                    return int(el.get("playerPrestigePoints", "0"))
                except ValueError:
                    return 0
        return 0

    def set_prestige(self, value: int) -> None:
        ql1 = self._root.find("questLines")
        if ql1 is None:
            return
        ql2 = ql1.find("questLines")
        if ql2 is None:
            return
        for el in ql2.findall("l"):
            if el.get("type") == "ExodusFleet":
                el.set("playerPrestigePoints", str(value))
                return

    # ------------------------------------------------------------------
    # Ships
    # ------------------------------------------------------------------

    def _parse_ships(self) -> None:
        self.ships.clear()
        seen: set[int] = set()
        # Player ships live in <game><ships><ship ...>
        ships_el = self._root.find("ships")
        if ships_el is None:
            return
        for ship_el in ships_el.findall("ship"):
            sid_str = ship_el.get("sid", "0")
            try:
                sid = int(sid_str)
            except ValueError:
                continue
            if sid == 0 or sid in seen:
                continue
            seen.add(sid)
            self.ships.append(Ship(
                sid=sid,
                name=ship_el.get("sname") or f"Ship #{sid}",
                sx=int(ship_el.get("sx", 0)),
                sy=int(ship_el.get("sy", 0)),
                element=ship_el,
            ))
        self.ships.sort(key=lambda s: s.name)

    def get_storage_containers(self, ship: Ship) -> list[StorageContainer]:
        """Return all storage containers (feat elements with eatAllowed + inv) for a ship."""
        containers: list[StorageContainer] = []
        idx = 0
        for feat in ship.element.iter("feat"):
            if feat.get("eatAllowed") is None:
                continue
            inv = feat.find(".//inv")
            if inv is None:
                continue
            items: list[StorageItem] = []
            for s_el in inv.findall("s"):
                try:
                    item_id = int(s_el.get("elementaryId", "0"))
                    qty = int(s_el.get("inStorage", "0"))
                except ValueError:
                    continue
                if qty <= 0:
                    continue
                items.append(StorageItem(
                    item_id=item_id,
                    name=STORAGE_IDS.get(item_id, f"Unknown ({item_id})"),
                    quantity=qty,
                    element=s_el,
                ))
            if not items:
                idx += 1
                continue
            # Generate a display name from ancestor <e> entId / objId
            parent_e = feat.getparent()
            while parent_e is not None and parent_e.tag != "e":
                parent_e = parent_e.getparent()
            ent_id = parent_e.get("entId") if parent_e is not None else None
            obj_id = parent_e.get("objId") if parent_e is not None else None
            if ent_id and ent_id != "0":
                display = f"Container (ID: {ent_id})"
            elif obj_id:
                display = f"Storage (Type: {obj_id}) #{idx + 1}"
            else:
                display = f"Storage Bay #{idx + 1}"
            containers.append(StorageContainer(
                display_name=display,
                items=sorted(items, key=lambda i: i.name),
                feat_element=feat,
                inv_element=inv,
            ))
            idx += 1
        return containers

    def add_storage_item(self, container: StorageContainer, item_id: int, quantity: int) -> None:
        inv = container.inv_element
        # Check if item already exists
        for s_el in inv.findall("s"):
            if s_el.get("elementaryId") == str(item_id):
                existing = int(s_el.get("inStorage", "0"))
                s_el.set("inStorage", str(existing + quantity))
                # Update in-memory list
                for item in container.items:
                    if item.item_id == item_id:
                        item.quantity = existing + quantity
                        return
                return
        # New item
        new_el = etree.SubElement(inv, "s")
        new_el.set("elementaryId", str(item_id))
        new_el.set("inStorage", str(quantity))
        new_el.set("onTheWayIn", "0")
        new_el.set("onTheWayOut", "0")
        container.items.append(StorageItem(
            item_id=item_id,
            name=STORAGE_IDS.get(item_id, f"Unknown ({item_id})"),
            quantity=quantity,
            element=new_el,
        ))
        container.items.sort(key=lambda i: i.name)

    def remove_storage_item(self, container: StorageContainer, item: StorageItem) -> None:
        if item.element is not None:
            parent = item.element.getparent()
            if parent is not None:
                parent.remove(item.element)
        container.items.remove(item)

    def set_storage_quantity(self, item: StorageItem, quantity: int) -> None:
        item.quantity = quantity
        if item.element is not None:
            item.element.set("inStorage", str(quantity))

    # ------------------------------------------------------------------
    # Characters
    # ------------------------------------------------------------------

    def _parse_characters(self) -> None:
        self.characters.clear()
        seen_ids: set[int] = set()
        for ship in self.ships:
            chars_el = ship.element.find("characters")
            if chars_el is None:
                continue
            for c_el in chars_el.findall("c"):
                try:
                    ent_id = int(c_el.get("entId", "0"))
                except ValueError:
                    continue
                if ent_id == 0 or ent_id in seen_ids:
                    continue
                seen_ids.add(ent_id)
                char = Character(
                    ent_id=ent_id,
                    first_name=c_el.get("name", "Unknown"),
                    last_name=c_el.get("lname", ""),
                    ship_sid=ship.sid,
                    element=c_el,
                )
                pers = c_el.find("pers")
                char.pers_element = pers
                self._parse_char_stats(c_el, char)
                if pers is not None:
                    self._parse_char_attributes(pers, char)
                    self._parse_char_skills(pers, char)
                    self._parse_char_traits(pers, char)
                    self._parse_char_conditions(pers, char)
                    self._parse_char_relationships(pers, char)
                self.characters.append(char)

        # Second pass: resolve relationship target names
        id_to_name = {c.ent_id: c.full_name for c in self.characters}
        for char in self.characters:
            for rel in char.relationships:
                if rel.target_name.startswith("Unknown"):
                    rel.target_name = id_to_name.get(rel.target_id, rel.target_name)

    def _parse_char_stats(self, c_el: etree._Element, char: Character) -> None:
        props = c_el.find("props")
        if props is None:
            return
        for tag in self.STAT_TAGS:
            el = props.find(tag)
            if el is not None:
                try:
                    v = int(float(el.get("v", "0")))
                except ValueError:
                    v = 0
                char.stats.append(Stat(tag=tag, value=v, element=el))

    def _parse_char_attributes(self, pers: etree._Element, char: Character) -> None:
        attr_el = pers.find("attr")
        if attr_el is None:
            return
        for a in attr_el.findall("a"):
            try:
                attr_id = int(a.get("id", "0"))
                points = int(a.get("points", "0"))
            except ValueError:
                continue
            char.attributes.append(Attribute(
                attr_id=attr_id,
                name=ATTRIBUTE_IDS.get(attr_id, f"Unknown ({attr_id})"),
                points=points,
                element=a,
            ))

    def _parse_char_skills(self, pers: etree._Element, char: Character) -> None:
        skills_el = pers.find("skills")
        if skills_el is None:
            return
        for s in skills_el.findall("s"):
            try:
                skill_id = int(s.get("sk", "0"))
                level = int(s.get("level", "0"))
                max_level = int(s.get("mxn", "0"))
            except ValueError:
                continue
            char.skills.append(Skill(
                skill_id=skill_id,
                name=SKILL_IDS.get(skill_id, f"Unknown ({skill_id})"),
                level=level,
                max_level=max_level,
                element=s,
            ))
        char.skills.sort(key=lambda s: s.name)

    def _parse_char_traits(self, pers: etree._Element, char: Character) -> None:
        traits_el = pers.find("traits")
        if traits_el is None:
            return
        for t in traits_el.findall("t"):
            try:
                trait_id = int(t.get("id", "0"))
            except ValueError:
                continue
            char.traits.append(Trait(
                trait_id=trait_id,
                name=TRAIT_IDS.get(trait_id, f"Unknown ({trait_id})"),
                element=t,
            ))

    def _parse_char_conditions(self, pers: etree._Element, char: Character) -> None:
        conds_el = pers.find("conditions")
        if conds_el is None:
            return
        for c in conds_el.findall("c"):
            try:
                cond_id = int(c.get("id", "0"))
            except ValueError:
                continue
            char.conditions.append(Condition(
                cond_id=cond_id,
                name=CONDITION_IDS.get(cond_id, f"Unknown ({cond_id})"),
                element=c,
            ))

    def _parse_char_relationships(self, pers: etree._Element, char: Character) -> None:
        sociality = pers.find("sociality")
        if sociality is None:
            return
        rels_el = sociality.find("relationships")
        if rels_el is None:
            return
        for l_el in rels_el.findall("l"):
            try:
                target_id = int(l_el.get("targetId", "0"))
                friendship = int(l_el.get("friendship", "0"))
                attraction = int(l_el.get("attraction", "0"))
                compatibility = int(l_el.get("compatibility", "0"))
            except ValueError:
                continue
            if target_id == 0:
                continue
            char.relationships.append(Relationship(
                target_id=target_id,
                target_name=f"Unknown ({target_id})",
                friendship=friendship,
                attraction=attraction,
                compatibility=compatibility,
            ))

    # ------------------------------------------------------------------
    # Character mutations
    # ------------------------------------------------------------------

    def set_stat(self, stat: Stat, value: int) -> None:
        stat.value = value
        if stat.element is not None:
            stat.element.set("v", str(value))

    def set_attribute(self, attr: Attribute, points: int) -> None:
        attr.points = points
        if attr.element is not None:
            attr.element.set("points", str(points))

    def set_skill_level(self, skill: Skill, level: int) -> None:
        skill.level = level
        if skill.element is not None:
            skill.element.set("level", str(level))

    def set_skill_max(self, skill: Skill, max_level: int) -> None:
        skill.max_level = max_level
        if skill.element is not None:
            skill.element.set("mxn", str(max_level))

    def add_trait(self, char: Character, trait_id: int) -> Trait | None:
        # Prevent duplicates
        if any(t.trait_id == trait_id for t in char.traits):
            return None
        pers = char.pers_element
        if pers is None:
            return None
        traits_el = pers.find("traits")
        if traits_el is None:
            traits_el = etree.SubElement(pers, "traits")
        t_el = etree.SubElement(traits_el, "t")
        t_el.set("id", str(trait_id))
        trait = Trait(
            trait_id=trait_id,
            name=TRAIT_IDS.get(trait_id, f"Unknown ({trait_id})"),
            element=t_el,
        )
        char.traits.append(trait)
        return trait

    def remove_trait(self, char: Character, trait: Trait) -> None:
        if trait.element is not None:
            parent = trait.element.getparent()
            if parent is not None:
                parent.remove(trait.element)
        if trait in char.traits:
            char.traits.remove(trait)

    def rename_character(self, char: Character, first: str, last: str) -> None:
        char.first_name = first
        char.last_name = last
        if char.element is not None:
            char.element.set("name", first)
            char.element.set("lname", last)

    def remove_condition(self, char: Character, cond: Condition) -> None:
        if cond.element is not None:
            parent = cond.element.getparent()
            if parent is not None:
                parent.remove(cond.element)
        if cond in char.conditions:
            char.conditions.remove(cond)

    def clear_conditions(self, char: Character) -> None:
        if char.pers_element is not None:
            conds_el = char.pers_element.find("conditions")
            if conds_el is not None:
                for c in list(conds_el.findall("c")):
                    conds_el.remove(c)
        char.conditions.clear()

    # ------------------------------------------------------------------
    # Batch operations
    # ------------------------------------------------------------------

    def heal_all_crew(self) -> int:
        """Set all crew stats to 100. Returns number of crew affected."""
        count = 0
        for char in self.characters:
            for stat in char.stats:
                self.set_stat(stat, 100)
            if char.stats:
                count += 1
        return count

    def max_all_skills(self) -> int:
        """Set all crew skills to level 20 / max 20. Returns number of skills changed."""
        count = 0
        for char in self.characters:
            for skill in char.skills:
                self.set_skill_level(skill, 20)
                self.set_skill_max(skill, 20)
                count += 1
        return count

    def clear_all_conditions(self) -> int:
        """Remove all conditions from all crew. Returns number of crew affected."""
        count = 0
        for char in self.characters:
            if char.conditions:
                self.clear_conditions(char)
                count += 1
        return count

    def fill_all_storage(self, quantity: int) -> int:
        """Set every existing storage item across all ships to `quantity`.
        Returns number of items updated."""
        count = 0
        for ship in self.ships:
            for container in self.get_storage_containers(ship):
                for item in container.items:
                    self.set_storage_quantity(item, quantity)
                    count += 1
        return count

    def rename_ship(self, ship: Ship, name: str) -> None:
        ship.name = name
        if ship.element is not None:
            ship.element.set("sname", name)

    # ------------------------------------------------------------------
    # Research
    # ------------------------------------------------------------------

    def _parse_research(self) -> None:
        self.research.clear()
        research_el = self._root.find(".//research")
        if research_el is None:
            return
        states_el = research_el.find("states")
        if states_el is None:
            return
        for l_el in states_el.findall("l"):
            try:
                tech_id = int(l_el.get("techId", "0"))
            except ValueError:
                continue
            if tech_id == 0:
                continue
            stage_states = l_el.find("stageStates")
            stages = stage_states.findall("l") if stage_states is not None else []
            done = bool(stages) and all(s.get("done", "false") == "true" for s in stages)
            in_progress = (not done) and any(
                any(int(bd.get(attr, "0")) > 0
                    for attr in ("level1", "level2", "level3")
                    for bd in [s.find("blocksDone")] if bd is not None)
                for s in stages
            )
            self.research.append(ResearchEntry(
                tech_id=tech_id,
                name=TECH_IDS.get(tech_id, f"Unknown ({tech_id})"),
                done=done,
                in_progress=in_progress,
                element=l_el,
            ))
        self.research.sort(key=lambda r: r.name)

    def complete_research(self, entry: ResearchEntry) -> None:
        """Mark a single research entry as fully completed."""
        if entry.element is None:
            return
        stage_states = entry.element.find("stageStates")
        if stage_states is None:
            return
        for stage_el in stage_states.findall("l"):
            stage_el.set("done", "true")
            bd = stage_el.find("blocksDone")
            if bd is None:
                bd = etree.SubElement(stage_el, "blocksDone")
            # Set high values so the game treats it as complete
            bd.set("level1", "9999")
            bd.set("level2", "9999")
            bd.set("level3", "9999")
        entry.done = True
        entry.in_progress = False

    def complete_all_research(self) -> int:
        """Complete every research entry. Returns number completed."""
        count = 0
        for entry in self.research:
            if not entry.done:
                self.complete_research(entry)
                count += 1
        return count

