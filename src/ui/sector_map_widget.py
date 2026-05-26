"""sector_map_widget.py - Interactive draggable sector map for ship positioning."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPen,
    QFont,
    QFontMetrics,
    QMouseEvent,
    QKeyEvent,
)
from PySide6.QtWidgets import QWidget

from src.save_file import world_to_ox_oy, ox_oy_to_world

if TYPE_CHECKING:
    from src.save_file import SaveFile, Ship


class SectorMapWidget(QWidget):
    """Interactive sector map showing ships as draggable rectangles."""
    
    ship_moved = Signal(object, int, int)  # ship, new_ox, new_oy
    
    MAP_PADDING = 40   # Padding around the map
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._ships: list[Ship] = []
        self._ship_colors: dict[int, QColor] = {}  # ship.sid -> color
        self._sector_sx: int = 382  # Sector width (default, updated on load)
        self._sector_sy: int = 382  # Sector height (default, updated on load)
        
        self._dragging_ship: Ship | None = None
        self._drag_start_pos: QPointF | None = None
        self._drag_offset: QPointF | None = None
        self._drag_original_ox: int = 0  # stored on drag start for Escape cancel
        self._drag_original_oy: int = 0
        self._hover_ship: Ship | None = None

        self.setMinimumSize(600, 600)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def load(self, save: SaveFile) -> None:
        """Load ships from the game file (current sector)."""
        self._save = save
        self._ships = [s for s in save.ships if s.in_game_file]
        self._sector_sx = save.sector_sx
        self._sector_sy = save.sector_sy

        # Assign stable colors keyed by ship id (new ships get a random color;
        # ships that were already in the map keep their existing color).
        for ship in self._ships:
            if ship.sid not in self._ship_colors:
                self._ship_colors[ship.sid] = self._random_pastel_color()

        self.update()
    
    def clear(self) -> None:
        """Clear the map."""
        self._save = None
        self._ships = []
        self._ship_colors.clear()
        self._dragging_ship = None
        self._hover_ship = None
        self.update()
    
    def _random_pastel_color(self) -> QColor:
        """Generate a random pastel color for ship rectangles."""
        hue = random.randint(0, 359)
        saturation = random.randint(40, 70)  # Pastel saturation
        value = random.randint(70, 90)  # Pastel brightness
        return QColor.fromHsv(hue, int(saturation * 2.55), int(value * 2.55))
    
    def _world_to_screen(self, wx: float, wy: float) -> QPointF:
        """Convert world coordinates to screen coordinates.

        The Y axis is flipped so that world-north (high wy) appears at the top
        of the widget.  X is unchanged.
        Maps: world (0, sy) → screen top-left, world (sx, sy) → screen top-right.
        """
        rotated_x = wx
        rotated_y = self._sector_sy - wy
        
        scale = self._get_scale()
        screen_x = self.MAP_PADDING + rotated_x * scale
        screen_y = self.MAP_PADDING + rotated_y * scale
        return QPointF(screen_x, screen_y)
    
    def _screen_to_world(self, screen_x: float, screen_y: float) -> tuple[float, float]:
        """Convert screen coordinates to world coordinates (reverse Y-flip)."""  
        scale = self._get_scale()
        rotated_x = (screen_x - self.MAP_PADDING) / scale
        rotated_y = (screen_y - self.MAP_PADDING) / scale
        
        # Reverse: wx = rotated_x, wy = sy - rotated_y
        wx = rotated_x
        wy = self._sector_sy - rotated_y
        return wx, wy
    
    def _get_scale(self) -> float:
        """Get the current scale factor (screen pixels per world unit)."""
        available_width = self.width() - 2 * self.MAP_PADDING
        available_height = self.height() - 2 * self.MAP_PADDING
        # Y-flip doesn't change dimensions
        scale_x = available_width / self._sector_sx
        scale_y = available_height / self._sector_sy
        return min(scale_x, scale_y)
    
    def _get_ship_rect_world(self, ship: Ship) -> tuple[float, float, int, int]:
        """Get ship rectangle in world coordinates: (wx, wy, width, height)."""
        wx, wy = ox_oy_to_world(ship.ox, ship.oy)
        return wx, wy, ship.sx, ship.sy
    
    def _get_ship_rect_screen(self, ship: Ship) -> QRectF:
        """Get ship rectangle in screen coordinates."""
        wx, wy, w, h = self._get_ship_rect_world(ship)
        # Screen top-left corresponds to world (wx, wy+h)
        anchor_world = self._world_to_screen(wx, wy + h)
        scale = self._get_scale()
        # Y-flip doesn't swap dimensions
        return QRectF(anchor_world.x(), anchor_world.y(), w * scale, h * scale)
    
    def _ship_at_point(self, screen_pos: QPointF) -> Ship | None:
        """Find ship at screen position."""
        for ship in reversed(self._ships):  # Check top ships first
            rect = self._get_ship_rect_screen(ship)
            if rect.contains(screen_pos):
                return ship
        return None
    
    def _clamp_ship_position(self, ship: Ship, wx: float, wy: float) -> tuple[float, float]:
        """Clamp ship position to stay within sector bounds."""
        wx = max(0.0, min(wx, self._sector_sx - 1 - ship.sx))
        wy = max(0.0, min(wy, self._sector_sy - 1 - ship.sy))
        return wx, wy
    
    def _check_overlap(self, ship: Ship, wx: float, wy: float) -> bool:
        """Return True if the ship placed at (wx, wy) would overlap any other ship."""
        ship_rect = QRectF(wx, wy, ship.sx, ship.sy)
        for other in self._ships:
            if other.sid == ship.sid:
                continue
            other_wx, other_wy, other_w, other_h = self._get_ship_rect_world(other)
            if ship_rect.intersects(QRectF(other_wx, other_wy, other_w, other_h)):
                return True
        return False
    
    def _find_valid_position(self, ship: Ship, target_wx: float, target_wy: float) -> tuple[float, float]:
        """Find nearest valid position for ship (no overlap, within bounds)."""
        # Clamp to bounds first
        target_wx, target_wy = self._clamp_ship_position(ship, target_wx, target_wy)
        
        # Check if target position is valid (no overlap)
        if not self._check_overlap(ship, target_wx, target_wy):
            return target_wx, target_wy
        
        # Try to slide along edges to find valid position
        # Try adjusting X
        for dx in [0, 1, -1, 2, -2, 5, -5, 10, -10]:
            test_wx = target_wx + dx
            test_wx, _ = self._clamp_ship_position(ship, test_wx, target_wy)
            if not self._check_overlap(ship, test_wx, target_wy):
                return test_wx, target_wy
        
        # Try adjusting Y
        for dy in [0, 1, -1, 2, -2, 5, -5, 10, -10]:
            test_wy = target_wy + dy
            _, test_wy = self._clamp_ship_position(ship, target_wx, test_wy)
            if not self._check_overlap(ship, target_wx, test_wy):
                return target_wx, test_wy
        
        # If no valid position found nearby, return original position
        orig_wx, orig_wy = ox_oy_to_world(ship.ox, ship.oy)
        return orig_wx, orig_wy
    
    def paintEvent(self, event) -> None:
        """Paint the sector map and ships."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(20, 20, 30))
        
        if not self._ships:
            # Show "no data" message
            painter.setPen(QColor(150, 150, 150))
            font = QFont("Arial", 12)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 
                           "No sector loaded")
            return
        
        # Draw sector boundary
        scale = self._get_scale()
        sector_rect = QRectF(
            self.MAP_PADDING,
            self.MAP_PADDING,
            self._sector_sx * scale,
            self._sector_sy * scale
        )
        painter.setPen(QPen(QColor(100, 100, 120), 2))
        painter.setBrush(QBrush(QColor(30, 30, 40)))
        painter.drawRect(sector_rect)
        
        # Draw ships
        for ship in self._ships:
            self._draw_ship(painter, ship)
    
    def _draw_ship(self, painter: QPainter, ship: Ship) -> None:
        """Draw a single ship rectangle with name label."""
        rect = self._get_ship_rect_screen(ship)
        
        # Determine appearance
        is_dragging = (ship == self._dragging_ship)
        is_hover = (ship == self._hover_ship and not is_dragging)
        
        # Ship rectangle
        color = self._ship_colors.get(ship.sid, QColor(100, 100, 150))
        
        if is_dragging:
            painter.setBrush(QBrush(color.lighter(120)))
            painter.setPen(QPen(QColor(255, 255, 255), 2))
        elif is_hover:
            painter.setBrush(QBrush(color.lighter(110)))
            painter.setPen(QPen(QColor(200, 200, 255), 2))
        else:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(50, 50, 60), 1))
        
        painter.drawRect(rect)
        
        # Ship name label
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        
        # Draw name above ship if there's room, otherwise below
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(ship.name)
        text_height = fm.height()
        
        text_x = rect.center().x() - text_width / 2
        if rect.top() > self.MAP_PADDING + text_height + 5:
            text_y = rect.top() - 5
        else:
            text_y = rect.bottom() + text_height
        
        # Draw text with black outline for readability
        painter.setPen(QColor(0, 0, 0))
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            painter.drawText(QPointF(text_x + dx, text_y + dy), ship.name)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QPointF(text_x, text_y), ship.name)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press - start dragging ship."""
        if event.button() == Qt.MouseButton.LeftButton:
            ship = self._ship_at_point(event.position())
            if ship:
                self._dragging_ship = ship
                self._drag_original_ox = ship.ox  # saved so Escape can revert
                self._drag_original_oy = ship.oy
                self._drag_start_pos = event.position()
                ship_rect = self._get_ship_rect_screen(ship)
                self._drag_offset = event.position() - ship_rect.topLeft()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.setFocus()  # receive key events while dragging
                self.update()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move - drag ship or update hover."""
        if self._dragging_ship:
            # Dragging
            if self._drag_offset:
                new_screen_pos = event.position() - self._drag_offset
                # new_screen_pos is the top-left of the ship rect in screen space.
                # Due to the Y-flip, the screen top-left of a ship rect maps to
                # world (wx, wy + ship.sy), so subtract ship.sy to get the base wy.
                new_wx_raw, new_wy_raw = self._screen_to_world(new_screen_pos.x(), new_screen_pos.y())
                new_wx = new_wx_raw
                new_wy = new_wy_raw - self._dragging_ship.sy
                
                # Find valid position (clamped and no overlap)
                valid_wx, valid_wy = self._find_valid_position(
                    self._dragging_ship, new_wx, new_wy
                )
                
                # Update ship position temporarily for visual feedback
                self._dragging_ship.ox, self._dragging_ship.oy = world_to_ox_oy(valid_wx, valid_wy)
                self.update()
        else:
            # Hover detection
            ship = self._ship_at_point(event.position())
            if ship != self._hover_ship:
                self._hover_ship = ship
                self.setCursor(Qt.CursorShape.OpenHandCursor if ship else Qt.CursorShape.ArrowCursor)
                self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release - commit the drag and emit ship_moved."""
        if event.button() == Qt.MouseButton.LeftButton and self._dragging_ship:
            self.ship_moved.emit(self._dragging_ship, self._dragging_ship.ox, self._dragging_ship.oy)
            self._end_drag(event.position())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Cancel an in-progress drag when Escape is pressed."""
        if event.key() == Qt.Key.Key_Escape and self._dragging_ship:
            # Revert ship to its position before the drag started
            self._dragging_ship.ox = self._drag_original_ox
            self._dragging_ship.oy = self._drag_original_oy
            self._end_drag(None)
        else:
            super().keyPressEvent(event)

    def _end_drag(self, cursor_pos: QPointF | None) -> None:
        """Tear down drag state and restore cursor."""
        self._dragging_ship = None
        self._drag_start_pos = None
        self._drag_offset = None
        if cursor_pos is not None:
            ship = self._ship_at_point(cursor_pos)
            self._hover_ship = ship
            self.setCursor(Qt.CursorShape.OpenHandCursor if ship else Qt.CursorShape.ArrowCursor)
        else:
            self._hover_ship = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
