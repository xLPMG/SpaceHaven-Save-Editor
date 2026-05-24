"""Space Haven Save Editor – entry point."""
from __future__ import annotations

import sys

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def _apply_dark_palette(app: QApplication) -> None:
    """Apply a dark color palette to the application."""
    app.setStyle("Fusion")
    palette = QPalette()

    base        = QColor("#1e1e2e")
    surface     = QColor("#2a2a3e")
    overlay     = QColor("#313145")
    text        = QColor("#cdd6f4")
    subtext     = QColor("#a6adc8")
    accent      = QColor("#89b4fa")
    accent_dark = QColor("#6c8fce")
    danger      = QColor("#f38ba8")
    highlight   = QColor("#45475a")

    palette.setColor(QPalette.ColorRole.Window, surface)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, overlay)
    palette.setColor(QPalette.ColorRole.ToolTipBase, surface)
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
        /* ── Base ──────────────────────────────────────────── */
        QMainWindow, QDialog, QWidget {
            background-color: #2a2a3e;
            font-size: 13px;
        }

        /* ── Menu bar ──────────────────────────────────────── */
        QMenuBar {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border-bottom: 1px solid #313145;
            padding: 2px 4px;
        }
        QMenuBar::item:selected {
            background-color: #313145;
            border-radius: 4px;
        }
        QMenu {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 4px;
        }
        QMenu::item {
            padding: 5px 22px 5px 12px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #313145;
        }
        QMenu::separator {
            height: 1px;
            background: #45475a;
            margin: 4px 8px;
        }

        /* ── Editor page (ensures file bar has no background bleed) ── */
        QWidget#EditorPage {
            background-color: #1e1e2e;
        }

        /* ── File bar (editor header) ───────────────────────── */
        QWidget#FileBar {
            background-color: #1e1e2e;
            border-bottom: 1px solid #313145;
        }
        QLabel#FileLabel {
            color: #a6adc8;
            font-size: 12px;
        }
        QLabel#UnsavedBadge {
            color: #f9e2af;
            font-size: 11px;
            font-weight: bold;
            padding: 1px 7px;
            background-color: rgba(249,226,175,0.12);
            border-radius: 8px;
        }
        QPushButton#SaveButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            border-radius: 6px;
            padding: 6px 18px;
            font-weight: bold;
        }
        QPushButton#SaveButton:hover {
            background-color: #9ec4fb;
        }
        QPushButton#SaveButton:pressed {
            background-color: #6c8fce;
        }
        QPushButton#FileBarButton {
            background-color: #313145;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton#FileBarButton:hover {
            background-color: #3d3d56;
            border-color: #89b4fa;
        }

        /* ── Sidebar navigation ───────────────────────────────── */
        QWidget#Sidebar {
            background-color: #1e1e2e;
        }
        QWidget#SidebarContainer {
            background-color: #1e1e2e;
        }
        QFrame#SidebarSep {
            color: #313145;
            max-width: 1px;
        }
        QPushButton#NavButton {
            background: transparent;
            border: none;
            border-left: 3px solid transparent;
            border-radius: 0;
            color: #6c7086;
            text-align: left;
            padding: 11px 14px;
            font-size: 13px;
        }
        QPushButton#NavButton:checked {
            background-color: rgba(137,180,250,0.10);
            border-left: 3px solid #89b4fa;
            color: #cdd6f4;
            font-weight: bold;
        }
        QPushButton#NavButton:hover:!checked {
            background-color: rgba(255,255,255,0.04);
            color: #a6adc8;
        }

        /* ── Info labels (save overview) ────────────────────────── */
        QLabel#InfoKey {
            color: #6c7086;
            font-size: 11px;
            font-weight: bold;
        }
        QLabel#InfoValue {
            color: #cdd6f4;
            font-size: 13px;
        }
        QScrollArea#GlobalsScroll {
            background-color: transparent;
            border: none;
        }

        /* ── Inner character detail tabs ──────────────────────── */
        QTabWidget#CharDetailTabs::pane {
            border: 1px solid #313145;
            border-radius: 0 6px 6px 6px;
            background-color: #252538;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab {
            background: #1e1e2e;
            color: #585b70;
            padding: 6px 14px;
            border: 1px solid #313145;
            border-bottom: none;
            margin-right: 2px;
            border-radius: 4px 4px 0 0;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab:selected {
            background: #252538;
            color: #cdd6f4;
            border-bottom: 2px solid #89b4fa;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab:hover:!selected {
            background: #26263a;
            color: #a6adc8;
        }

        /* ── Welcome screen ──────────────────────────────────── */
        QLabel#WelcomeTitle {
            color: #cdd6f4;
            font-size: 26px;
            font-weight: bold;
        }
        QLabel#WelcomeSubtitle {
            color: #a6adc8;
            font-size: 14px;
        }
        QLabel#WelcomeTip {
            color: #6c7086;
            font-size: 12px;
        }
        QLabel#DropArrow {
            color: #45475a;
            font-size: 40px;
        }
        QLabel#DropTitle {
            color: #cdd6f4;
            font-size: 16px;
            font-weight: 600;
        }
        QLabel#DropHint {
            color: #6c7086;
            font-size: 12px;
        }
        QPushButton#BrowseButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            border-radius: 8px;
            padding: 8px 22px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton#BrowseButton:hover {
            background-color: #9ec4fb;
        }
        QPushButton#BrowseButton:pressed {
            background-color: #6c8fce;
        }

        /* ── Globals tab ──────────────────────────────────────── */
        QLabel#TabTitle {
            color: #cdd6f4;
            font-size: 18px;
            font-weight: bold;
        }
        QFrame#Separator {
            color: #313145;
        }
        QWidget#StatCard {
            background-color: #252538;
            border: 1px solid #313145;
            border-radius: 10px;
        }
        QLabel#StatCardIcon {
            font-size: 18px;
        }
        QLabel#StatCardLabel {
            color: #cdd6f4;
            font-size: 14px;
            font-weight: bold;
        }
        QLabel#StatCardDesc {
            color: #6c7086;
            font-size: 11px;
        }
        QSpinBox#StatCardSpin {
            background-color: #1e1e2e;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 16px;
            font-weight: bold;
            color: #89b4fa;
        }
        QPushButton#PrimaryButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: none;
            border-radius: 6px;
            padding: 7px 20px;
            font-weight: bold;
        }
        QPushButton#PrimaryButton:hover {
            background-color: #9ec4fb;
        }
        QPushButton#PrimaryButton:pressed {
            background-color: #6c8fce;
        }
        QPushButton#PrimaryButton:disabled {
            background-color: #313145;
            color: #585b70;
        }
        QCheckBox#SandboxCheck {
            color: #cdd6f4;
            font-size: 13px;
            spacing: 8px;
        }

        /* ── Crew / Storage left panel ───────────────────────── */
        QWidget#CrewLeftPanel {
            background-color: #1e1e2e;
            border-right: 1px solid #313145;
        }
        QLabel#PanelSectionLabel {
            color: #6c7086;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        QLabel#CrewCountBadge {
            background-color: #313145;
            color: #a6adc8;
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
            border-radius: 6px;
            margin: 1px 0;
        }
        QListWidget#CrewList::item:selected {
            background-color: #313145;
            color: #cdd6f4;
        }
        QListWidget#CrewList::item:hover:!selected {
            background-color: rgba(255,255,255,0.04);
        }

        /* ── Character header card ───────────────────────────── */
        QWidget#CharHeaderCard {
            background-color: #252538;
            border: 1px solid #313145;
            border-radius: 10px;
        }
        QLineEdit#NameEdit {
            background-color: #1e1e2e;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 6px 10px;
            color: #cdd6f4;
            font-size: 14px;
        }
        QLineEdit#NameEdit:focus {
            border-color: #89b4fa;
        }
        QPushButton#InlineButton {
            background-color: #313145;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton#InlineButton:hover {
            background-color: #3d3d56;
            border-color: #89b4fa;
        }
        QPushButton#DangerButton {
            background-color: transparent;
            color: #f38ba8;
            border: 1px solid #f38ba8;
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton#DangerButton:hover {
            background-color: rgba(243,139,168,0.12);
        }

        /* ── Search / filter ──────────────────────────────────── */
        QLineEdit#FilterEdit {
            background-color: #1e1e2e;
            border: 1px solid #45475a;
            border-radius: 8px;
            padding: 6px 10px;
            color: #cdd6f4;
        }
        QLineEdit#FilterEdit:focus {
            border-color: #89b4fa;
        }

        /* ── Standard controls ────────────────────────────────── */
        QPushButton {
            background-color: #313145;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 5px 12px;
        }
        QPushButton:hover {
            background-color: #3d3d56;
            border-color: #89b4fa;
        }
        QPushButton:pressed {
            background-color: #89b4fa;
            color: #1e1e2e;
        }
        QPushButton:disabled {
            background-color: #252538;
            color: #45475a;
            border-color: #313145;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 4px 8px;
            selection-background-color: #89b4fa;
            selection-color: #1e1e2e;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border-color: #89b4fa;
        }
        QSpinBox::up-button {
            background-color: #313145;
            border: none;
            border-radius: 0 4px 0 0;
            width: 20px;
            image: url(src/ui/icons/plus.svg);
        }
        QSpinBox::down-button {
            background-color: #313145;
            border: none;
            border-radius: 0 0 4px 0;
            width: 20px;
            image: url(src/ui/icons/minus.svg);
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #45475a;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #313145;
            width: 22px;
            border-radius: 0 6px 6px 0;
        }
        QComboBox::down-arrow {
            image: url(src/ui/icons/minus.svg);
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: #1e1e2e;
            color: #cdd6f4;
            selection-background-color: #45475a;
            border: 1px solid #45475a;
            border-radius: 6px;
        }
        QListWidget {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            outline: none;
        }
        QListWidget::item {
            padding: 5px 8px;
        }
        QListWidget::item:selected {
            background-color: #45475a;
            color: #cdd6f4;
        }
        QListWidget::item:hover:!selected {
            background-color: #313145;
        }
        QTableWidget {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            gridline-color: #252538;
            outline: none;
        }
        QTableWidget::item {
            padding: 5px 10px;
        }
        QTableWidget::item:selected {
            background-color: #45475a;
            color: #cdd6f4;
        }
        QHeaderView::section {
            background-color: #252538;
            color: #6c7086;
            border: none;
            border-right: 1px solid #313145;
            border-bottom: 1px solid #313145;
            padding: 6px 10px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        }
        QGroupBox {
            color: #a6adc8;
            border: 1px solid #313145;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }
        QCheckBox {
            color: #cdd6f4;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #45475a;
            border-radius: 4px;
            background-color: #1e1e2e;
        }
        QCheckBox::indicator:checked {
            background-color: #89b4fa;
            border-color: #89b4fa;
        }
        QCheckBox::indicator:hover {
            border-color: #89b4fa;
        }
        QScrollBar:vertical {
            background-color: transparent;
            width: 8px;
        }
        QScrollBar::handle:vertical {
            background-color: #45475a;
            border-radius: 4px;
            min-height: 24px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #585b70;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: transparent;
            height: 8px;
        }
        QScrollBar::handle:horizontal {
            background-color: #45475a;
            border-radius: 4px;
            min-width: 24px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #585b70;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QSplitter::handle {
            background-color: #313145;
            width: 1px;
        }
        QStatusBar {
            background-color: #1e1e2e;
            color: #6c7086;
            border-top: 1px solid #313145;
            font-size: 12px;
        }
        QLabel {
            color: #cdd6f4;
            background-color: transparent;
        }
        QToolTip {
            background-color: #313145;
            color: #cdd6f4;
            border: 1px solid #45475a;
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
