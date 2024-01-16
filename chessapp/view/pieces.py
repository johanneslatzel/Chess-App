from PyQt5.QtGui import QPainter, QPixmap
from os.path import join
from chessapp.util.paths import get_chess_pieces_folder


class PiecePosition():
    def __init__(self, x, y):
        self.x = x
        self.y = y


class PieceDimenson():
    def __init__(self):
        self.width = 0
        self.height = 0


class ChessPiece():
    def __init__(self, piece_color, piece_type):
        self.piece_type = piece_type
        self.piece_color = piece_color
        self.piece = QPixmap(
            join(get_chess_pieces_folder(), piece_color + piece_type + ".png"))

    def drawOn(self, qp: QPainter, pos: PiecePosition, dim: PieceDimenson):
        qp.drawPixmap(pos.x, pos.y, dim.width, dim.height,
                      self.piece, 0, 0, 300, 300)

    def __str__(self) -> str:
        return self.piece_color + " " + self.piece_type


class Queen(ChessPiece):
    def __init__(self, piece_color):
        super().__init__(piece_color, "q")


class King(ChessPiece):
    def __init__(self, piece_color):
        super().__init__(piece_color, "k")


class Rook(ChessPiece):
    def __init__(self, piece_color):
        super().__init__(piece_color, "r")


class Knight(ChessPiece):
    def __init__(self, piece_color):
        super().__init__(piece_color, "n")


class Bishop(ChessPiece):
    def __init__(self, piece_color):
        super().__init__(piece_color, "b")


class Pawn(ChessPiece):
    def __init__(self, piece_color):
        super().__init__(piece_color, "p")
