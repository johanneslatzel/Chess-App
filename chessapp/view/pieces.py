from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import QPoint, QSize
from os.path import join
from chessapp.util.paths import get_chess_pieces_folder
from enum import Enum


class PieceColor(Enum):
    """color of a chess piece: white (w) or black (b)
    """
    WHITE = "w"
    BLACK = "b"


class PieceType(Enum):
    """representation of the different chess pieces: queen (q), king (k), rook (r), knight (n), bishop (b) and pawn (p)
    """
    QUEEN = "q"
    KING = "k"
    ROOK = "r"
    KNIGHT = "n"
    BISHOP = "b"
    PAWN = "p"


class ChessPiece():
    """ This is the abstract base class for chess pieces. It tries to load a png file from the chess_pieces folder with the name <piece_color><piece_type>.png
    and draws this image on the given position with the given dimensions. Known subclasses are Queen, King, Rook, Knight, Bishop and Pawn that are all
    located within chessapp.view.pieces.
    """

    def __init__(self, piece_color: PieceColor, piece_type: PieceType):
        """ Creates a new instance of a ChessPiece. Don't instantiate this class directly, use one of the subclasses instead.

        Args:
            piece_color (PieceColor): color of the piece (e.g. black or white)
            piece_type (PieceType): type of the piece (e.g. queen, rook, pawn, ...)
        """
        self.piece_color: PieceColor = piece_color
        self.piece_type: PieceType = piece_type
        self.pixmap: QPixmap = None

    def load_pixmap(self):
        self.pixmap = QPixmap(join(get_chess_pieces_folder(), str(
            self.piece_color.value) + str(self.piece_type.value) + ".png"))

    def drawOn(self, qp: QPainter, position: QPoint, dimension: QSize):
        """draws the piece on the given position with the given dimensions. if load_pixmap was not called before, this method cannot draw anything.

        Args:
            qp (QPainter): QPainter of the GUI
            position (QPoint): position of the piece (x, y upper left corner)
            dimension (PieceDimenson): dimensions of the piece (width and height)
        """
        if self.pixmap:
            qp.drawPixmap(position.x(), position.y(), dimension.width, dimension.height,
                          self.pixmap, 0, 0, 300, 300)


class Queen(ChessPiece):
    def __init__(self, piece_color: PieceColor):
        super().__init__(piece_color, PieceType.QUEEN)


class King(ChessPiece):
    def __init__(self, piece_color: PieceColor):
        super().__init__(piece_color, PieceType.KING)


class Rook(ChessPiece):
    def __init__(self, piece_color: PieceColor):
        super().__init__(piece_color, PieceType.ROOK)


class Knight(ChessPiece):
    def __init__(self, piece_color: PieceColor):
        super().__init__(piece_color, PieceType.KNIGHT)


class Bishop(ChessPiece):
    def __init__(self, piece_color: PieceColor):
        super().__init__(piece_color, PieceType.BISHOP)


class Pawn(ChessPiece):
    def __init__(self, piece_color: PieceColor):
        super().__init__(piece_color, PieceType.PAWN)


"""this is a map that maps a letter to a chess piece. The letter is the first letter of the piece type (e.g. "r" for rook, "q" for queen, ...) except
for knights which start with "n" and not "k" because "k" is the king. The letter is lower case for black pieces and upper case for white pieces.
"""
LETTER_MAP = {
    "r": Rook(PieceColor.BLACK),
    "R": Rook(PieceColor.WHITE),
    "n": Knight(PieceColor.BLACK),
    "N": Knight(PieceColor.WHITE),
    "k": King(PieceColor.BLACK),
    "K": King(PieceColor.WHITE),
    "q": Queen(PieceColor.BLACK),
    "Q": Queen(PieceColor.WHITE),
    "b": Bishop(PieceColor.BLACK),
    "B": Bishop(PieceColor.WHITE),
    "p": Pawn(PieceColor.BLACK),
    "P": Pawn(PieceColor.WHITE)
}


def load_pieces():
    """loads all the pixmaps of the chess pieces
    """
    for piece in LETTER_MAP.values():
        piece.load_pixmap()


def get_piece_from(letter: str) -> ChessPiece | None:
    """returns the chess piece that is mapped by LETTER_MAP to the given letter (e.g. "r" for black rook, "Q" for white queen, ...)

    Args:
        letter (str): the letter that is mapped to a chess piece

    Raises:
        Exception: if the letter is not mapped to a chess piece

    Returns:
        None: if the letter is not mapped to a chess piece
        ChessPiece: the chess piece that is mapped to the given letter
    """
    if not letter in LETTER_MAP:
        return None
    return LETTER_MAP[letter]
