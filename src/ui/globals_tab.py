"""globals_tab.py – Tab for editing game-wide settings."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
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

        name_lbl = QLabel(label)
        name_lbl.setObjectName("StatCardLabel")
        layout.addWidget(name_lbl)

        self.spin = QSpinBox()
        self.spin.setRange(0, 2_000_000_000)
        self.spin.setObjectName("StatCardSpin")
        layout.addWidget(self.spin)

        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("StatCardDesc")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)


class GlobalsTab(QWidget):
    status_message = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save: SaveFile | None = None
        self._build_ui()

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

        # ── Page title ───────────────────────────────────────────────
        title = QLabel("Overview")
        title.setObjectName("TabTitle")
        root.addWidget(title)

        root.addWidget(_sep())

        # ── Save file info (read-only) ────────────────────────────────
        info_group = QGroupBox("Save File")
        info_grid = QGridLayout(info_group)
        info_grid.setContentsMargins(16, 20, 16, 16)
        info_grid.setHorizontalSpacing(24)
        info_grid.setVerticalSpacing(14)
        info_grid.setColumnStretch(1, 1)
        info_grid.setColumnStretch(3, 1)

        self._info_labels: dict[str, QLabel] = {}

        def _add_info(r: int, c: int, key: str, label: str) -> None:
            k = QLabel(label)
            k.setObjectName("InfoKey")
            v = QLabel("—")
            v.setObjectName("InfoValue")
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            info_grid.addWidget(k, r, c * 2)
            info_grid.addWidget(v, r, c * 2 + 1)
            self._info_labels[key] = v

        _add_info(0, 0, "mode",  "Game Mode")
        _add_info(0, 1, "seed",  "Seed")
        _add_info(1, 0, "ships", "Ships")
        _add_info(1, 1, "crew",  "Total Crew")

        # Save path spans full width
        path_key = QLabel("Save Path")
        path_key.setObjectName("InfoKey")
        self._info_labels["path"] = QLabel("—")
        self._info_labels["path"].setObjectName("InfoValue")
        self._info_labels["path"].setWordWrap(True)
        self._info_labels["path"].setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        info_grid.addWidget(path_key, 2, 0)
        info_grid.addWidget(self._info_labels["path"], 2, 1, 1, 3)

        root.addWidget(info_group)

        # ── Resources (editable cards) ────────────────────────────────
        res_group = QGroupBox("Resources")
        res_grid = QGridLayout(res_group)
        res_grid.setContentsMargins(16, 20, 16, 16)
        res_grid.setSpacing(16)

        self._credits_card = _EditCard(
            "Player Credits",
            "The credits balance held in your player account.",
        )
        self._credits_card.spin.setSingleStep(1000)
        res_grid.addWidget(self._credits_card, 0, 0)

        self._prestige_card = _EditCard(
            "Prestige Points",
            "Prestige accumulated through gameplay achievements.",
        )
        self._prestige_card.spin.setSingleStep(100)
        res_grid.addWidget(self._prestige_card, 0, 1)

        res_grid.setColumnStretch(0, 1)
        res_grid.setColumnStretch(1, 1)
        root.addWidget(res_group)

        # ── Difficulty ────────────────────────────────────────────────
        diff_group = QGroupBox("Difficulty")
        diff_layout = QVBoxLayout(diff_group)
        diff_layout.setContentsMargins(16, 16, 16, 16)
        diff_layout.setSpacing(10)

        self._sandbox_check = QCheckBox("Enable Sandbox Mode")
        self._sandbox_check.setObjectName("SandboxCheck")
        diff_layout.addWidget(self._sandbox_check)

        sandbox_desc = QLabel(
            "Sandbox mode removes some of the survival pressure, letting you explore "
            "and build at your own pace without risk of crew starvation or hull collapse."
        )
        sandbox_desc.setObjectName("StatCardDesc")
        sandbox_desc.setWordWrap(True)
        diff_layout.addWidget(sandbox_desc)

        root.addWidget(diff_group)

        # ── Quick Actions ──────────────────────────────────────────────
        root.addWidget(_sep())

        qa_group = QGroupBox("Quick Actions")
        qa_layout = QVBoxLayout(qa_group)
        qa_layout.setContentsMargins(16, 16, 16, 16)
        qa_layout.setSpacing(10)

        def _action_row(label: str, desc: str, btn_text: str, slot) -> QHBoxLayout:
            row = QHBoxLayout()
            row.setSpacing(12)
            text_col = QVBoxLayout()
            text_col.setSpacing(2)
            lbl = QLabel(label)
            lbl.setObjectName("StatCardLabel")
            text_col.addWidget(lbl)
            d = QLabel(desc)
            d.setObjectName("StatCardDesc")
            text_col.addWidget(d)
            row.addLayout(text_col)
            row.addStretch()
            btn = QPushButton(btn_text)
            btn.setObjectName("InlineButton")
            btn.setFixedWidth(140)
            btn.clicked.connect(slot)
            row.addWidget(btn)
            return row

        qa_layout.addLayout(_action_row(
            "Heal All Crew",
            "Set every stat (health, food, rest…) to 100 for all crew members.",
            "Heal All",
            self._qa_heal_all,
        ))
        qa_layout.addWidget(_sep())
        qa_layout.addLayout(_action_row(
            "Max All Skills",
            "Set all crew skills to level 20 and max natural level 20.",
            "Max Skills",
            self._qa_max_skills,
        ))
        qa_layout.addWidget(_sep())
        qa_layout.addLayout(_action_row(
            "Clear All Conditions",
            "Remove every active condition from all crew (injuries, moods, etc.).",
            "Clear Conditions",
            self._qa_clear_conditions,
        ))
        qa_layout.addWidget(_sep())

        fill_row = QHBoxLayout()
        fill_row.setSpacing(12)
        fill_text = QVBoxLayout()
        fill_text.setSpacing(2)
        fill_lbl = QLabel("Fill All Storage")
        fill_lbl.setObjectName("StatCardLabel")
        fill_text.addWidget(fill_lbl)
        fill_desc = QLabel("Set every item in every storage container to the specified quantity.")
        fill_desc.setObjectName("StatCardDesc")
        fill_text.addWidget(fill_desc)
        fill_row.addLayout(fill_text)
        fill_row.addStretch()
        self._fill_qty_spin = QSpinBox()
        self._fill_qty_spin.setRange(1, 1_000_000)
        self._fill_qty_spin.setValue(9999)
        self._fill_qty_spin.setFixedWidth(90)
        fill_row.addWidget(self._fill_qty_spin)
        fill_btn = QPushButton("Fill Storage")
        fill_btn.setObjectName("InlineButton")
        fill_btn.setFixedWidth(140)
        fill_btn.clicked.connect(self._qa_fill_storage)
        fill_row.addWidget(fill_btn)
        qa_layout.addLayout(fill_row)

        root.addWidget(qa_group)

        # Wire auto-apply
        self._credits_card.spin.valueChanged.connect(self._apply)
        self._prestige_card.spin.valueChanged.connect(self._apply)
        self._sandbox_check.stateChanged.connect(self._apply)

        self._set_enabled(False)

    # ------------------------------------------------------------------

    def _set_enabled(self, enabled: bool) -> None:
        self._credits_card.spin.setEnabled(enabled)
        self._prestige_card.spin.setEnabled(enabled)
        self._sandbox_check.setEnabled(enabled)
        self._fill_qty_spin.setEnabled(enabled)

    def load(self, save: SaveFile) -> None:
        self._save = save
        for w in (self._credits_card.spin, self._prestige_card.spin, self._sandbox_check):
            w.blockSignals(True)
        self._credits_card.spin.setValue(save.get_credits())
        self._prestige_card.spin.setValue(save.get_prestige())
        self._sandbox_check.setChecked(save.get_sandbox())
        for w in (self._credits_card.spin, self._prestige_card.spin, self._sandbox_check):
            w.blockSignals(False)

        # Update info labels
        self._info_labels["mode"].setText(save.get_game_mode())
        self._info_labels["seed"].setText(save.get_seed())
        self._info_labels["ships"].setText(str(len(save.ships)))
        self._info_labels["crew"].setText(str(len(save.characters)))
        self._info_labels["path"].setText(str(save.path) if save.path else "—")

        self._set_enabled(True)

    def clear(self) -> None:
        self._save = None
        for w in (self._credits_card.spin, self._prestige_card.spin, self._sandbox_check):
            w.blockSignals(True)
        self._credits_card.spin.setValue(0)
        self._prestige_card.spin.setValue(0)
        self._sandbox_check.setChecked(False)
        for w in (self._credits_card.spin, self._prestige_card.spin, self._sandbox_check):
            w.blockSignals(False)
        for lbl in self._info_labels.values():
            lbl.setText("—")
        self._set_enabled(False)

    def _apply(self, _=None) -> None:
        if self._save is None:
            return
        self._save.set_credits(self._credits_card.spin.value())
        self._save.set_prestige(self._prestige_card.spin.value())
        self._save.set_sandbox(self._sandbox_check.isChecked())
        self.status_message.emit("Changes applied (unsaved).")

    # ------------------------------------------------------------------
    # Quick actions
    # ------------------------------------------------------------------

    def _qa_heal_all(self) -> None:
        if self._save is None:
            return
        n = self._save.heal_all_crew()
        self.status_message.emit(f"Healed {n} crew members (unsaved).")

    def _qa_max_skills(self) -> None:
        if self._save is None:
            return
        n = self._save.max_all_skills()
        self.status_message.emit(f"Maxed {n} skills across all crew (unsaved).")

    def _qa_clear_conditions(self) -> None:
        if self._save is None:
            return
        n = self._save.clear_all_conditions()
        self.status_message.emit(f"Cleared conditions from {n} crew members (unsaved).")

    def _qa_fill_storage(self) -> None:
        if self._save is None:
            return
        qty = self._fill_qty_spin.value()
        n = self._save.fill_all_storage(qty)
        self.status_message.emit(f"Set {n} storage items to {qty:,} (unsaved).")


