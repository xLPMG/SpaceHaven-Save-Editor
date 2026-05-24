"""Space Haven Save Editor – entry point."""
from __future__ import annotations

import sys

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def _apply_dark_palette(app: QApplication) -> None:
    """Apply a deep-space HUD color palette to the application."""
    app.setStyle("Fusion")
    palette = QPalette()

    base        = QColor("#030d1a")   # void black
    surface     = QColor("#061428")   # deep space
    overlay     = QColor("#0a1e38")   # panel surface
    text        = QColor("#e2f0ff")   # starlight white
    subtext     = QColor("#6ea8d4")   # dim blue
    accent      = QColor("#00cfff")   # electric cyan
    accent_dark = QColor("#0095bb")   # darker cyan
    danger      = QColor("#ff3366")   # alert red
    highlight   = QColor("#0e2847")   # selection bg

    palette.setColor(QPalette.ColorRole.Window, surface)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, overlay)
    palette.setColor(QPalette.ColorRole.ToolTipBase, overlay)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, overlay)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.BrightText, danger)
    palette.setColor(QPalette.ColorRole.Link, accent)
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, base)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, subtext)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, subtext)

    app.setPalette(palette)

    app.setStyleSheet("""
        /* ── Base ────────────────────────────────────────────── */
        QMainWindow, QDialog, QWidget {
            background-color: #061428;
            font-size: 13px;
        }

        /* ── Menu bar ────────────────────────────────────────── */
        QMenuBar {
            background-color: #030d1a;
            color: #e2f0ff;
            border-bottom: 1px solid rgba(0,207,255,0.18);
            padding: 2px 4px;
        }
        QMenuBar::item:selected {
            background-color: #0a1e38;
            border-radius: 4px;
        }
        QMenu {
            background-color: #030d1a;
            color: #e2f0ff;
            border: 1px solid rgba(0,207,255,0.2);
            border-radius: 6px;
            padding: 4px;
        }
        QMenu::item {
            padding: 5px 22px 5px 12px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: rgba(0,207,255,0.1);
            color: #00cfff;
        }
        QMenu::separator {
            height: 1px;
            background: rgba(0,207,255,0.12);
            margin: 4px 8px;
        }

        /* ── Editor page ─────────────────────────────────────── */
        QWidget#EditorPage {
            background-color: #030d1a;
        }

        /* ── File bar ────────────────────────────────────────── */
        QWidget#FileBar {
            background-color: #030d1a;
            border-bottom: 1px solid rgba(0,207,255,0.25);
        }
        QLabel#FileLabel {
            color: #6ea8d4;
            font-size: 12px;
        }
        QLabel#UnsavedBadge {
            color: #ffa040;
            font-size: 11px;
            font-weight: bold;
            padding: 1px 7px;
            background-color: rgba(255,160,64,0.12);
            border-radius: 8px;
        }
        QPushButton#SaveButton {
            background-color: #00cfff;
            color: #030d1a;
            border: none;
            border-radius: 6px;
            padding: 6px 18px;
            font-weight: bold;
        }
        QPushButton#SaveButton:hover {
            background-color: #33daff;
        }
        QPushButton#SaveButton:pressed {
            background-color: #0095bb;
        }
        QPushButton#FileBarButton {
            background-color: transparent;
            color: #6ea8d4;
            border: 1px solid rgba(0,207,255,0.2);
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton#FileBarButton:hover {
            background-color: rgba(0,207,255,0.08);
            border-color: #00cfff;
            color: #00cfff;
        }

        /* ── Sidebar navigation ──────────────────────────────── */
        QWidget#Sidebar {
            background-color: #030d1a;
        }
        QWidget#SidebarContainer {
            background-color: #030d1a;
        }
        QFrame#SidebarSep {
            color: rgba(0,207,255,0.15);
            max-width: 1px;
        }
        QPushButton#NavButton {
            background: transparent;
            border: none;
            border-left: 3px solid transparent;
            border-radius: 0;
            color: #2d5a7a;
            text-align: left;
            padding: 11px 14px;
            font-size: 13px;
        }
        QPushButton#NavButton:checked {
            background-color: rgba(0,207,255,0.07);
            border-left: 3px solid #00cfff;
            color: #00cfff;
            font-weight: bold;
        }
        QPushButton#NavButton:hover:!checked {
            background-color: rgba(0,207,255,0.04);
            color: #6ea8d4;
        }

        /* ── Info labels (save overview) ──────────────────────── */
        QLabel#InfoKey {
            color: #2d5a7a;
            font-size: 11px;
            font-weight: bold;
        }
        QLabel#InfoValue {
            color: #00cfff;
            font-size: 12px;
            font-family: "Courier New", "Menlo", monospace;
        }
        QScrollArea#GlobalsScroll {
            background-color: transparent;
            border: none;
        }

        /* ── Inner character detail tabs ──────────────────────── */
        QTabWidget#CharDetailTabs::pane {
            border: 1px solid rgba(0,207,255,0.15);
            border-radius: 0 6px 6px 6px;
            background-color: #081626;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab {
            background: #030d1a;
            color: #2d5a7a;
            padding: 6px 14px;
            border: 1px solid rgba(0,207,255,0.12);
            border-bottom: none;
            margin-right: 2px;
            border-radius: 4px 4px 0 0;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab:selected {
            background: #081626;
            color: #00cfff;
            border-bottom: 2px solid #00cfff;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab:hover:!selected {
            background: #0a1e38;
            color: #6ea8d4;
        }

        /* ── Welcome screen ───────────────────────────────────── */
        QLabel#WelcomeTitle {
            color: #00cfff;
            font-size: 28px;
            font-weight: bold;
        }
        QLabel#WelcomeSubtitle {
            color: #6ea8d4;
            font-size: 14px;
        }
        QLabel#WelcomeTip {
            color: #2d5a7a;
            font-size: 12px;
        }
        QLabel#DropArrow {
            color: #00cfff;
            font-size: 36px;
        }
        QLabel#DropTitle {
            color: #e2f0ff;
            font-size: 16px;
            font-weight: 600;
        }
        QLabel#DropHint {
            color: #3d7a9e;
            font-size: 12px;
        }
        QPushButton#BrowseButton {
            background-color: #00cfff;
            color: #030d1a;
            border: none;
            border-radius: 6px;
            padding: 8px 22px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton#BrowseButton:hover {
            background-color: #33daff;
        }
        QPushButton#BrowseButton:pressed {
            background-color: #0095bb;
        }

        /* ── Globals tab ──────────────────────────────────────── */
        QLabel#TabTitle {
            color: #00cfff;
            font-size: 18px;
            font-weight: bold;
        }
        QFrame#Separator {
            color: rgba(0,207,255,0.12);
        }
        QWidget#StatCard {
            background-color: #081626;
            border: 1px solid rgba(0,207,255,0.18);
            border-radius: 8px;
        }
        QLabel#StatCardLabel {
            color: #e2f0ff;
            font-size: 13px;
            font-weight: bold;
        }
        QLabel#StatCardDesc {
            color: #2d5a7a;
            font-size: 11px;
        }
        QSpinBox#StatCardSpin {
            background-color: #030d1a;
            border: 1px solid rgba(0,207,255,0.25);
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 16px;
            font-weight: bold;
            color: #00cfff;
            font-family: "Courier New", "Menlo", monospace;
        }
        QPushButton#PrimaryButton {
            background-color: #00cfff;
            color: #030d1a;
            border: none;
            border-radius: 6px;
            padding: 7px 20px;
            font-weight: bold;
        }
        QPushButton#PrimaryButton:hover {
            background-color: #33daff;
        }
        QPushButton#PrimaryButton:pressed {
            background-color: #0095bb;
        }
        QPushButton#PrimaryButton:disabled {
            background-color: #0a1e38;
            color: #2d5a7a;
        }
        QCheckBox#SandboxCheck {
            color: #e2f0ff;
            font-size: 13px;
            spacing: 8px;
        }

        /* ── Crew / Storage left panel ────────────────────────── */
        QWidget#CrewLeftPanel {
            background-color: #030d1a;
            border-right: 1px solid rgba(0,207,255,0.12);
        }
        QLabel#PanelSectionLabel {
            color: #2d5a7a;
            font-size: 10px;
            font-weight: bold;
        }
        QLabel#CrewCountBadge {
            background-color: rgba(0,207,255,0.1);
            color: #00cfff;
            font-size: 11px;
            font-weight: bold;
            padding: 1px 8px;
            border-radius: 10px;
        }
        QListWidget#CrewList {
            background-color: transparent;
            border: none;
            outline: none;
        }
        QListWidget#CrewList::item {
            padding: 8px 10px;
            border-radius: 4px;
            margin: 1px 0;
            color: #6ea8d4;
        }
        QListWidget#CrewList::item:selected {
            background-color: rgba(0,207,255,0.1);
            color: #00cfff;
        }
        QListWidget#CrewList::item:hover:!selected {
            background-color: rgba(0,207,255,0.04);
            color: #e2f0ff;
        }

        /* ── Character header card ────────────────────────────── */
        QWidget#CharHeaderCard {
            background-color: #081626;
            border: 1px solid rgba(0,207,255,0.18);
            border-radius: 8px;
        }
        QLineEdit#NameEdit {
            background-color: #030d1a;
            border: 1px solid rgba(0,207,255,0.2);
            border-radius: 6px;
            padding: 6px 10px;
            color: #e2f0ff;
            font-size: 14px;
        }
        QLineEdit#NameEdit:focus {
            border-color: #00cfff;
        }
        QPushButton#InlineButton {
            background-color: transparent;
            color: #6ea8d4;
            border: 1px solid rgba(0,207,255,0.2);
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton#InlineButton:hover {
            background-color: rgba(0,207,255,0.08);
            border-color: #00cfff;
            color: #00cfff;
        }
        QPushButton#DangerButton {
            background-color: transparent;
            color: #ff3366;
            border: 1px solid rgba(255,51,102,0.4);
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton#DangerButton:hover {
            background-color: rgba(255,51,102,0.1);
            border-color: #ff3366;
        }

        /* ── Search / filter ──────────────────────────────────── */
        QLineEdit#FilterEdit {
            background-color: #030d1a;
            border: 1px solid rgba(0,207,255,0.2);
            border-radius: 8px;
            padding: 6px 10px;
            color: #e2f0ff;
        }
        QLineEdit#FilterEdit:focus {
            border-color: #00cfff;
        }

        /* ── Standard controls ────────────────────────────────── */
        QPushButton {
            background-color: #0a1e38;
            color: #6ea8d4;
            border: 1px solid rgba(0,207,255,0.2);
            border-radius: 6px;
            padding: 5px 12px;
        }
        QPushButton:hover {
            background-color: rgba(0,207,255,0.08);
            border-color: #00cfff;
            color: #00cfff;
        }
        QPushButton:pressed {
            background-color: rgba(0,207,255,0.15);
            color: #00cfff;
        }
        QPushButton:disabled {
            background-color: #050f1e;
            color: #1e3a5c;
            border-color: rgba(0,207,255,0.06);
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #030d1a;
            color: #e2f0ff;
            border: 1px solid rgba(0,207,255,0.2);
            border-radius: 6px;
            padding: 4px 8px;
            selection-background-color: rgba(0,207,255,0.25);
            selection-color: #e2f0ff;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border-color: #00cfff;
        }
        QSpinBox::up-button {
            background-color: #0a1e38;
            border: none;
            border-radius: 0 4px 0 0;
            width: 20px;
            image: url(src/ui/icons/plus.svg);
        }
        QSpinBox::down-button {
            background-color: #0a1e38;
            border: none;
            border-radius: 0 0 4px 0;
            width: 20px;
            image: url(src/ui/icons/minus.svg);
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: rgba(0,207,255,0.12);
        }
        QComboBox::drop-down {
            border: none;
            background-color: #0a1e38;
            width: 22px;
            border-radius: 0 6px 6px 0;
        }
        QComboBox::down-arrow {
            image: url(src/ui/icons/minus.svg);
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: #030d1a;
            color: #e2f0ff;
            selection-background-color: rgba(0,207,255,0.12);
            border: 1px solid rgba(0,207,255,0.2);
            border-radius: 6px;
        }
        QListWidget {
            background-color: #030d1a;
            color: #e2f0ff;
            border: 1px solid rgba(0,207,255,0.15);
            border-radius: 6px;
            outline: none;
        }
        QListWidget::item {
            padding: 5px 8px;
        }
        QListWidget::item:selected {
            background-color: rgba(0,207,255,0.12);
            color: #00cfff;
        }
        QListWidget::item:hover:!selected {
            background-color: rgba(0,207,255,0.05);
        }
        QTableWidget {
            background-color: #030d1a;
            color: #e2f0ff;
            border: 1px solid rgba(0,207,255,0.15);
            border-radius: 6px;
            gridline-color: #081626;
            outline: none;
        }
        QTableWidget::item {
            padding: 5px 10px;
        }
        QTableWidget::item:selected {
            background-color: rgba(0,207,255,0.12);
            color: #00cfff;
        }
        QHeaderView::section {
            background-color: #050f1e;
            color: #2d5a7a;
            border: none;
            border-right: 1px solid rgba(0,207,255,0.08);
            border-bottom: 1px solid rgba(0,207,255,0.12);
            padding: 6px 10px;
            font-size: 11px;
            font-weight: bold;
        }
        QGroupBox {
            color: #00cfff;
            border: 1px solid rgba(0,207,255,0.18);
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            font-size: 11px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }
        QCheckBox {
            color: #e2f0ff;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid rgba(0,207,255,0.3);
            border-radius: 4px;
            background-color: #030d1a;
        }
        QCheckBox::indicator:checked {
            background-color: #00cfff;
            border-color: #00cfff;
        }
        QCheckBox::indicator:hover {
            border-color: #00cfff;
        }
        QScrollBar:vertical {
            background-color: transparent;
            width: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: rgba(0,207,255,0.2);
            border-radius: 3px;
            min-height: 24px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: rgba(0,207,255,0.4);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: transparent;
            height: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: rgba(0,207,255,0.2);
            border-radius: 3px;
            min-width: 24px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: rgba(0,207,255,0.4);
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QSplitter::handle {
            background-color: rgba(0,207,255,0.1);
            width: 1px;
        }
        QLabel {
            color: #e2f0ff;
            background-color: transparent;
        }
        QToolTip {
            background-color: #0a1e38;
            color: #e2f0ff;
            border: 1px solid rgba(0,207,255,0.3);
            border-radius: 4px;
            padding: 4px 8px;
        }
    """)




def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Space Haven Save Editor")
    app.setApplicationVersion("1.0.0")
    _apply_dark_palette(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
