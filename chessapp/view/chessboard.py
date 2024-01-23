from chessapp.view.pieces import get_piece_from, ChessPiece
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QRect, QPoint, QSize
from PyQt5.QtGui import QPainter, QPixmap
from enum import Enum
from chessapp.view.arrow import Arrow
from chessapp.configuration import SQUARE_ICON_SQUARE_PERCENTAGE
from os.path import join
from chessapp.util.paths import get_images_folder


s_square_icon_source_width: int = 64
s_square_icon_source_height: int = 64


class SquareIconType(Enum):
    BEST_MOVE = 1
    ONLY_MOVE = 2
    BRILLIANT_MOVE = 3
    GOOD_MOVE = 4
    INACCURACY = 5
    BLUNDER = 6
    BOOK_MOVE = 7
    EXCELLENT_MOVE = 8
    MISTAKE = 9

    def sformat(self):
        return str(self).replace("SquareIconType.", "")

    def from_cp_loss(cp_loss: int, is_book: bool, is_best_known: bool):
        if cp_loss <= 35 and is_book:
            return SquareIconType.BOOK_MOVE
        if SquareIconType.is_best(cp_loss, is_best_known):
            return SquareIconType.BEST_MOVE
        if cp_loss <= 15:
            return SquareIconType.EXCELLENT_MOVE
        if cp_loss <= 25:
            return SquareIconType.GOOD_MOVE
        if cp_loss <= 40:
            return SquareIconType.INACCURACY
        if cp_loss <= 99:
            return SquareIconType.MISTAKE
        return SquareIconType.BLUNDER

    def is_best(cp_loss: int, is_best_known: bool) -> bool:
        return cp_loss == 0 or is_best_known and cp_loss <= 10


class SquareIcon:
    def __init__(self, square_icon_type: SquareIconType):
        self.path = join(get_images_folder(), "chessboard", "square_icon",
                         square_icon_type.sformat().lower() + ".png")
        self.icon = QPixmap(self.path)

    def drawOn(self, qp: QPainter, pos: QPoint, dim: QSize):
        target_width = int(SQUARE_ICON_SQUARE_PERCENTAGE * dim.width)
        target_height = int(SQUARE_ICON_SQUARE_PERCENTAGE * dim.height)
        qp.drawPixmap(pos.x() + dim.width - target_width, pos.y(), target_width, target_height,
                      self.icon, 0, 0, s_square_icon_source_width, s_square_icon_source_height)


class ChessBoard:
    def __init__(self):
        self.icon_map = {}
        self.white_square_color = QColor(228, 238, 210, 255)
        self.black_square_color = QColor(118, 150, 86, 255)
        self.red_square_color = QColor(255, 0, 0, 255)
        self.ascii_board: str = """r n b q k b n r
p p p p p p p p
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
P P P P P P P P
R N B Q K B N R"""
        self.flip_board: bool = True
        self.enable_piece_to_cursor: bool = False
        self.mouse_x: float = 0
        self.mouse_y: float = 0
        self.active_piece = None
        self.active_piece_origin: str = ""
        self.legal_moves = []
        self.active_piece_legal_move_destinations = []
        self.last_move_cp_loss: int = 0
        self.last_move_source: str = ""
        self.last_move_destination: str = ""
        self.last_move_is_book: bool = False
        self.last_move_is_best_known: bool = False
        self.node_depth: int = 0
        self.best_move: str = None
        self.show_best_move: bool = False
        self.best_move_cp_loss: int = 0
        self.show_last_move_arrow: bool = True
        self.show_last_move_icon: bool = True
        self.init_icon_map()

    def init_icon_map(self):
        for icon_type in SquareIconType:
            self.icon_map[icon_type] = SquareIcon(icon_type)

    def coords_to_square(self, x, y, width, height):
        square_row = ""
        square_col = ""
        row = 8 * y // height
        col = 8 * x // width
        if self.flip_board:
            square_row = str(row + 1)
            square_col = chr(ord("h") - col)
        else:
            square_row = str(8 - row)
            square_col = chr(ord("a") + col)
        return square_col + square_row

    def square_to_coords(self, square, widht, height):
        piece_width = widht // 8
        piece_height = height // 8
        row = 8 - int(square[1])
        col = ord(square[0]) - ord("a")
        if self.flip_board:
            col = 7 - col
            row = 7 - row
        x = col * piece_width
        y = row * piece_height
        return x, y

    def select_piece(self, x, y, width, height):
        row = 8 * y // height
        col = 8 * x // width
        if self.flip_board:
            row = 7 - row
            col = 7 - col
        self.active_piece_origin = self.coords_to_square(x, y, width, height)
        self.active_piece = get_piece_from(
            self.ascii_board.split("\n")[row].split(" ")[col])
        self.active_piece_legal_move_destinations = []
        if not self.legal_moves:
            return
        for move in self.legal_moves:
            if str(move).startswith(self.active_piece_origin):
                self.active_piece_legal_move_destinations.append(
                    str(move)[2:])

    def flip(self):
        self.flip_board = not self.flip_board

    def view_black(self):
        self.flip_board = True

    def view_white(self):
        self.flip_board = False

    def is_active_piece(self, row: int, col: int) -> bool:
        return self.active_piece and self.active_piece_origin and col == (ord(self.active_piece_origin[0]) - ord('a')) and row == (int(self.active_piece_origin[1]) - 1)

    def should_draw_active_piece(self) -> bool:
        return self.active_piece and len(self.active_piece_legal_move_destinations) > 0

    def drawOn(self, qp: QPainter, bound: QRect):
        dim = QSize()
        dim.width = bound.width() // 8
        dim.height = bound.height() // 8
        self.draw_squares(qp, bound, dim)
        self.draw_pieces(qp, bound, dim)
        self.draw_last_move_arrow(qp, bound, dim)
        self.draw_best_move_arrow(qp, bound, dim)
        self.draw_square_icon_last_move(qp, bound, dim)
        self.draw_piece_movement(qp, bound, dim)

    def draw_squares(self, qp: QPainter, bound: QRect, dim: QSize):
        square_color = None
        for row in range(0, 8):
            for col in range(0, 8):
                square_color = self.black_square_color if row % 2 == col % 2 else self.white_square_color
                if (not self.flip_board and self.is_active_piece(row, col)) or (self.flip_board and self.is_active_piece(7 - row, 7 - col)):
                    square_color = self.red_square_color
                qp.fillRect(col * dim.width + bound.x(), (7 - row) * dim.height + bound.y(),
                            dim.width, dim.height, square_color)

    def draw_pieces(self, qp: QPainter, bound: QRect, dim: QSize):
        rows = self.ascii_board.split("\n")
        for i in range(0, 8):
            row = rows[i].split(" ")
            for j in range(0, 8):
                piece: ChessPiece = get_piece_from(row[j])
                i_value = i
                j_value = j
                if self.flip_board:
                    i_value = 7 - i
                    j_value = 7 - j
                if piece and not (self.is_active_piece(7 - i, j) and self.should_draw_active_piece()):
                    piece.drawOn(qp, QPoint(
                        dim.width * j_value + bound.x(), dim.height * i_value + bound.y()), dim)

    def draw_last_move_arrow(self, qp: QPainter, bound: QRect, dim: QSize):
        if not self.last_move_source or not self.last_move_destination:
            return
        sx, sy = self.square_to_coords(
            self.last_move_source, bound.width(), bound.height())
        dx, dy = self.square_to_coords(
            self.last_move_destination, bound.width(), bound.height())
        arrow = Arrow(QPoint(sx, sy), QPoint(dx, dy))
        arrow.width = min(dim.width, dim.height) / 10
        arrow.arrow_head_scale = 1.1
        arrow.arrow_head_length_scale = 1.3
        arrow.color = QColor(252, 186, 3, 192)
        arrow.indentation = 0.4
        arrow.drawOn(qp, bound, dim)

    def draw_best_move_arrow(self, qp: QPainter, bound: QRect, dim: QSize):
        if not self.show_best_move or not self.best_move or not SquareIconType.is_best(self.best_move_cp_loss, True) or not self.show_last_move_arrow:
            return
        sx, sy = self.square_to_coords(
            self.best_move[:2], bound.width(), bound.height())
        dx, dy = self.square_to_coords(
            self.best_move[2:], bound.width(), bound.height())
        arrow = Arrow(QPoint(sx, sy), QPoint(dx, dy))
        arrow.width = min(dim.width, dim.height) / 5
        arrow.drawOn(qp, bound, dim)

    def draw_square_icon_last_move(self, qp: QPainter, bound: QRect, dim: QSize):
        if not self.last_move_destination or self.node_depth <= 0 or not self.show_last_move_icon:
            return
        x, y = self.square_to_coords(
            self.last_move_destination, bound.width(), bound.height())
        self.icon_map[SquareIconType.from_cp_loss(self.last_move_cp_loss, self.last_move_is_book, self.last_move_is_best_known)].drawOn(
            qp, QPoint(bound.x() + x, bound.y() + y), dim)

    def draw_piece_movement(self, qp: QPainter, bound: QRect, dim: QSize):
        if not self.should_draw_active_piece() or not self.enable_piece_to_cursor:
            return
        # draw possible destinations
        for destination in self.active_piece_legal_move_destinations:
            x, y = self.square_to_coords(
                destination, bound.width(), bound.height())
            qp.setPen(QColor(0, 0, 0, 255))
            qp.drawEllipse(QPoint(x + bound.x() + dim.width // 2, y + bound.y() + dim.height // 2),
                           dim.width // 6, dim.height // 6)
            qp.drawEllipse(QPoint(x + bound.x() + dim.width // 2, y + bound.y() + dim.height // 2),
                           dim.width // 5, dim.height // 5)
        # draw piece itself
        self.active_piece.drawOn(qp, QPoint(
            int(self.mouse_x - (dim.width / 2)), int(self.mouse_y - (dim.height / 2))), dim)

    def get_preferred_length(self, length: int) -> int:
        return 8 * (length // 8)
