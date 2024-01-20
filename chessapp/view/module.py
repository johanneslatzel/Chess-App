from PyQt5.QtCore import QRunnable, QObject, Qt
from PyQt5.QtWidgets import QAction, QMenuBar, QMenu, QWidget, QListWidget, QHBoxLayout, QLabel, QVBoxLayout, QListWidgetItem
from PyQt5.QtGui import QFont
from chessapp.view.chessboardwidget import ChessBoardWidget, PieceMovement
from PyQt5.QtCore import pyqtSignal
from chessapp.configuration import DEFAULT_STYLESHEET


class BaseModule(QObject):
    def __init__(self, app, display_name: str, actions: [QAction]) -> None:
        super().__init__()
        self.app = app
        self.display_name: str = display_name
        self.is_focused = False
        self.central_widget = QWidget()
        self.main_widget = QWidget()
        self.header_label = QLabel()
        self.footer_label = QLabel()
        self.actions: [QAction] = actions
        self.is_closing = False
        self.is_closed = False

    def init(self) -> None:
        # widget configuration
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setFont(QFont("Times", 20, QFont.Bold))
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.central_widget.setStyleSheet(
            self.central_widget.styleSheet() + ";" + DEFAULT_STYLESHEET)

        # header, main, footer
        v_layout = QVBoxLayout()
        self.central_widget.setLayout(v_layout)
        v_layout.addWidget(self.header_label)
        v_layout.addWidget(self.main_widget)
        v_layout.addWidget(self.footer_label)

        # default values
        self.header_label.setText(self.display_name)

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

    def focus(self):
        if self.is_focused:
            return
        self.app.unfocus_all_modules()
        self.app.set_central_widget(self.central_widget)
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


class LogModule(BaseModule):

    log_message_received = pyqtSignal(str)

    def __init__(self, app, display_name: str, actions: [QAction]):
        super().__init__(app, display_name, actions)
        self.log_widget = QListWidget()

    def init(self):
        super().init()
        # main: log
        v_Layout = QVBoxLayout()
        self.main_widget.setLayout(v_Layout)
        v_Layout.addWidget(self.log_widget)
        # connections
        self.log_message_received.connect(self.__log_message)

    def log_message(self, message: str, timeout_milliseconds: int = 2000):
        self.log_message_received.emit(message)
        self.app.show_status_message(message, timeout_milliseconds)

    def __log_message(self, message: str):
        QListWidgetItem(message, self.log_widget)
        self.log_widget.scrollToBottom()


class ChessboardAndLogModule(LogModule):

    def __init__(self, app, display_name: str, actions: [QAction]):
        super().__init__(app, display_name, actions)
        self.chess_board_widget = ChessBoardWidget()
        self.chess_board_widget.piece_movement_observer.append(
            self.on_piece_movement)

    def init(self):
        super().init()
        # reset main widget because it is used differently in LogModule. also reset parent of log widget so that it is not deleted when
        # the main widget is deleted/removed as a child
        self.log_widget.setParent(None)
        QWidget().setLayout(self.main_widget.layout())
        # main: left chess board, right log
        h_Layout = QHBoxLayout()
        self.main_widget.setLayout(h_Layout)
        h_Layout.addWidget(self.chess_board_widget)
        h_Layout.addWidget(self.log_widget)

    def on_piece_movement(self, piece_movement: PieceMovement):
        pass

    def on_focus(self):
        super().on_focus()
        self.chess_board_widget.grabKeyboard()


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
