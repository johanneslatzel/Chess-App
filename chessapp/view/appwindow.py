from PyQt5.QtWidgets import QMainWindow
from chessapp.view.statusmessage import StatusMessage


class AppWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Chess App")
        self.initUI()

    def initUI(self):
        self.init_status_bar()

    def on_status_message_shown(self, status_message: StatusMessage):
        self.status_bar.showMessage(
            status_message.text, status_message.timeout_milliseconds)

    def init_status_bar(self):
        self.status_bar = self.statusBar()
        self.app.status_message_shown.connect(self.on_status_message_shown)
