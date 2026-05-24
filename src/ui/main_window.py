"""main_window.py – Application main window."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
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
from src.ui.welcome_widget import WelcomeWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._save: SaveFile | None = None
        self._unsaved = False
        self.setWindowTitle("Space Haven Save Editor")
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

        self._open_action = QAction("&Open…", self)
        self._open_action.setShortcut(QKeySequence.StandardKey.Open)
        self._open_action.triggered.connect(self._open_file)
        file_menu.addAction(self._open_action)

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
    # Central widget – stacked: welcome | editor
    # ------------------------------------------------------------------

    def _build_central(self) -> None:
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # ── Page 0: Welcome ──────────────────────────────────────────
        self._welcome = WelcomeWidget()
        self._welcome.file_selected.connect(self._load_file)
        self._stack.addWidget(self._welcome)

        # ── Page 1: Editor ───────────────────────────────────────────
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
        self._content_stack.addWidget(self._globals_tab)   # index 0
        self._content_stack.addWidget(self._crew_tab)      # index 1
        self._content_stack.addWidget(self._storage_tab)   # index 2
        self._content_stack.addWidget(self._ships_tab)     # index 3
        self._content_stack.addWidget(self._research_tab)  # index 4

        self._globals_tab.status_message.connect(self._mark_unsaved)
        self._crew_tab.status_message.connect(self._mark_unsaved)
        self._storage_tab.status_message.connect(self._mark_unsaved)
        self._ships_tab.status_message.connect(self._mark_unsaved)
        self._research_tab.status_message.connect(self._mark_unsaved)

        body_layout.addWidget(self._content_stack)
        ev.addWidget(body)
        self._stack.addWidget(editor_page)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(168)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(2)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        nav_items = [
            ("Overview", 0),
            ("Crew", 1),
            ("Storage", 2),
            ("Ships", 3),
            ("Research", 4),
        ]

        for label, page_idx in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setObjectName("NavButton")
            btn.clicked.connect(lambda _, p=page_idx: self._content_stack.setCurrentIndex(p))
            self._nav_group.addButton(btn, page_idx)
            layout.addWidget(btn)

        self._nav_group.button(0).setChecked(True)
        layout.addStretch()

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
        return container

    def _build_file_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("FileBar")
        bar.setFixedHeight(50)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(8)

        self._file_label = QLabel("No file loaded")
        self._file_label.setObjectName("FileLabel")
        self._file_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self._file_label)

        self._unsaved_badge = QLabel("● Unsaved")
        self._unsaved_badge.setObjectName("UnsavedBadge")
        self._unsaved_badge.setFixedHeight(22)
        self._unsaved_badge.setVisible(False)
        layout.addWidget(self._unsaved_badge)

        layout.addSpacing(12)

        self._backup_btn = QPushButton("Backup")
        self._backup_btn.setObjectName("FileBarButton")
        self._backup_btn.setToolTip("Create a backup of the current save file")
        self._backup_btn.clicked.connect(self._create_backup)
        layout.addWidget(self._backup_btn)

        self._save_as_btn = QPushButton("Save As…")
        self._save_as_btn.setObjectName("FileBarButton")
        self._save_as_btn.clicked.connect(self._save_file_as)
        layout.addWidget(self._save_as_btn)

        self._save_btn = QPushButton("Save")
        self._save_btn.setObjectName("SaveButton")
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
    # Drag & drop (main-window level – catches drops on the editor view)
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
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Open a new file anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
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
        self._update_actions()
        self._clear_unsaved()

        p = Path(path)
        self._file_label.setText(str(p))
        self._file_label.setToolTip(str(p))

        self.setWindowTitle(f"Space Haven Save Editor  –  {p.parent.name}")
        self._show_editor()

    def _open_file(self) -> None:
        if self._unsaved:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Open a new file anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

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
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Close file anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._save = None
        self._globals_tab.clear()
        self._crew_tab.clear()
        self._storage_tab.clear()
        self._ships_tab.clear()
        self._research_tab.clear()
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
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            str(self._save.path.parent if self._save.path else Path.home()),
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
        QMessageBox.about(
            self,
            "About Space Haven Save Editor",
            "<b>Space Haven Save Editor</b><br>"
            "A cross-platform save game editor for Space Haven.<br><br>"
            "Built with Python and PySide6.",
        )

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._unsaved:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Quit anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        event.accept()
