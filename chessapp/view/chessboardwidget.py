import chess
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QPainter, QPaintEvent
from PyQt5.QtCore import QRect, Qt, QSize
from PyQt5.QtWidgets import QWidget
from chessapp.view.chessboard import ChessBoard
from chess import Board
from chessapp.view.evalbar import EvalBar
from chessapp.model.node import Node
import chessapp.model.move
from chessapp.model.sourcetype import SourceType
from chessapp.sound.chessboardsound import ChessboardSound
import traceback
from dataclasses import dataclass

s_size_scale = 100
s_width_hint = 8 * s_size_scale
s_height_hint = s_width_hint
s_eval_bar_min_width = 10
s_min_depth_best_move = 20


@dataclass
class PieceMovement():
    """ represents a move on a chessboard of a piece from a source square to a destination square
    """
    source_square: str
    destination_square: str

    def uci_format(self) -> str:
        """ returns the move in UCI format

        Returns:
            str: the move in UCI format
        """
        return self.source_square + self.destination_square


class ChessBoardWidget(QWidget):
    """ a widget that displays a chessboard and allows to play moves. It also displays an eval bar if enabled.
    """

    def __init__(self):
        """ constructor for the ChessBoardWidget class. It initializes the chessboard and the eval bar.
        """
        super().__init__()
        self.board = ChessBoard()
        self.last_press_x = 0
        self.last_press_y = 0
        self.piece_movement_observer = []
        self.back_actions = []
        self.eval_bar = EvalBar()

    def sizeHint(self) -> QSize:
        """ returns the size hint for the widget that is used to calculate the size of the widget

        Returns:
            QSize: the size hint for the widget
        """
        return QSize(s_width_hint, s_height_hint)

    def get_board_length(self) -> int:
        """ the length of the board is the minimum of the width and the height of the widget (the evalbar width is also respected).
        the length then is used as a width and height of the bounding box of the chessboard.

        Returns:
            int: the length of the board
        """
        return 8 * (min(self.width() - self.eval_bar.width, self.height()) // 8)

    def paintEvent(self, event: QPaintEvent):
        """ paints the widget and is called when the widget needs to be updated

        Args:
            event (QPaintEvent): the paint event
        """
        qp = QPainter(self)
        qp.fillRect(0, 0, self.width(), self.height(), Qt.GlobalColor.black)
        # make sure there is enough width for an eval bar
        if self.eval_bar.is_visible and self.width() > 2 * s_eval_bar_min_width:
            self.eval_bar.width = max(
                s_eval_bar_min_width, int(self.width() * 0.03))
            self.eval_bar.drawOn(
                qp, QRect(0, 0, self.eval_bar.width, self.get_board_length()))
        else:
            self.eval_bar.width = 0
        self.board.drawOn(qp, QRect(self.eval_bar.width, 0,
                          self.get_board_length(), self.get_board_length()))

    def display(self, board: Board, node: Node = None, previous_node: Node = None, last_move: chessapp.model.move.Move = None, show_last_move_icon: bool = True, last_move_is_opponent_move: bool = False, play_sound: bool = False):
        """ displays the chessboard in a way that is compatible with the given board.

            TODO: refactor the playing of sound. The sound should not be depend on when the move is displayed but when the move is played.

        Args:
            board (Board): the board to display
            node (Node, optional): used to display the eval bar (e.g. evaluation value)
            previous_node (Node, optional): used to calculate the last move cp loss to display corresponding last move icon (e.g. best move, blunder, etc.)
            last_move (chessapp.model.move.Move, optional): the last move that was played (used together with previous_node to calculate the last move cp loss)
            show_last_move_icon (bool, optional): True if the last move icon should be displayed.
            last_move_is_opponent_move (bool, optional): true if the last move played was the opponent's move.
            play_sound (bool, optional): true if a sound should be played when the last move is displayed.
        """
        self.board.ascii_board = str(board)
        self.board.legal_moves = []
        for move in board.legal_moves:
            self.board.legal_moves.append(move)
        self.eval_bar.node = node
        self.board.last_move_source = None
        self.board.last_move_destination = None
        self.board.last_move_is_best_known = False
        self.board.last_move_is_book = False
        self.board.best_move = None
        self.board.show_last_move_icon = show_last_move_icon
        if node:
            move = node.get_best_move(min_depth=s_min_depth_best_move)
            if move:
                self.board.best_move = board.uci(board.parse_san(move.san))
                self.board.best_move_cp_loss = node.get_cp_loss(move)
        if previous_node and last_move:
            previous_board = Board(previous_node.state)
            try:
                self.board.last_move_cp_loss = previous_node.get_cp_loss(
                    last_move)
                # https://www.reddit.com/r/ComputerChess/comments/qisai2/conversion_from_algebraic_notation_to_uci_notation/
                uci_text = previous_board.push_san(last_move.san).uci()
                self.board.last_move_destination = uci_text[2:]
                self.board.last_move_source = uci_text[0:2]
            except:
                print("error while trying to set SquareIcon associated with last move")
                print(traceback.format_exc())
            equivalent_move = previous_node.get_equivalent_move(last_move)
            if equivalent_move:
                last_move = equivalent_move
            self.board.last_move_is_book = last_move.source == SourceType.BOOK
            # can be None if no move is known
            previous_node_best_move = previous_node.get_best_move()
            self.board.last_move_is_best_known = previous_node_best_move and previous_node_best_move.is_equivalent_to(
                last_move)
            if node:
                self.board.node_depth = node.eval_depth
        self.update()
        # play move sound
        if play_sound:
            if last_move and "#" in last_move.san:
                ChessboardSound.GAME_END.play()
            elif last_move and "+" in last_move.san:
                ChessboardSound.MOVE_CHECK.play()
            elif last_move and "-" in last_move.san:
                ChessboardSound.MOVE_CASTLE.play()
            elif last_move and "x" in last_move.san:
                ChessboardSound.CAPTURE_PIECE.play()
            elif last_move_is_opponent_move:
                ChessboardSound.MOVE_OPPONENT.play()
            else:
                ChessboardSound.MOVE_SELF.play()

    def flip_board(self):
        """ flips the board and the eval bar
        """
        self.board.flip()
        self.eval_bar.flip()
        self.update()

    def view_white(self):
        """ sets the perspective to white

        TODO: is this even needed?
        """
        self.perspective("w")

    def view_black(self):
        """ sets the perspective to black

        TODO: is this even needed?
        """
        self.perspective("b")

    def perspective(self, perspective: str):
        """ sets the perspective of the board

        TODO: is this even needed?

        Args:
            perspective (str): "w" for white, "b" for black
        """
        self.board.flip_board = perspective != "w"
        self.eval_bar.is_flipped = perspective != "w"
        self.update()

    def is_inside_bounding_box(self, event: QMouseEvent) -> bool:
        """ checks if the event is inside the bounding box of the chessboard

        Args:
            event (QMouseEvent): the mouse event

        Returns:
            bool: true if the event is inside the bounding box of the chessboard
        """
        return self.eval_bar.width < event.x() and event.x() < self.get_board_length(
        ) + self.eval_bar.width and event.y() < self.get_board_length() and event.y() >= 0

    def keyReleaseEvent(self, key_event: QKeyEvent) -> None:
        """ handles the key release event. If the left arrow key or the backspace key is pressed, the back actions are executed.

        Args:
            key_event (QKeyEvent): the key event
        """
        if key_event.key() == Qt.Key.Key_Left or key_event.key() == Qt.Key.Key_Backspace:
            for back_action in self.back_actions:
                back_action()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """ handles the mouse press event. If the left mouse button is pressed, the piece is selected if it is inside the bounding box of the chessboard.

        Args:
            event (QMouseEvent): the mouse event
        """
        self.board.mouse_x = event.x()
        self.board.mouse_y = event.y()
        if self.is_inside_bounding_box(event) and event.button() == Qt.MouseButton.LeftButton:
            self.board.select_piece(event.x() - self.eval_bar.width, event.y(),
                                    self.get_board_length(), self.get_board_length())
        self.board.enable_piece_to_cursor = True
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """ handles the mouse release event. If the left mouse button is released, the piece is moved if it is inside
        the bounding box of the chessboard and the destination square is not the current square of the piece. If the
        squares are the same then the peice is "clicked" and selected. This is used to display legal moves of the piece.
        If the piece is actually moved then the piece movement observers are called.

        Args:
            event (QMouseEvent): the mouse event
        """
        self.board.mouse_x = event.x()
        self.board.mouse_y = event.y()
        self.board.enable_piece_to_cursor = False
        self.board.active_piece = None
        if self.is_inside_bounding_box(event) and event.button() == Qt.MouseButton.LeftButton:
            piece_movement = PieceMovement(self.board.active_piece_origin, self.board.coords_to_square(
                event.x() - self.eval_bar.width, event.y(), self.get_board_length(), self.get_board_length()))
            if piece_movement.source_square != piece_movement.destination_square:
                if chess.Move.from_uci(piece_movement.uci_format()) in self.board.legal_moves:
                    for observer in self.piece_movement_observer:
                        observer(PieceMovement(self.board.active_piece_origin, self.board.coords_to_square(
                            event.x() - self.eval_bar.width, event.y(), self.get_board_length(), self.get_board_length())))
                else:
                    ChessboardSound.MOVE_ILLEGAL.play()
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """ handles the mouse move event. the position of the mouse is saved to handle the piece movement before the mouse
        is released (e.g. drag and drop)

        Args:
            event (QMouseEvent): the mouse event
        """
        self.board.mouse_x = event.x()
        self.board.mouse_y = event.y()
        self.update()

    def reset(self):
        """ resets the chessboard to its initial state
        """
        self.last_press_x = 0
        self.last_press_y = 0
        self.board.last_move_destination = None
        self.board.last_move_source = None
