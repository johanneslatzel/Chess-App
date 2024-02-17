from chessapp.model.chesstree import ChessTree
from chessapp.view.chessboardwidget import ChessBoardWidget, PieceMovement
from chess import Board
import chess
import chessapp.model.move
from chessapp.controller.engine import LocalStockfishEngine, MoveDescriptor, LichessCloudEngine
import traceback
from chessapp.model.node import Node
import chess
from chessapp.model.sourcetype import SourceType
from chessapp.util.fen import get_reduced_fen_from_board
from chessapp.view.mainwidget import SidebarElement

s_eval_time_seconds = 60
s_eval_depth = 20
s_best_moves_eval_depth = 30
s_best_moves_multipv = 3


class Explorer():
    """ Explore the ChessTree by playing moves on the board. The quality of the moves will be analysed by the engine and icons
    indicating the quality will be shown on the board. An evalbar is shown to further indicate the position evaluation. This
    module has several actions to both analyse a positon and show moves for a position that already have been found and analysed.
    """

    def __init__(self):
        self.chessboard_widget = ChessBoardWidget()
        self.sidebar_element = SidebarElement(
            self.chessboard_widget, "compass.png")
        self.board = Board()
        self.engine = LichessCloudEngine()
        self.previous_node = None
        self.last_move = None

    def flip_board(self):
        """ Flips the board
        """
        self.chessboard_widget.flip_board()

    def find_best_moves(self):
        """ Finds the best moves for the current position and adds them to the tree.
        """
        base_fen = get_reduced_fen_from_board(self.board)
        base_board = Board(base_fen)
        try:
            best_moves = self.engine.find_best_moves(
                base_board, s_eval_time_seconds, s_best_moves_eval_depth, multipv=s_best_moves_multipv)
        except Exception as e:
            print("error while analysing position in explorer")
            print(e)
            return
        for move_descriptor in best_moves:
            self.consume_move_descriptor(move_descriptor)
        self.display()

    def on_back(self):
        """ tries to return from the current board state to the previous board state. @see ChessboardAndLogModule.on_back
        """
        try:
            self.board.pop()
            self.reset_last_move()
            self.display(False)
        except IndexError:
            pass

    def set_board(self, board: Board):
        """ called by other modules to set the board of this module.

        Args:
            board (Board): the board to set
        """
        if not board:
            return
        self.reset_board()
        self.board = board.copy()
        self.display()

    def display(self, perform_analysis: bool = True, play_sound: bool = False):
        """ Displays the current board state. Choose whether to play a sound or not: A sound could represent a move
        or the start of a game. Sometimes this behaviour is not desired (e.g. when setting the board and displaying
        it without any prior user interaction).

        Args:
            perform_analysis (bool, optional): Defaults to True. Whether to perform an analysis of the current position.
            play_sound (bool, optional): Defaults to False. Whether to play a sound when displaying the board. 
        """
        self.chessboard_widget.display(
            self.board, None, self.previous_node, self.last_move, play_sound=play_sound)

    def on_piece_movement(self, piece_movement: PieceMovement):
        """ reacts to a user interaction with the board and tries to perform the given move. @see ChessboardAndLogModule.on_piece_movement

        Args:
            piece_movement (PieceMovement): the move to perform
        """
        if self.about_to_close():
            return
        self.last_move = None
        self.previous_node = None
        try:
            fen = get_reduced_fen_from_board(self.board)
            node = self.tree.get(fen)
            san = self.board.san(chess.Move.from_uci(
                piece_movement.uci_format()))
            board_copy = Board(fen)
            board_copy.push_san(san)
            result = get_reduced_fen_from_board(board_copy)
            move = chessapp.model.move.Move(
                self.tree, san, result, source=SourceType.MANUAL_EXPLORATION)
            if not node.knows_move(move):
                node.add(move)
            self.board.push_san(san)
            self.previous_node = node
            self.last_move = move
            self.display(play_sound=True)
        except Exception as e:
            print("error while exploring")
            print(traceback.format_exc())

    def reset_last_move(self):
        """ Forgets the last move and previous node and practially makes this module behave as if there was no prior board state.
        """
        self.last_move = None
        self.previous_node = None

    def reset_board(self):
        """ Resets the board to the initial state.
        """
        self.board = Board()
        self.reset_last_move()
        self.chessboard_widget.reset()
        self.display()

    def on_close(self):
        """ closes the engine. @see ChessboardAndLogModule.on_close
        """
        self.engine.close()
