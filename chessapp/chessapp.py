from PyQt5.QtWidgets import QApplication, QWidget
from chessapp.view.appwindow import AppWindow, StatusMessage
from chessapp.controller.updater import Updater
from chessapp.controller.saver import Saver
from chessapp.controller.quiz import Quiz
from chessapp.model.chesstree import ChessTree
from PyQt5.QtCore import QThreadPool, pyqtSignal
from chessapp.controller.analyser import Analyser
from chessapp.controller.explorer import Explorer
from chessapp.view.module import BaseModule
from chessapp.controller.openingtree import OpeningTree
from chessapp.controller.puzzles import Puzzles
from chessapp.sound.chessboardsound import register_all_sounds


class ChessApp(QApplication):
    """ This is the main application and derives from QApplication. It handles the main window (View) and all the modules (Controller).
    The app also has a threadpool that can be used to dispatch tasks on non-GUI threads.
    """

    changing_central_widget = pyqtSignal(QWidget)

    def __init__(self, tree: ChessTree, argv: list[str]):
        """ initialises the application. This should be called by the main method of the application and only by that method.


        Args:
            tree (ChessTree): the tree that should be used by the application
            argv (list[str]): arguments passed to the application by the command line/shell/operating system/parent process/...
        """
        super().__init__(argv)
        # set this at the start so other parts of the program work already before this construtor is finished...
        self.is_closed = False
        self.threadpool = QThreadPool()
        self.window = AppWindow(self)
        self.window.showMaximized()
        opening_tree = OpeningTree(self)
        explorer = Explorer(self, tree)
        self.modules: [BaseModule] = [
            Analyser(self, tree),
            explorer,
            opening_tree,
            Puzzles(self, explorer, tree),
            Saver(self, tree),
            Updater(self, tree),
            Quiz(self, tree, opening_tree, explorer)
        ]
        self.widgets = []
        self.changing_central_widget.connect(self.__set_central_widget)
        # register modules
        for module in self.modules:
            module.init()
            module.register()
        register_all_sounds()

    def unfocus_all_modules(self):
        """ call this method to assure that no module is focused. @See BaseModule.focus for more information.
        """
        for module in self.modules:
            module.unfocus()

    def set_central_widget(self, central_widget: QWidget):
        """ sets the central widget of the main window. This is the main method to change the view of the application. The
        change of the central widget is not instantanious. Instead this method dispatches this task onto the GUI thread that
        processes it at some point in the future.

        Args:
            central_widget (QWidget): the widget that should be shown in the main window
        """
        self.changing_central_widget.emit(central_widget)

    def __set_central_widget(self, central_widget: QWidget):
        """ directly changes the central widget of the main window. This method should not be called directly as this is
        a GUI action and should only be called on the GUI thread. Use set_central_widget instead.

        Args:
            central_widget (QWidget): the widget that should be shown in the main window
        """
        if self.window.centralWidget():
            self.window.centralWidget().setParent(None)
        self.window.setCentralWidget(central_widget)

    def show_status_message(self, text: str, timeout_milliseconds: int = 2000):
        """ call this method to show a status message on the bottom of the main window.

        Args:
            text (str): the text that should be shown
            timeout_milliseconds (int, optional): Defaults to 2000. the time in milliseconds after which the message should disappear
        """
        if self.is_closed:
            return
        self.window.status_message_shown.emit(
            StatusMessage(text, timeout_milliseconds))

    def close(self):
        """ closes the application and all modules.
        """
        if self.is_closed:
            return
        self.is_closed = True
        for module in self.modules:
            module.close()
        self.deleteLater()
