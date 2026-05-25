from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    palette = QPalette()
    base    = QColor("#050A0B")
    surface = QColor("#080F11")
    overlay = QColor("#0D1C1F")
    text    = QColor("#DDF0F5")
    subtext = QColor("#3BBECE")
    accent  = QColor("#00D8F0")
    danger  = QColor("#FF8800")

    palette.setColor(QPalette.ColorRole.Window,          surface)
    palette.setColor(QPalette.ColorRole.WindowText,      text)
    palette.setColor(QPalette.ColorRole.Base,            base)
    palette.setColor(QPalette.ColorRole.AlternateBase,   overlay)
    palette.setColor(QPalette.ColorRole.ToolTipBase,     overlay)
    palette.setColor(QPalette.ColorRole.ToolTipText,     text)
    palette.setColor(QPalette.ColorRole.Text,            text)
    palette.setColor(QPalette.ColorRole.Button,          overlay)
    palette.setColor(QPalette.ColorRole.ButtonText,      text)
    palette.setColor(QPalette.ColorRole.BrightText,      danger)
    palette.setColor(QPalette.ColorRole.Link,            accent)
    palette.setColor(QPalette.ColorRole.Highlight,       accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, base)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,       subtext)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, subtext)

    app.setPalette(palette)

    app.setStyleSheet("""
        QMainWindow, QDialog, QWidget {
            background-color: #080F11;
            font-size: 13px;
        }

        QMenuBar {
            background-color: #050A0B;
            color: #DDF0F5;
            border-bottom: 1px solid rgba(0,216,240,0.18);
            padding: 2px 4px;
        }
        QMenuBar::item:selected {
            background-color: #0D1C1F;
            border-radius: 4px;
        }
        QMenu {
            background-color: #050A0B;
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.22);
            border-radius: 6px;
            padding: 4px;
        }
        QMenu::item {
            padding: 5px 22px 5px 12px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: rgba(0,216,240,0.1);
            color: #00D8F0;
        }
        QMenu::separator {
            height: 1px;
            background: rgba(0,216,240,0.12);
            margin: 4px 8px;
        }

        QWidget#EditorPage {
            background-color: #050A0B;
        }

        QWidget#FileBar {
            background-color: #050A0B;
            border-bottom: 1px solid rgba(0,216,240,0.25);
        }
        QLabel#FileLabel {
            color: #3BBECE;
            font-size: 12px;
        }
        QLabel#UnsavedBadge {
            color: #FDBF00;
            font-size: 11px;
            font-weight: bold;
            padding: 1px 7px;
            background-color: rgba(253,191,0,0.13);
            border-radius: 8px;
        }
        QPushButton#SaveButton {
            background-color: #014011;
            color: #04D912;
            border: 1px solid rgba(4,217,18,0.35);
            border-radius: 6px;
            padding: 6px 18px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        QPushButton#SaveButton:hover {
            background-color: #025018;
            border-color: #04D912;
        }
        QPushButton#SaveButton:pressed {
            background-color: #013010;
        }
        QPushButton#FileBarButton {
            background-color: transparent;
            color: #3BBECE;
            border: 1px solid rgba(0,216,240,0.2);
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton#FileBarButton:hover {
            background-color: rgba(0,216,240,0.08);
            border-color: #00D8F0;
            color: #00D8F0;
        }

        QWidget#Sidebar {
            background-color: #050A0B;
        }
        QWidget#SidebarContainer {
            background-color: #050A0B;
        }
        QFrame#SidebarSep {
            color: rgba(0,216,240,0.15);
            max-width: 1px;
        }
        QPushButton#NavButton {
            background: transparent;
            border: none;
            border-left: 3px solid transparent;
            border-radius: 0;
            color: #1A4A58;
            text-align: left;
            padding: 11px 14px;
            font-size: 13px;
            letter-spacing: 0.5px;
        }
        QPushButton#NavButton:checked {
            background-color: rgba(0,216,240,0.08);
            border-left: 3px solid #00D8F0;
            color: #00D8F0;
            font-weight: bold;
        }
        QPushButton#NavButton:hover:!checked {
            background-color: rgba(0,216,240,0.04);
            color: #3BBECE;
        }

        QLabel#InfoKey {
            color: #1A4A58;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 0.8px;
        }
        QLabel#InfoValue {
            color: #00D8F0;
            font-size: 12px;
            font-family: "Courier New", "Menlo", monospace;
        }
        QScrollArea#GlobalsScroll {
            background-color: transparent;
            border: none;
        }

        QTabWidget#CharDetailTabs::pane {
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 0 6px 6px 6px;
            background-color: #0B1D20;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab {
            background: #050A0B;
            color: #1A4A58;
            padding: 6px 14px;
            border: 1px solid rgba(0,216,240,0.12);
            border-bottom: none;
            margin-right: 2px;
            border-radius: 4px 4px 0 0;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab:selected {
            background: #0B1D20;
            color: #00D8F0;
            border-bottom: 2px solid #00D8F0;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab:hover:!selected {
            background: #0D1C1F;
            color: #3BBECE;
        }

        QLabel#WelcomeTitle {
            color: #00D8F0;
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        QLabel#WelcomeTip {
            color: #1A4A58;
            font-size: 12px;
        }
        QLabel#DropArrow {
            color: #00D8F0;
            font-size: 36px;
        }
        QLabel#DropTitle {
            color: #DDF0F5;
            font-size: 16px;
            font-weight: 600;
        }
        QLabel#DropHint {
            color: #1E5060;
            font-size: 12px;
        }
        QPushButton#BrowseButton {
            background-color: #00D8F0;
            color: #050A0B;
            border: none;
            border-radius: 6px;
            padding: 8px 22px;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        QPushButton#BrowseButton:hover {
            background-color: #33E2F5;
        }
        QPushButton#BrowseButton:pressed {
            background-color: #008EA0;
        }

        QLabel#TabTitle {
            color: #00D8F0;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        QFrame#Separator {
            color: rgba(0,216,240,0.12);
        }
        QWidget#StatCard {
            background-color: #0B1D20;
            border: 1px solid rgba(0,216,240,0.18);
            border-radius: 8px;
        }
        QLabel#StatCardLabel {
            color: #DDF0F5;
            font-size: 13px;
            font-weight: bold;
        }
        QLabel#StatCardDesc {
            color: #1A4A58;
            font-size: 11px;
        }
        QSpinBox#StatCardSpin {
            background-color: #050A0B;
            border: 1px solid rgba(0,216,240,0.25);
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 16px;
            font-weight: bold;
            color: #00D8F0;
            font-family: "Courier New", "Menlo", monospace;
        }
        QPushButton#PrimaryButton {
            background-color: #00D8F0;
            color: #050A0B;
            border: none;
            border-radius: 6px;
            padding: 7px 20px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        QPushButton#PrimaryButton:hover {
            background-color: #33E2F5;
        }
        QPushButton#PrimaryButton:pressed {
            background-color: #008EA0;
        }
        QPushButton#PrimaryButton:disabled {
            background-color: #0D1C1F;
            color: #1A4A58;
        }
        QCheckBox#SandboxCheck {
            color: #DDF0F5;
            font-size: 13px;
            spacing: 8px;
        }

        QWidget#CrewLeftPanel {
            background-color: #050A0B;
            border-right: 1px solid rgba(0,216,240,0.12);
        }
        QLabel#PanelSectionLabel {
            color: #1A4A58;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 0.8px;
        }
        QLabel#CrewCountBadge {
            background-color: rgba(0,216,240,0.1);
            color: #00D8F0;
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
            color: #3BBECE;
        }
        QListWidget#CrewList::item:selected {
            background-color: rgba(0,216,240,0.1);
            color: #00D8F0;
        }
        QListWidget#CrewList::item:hover:!selected {
            background-color: rgba(0,216,240,0.04);
            color: #DDF0F5;
        }

        QWidget#CharHeaderCard {
            background-color: #0B1D20;
            border: 1px solid rgba(0,216,240,0.18);
            border-radius: 8px;
        }
        QLineEdit#NameEdit {
            background-color: #050A0B;
            border: 1px solid rgba(0,216,240,0.2);
            border-radius: 6px;
            padding: 6px 10px;
            color: #DDF0F5;
            font-size: 14px;
        }
        QLineEdit#NameEdit:focus {
            border-color: #00D8F0;
        }
        QPushButton#InlineButton {
            background-color: transparent;
            color: #3BBECE;
            border: 1px solid rgba(0,216,240,0.2);
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton#InlineButton:hover {
            background-color: rgba(0,216,240,0.08);
            border-color: #00D8F0;
            color: #00D8F0;
        }
        QPushButton#DangerButton {
            background-color: #5B0E14;
            color: #F21B42;
            border: 1px solid rgba(242,27,66,0.35);
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton#DangerButton:hover {
            background-color: #7A1020;
            border-color: #F21B42;
        }
        QPushButton#DangerButton:pressed {
            background-color: #4A0A10;
        }
        QPushButton#CompleteButton {
            background-color: #014011;
            color: #04D912;
            border: 1px solid rgba(4,217,18,0.3);
            border-radius: 6px;
            padding: 5px 14px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        QPushButton#CompleteButton:hover {
            background-color: #025018;
            border-color: #04D912;
        }
        QPushButton#CompleteButton:pressed {
            background-color: #013010;
        }
        QPushButton#CompleteButton:disabled {
            background-color: #050A0B;
            color: #1A4A58;
            border-color: rgba(4,217,18,0.06);
        }

        QLineEdit#FilterEdit {
            background-color: #050A0B;
            border: 1px solid rgba(0,216,240,0.2);
            border-radius: 8px;
            padding: 6px 10px;
            color: #DDF0F5;
        }
        QLineEdit#FilterEdit:focus {
            border-color: #00D8F0;
        }

        QFrame#ResearchBanner {
            background-color: #0B1D20;
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 8px;
        }
        QListWidget#TechList {
            background-color: #050A0B;
            border: 1px solid rgba(0,216,240,0.12);
            border-radius: 6px;
            outline: none;
        }
        QListWidget#TechList::item {
            padding: 0px;
            border: none;
        }
        QListWidget#TechList::item:selected {
            background-color: #0D1C1F;
        }
        QProgressBar#ResearchProgress {
            background-color: #050A0B;
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 3px;
        }
        QProgressBar#ResearchProgress::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #013010, stop:1 #04D912);
            border-radius: 3px;
        }
        QPushButton#FilterButton {
            background-color: transparent;
            color: #1A4A58;
            border: 1px solid rgba(0,216,240,0.12);
            border-radius: 5px;
            padding: 4px 10px;
            font-size: 11px;
        }
        QPushButton#FilterButton:hover {
            color: #3BBECE;
            border-color: rgba(0,216,240,0.3);
        }
        QPushButton#FilterButton:checked {
            background-color: rgba(0,216,240,0.12);
            color: #00D8F0;
            border-color: rgba(0,216,240,0.5);
        }

        QPushButton {
            background-color: #0D1C1F;
            color: #3BBECE;
            border: 1px solid rgba(0,216,240,0.2);
            border-radius: 6px;
            padding: 5px 12px;
        }
        QPushButton:hover {
            background-color: rgba(0,216,240,0.08);
            border-color: #00D8F0;
            color: #00D8F0;
        }
        QPushButton:pressed {
            background-color: rgba(0,216,240,0.15);
            color: #00D8F0;
        }
        QPushButton:disabled {
            background-color: #050A0B;
            color: #0F2A35;
            border-color: rgba(0,216,240,0.06);
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #050A0B;
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.2);
            border-radius: 6px;
            padding: 4px 8px;
            selection-background-color: rgba(0,216,240,0.25);
            selection-color: #DDF0F5;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border-color: #00D8F0;
        }
        QSpinBox::up-button {
            background-color: #0D1C1F;
            border: none;
            border-radius: 0 4px 0 0;
            width: 20px;
            image: url(src/ui/icons/plus.svg);
        }
        QSpinBox::down-button {
            background-color: #0D1C1F;
            border: none;
            border-radius: 0 0 4px 0;
            width: 20px;
            image: url(src/ui/icons/minus.svg);
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: rgba(0,216,240,0.12);
        }
        QComboBox::drop-down {
            border: none;
            background-color: #0D1C1F;
            width: 22px;
            border-radius: 0 6px 6px 0;
        }
        QComboBox::down-arrow {
            image: url(src/ui/icons/minus.svg);
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background-color: #050A0B;
            color: #DDF0F5;
            selection-background-color: rgba(0,216,240,0.12);
            border: 1px solid rgba(0,216,240,0.2);
            border-radius: 6px;
        }
        QListWidget {
            background-color: #050A0B;
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 6px;
            outline: none;
        }
        QListWidget::item {
            padding: 5px 8px;
        }
        QListWidget::item:selected {
            background-color: rgba(0,216,240,0.12);
            color: #00D8F0;
        }
        QListWidget::item:hover:!selected {
            background-color: rgba(0,216,240,0.05);
        }
        QTableWidget {
            background-color: #050A0B;
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 6px;
            gridline-color: #0B1D20;
            outline: none;
        }
        QTableWidget::item {
            padding: 5px 10px;
        }
        QTableWidget::item:selected {
            background-color: rgba(0,216,240,0.12);
            color: #00D8F0;
        }
        QHeaderView::section {
            background-color: #050A0B;
            color: #1A4A58;
            border: none;
            border-right: 1px solid rgba(0,216,240,0.08);
            border-bottom: 1px solid rgba(0,216,240,0.12);
            padding: 6px 10px;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 0.8px;
        }
        QGroupBox {
            color: #00D8F0;
            border: 1px solid rgba(0,216,240,0.18);
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            font-size: 11px;
            letter-spacing: 0.5px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }
        QCheckBox {
            color: #DDF0F5;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid rgba(0,216,240,0.3);
            border-radius: 4px;
            background-color: #050A0B;
        }
        QCheckBox::indicator:checked {
            background-color: #00D8F0;
            border-color: #00D8F0;
        }
        QCheckBox::indicator:hover {
            border-color: #00D8F0;
        }
        QScrollBar:vertical {
            background-color: transparent;
            width: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: rgba(0,216,240,0.2);
            border-radius: 3px;
            min-height: 24px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: rgba(0,216,240,0.4);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: transparent;
            height: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: rgba(0,216,240,0.2);
            border-radius: 3px;
            min-width: 24px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: rgba(0,216,240,0.4);
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QSplitter::handle {
            background-color: rgba(0,216,240,0.1);
            width: 1px;
        }
        QLabel {
            color: #DDF0F5;
            background-color: transparent;
        }
        QToolTip {
            background-color: #0D1C1F;
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.35);
            border-radius: 4px;
            padding: 4px 8px;
        }
    """)
