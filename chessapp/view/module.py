from PyQt5.QtCore import QRunnable, QObject, Qt
from PyQt5.QtWidgets import QAction, QMenuBar, QMenu, QWidget, QListWidget, QHBoxLayout, QLabel, QVBoxLayout, QListWidgetItem
from PyQt5.QtGui import QFont
from chessapp.view.chessboardwidget import ChessBoardWidget, PieceMovement
from PyQt5.QtCore import pyqtSignal
from chessapp.configuration import DEFAULT_STYLESHEET


class BaseModule(QObject):
    """ A module is a widget that offers the user GUI interactions with the program. It is registered in the menu bar with
    its own menu item whose display name is given by display_name. The menu item has a "Focus" action that makes the modules'
    central_widget the AppWindow's central widget. The central_widget is a QWidget that contains a QVBoxLayout with a header
    label, the main widget and a footer label. The main_widget is a QWidget that contains the main content of the module.

    Only change the content of main_widget or the text of the header_label and footer_label!

    TODO: This class needs to be refactored! The chessapp.controller classes are derived from it which mixes GUI and logic. Instead a controller should be able to offer a GUI-element to the application and interact through it with the user and vice versa.
    """

    def __init__(self, app, display_name: str, actions: list[QAction]) -> None:
        """ initialises the module with the given parameters. The module is not focused after initialisation. After
        initialising this class the method init needs to be called on the GUI thread to finish up the initialisation.

        Args:
            app (ChessApp): the main application
            display_name (str): the name of the module that is displayed in the menu bar
            actions (list[QAction]): a list of actions that are displayed in the menu of the module
        """
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
        """ call this method only once per instance and only on the GUI thread. This method finishes the initialisation of
        the module.
        """
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
        """ this method is only called once by the main application. Don't call this in any other way.
        It registers the module in the menu bar with the "Focus" action and the actions given in the constructor.
        """
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
        """ returns True if the module is about to close or is already closed. Closing happens when the main application
        closes down itself. This method is used as an indicator by deriving classes to determine if it is feasible or
        not to continue actions. Often it is prudent to include this method inside loops to abort actions when the program
        wants to close.

        Returns:
            bool: True if the module is about to close or is already closed
        """
        return self.is_closing or self.is_closed

    def on_register(self):
        """ override this method to react to the registration of the module in the main application.
        """
        pass

    def on_close(self):
        """ override this method to react to the closing of the module.
        """
        pass

    def close(self):
        """ closes the module
        """
        if self.about_to_close():
            return
        self.is_closing = True
        self.on_close()
        # this way around "self.about_to_close()" stays True
        self.is_closed = True
        self.is_closing = False

    def focus(self):
        """ focuses this module by setting its central_widget as the main application's central widget and unfocusing all
        other modules. This method is called by the "Focus" action in the menu bar.
        """
        if self.is_focused:
            return
        self.app.unfocus_all_modules()
        self.app.set_central_widget(self.central_widget)
        self.is_focused = True
        self.on_focus()

    def unfocus(self):
        """ unfocuses this module.
        """
        if not self.is_focused:
            return
        self.is_focused = False
        self.on_unfocus()

    def on_focus(self):
        """ override this method to react to the focusing of the module.
        """
        pass

    def on_unfocus(self):
        """ override this method to react to the unfocusing of the module.
        """
        pass

    def dispatch_threadpool(self, callable):
        """ dispatches the given callable to the threadpool of the main application.

        Args:
            callable (callable): any callable object like a method of an object or a lambda function
        """
        self.app.threadpool.start(MethodAction(callable))


class LogModule(BaseModule):
    """ This derivation adds a log widget to the main widget. The log widget is a QListWidget that displays log messages.
    """

    log_message_received = pyqtSignal(str)

    def __init__(self, app, display_name: str, actions: list[QAction]):
        """ basically only calls the constructor of BaseModule and initialises the log widget.

        Args:
            app (ChessApp): the main application
            display_name (str): the name of the module that is displayed in the menu bar
            actions (list[QAction]): the actions that are displayed in the menu of the module
        """
        super().__init__(app, display_name, actions)
        self.log_widget = QListWidget()

    def init(self):
        """ @see BaseModule.init. Adds the log widget to the main widget.
        """
        super().init()
        # main: log
        v_Layout = QVBoxLayout()
        self.main_widget.setLayout(v_Layout)
        v_Layout.addWidget(self.log_widget)
        # connections
        self.log_message_received.connect(self.__log_message)

    def log_message(self, message: str, timeout_milliseconds: int = 2000):
        """ logs the given message in the log widget and shows it as a status message in the status bar of the main application.

        Args:
            message (str): the message to log
            timeout_milliseconds (int, optional): the timeout of the status message in milliseconds.
        """
        self.log_message_received.emit(message)
        self.app.show_status_message(message, timeout_milliseconds)

    def __log_message(self, message: str):
        """ internal method that is called by the GUI thread when a new status message is received.

        Args:
            message (str): the message to log
        """
        QListWidgetItem(message, self.log_widget)
        self.log_widget.scrollToBottom()


class ChessboardAndLogModule(LogModule):
    """ This derivation adds a ChessBoardWidget left of the log widget as a sort of split-screen. Override
    on_piece_movement and on_back to react to the user's actions on the chess board.
    """

    def __init__(self, app, display_name: str, actions: list[QAction]):
        """ basically only calls the constructor of LogModule and initialises the ChessBoardWidget.

        Args:
            app (ChessApp): the main application
            display_name (str): the name of the module that is displayed in the menu bar
            actions (list[QAction]): the actions that are displayed in the menu of the module
        """
        super().__init__(app, display_name, actions)
        self.chess_board_widget = ChessBoardWidget()
        self.chess_board_widget.piece_movement_observer.append(
            self.on_piece_movement)
        self.chess_board_widget.back_actions.append(
            self.on_back)

    def init(self):
        """ @see LogModule.init. Adds the ChessBoardWidget to the main widget. In order to show the ChessBoardWidget
        split-screen the log widget first needs to be removed from the main_widget and then placed inside it again.
        TODO: change this behaviour so that the log widget is not removed and placed inside the main widget again.
        """
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
        """ this method is called when a piece has been move by the user on the chess board. Override this method
        to react to this user input.

        Args:
            piece_movement (PieceMovement): the piece movement that has been performed
        """
        pass

    def on_back(self):
        """ this method is called when the user presses the back button on the chess board. Override this method
        to react to this user input.
        """
        pass

    def on_focus(self):
        """ @see LogModule.on_focus. This method grabs the keyboard so that the ChessBoardWidget can receive keyboard
        input by the user.
        """
        super().on_focus()
        self.chess_board_widget.grabKeyboard()


class MethodAction(QRunnable):
    """ This class is used to dispatch a method to the threadpool of the main application.
    """

    def __init__(self, method):
        """ initialises the MethodAction with the given method.

        Args:
            method (callable): any callable object like a method of an object or a lambda function
        """
        super().__init__()
        self.method = method

    def run(self):
        """ runs the method that was given in the constructor.
        """
        self.method()


def create_method_action(app, display_name: str, method):
    """ helper function to create a QAction that calls the given method when triggered.

    Args:
        app (ChessApp): the main application
        display_name (str): the name of the action that is displayed in the menu
        method (callable): the method that is called when the action is triggered

    Returns:
        MethodAction: the QAction that calls the given method when triggered
    """
    method_action = QAction("&" + display_name)
    method_action.triggered.connect(
        lambda: app.threadpool.start(MethodAction(method)))
    return method_action
