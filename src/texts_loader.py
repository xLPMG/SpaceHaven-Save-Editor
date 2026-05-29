"""texts_loader.py – Loads the bundled SpaceHaven library/texts file.

The game ships a single ``library/texts`` XML file that contains translated
strings for every language the game supports, keyed by an integer text ID.
This module parses that file at startup and exposes a :class:`GameTexts`
singleton (:data:`game_texts`) that the UI can use for localized lookups.

The file uses ``<t id="N">`` nodes with child elements named after each
language code (``<EN>``, ``<DE>``, ``<FR>``, …).  The raw file contains
occasional bare ``<`` characters inside element text (line-wrapped content),
so we rely on *lxml* with ``recover=True`` to parse it tolerantly.

This module intentionally does **not** import Qt so it can be safely imported
before ``QApplication`` is created.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

_TEXTS_PATH = Path(__file__).parent.parent / "data" / "library" / "texts"

# Preferred display order + human-readable names for every language in the file.
LANG_DISPLAY: dict[str, str] = {
    "EN": "English",
    "DE": "Deutsch",
    "ES": "Español",
    "FR": "Français",
    "IT": "Italiano",
    "PL": "Polski",
    "CS": "Čeština",
    "RU": "Русский",
    "PTBR": "Português (BR)",
    "KO": "한국어",
    "JA": "日本語",
    "CN": "中文",
    "TR": "Türkçe",
}


class GameTexts:
    """Provides translated text lookups from the bundled ``library/texts`` file.

    Language selection is tracked via :py:attr:`current_lang`.  Register a
    callable with :py:meth:`on_lang_changed` to be notified (with the new
    language code) whenever the language changes.

    This class is **not** a ``QObject`` so it can be instantiated before
    ``QApplication`` exists.
    """

    def __init__(self) -> None:
        self._lang: str = "EN"
        # {text_id: {lang_code: translated_string}}
        self._data: dict[int, dict[str, str]] = {}
        self._langs: list[str] = []
        self._listeners: list[Callable[[str], None]] = []
        self._load()

    # ------------------------------------------------------------------
    # Internal loading
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not _TEXTS_PATH.exists():
            return
        try:
            from lxml import etree  # already a project dependency

            parser = etree.XMLParser(recover=True)
            tree = etree.parse(str(_TEXTS_PATH), parser)
            root = tree.getroot()
            langs_seen: set[str] = set()
            for node in root.iter("t"):
                tid_str = node.get("id")
                if tid_str is None:
                    continue
                try:
                    tid = int(tid_str)
                except ValueError:
                    continue
                texts: dict[str, str] = {}
                for child in node:
                    tag = child.tag
                    if not isinstance(tag, str) or tag == "t":
                        continue
                    text = (child.text or "").strip()
                    if text:
                        texts[tag] = text
                        langs_seen.add(tag)
                if texts:
                    self._data[tid] = texts
            # Preserve the preferred order defined in LANG_DISPLAY.
            self._langs = [c for c in LANG_DISPLAY if c in langs_seen]
        except Exception:
            # Degrade gracefully – the hardcoded EN strings in game_data.py
            # serve as fallbacks whenever this loader is unavailable.
            pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def current_lang(self) -> str:
        """Currently selected language code (e.g. ``"EN"``, ``"DE"``)."""
        return self._lang

    @property
    def available_langs(self) -> list[tuple[str, str]]:
        """``[(code, display_name), …]`` for every language present in the file."""
        return [(c, LANG_DISPLAY.get(c, c)) for c in self._langs]

    def set_lang(self, code: str) -> None:
        """Switch to *code* and notify all registered listeners."""
        if code != self._lang:
            self._lang = code
            for fn in self._listeners:
                fn(code)

    def on_lang_changed(self, fn: Callable[[str], None]) -> None:
        """Register *fn* to be called with the new language code on change."""
        self._listeners.append(fn)

    def get(self, text_id: int, fallback: str = "") -> str:
        """Return the string for *text_id* in :py:attr:`current_lang`.

        Falls back to ``"EN"`` if the current language has no entry, then to
        *fallback* if even the English string is absent.
        """
        entry = self._data.get(text_id)
        if entry is None:
            return fallback
        return entry.get(self._lang) or entry.get("EN") or fallback


game_texts: GameTexts = GameTexts()
