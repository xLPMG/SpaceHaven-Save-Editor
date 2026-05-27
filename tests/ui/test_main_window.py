"""Tests for src/ui/main_window.py using pytest-qt and a minimal SaveFile fixture."""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtCore import QMimeData, Qt, QUrl
from PySide6.QtGui import QCloseEvent, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QDialog, QMessageBox, QPushButton

from src.save_file import SaveFile
from src.ui.main_window import MainWindow, _ConfirmDialog, _NAV_ITEMS, _SidebarIndicator
from tests.helpers import make_save_from_xml

# ---------------------------------------------------------------------------
# XML fixtures used by _make_save (imported from tests.helpers)
# ---------------------------------------------------------------------------

MINIMAL_XML = textwrap.dedent("""\
    <game mode="Normal" seed="42">
      <playerBank ca="1000" cr="0"/>
      <settings><diff sandbox="false"/></settings>
      <questLines><questLines>
        <l type="ExodusFleet" playerPrestigePoints="8"/>
      </questLines></questLines>
      <ships>
        <ship sid="10" sname="HSS ALPHA" sx="56" sy="56">
          <characters>
            <c entId="1" name="Alice" lname="Smith" cid="10">
              <props>
                <Health v="80"/><Food v="100"/><Rest v="90"/>
                <Comfort v="50"/><Mood v="70"/><Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr><a points="3" id="210"/></attr>
                <traits><t id="1046"/></traits>
                <conditions><c id="3307"/></conditions>
                <sociality><relationships>
                  <l targetId="2" friendship="20" attraction="-5" compatibility="60"/>
                </relationships></sociality>
                <skills>
                  <s sk="6" level="3" mxn="8" exp="0" expd="0"/>
                  <s sk="14" level="5" mxn="7" exp="0" expd="0"/>
                </skills>
              </pers>
            </c>
            <c entId="2" name="Bob" lname="Jones" cid="10">
              <props>
                <Health v="50"/><Food v="90"/><Rest v="80"/>
                <Comfort v="60"/><Mood v="55"/><Oxygen v="0"/>
                <Temperature v="100"/>
              </props>
              <pers>
                <attr/>
                <traits/>
                <conditions/>
                <sociality><relationships>
                  <l targetId="1" friendship="15" attraction="5" compatibility="40"/>
                </relationships></sociality>
                <skills>
                  <s sk="22" level="2" mxn="10" exp="0" expd="0"/>
                </skills>
              </pers>
            </c>
          </characters>
          <storage>
            <stacks>
              <stack itemId="1" amount="100"/>
              <stack itemId="2" amount="200"/>
            </stacks>
          </storage>
        </ship>
        <ship sid="20" sname="HSS BETA" sx="28" sy="28">
          <characters/>
        </ship>
      </ships>
      <research treeId="2535"><states/></research>
    </game>
""")


def _make_save(xml: str = MINIMAL_XML) -> SaveFile:
    return make_save_from_xml(xml)


def _load_file_with_mock(win: MainWindow, file_path: str | Path) -> SaveFile:
    """Helper to load a file with proper mocking."""
    mock_save = _make_save()
    mock_save.path = Path(file_path)
    with patch("src.ui.main_window.SaveFile", return_value=mock_save):
        win._load_file(str(file_path))
    return mock_save


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function", autouse=True)
def mock_all_dialogs():
    """
    Mock all confirmation and message dialogs at module level to prevent popups.
    This ensures NO dialogs appear during any test execution or cleanup.
    """
    with patch("src.ui.main_window._ConfirmDialog") as mock_confirm:
        # Always return Accepted so tests can proceed
        mock_confirm.return_value.exec.return_value = QDialog.DialogCode.Accepted
        yield mock_confirm


@pytest.fixture(autouse=True)
def cleanup_windows(qtbot):
    """
    Ensure all MainWindow instances are properly cleaned up after each test.
    This prevents closeEvent dialogs during pytest cleanup.
    """
    yield
    
    # After each test, find all MainWindow instances and clear their unsaved state
    from PySide6.QtWidgets import QApplication
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, MainWindow):
            widget._unsaved = False


@pytest.fixture
def main_window(qtbot):
    """Fixture that creates a MainWindow with proper cleanup."""
    win = MainWindow()
    qtbot.addWidget(win)
    yield win
    win._unsaved = False


# ===========================================================================
# _ConfirmDialog
# ===========================================================================


class TestConfirmDialog:
    def test_dialog_created_with_title(self, qtbot, mock_all_dialogs):
        # _ConfirmDialog is imported directly here, so the module-level
        # patch (which covers main_window.py internals) does not intercept
        # these direct instantiations.
        dlg = _ConfirmDialog("Test Title", "Test message")
        qtbot.addWidget(dlg)
        assert dlg.windowTitle() == "Test Title"
        dlg.close()

    def test_dialog_is_modal(self, qtbot, mock_all_dialogs):
        dlg = _ConfirmDialog("Title", "Message")
        qtbot.addWidget(dlg)
        assert dlg.isModal()
        dlg.close()

    def test_dialog_has_fixed_width(self, qtbot, mock_all_dialogs):
        dlg = _ConfirmDialog("Title", "Message")
        qtbot.addWidget(dlg)
        assert dlg.width() == _ConfirmDialog._WIDTH
        dlg.close()

    def test_default_confirm_text_is_proceed(self, qtbot, mock_all_dialogs):
        dlg = _ConfirmDialog("Title", "Message")
        qtbot.addWidget(dlg)
        confirm_btn = dlg.findChild(QPushButton, "DangerButton")
        assert confirm_btn is not None
        assert confirm_btn.text() == "Proceed"
        dlg.close()

    def test_custom_confirm_text(self, qtbot, mock_all_dialogs):
        dlg = _ConfirmDialog("Title", "Message", "Delete")
        qtbot.addWidget(dlg)
        confirm_btn = dlg.findChild(QPushButton, "DangerButton")
        assert confirm_btn.text() == "Delete"
        dlg.close()

    def test_cancel_button_rejects(self, qtbot, mock_all_dialogs):
        dlg = _ConfirmDialog("Title", "Message")
        qtbot.addWidget(dlg)
        buttons = dlg.findChildren(QPushButton)
        cancel_btn = next(b for b in buttons if b.objectName() != "DangerButton")
        with qtbot.waitSignal(dlg.rejected, timeout=1000):
            cancel_btn.click()

    def test_confirm_button_accepts(self, qtbot, mock_all_dialogs):
        dlg = _ConfirmDialog("Title", "Message")
        qtbot.addWidget(dlg)
        confirm_btn = dlg.findChild(QPushButton, "DangerButton")
        with qtbot.waitSignal(dlg.accepted, timeout=1000):
            confirm_btn.click()


# ===========================================================================
# _SidebarIndicator
# ===========================================================================


class TestSidebarIndicator:
    def test_indicator_created_with_parent_width(self, qtbot):
        from PySide6.QtWidgets import QWidget

        parent = QWidget()
        parent.setFixedWidth(200)
        qtbot.addWidget(parent)
        indicator = _SidebarIndicator(parent)
        assert indicator.width() == 200

    def test_indicator_transparent_for_mouse_events(self, qtbot):
        from PySide6.QtWidgets import QWidget

        parent = QWidget()
        qtbot.addWidget(parent)
        indicator = _SidebarIndicator(parent)
        assert indicator.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def test_slide_to_changes_geometry(self, qtbot):
        from PySide6.QtCore import QAbstractAnimation, QRect
        from PySide6.QtWidgets import QWidget

        parent = QWidget()
        parent.setFixedWidth(200)
        qtbot.addWidget(parent)
        indicator = _SidebarIndicator(parent)
        new_rect = QRect(0, 50, parent.width(), 40)
        indicator.slide_to(new_rect)
        # Wait for the animation to finish rather than an arbitrary sleep.
        qtbot.waitUntil(
            lambda: indicator._anim.state() == QAbstractAnimation.State.Stopped,
            timeout=1000,
        )
        final_rect = indicator.geometry()
        assert abs(final_rect.y() - new_rect.y()) <= 1
        assert final_rect.width() == new_rect.width()
        assert final_rect.height() == new_rect.height()

    def test_slide_to_same_rect_does_nothing(self, qtbot):
        from PySide6.QtCore import QRect
        from PySide6.QtWidgets import QWidget
        from PySide6.QtCore import QAbstractAnimation

        parent = QWidget()
        parent.setFixedWidth(200)
        qtbot.addWidget(parent)
        indicator = _SidebarIndicator(parent)
        rect = QRect(0, 0, parent.width(), 40)
        indicator.setGeometry(rect)
        # Sliding to same rect should not start animation
        indicator.slide_to(rect)
        # Animation should not be running
        assert indicator._anim.state() != QAbstractAnimation.State.Running


# ===========================================================================
# MainWindow - initialization
# ===========================================================================


class TestMainWindowInit:
    def test_window_title_set(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert "Space Haven Save Editor" in win.windowTitle()

    def test_window_accepts_drops(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert win.acceptDrops()


    def test_shows_welcome_page_initially(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert win._stack.currentIndex() == 0

    def test_save_initially_none(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert win._save is None

    def test_unsaved_initially_false(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert not win._unsaved

    def test_menu_actions_exist(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert win._open_action is not None
        assert win._open_file_action is not None
        assert win._save_action is not None
        assert win._save_as_action is not None
        assert win._backup_action is not None
        assert win._close_action is not None

    def test_file_actions_disabled_initially(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert not win._save_action.isEnabled()
        assert not win._save_as_action.isEnabled()
        assert not win._backup_action.isEnabled()
        assert not win._close_action.isEnabled()

    def test_nav_buttons_created(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert len(win._nav_buttons) == len(_NAV_ITEMS)

    def test_first_nav_button_checked(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert win._nav_group.button(0).isChecked()

    def test_tabs_created(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        assert win._globals_tab is not None
        assert win._crew_tab is not None
        assert win._storage_tab is not None
        assert win._ships_tab is not None
        assert win._research_tab is not None
        assert win._universe_tab is not None

    def test_all_tabs_connected_to_mark_unsaved(self, qtbot):
        """Test that all tabs have status_message connected to _mark_unsaved."""
        win = MainWindow()
        qtbot.addWidget(win)
        
        # Test each tab individually with proper signal handling
        tabs_to_test = [
            (win._globals_tab, "globals_tab"),
            (win._crew_tab, "crew_tab"),
            (win._storage_tab, "storage_tab"),
            (win._ships_tab, "ships_tab"),
            (win._research_tab, "research_tab"),
            (win._universe_tab, "universe_tab"),
        ]
        
        for tab, tab_name in tabs_to_test:
            # Reset state
            win._unsaved = False
            win._unsaved_badge.setVisible(False)
            
            # Emit signal and verify connection
            tab.status_message.emit(f"test from {tab_name}")
            
            # Verify the signal was processed
            assert win._unsaved is True, f"{tab_name} did not trigger _mark_unsaved"


# ===========================================================================
# MainWindow - navigation
# ===========================================================================


class TestMainWindowNavigation:
    def test_nav_to_changes_page(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._nav_to(2)
        assert win._content_stack.currentIndex() == 2

    def test_nav_button_click_changes_page(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._nav_buttons[3].click()
        assert win._content_stack.currentIndex() == 3

    def test_nav_to_updates_indicator(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._nav_to(1)
        btn_rect = win._nav_buttons[1].geometry()
        qtbot.waitUntil(
            lambda: win._nav_indicator.geometry().y() == btn_rect.y(),
            timeout=500,
        )

    def test_show_welcome_switches_to_page_0(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._stack.setCurrentIndex(1)
        win._show_welcome()
        assert win._stack.currentIndex() == 0

    def test_show_editor_switches_to_page_1(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._show_editor()
        assert win._stack.currentIndex() == 1


# ===========================================================================
# MainWindow - unsaved state
# ===========================================================================


class TestMainWindowUnsavedState:
    def test_mark_unsaved_sets_flag(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._mark_unsaved()
        assert win._unsaved is True
        # Cleanup to prevent dialog on window close
        win._unsaved = False

    def test_mark_unsaved_shows_badge(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._show_editor()  # Switch to editor page where badge is visible
        win.show()
        qtbot.waitExposed(win)
        win._mark_unsaved()
        qtbot.waitUntil(lambda: win._unsaved_badge.isVisible(), timeout=500)
        # Cleanup to prevent dialog on window close
        win._unsaved = False

    def test_clear_unsaved_clears_flag(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._mark_unsaved()
        win._clear_unsaved()
        assert win._unsaved is False

    def test_clear_unsaved_hides_badge(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._show_editor()  # Switch to editor page where badge is visible
        win._mark_unsaved()
        win._clear_unsaved()
        assert not win._unsaved_badge.isVisible()


# ===========================================================================
# MainWindow - drag and drop
# ===========================================================================


class TestMainWindowDragDrop:
    def test_drag_enter_accepts_urls(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile("/tmp/test")])
        event = QDragEnterEvent(
            win.rect().center(), Qt.DropAction.CopyAction, mime, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
        )
        win.dragEnterEvent(event)
        assert event.isAccepted()

    def test_drag_enter_ignores_non_urls(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        mime = QMimeData()
        mime.setText("test")
        event = QDragEnterEvent(
            win.rect().center(), Qt.DropAction.CopyAction, mime, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
        )
        win.dragEnterEvent(event)
        assert not event.isAccepted()

    def test_drop_event_loads_file(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        # Create a mock file
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        with patch.object(win, "_load_file") as mock_load:
            mime = QMimeData()
            mime.setUrls([QUrl.fromLocalFile(str(test_file))])
            event = QDropEvent(
                win.rect().center(),
                Qt.DropAction.CopyAction,
                mime,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
            win.dropEvent(event)
            mock_load.assert_called_once()
            assert Path(mock_load.call_args.args[0]) == test_file


# ===========================================================================
# MainWindow - file loading
# ===========================================================================


class TestMainWindowFileLoading:
    def test_load_file_sets_save(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        # Create a properly initialized mock save
        mock_save = _make_save()
        mock_save.path = test_file
        with patch("src.ui.main_window.SaveFile", return_value=mock_save):
                win._load_file(str(test_file))
                assert win._save is not None

    def test_load_file_switches_to_editor(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        mock_save = _make_save()
        mock_save.path = test_file
        with patch("src.ui.main_window.SaveFile", return_value=mock_save):
            win._load_file(str(test_file))
            assert win._stack.currentIndex() == 1

    def test_load_file_updates_file_label(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        mock_save = _make_save()
        mock_save.path = test_file
        with patch("src.ui.main_window.SaveFile", return_value=mock_save):
            win._load_file(str(test_file))
            assert str(test_file) in win._file_label.text()

    def test_load_file_clears_unsaved(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        win._mark_unsaved()
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        mock_save = _make_save()
        mock_save.path = test_file
        # Module-level mock handles the confirm dialog
        with patch("src.ui.main_window.SaveFile", return_value=mock_save):
            win._load_file(str(test_file))
            assert not win._unsaved

    def test_load_file_enables_actions(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        mock_save = _make_save()
        mock_save.path = test_file
        with patch("src.ui.main_window.SaveFile", return_value=mock_save):
            win._load_file(str(test_file))
            assert win._save_action.isEnabled()
            assert win._save_as_action.isEnabled()
            assert win._backup_action.isEnabled()
            assert win._close_action.isEnabled()

    def test_load_file_with_unsaved_prompts_confirm(self, qtbot, tmp_path, mock_all_dialogs):
        """When there are unsaved changes, a confirm dialog must be raised before loading."""
        win = MainWindow()
        qtbot.addWidget(win)
        win._mark_unsaved()
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        call_count_before = mock_all_dialogs.call_count
        win._load_file(str(test_file))
        # Confirm dialog must have been instantiated exactly once more
        assert mock_all_dialogs.call_count == call_count_before + 1
        # With confirm accepted (mocked), file should be loaded
        assert win._save is not None

    def test_load_file_error_shows_messagebox(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text("invalid xml")

        with patch.object(QMessageBox, "critical") as mock_msg:
            win._load_file(str(test_file))
            mock_msg.assert_called_once()

    def test_load_file_directory_displays_folder_name(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        slot_folder = tmp_path / "SlotFolder"
        slot_folder.mkdir()
        save_folder = slot_folder / "save"
        save_folder.mkdir()
        game_file = save_folder / "game"
        game_file.write_text(MINIMAL_XML)

        mock_save = _make_save()
        mock_save.path = save_folder
        with patch("src.ui.main_window.SaveFile", return_value=mock_save):
            win._load_file(str(save_folder))
            # Window title should contain the slot folder name
            assert "SlotFolder" in win.windowTitle()

    def test_load_file_game_file_displays_slot_name(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        slot_folder = tmp_path / "MySlot"
        slot_folder.mkdir()
        save_folder = slot_folder / "save"
        save_folder.mkdir()
        game_file = save_folder / "game"
        game_file.write_text(MINIMAL_XML)

        mock_save = _make_save()
        mock_save.path = game_file
        with patch("src.ui.main_window.SaveFile", return_value=mock_save):
            win._load_file(str(game_file))
            # Window title should contain the slot folder name
            assert "MySlot" in win.windowTitle()


# ===========================================================================
# MainWindow - file closing
# ===========================================================================


class TestMainWindowFileClosing:
    def test_close_file_clears_save(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        win._close_file()
        assert win._save is None

    def test_close_file_switches_to_welcome(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        win._close_file()
        assert win._stack.currentIndex() == 0

    def test_close_file_clears_unsaved(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        win._mark_unsaved()
        # Module-level mock handles the confirm dialog
        win._close_file()
        assert not win._unsaved

    def test_close_file_disables_actions(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        win._close_file()
        assert not win._save_action.isEnabled()
        assert not win._save_as_action.isEnabled()
        assert not win._backup_action.isEnabled()
        assert not win._close_action.isEnabled()

    def test_close_file_with_unsaved_prompts_confirm(self, qtbot, tmp_path, mock_all_dialogs):
        """When there are unsaved changes, a confirm dialog must be raised before closing."""
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        win._mark_unsaved()
        call_count_before = mock_all_dialogs.call_count
        win._close_file()
        assert mock_all_dialogs.call_count == call_count_before + 1
        # With confirm accepted, file should be closed
        assert win._save is None

    def test_close_file_calls_clear_on_all_tabs(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        # Mock clear methods
        with patch.object(win._globals_tab, "clear") as mock_globals, \
             patch.object(win._crew_tab, "clear") as mock_crew, \
             patch.object(win._storage_tab, "clear") as mock_storage, \
             patch.object(win._ships_tab, "clear") as mock_ships, \
             patch.object(win._research_tab, "clear") as mock_research, \
             patch.object(win._universe_tab, "clear") as mock_universe:
            win._close_file()
            mock_globals.assert_called_once()
            mock_crew.assert_called_once()
            mock_storage.assert_called_once()
            mock_ships.assert_called_once()
            mock_research.assert_called_once()
            mock_universe.assert_called_once()


# ===========================================================================
# MainWindow - file saving
# ===========================================================================


class TestMainWindowFileSaving:
    def test_save_file_does_nothing_if_no_save(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        # Should not crash
        win._save_file()

    def test_save_file_calls_save(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        with patch.object(win._save, "save") as mock_save:
            win._save_file()
            mock_save.assert_called_once()

    def test_save_file_clears_unsaved(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        win._mark_unsaved()
        with patch.object(win._save, "save"):
            win._save_file()
            assert not win._unsaved

    def test_save_file_error_shows_messagebox(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        with patch.object(win._save, "save", side_effect=Exception("Test error")):
            with patch.object(QMessageBox, "critical") as mock_msg:
                win._save_file()
                mock_msg.assert_called_once()

    def test_save_as_does_nothing_if_no_save(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        with patch("src.ui.main_window.QFileDialog.getSaveFileName", return_value=("/tmp/test", "")):
            win._save_file_as()
            # Should not crash

    def test_save_as_with_path_saves_file(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)
        new_file = tmp_path / "game2"

        _load_file_with_mock(win, test_file)
        with patch("src.ui.main_window.QFileDialog.getSaveFileName", return_value=(str(new_file), "")):
            with patch.object(win._save, "save") as mock_save:
                win._save_file_as()
                mock_save.assert_called_once_with(str(new_file))

    def test_save_as_updates_file_label(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)
        new_file = tmp_path / "game2"

        _load_file_with_mock(win, test_file)
        with patch("src.ui.main_window.QFileDialog.getSaveFileName", return_value=(str(new_file), "")):
            with patch.object(win._save, "save"):
                win._save_file_as()
                assert str(new_file) in win._file_label.text()

    def test_save_as_clears_unsaved(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)
        new_file = tmp_path / "game2"

        _load_file_with_mock(win, test_file)
        win._mark_unsaved()
        with patch("src.ui.main_window.QFileDialog.getSaveFileName", return_value=(str(new_file), "")):
            with patch.object(win._save, "save"):
                win._save_file_as()
                assert not win._unsaved

    def test_save_as_cancelled_does_nothing(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        with patch("src.ui.main_window.QFileDialog.getSaveFileName", return_value=("", "")):
            with patch.object(win._save, "save") as mock_save:
                win._save_file_as()
                mock_save.assert_not_called()

    def test_save_as_handles_none_path_gracefully(self, qtbot, tmp_path):
        """Test fix for bug where _save.path could be None."""
        win = MainWindow()
        qtbot.addWidget(win)
        # Create a save with no path
        sf = _make_save()
        sf.path = None
        win._save = sf
        win._show_editor()

        with patch("src.ui.main_window.QFileDialog.getSaveFileName", return_value=("", "")):
            # Should not crash even with None path
            win._save_file_as()


# ===========================================================================
# MainWindow - backup
# ===========================================================================


class TestMainWindowBackup:
    def test_backup_does_nothing_if_no_save(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        # Should not crash
        win._create_backup()

    def test_backup_calls_backup(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        with patch.object(win._save, "backup", return_value="/tmp/backup") as mock_backup:
            with patch.object(QMessageBox, "information"):
                win._create_backup()
                mock_backup.assert_called_once()

    def test_backup_shows_success_message(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        with patch.object(win._save, "backup", return_value="/tmp/backup"):
            with patch.object(QMessageBox, "information") as mock_msg:
                win._create_backup()
                mock_msg.assert_called_once()

    def test_backup_error_shows_messagebox(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        with patch.object(win._save, "backup", side_effect=Exception("Test error")):
            with patch.object(QMessageBox, "critical") as mock_msg:
                win._create_backup()
                mock_msg.assert_called_once()


# ===========================================================================
# MainWindow - window close event
# ===========================================================================


class TestMainWindowCloseEvent:
    def test_close_event_with_no_unsaved_accepts(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        event = QCloseEvent()
        win.closeEvent(event)
        assert event.isAccepted()

    def test_close_event_with_unsaved_accepts_with_mock(self, qtbot):
        """Test that close event accepts when dialog is mocked (as in tests)."""
        win = MainWindow()
        qtbot.addWidget(win)
        win._mark_unsaved()
        from PySide6.QtGui import QCloseEvent

        event = QCloseEvent()
        # Module-level mock will auto-accept the dialog
        win.closeEvent(event)
        # With mocked dialog accepting, event should be accepted
        assert event.isAccepted()

    def test_close_event_dialog_behavior(self, qtbot, mock_all_dialogs):
        """Test that close event shows dialog when unsaved."""
        win = MainWindow()
        qtbot.addWidget(win)
        win._mark_unsaved()
        from PySide6.QtGui import QCloseEvent

        event = QCloseEvent()
        win.closeEvent(event)
        # Verify the dialog was called
        mock_all_dialogs.assert_called()


# ===========================================================================
# MainWindow - about dialog
# ===========================================================================


class TestMainWindowAbout:
    def test_show_about_displays_messagebox(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        with patch("src.ui.main_window.QMessageBox") as mock_mb_cls:
            mock_instance = mock_mb_cls.return_value
            mock_instance.findChildren.return_value = []
            win._show_about()
            mock_mb_cls.assert_called_once_with(win)
            # Check that the dialog text contains version info
            text_arg = mock_instance.setText.call_args[0][0]
            assert "Space Haven Save Editor" in text_arg
            mock_instance.exec.assert_called_once()


# ===========================================================================
# MainWindow - file dialogs
# ===========================================================================


class TestMainWindowFileDialogs:
    def test_open_folder_cancelled_does_nothing(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        with patch("src.ui.main_window.QFileDialog.getExistingDirectory", return_value=""):
            with patch.object(win, "_load_file") as mock_load:
                win._open_folder()
                mock_load.assert_not_called()

    def test_open_folder_with_path_loads_file(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        with patch("src.ui.main_window.QFileDialog.getExistingDirectory", return_value="/tmp/test"):
            with patch.object(win, "_load_file") as mock_load:
                win._open_folder()
                mock_load.assert_called_once_with("/tmp/test")

    def test_open_file_cancelled_does_nothing(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        with patch("src.ui.main_window.QFileDialog.getOpenFileName", return_value=("", "")):
            with patch.object(win, "_load_file") as mock_load:
                win._open_file()
                mock_load.assert_not_called()

    def test_open_file_with_path_loads_file(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        with patch("src.ui.main_window.QFileDialog.getOpenFileName", return_value=("/tmp/game", "")):
            with patch.object(win, "_load_file") as mock_load:
                win._open_file()
                mock_load.assert_called_once_with("/tmp/game")


# ===========================================================================
# MainWindow - update actions
# ===========================================================================


class TestMainWindowUpdateActions:
    def test_update_actions_with_no_save_disables(self, qtbot):
        win = MainWindow()
        qtbot.addWidget(win)
        win._save = None
        win._update_actions()
        assert not win._save_action.isEnabled()
        assert not win._save_as_action.isEnabled()
        assert not win._backup_action.isEnabled()
        assert not win._close_action.isEnabled()

    def test_update_actions_with_save_enables(self, qtbot, tmp_path):
        win = MainWindow()
        qtbot.addWidget(win)
        test_file = tmp_path / "game"
        test_file.write_text(MINIMAL_XML)

        _load_file_with_mock(win, test_file)
        # Actions should be enabled after load
        assert win._save_action.isEnabled()
        assert win._save_as_action.isEnabled()
        assert win._backup_action.isEnabled()
        assert win._close_action.isEnabled()


# ===========================================================================
# MainWindow - indicator updates on resize
# ===========================================================================


class TestMainWindowIndicatorResize:
    def test_indicator_updates_on_sidebar_resize(self, qtbot):
        """Test that indicator updates position when sidebar is resized."""
        from PySide6.QtWidgets import QWidget

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()
        qtbot.waitExposed(win)
        sidebar = win.findChild(QWidget, "Sidebar")
        assert sidebar is not None, "Could not find 'Sidebar' widget by object name"
        sidebar.resize(200, 600)
        assert win._nav_indicator.geometry().y() == win._nav_buttons[0].geometry().y()

    def test_update_indicator_handles_none_parent(self, qtbot):
        """Test fix for bug where indicator parent could be None."""
        win = MainWindow()
        qtbot.addWidget(win)
        # Temporarily set parent to None
        original_parent = win._nav_indicator.parent()
        win._nav_indicator.setParent(None)
        # Should not crash
        win._update_indicator()
        # Restore parent
        win._nav_indicator.setParent(original_parent)
