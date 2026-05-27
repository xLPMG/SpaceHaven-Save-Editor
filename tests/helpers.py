"""Shared test utilities for the SpaceHaven Save Editor test suite."""

from __future__ import annotations

import io

from lxml import etree

from src.save_file import SaveFile


def make_save_from_xml(xml: str | bytes) -> SaveFile:
    """Parse an XML string or bytes into a SaveFile without touching the filesystem.

    This is the single canonical implementation of the save-file test factory;
    all test modules should import and alias it rather than duplicating the
    boilerplate.
    """
    sf = SaveFile()
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    data = xml if isinstance(xml, bytes) else xml.encode()
    sf._tree = etree.parse(io.BytesIO(data), parser)
    sf._root = sf._tree.getroot()
    sf._parse_ships()
    sf._parse_characters()
    sf._parse_research()
    return sf
