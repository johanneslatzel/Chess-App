from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLayout, QStackedWidget, QToolBar, QHBoxLayout, QSizePolicy, QLabel
from chessapp.util.paths import get_icons_folder
from os.path import join


class SidebarElement():

    def __init__(self, display_widget: QWidget, icon_file_name: str) -> None:
        self.icon: QIcon = QIcon(join(get_icons_folder(), icon_file_name))
        self.display_widget: QWidget = display_widget


class MainWidget(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.stacked_widget: QStackedWidget = QStackedWidget()
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        layout: QLayout = QHBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    def add_sidebar_element(self, element: SidebarElement):
        index: int = self.stacked_widget.addWidget(element.display_widget)
        if element.icon:
            action = self.toolbar.addAction(element.icon, "")
        else:
            action = self.toolbar.addAction(element.display_text)
        action.triggered.connect(
            lambda: self.stacked_widget.setCurrentIndex(index))
