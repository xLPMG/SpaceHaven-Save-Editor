"""crew_tab.py – Ship / crew / character editor tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QEvent, QRect, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.save_file import Character, SaveFile, Ship, Skill, Trait

from src.save_file import Condition
from src.game_data import TRAIT_BY_NAME, TRAIT_IDS

class _CrewRemoveDelegate(QStyledItemDelegate):
    """Paints a ✕ glyph on the right of each crew entry and emits
    *remove_requested(row)* when it is clicked."""

    remove_requested = Signal(int)
    _BTN_W = 22

    def paint(self, painter, option, index) -> None:
        # Shrink the text rect so it doesn't overlap the ✕ glyph
        text_opt = QStyleOptionViewItem(option)
        text_opt.rect = option.rect.adjusted(0, 0, -self._BTN_W, 0)
        super().paint(painter, text_opt, index)

        btn_rect = QRect(
            option.rect.right() - self._BTN_W,
            option.rect.top(),
            self._BTN_W,
            option.rect.height(),
        )
        painter.save()
        painter.setPen(QColor("#f38ba8"))
        f = QFont(painter.font())
        f.setPointSize(10)
        painter.setFont(f)
        painter.drawText(btn_rect, Qt.AlignmentFlag.AlignCenter, "\u2715")
        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:
        if event.type() == QEvent.Type.MouseButtonRelease:
            btn_rect = QRect(
                option.rect.right() - self._BTN_W,
                option.rect.top(),
                self._BTN_W,
                option.rect.height(),
            )
            if btn_rect.contains(event.position().toPoint()):
                self.remove_requested.emit(index.row())
                return True
        return super().editorEvent(event, model, option, index)


# Palette of muted accent colors for avatar circles
_AVATAR_COLORS = [
    "#89b4fa",
    "#a6e3a1",
    "#fab387",
    "#f38ba8",
    "#cba6f7",
    "#94e2d5",
    "#f9e2af",
    "#89dceb",
]


class _AvatarLabel(QLabel):
    """Circular label showing character initials."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._initials = "?"
        self._color = _AVATAR_COLORS[0]
        self.setFixedSize(56, 56)

    def set_character(self, first: str, last: str) -> None:
        self._initials = (first[:1] + last[:1]).upper() if first or last else "?"
        # Deterministic color from name
        idx = (ord(first[:1]) if first else 0) % len(_AVATAR_COLORS)
        self._color = _AVATAR_COLORS[idx]
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addEllipse(2, 2, self.width() - 4, self.height() - 4)
        painter.fillPath(path, QColor(self._color))

        font = QFont()
        font.setPointSize(18)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#1e1e2e"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._initials)
        painter.end()


class CrewTab(QWidget):
    status_message = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._current_ship: Ship | None = None
        self._current_char: Character | None = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        # ── Left panel ──────────────────────────────────────────────
        left = QWidget()
        left.setObjectName("CrewLeftPanel")
        left.setMinimumWidth(210)
        left.setMaximumWidth(290)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(14, 14, 8, 14)
        lv.setSpacing(8)

        ship_label = QLabel("Ship")
        ship_label.setObjectName("PanelSectionLabel")
        lv.addWidget(ship_label)

        self._ship_combo = QComboBox()
        self._ship_combo.currentIndexChanged.connect(self._on_ship_changed)
        lv.addWidget(self._ship_combo)

        crew_header = QHBoxLayout()
        crew_lbl = QLabel("Crew Members")
        crew_lbl.setObjectName("PanelSectionLabel")
        crew_header.addWidget(crew_lbl)
        crew_header.addStretch()
        self._crew_count = QLabel("0")
        self._crew_count.setObjectName("CrewCountBadge")
        crew_header.addWidget(self._crew_count)
        lv.addSpacing(4)
        lv.addLayout(crew_header)

        self._crew_list = QListWidget()
        self._crew_list.setObjectName("CrewList")
        self._crew_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._crew_list.currentRowChanged.connect(self._on_crew_selected)
        self._crew_delegate = _CrewRemoveDelegate(self._crew_list)
        self._crew_delegate.remove_requested.connect(self._on_remove_requested)
        self._crew_list.setItemDelegate(self._crew_delegate)
        lv.addWidget(self._crew_list)

        add_crew_btn = QPushButton("+ Add Member")
        add_crew_btn.setObjectName("InlineButton")
        add_crew_btn.clicked.connect(self._add_crew_member)
        lv.addWidget(add_crew_btn)

        splitter.addWidget(left)

        # ── Right panel ─────────────────────────────────────────────
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(8, 14, 14, 14)
        rv.setSpacing(10)

        # Character header card
        header_card = QWidget()
        header_card.setObjectName("CharHeaderCard")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setSpacing(14)

        self._avatar = _AvatarLabel()
        header_layout.addWidget(self._avatar)

        name_col = QVBoxLayout()
        name_col.setSpacing(6)

        name_edit_row = QHBoxLayout()
        name_edit_row.setSpacing(8)
        self._first_name_edit = QLineEdit()
        self._first_name_edit.setPlaceholderText("First name")
        self._first_name_edit.setObjectName("NameEdit")
        self._last_name_edit = QLineEdit()
        self._last_name_edit.setPlaceholderText("Last name")
        self._last_name_edit.setObjectName("NameEdit")
        name_edit_row.addWidget(self._first_name_edit)
        name_edit_row.addWidget(self._last_name_edit)
        name_col.addLayout(name_edit_row)

        rename_btn = QPushButton("Rename")
        rename_btn.setObjectName("InlineButton")
        rename_btn.setFixedWidth(90)
        rename_btn.clicked.connect(self._rename_character)
        name_col.addWidget(rename_btn)

        header_layout.addLayout(name_col)
        rv.addWidget(header_card)

        # Detail tabs
        self._tabs = QTabWidget()
        self._tabs.setObjectName("CharDetailTabs")
        self._tabs.addTab(self._build_stats_tab(), "Stats")
        self._tabs.addTab(self._build_attributes_tab(), "Attributes")
        self._tabs.addTab(self._build_skills_tab(), "Skills")
        self._tabs.addTab(self._build_traits_tab(), "Traits")
        self._tabs.addTab(self._build_conditions_tab(), "Conditions")
        self._tabs.addTab(self._build_relationships_tab(), "Relationships")
        rv.addWidget(self._tabs)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self._set_right_enabled(False)

    # ── Sub-tab builders ────────────────────────────────────────────

    def _build_stats_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        self._stats_form = QFormLayout()
        self._stats_form.setSpacing(6)
        self._stats_spins: dict[str, QSpinBox] = {}
        for tag in (
            "Health",
            "Food",
            "Rest",
            "Mood",
            "Comfort",
            "Oxygen",
            "Temperature",
        ):
            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setFixedWidth(80)
            self._stats_spins[tag] = spin
            self._stats_form.addRow(f"{tag}:", spin)
        layout.addLayout(self._stats_form)

        layout.addStretch()
        return w

    def _build_attributes_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        info = QLabel("Attribute points (typically 0–10).")
        info.setObjectName("StatCardDesc")
        layout.addWidget(info)

        self._attr_table = QTableWidget(0, 2)
        self._attr_table.setHorizontalHeaderLabels(["Attribute", "Points"])
        self._attr_table.horizontalHeader().setStretchLastSection(True)
        self._attr_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._attr_table.verticalHeader().setVisible(False)
        layout.addWidget(self._attr_table)

        return w

    def _build_skills_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        info = QLabel("Edit skill levels and max natural levels.")
        info.setObjectName("StatCardDesc")
        layout.addWidget(info)

        self._skills_table = QTableWidget(0, 3)
        self._skills_table.setHorizontalHeaderLabels(["Skill", "Level", "Max Level"])
        self._skills_table.horizontalHeader().setStretchLastSection(False)
        self._skills_table.horizontalHeader().setSectionResizeMode(
            0, self._skills_table.horizontalHeader().ResizeMode.Stretch
        )
        self._skills_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._skills_table.verticalHeader().setVisible(False)
        self._skills_table.verticalHeader().setDefaultSectionSize(42)
        layout.addWidget(self._skills_table)

        return w

    def _build_traits_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self._traits_list = QListWidget()
        self._traits_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        layout.addWidget(self._traits_list)

        row = QHBoxLayout()
        row.setSpacing(6)
        self._add_trait_combo = QComboBox()
        self._add_trait_combo.setEditable(False)
        for name in sorted(TRAIT_IDS.values()):
            self._add_trait_combo.addItem(name, TRAIT_BY_NAME[name])
        self._add_trait_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        row.addWidget(self._add_trait_combo)

        add_btn = QPushButton("Add Trait")
        add_btn.setObjectName("InlineButton")
        add_btn.setFixedWidth(90)
        add_btn.clicked.connect(self._add_trait)
        row.addWidget(add_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("DangerButton")
        remove_btn.setFixedWidth(80)
        remove_btn.clicked.connect(self._remove_trait)
        row.addWidget(remove_btn)
        layout.addLayout(row)

        return w

    def _build_conditions_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self._conditions_list = QListWidget()
        self._conditions_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        layout.addWidget(self._conditions_list)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        remove_cond_btn = QPushButton("Remove Selected")
        remove_cond_btn.setObjectName("DangerButton")
        remove_cond_btn.clicked.connect(self._remove_condition)
        btn_row.addWidget(remove_cond_btn)
        clear_cond_btn = QPushButton("Clear All")
        clear_cond_btn.setObjectName("DangerButton")
        clear_cond_btn.clicked.connect(self._clear_conditions)
        btn_row.addWidget(clear_cond_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        return w

    def _build_relationships_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)

        self._rel_table = QTableWidget(0, 4)
        self._rel_table.setHorizontalHeaderLabels(
            ["Character", "Friendship", "Attraction", "Compatibility"]
        )
        hdr = self._rel_table.horizontalHeader()
        hdr.setSectionResizeMode(0, hdr.ResizeMode.Stretch)
        self._rel_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._rel_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._rel_table.verticalHeader().setVisible(False)
        layout.addWidget(self._rel_table)
        return w

    # ------------------------------------------------------------------
    # Load / Clear
    # ------------------------------------------------------------------

    def load(self, save: SaveFile) -> None:
        self._save = save
        self._current_ship = None
        self._current_char = None

        self._ship_combo.blockSignals(True)
        self._ship_combo.clear()
        for ship in save.ships:
            self._ship_combo.addItem(ship.name, ship)
        self._ship_combo.blockSignals(False)

        if save.ships:
            self._ship_combo.setCurrentIndex(0)
            self._on_ship_changed(0)
        else:
            self._crew_list.clear()
            self._set_right_enabled(False)

    def clear(self) -> None:
        self._save = None
        self._current_ship = None
        self._current_char = None
        self._ship_combo.blockSignals(True)
        self._ship_combo.clear()
        self._ship_combo.blockSignals(False)
        self._crew_list.clear()
        self._crew_count.setText("Crew: 0")
        self._clear_character_panels()
        self._set_right_enabled(False)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_ship_changed(self, index: int) -> None:
        if self._save is None or index < 0:
            return
        ship: Ship = self._ship_combo.itemData(index)
        self._current_ship = ship
        self._current_char = None

        crew = [c for c in self._save.characters if c.ship_sid == ship.sid]
        crew.sort(key=lambda c: c.full_name)

        self._crew_list.blockSignals(True)
        self._crew_list.clear()
        for char in crew:
            self._add_crew_item(char)
        self._crew_list.blockSignals(False)
        self._crew_count.setText(str(len(crew)))
        self._clear_character_panels()
        self._set_right_enabled(False)

    def _on_crew_selected(self, row: int) -> None:
        if row < 0:
            self._current_char = None
            self._clear_character_panels()
            self._set_right_enabled(False)
            return
        item = self._crew_list.item(row)
        if item is None:
            return
        char: Character = item.data(Qt.ItemDataRole.UserRole)
        self._current_char = char
        self._populate_character(char)
        self._set_right_enabled(True)

    # ------------------------------------------------------------------
    # Populate panels
    # ------------------------------------------------------------------

    def _populate_character(self, char: Character) -> None:
        self._avatar.set_character(char.first_name, char.last_name)
        self._first_name_edit.setText(char.first_name)
        self._last_name_edit.setText(char.last_name)
        self._populate_stats(char)
        self._populate_attributes(char)
        self._populate_skills(char)
        self._populate_traits(char)
        self._populate_conditions(char)
        self._populate_relationships(char)

    def _populate_stats(self, char: Character) -> None:
        stat_map = {s.tag: s for s in char.stats}
        for tag, spin in self._stats_spins.items():
            spin.blockSignals(True)
            stat = stat_map.get(tag)
            spin.setValue(stat.value if stat else 0)
            spin.blockSignals(False)
            # Reconnect to the specific Stat object for this character
            try:
                spin.valueChanged.disconnect()
            except RuntimeError:
                pass
            if stat is not None:
                spin.valueChanged.connect(
                    lambda v, s=stat: self._on_stat_changed(s, v)
                )

    def _on_stat_changed(self, stat, value: int) -> None:
        if self._save is None:
            return
        self._save.set_stat(stat, value)
        self.status_message.emit("Stats applied (unsaved).")

    def _populate_attributes(self, char: Character) -> None:
        self._attr_table.setRowCount(0)
        for attr in sorted(char.attributes, key=lambda a: a.name):
            row = self._attr_table.rowCount()
            self._attr_table.insertRow(row)
            name_item = QTableWidgetItem(attr.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, attr)
            self._attr_table.setItem(row, 0, name_item)
            spin = QSpinBox()
            spin.setRange(0, 20)
            spin.setValue(attr.points)
            spin.valueChanged.connect(
                lambda v, a=attr: self._on_attribute_changed(a, v)
            )
            self._attr_table.setCellWidget(row, 1, spin)

    def _on_attribute_changed(self, attr, value: int) -> None:
        if self._save is None:
            return
        self._save.set_attribute(attr, value)
        self.status_message.emit("Attributes applied (unsaved).")

    def _populate_skills(self, char: Character) -> None:
        self._skills_table.setRowCount(0)
        for skill in char.skills:
            row = self._skills_table.rowCount()
            self._skills_table.insertRow(row)
            name_item = QTableWidgetItem(skill.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, skill)
            self._skills_table.setItem(row, 0, name_item)

            level_spin = QSpinBox()
            level_spin.setRange(0, skill.max_level)
            level_spin.setValue(skill.level)
            self._skills_table.setCellWidget(row, 1, level_spin)

            max_spin = QSpinBox()
            max_spin.setRange(skill.level, 20)
            max_spin.setValue(skill.max_level)
            self._skills_table.setCellWidget(row, 2, max_spin)

            # Cross-link: level's max tracks max_spin; max's min tracks level_spin
            level_spin.valueChanged.connect(
                lambda v, ms=max_spin, sk=skill: (
                    ms.setMinimum(v),
                    self._on_skill_level_changed(sk, v),
                )
            )
            max_spin.valueChanged.connect(
                lambda v, ls=level_spin, sk=skill: (
                    ls.setMaximum(v),
                    self._on_skill_max_changed(sk, v),
                )
            )

    def _on_skill_level_changed(self, skill, value: int) -> None:
        if self._save is None:
            return
        self._save.set_skill_level(skill, value)
        self.status_message.emit("Skills applied (unsaved).")

    def _on_skill_max_changed(self, skill, value: int) -> None:
        if self._save is None:
            return
        self._save.set_skill_max(skill, value)
        self.status_message.emit("Skills applied (unsaved.).")

    def _populate_traits(self, char: Character) -> None:
        self._traits_list.clear()
        for trait in sorted(char.traits, key=lambda t: t.name):
            item = QListWidgetItem(trait.name)
            item.setData(Qt.ItemDataRole.UserRole, trait)
            self._traits_list.addItem(item)

    def _populate_conditions(self, char: Character) -> None:
        self._conditions_list.clear()
        for cond in sorted(char.conditions, key=lambda c: c.name):
            item = QListWidgetItem(cond.name)
            item.setData(Qt.ItemDataRole.UserRole, cond)
            self._conditions_list.addItem(item)

    def _populate_relationships(self, char: Character) -> None:
        self._rel_table.setRowCount(0)
        for rel in sorted(char.relationships, key=lambda r: r.target_name):
            row = self._rel_table.rowCount()
            self._rel_table.insertRow(row)
            self._rel_table.setItem(row, 0, QTableWidgetItem(rel.target_name))
            self._rel_table.setItem(row, 1, QTableWidgetItem(str(rel.friendship)))
            self._rel_table.setItem(row, 2, QTableWidgetItem(str(rel.attraction)))
            self._rel_table.setItem(row, 3, QTableWidgetItem(str(rel.compatibility)))

    # ------------------------------------------------------------------
    # Apply changes
    # ------------------------------------------------------------------

    def _remove_condition(self) -> None:
        if self._save is None or self._current_char is None:
            return
        selected = self._conditions_list.currentItem()
        if selected is None:
            return
        cond: Condition = selected.data(Qt.ItemDataRole.UserRole)
        self._save.remove_condition(self._current_char, cond)
        self._conditions_list.takeItem(self._conditions_list.row(selected))
        self.status_message.emit("Condition removed (unsaved).")

    def _clear_conditions(self) -> None:
        if self._save is None or self._current_char is None:
            return
        self._save.clear_conditions(self._current_char)
        self._conditions_list.clear()
        self.status_message.emit("All conditions cleared (unsaved).")

    def _rename_character(self) -> None:
        if self._save is None or self._current_char is None:
            return
        first = self._first_name_edit.text().strip()
        last = self._last_name_edit.text().strip()
        if not first:
            QMessageBox.warning(self, "Rename", "First name cannot be empty.")
            return
        self._save.rename_character(self._current_char, first, last)
        # Refresh crew list item text
        for i in range(self._crew_list.count()):
            item = self._crew_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) is self._current_char:
                item.setText(self._current_char.full_name)
                break
        self.status_message.emit("Character renamed (unsaved).")

    def _add_trait(self) -> None:
        if self._save is None or self._current_char is None:
            return
        trait_id: int = self._add_trait_combo.currentData()
        trait = self._save.add_trait(self._current_char, trait_id)
        if trait is None:
            QMessageBox.information(self, "Add Trait", "That trait is already present.")
            return
        item = QListWidgetItem(trait.name)
        item.setData(Qt.ItemDataRole.UserRole, trait)
        self._traits_list.addItem(item)
        # Keep sorted
        self._populate_traits(self._current_char)
        self.status_message.emit("Trait added (unsaved).")

    def _remove_trait(self) -> None:
        if self._save is None or self._current_char is None:
            return
        selected = self._traits_list.currentItem()
        if selected is None:
            QMessageBox.information(self, "Remove Trait", "Select a trait to remove.")
            return
        trait: Trait = selected.data(Qt.ItemDataRole.UserRole)
        self._save.remove_trait(self._current_char, trait)
        self._traits_list.takeItem(self._traits_list.row(selected))
        self.status_message.emit("Trait removed (unsaved).")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _add_crew_item(self, char: Character, row: int | None = None) -> QListWidgetItem:
        """Create a crew list entry (the delegate draws the ✕ glyph)."""
        item = QListWidgetItem(char.full_name)
        item.setData(Qt.ItemDataRole.UserRole, char)
        if row is None:
            self._crew_list.addItem(item)
        else:
            self._crew_list.insertItem(row, item)
        return item

    def _on_remove_requested(self, row: int) -> None:
        item = self._crew_list.item(row)
        if item is None:
            return
        char: Character = item.data(Qt.ItemDataRole.UserRole)
        self._remove_crew_member_by_char(char)

    def _clear_character_panels(self) -> None:
        self._avatar.set_character("", "")
        self._first_name_edit.clear()
        self._last_name_edit.clear()
        for spin in self._stats_spins.values():
            spin.setValue(0)
        self._attr_table.setRowCount(0)
        self._skills_table.setRowCount(0)
        self._traits_list.clear()
        self._conditions_list.clear()
        self._rel_table.setRowCount(0)

    def _set_right_enabled(self, enabled: bool) -> None:
        self._first_name_edit.setEnabled(enabled)
        self._last_name_edit.setEnabled(enabled)
        self._tabs.setEnabled(enabled)

    # ------------------------------------------------------------------
    # Add / Remove crew members
    # ------------------------------------------------------------------

    def _add_crew_member(self) -> None:
        if self._save is None or self._current_ship is None:
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Add Crew Member")
        dlg_layout = QVBoxLayout(dlg)
        dlg_layout.setSpacing(10)
        dlg_layout.setContentsMargins(16, 16, 16, 16)

        form = QFormLayout()
        first_edit = QLineEdit()
        first_edit.setPlaceholderText("First name")
        last_edit = QLineEdit()
        last_edit.setPlaceholderText("Last name")
        form.addRow("First name:", first_edit)
        form.addRow("Last name:", last_edit)
        dlg_layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        dlg_layout.addWidget(buttons)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        first = first_edit.text().strip()
        last = last_edit.text().strip()
        if not first:
            QMessageBox.warning(self, "Add Crew Member", "First name cannot be empty.")
            return

        char = self._save.add_character(self._current_ship, first, last)
        # Insert in sorted position
        crew = [c for c in self._save.characters if c.ship_sid == self._current_ship.sid]
        crew.sort(key=lambda c: c.full_name)
        idx = crew.index(char)
        self._add_crew_item(char, row=idx)
        self._crew_count.setText(str(self._crew_list.count()))
        self._crew_list.setCurrentRow(idx)
        self.status_message.emit(f"Crew member '{char.full_name}' added (unsaved).")

    def _remove_crew_member_by_char(self, char: Character) -> None:
        """Remove a crew member (called from the ✕ button on each list row)."""
        if self._save is None:
            return
        target_row = -1
        for i in range(self._crew_list.count()):
            if self._crew_list.item(i).data(Qt.ItemDataRole.UserRole) is char:
                target_row = i
                break
        if target_row == -1:
            return
        self._save.remove_character(char)
        self._crew_list.takeItem(target_row)
        self._crew_count.setText(str(self._crew_list.count()))
        if self._current_char is char:
            self._current_char = None
            self._clear_character_panels()
            self._set_right_enabled(False)
        self.status_message.emit(f"'{char.full_name}' removed (unsaved).")
