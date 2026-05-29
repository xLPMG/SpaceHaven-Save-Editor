"""crew_tab.py – Ship / crew / character editor tab."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from lxml import etree

from PySide6.QtCore import Qt, QEvent, QRect, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
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
    QToolTip,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.save_file import Character, SaveFile, Ship, Trait

from src.save_file import Condition, SKILL_HARD_MAX
from src.game_data import (
    ATTRIBUTE_TEXT_IDS,
    BACKSTORY_IDS,
    BACKSTORY_TEXT_IDS,
    CONDITION_TEXT_IDS,
    CUSTOM_SKILL_PRESETS,
    DEFAULT_SCHEDULE_P0,
    DEFAULT_SCHEDULE_P1,
    DEFAULT_SCHEDULE_P2,
    DEFAULT_SEC_S0,
    DEFAULT_SEC_S1,
    DEFAULT_SEC_S2,
    SKILL_TEXT_IDS,
    TRAIT_IDS,
    TRAIT_TEXT_IDS,
)
from src.texts_loader import game_texts
from src.ui.styles import (
    ACTION_CLONE_COLOR,
    ACTION_REMOVE_COLOR,
    CREW_AVATAR_COLORS,
    CREW_AVATAR_TEXT_COLOR,
    PIP_FILLED_COLOR,
    PIP_EMPTY_COLOR,
)

MAX_ATTR_POINTS: int = 10  # UI edit cap for attribute points

JOB_PRIORITY_VALUES: tuple[str, ...] = (
    "DontDo",
    "Lowest",
    "Low",
    "Normal",
    "High",
    "Highest",
)
JOB_PROFESSIONS: tuple[str, ...] = (
    "Navigate",
    "Gunner",
    "Shield",
    "Operations",
    "Fighter",
    "Medical",
    "Farm",
    "Construct",
    "Maintenance",
    "Mine",
    "Industry",
    "Research",
    "Logistics",
)
COMMON_TASKS: tuple[str, ...] = (
    "Walk",
    "Sleep",
    "MedicalSleep",
    "Idle",
)
COMMON_DIRECTIONS: tuple[str, ...] = ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8")


class _CrewDelegate(QStyledItemDelegate):
    """Paints clone and remove action glyphs on the right of each
    crew entry and emits the corresponding signal when clicked."""

    remove_requested = Signal(int)
    clone_requested = Signal(int)
    _ICON_BTN_W = 24

    def paint(self, painter, option, index) -> None:
        text_opt = QStyleOptionViewItem(option)
        text_opt.rect = option.rect.adjusted(0, 0, -self._ICON_BTN_W * 2, 0)
        super().paint(painter, text_opt, index)

        clone_rect = QRect(
            option.rect.right() - self._ICON_BTN_W * 2,
            option.rect.top(),
            self._ICON_BTN_W,
            option.rect.height(),
        )
        remove_rect = QRect(
            option.rect.right() - self._ICON_BTN_W,
            option.rect.top(),
            self._ICON_BTN_W,
            option.rect.height(),
        )
        painter.save()
        f = QFont(painter.font())
        f.setPointSize(13)
        painter.setFont(f)
        painter.setPen(ACTION_CLONE_COLOR)
        painter.drawText(clone_rect, Qt.AlignmentFlag.AlignCenter, "\u29c9")
        painter.setPen(ACTION_REMOVE_COLOR)
        painter.drawText(remove_rect, Qt.AlignmentFlag.AlignCenter, "\u2715")
        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:
        if event.type() == QEvent.Type.MouseButtonRelease:
            pos = event.position().toPoint()
            clone_rect = QRect(
                option.rect.right() - self._ICON_BTN_W * 2,
                option.rect.top(),
                self._ICON_BTN_W,
                option.rect.height(),
            )
            remove_rect = QRect(
                option.rect.right() - self._ICON_BTN_W,
                option.rect.top(),
                self._ICON_BTN_W,
                option.rect.height(),
            )
            if clone_rect.contains(pos):
                self.clone_requested.emit(index.row())
                return True
            if remove_rect.contains(pos):
                self.remove_requested.emit(index.row())
                return True
        return super().editorEvent(event, model, option, index)

    def helpEvent(self, event, view, option, index) -> bool:
        pos = event.pos()
        clone_rect = QRect(
            option.rect.right() - self._ICON_BTN_W * 2,
            option.rect.top(),
            self._ICON_BTN_W,
            option.rect.height(),
        )
        remove_rect = QRect(
            option.rect.right() - self._ICON_BTN_W,
            option.rect.top(),
            self._ICON_BTN_W,
            option.rect.height(),
        )
        if clone_rect.contains(pos):
            QToolTip.showText(event.globalPos(), "Duplicate crew member", view)
            return True
        if remove_rect.contains(pos):
            QToolTip.showText(event.globalPos(), "Remove crew member", view)
            return True
        return super().helpEvent(event, view, option, index)


def _pip_html(level: int, max_level: int) -> str:
    """Return rich-text pip string for a skill/attribute bar."""
    filled = f"<span style='color:{PIP_FILLED_COLOR};'>{'●' * level}</span>"
    empty = f"<span style='color:{PIP_EMPTY_COLOR};'>{'○' * (max_level - level)}</span>"
    return filled + empty


class _AvatarLabel(QLabel):
    """Circular label showing character initials."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._initials = "?"
        self._color = CREW_AVATAR_COLORS[0]
        self.setFixedSize(56, 56)

    def set_character(self, first: str, last: str) -> None:
        self._initials = (first[:1] + last[:1]).upper() if first or last else "?"
        # Deterministic color from name
        idx = (ord(first[:1]) if first else 0) % len(CREW_AVATAR_COLORS)
        self._color = CREW_AVATAR_COLORS[idx]
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
        painter.setPen(CREW_AVATAR_TEXT_COLOR)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._initials)
        painter.end()


class CrewTab(QWidget):
    status_message = Signal(str)
    crew_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._current_ship: Ship | None = None
        self._current_char: Character | None = None
        self._build_ui()
        game_texts.on_lang_changed(self._on_lang_changed)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        # Left panel
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
        self._crew_delegate = _CrewDelegate(self._crew_list)
        self._crew_delegate.remove_requested.connect(self._on_remove_requested)
        self._crew_delegate.clone_requested.connect(self._clone_crew_member)
        self._crew_list.setItemDelegate(self._crew_delegate)
        lv.addWidget(self._crew_list)

        add_crew_btn = QPushButton("+ Add Member")
        add_crew_btn.setObjectName("InlineButton")
        add_crew_btn.clicked.connect(self._add_crew_member)
        lv.addWidget(add_crew_btn)

        splitter.addWidget(left)

        # Right panel
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
        self._first_name_edit.editingFinished.connect(self._rename_character)
        self._last_name_edit.editingFinished.connect(self._rename_character)
        name_edit_row.addWidget(self._first_name_edit)
        name_edit_row.addWidget(self._last_name_edit)
        name_col.addLayout(name_edit_row)

        header_layout.addLayout(name_col)
        rv.addWidget(header_card)

        # Detail tabs
        self._tabs = QTabWidget()
        self._tabs.setObjectName("CharDetailTabs")
        self._tabs.setDocumentMode(True)
        tab_bar = self._tabs.tabBar()
        tab_bar.setExpanding(True)
        tab_bar.setUsesScrollButtons(False)
        tab_bar.setElideMode(Qt.TextElideMode.ElideNone)
        self._tabs.addTab(self._build_stats_tab(), "Stats")
        self._tabs.addTab(self._build_attributes_tab(), "Attributes")
        self._tabs.addTab(self._build_skills_tab(), "Skills")
        self._tabs.addTab(self._build_jobs_tab(), "Jobs")
        self._tabs.addTab(self._build_traits_tab(), "Traits")
        self._tabs.addTab(self._build_conditions_tab(), "Conditions")
        self._tabs.addTab(self._build_relationships_tab(), "Relationships")
        self._tabs.addTab(self._build_behavior_tab(), "Behavior")
        self._tabs.addTab(self._build_schedule_tab(), "Schedule")
        self._tabs.addTab(self._build_appearance_tab(), "Appearance")
        self._tabs.addTab(self._build_loadout_tab(), "Loadout")
        self._tabs.addTab(self._build_identity_tab(), "Identity")

        self._advanced_tab_names = {
            "Behavior",
            "Schedule",
            "Appearance",
            "Loadout",
            "Identity",
        }
        mode_row = QHBoxLayout()
        mode_row.addStretch()
        self._advanced_mode_check = QCheckBox("Advanced mode")
        self._advanced_mode_check.setChecked(False)
        self._advanced_mode_check.toggled.connect(self._set_advanced_tabs_visible)
        mode_row.addWidget(self._advanced_mode_check)
        rv.addLayout(mode_row)

        rv.addWidget(self._tabs)
        self._set_advanced_tabs_visible(False)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self._set_right_enabled(False)

    # Sub-tab builders

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
            "Comfort",
            "Mood",
            "Oxygen",
            "Temperature",
        ):
            spin = QSpinBox()
            spin.setRange(0, 200)  # game allows values > 100 (e.g. buffed health)
            spin.setFixedWidth(80)
            spin.valueChanged.connect(
                lambda v, t=tag: self._on_stat_changed_by_tag(t, v)
            )
            self._stats_spins[tag] = spin
            self._stats_form.addRow(f"{tag}:", spin)
        layout.addLayout(self._stats_form)

        layout.addSpacing(6)

        advanced_lbl = QLabel("Advanced atmosphere sensors")
        advanced_lbl.setObjectName("StatCardDesc")
        layout.addWidget(advanced_lbl)

        layout.addSpacing(6)

        self._gas_spins: dict[str, QSpinBox] = {}
        gas_form = QFormLayout()
        for tag in ("Co2Gas", "SmokeGas", "HazardousGas"):
            spin = QSpinBox()
            spin.setRange(0, 200)
            spin.setFixedWidth(80)
            spin.valueChanged.connect(
                lambda v, t=tag: self._on_gas_stat_changed_by_tag(t, v)
            )
            self._gas_spins[tag] = spin
            gas_form.addRow(f"{tag}:", spin)
        layout.addLayout(gas_form)

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

        self._attr_table = QTableWidget(0, 3)
        self._attr_table.setHorizontalHeaderLabels(["Attribute", "", "Points"])
        self._attr_table.horizontalHeader().setStretchLastSection(False)
        self._attr_table.horizontalHeader().setSectionResizeMode(
            0, self._attr_table.horizontalHeader().ResizeMode.ResizeToContents
        )
        self._attr_table.horizontalHeader().setSectionResizeMode(
            1, self._attr_table.horizontalHeader().ResizeMode.Stretch
        )
        self._attr_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._attr_table.verticalHeader().setVisible(False)
        self._attr_table.verticalHeader().setDefaultSectionSize(42)
        layout.addWidget(self._attr_table)

        return w

    def _build_skills_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Preset:"))
        self._skill_preset_combo = QComboBox()
        self._skill_preset_combo.addItems(list(CUSTOM_SKILL_PRESETS.keys()))
        preset_row.addWidget(self._skill_preset_combo)
        preset_btn = QPushButton("Apply")
        preset_btn.setObjectName("InlineButton")
        preset_btn.clicked.connect(self._apply_skill_preset)
        preset_row.addWidget(preset_btn)
        preset_row.addStretch()
        layout.addLayout(preset_row)

        self._skills_table = QTableWidget(0, 4)
        self._skills_table.setHorizontalHeaderLabels(
            ["Skill", "", "Level", "Max Level"]
        )
        self._skills_table.horizontalHeader().setStretchLastSection(False)
        self._skills_table.horizontalHeader().setSectionResizeMode(
            0, self._skills_table.horizontalHeader().ResizeMode.ResizeToContents
        )
        self._skills_table.horizontalHeader().setSectionResizeMode(
            1, self._skills_table.horizontalHeader().ResizeMode.Stretch
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
        for trait_id, en_name in sorted(
            TRAIT_IDS.items(),
            key=lambda x: game_texts.get(TRAIT_TEXT_IDS.get(x[0], 0), x[1]),
        ):
            self._add_trait_combo.addItem(
                game_texts.get(TRAIT_TEXT_IDS.get(trait_id, 0), en_name), trait_id
            )
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
        self._rel_table.verticalHeader().setDefaultSectionSize(42)
        layout.addWidget(self._rel_table)

        btn_row = QHBoxLayout()
        normalize_btn = QPushButton("Normalize All")
        normalize_btn.setObjectName("InlineButton")
        normalize_btn.clicked.connect(self._normalize_relationships)
        btn_row.addWidget(normalize_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        return w

    def _build_behavior_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        form = QFormLayout()
        form.setSpacing(6)

        self._task_combo = QComboBox()
        self._task_combo.setEditable(True)
        for task in COMMON_TASKS:
            self._task_combo.addItem(task)
        self._task_combo.currentTextChanged.connect(self._on_task_changed)
        form.addRow("Task:", self._task_combo)

        self._ai_spins: dict[str, QSpinBox] = {}
        for key, min_v, max_v in (
            ("bts", 0, 1000),
            ("suitOn", 0, 1),
            ("bstx", -5000, 5000),
            ("bsty", -5000, 5000),
            ("bstsh", 0, 1000),
            ("hsid", 0, 1000000),
            ("rest", 0, 1000000000),
        ):
            sp = QSpinBox()
            sp.setRange(min_v, max_v)
            sp.valueChanged.connect(lambda v, k=key: self._on_ai_field_changed(k, v))
            self._ai_spins[key] = sp
            form.addRow(f"AI {key}:", sp)

        self._pers_spins: dict[str, QSpinBox] = {}
        for key, min_v, max_v in (
            ("ret", 0, 10),
            ("ret2", 0, 10),
            ("globalSch", 0, 10),
        ):
            sp = QSpinBox()
            sp.setRange(min_v, max_v)
            sp.valueChanged.connect(
                lambda v, k=key: self._on_pers_field_changed(k, str(v))
            )
            self._pers_spins[key] = sp
            form.addRow(f"Pers {key}:", sp)

        self._use_global_check = QCheckBox("Use global schedule")
        self._use_global_check.toggled.connect(self._on_use_global_toggled)
        form.addRow("", self._use_global_check)
        layout.addLayout(form)

        layout.addStretch()
        return w

    def _build_jobs_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        backstory_row = QHBoxLayout()
        backstory_row.addWidget(QLabel("Backstory:"))
        self._backstory_combo = QComboBox()
        for bs_id, bs_name in sorted(
            BACKSTORY_IDS.items(),
            key=lambda x: game_texts.get(BACKSTORY_TEXT_IDS.get(x[0], 0), x[1]),
        ):
            self._backstory_combo.addItem(
                game_texts.get(BACKSTORY_TEXT_IDS.get(bs_id, 0), bs_name), bs_id
            )
        self._backstory_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._backstory_combo.currentIndexChanged.connect(self._on_backstory_changed)
        backstory_row.addWidget(self._backstory_combo)
        layout.addLayout(backstory_row)

        note = QLabel(
            "Backstory is the character's pre-game profession (e.g. Teacher, Doctor). "
            "It affects starting skill minimums and mood factors, but does not control "
            "what the character does on the ship, which is set by the priorities below."
        )
        note.setObjectName("StatCardDesc")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addSpacing(4)

        self._job_table = QTableWidget(0, 2)
        self._job_table.setHorizontalHeaderLabels(["Profession", "Priority"])
        self._job_table.horizontalHeader().setStretchLastSection(True)
        self._job_table.verticalHeader().setVisible(False)
        self._job_table.verticalHeader().setDefaultSectionSize(48)
        self._job_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._job_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        job_hdr = self._job_table.horizontalHeader()
        job_hdr.setSectionResizeMode(0, job_hdr.ResizeMode.Stretch)
        job_hdr.setSectionResizeMode(1, job_hdr.ResizeMode.Fixed)
        self._job_table.setColumnWidth(1, 170)
        for prof in JOB_PROFESSIONS:
            row = self._job_table.rowCount()
            self._job_table.insertRow(row)
            item = QTableWidgetItem(prof)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._job_table.setItem(row, 0, item)
            combo = QComboBox()
            for p in JOB_PRIORITY_VALUES:
                combo.addItem(p)
            combo.setMinimumContentsLength(8)
            combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
            combo.setMinimumWidth(150)
            combo.setMinimumHeight(36)
            combo.currentTextChanged.connect(
                lambda text, profession=prof: self._on_job_priority_changed(
                    profession, text
                )
            )
            self._job_table.setCellWidget(row, 1, combo)
        layout.addWidget(self._job_table)
        return w

    def _build_schedule_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)
        self._mask_edits: dict[str, QLineEdit] = {}
        self._mask_binary_labels: dict[str, QLabel] = {}
        labels = ["p0", "p1", "p2", "s0", "s1", "s2"]
        for row, key in enumerate(labels):
            grid.addWidget(QLabel(f"{key}:"), row, 0)
            edit = QLineEdit()
            edit.setPlaceholderText("integer mask")
            edit.editingFinished.connect(
                lambda k=key, e=edit: self._on_mask_edited(k, e)
            )
            self._mask_edits[key] = edit
            grid.addWidget(edit, row, 1)
            bin_lbl = QLabel("")
            bin_lbl.setObjectName("StatCardDesc")
            self._mask_binary_labels[key] = bin_lbl
            grid.addWidget(bin_lbl, row, 2)
        layout.addLayout(grid)

        note = QLabel("Bitmask preview is shown as binary for quick sanity checks.")
        note.setObjectName("StatCardDesc")
        layout.addWidget(note)
        layout.addStretch()
        return w

    def _build_appearance_tab(self) -> QWidget:
        w = QWidget()
        wrap = QVBoxLayout(w)
        wrap.setContentsMargins(12, 12, 12, 12)
        wrap.setSpacing(8)

        top = QHBoxLayout()
        randomize_btn = QPushButton("Randomize")
        randomize_btn.setObjectName("InlineButton")
        randomize_btn.clicked.connect(self._randomize_appearance)
        top.addWidget(randomize_btn)
        top.addStretch()
        wrap.addLayout(top)

        form_widget = QWidget()
        layout = QFormLayout(form_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._appearance_controls: dict[str, QWidget] = {}
        color_keys = {
            "pantsSet",
            "shirtSet",
            "skinSet",
            "sp",
            "ss",
            "sr",
            "sh",
            "ssh",
            "sg",
            "sl",
        }

        def _add_combo(key: str, values: tuple[str, ...], label: str) -> None:
            cb = QComboBox()
            for value in values:
                cb.addItem(value)
            cb.currentTextChanged.connect(
                lambda text, k=key: self._set_char_attr(k, text)
            )
            self._appearance_controls[key] = cb
            layout.addRow(label, cb)

        def _add_spin(key: str, min_v: int, max_v: int, label: str) -> None:
            sp = QSpinBox()
            sp.setRange(min_v, max_v)
            if key in color_keys:
                sp.valueChanged.connect(
                    lambda value, k=key: self._set_colors_attr(k, str(value))
                )
            else:
                sp.valueChanged.connect(
                    lambda value, k=key: self._set_char_attr(k, str(value))
                )
            self._appearance_controls[key] = sp
            layout.addRow(label, sp)

        def _add_check(key: str, label: str) -> None:
            ch = QCheckBox()
            ch.toggled.connect(
                lambda on, k=key: self._set_colors_attr(k, "true" if on else "false")
            )
            self._appearance_controls[key] = ch
            layout.addRow(label, ch)

        _add_combo("bb", ("m", "f"), "Body BB:")
        _add_spin("bs", 0, 10, "Body BS:")
        _add_combo("bh", ("m", "f"), "Body BH:")
        _add_spin("bp", 0, 10, "Body BP:")
        _add_spin("orgColor", 0, 100000, "Org Color:")
        _add_spin("colorSet", 0, 100000, "Color Set:")

        for key, label in (
            ("glovesOff", "Gloves Off:"),
            ("longSleeve", "Long Sleeve:"),
        ):
            _add_check(key, label)
        for key, label in (
            ("pantsSet", "Pants Set:"),
            ("shirtSet", "Shirt Set:"),
            ("skinSet", "Skin Set:"),
            ("sp", "SP:"),
            ("ss", "SS:"),
            ("sr", "SR:"),
            ("sh", "SH:"),
            ("ssh", "SSH:"),
            ("sg", "SG:"),
            ("sl", "SL:"),
        ):
            _add_spin(key, 0, 100000, label)

        wrap.addWidget(form_widget)
        return w

    def _build_loadout_tab(self) -> QWidget:
        w = QWidget()
        layout = QFormLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        self._loadout_spins: dict[str, QSpinBox] = {}
        self._loadout_checks: dict[str, QCheckBox] = {}

        for key, label in (
            ("headgear", "Headgear:"),
            ("armor", "Armor:"),
            ("primary", "Primary:"),
            ("attachment", "Attachment:"),
            ("secondary", "Secondary:"),
            ("pocket1", "Pocket 1:"),
            ("pocket2", "Pocket 2:"),
            ("pocket3", "Pocket 3:"),
        ):
            sp = QSpinBox()
            sp.setRange(0, 10000000)
            sp.valueChanged.connect(lambda v, k=key: self._set_loadout_attr(k, str(v)))
            self._loadout_spins[key] = sp
            layout.addRow(label, sp)

        for key, label in (
            ("bestQArmor", "Best Quality Armor:"),
            ("bestQPrimary", "Best Quality Primary:"),
        ):
            ch = QCheckBox()
            ch.toggled.connect(
                lambda on, k=key: self._set_loadout_attr(k, "true" if on else "false")
            )
            self._loadout_checks[key] = ch
            layout.addRow(label, ch)

        return w

    def _build_identity_tab(self) -> QWidget:
        w = QWidget()
        layout = QFormLayout(w)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self._cid_combo = QComboBox()
        self._cid_combo.setEditable(True)
        self._cid_combo.addItem("89")
        self._cid_combo.currentTextChanged.connect(
            lambda text: self._set_char_attr("cid", text)
        )
        layout.addRow("Character Template (cid):", self._cid_combo)

        self._side_combo = QComboBox()
        self._side_combo.setEditable(True)
        for side in ("Player", "Neutral", "Enemy"):
            self._side_combo.addItem(side)
        self._side_combo.currentTextChanged.connect(
            lambda text: self._set_char_attr("side", text)
        )
        layout.addRow("Side:", self._side_combo)

        self._fac_spin = QSpinBox()
        self._fac_spin.setRange(0, 1000000)
        self._fac_spin.valueChanged.connect(
            lambda value: self._set_char_attr("fac", str(value))
        )
        layout.addRow("Faction (fac):", self._fac_spin)

        self._dir_combo = QComboBox()
        self._dir_combo.setEditable(True)
        for direction in COMMON_DIRECTIONS:
            self._dir_combo.addItem(direction)
        self._dir_combo.currentTextChanged.connect(
            lambda text: self._set_char_attr("dir", text)
        )
        layout.addRow("Direction:", self._dir_combo)

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
        self._crew_count.setText("0")
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
        if crew:
            self._crew_list.setCurrentRow(0)
        else:
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
        self._populate_jobs(char)
        self._populate_behavior(char)
        self._populate_schedule(char)
        self._populate_appearance(char)
        self._populate_loadout(char)
        self._populate_identity(char)

    def _populate_stats(self, char: Character) -> None:
        stat_map = {s.tag: s for s in char.stats}
        for tag, spin in self._stats_spins.items():
            spin.blockSignals(True)
            stat = stat_map.get(tag)
            spin.setValue(stat.value if stat else 0)
            spin.blockSignals(False)

        props = char.element.find("props")
        for tag, spin in self._gas_spins.items():
            spin.blockSignals(True)
            value = 0
            if props is not None:
                node = props.find(tag)
                if node is not None:
                    value = self._parse_int(node.get("v", "0"), 0)
            spin.setValue(value)
            spin.blockSignals(False)

    def _on_stat_changed_by_tag(self, tag: str, value: int) -> None:
        if self._save is None or self._current_char is None:
            return
        stat = next((s for s in self._current_char.stats if s.tag == tag), None)
        if stat is not None:
            self._save.set_stat(stat, value)
            self.status_message.emit("Stats applied (unsaved.)")

    def _on_gas_stat_changed_by_tag(self, tag: str, value: int) -> None:
        if self._current_char is None:
            return
        props = self._current_char.element.find("props")
        if props is None:
            props = etree.SubElement(self._current_char.element, "props")
        node = props.find(tag)
        if node is None:
            node = etree.SubElement(props, tag)
        node.set("v", str(value))
        self.status_message.emit("Advanced stats applied (unsaved).")

    def _populate_attributes(self, char: Character) -> None:
        self._attr_table.setRowCount(0)
        for attr in sorted(char.attributes, key=lambda a: game_texts.get(ATTRIBUTE_TEXT_IDS.get(a.attr_id, 0), a.name)):
            if self._save is not None:
                clamped = max(0, min(attr.points, MAX_ATTR_POINTS))
                if clamped != attr.points:
                    self._save.set_attribute(attr, clamped)

            row = self._attr_table.rowCount()
            self._attr_table.insertRow(row)
            name_item = QTableWidgetItem(game_texts.get(ATTRIBUTE_TEXT_IDS.get(attr.attr_id, 0), attr.name))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, attr)
            self._attr_table.setItem(row, 0, name_item)

            pip_lbl = self._skill_pip_label(attr.points, MAX_ATTR_POINTS)
            self._attr_table.setCellWidget(row, 1, pip_lbl)

            spin = QSpinBox()
            spin.setRange(0, MAX_ATTR_POINTS)
            spin.setValue(attr.points)
            spin.valueChanged.connect(
                lambda v, a=attr, pl=pip_lbl: self._on_attr_spin_changed(a, pl, v)
            )
            self._attr_table.setCellWidget(row, 2, spin)

    def _on_attribute_changed(self, attr, value: int) -> None:
        if self._save is None:
            return
        self._save.set_attribute(attr, value)
        self.status_message.emit("Attributes applied (unsaved).")

    @staticmethod
    def _skill_pip_label(level: int, max_level: int) -> QLabel:
        lbl = QLabel(_pip_html(level, max_level))
        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        lbl.setStyleSheet("padding-left: 6px; letter-spacing: 1px;")
        lbl.setTextFormat(Qt.TextFormat.RichText)
        return lbl

    def _populate_skills(self, char: Character) -> None:
        self._skills_table.setRowCount(0)
        for skill in char.skills:
            # Clamp out-of-range values and persist the correction via _save
            if self._save is not None:
                clamped_max = max(0, min(skill.max_level, SKILL_HARD_MAX))
                if clamped_max != skill.max_level:
                    self._save.set_skill_max(skill, clamped_max)
                clamped_level = max(0, min(skill.level, skill.max_level))
                if clamped_level != skill.level:
                    self._save.set_skill_level(skill, clamped_level)

            row = self._skills_table.rowCount()
            self._skills_table.insertRow(row)
            name_item = QTableWidgetItem(game_texts.get(SKILL_TEXT_IDS.get(skill.skill_id, 0), skill.name))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, skill)
            self._skills_table.setItem(row, 0, name_item)

            pip_lbl = self._skill_pip_label(skill.level, skill.max_level)
            self._skills_table.setCellWidget(row, 1, pip_lbl)

            level_spin = QSpinBox()
            level_spin.setRange(0, skill.max_level)
            level_spin.setValue(skill.level)
            self._skills_table.setCellWidget(row, 2, level_spin)

            max_spin = QSpinBox()
            max_spin.setRange(0, SKILL_HARD_MAX)
            max_spin.setValue(skill.max_level)
            self._skills_table.setCellWidget(row, 3, max_spin)

            level_spin.valueChanged.connect(
                lambda v, pl=pip_lbl, ms=max_spin, sk=skill: (
                    pl.setText(_pip_html(v, ms.value())),
                    self._on_skill_level_changed(sk, v),
                )
            )
            max_spin.valueChanged.connect(
                lambda v, ls=level_spin, pl=pip_lbl, sk=skill: (
                    ls.setMaximum(v),
                    pl.setText(_pip_html(ls.value(), v)),
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
        self.status_message.emit("Skills applied (unsaved).")

    def _apply_skill_preset(self) -> None:
        if self._save is None or self._current_char is None:
            return
        preset = self._skill_preset_combo.currentText()
        profile = CUSTOM_SKILL_PRESETS.get(preset, {})
        changes = 0
        for skill in self._current_char.skills:
            target = profile.get(skill.skill_id)
            if target is None:
                continue
            start_level, max_level = target
            max_level = max(0, min(max_level, SKILL_HARD_MAX))
            start_level = max(0, min(start_level, max_level))

            if skill.max_level != max_level:
                self._save.set_skill_max(skill, max_level)
                changes += 1
            if skill.level != start_level:
                self._save.set_skill_level(skill, start_level)
                changes += 1
        self._populate_skills(self._current_char)
        if changes:
            self.status_message.emit(f"Applied {preset} preset (unsaved).")
        else:
            self.status_message.emit(f"{preset} already satisfied (no changes).")

    def _on_attr_spin_changed(self, attr, pip_lbl: QLabel, value: int) -> None:
        self._on_attribute_changed(attr, value)
        pip_lbl.setText(_pip_html(value, 10))

    def _populate_traits(self, char: Character) -> None:
        self._traits_list.clear()
        for trait in sorted(
            char.traits,
            key=lambda t: game_texts.get(TRAIT_TEXT_IDS.get(t.trait_id, 0), t.name),
        ):
            display = game_texts.get(TRAIT_TEXT_IDS.get(trait.trait_id, 0), trait.name)
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, trait)
            self._traits_list.addItem(item)

    def _populate_conditions(self, char: Character) -> None:
        self._conditions_list.clear()
        for cond in sorted(
            char.conditions,
            key=lambda c: game_texts.get(CONDITION_TEXT_IDS.get(c.cond_id, 0), c.name),
        ):
            display = game_texts.get(CONDITION_TEXT_IDS.get(cond.cond_id, 0), cond.name)
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, cond)
            self._conditions_list.addItem(item)

    def _populate_relationships(self, char: Character) -> None:
        self._rel_table.setRowCount(0)
        for rel in sorted(char.relationships, key=lambda r: r.target_name):
            row = self._rel_table.rowCount()
            self._rel_table.insertRow(row)
            self._rel_table.setItem(row, 0, QTableWidgetItem(rel.target_name))

            for col, value, setter in [
                (1, rel.friendship, self._save.set_friendship if self._save else None),
                (2, rel.attraction, self._save.set_attraction if self._save else None),
                (
                    3,
                    rel.compatibility,
                    self._save.set_compatibility if self._save else None,
                ),
            ]:
                edit = QLineEdit(str(value))
                edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

                def _make_handler(e=edit, r=rel, s=setter):
                    def _on_editing_finished():
                        if s is None:
                            return
                        try:
                            v = int(e.text())
                        except ValueError:
                            return
                        s(r, v)
                        self.status_message.emit("Relationships applied (unsaved).")

                    return _on_editing_finished

                edit.editingFinished.connect(_make_handler())
                self._rel_table.setCellWidget(row, col, edit)

    def _populate_jobs(self, char: Character) -> None:
        pers = char.element.find("pers")

        # Backstory combo
        bsid = self._parse_int(pers.get("bsid") if pers is not None else None, 1776)
        self._backstory_combo.blockSignals(True)
        idx = self._backstory_combo.findData(bsid)
        if idx >= 0:
            self._backstory_combo.setCurrentIndex(idx)
        else:
            self._backstory_combo.setCurrentIndex(0)
        self._backstory_combo.blockSignals(False)

        # Job priorities
        priorities: dict[str, str] = {}
        js_el = pers.find("jobsetting") if pers is not None else None
        if js_el is not None:
            for j in js_el.findall("j"):
                prof = j.get("profession")
                prio = j.get("priority")
                if prof and prio:
                    priorities[prof] = prio

        for row in range(self._job_table.rowCount()):
            profession = self._job_table.item(row, 0).text()
            combo = self._job_table.cellWidget(row, 1)
            if isinstance(combo, QComboBox):
                combo.blockSignals(True)
                combo.setCurrentText(priorities.get(profession, "Normal"))
                combo.blockSignals(False)

    def _populate_behavior(self, char: Character) -> None:
        self._task_combo.blockSignals(True)
        self._task_combo.setCurrentText(char.element.get("task", "Walk"))
        self._task_combo.blockSignals(False)

        ai_el = char.element.find("ai")
        ai_defaults = {
            "bts": 100,
            "suitOn": 0,
            "bstx": -1,
            "bsty": -1,
            "bstsh": 0,
            "hsid": char.ship_sid,
            "rest": 0,
        }
        for key, spin in self._ai_spins.items():
            spin.blockSignals(True)
            spin.setValue(self._int_attr(ai_el, key, ai_defaults.get(key, 0)))
            spin.blockSignals(False)

        pers = char.element.find("pers")
        for key, spin in self._pers_spins.items():
            spin.blockSignals(True)
            spin.setValue(self._int_attr(pers, key, spin.minimum()))
            spin.blockSignals(False)

        self._use_global_check.blockSignals(True)
        use_global = pers.get("useGlobal", "false") if pers is not None else "false"
        self._use_global_check.setChecked(use_global == "true")
        self._use_global_check.blockSignals(False)

    def _populate_schedule(self, char: Character) -> None:
        pers = char.element.find("pers")
        sched = pers.find("schedule") if pers is not None else None
        sec = pers.find("sec") if pers is not None else None

        defaults = {
            "p0": DEFAULT_SCHEDULE_P0,
            "p1": DEFAULT_SCHEDULE_P1,
            "p2": DEFAULT_SCHEDULE_P2,
            "s0": DEFAULT_SEC_S0,
            "s1": DEFAULT_SEC_S1,
            "s2": DEFAULT_SEC_S2,
        }
        for key, edit in self._mask_edits.items():
            if key.startswith("p") and sched is not None:
                value = sched.get(key, defaults[key])
            elif key.startswith("s") and sec is not None:
                value = sec.get(key, defaults[key])
            else:
                value = defaults[key]
            edit.blockSignals(True)
            edit.setText(value)
            edit.blockSignals(False)
            self._update_mask_binary_label(key, value)

    def _populate_appearance(self, char: Character) -> None:
        colors = char.element.find("colors")
        for key, control in self._appearance_controls.items():
            if key in {"glovesOff", "longSleeve"}:
                if isinstance(control, QCheckBox):
                    control.blockSignals(True)
                    control.setChecked(
                        (colors.get(key, "false") if colors is not None else "false")
                        == "true"
                    )
                    control.blockSignals(False)
                continue

            source = (
                colors
                if key
                in {
                    "pantsSet",
                    "shirtSet",
                    "skinSet",
                    "sp",
                    "ss",
                    "sr",
                    "sh",
                    "ssh",
                    "sg",
                    "sl",
                }
                else char.element
            )
            raw = source.get(key, "0") if source is not None else "0"
            if isinstance(control, QComboBox):
                control.blockSignals(True)
                control.setCurrentText(raw)
                control.blockSignals(False)
            elif isinstance(control, QSpinBox):
                control.blockSignals(True)
                control.setValue(self._parse_int(raw, 0))
                control.blockSignals(False)

    def _populate_loadout(self, char: Character) -> None:
        loadout = char.element.find("loadout")
        for key, spin in self._loadout_spins.items():
            spin.blockSignals(True)
            value = loadout.get(key, "0") if loadout is not None else "0"
            spin.setValue(self._parse_int(value, 0))
            spin.blockSignals(False)
        for key, check in self._loadout_checks.items():
            check.blockSignals(True)
            value = loadout.get(key, "false") if loadout is not None else "false"
            check.setChecked(value == "true")
            check.blockSignals(False)

    def _populate_identity(self, char: Character) -> None:
        self._cid_combo.blockSignals(True)
        self._cid_combo.setCurrentText(char.element.get("cid", "89"))
        self._cid_combo.blockSignals(False)

        self._side_combo.blockSignals(True)
        self._side_combo.setCurrentText(char.element.get("side", "Player"))
        self._side_combo.blockSignals(False)

        self._fac_spin.blockSignals(True)
        self._fac_spin.setValue(self._parse_int(char.element.get("fac", "0"), 0))
        self._fac_spin.blockSignals(False)

        self._dir_combo.blockSignals(True)
        self._dir_combo.setCurrentText(char.element.get("dir", "D1"))
        self._dir_combo.blockSignals(False)

    def _clear_new_tabs(self) -> None:
        self._task_combo.setCurrentText("Walk")
        for spin in self._ai_spins.values():
            spin.setValue(0)
        for spin in self._pers_spins.values():
            spin.setValue(0)
        self._use_global_check.setChecked(False)
        # Reset backstory to Teacher (default for new characters)
        idx = self._backstory_combo.findData(1776)
        if idx >= 0:
            self._backstory_combo.setCurrentIndex(idx)
        for row in range(self._job_table.rowCount()):
            combo = self._job_table.cellWidget(row, 1)
            if isinstance(combo, QComboBox):
                combo.setCurrentText("Normal")
        for key, edit in self._mask_edits.items():
            edit.setText("0")
            self._update_mask_binary_label(key, "0")
        for control in self._appearance_controls.values():
            if isinstance(control, QCheckBox):
                control.setChecked(False)
            elif isinstance(control, QComboBox):
                control.setCurrentIndex(0)
            elif isinstance(control, QSpinBox):
                control.setValue(0)
        for spin in self._loadout_spins.values():
            spin.setValue(0)
        for check in self._loadout_checks.values():
            check.setChecked(False)
        self._cid_combo.setCurrentText("89")
        self._side_combo.setCurrentText("Player")
        self._fac_spin.setValue(0)
        self._dir_combo.setCurrentText("D1")

    @staticmethod
    def _parse_int(raw: str | None, fallback: int) -> int:
        if raw is None:
            return fallback
        try:
            return int(raw)
        except ValueError:
            return fallback

    def _int_attr(self, el, key: str, fallback: int) -> int:
        if el is None:
            return fallback
        return self._parse_int(el.get(key), fallback)

    @staticmethod
    def _ensure_child(parent, tag: str):
        child = parent.find(tag)
        if child is None:
            child = etree.SubElement(parent, tag)
        return child

    def _ensure_pers(self, char: Character):
        pers = char.element.find("pers")
        if pers is None:
            pers = self._ensure_child(char.element, "pers")
        return pers

    def _on_task_changed(self, text: str) -> None:
        self._set_char_attr("task", text)

    def _on_ai_field_changed(self, key: str, value: int) -> None:
        if self._current_char is None:
            return
        ai_el = self._ensure_child(self._current_char.element, "ai")
        ai_el.set(key, str(value))
        self.status_message.emit("AI settings applied (unsaved).")

    def _on_pers_field_changed(self, key: str, value: str) -> None:
        if self._current_char is None:
            return
        pers = self._ensure_pers(self._current_char)
        pers.set(key, value)
        self.status_message.emit("Personality settings applied (unsaved).")

    def _on_use_global_toggled(self, on: bool) -> None:
        self._on_pers_field_changed("useGlobal", "true" if on else "false")

    # ------------------------------------------------------------------
    # Language change
    # ------------------------------------------------------------------

    def _on_lang_changed(self, _lang: str) -> None:
        """Refresh all translatable combo boxes and the current character display."""
        self._refresh_backstory_combo()
        self._refresh_traits_combo()
        if self._current_char is not None:
            self._populate_attributes(self._current_char)
            self._populate_skills(self._current_char)
            self._populate_traits(self._current_char)
            self._populate_conditions(self._current_char)

    def _refresh_backstory_combo(self) -> None:
        """Re-populate the backstory combo with names in the current language."""
        current_data = self._backstory_combo.currentData()
        self._backstory_combo.blockSignals(True)
        self._backstory_combo.clear()
        for bs_id, bs_name in sorted(
            BACKSTORY_IDS.items(),
            key=lambda x: game_texts.get(BACKSTORY_TEXT_IDS.get(x[0], 0), x[1]),
        ):
            self._backstory_combo.addItem(
                game_texts.get(BACKSTORY_TEXT_IDS.get(bs_id, 0), bs_name), bs_id
            )
        # Restore the previously selected backstory ID
        if current_data is not None:
            idx = next(
                (i for i in range(self._backstory_combo.count())
                 if self._backstory_combo.itemData(i) == current_data),
                0,
            )
            self._backstory_combo.setCurrentIndex(idx)
        self._backstory_combo.blockSignals(False)

    def _refresh_traits_combo(self) -> None:
        """Re-populate the traits picker combo with names in the current language."""
        current_data = self._add_trait_combo.currentData()
        self._add_trait_combo.blockSignals(True)
        self._add_trait_combo.clear()
        for trait_id, en_name in sorted(
            TRAIT_IDS.items(),
            key=lambda x: game_texts.get(TRAIT_TEXT_IDS.get(x[0], 0), x[1]),
        ):
            self._add_trait_combo.addItem(
                game_texts.get(TRAIT_TEXT_IDS.get(trait_id, 0), en_name), trait_id
            )
        if current_data is not None:
            idx = next(
                (i for i in range(self._add_trait_combo.count())
                 if self._add_trait_combo.itemData(i) == current_data),
                0,
            )
            self._add_trait_combo.setCurrentIndex(idx)
        self._add_trait_combo.blockSignals(False)

    def _on_backstory_changed(self, index: int) -> None:
        if self._current_char is None:
            return
        bs_id = self._backstory_combo.itemData(index)
        if bs_id is None:
            return
        pers = self._ensure_pers(self._current_char)
        pers.set("bsid", str(bs_id))
        self.status_message.emit("Backstory applied (unsaved).")

    def _on_job_priority_changed(self, profession: str, priority: str) -> None:
        if self._current_char is None:
            return
        pers = self._ensure_pers(self._current_char)
        js_el = pers.find("jobsetting")
        if js_el is None:
            js_el = self._ensure_child(pers, "jobsetting")
        target = None
        for j in js_el.findall("j"):
            if j.get("profession") == profession:
                target = j
                break
        if target is None:
            target = etree.SubElement(js_el, "j")
            target.set("profession", profession)
        target.set("priority", priority)
        self.status_message.emit("Job priorities applied (unsaved).")

    def _on_mask_edited(self, key: str, edit: QLineEdit) -> None:
        value = edit.text().strip()
        if not value:
            return
        if self._set_mask_value(key, value):
            self._update_mask_binary_label(key, value)
            self.status_message.emit("Bitmasks applied (unsaved).")
        else:
            QMessageBox.warning(self, "Invalid Bitmask", f"{key} must be an integer.")

    def _set_mask_value(self, key: str, value: str) -> bool:
        if self._current_char is None:
            return False
        try:
            int(value)
        except ValueError:
            return False
        pers = self._ensure_pers(self._current_char)
        tag = "schedule" if key.startswith("p") else "sec"
        node = pers.find(tag)
        if node is None:
            node = self._ensure_child(pers, tag)
        node.set(key, value)
        return True

    def _update_mask_binary_label(self, key: str, value: str) -> None:
        label = self._mask_binary_labels.get(key)
        if label is None:
            return
        try:
            parsed = int(value)
            label.setText(f"0b{parsed:b}")
        except ValueError:
            label.setText("invalid")

    def _set_char_attr(self, key: str, value: str) -> None:
        if self._current_char is None:
            return
        self._current_char.element.set(key, value)
        if key in {"name", "lname"}:
            self._avatar.set_character(
                self._current_char.element.get("name", ""),
                self._current_char.element.get("lname", ""),
            )
        self.status_message.emit("Identity/appearance applied (unsaved).")

    def _set_colors_attr(self, key: str, value: str) -> None:
        if self._current_char is None:
            return
        colors = self._ensure_child(self._current_char.element, "colors")
        colors.set(key, value)
        self.status_message.emit("Appearance applied (unsaved).")

    def _set_loadout_attr(self, key: str, value: str) -> None:
        if self._current_char is None:
            return
        loadout = self._ensure_child(self._current_char.element, "loadout")
        loadout.set(key, value)
        self.status_message.emit("Loadout applied (unsaved).")

    def _randomize_appearance(self) -> None:
        if self._current_char is None:
            return
        self._set_char_attr("bb", random.choice(["m", "f"]))
        self._set_char_attr("bh", random.choice(["m", "f"]))
        self._set_char_attr("bs", str(random.randint(1, 2)))
        self._set_char_attr("bp", str(random.randint(1, 2)))
        for key in ("sp", "ss", "sr", "sh", "ssh", "sg", "sl"):
            self._set_colors_attr(key, str(random.randint(0, 5)))
        self._populate_appearance(self._current_char)
        self.status_message.emit("Appearance randomized (unsaved).")

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

    def _normalize_relationships(self) -> None:
        if self._save is None or self._current_char is None:
            return
        for rel in self._current_char.relationships:
            self._save.set_friendship(rel, 0)
            self._save.set_attraction(rel, 0)
            self._save.set_compatibility(rel, 50)
        self._populate_relationships(self._current_char)
        self.status_message.emit("Relationships normalized (unsaved).")

    def _rename_character(self) -> None:
        if self._save is None or self._current_char is None:
            return
        first = self._first_name_edit.text().strip()
        last = self._last_name_edit.text().strip()
        if not first:
            QMessageBox.warning(self, "Rename", "First name cannot be empty.")
            return
        self._save.rename_character(self._current_char, first, last)
        self._avatar.set_character(first, last)
        # Find, re-label, and re-sort the crew list item
        old_row = -1
        for i in range(self._crew_list.count()):
            if (
                self._crew_list.item(i).data(Qt.ItemDataRole.UserRole)
                is self._current_char
            ):
                old_row = i
                break
        if old_row != -1:
            self._crew_list.blockSignals(True)
            item = self._crew_list.takeItem(old_row)
            item.setText(self._current_char.full_name)
            # Binary-search insertion point to maintain sort order
            new_row = self._crew_list.count()
            for i in range(self._crew_list.count()):
                if self._current_char.full_name <= self._crew_list.item(i).text():
                    new_row = i
                    break
            self._crew_list.insertItem(new_row, item)
            self._crew_list.setCurrentRow(new_row)
            self._crew_list.blockSignals(False)
        self.status_message.emit("Character renamed (unsaved).")

    def _add_trait(self) -> None:
        if self._save is None or self._current_char is None:
            return
        trait_id: int = self._add_trait_combo.currentData()
        trait = self._save.add_trait(self._current_char, trait_id)
        if trait is None:
            QMessageBox.information(self, "Add Trait", "That trait is already present.")
            return
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

    def _add_crew_item(
        self, char: Character, row: int | None = None
    ) -> QListWidgetItem:
        """Create a crew list entry. If row is specified, insert at that index; otherwise append."""
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
            spin.blockSignals(True)
            spin.setValue(0)
            spin.blockSignals(False)
        for spin in self._gas_spins.values():
            spin.blockSignals(True)
            spin.setValue(0)
            spin.blockSignals(False)
        self._attr_table.setRowCount(0)
        self._skills_table.setRowCount(0)
        self._traits_list.clear()
        self._conditions_list.clear()
        self._rel_table.setRowCount(0)
        self._clear_new_tabs()

    def _set_right_enabled(self, enabled: bool) -> None:
        self._first_name_edit.setEnabled(enabled)
        self._last_name_edit.setEnabled(enabled)
        self._tabs.setEnabled(enabled)

    def _set_advanced_tabs_visible(self, visible: bool) -> None:
        bar = self._tabs.tabBar()
        for idx in range(self._tabs.count()):
            name = self._tabs.tabText(idx)
            if name in self._advanced_tab_names:
                bar.setTabVisible(idx, visible)

        # Force a geometry pass so visible tabs re-expand/re-squash immediately.
        bar.updateGeometry()
        self._tabs.updateGeometry()
        self._tabs.repaint()

    def refresh_current_char(self) -> None:
        """Re-populate the character detail panel for the currently selected character."""
        if self._current_char is not None:
            self._populate_character(self._current_char)

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
        crew = [
            c for c in self._save.characters if c.ship_sid == self._current_ship.sid
        ]
        crew.sort(key=lambda c: c.full_name)
        idx = crew.index(char)
        self._add_crew_item(char, row=idx)
        self._crew_count.setText(str(self._crew_list.count()))
        self._crew_list.setCurrentRow(idx)
        self.crew_changed.emit()
        self.status_message.emit(f"Crew member '{char.full_name}' added (unsaved).")

    def _remove_crew_member_by_char(self, char: Character) -> None:
        """Remove a crew member."""
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
        self.crew_changed.emit()
        self.status_message.emit(f"'{char.full_name}' removed (unsaved).")

    @staticmethod
    def _unique_crew_name(
        first_name: str, last_name: str, existing: set[str]
    ) -> tuple[str, str]:
        """Return a collision-free (first, last) name based on the source."""
        candidate_first = f"{first_name} - Copy"
        if f"{candidate_first} {last_name}".strip() not in existing:
            return candidate_first, last_name
        n = 2
        while True:
            candidate_first = f"{first_name} - Copy {n}"
            if f"{candidate_first} {last_name}".strip() not in existing:
                return candidate_first, last_name
            n += 1

    def _clone_crew_member(self, row: int) -> None:
        if self._save is None or self._current_ship is None:
            return
        item = self._crew_list.item(row)
        if item is None:
            return
        source: Character = item.data(Qt.ItemDataRole.UserRole)
        existing = {
            self._crew_list.item(i).text()
            for i in range(self._crew_list.count())
            if self._crew_list.item(i)
        }
        new_first, new_last = self._unique_crew_name(
            source.first_name, source.last_name, existing
        )
        try:
            char = self._save.clone_character(
                source, self._current_ship, new_first, new_last
            )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Failed to clone crew member:\n{exc}")
            return
        crew = [
            c for c in self._save.characters if c.ship_sid == self._current_ship.sid
        ]
        crew.sort(key=lambda c: c.full_name)
        idx = crew.index(char)
        self._add_crew_item(char, row=idx)
        self._crew_count.setText(str(self._crew_list.count()))
        self._crew_list.setCurrentRow(idx)
        self.crew_changed.emit()
        self.status_message.emit(f"'{char.full_name}' cloned (unsaved).")
