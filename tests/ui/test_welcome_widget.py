"""Tests for src/ui/welcome_widget.py using pytest-qt."""

from __future__ import annotations

from unittest.mock import patch

from PySide6.QtCore import QMimeData, Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QHideEvent, QShowEvent
from PySide6.QtWidgets import QLabel

from src.ui.welcome_widget import WelcomeWidget, _StarfieldWidget, _TitleLabel

# ===========================================================================
# WelcomeWidget – construction
# ===========================================================================


class TestWelcomeWidgetConstruction:
    def test_widget_builds_expected_children(self, qtbot):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        assert isinstance(widget._starfield, _StarfieldWidget)
        assert widget._drop_zone is not None
        assert widget._drop_zone.browse_button.text() == "Browse…"
        assert widget._drop_zone.objectName() == "DropZone"
        assert widget._drop_zone.browse_button.objectName() == "BrowseButton"

        title = widget._overlay.layout().itemAt(0).widget()
        assert isinstance(title, _TitleLabel)
        assert title.objectName() == "WelcomeTitle"

        labels = widget.findChildren(QLabel)
        texts = {label.text() for label in labels}
        assert "Mission Control for your save files" in texts
        assert any("Always create a backup" in label.text() for label in labels)
        assert any("github.com/xLPMG" in label.text() for label in labels)

    def test_starfield_and_drop_timers_start_on_show_event(self, qtbot):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        widget.resize(1200, 780)

        widget._starfield.showEvent(QShowEvent())
        widget._drop_zone.showEvent(QShowEvent())

        assert widget._starfield._timer.isActive()
        assert widget._drop_zone._pulse_timer.isActive()
        assert len(widget._starfield._stars) == _StarfieldWidget._N_STARS

    def test_timers_stop_on_hide_event(self, qtbot):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        widget._starfield.showEvent(QShowEvent())
        widget._drop_zone.showEvent(QShowEvent())
        widget._starfield.hideEvent(QHideEvent())
        widget._drop_zone.hideEvent(QHideEvent())

        assert not widget._starfield._timer.isActive()
        assert not widget._drop_zone._pulse_timer.isActive()


# ===========================================================================
# WelcomeWidget – drag and drop
# ===========================================================================


class TestWelcomeWidgetDragDrop:
    def test_drag_enter_accepts_urls_and_sets_hover(self, qtbot):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile("/tmp/test-save")])
        event = QDragEnterEvent(
            widget.rect().center(),
            Qt.DropAction.CopyAction,
            mime,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        widget._drop_zone.dragEnterEvent(event)

        assert event.isAccepted()
        assert widget._drop_zone._hovered

    def test_drag_enter_ignores_text_only_payload(self, qtbot):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        mime = QMimeData()
        mime.setText("not-a-file")
        event = QDragEnterEvent(
            widget.rect().center(),
            Qt.DropAction.CopyAction,
            mime,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        widget._drop_zone.dragEnterEvent(event)

        assert not event.isAccepted()
        assert not widget._drop_zone._hovered

    def test_drop_event_emits_selected_path(self, qtbot, tmp_path):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        dropped_file = tmp_path / "game"
        dropped_file.write_text("save")

        received: list[str] = []
        widget.file_selected.connect(received.append)

        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(dropped_file))])
        event = QDropEvent(
            widget.rect().center(),
            Qt.DropAction.CopyAction,
            mime,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        widget._drop_zone._hovered = True
        widget._drop_zone.dropEvent(event)

        assert received == [str(dropped_file)]
        assert event.isAccepted()
        assert not widget._drop_zone._hovered

    def test_drop_event_without_urls_is_ignored(self, qtbot):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        mime = QMimeData()
        mime.setText("still-not-a-file")
        event = QDropEvent(
            widget.rect().center(),
            Qt.DropAction.CopyAction,
            mime,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        received: list[str] = []
        widget.file_selected.connect(received.append)

        widget._drop_zone._hovered = True
        widget._drop_zone.dropEvent(event)

        assert received == []
        assert not event.isAccepted()
        assert not widget._drop_zone._hovered


# ===========================================================================
# WelcomeWidget – browse menu
# ===========================================================================
# Helpers
# ===========================================================================


def _fake_menu_class(action_index: int | None):
    """Return a FakeMenu class that selects the nth action (or None to cancel)."""

    class FakeMenu:
        def __init__(self, parent=None) -> None:
            self._actions: list[object] = []

        def addAction(self, _text: str):
            action = object()
            self._actions.append(action)
            return action

        def exec(self, _pos):
            if action_index is None:
                return None
            return self._actions[action_index]

    return FakeMenu


# ===========================================================================


class TestWelcomeWidgetBrowse:
    def test_browse_folder_emits_directory_path(self, qtbot, monkeypatch, tmp_path):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        target_dir = tmp_path / "save"
        target_dir.mkdir()
        received: list[str] = []
        widget.file_selected.connect(received.append)

        monkeypatch.setattr("src.ui.welcome_widget.QMenu", _fake_menu_class(0))
        monkeypatch.setattr(
            "src.ui.welcome_widget.QFileDialog.getExistingDirectory",
            lambda *args, **kwargs: str(target_dir),
        )

        widget._browse()

        assert received == [str(target_dir)]

    def test_browse_file_emits_file_path(self, qtbot, monkeypatch, tmp_path):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        target_file = tmp_path / "game"
        target_file.write_text("save")
        received: list[str] = []
        widget.file_selected.connect(received.append)

        monkeypatch.setattr("src.ui.welcome_widget.QMenu", _fake_menu_class(1))
        monkeypatch.setattr(
            "src.ui.welcome_widget.QFileDialog.getOpenFileName",
            lambda *args, **kwargs: (str(target_file), ""),
        )

        widget._browse()

        assert received == [str(target_file)]

    def test_browse_cancel_emits_nothing(self, qtbot, monkeypatch):
        widget = WelcomeWidget()
        qtbot.addWidget(widget)

        received: list[str] = []
        widget.file_selected.connect(received.append)

        monkeypatch.setattr("src.ui.welcome_widget.QMenu", _fake_menu_class(None))

        with patch(
            "src.ui.welcome_widget.QFileDialog.getExistingDirectory"
        ) as mock_dir:
            with patch(
                "src.ui.welcome_widget.QFileDialog.getOpenFileName"
            ) as mock_file:
                widget._browse()

        mock_dir.assert_not_called()
        mock_file.assert_not_called()
        assert received == []
