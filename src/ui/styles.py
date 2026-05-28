from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

MAP_COLOR_HULL = QColor("#C0C8CC")
MAP_COLOR_WALL = QColor("#607080")
MAP_COLOR_DOOR = QColor("#4488EE")
MAP_COLOR_ENGINE = QColor("#E8C040")
MAP_COLOR_STORAGE = QColor("#E87820")
MAP_COLOR_RESTRICTED = QColor("#32415AB4")
MAP_COLOR_INTERIOR = QColor("#303840")
MAP_COLOR_BG = QColor(0, 0, 0, 0)
MAP_COLOR_LEGEND_TEXT = QColor("#8FBFCC")

MAP_LEGEND: list[tuple[QColor, str]] = [
    (MAP_COLOR_HULL, "Hull"),
    (MAP_COLOR_WALL, "Wall"),
    (MAP_COLOR_DOOR, "Door"),
    (MAP_COLOR_ENGINE, "Engine"),
    (MAP_COLOR_STORAGE, "Storage"),
    (MAP_COLOR_INTERIOR, "Interior"),
]

# Crew tab colours
CREW_AVATAR_COLORS: list[str] = [
    "#89b4fa",
    "#a6e3a1",
    "#fab387",
    "#f38ba8",
    "#cba6f7",
    "#94e2d5",
    "#f9e2af",
    "#89dceb",
]
CREW_AVATAR_TEXT_COLOR = QColor("#1e1e2e")
ACTION_CLONE_COLOR = QColor("#89dceb")
ACTION_REMOVE_COLOR = QColor("#f38ba8")
PIP_FILLED_COLOR = "#00D8F0"
PIP_EMPTY_COLOR = "#1E3A40"

# Ship tab colours
SHIP_TAB_SECTION_COLOR = QColor("#00D8F0")

# Storage tab colours
STORAGE_FILTER_ICON_COLOR = QColor("#3BBECE")

# Universe / sector map colors
SECTOR_MAP_BG_COLOR = QColor(20, 20, 30)
SECTOR_MAP_EMPTY_TEXT_COLOR = QColor(150, 150, 150)
SECTOR_MAP_BORDER_COLOR = QColor(100, 100, 120)
SECTOR_MAP_FILL_COLOR = QColor(30, 30, 40)
SECTOR_MAP_SHIP_FALLBACK_COLOR = QColor(100, 100, 150)
SECTOR_MAP_SHIP_DRAG_PEN_COLOR = QColor(255, 255, 255)
SECTOR_MAP_SHIP_HOVER_PEN_COLOR = QColor(200, 200, 255)
SECTOR_MAP_SHIP_NORMAL_PEN_COLOR = QColor(50, 50, 60)
SECTOR_MAP_SHIP_NAME_TEXT_COLOR = QColor(255, 255, 255)
SECTOR_MAP_SHIP_NAME_OUTLINE_COLOR = QColor(0, 0, 0)

# Research tab colors
RESEARCH_DONE_COLOR = QColor("#04D912")
RESEARCH_PROGRESS_COLOR = QColor("#FF8800")
RESEARCH_NONE_COLOR = QColor("#1A4A58")
RESEARCH_BG_EVEN = QColor("#050A0B")
RESEARCH_BG_ODD = QColor("#070E10")
RESEARCH_BG_SEL = QColor("#071820")
RESEARCH_BG_HOVER = QColor("#0A1618")
RESEARCH_SEP = QColor(0, 216, 240, 18)
RESEARCH_TEXT_MAIN = QColor("#DDF0F5")
RESEARCH_TEXT_DIM = QColor("#3BBECE")
RESEARCH_BADGE_DONE_BG = QColor(4, 217, 18, 28)
RESEARCH_BADGE_PROGRESS_BG = QColor(255, 136, 0, 28)
RESEARCH_BADGE_NONE_BG = QColor(26, 74, 88, 20)

# Welcome widget colors
WELCOME_BG_COLOR = QColor("#030709")
WELCOME_STAR_TINTS: list[QColor] = [
    QColor(220, 235, 255),
    QColor(255, 255, 255),
    QColor(255, 252, 240),
    QColor(255, 240, 200),
    QColor(255, 225, 215),
]
WELCOME_TITLE_COLOR = QColor("#00D8F0")
WELCOME_SUBTITLE_COLOR = QColor("#5DDAEB")
WELCOME_TIP_COLOR = QColor("#2D7A94")
WELCOME_AUTHOR_COLOR = QColor("#2D7A94")
WELCOME_LINK_COLOR = QColor("#00D8F0")
WELCOME_DROP_HOVER_BG = QColor(0, 216, 240, 18)
WELCOME_DROP_BG = QColor(3, 7, 9, 170)
WELCOME_DROP_BORDER_COLOR = QColor(0, 216, 240, 80)
WELCOME_DROP_BORDER_HOVER_COLOR = QColor(0, 216, 240, 200)
WELCOME_DROP_CORNER_COLOR = QColor(0, 216, 240, 200)
WELCOME_DROP_ARROW_COLOR = QColor("#00D8F0")
WELCOME_DROP_TITLE_COLOR = QColor("#DDF0F5")
WELCOME_DROP_HINT_COLOR = QColor("#2D7A94")
WELCOME_BROWSE_BG_START = QColor("#12EEFF")
WELCOME_BROWSE_BG_END = QColor("#00B0C8")
WELCOME_BROWSE_BG_HOVER_START = QColor("#30F5FF")
WELCOME_BROWSE_BG_HOVER_END = QColor("#00C8E0")
WELCOME_BROWSE_BG_PRESSED = QColor("#00A0B8")
WELCOME_BROWSE_BORDER_BOTTOM = QColor("#008499")
WELCOME_BROWSE_BORDER_BOTTOM_HOVER = QColor("#009AB0")
WELCOME_BROWSE_BORDER_BOTTOM_PRESSED = QColor("#007A8A")
WELCOME_BROWSE_TEXT_COLOR = QColor("#020C10")


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
            font-family: "D-DIN", "Inter", "SF Pro Display", "Segoe UI", system-ui, sans-serif;
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
            font-size: 13px;
            letter-spacing: 0.3px;
        }
        QLabel#UnsavedBadge {
            color: #FDBF00;
            font-size: 12px;
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
            color: #2D7A94;
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
            color: #2D7A94;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1.2px;
        }
        QLabel#InfoValue {
            color: #00D8F0;
            font-size: 13px;
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
            color: #2D7A94;
            font-size: 13px;
        }
        QLabel#WelcomeAuthor {
            color: #2D7A94;
            font-size: 13px;
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
            color: #2D7A94;
            font-size: 13px;
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
            color: #2D7A94;
            font-size: 12px;
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
            color: #2D7A94;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1.2px;
        }
        QLabel#CrewCountBadge {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,216,240,0.18), stop:1 rgba(0,216,240,0.08));
            color: #00D8F0;
            font-size: 12px;
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
        QPushButton#CompleteAllButton {
            background: transparent;
            color: #04D912;
            border: 1px solid rgba(4,217,18,0.4);
            border-radius: 7px;
            padding: 5px 16px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        QPushButton#CompleteAllButton:hover {
            background: rgba(4,217,18,0.08);
            border-color: rgba(4,217,18,0.65);
        }
        QPushButton#CompleteAllButton:pressed {
            background: rgba(4,217,18,0.14);
        }
        QPushButton#CompleteAllButton:disabled {
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
            color: #2D7A94;
            border: 1px solid rgba(0,216,240,0.15);
            border-radius: 6px;
            padding: 4px 12px;
            font-size: 12px;
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
            background: transparent;
            border: none;
            border-radius: 0 7px 0 0;
            width: 20px;
            image: url(src/ui/icons/plus.svg);
        }
        QSpinBox::down-button {
            background: transparent;
            border: none;
            border-radius: 0 0 7px 0;
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
            color: #2D7A94;
            border: none;
            border-right: 1px solid rgba(0,216,240,0.08);
            border-bottom: 1px solid rgba(0,216,240,0.2);
            padding: 7px 10px;
            font-size: 12px;
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
            font-size: 12px;
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
