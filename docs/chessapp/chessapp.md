# chessapp

::: chessapp.chessapp.ChessApp
    options:
        show_root_heading: true
        show_source: true

# Source
```python
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

    changing_central_widget = pyqtSignal(QWidget)

    def __init__(self, tree: ChessTree, argv):
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
        self.register_modules()
        self.widgets = []
        self.changing_central_widget.connect(self.__set_central_widget)
        register_all_sounds()

    def register_modules(self):
        for module in self.modules:
            module.init()
            module.register()

    def unfocus_all_modules(self):
        for module in self.modules:
            module.unfocus()

    def set_central_widget(self, central_widget: QWidget):
        self.changing_central_widget.emit(central_widget)

    def __set_central_widget(self, central_widget):
        if self.window.centralWidget():
            self.window.centralWidget().setParent(None)
        self.window.setCentralWidget(central_widget)

    def explore(self, piece_move_callback):
        self.window.piece_move_callback = piece_move_callback

    def show_status_message(self, text: str, timeout_milliseconds: int = 2000):
        if self.is_closed:
            return
        self.window.status_message_shown.emit(
            StatusMessage(text, timeout_milliseconds))

    def close(self):
        if self.is_closed:
            return
        self.is_closed = True
        for module in self.modules:
            module.close()
        self.deleteLater()
```
