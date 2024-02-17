from PyQt5.QtWidgets import QApplication
from chessapp.view.appwindow import AppWindow
from chessapp.model.chesstree import ChessTree
from PyQt5.QtCore import QThreadPool
from chessapp.sound.chessboardsound import register_all_sounds


class ChessApp(QApplication):
    """ This is the main application and derives from QApplication. It handles the main window (View) and all the modules (Controller).
    The app also has a threadpool that can be used to dispatch tasks on non-GUI threads.
    """

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
        register_all_sounds()

    def close(self):
        """ closes the application and all modules.
        """
        if self.is_closed:
            return
        self.is_closed = True
        self.deleteLater()
