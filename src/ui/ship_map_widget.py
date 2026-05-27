"""ship_map_widget.py - Color-coded bird's-eye ship layout renderer."""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QSizePolicy, QWidget

from src.ui.styles import (
    MAP_COLOR_BG,
    MAP_COLOR_DOOR,
    MAP_COLOR_ENGINE,
    MAP_COLOR_HULL,
    MAP_COLOR_INTERIOR,
    MAP_COLOR_LEGEND_TEXT,
    MAP_COLOR_RESTRICTED,
    MAP_COLOR_STORAGE,
    MAP_COLOR_WALL,
    MAP_LEGEND,
)
from src.game_data import (
    DOOR_TILE_IDS,
    ENGINE_TILE_IDS,
    HULL_TILE_IDS,
    STORAGE_TILE_IDS,
    WALL_TILE_IDS,
)


def _tile_color(m: str) -> QColor | None:
    """Return the display color for a tile with module-id *m*, or None to skip."""
    if m == "-2":
        return MAP_COLOR_RESTRICTED
    if m in HULL_TILE_IDS:
        return MAP_COLOR_HULL
    if m in WALL_TILE_IDS:
        return MAP_COLOR_WALL
    if m in DOOR_TILE_IDS:
        return MAP_COLOR_DOOR
    if m in ENGINE_TILE_IDS:
        return MAP_COLOR_ENGINE
    if m in STORAGE_TILE_IDS:
        return MAP_COLOR_STORAGE
    return MAP_COLOR_INTERIOR


class ShipMapWidget(QWidget):
    """Renders a zoomable, color-coded floor-plan of a Space Haven ship."""

    _LEGEND_H = 22  # pixels reserved for the legend strip
    _MIN_CELL = 2  # minimum cell size in pixels
    _MAX_CELL = 20  # maximum cell size in pixels
    _GAP = 1  # gap between cells

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tiles: list[tuple[int, int, str]] = []  # (x, y, m)
        self._grid_w = 0
        self._grid_h = 0
        self.setMinimumSize(200, 140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_tiles(self, tiles: list[tuple[int, int, str]]) -> None:
        """Load tile data and repaint.

        Each element is a (grid_x, grid_y, module_id_str) tuple where
        module_id_str is the raw value of the XML attribute ``m``.
        """
        self._tiles = tiles
        if tiles:
            xs = [x for x, _, _ in tiles]
            ys = [y for _, y, _ in tiles]
            self._grid_w = max(xs) - min(xs) + 1
            self._grid_h = max(ys) - min(ys) + 1
            self._min_x = min(xs)
            self._min_y = min(ys)
        else:
            self._grid_w = self._grid_h = 0
            self._min_x = self._min_y = 0
        self.update()

    def clear(self) -> None:
        self._tiles = []
        self._grid_w = self._grid_h = 0
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(400, 260)

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        w = self.width()
        h = self.height() - self._LEGEND_H

        # Background
        painter.fillRect(0, 0, w, h, MAP_COLOR_BG)

        if not self._tiles or self._grid_w == 0 or self._grid_h == 0:
            painter.setPen(MAP_COLOR_LEGEND_TEXT)
            painter.drawText(
                QRect(0, 0, w, h),
                Qt.AlignmentFlag.AlignCenter,
                "No tile data available",
            )
            self._paint_legend(painter, w, h)
            painter.end()
            return

        # Compute cell size so the grid fits with a small margin
        margin = 8
        available_w = w - 2 * margin
        available_h = h - 2 * margin
        cell_w = available_w // self._grid_w - self._GAP
        cell_h = available_h // self._grid_h - self._GAP
        cell = max(self._MIN_CELL, min(cell_w, cell_h, self._MAX_CELL))

        # Centre the grid
        total_w = self._grid_w * (cell + self._GAP) - self._GAP
        total_h = self._grid_h * (cell + self._GAP) - self._GAP
        off_x = (w - total_w) // 2
        off_y = (h - total_h) // 2

        # Build a lookup for fast painting
        tile_lookup: dict[tuple[int, int], str] = {}
        for tx, ty, m in self._tiles:
            tile_lookup[(tx - self._min_x, ty - self._min_y)] = m

        painter.setPen(Qt.PenStyle.NoPen)
        for (gx, gy), m in tile_lookup.items():
            color = _tile_color(m)
            if color is None:
                continue
            # Flip 180 deg: mirror both axes
            flipped_gx = (self._grid_w - 1) - gx
            flipped_gy = (self._grid_h - 1) - gy
            px = off_x + flipped_gx * (cell + self._GAP)
            py = off_y + flipped_gy * (cell + self._GAP)
            painter.fillRect(px, py, cell, cell, color)

        self._paint_legend(painter, w, h)
        painter.end()

    def _paint_legend(self, painter: QPainter, w: int, map_h: int) -> None:
        y = map_h + 2
        strip_h = self._LEGEND_H - 4
        painter.fillRect(0, map_h, w, self._LEGEND_H, MAP_COLOR_BG)

        swatch = strip_h - 2
        x = 8
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        for color, label in MAP_LEGEND:
            if x + swatch + 4 + 50 > w:
                break
            painter.fillRect(x, y + 1, swatch, swatch, color)
            painter.setPen(MAP_COLOR_LEGEND_TEXT)
            painter.drawText(
                x + swatch + 4, y, 60, strip_h, Qt.AlignmentFlag.AlignVCenter, label
            )
            x += swatch + 4 + 52
