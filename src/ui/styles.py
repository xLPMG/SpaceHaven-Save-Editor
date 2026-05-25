from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    palette = QPalette()
    base = QColor("#030709")
    surface = QColor("#060D0F")
    overlay = QColor("#0A1A1E")
    text = QColor("#DDF0F5")
    subtext = QColor("#3BBECE")
    accent = QColor("#00D8F0")
    danger = QColor("#FFC533")

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
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, subtext
    )

    app.setPalette(palette)

    app.setStyleSheet("""
        QMainWindow, QDialog, QWidget {
            background-color: #060D0F;
            font-size: 13px;
            font-family: "Inter", "SF Pro Display", "Segoe UI", system-ui, sans-serif;
        }

        QMenuBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #080E10, stop:1 #040A0C);
            color: #DDF0F5;
            border-bottom: 1px solid rgba(0,216,240,0.25);
            padding: 2px 4px;
        }
        QMenuBar::item {
            padding: 4px 10px;
            border-radius: 4px;
        }
        QMenuBar::item:selected {
            background-color: rgba(0,216,240,0.1);
            color: #00D8F0;
        }
        QMenu {
            background: #040A0C;
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.28);
            border-radius: 9px;
            padding: 6px 4px;
        }
        QMenu::item {
            padding: 6px 22px 6px 12px;
            border-radius: 5px;
        }
        QMenu::item:selected {
            background-color: rgba(0,216,240,0.12);
            color: #00D8F0;
        }
        QMenu::separator {
            height: 1px;
            background: rgba(0,216,240,0.12);
            margin: 4px 8px;
        }

        QWidget#EditorPage {
            background-color: #040A0C;
        }

        QWidget#FileBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #070F12, stop:1 #040A0C);
            border-bottom: 1px solid rgba(0,216,240,0.32);
        }
        QLabel#FileLabel {
            color: #3BBECE;
            font-size: 12px;
            letter-spacing: 0.3px;
        }
        QLabel#UnsavedBadge {
            color: #FDBF00;
            font-size: 11px;
            font-weight: bold;
            padding: 2px 9px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(253,191,0,0.22), stop:1 rgba(253,191,0,0.08));
            border: 1px solid rgba(253,191,0,0.45);
            border-radius: 10px;
        }
        QPushButton#SaveButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #02691A, stop:1 #013F10);
            color: #04D912;
            border: 1px solid rgba(4,217,18,0.45);
            border-top: 1px solid rgba(4,217,18,0.7);
            border-radius: 7px;
            padding: 6px 20px;
            font-weight: bold;
            letter-spacing: 0.8px;
        }
        QPushButton#SaveButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #038022, stop:1 #025018);
            border-color: rgba(4,217,18,0.7);
            color: #20FF30;
        }
        QPushButton#SaveButton:pressed {
            background: #013010;
            border-top-color: rgba(4,217,18,0.3);
        }
        QPushButton#FileBarButton {
            background: transparent;
            color: #3BBECE;
            border: 1px solid rgba(0,216,240,0.22);
            border-radius: 7px;
            padding: 5px 16px;
            letter-spacing: 0.3px;
        }
        QPushButton#FileBarButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,216,240,0.1), stop:1 rgba(0,216,240,0.04));
            border-color: rgba(0,216,240,0.6);
            color: #00D8F0;
        }
        QFrame#FileBarSep {
            color: rgba(0,216,240,0.25);
            max-width: 1px;
        }

        QWidget#Sidebar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #030709, stop:1 #040A0C);
        }
        QWidget#SidebarContainer {
            background-color: transparent;
        }
        QFrame#SidebarSep {
            color: rgba(0,216,240,0.18);
            max-width: 1px;
        }
        QPushButton#NavButton {
            background: transparent;
            border: none;
            border-left: 3px solid transparent;
            border-radius: 0;
            color: #1E5060;
            text-align: left;
            padding: 12px 16px;
            font-size: 13px;
            letter-spacing: 0.6px;
        }
        QPushButton#NavButton:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0,216,240,0.18), stop:0.7 rgba(0,216,240,0.06), stop:1 transparent);
            border-left: 3px solid #00D8F0;
            color: #00D8F0;
            font-weight: bold;
        }
        QPushButton#NavButton:hover:!checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0,216,240,0.07), stop:1 transparent);
            color: #4DCEDD;
        }

        QLabel#InfoKey {
            color: #1A4A58;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1.2px;
        }
        QLabel#InfoValue {
            color: #00D8F0;
            font-size: 12px;
            font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace;
        }
        QScrollArea#GlobalsScroll {
            background-color: transparent;
            border: none;
        }

        QTabWidget#CharDetailTabs::pane {
            border: 1px solid rgba(0,216,240,0.18);
            border-top: none;
            border-radius: 0 0 9px 9px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0C1C20, stop:1 #080F11);
        }
        QTabWidget#CharDetailTabs > QTabBar::tab {
            background: #040A0C;
            color: #1A4A58;
            padding: 7px 16px;
            border: 1px solid rgba(0,216,240,0.12);
            border-bottom: none;
            margin-right: 2px;
            border-radius: 5px 5px 0 0;
            letter-spacing: 0.4px;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0F2428, stop:1 #0C1C20);
            color: #00D8F0;
            border-color: rgba(0,216,240,0.28);
            border-top: 2px solid #00D8F0;
        }
        QTabWidget#CharDetailTabs > QTabBar::tab:hover:!selected {
            background: #0A1720;
            color: #3BBECE;
        }

        QLabel#WelcomeTitle {
            color: #00D8F0;
            font-size: 32px;
            font-weight: bold;
            letter-spacing: 3px;
        }
        QLabel#WelcomeSubtitle {
            color: #5DDAEB;
            font-size: 15px;
            letter-spacing: 1px;
        }
        QLabel#WelcomeTip {
            color: #1A4A58;
            font-size: 12px;
        }
        QLabel#WelcomeAuthor {
            color: #1A4A58;
            font-size: 12px;
        }
        QLabel#DropArrow {
            color: #00D8F0;
            font-size: 36px;
        }
        QLabel#DropTitle {
            color: #DDF0F5;
            font-size: 17px;
            font-weight: 600;
        }
        QLabel#DropHint {
            color: #1E5060;
            font-size: 12px;
        }
        QPushButton#BrowseButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #12EEFF, stop:1 #00B0C8);
            color: #020C10;
            border: none;
            border-bottom: 2px solid #008499;
            border-radius: 9px;
            padding: 10px 30px;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 0.8px;
        }
        QPushButton#BrowseButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #30F5FF, stop:1 #00C8E0);
            border-bottom-color: #009AB0;
        }
        QPushButton#BrowseButton:pressed {
            background: #00A0B8;
            border-bottom-color: transparent;
            border-top: 2px solid #007A8A;
        }
        QLabel#TabTitle {
            color: #00D8F0;
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 1.5px;
        }
        QFrame#Separator {
            color: rgba(0,216,240,0.1);
        }

        QWidget#StatCard {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0E2428, stop:1 #080F11);
            border: 1px solid rgba(0,216,240,0.22);
            border-top: 1px solid rgba(0,216,240,0.48);
            border-radius: 10px;
        }
        QLabel#StatCardLabel {
            color: #DDF0F5;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 0.3px;
        }
        QLabel#StatCardDesc {
            color: #1A4A58;
            font-size: 11px;
        }
        QSpinBox#StatCardSpin {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #060E10, stop:1 #030709);
            border: 1px solid rgba(0,216,240,0.32);
            border-radius: 7px;
            padding: 8px 10px;
            font-size: 18px;
            font-weight: bold;
            color: #00D8F0;
            font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace;
        }
        QSpinBox#StatCardSpin:focus {
            border-color: rgba(0,216,240,0.75);
            border-top-color: #00D8F0;
        }

        QPushButton#PrimaryButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #12EEFF, stop:1 #00B0C8);
            color: #020C10;
            border: none;
            border-bottom: 2px solid #008499;
            border-radius: 7px;
            padding: 7px 22px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        QPushButton#PrimaryButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #30F5FF, stop:1 #00C8E0);
        }
        QPushButton#PrimaryButton:pressed {
            background: #00A0B8;
            border-bottom-color: transparent;
        }
        QPushButton#PrimaryButton:disabled {
            background: #0A1A1E;
            color: #1A4A58;
            border-bottom-color: transparent;
        }
        QCheckBox#SandboxCheck {
            color: #DDF0F5;
            font-size: 13px;
            spacing: 8px;
        }

        QWidget#CrewLeftPanel {
            background: qlineargradient(x1:1, y1:0, x2:0, y2:0,
                stop:0 #040A0C, stop:1 #030709);
            border-right: 1px solid rgba(0,216,240,0.15);
        }
        QLabel#PanelSectionLabel {
            color: #1A4A58;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1.2px;
        }
        QLabel#CrewCountBadge {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,216,240,0.18), stop:1 rgba(0,216,240,0.08));
            color: #00D8F0;
            font-size: 11px;
            font-weight: bold;
            padding: 2px 10px;
            border: 1px solid rgba(0,216,240,0.32);
            border-radius: 12px;
        }
        QListWidget#CrewList {
            background-color: transparent;
            border: none;
            outline: none;
        }
        QListWidget#CrewList::item {
            padding: 9px 12px;
            border-radius: 5px;
            margin: 1px 0;
            color: #3BBECE;
        }
        QListWidget#CrewList::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0,216,240,0.15), stop:1 rgba(0,216,240,0.04));
            color: #00D8F0;
        }
        QListWidget#CrewList::item:hover:!selected {
            background: rgba(0,216,240,0.05);
            color: #DDF0F5;
        }

        QWidget#CharHeaderCard {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0E2428, stop:1 #080F11);
            border: 1px solid rgba(0,216,240,0.22);
            border-top: 1px solid rgba(0,216,240,0.48);
            border-radius: 10px;
        }
        QLineEdit#NameEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #060E10, stop:1 #040A0C);
            border: 1px solid rgba(0,216,240,0.22);
            border-radius: 7px;
            padding: 7px 12px;
            color: #DDF0F5;
            font-size: 15px;
            font-weight: 600;
        }
        QLineEdit#NameEdit:focus {
            border-color: rgba(0,216,240,0.7);
            border-top-color: #00D8F0;
        }
        QPushButton#InlineButton {
            background: transparent;
            color: #3BBECE;
            border: 1px solid rgba(0,216,240,0.22);
            border-radius: 7px;
            padding: 5px 16px;
        }
        QPushButton#InlineButton:hover {
            background: rgba(0,216,240,0.08);
            border-color: rgba(0,216,240,0.6);
            color: #00D8F0;
        }
        QPushButton#DangerButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #6B1018, stop:1 #450810);
            color: #F21B42;
            border: 1px solid rgba(242,27,66,0.4);
            border-top: 1px solid rgba(242,27,66,0.65);
            border-radius: 7px;
            padding: 5px 16px;
        }
        QPushButton#DangerButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #8A1420, stop:1 #5B0E14);
            border-color: rgba(242,27,66,0.7);
            color: #FF3560;
        }
        QPushButton#DangerButton:pressed {
            background: #3A0A0E;
        }
        QPushButton#CompleteButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #025A1A, stop:1 #013510);
            color: #04D912;
            border: 1px solid rgba(4,217,18,0.4);
            border-top: 1px solid rgba(4,217,18,0.65);
            border-radius: 7px;
            padding: 5px 16px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        QPushButton#CompleteButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #036022, stop:1 #024018);
            color: #20FF30;
        }
        QPushButton#CompleteButton:pressed {
            background: #012810;
        }
        QPushButton#CompleteButton:disabled {
            background: #040A0C;
            color: #1A4A58;
            border-color: rgba(4,217,18,0.06);
        }

        QLineEdit#FilterEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #060E10, stop:1 #040A0C);
            border: 1px solid rgba(0,216,240,0.22);
            border-radius: 10px;
            padding: 7px 12px;
            color: #DDF0F5;
        }
        QLineEdit#FilterEdit:focus {
            border-color: rgba(0,216,240,0.7);
        }

        QFrame#ResearchBanner {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0E2428, stop:1 #080F11);
            border: 1px solid rgba(0,216,240,0.2);
            border-top: 1px solid rgba(0,216,240,0.48);
            border-radius: 10px;
        }
        QListWidget#TechList {
            background: #040A0C;
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 9px;
            outline: none;
        }
        QListWidget#TechList::item {
            padding: 0px;
            border: none;
        }
        QListWidget#TechList::item:selected {
            background: #0A1820;
        }
        QProgressBar#ResearchProgress {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #060E10, stop:1 #040A0C);
            border: 1px solid rgba(0,216,240,0.18);
            border-radius: 4px;
            max-height: 6px;
        }
        QProgressBar#ResearchProgress::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #005A12, stop:1 #04D912);
            border-radius: 4px;
        }
        QPushButton#FilterButton {
            background: transparent;
            color: #1A4A58;
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 6px;
            padding: 4px 12px;
            font-size: 11px;
            letter-spacing: 0.3px;
        }
        QPushButton#FilterButton:hover {
            color: #3BBECE;
            border-color: rgba(0,216,240,0.4);
            background: rgba(0,216,240,0.04);
        }
        QPushButton#FilterButton:checked {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,216,240,0.18), stop:1 rgba(0,216,240,0.08));
            color: #00D8F0;
            border-color: rgba(0,216,240,0.55);
        }

        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0F2428, stop:1 #0A1A1E);
            color: #3BBECE;
            border: 1px solid rgba(0,216,240,0.22);
            border-radius: 7px;
            padding: 5px 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,216,240,0.14), stop:1 rgba(0,216,240,0.06));
            border-color: rgba(0,216,240,0.6);
            color: #00D8F0;
        }
        QPushButton:pressed {
            background: rgba(0,216,240,0.18);
            color: #00D8F0;
        }
        QPushButton:disabled {
            background: #040A0C;
            color: #0F2A35;
            border-color: rgba(0,216,240,0.06);
        }
        QLineEdit, QSpinBox, QComboBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #060E10, stop:1 #040A0C);
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.22);
            border-radius: 7px;
            padding: 5px 8px;
            selection-background-color: rgba(0,216,240,0.25);
            selection-color: #DDF0F5;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border-color: rgba(0,216,240,0.75);
        }
        QSpinBox::up-button {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0F2428, stop:1 #0A1A1E);
            border: none;
            border-radius: 0 4px 0 0;
            width: 20px;
            image: url(src/ui/icons/plus.svg);
        }
        QSpinBox::down-button {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0A1A1E, stop:1 #0F2428);
            border: none;
            border-radius: 0 0 4px 0;
            width: 20px;
            image: url(src/ui/icons/minus.svg);
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background: rgba(0,216,240,0.15);
        }
        QComboBox::drop-down {
            border: none;
            background: rgba(0,216,240,0.08);
            width: 24px;
            border-radius: 0 7px 7px 0;
        }
        QComboBox::down-arrow {
            image: url(src/ui/icons/minus.svg);
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background: #040A0C;
            color: #DDF0F5;
            selection-background-color: rgba(0,216,240,0.14);
            border: 1px solid rgba(0,216,240,0.25);
            border-radius: 9px;
            outline: none;
        }
        QListWidget {
            background: #040A0C;
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 9px;
            outline: none;
        }
        QListWidget::item {
            padding: 5px 8px;
        }
        QListWidget::item:selected {
            background: rgba(0,216,240,0.14);
            color: #00D8F0;
        }
        QListWidget::item:hover:!selected {
            background: rgba(0,216,240,0.05);
        }
        QTableWidget {
            background: #040A0C;
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 9px;
            gridline-color: rgba(0,216,240,0.06);
            outline: none;
            selection-background-color: rgba(0,216,240,0.14);
            selection-color: #00D8F0;
        }
        QTableWidget::item {
            padding: 6px 10px;
        }
        QTableWidget::item:selected {
            background: rgba(0,216,240,0.14);
            color: #00D8F0;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0A1A1E, stop:1 #060E10);
            color: #1A4A58;
            border: none;
            border-right: 1px solid rgba(0,216,240,0.08);
            border-bottom: 1px solid rgba(0,216,240,0.2);
            padding: 7px 10px;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        QGroupBox {
            color: #3BBECE;
            border: 1px solid rgba(0,216,240,0.18);
            border-top: 1px solid rgba(0,216,240,0.42);
            border-radius: 10px;
            margin-top: 14px;
            padding-top: 14px;
            font-weight: bold;
            font-size: 11px;
            letter-spacing: 0.8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 14px;
            padding: 0 8px;
            color: #3BBECE;
        }
        QCheckBox {
            color: #DDF0F5;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid rgba(0,216,240,0.35);
            border-radius: 5px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #060E10, stop:1 #040A0C);
        }
        QCheckBox::indicator:checked {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #00E8FF, stop:1 #00A8C0);
            border-color: #00D8F0;
        }
        QCheckBox::indicator:hover {
            border-color: rgba(0,216,240,0.7);
        }
        QScrollBar:vertical {
            background: transparent;
            width: 6px;
        }
        QScrollBar::handle:vertical {
            background: rgba(0,216,240,0.22);
            border-radius: 3px;
            min-height: 24px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(0,216,240,0.45);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background: transparent;
            height: 6px;
        }
        QScrollBar::handle:horizontal {
            background: rgba(0,216,240,0.22);
            border-radius: 3px;
            min-width: 24px;
        }
        QScrollBar::handle:horizontal:hover {
            background: rgba(0,216,240,0.45);
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QSplitter::handle {
            background: rgba(0,216,240,0.1);
            width: 1px;
        }
        QLabel {
            color: #DDF0F5;
            background: transparent;
        }
        QToolTip {
            background: #080F11;
            color: #DDF0F5;
            border: 1px solid rgba(0,216,240,0.42);
            border-radius: 7px;
            padding: 5px 10px;
        }
    """)
