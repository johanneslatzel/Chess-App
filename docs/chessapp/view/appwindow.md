# appwindow

::: chessapp.view.appwindow.StatusMessage
    options:
        show_root_heading: true
        show_source: true

::: chessapp.view.appwindow.AppWindow
    options:
        show_root_heading: true
        show_source: true

# Source
```python
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal


class StatusMessage:
    """A message that can be shown in the status bar of the main window.
    """

    def __init__(self, text: str, timeout_milliseconds: int = 2000):
        """A message that can be shown in the status bar of the main window.

        Args:
            text (str): the text of the message
            timeout_milliseconds (int, optional): Defaults to 2000. the time in milliseconds after which the message will disappear again
        """
        self.text = text
        self.timeout_milliseconds = timeout_milliseconds


class AppWindow(QMainWindow):
    """The main window of the application.

    Args:
        app (chessapp.chessapp.Chessapp): the main application
    """

    status_message_shown = pyqtSignal(StatusMessage)

    def __init__(self, app):
        """initializes the main window of the application

        Args:
            app (chessapp.chessapp.Chessapp): the main application
        """
        super().__init__()
        self.app = app
        self.setWindowTitle("Chess App")
        self.init_status_bar()

    def on_status_message_shown(self, status_message: StatusMessage):
        """forwards the status message to the status bar

        Args:
            status_message (StatusMessage): this message will be shown in the status bar
        """
        self.status_bar.showMessage(
            status_message.text, status_message.timeout_milliseconds)

    def init_status_bar(self):
        """initializes the status bar on the lower part of the window to display short messages that are received with on_status_message_shown
        """
        self.status_bar = self.statusBar()
        self.status_message_shown.connect(self.on_status_message_shown)
```
