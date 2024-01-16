from PyQt5.QtCore import QRunnable, QObject, Qt
from PyQt5.QtWidgets import QAction, QMenuBar, QMenu, QWidget, QListWidget, QHBoxLayout, QLabel, QVBoxLayout, QListWidgetItem
from PyQt5.QtGui import QFont
from chessapp.view.chessboardwidget import ChessBoardWidget
from chessapp.view.piecemovement import PieceMovement
from PyQt5.QtCore import pyqtSignal
from chessapp.configuration import DEFAULT_STYLESHEET


class Module(QObject):

    log_message_received = pyqtSignal(str)

    def __init__(self, app, display_name: str, actions: [QAction]):
        super().__init__()
        self.app = app
        self.display_name: str = display_name
        self.is_focused = False
        self.central_widget = QWidget()
        self.center_widget = QWidget()
        self.log_widget = QListWidget()
        self.chess_board_widget = ChessBoardWidget()
        self.header_label = QLabel()
        self.footer_label = QLabel()
        self.chess_board_widget.piece_movement_observer.append(
            self.on_piece_movement)
        self.actions: [QAction] = actions
        self.init()
        self.is_closing = False
        self.is_closed = False

    def init(self):
        # widget configuration
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setFont(QFont("Times", 20, QFont.Bold))
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.central_widget.setStyleSheet(
            self.central_widget.styleSheet() + ";" + DEFAULT_STYLESHEET)

        # top, centre, bottom
        v_layout = QVBoxLayout()
        self.central_widget.setLayout(v_layout)
        v_layout.addWidget(self.header_label)
        v_layout.addWidget(self.center_widget)
        v_layout.addWidget(self.footer_label)

        # centre: left chess board, right log
        h_Layout = QHBoxLayout()
        self.center_widget.setLayout(h_Layout)
        h_Layout.addWidget(self.chess_board_widget)
        h_Layout.addWidget(self.log_widget)

        # default values
        self.header_label.setText(self.display_name)

        # connections
        self.log_message_received.connect(self.__log_message)

    def register(self):
        menu_bar: QMenuBar = self.app.window.menuBar()
        menu: QMenu = menu_bar.addMenu("&" + self.display_name)
        focus_action = QAction("&Focus", self.app.window)
        focus_action.triggered.connect(
            lambda: self.app.threadpool.start(MethodAction(self.focus)))
        menu.addAction(focus_action)
        for action in self.actions:
            menu.addAction(action)
        self.on_register()

    def about_to_close(self) -> bool:
        return self.is_closing or self.is_closed

    def on_register(self):
        pass

    def on_piece_movement(self, piece_movement: PieceMovement):
        pass

    def on_close(self):
        pass

    def close(self):
        if self.about_to_close():
            return
        self.is_closing = True
        self.on_close()
        # this way around "self.about_to_close()" stays True
        self.is_closed = True
        self.is_closing = False

    def log_message(self, message: str, timeout_milliseconds: int = 2000):
        self.log_message_received.emit(message)
        self.app.show_status_message(message, timeout_milliseconds)

    def __log_message(self, message: str):
        QListWidgetItem(message, self.log_widget)
        self.log_widget.scrollToBottom()

    def focus(self):
        if self.is_focused:
            return
        self.app.unfocus_all_modules()
        self.app.set_central_widget(self.central_widget)
        self.chess_board_widget.grabKeyboard()
        self.is_focused = True
        self.on_focus()

    def unfocus(self):
        if not self.is_focused:
            return
        self.is_focused = False
        self.on_unfocus()

    def on_focus(self):
        pass

    def on_unfocus(self):
        pass

    def dispatch_threadpool(self, callable):
        self.app.threadpool.start(MethodAction(callable))


class MethodAction(QRunnable):
    def __init__(self, method):
        super().__init__()
        self.method = method

    def run(self):
        self.method()


def create_method_action(app, display_name: str, method):
    method_action = QAction("&" + display_name)
    method_action.triggered.connect(
        lambda: app.threadpool.start(MethodAction(method)))
    return method_action
