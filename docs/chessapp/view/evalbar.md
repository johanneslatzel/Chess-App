# evalbar

::: chessapp.view.evalbar.EvalBar
    options:
        show_root_heading: true
        show_source: true

# Source
```python
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QRect, QSize, Qt
from chessapp.model.node import Node
from chessapp.configuration import MAX_EVALBAR_VALUE_ABS
from chessapp.util.font import find_font_size


class EvalBar():
    """ This class represents the evalbar of a chessboard. It is drawn on the left side of the chessboard
    and shows the evaluation of the current position. The evaluation is shown by a bar with coloring
    proportionally to the evaluation. In the center of the bar the evaluation is shown as text. The size of
    the text is chosen so that it fits into the bar (scaling fits). The bar is usually flipped if the chessboard
    gets flipped.
    """

    def __init__(self):
        """ Initializes the evalbar.
        """
        self.width = 0
        self.is_visible = False
        self.node: Node = None
        self.is_flipped = False

    def flip(self):
        """ Flips the evalbar. If the evalbar is flipped then white is on top and black on bottom. otherwise
        black is on top and white on bottom.
        """
        self.is_flipped = not self.is_flipped

    def drawOn(self, qp: QPainter, bound: QRect):
        """ Draws the evalbar on the given painter within the given bounds.

        Args:
            qp (QPainter): the painter to draw on
            bound (QRect): the bounds to draw in
        """
        # draw evalbar itself
        second_color_height_percentage = (
            MAX_EVALBAR_VALUE_ABS - self.node.eval) / (2 * MAX_EVALBAR_VALUE_ABS)
        if self.is_flipped:
            second_color_height_percentage = 1 - second_color_height_percentage
        qp.fillRect(bound.x(), bound.y(), bound.width(), bound.height(
        ), Qt.GlobalColor.black if self.is_flipped else Qt.GlobalColor.white)
        qp.fillRect(bound.x(), bound.y(), bound.width(), int(second_color_height_percentage *
                    bound.height()), Qt.GlobalColor.white if self.is_flipped else Qt.GlobalColor.black)
        # draw evalbar text
        font = qp.font()
        eval_text: str = str(self.node.eval)
        if self.node.eval > 0:
            eval_text = "+" + eval_text
        elif self.node.eval == 0:
            eval_text = "=0.00"
        size = find_font_size(
            QSize(bound.width(), bound.height()), eval_text)
        font.setPointSize(size)
        qp.setFont(font)
        qp.drawText(bound, Qt.AlignCenter, eval_text)
```
