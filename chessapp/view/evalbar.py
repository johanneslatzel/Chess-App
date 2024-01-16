from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
from chessapp.model.node import Node
from chessapp.configuration import MAX_EVALBAR_VALUE_ABS


class EvalBar():

    def __init__(self):
        self.width = 0
        self.is_visible = False
        self.node: Node = None
        self.is_flipped = False

    def flip(self):
        self.is_flipped = not self.is_flipped

    def drawOn(self, qp: QPainter, bound: QRect):
        second_color_height_percentage = (
            MAX_EVALBAR_VALUE_ABS - self.node.eval) / (2 * MAX_EVALBAR_VALUE_ABS)
        if self.is_flipped:
            second_color_height_percentage = 1 - second_color_height_percentage
        qp.fillRect(bound.x(), bound.y(), bound.width(), bound.height(
        ), Qt.GlobalColor.black if self.is_flipped else Qt.GlobalColor.white)
        qp.fillRect(bound.x(), bound.y(), bound.width(), int(second_color_height_percentage *
                    bound.height()), Qt.GlobalColor.white if self.is_flipped else Qt.GlobalColor.black)
