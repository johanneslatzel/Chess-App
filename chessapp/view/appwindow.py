from PyQt5.QtWidgets import QMainWindow
from chessapp.view.mainwidget import MainWidget
from chessapp.view.modules.explorer import Explorer


class AppWindow(QMainWindow):
    """The main window of the application.
    """

    def __init__(self, app):
        """initializes the main window of the application

        Args:
            app (chessapp.chessapp.Chessapp): the main application
        """
        super().__init__()
        self.app = app
        self.setWindowTitle("Chess App")
        self.main_widget = MainWidget()
        explorer = Explorer()
        self.main_widget.add_sidebar_element(explorer.sidebar_element)
        self.setCentralWidget(self.main_widget)
        self.showMaximized()
