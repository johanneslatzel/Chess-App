from PyQt5.QtGui import QPainter, QPainterPath, QColor
from PyQt5.QtCore import QRect, QPoint, QPointF
from chessapp.view.pieces import QSize
from math import sqrt


class Arrow:
    """ An arrow from source to destination point with a given width and color. The arrow can be indented and scaled.
    
    Attributes:
        source (QPoint): source point (root of the arrow)
        destination (QPoint): destination point (tip of the arrow)
        width (int): width of the arrow
        color (QColor): color of the arrow
        indentation (float): indentation of the arrow (0 = no indentation, 1 = full indentation). TODO: describe indentation
        arrow_head_length_scale (float): scale of the arrow head length (0 = no arrow head, 1 = full arrow head)
        arrow_head_width_scale (float): scale of the arrow head width (0 = no arrow head, 1 = full arrow head)
    """

    def __init__(self, source: QPoint, destination: QPoint):
        """ initialize an arrow

        Args:
            source (QPoint): source point (root of the arrow)
            destination (QPoint): destination point (tip of the arrow)
        """
        self.source = source
        self.destination = destination
        self.width = 10
        self.color = QColor(0, 0, 128, 64)
        self.indentation: float = 0
        self.arrow_head_length_scale: float = 1
        self.arrow_head_width_scale: float = 1

    def drawOn(self, qp: QPainter, bound: QRect, offset: QPointF):
        """ draw the arrow on the given painter

        Args:
            qp (QPainter): the painter to draw on
            bound (QRect): the bounding rectangle of the arrow
            offset (QSize): the offset of the arrow
        """
        head_width = self.width * 2 * max(0, self.arrow_head_width_scale)
        sx: float = self.source.x() + bound.x() + offset.x()
        sy: float = self.source.y() + bound.y() + offset.y()
        s = QPointF(sx, sy)
        dx: float = self.destination.x() + bound.x() + offset.x()
        dy: float = self.destination.y() + bound.y() + offset.y()
        d = QPointF(dx, dy)
        vx: float = dx - sx
        vy: float = dy - sy
        length: float = sqrt(vx * vx + vy * vy)
        if length <= head_width:
            return
        if vx == 0:
            ax = 1
            ay = 0
        else:
            ax = vy / length
            ay = -vx / length
        normal_vector = QPointF(ax, ay)
        direction_vector = QPointF(vx / length, vy / length)
        p0 = s + normal_vector * self.width / 2
        p6 = s - normal_vector * self.width / 2
        head_length: float = min(
            head_width * max(0, self.arrow_head_length_scale), 0.5 * length)
        base_length: float = length - head_length
        p1 = p0 + direction_vector * base_length
        p5 = p6 + direction_vector * base_length
        width_head_width_diff: float = head_width - self.width
        p2 = p1 + normal_vector * width_head_width_diff
        p7 = p5 - normal_vector * width_head_width_diff
        # if there is an indentation
        if self.indentation > 0:
            indentation_base_length = length + head_length * \
                (0.5 * max(0, min(1, self.indentation)) - 1)
            p1 = p0 + direction_vector * indentation_base_length
            p5 = p6 + direction_vector * indentation_base_length
        path: QPainterPath = QPainterPath()
        path.moveTo(s)  # center of base and source point
        path.lineTo(p0)  # corner 1 of base
        path.lineTo(p1)  # corner 1 of indentation
        path.lineTo(p2)  # corner 1 of outer head
        path.lineTo(d)  # destination point
        path.lineTo(p7)  # corner 2 of outer head
        path.lineTo(p5)  # corner 2 of indentation
        path.lineTo(p6)  # corner 2 of base
        qp.fillPath(path, self.color)
