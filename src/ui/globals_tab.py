"""globals_tab.py - Tab for editing game-wide settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.save_file import SaveFile


_RESOURCE_SPIN_MAX: int = 2_000_000_000  # upper bound for credits / prestige spins
_FILL_QTY_DEFAULT: int = 9_999  # default quantity for the Fill Storage action
_FILL_QTY_MAX: int = 1_000_000  # maximum quantity for the Fill Storage spin


def _sep() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setObjectName("Separator")
    return line


class _EditCard(QWidget):
    """A labeled SpinBox displayed as an editable card."""

    def __init__(self, label: str, description: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StatCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        self.name_lbl = QLabel(label)
        self.name_lbl.setObjectName("StatCardLabel")
        layout.addWidget(self.name_lbl)

        self.spin = QSpinBox()
        self.spin.setRange(0, _RESOURCE_SPIN_MAX)
        self.spin.setObjectName("StatCardSpin")
        layout.addWidget(self.spin)

        self.desc_lbl = QLabel(description)
        self.desc_lbl.setObjectName("StatCardDesc")
        self.desc_lbl.setWordWrap(True)
        layout.addWidget(self.desc_lbl)


class GlobalsTab(QWidget):
    status_message = Signal(str)
    crew_data_changed = Signal()
    storage_data_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._build_ui()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    def _build_ui(self) -> None:
        # Scrollable page
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("GlobalsScroll")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)
        root = QVBoxLayout(page)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(22)

        # Page title
        self._title_lbl = QLabel()
        self._title_lbl.setObjectName("TabTitle")
        root.addWidget(self._title_lbl)

        root.addWidget(_sep())

        # Save file info (read-only)
        self._info_group = QGroupBox()
        info_grid = QGridLayout(self._info_group)
        info_grid.setContentsMargins(16, 20, 16, 16)
        info_grid.setHorizontalSpacing(24)
        info_grid.setVerticalSpacing(14)
        info_grid.setColumnStretch(1, 1)
        info_grid.setColumnStretch(3, 1)

        self._info_labels: dict[str, QLabel] = {}
        self._info_key_labels: dict[str, QLabel] = {}

        def _add_info(r: int, c: int, key: str) -> None:
            k = QLabel()
            k.setObjectName("InfoKey")
            v = QLabel("—")
            v.setObjectName("InfoValue")
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            info_grid.addWidget(k, r, c * 2)
            info_grid.addWidget(v, r, c * 2 + 1)
            self._info_labels[key] = v
            self._info_key_labels[key] = k

        _add_info(0, 0, "mode")
        _add_info(0, 1, "seed")
        _add_info(1, 0, "ships")
        _add_info(1, 1, "crew")
        _add_info(2, 0, "gametime")
        _add_info(2, 1, "sectors")
        _add_info(3, 0, "savedate")
        _add_info(3, 1, "systems")

        # Save path spans full width
        self._path_key_lbl = QLabel()
        self._path_key_lbl.setObjectName("InfoKey")
        self._info_labels["path"] = QLabel("—")
        self._info_labels["path"].setObjectName("InfoValue")
        self._info_labels["path"].setWordWrap(True)
        self._info_labels["path"].setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        info_grid.addWidget(self._path_key_lbl, 4, 0)
        info_grid.addWidget(self._info_labels["path"], 4, 1, 1, 3)

        root.addWidget(self._info_group)

        # Resources (editable cards)
        self._res_group = QGroupBox()
        res_grid = QGridLayout(self._res_group)
        res_grid.setContentsMargins(16, 20, 16, 16)
        res_grid.setSpacing(16)

        self._credits_card = _EditCard("", "")
        self._credits_card.spin.setSingleStep(1000)
        res_grid.addWidget(self._credits_card, 0, 0)

        self._prestige_card = _EditCard("", "")
        self._prestige_card.spin.setSingleStep(100)
        res_grid.addWidget(self._prestige_card, 0, 1)

        res_grid.setColumnStretch(0, 1)
        res_grid.setColumnStretch(1, 1)
        root.addWidget(self._res_group)

        # Difficulty
        self._diff_group = QGroupBox()
        diff_layout = QVBoxLayout(self._diff_group)
        diff_layout.setContentsMargins(16, 16, 16, 16)
        diff_layout.setSpacing(10)

        self._sandbox_check = QCheckBox()
        self._sandbox_check.setObjectName("SandboxCheck")
        diff_layout.addWidget(self._sandbox_check)

        self._sandbox_desc = QLabel()
        self._sandbox_desc.setObjectName("StatCardDesc")
        self._sandbox_desc.setWordWrap(True)
        diff_layout.addWidget(self._sandbox_desc)

        root.addWidget(self._diff_group)

        # Quick actions
        root.addWidget(_sep())

        self._qa_group = QGroupBox()
        qa_layout = QVBoxLayout(self._qa_group)
        qa_layout.setContentsMargins(16, 16, 16, 16)
        qa_layout.setSpacing(10)

        def _action_row(slot) -> tuple[QHBoxLayout, QPushButton, QLabel, QLabel]:
            row = QHBoxLayout()
            row.setSpacing(12)
            text_col = QVBoxLayout()
            text_col.setSpacing(2)
            lbl = QLabel()
            lbl.setObjectName("StatCardLabel")
            text_col.addWidget(lbl)
            d = QLabel()
            d.setObjectName("StatCardDesc")
            text_col.addWidget(d)
            row.addLayout(text_col)
            row.addStretch()
            btn = QPushButton()
            btn.setObjectName("InlineButton")
            btn.setFixedWidth(140)
            btn.clicked.connect(slot)
            row.addWidget(btn)
            return row, btn, lbl, d

        heal_row, self._heal_btn, self._heal_lbl, self._heal_desc = _action_row(
            self._heal_all_crew,
        )
        qa_layout.addLayout(heal_row)
        qa_layout.addWidget(_sep())

        skills_row, self._skills_btn, self._skills_lbl, self._skills_desc = _action_row(
            self._max_all_skills,
        )
        qa_layout.addLayout(skills_row)
        qa_layout.addWidget(_sep())

        (
            conditions_row,
            self._conditions_btn,
            self._conditions_lbl,
            self._conditions_desc,
        ) = _action_row(self._clear_all_conditions)
        qa_layout.addLayout(conditions_row)
        qa_layout.addWidget(_sep())

        fill_row = QHBoxLayout()
        fill_row.setSpacing(12)
        fill_text = QVBoxLayout()
        fill_text.setSpacing(2)
        self._fill_lbl = QLabel()
        self._fill_lbl.setObjectName("StatCardLabel")
        fill_text.addWidget(self._fill_lbl)
        self._fill_desc = QLabel()
        self._fill_desc.setObjectName("StatCardDesc")
        fill_text.addWidget(self._fill_desc)
        fill_row.addLayout(fill_text)
        fill_row.addStretch()
        self._fill_qty_spin = QSpinBox()
        self._fill_qty_spin.setRange(1, _FILL_QTY_MAX)
        self._fill_qty_spin.setValue(_FILL_QTY_DEFAULT)
        self._fill_qty_spin.setFixedWidth(90)
        fill_row.addWidget(self._fill_qty_spin)
        fill_btn = QPushButton()
        fill_btn.setObjectName("InlineButton")
        fill_btn.setFixedWidth(140)
        fill_btn.clicked.connect(self._fill_all_storage)
        fill_row.addWidget(fill_btn)
        self._fill_btn = fill_btn
        qa_layout.addLayout(fill_row)

        root.addWidget(self._qa_group)

        self._credits_card.spin.valueChanged.connect(self._apply_changes)
        self._prestige_card.spin.valueChanged.connect(self._apply_changes)
        self._sandbox_check.stateChanged.connect(self._apply_changes)

        self._set_controls_enabled(False)
        self.retranslate_ui()

    def _set_controls_enabled(self, enabled: bool) -> None:
        self._credits_card.spin.setEnabled(enabled)
        self._prestige_card.spin.setEnabled(enabled)
        self._sandbox_check.setEnabled(enabled)
        self._heal_btn.setEnabled(enabled)
        self._skills_btn.setEnabled(enabled)
        self._conditions_btn.setEnabled(enabled)
        self._fill_qty_spin.setEnabled(enabled)
        self._fill_btn.setEnabled(enabled)

    def retranslate_ui(self) -> None:
        """Update all static labels on language change."""
        self._title_lbl.setText(self.tr("Overview"))
        self._info_group.setTitle(self.tr("Save File"))
        self._res_group.setTitle(self.tr("Resources"))
        self._diff_group.setTitle(self.tr("Difficulty"))
        self._qa_group.setTitle(self.tr("Quick Actions"))

        # Info key labels
        _info_key_map = {
            "mode":     self.tr("Game Mode"),
            "seed":     self.tr("Seed"),
            "ships":    self.tr("Ships"),
            "crew":     self.tr("Crew"),
            "gametime": self.tr("Game Time"),
            "sectors":  self.tr("Sectors"),
            "savedate": self.tr("Last Saved"),
            "systems":  self.tr("Systems"),
        }
        for key, label in _info_key_map.items():
            self._info_key_labels[key].setText(label)
        self._path_key_lbl.setText(self.tr("Save Path"))

        # Resource cards
        self._credits_card.name_lbl.setText(self.tr("Credits"))
        self._credits_card.desc_lbl.setText(self.tr("Spend at traders and shipyards."))
        self._prestige_card.name_lbl.setText(self.tr("Prestige"))
        self._prestige_card.desc_lbl.setText(self.tr("Reputation across the galaxy."))

        # Difficulty
        self._sandbox_check.setText(self.tr("Sandbox mode"))
        self._sandbox_desc.setText(self.tr("Enables god mode, no resource costs, etc."))

        # Quick actions
        self._heal_lbl.setText(self.tr("Heal Crew"))
        self._heal_desc.setText(self.tr("Restore all crew to full health and remove injuries."))
        self._heal_btn.setText(self.tr("Heal All"))
        self._skills_lbl.setText(self.tr("Max Skills"))
        self._skills_desc.setText(self.tr("Set all crew skills and attributes to maximum."))
        self._skills_btn.setText(self.tr("Max All"))
        self._conditions_lbl.setText(self.tr("Clear Conditions"))
        self._conditions_desc.setText(self.tr("Remove all conditions from every crew member."))
        self._conditions_btn.setText(self.tr("Clear All"))
        self._fill_lbl.setText(self.tr("Fill Storage"))
        self._fill_desc.setText(self.tr("Add items to all storage containers on a ship."))
        self._fill_btn.setText(self.tr("Fill"))

    def load(self, save: SaveFile) -> None:
        self._save = save
        for w in (
            self._credits_card.spin,
            self._prestige_card.spin,
            self._sandbox_check,
        ):
            w.blockSignals(True)
        self._credits_card.spin.setValue(save.get_credits())
        self._prestige_card.spin.setValue(save.get_prestige())
        self._sandbox_check.setChecked(save.get_sandbox())
        for w in (
            self._credits_card.spin,
            self._prestige_card.spin,
            self._sandbox_check,
        ):
            w.blockSignals(False)

        self._info_labels["mode"].setText(save.get_game_mode())
        self._info_labels["seed"].setText(save.get_seed())
        self._info_labels["ships"].setText(str(len(save.ships)))
        self._info_labels["crew"].setText(str(len(save.characters)))
        self._info_labels["gametime"].setText(save.get_game_time_str())
        self._info_labels["sectors"].setText(
            str(len(save.sectors)) if save.sectors else "—"
        )
        self._info_labels["savedate"].setText(save.get_real_date_str())
        self._info_labels["systems"].setText(str(save.get_star_system_count()))
        self._info_labels["path"].setText(
            str(save.folder) if save.folder else str(save.path) if save.path else "—"
        )

        self._set_controls_enabled(True)

    def clear(self) -> None:
        self._save = None
        for w in (
            self._credits_card.spin,
            self._prestige_card.spin,
            self._sandbox_check,
        ):
            w.blockSignals(True)
        self._credits_card.spin.setValue(0)
        self._prestige_card.spin.setValue(0)
        self._sandbox_check.setChecked(False)
        for w in (
            self._credits_card.spin,
            self._prestige_card.spin,
            self._sandbox_check,
        ):
            w.blockSignals(False)
        for lbl in self._info_labels.values():
            lbl.setText("—")
        self._set_controls_enabled(False)

    def _apply_changes(self, _=None) -> None:
        if self._save is None:
            return
        self._save.set_credits(self._credits_card.spin.value())
        self._save.set_prestige(self._prestige_card.spin.value())
        self._save.set_sandbox(self._sandbox_check.isChecked())
        self.status_message.emit("Changes applied (unsaved).")

    # ------------------------------------------------------------------
    # Quick actions
    # ------------------------------------------------------------------

    def _heal_all_crew(self) -> None:
        if self._save is None:
            return
        n = self._save.heal_all_crew()
        self.crew_data_changed.emit()
        self.status_message.emit(f"Healed {n} crew members (unsaved).")

    def _max_all_skills(self) -> None:
        if self._save is None:
            return
        n = self._save.max_all_skills()
        self.crew_data_changed.emit()
        self.status_message.emit(f"Maxed {n} skills across all crew (unsaved).")

    def _clear_all_conditions(self) -> None:
        if self._save is None:
            return
        n = self._save.clear_all_conditions()
        self.crew_data_changed.emit()
        self.status_message.emit(f"Cleared conditions from {n} crew members (unsaved).")

    def _fill_all_storage(self) -> None:
        if self._save is None:
            return
        qty = self._fill_qty_spin.value()
        n = self._save.fill_all_storage(qty)
        self.storage_data_changed.emit()
        self.status_message.emit(f"Set {n} storage items to {qty:,} (unsaved).")
