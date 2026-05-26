"""Parses and writes Space Haven save files (XML via lxml).

Supports loading either a single ``game`` file or a complete save *folder*
(which also contains a ``ships/`` sub-folder, ``sector*/space`` files,
an ``info`` metadata file, and ``timeline.xml``).
"""

from __future__ import annotations

import copy
import random
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from lxml import etree

from src.game_data import (
    ATTRIBUTE_IDS,
    CONDITION_IDS,
    SKILL_IDS,
    STAT_TAGS,
    STORAGE_IDS,
    TECH_IDS,
    TIMELINE_EVENT_NAMES,
    TRAIT_IDS,
)

# ---------------------------------------------------------------------------
# Data-model classes
# ---------------------------------------------------------------------------


@dataclass
class Stat:
    tag: str  # XML element name, e.g. "Health"
    value: int  # current value (attribute "v")
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
    element: object = field(repr=False, default=None)


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
    element: object = field(repr=False, default=None)  # <c> element
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
    inv_element: object = field(repr=False, default=None)  # <inv> element


@dataclass
class Sector:
    folder_name: str   # e.g. "sector240"
    sector_id: int
    sx: int
    sy: int
    entity_count: int
    path: object = field(repr=False, default=None)  # Path to the space file


@dataclass
class TimelineEvent:
    event_type: int
    type_name: str
    day: int
    text: str


@dataclass
class SaveInfo:
    version: int
    game_date: int          # in-game date (ticks)
    real_time_ms: int       # Unix epoch ms


@dataclass
class Ship:
    sid: int
    name: str
    sx: int  # grid size X in units (1 square = 28 units)
    sy: int  # grid size Y in units
    ox: int = 0  # sector offset X
    oy: int = 0  # sector offset Y
    in_game_file: bool = True   # False -> lives in ships/ folder
    external_path: Optional[Path] = field(repr=False, default=None)
    external_tree: object = field(repr=False, default=None)  # lxml tree if external
    element: object = field(repr=False, default=None)  # <ship> element


@dataclass
class ResearchEntry:
    tech_id: int
    name: str
    done: bool  # True if all stages completed
    in_progress: bool  # True if any stage has partial progress
    element: object = field(repr=False, default=None)  # <l techId=...> element


# ---------------------------------------------------------------------------
# Main save-file class
# ---------------------------------------------------------------------------


class SaveFile:
    """Loads, exposes, and saves a Space Haven save file or save folder."""

    def __init__(self) -> None:
        self._tree: etree._ElementTree | None = None
        self._root: etree._Element | None = None
        self.path: Path | None = None          # path to the ``game`` file
        self.folder: Path | None = None        # save folder (None if single-file load)
        self.ships: list[Ship] = []
        self.characters: list[Character] = []
        self.research: list[ResearchEntry] = []
        self.sectors: list[Sector] = []
        self.timeline_events: list[TimelineEvent] = []
        self.save_info: SaveInfo | None = None
        self._containers_cache: dict[int, list[StorageContainer]] = {}

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------

    def load(self, path: str | Path) -> None:
        """Load from a ``game`` file, the ``save/`` folder, or the outer slot folder.

        Accepted inputs:
        - The ``game`` file directly
        - The ``save/`` folder (contains ``game``, ``ships/``, ``sector*/``)
        - The outer slot folder (contains a ``save/`` subfolder with ``game`` inside)
        """
        p = Path(path)
        if p.is_dir():
            # Check if it's the outer slot folder (contains save/game)
            candidate = p / "save"
            if candidate.is_dir() and (candidate / "game").exists():
                self._load_from_folder(candidate)
            else:
                self._load_from_folder(p)
        else:
            self._load_game_file(p)

    def _load_game_file(self, game_path: Path) -> None:
        """Parse a single ``game`` file (minimal / backward-compat mode)."""
        self.path = game_path
        self.folder = None
        parser = etree.XMLParser(remove_blank_text=False, recover=True)
        self._tree = etree.parse(str(game_path), parser)
        self._root = self._tree.getroot()

        if self._root is None or self._root.tag != "game":
            raise ValueError(
                "Not a valid Space Haven save file (root element must be <game>)."
            )

        self._containers_cache.clear()
        self.sectors.clear()
        self.timeline_events.clear()
        self.save_info = None
        self._parse_ships()
        self._parse_characters()
        self._parse_research()

    def _load_from_folder(self, folder: Path) -> None:
        """Parse an entire save folder."""
        game_path = folder / "game"
        if not game_path.exists():
            raise ValueError(
                f"No 'game' file found in folder: {folder}"
            )

        self._load_game_file(game_path)
        self.folder = folder  # restore after _load_game_file resets it

        # Parse supplementary files (errors are silently ignored so a
        # partially-written save still opens as much as possible).
        self._parse_info_file()
        self._parse_external_ships()
        self._parse_sectors()
        self._parse_timeline()

        # Re-parse characters now that external ships are loaded
        self._parse_characters()

    # ------------------------------------------------------------------
    # Supplementary parsers (folder-only)
    # ------------------------------------------------------------------

    def _parse_info_file(self) -> None:
        info_path = self.folder / "info"
        if not info_path.exists():
            return
        try:
            parser = etree.XMLParser(recover=True)
            root = etree.parse(str(info_path), parser).getroot()
            self.save_info = SaveInfo(
                version=int(root.get("version", "0")),
                game_date=int(root.get("date", "0")),
                real_time_ms=int(root.get("realTimeDate", "0")),
            )
        except Exception:
            pass

    def _parse_external_ships(self) -> None:
        """Load ship files from the ``ships/`` sub-folder."""
        ships_dir = self.folder / "ships"
        if not ships_dir.is_dir():
            return
        parser = etree.XMLParser(remove_blank_text=False, recover=True)
        existing_sids = {s.sid for s in self.ships}
        for ship_file in sorted(ships_dir.iterdir()):
            if ship_file.is_dir() or ship_file.name.startswith("."):
                continue
            try:
                tree = etree.parse(str(ship_file), parser)
                ship_el = tree.getroot()
                if ship_el is None or ship_el.tag != "ship":
                    continue
                sid = int(ship_el.get("sid", "0"))
                if sid == 0 or sid in existing_sids:
                    continue
                existing_sids.add(sid)
                self.ships.append(
                    Ship(
                        sid=sid,
                        name=ship_el.get("sname") or f"Ship #{sid}",
                        sx=int(ship_el.get("sx", 0)),
                        sy=int(ship_el.get("sy", 0)),
                        ox=int(ship_el.get("ox", 0)),
                        oy=int(ship_el.get("oy", 0)),
                        in_game_file=False,
                        external_path=ship_file,
                        external_tree=tree,
                        element=ship_el,
                    )
                )
            except Exception:
                continue
        self.ships.sort(key=lambda s: s.name)

    def _parse_sectors(self) -> None:
        """Parse all sector*/space files inside the save folder."""
        self.sectors.clear()
        for item in sorted(self.folder.iterdir()):
            if not item.is_dir() or not item.name.startswith("sector"):
                continue
            space_file = item / "space"
            if not space_file.exists():
                continue
            try:
                parser = etree.XMLParser(recover=True)
                root = etree.parse(str(space_file), parser).getroot()
                sector_id_str = item.name.replace("sector", "")
                sector_id = int(sector_id_str) if sector_id_str.isdigit() else 0
                entity_count = sum(1 for el in root if el.tag == "e")
                self.sectors.append(
                    Sector(
                        folder_name=item.name,
                        sector_id=sector_id,
                        sx=int(root.get("sx", 0)),
                        sy=int(root.get("sy", 0)),
                        entity_count=entity_count,
                        path=space_file,
                    )
                )
            except Exception:
                continue
        self.sectors.sort(key=lambda s: s.sector_id)

    def _parse_timeline(self) -> None:
        """Parse timeline.xml for the game event log."""
        self.timeline_events.clear()
        timeline_path = self.folder / "timeline.xml"
        if not timeline_path.exists():
            return
        try:
            parser = etree.XMLParser(recover=True)
            root = etree.parse(str(timeline_path), parser).getroot()
            for e in root.findall("e"):
                try:
                    event_type = int(e.get("type", "0"))
                    day = int(e.get("day", "0"))
                    p_el = e.find("p")
                    text = (p_el.text or "").strip() if p_el is not None else ""
                    self.timeline_events.append(
                        TimelineEvent(
                            event_type=event_type,
                            type_name=TIMELINE_EVENT_NAMES.get(event_type, f"Event #{event_type}"),
                            day=day,
                            text=text,
                        )
                    )
                except Exception:
                    continue
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Convenience accessors for folder-wide metadata
    # ------------------------------------------------------------------

    def get_game_time_str(self) -> str:
        """Return formatted in-game time from the ``<clock>`` element."""
        if self._root is None:
            return "—"
        clock = self._root.find("clock")
        if clock is None:
            return "—"
        try:
            days = int(clock.get("days", "0"))
            hours = int(clock.get("hours", "0"))
            minutes = int(clock.get("minutes", "0"))
            return f"Day {days}, {hours:02d}:{minutes:02d}"
        except ValueError:
            return "—"

    def get_real_date_str(self) -> str:
        """Return the real-world save date from the ``info`` file."""
        if self.save_info is None or self.save_info.real_time_ms == 0:
            return "—"
        try:
            dt = datetime.fromtimestamp(
                self.save_info.real_time_ms / 1000, tz=timezone.utc
            ).astimezone()
            return dt.strftime("%Y-%m-%d  %H:%M")
        except Exception:
            return "—"

    def get_star_system_count(self) -> int:
        """Return total star systems from the starmap."""
        if self._root is None:
            return 0
        starmap = self._root.find("starmap")
        if starmap is None:
            return 0
        systems = starmap.find("systems")
        return len(systems) if systems is not None else 0

    def save(self, path: str | Path | None = None) -> None:
        # Write the main game file
        dest = Path(path) if path else self.path
        if dest is None:
            raise ValueError("No save path specified.")
        self._write_tree(self._tree, dest)

        # Write external ship files (only when doing an in-place save, not Save As)
        if path is None:
            for ship in self.ships:
                if not ship.in_game_file and ship.external_tree is not None and ship.external_path is not None:
                    self._write_tree(ship.external_tree, ship.external_path)

    @staticmethod
    def _write_tree(tree: etree._ElementTree, dest: Path) -> None:
        """Write *tree* to *dest* atomically."""
        dest_dir = dest.parent
        fd, tmp_path = tempfile.mkstemp(dir=dest_dir, prefix=".tmp_save_")
        try:
            with open(fd, "wb") as fh:
                tree.write(
                    fh,
                    pretty_print=True,
                    xml_declaration=False,
                    encoding="utf-8",
                )
            shutil.move(tmp_path, str(dest))
        except Exception:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except OSError:
                pass
            raise

    def backup(self) -> Path:
        """Create a timestamped backup next to the save file (or folder)."""
        if self.path is None:
            raise ValueError("No file loaded; cannot create backup.")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.folder is not None:
            # Back up the entire folder
            backup_path = self.folder.parent / f"{self.folder.name}.backup.{ts}"
            shutil.copytree(str(self.folder), str(backup_path))
        else:
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
            self.ships.append(
                Ship(
                    sid=sid,
                    name=ship_el.get("sname") or f"Ship #{sid}",
                    sx=int(ship_el.get("sx", 0)),
                    sy=int(ship_el.get("sy", 0)),
                    ox=int(ship_el.get("ox", 0)),
                    oy=int(ship_el.get("oy", 0)),
                    element=ship_el,
                )
            )
        self.ships.sort(key=lambda s: s.name)

    def get_ship_tiles(self, ship: Ship) -> list[tuple[int, int, str]]:
        """Return floor-plan tile data for *ship* as a list of (x, y, module_id) tuples.

        Each ``<e>`` child element of the ship element that carries both ``x``/``y``
        grid coordinates and an ``m`` module-type attribute is included.  The ``m``
        value identifies the kind of block (hull, wall, door, engine, storage, …).
        """
        if ship.element is None:
            return []
        tiles: list[tuple[int, int, str]] = []
        for e in ship.element.findall("e"):
            m = e.get("m")
            if m is None:
                continue
            try:
                x = int(e.get("x", "0"))
                y = int(e.get("y", "0"))
            except ValueError:
                continue
            tiles.append((x, y, m))
        return tiles

    def get_storage_containers(self, ship: Ship) -> list[StorageContainer]:
        """Return all storage containers (feat elements with eatAllowed + inv) for a ship."""
        if ship.sid in self._containers_cache:
            return self._containers_cache[ship.sid]
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
                items.append(
                    StorageItem(
                        item_id=item_id,
                        name=STORAGE_IDS.get(item_id, f"Unknown ({item_id})"),
                        quantity=qty,
                        element=s_el,
                    )
                )
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
            containers.append(
                StorageContainer(
                    display_name=display,
                    items=sorted(items, key=lambda i: i.name),
                    feat_element=feat,
                    inv_element=inv,
                )
            )
            idx += 1
        self._containers_cache[ship.sid] = containers
        return containers

    def add_storage_item(
        self, container: StorageContainer, item_id: int, quantity: int
    ) -> StorageItem | None:
        """Add or stack an item. Returns the new StorageItem, or None if stacked onto an existing one."""
        inv = container.inv_element
        # Check if item already exists in XML
        for s_el in inv.findall("s"):
            if s_el.get("elementaryId") == str(item_id):
                existing = int(s_el.get("inStorage", "0"))
                new_qty = existing + quantity
                s_el.set("inStorage", str(new_qty))
                # Update in-memory list if the item was already surfaced
                for item in container.items:
                    if item.item_id == item_id:
                        item.quantity = new_qty
                        return None  # stacked onto existing
                # Item existed in XML with qty=0 (filtered during parse) - surface it now
                surfaced = StorageItem(
                    item_id=item_id,
                    name=STORAGE_IDS.get(item_id, f"Unknown ({item_id})"),
                    quantity=new_qty,
                    element=s_el,
                )
                container.items.append(surfaced)
                container.items.sort(key=lambda i: i.name)
                return surfaced
        # New item
        new_el = etree.SubElement(inv, "s")
        new_el.set("elementaryId", str(item_id))
        new_el.set("inStorage", str(quantity))
        new_el.set("onTheWayIn", "0")
        new_el.set("onTheWayOut", "0")
        new_item = StorageItem(
            item_id=item_id,
            name=STORAGE_IDS.get(item_id, f"Unknown ({item_id})"),
            quantity=quantity,
            element=new_el,
        )
        container.items.append(new_item)
        container.items.sort(key=lambda i: i.name)
        return new_item

    def remove_storage_item(
        self, container: StorageContainer, item: StorageItem
    ) -> None:
        if item.element is not None:
            parent = item.element.getparent()
            if parent is not None:
                parent.remove(item.element)
        if item in container.items:
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
        for tag in STAT_TAGS:
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
            char.attributes.append(
                Attribute(
                    attr_id=attr_id,
                    name=ATTRIBUTE_IDS.get(attr_id, f"Unknown ({attr_id})"),
                    points=points,
                    element=a,
                )
            )

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
            char.skills.append(
                Skill(
                    skill_id=skill_id,
                    name=SKILL_IDS.get(skill_id, f"Unknown ({skill_id})"),
                    level=level,
                    max_level=max_level,
                    element=s,
                )
            )
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
            char.traits.append(
                Trait(
                    trait_id=trait_id,
                    name=TRAIT_IDS.get(trait_id, f"Unknown ({trait_id})"),
                    element=t,
                )
            )

    def _parse_char_conditions(self, pers: etree._Element, char: Character) -> None:
        conds_el = pers.find("conditions")
        if conds_el is None:
            return
        for c in conds_el.findall("c"):
            try:
                cond_id = int(c.get("id", "0"))
            except ValueError:
                continue
            char.conditions.append(
                Condition(
                    cond_id=cond_id,
                    name=CONDITION_IDS.get(cond_id, f"Unknown ({cond_id})"),
                    element=c,
                )
            )

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
            char.relationships.append(
                Relationship(
                    target_id=target_id,
                    target_name=f"Unknown ({target_id})",
                    friendship=friendship,
                    attraction=attraction,
                    compatibility=compatibility,
                    element=l_el,
                )
            )

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

    def set_friendship(self, rel: "Relationship", value: int) -> None:
        rel.friendship = value
        if rel.element is not None:
            rel.element.set("friendship", str(value))

    def set_attraction(self, rel: "Relationship", value: int) -> None:
        rel.attraction = value
        if rel.element is not None:
            rel.element.set("attraction", str(value))

    def set_compatibility(self, rel: "Relationship", value: int) -> None:
        rel.compatibility = value
        if rel.element is not None:
            rel.element.set("compatibility", str(value))

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

    def add_character(self, ship: Ship, first_name: str, last_name: str) -> Character:
        """Create a new crew member on *ship* with default stats and return it."""
        new_id = self._next_master_id()

        chars_el = ship.element.find("characters")
        if chars_el is None:
            chars_el = etree.SubElement(ship.element, "characters")

        c_el = etree.SubElement(chars_el, "c")
        c_el.set("entId", str(new_id))
        c_el.set("name", first_name)
        c_el.set("lname", last_name)
        c_el.set("cid", str(ship.sid))

        # Default stats at full health
        props = etree.SubElement(c_el, "props")
        for tag in STAT_TAGS:
            el = etree.SubElement(props, tag)
            el.set("v", "100")

        # Personality/skills container
        pers = etree.SubElement(c_el, "pers")

        # Default attributes (mid-range)
        attr_el = etree.SubElement(pers, "attr")
        for attr_id in ATTRIBUTE_IDS:
            a = etree.SubElement(attr_el, "a")
            a.set("id", str(attr_id))
            a.set("points", "5")

        # Default skills (level 0, max 10)
        skills_el = etree.SubElement(pers, "skills")
        for skill_id in SKILL_IDS:
            s = etree.SubElement(skills_el, "s")
            s.set("sk", str(skill_id))
            s.set("level", "0")
            s.set("mxn", "10")
            s.set("exp", "0")
            s.set("expd", "0")

        etree.SubElement(pers, "traits")
        etree.SubElement(pers, "conditions")
        sociality = etree.SubElement(pers, "sociality")
        etree.SubElement(sociality, "relationships")

        char = Character(
            ent_id=new_id,
            first_name=first_name,
            last_name=last_name,
            ship_sid=ship.sid,
            element=c_el,
            pers_element=pers,
        )
        self._parse_char_stats(c_el, char)
        self._parse_char_attributes(pers, char)
        self._parse_char_skills(pers, char)
        self.characters.append(char)
        return char

    def clone_character(self, source: Character, ship: Ship, first_name: str, last_name: str) -> Character:
        """Deep-copy *source* onto *ship* with a new entity ID and *first_name*/*last_name*."""
        new_id = self._next_master_id()
        new_el = copy.deepcopy(source.element)
        new_el.set("entId", str(new_id))
        new_el.set("name", first_name)
        new_el.set("lname", last_name)
        new_el.set("cid", str(ship.sid))

        chars_el = ship.element.find("characters")
        if chars_el is None:
            chars_el = etree.SubElement(ship.element, "characters")
        chars_el.append(new_el)

        pers_el = new_el.find("pers")
        char = Character(
            ent_id=new_id,
            first_name=first_name,
            last_name=last_name,
            ship_sid=ship.sid,
            element=new_el,
            pers_element=pers_el,
        )
        self._parse_char_stats(new_el, char)
        if pers_el is not None:
            self._parse_char_attributes(pers_el, char)
            self._parse_char_skills(pers_el, char)
            self._parse_char_traits(pers_el, char)
            self._parse_char_conditions(pers_el, char)
        self.characters.append(char)
        return char

    def remove_character(self, char: Character) -> None:
        """Remove *char* from its ship and from the in-memory character list."""
        if char.element is not None:
            parent = char.element.getparent()
            if parent is not None:
                parent.remove(char.element)
        if char in self.characters:
            self.characters.remove(char)

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

    def remove_ship(self, ship: Ship) -> None:
        """Remove *ship*, its crew, and its fleet reference from the XML."""
        # Drop in-memory characters for this ship
        self.characters = [c for c in self.characters if c.ship_sid != ship.sid]
        self._containers_cache.pop(ship.sid, None)
        # Remove the <ship> element
        if ship.element is not None:
            parent = ship.element.getparent()
            if parent is not None:
                parent.remove(ship.element)
        if not ship.in_game_file:
            # External ship: its fleet reference is recorded in the game file's starmap
            pass  # ship element already detached from its external tree above
        # Remove the fleet reference from the game file
        for f_el in self._root.iter("f"):
            if f_el.get("isPlayer") == "true":
                cs_el = f_el.find("createdShips")
                if cs_el is not None:
                    for l_el in cs_el.findall("l"):
                        if l_el.get("createdShipId") == str(ship.sid):
                            cs_el.remove(l_el)
                            break
        if ship in self.ships:
            self.ships.remove(ship)

    def add_ship(self, source_ship: Ship, name: str) -> Ship:
        """Clone *source_ship*, give it a new SID and *name*, clear its crew,
        remap internal entity IDs to avoid conflicts, register it in the player
        fleet, and return the new Ship object."""
        new_ship_el = copy.deepcopy(source_ship.element)

        # Derive a new unique SID from masterData.idCounter (same source the
        # game uses), falling back to max-existing-SID + 1.
        new_sid = self._next_master_id()
        new_ship_el.set("sid", str(new_sid))
        new_ship_el.set("sname", name)

        # Clear characters to avoid duplicate entity IDs in the roster
        chars_el = new_ship_el.find("characters")
        if chars_el is not None:
            new_ship_el.remove(chars_el)
        etree.SubElement(new_ship_el, "characters")

        # Remap all entity IDs inside the cloned ship so they are globally
        # unique (mirrors what the reference editor does).
        self._remap_entity_ids(new_ship_el)

        # Place the clone well clear of all existing ships in the sector.
        # Ship sx/sy are in tile units (~56 for a 2x2 ship) while sector
        # coordinates ox/oy are in the thousands, so use a large fixed gap.
        try:
            source_oy = int(new_ship_el.get("oy", "0"))
            all_ox = [
                int(s.element.get("ox", "0"))
                for s in self.ships
                if s.element is not None
            ]
            max_ox = max(all_ox) if all_ox else 0
            SECTOR_GAP = 5000  # puts the clone in a clearly different region
            new_ship_el.set("ox", str(max_ox + SECTOR_GAP * (len(self.ships))))
            new_ship_el.set("oy", str(source_oy))
        except ValueError:
            pass

        # Append to <ships>
        ships_el = self._root.find("ships")
        if ships_el is None:
            ships_el = etree.SubElement(self._root, "ships")
        ships_el.append(new_ship_el)

        # Register in the player fleet so the game recognises the ship
        self._add_fleet_reference(new_sid, name, source_ship.sx, source_ship.sy)

        new_ship = Ship(
            sid=new_sid,
            name=name,
            sx=source_ship.sx,
            sy=source_ship.sy,
            ox=int(new_ship_el.get("ox", 0)),
            oy=int(new_ship_el.get("oy", 0)),
            in_game_file=True,
            element=new_ship_el,
        )
        self.ships.append(new_ship)
        self.ships.sort(key=lambda s: s.name)
        return new_ship

    # ------------------------------------------------------------------
    # Helpers for add_ship
    # ------------------------------------------------------------------

    def _next_master_id(self) -> int:
        """Return a new unique ID from masterData.idCounter and advance it.

        Falls back to scanning the document for the highest existing entity ID
        (entId attributes + ship SIDs) when masterData is absent, so new IDs
        never collide with any entity already present in the tree.
        """
        md = self._root.find("masterData")
        if md is not None:
            try:
                current = int(md.get("idCounter", "0"))
                md.set("idCounter", str(current + 1))
                return current + 1
            except ValueError:
                pass
        # No masterData: derive a collision-free ID from the whole document.
        max_ent = max(
            (
                int(el.get("entId"))
                for el in self._root.iter()
                if el.get("entId") is not None and el.get("entId").lstrip("-").isdigit()
            ),
            default=0,
        )
        max_sid = max((s.sid for s in self.ships), default=0)
        return max(max_ent, max_sid) + 1

    _REMAP_REF_ATTRS = frozenset(
        {"bedLink", "targetId", "owner", "link", "doorLink", "controllerId"}
    )

    def _remap_entity_ids(self, ship_el: etree._Element) -> None:
        """Reassign every entId inside *ship_el* to a fresh globally-unique ID
        (from masterData.idCounter) and patch all cross-reference attributes."""
        md = self._root.find("masterData")
        if md is None:
            return
        try:
            id_counter = int(md.get("idCounter", "0"))
        except ValueError:
            return

        id_map: dict[str, str] = {}

        # First pass: assign new IDs
        for el in ship_el.iter():
            old = el.get("entId")
            if old:
                id_counter += 1
                new_id = str(id_counter)
                id_map[old] = new_id
                el.set("entId", new_id)

        # Second pass: patch references that point to remapped IDs
        for el in ship_el.iter():
            for attr in self._REMAP_REF_ATTRS:
                val = el.get(attr)
                if val and val in id_map:
                    el.set(attr, id_map[val])

        md.set("idCounter", str(id_counter))

    def _add_fleet_reference(self, sid: int, name: str, sx: int, sy: int) -> None:
        """Insert a <l createdShipId=...> entry in the player fleet."""
        for f_el in self._root.iter("f"):
            if f_el.get("isPlayer") == "true":
                cs_el = f_el.find("createdShips")
                if cs_el is None:
                    cs_el = etree.SubElement(f_el, "createdShips")
                l_el = etree.SubElement(cs_el, "l")
                l_el.set("seed", str(random.getrandbits(63)))
                l_el.set("createdShipId", str(sid))
                l_el.set("created", "true")
                l_el.set("station", "false")
                l_el.set("shipDamagedNoFTL", "false")
                l_el.set("crew", "0")
                l_el.set("cryoCrew", "0")
                l_el.set("monsters", "0")
                l_el.set("bigMonsters", "0")
                l_el.set("hives", "0")
                l_el.set("infesters", "0")
                l_el.set("flybots", "0")
                l_el.set("walkers", "0")
                l_el.set("roboBase", "0")
                l_el.set("derelict", "false")
                l_el.set("addLoot", "false")
                l_el.set("inHyper", "false")
                l_el.set("sx", str(sx))
                l_el.set("sy", str(sy))
                l_el.set("shn", name)
                l_el.set("idle", "-1")
                return

    # ------------------------------------------------------------------
    # Research
    # ------------------------------------------------------------------

    def _parse_research(self) -> None:
        self.research.clear()
        research_el = self._root.find("research")
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
            done = bool(stages) and all(
                s.get("done", "false") == "true" for s in stages
            )
            in_progress = (not done) and any(
                (
                    (bd := s.find("blocksDone")) is not None
                    and any(int(bd.get(a, "0")) > 0 for a in ("level1", "level2", "level3"))
                )
                for s in stages
            )
            self.research.append(
                ResearchEntry(
                    tech_id=tech_id,
                    name=TECH_IDS.get(tech_id, f"Unknown ({tech_id})"),
                    done=done,
                    in_progress=in_progress,
                    element=l_el,
                )
            )
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
