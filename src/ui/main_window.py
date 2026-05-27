"""main_window.py - Application main window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QSize, Qt
from PySide6.QtGui import (
    QAction,
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QIcon,
    QKeySequence,
    QLinearGradient,
    QPainter,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.save_file import SaveFile
from src.ui.crew_tab import CrewTab
from src.ui.globals_tab import GlobalsTab
from src.ui.research_tab import ResearchTab
from src.ui.ships_tab import ShipsTab
from src.ui.storage_tab import StorageTab
from src.ui.universe_tab import UniverseTab
from src.ui.welcome_widget import WelcomeWidget

_ICONS_DIR = Path(__file__).parent / "icons"

_NAV_ITEMS: tuple[tuple[str, int, str], ...] = (
    ("Overview", 0, "overview"),
    ("Crew", 1, "crew"),
    ("Storage", 2, "storage"),
    ("Ships", 3, "ships"),
    ("Research", 4, "research"),
    ("Universe", 5, "universe"),
)


def _icon(name: str) -> QIcon:
    """Load an SVG icon from the icons directory; returns empty QIcon if missing."""
    path = _ICONS_DIR / f"{name}.svg"
    return QIcon(str(path)) if path.exists() else QIcon()


class _ConfirmDialog(QDialog):
    """A minimal dark-themed confirmation dialog."""

    _WIDTH: int = 400

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Proceed",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(self._WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        # Icon + message row
        row = QHBoxLayout()
        row.setSpacing(16)

        icon_lbl = QLabel("⚠")
        icon_lbl.setStyleSheet(
            "color: #FDBF00; font-size: 28px; background: transparent;"
        )
        icon_lbl.setFixedWidth(36)
        row.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignTop)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(
            "color: #DDF0F5; font-size: 13px; background: transparent;"
        )
        row.addWidget(msg_lbl)
        layout.addLayout(row)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setObjectName("DangerButton")
        confirm_btn.setFixedWidth(120)
        confirm_btn.clicked.connect(self.accept)
        btn_row.addWidget(confirm_btn)

        layout.addLayout(btn_row)


class _SidebarIndicator(QWidget):
    """A glowing bar that slides smoothly to the active nav button."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setFixedWidth(parent.width() if parent else 168)

        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def slide_to(self, rect: QRect) -> None:
        if self.geometry() == rect:
            return
        self._anim.stop()
        self._anim.setStartValue(self.geometry())
        self._anim.setEndValue(rect)
        self._anim.start()

    def paintEvent(self, event) -> None:  # noqa: N802
        if self.height() == 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Gradient fade from left (bright) to right (transparent)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor(0, 216, 240, 45))
        grad.setColorAt(0.6, QColor(0, 216, 240, 18))
        grad.setColorAt(1.0, QColor(0, 216, 240, 0))
        painter.fillRect(self.rect(), grad)

        # Bright left edge accent
        painter.fillRect(0, 0, 3, self.height(), QColor(0, 216, 240, 230))
        painter.end()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._save: SaveFile | None = None
        self._unsaved = False
        self.setWindowTitle("Space Haven Save Editor")
        self.setWindowIcon(_icon("app"))
        self.resize(1200, 780)
        self.setAcceptDrops(True)
        self._build_menu()
        self._build_central()
        self._update_actions()
        self._show_welcome()

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        mb = self.menuBar()

        file_menu = mb.addMenu("&File")

        self._open_action = QAction("&Open Save Folder…", self)
        self._open_action.setShortcut(QKeySequence.StandardKey.Open)
        self._open_action.triggered.connect(self._open_folder)
        file_menu.addAction(self._open_action)

        self._open_file_action = QAction("Open game &File…", self)
        self._open_file_action.triggered.connect(self._open_file)
        file_menu.addAction(self._open_file_action)

        self._save_action = QAction("&Save", self)
        self._save_action.setShortcut(QKeySequence.StandardKey.Save)
        self._save_action.triggered.connect(self._save_file)
        file_menu.addAction(self._save_action)

        self._save_as_action = QAction("Save &As…", self)
        self._save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self._save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(self._save_as_action)

        file_menu.addSeparator()

        self._backup_action = QAction("Create &Backup", self)
        self._backup_action.triggered.connect(self._create_backup)
        file_menu.addAction(self._backup_action)

        self._close_action = QAction("&Close File", self)
        self._close_action.triggered.connect(self._close_file)
        file_menu.addAction(self._close_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = mb.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    # ------------------------------------------------------------------
    # Central widget: stacked welcome | editor
    # ------------------------------------------------------------------

    def _build_central(self) -> None:
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # Page 0: Welcome
        self._welcome = WelcomeWidget()
        self._welcome.file_selected.connect(self._load_file)
        self._stack.addWidget(self._welcome)

        # Page 1: Editor
        editor_page = QWidget()
        editor_page.setObjectName("EditorPage")
        ev = QVBoxLayout(editor_page)
        ev.setContentsMargins(0, 0, 0, 0)
        ev.setSpacing(0)

        ev.addWidget(self._build_file_bar())

        # Editor body: sidebar | content
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        body_layout.addWidget(self._build_sidebar())

        self._content_stack = QStackedWidget()
        self._globals_tab = GlobalsTab()
        self._crew_tab = CrewTab()
        self._storage_tab = StorageTab()
        self._ships_tab = ShipsTab()
        self._research_tab = ResearchTab()
        self._universe_tab = UniverseTab()
        self._content_stack.addWidget(self._globals_tab)  # index 0
        self._content_stack.addWidget(self._crew_tab)  # index 1
        self._content_stack.addWidget(self._storage_tab)  # index 2
        self._content_stack.addWidget(self._ships_tab)  # index 3
        self._content_stack.addWidget(self._research_tab)  # index 4
        self._content_stack.addWidget(self._universe_tab)  # index 5

        self._globals_tab.status_message.connect(self._mark_unsaved)
        self._crew_tab.status_message.connect(self._mark_unsaved)
        self._storage_tab.status_message.connect(self._mark_unsaved)
        self._ships_tab.status_message.connect(self._mark_unsaved)
        self._research_tab.status_message.connect(self._mark_unsaved)
        self._universe_tab.status_message.connect(self._mark_unsaved)

        body_layout.addWidget(self._content_stack)
        ev.addWidget(body)
        self._stack.addWidget(editor_page)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(168)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(2)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        self._nav_buttons: list[QPushButton] = []
        for label, page_idx, icon_name in _NAV_ITEMS:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setObjectName("NavButton")
            btn.setIcon(_icon(icon_name))
            btn.setIconSize(QSize(17, 17))
            btn.clicked.connect(lambda _, p=page_idx: self._nav_to(p))
            self._nav_group.addButton(btn, page_idx)
            layout.addWidget(btn)
            self._nav_buttons.append(btn)

        self._nav_group.button(0).setChecked(True)
        layout.addStretch()

        # Animated indicator overlaid on the sidebar
        self._nav_indicator = _SidebarIndicator(sidebar)
        self._nav_indicator.raise_()

        # Right border separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setObjectName("SidebarSep")

        container = QWidget()
        container.setObjectName("SidebarContainer")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(sidebar)
        row.addWidget(sep)

        def _resize_handler(event):
            QWidget.resizeEvent(sidebar, event)
            self._update_indicator(animated=False)

        # Position indicator on first button after layout is settled
        sidebar.resizeEvent = _resize_handler  # type: ignore[attr-defined]
        return container



    def _nav_to(self, page_idx: int) -> None:
        self._content_stack.setCurrentIndex(page_idx)
        self._update_indicator(animated=True)

    def _update_indicator(self, *, animated: bool = True) -> None:
        checked = self._nav_group.checkedButton()
        if checked is None or not hasattr(self, "_nav_indicator"):
            return
        parent = self._nav_indicator.parent()
        if parent is None:
            return
        # Map button rect to sidebar coords (indicator's parent)
        btn_rect = checked.geometry()
        target = QRect(0, btn_rect.y(), parent.width(), btn_rect.height())
        if animated:
            self._nav_indicator.slide_to(target)
        else:
            self._nav_indicator.setGeometry(target)

    def _build_file_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("FileBar")
        bar.setFixedHeight(50)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(8)

        self._close_file_btn = QPushButton("✕  Close File")
        self._close_file_btn.setObjectName("FileBarButton")
        self._close_file_btn.setToolTip("Close file and return to welcome screen")
        self._close_file_btn.clicked.connect(self._close_file)
        layout.addWidget(self._close_file_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedHeight(22)
        sep.setObjectName("FileBarSep")
        layout.addWidget(sep)

        layout.addSpacing(4)

        self._file_label = QLabel("No file loaded")
        self._file_label.setObjectName("FileLabel")
        self._file_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self._file_label)

        self._unsaved_badge = QLabel("● Unsaved")
        self._unsaved_badge.setObjectName("UnsavedBadge")
        self._unsaved_badge.setFixedHeight(22)
        self._unsaved_badge.setVisible(False)
        layout.addWidget(self._unsaved_badge)

        layout.addSpacing(12)

        self._backup_btn = QPushButton("Backup")
        self._backup_btn.setObjectName("FileBarButton")
        self._backup_btn.setIcon(_icon("backup"))
        self._backup_btn.setIconSize(QSize(15, 15))
        self._backup_btn.setToolTip("Create a backup of the current save file")
        self._backup_btn.clicked.connect(self._create_backup)
        layout.addWidget(self._backup_btn)

        self._save_as_btn = QPushButton("Save As…")
        self._save_as_btn.setObjectName("FileBarButton")
        self._save_as_btn.setIcon(_icon("save"))
        self._save_as_btn.setIconSize(QSize(15, 15))
        self._save_as_btn.clicked.connect(self._save_file_as)
        layout.addWidget(self._save_as_btn)

        self._save_btn = QPushButton("Save")
        self._save_btn.setObjectName("SaveButton")
        self._save_btn.setIcon(_icon("save"))
        self._save_btn.setIconSize(QSize(15, 15))
        self._save_btn.clicked.connect(self._save_file)
        layout.addWidget(self._save_btn)

        return bar

    # ------------------------------------------------------------------
    # Page switching
    # ------------------------------------------------------------------

    def _show_welcome(self) -> None:
        self._stack.setCurrentIndex(0)
        self.setWindowTitle("Space Haven Save Editor")

    def _show_editor(self) -> None:
        self._stack.setCurrentIndex(1)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------

    def _mark_unsaved(self, _msg: str = "") -> None:
        self._unsaved = True
        self._unsaved_badge.setVisible(True)

    def _clear_unsaved(self) -> None:
        self._unsaved = False
        self._unsaved_badge.setVisible(False)

    # ------------------------------------------------------------------
    # Drag & drop (main-window level - catches drops on the editor view)
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            self._load_file(urls[0].toLocalFile())

    # ------------------------------------------------------------------
    # File actions
    # ------------------------------------------------------------------

    def _load_file(self, path: str) -> None:
        if self._unsaved:
            dlg = _ConfirmDialog(
                "Unsaved Changes",
                "You have unsaved changes. Open a new file anyway?",
                "Open anyway",
                self,
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

        save = SaveFile()
        try:
            save.load(path)
        except Exception as exc:
            QMessageBox.critical(
                self, "Load Error", f"Failed to load save file:\n\n{exc}"
            )
            return

        self._save = save
        self._globals_tab.load(save)
        self._crew_tab.load(save)
        self._storage_tab.load(save)
        self._ships_tab.load(save)
        self._research_tab.load(save)
        self._universe_tab.load(save)
        self._update_actions()
        self._clear_unsaved()

        p = Path(path)
        if p.is_dir():
            display_path = str(p)
            # Outer slot folder: use its name; save/ subfolder: use parent name
            if p.name == "save":
                folder_name = p.parent.name
            else:
                folder_name = p.name
        else:
            display_path = str(p)
            # game file: parent is save/, grandparent is the slot folder
            if p.parent.name == "save":
                folder_name = p.parent.parent.name
            else:
                folder_name = p.parent.name

        self._file_label.setText(display_path)
        self._file_label.setToolTip(display_path)
        self.setWindowTitle(f"Space Haven Save Editor  –  {folder_name}")
        self._show_editor()

    def _open_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Open Space Haven Save Folder",
            str(Path.home()),
        )
        if not path:
            return
        self._load_file(path)

    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Space Haven Save File",
            str(Path.home()),
            "Space Haven Save (game);;All Files (*)",
        )
        if not path:
            return
        self._load_file(path)

    def _close_file(self) -> None:
        if self._unsaved:
            dlg = _ConfirmDialog(
                "Unsaved Changes",
                "You have unsaved changes. Close file anyway?",
                "Close anyway",
                self,
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return
        self._save = None
        self._globals_tab.clear()
        self._crew_tab.clear()
        self._storage_tab.clear()
        self._ships_tab.clear()
        self._research_tab.clear()
        self._universe_tab.clear()
        self._clear_unsaved()
        self._update_actions()
        self._show_welcome()

    def _save_file(self) -> None:
        if self._save is None:
            return
        try:
            self._save.save()
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", f"Failed to save:\n\n{exc}")
            return
        self._clear_unsaved()

    def _save_file_as(self) -> None:
        if self._save is None:
            return
        default_dir = Path.home()
        if self._save.path and self._save.path.parent:
            default_dir = self._save.path.parent
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            str(default_dir),
            "Space Haven Save (game);;All Files (*)",
        )
        if not path:
            return
        try:
            self._save.save(path)
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", f"Failed to save:\n\n{exc}")
            return
        p = Path(path)
        self._file_label.setText(str(p))
        self._file_label.setToolTip(str(p))
        self._clear_unsaved()

    def _create_backup(self) -> None:
        if self._save is None:
            return
        try:
            backup_path = self._save.backup()
        except Exception as exc:
            QMessageBox.critical(
                self, "Backup Error", f"Failed to create backup:\n\n{exc}"
            )
            return
        QMessageBox.information(
            self, "Backup Created", f"Backup saved to:\n{backup_path}"
        )

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def _update_actions(self) -> None:
        loaded = self._save is not None
        self._save_action.setEnabled(loaded)
        self._save_as_action.setEnabled(loaded)
        self._backup_action.setEnabled(loaded)
        self._close_action.setEnabled(loaded)

    def _show_about(self) -> None:
        from PySide6.QtWidgets import QApplication

        version = QApplication.applicationVersion()
        msg = QMessageBox(self)
        msg.setWindowTitle("About Space Haven Save Editor")
        msg.setText(
            f"<b>Space Haven Save Editor</b> v{version}<br>"
            "A cross-platform save game editor for Space Haven.<br><br>"
            "Built with Python and PySide6.<br><br>"
            'Author: <a href="https://github.com/xLPMG">xLPMG</a>'
        )
        msg.setTextFormat(Qt.TextFormat.RichText)
        for lbl in msg.findChildren(QLabel):
            lbl.setOpenExternalLinks(True)
        msg.exec()

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._unsaved:
            dlg = _ConfirmDialog(
                "Unsaved Changes",
                "You have unsaved changes. Quit anyway?",
                "Quit anyway",
                self,
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                event.ignore()
                return
        event.accept()
