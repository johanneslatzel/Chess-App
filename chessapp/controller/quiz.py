import random
from PyQt5.QtCore import QRunnable
from chess import Board
from chessapp.model.chesstree import ChessTree
from chessapp.view.chessboardwidget import PieceMovement
import time
import chess
from chessapp.model.move import Move
from chessapp.model.sourcetype import SourceType
from chessapp.view.module import ChessboardAndLogModule, create_method_action
from chessapp.controller.openingtree import OpeningTree
from chessapp.controller.explorer import Explorer
from chessapp.model.node import Node
from chessapp.sound.chessboardsound import ChessboardSound
from chessapp.util.pgn import moves_to_pgn
from chessapp.util.fen import get_reduced_fen_from_board

s_starting_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"


class Quiz(ChessboardAndLogModule):
    """ this module is an interactive quiz in which the player has to find acceptable moves (given by the position evaluations) for given positions.
    usually the opening tree of the opening tree module (@see chessapp.controller.OpeningTree) is used to find opponent moves played with a
    probability that is in proportion to the statistical occurence of that move given the specific players the opening tree is based on. if no move
    is known for the given position in the opening tree then a random move is chosen from the tree that is given during module initialization.
    the quiz ends when a no more moves are known for a certain positon.
    """

    def __init__(self, app, tree: ChessTree, opening_tree: OpeningTree, explorer: Explorer):
        """initializes the quiz module. the actions are start, reset and explore. explore opens the explorer module (@see chessapp.controller.Explorer)
        and sets the board to the current position. start starts the quiz. reset resets the board to the starting position.

        Args:
            app (ChessApp): the main application
            tree (ChessTree): the tree to use for the quiz
            opening_tree (OpeningTree): the opening tree to use for the quiz
            explorer (Explorer): the explorer module
        """
        super().__init__(app, "Quiz", [create_method_action(app, "Start", self.start), create_method_action(
            app, "Reset", self.reset), create_method_action(app, "Explore", self.explore)])
        self.tree: ChessTree = tree
        self.explorer = explorer
        self.player_turn: bool = False
        self.quiz_started: bool = False
        self.opponent_color: str = ""
        self.board: Board = None
        self.moves_played = []
        self.opening_tree = opening_tree
        random.seed()

    def apply_movement(self, piece_movement: PieceMovement):
        """ this method is called when the user makes a move on the chessboard. it checks if the move is acceptable and if so applies it to the board. 
        if the move is acceptable it will call apply_opponent_move to apply the opponents move. if the move is not acceptable it will log a message.
        also if the move is unknown it will be added to the opening tree (and can be explored later).

        Args:
            piece_movement (PieceMovement): the movement to apply

        Raises:
            Exception: if this method is called during an opponents move
        """
        if not self.quiz_started:
            return
        if not self.player_turn:
            raise Exception(
                "this method can only be called during the players turn")
        fen = get_reduced_fen_from_board(self.board)
        node = self.tree.get(fen)
        san = self.board.san(chess.Move.from_uci(piece_movement.uci_format()))
        move = node.get_move_by_san(san)
        if not move:
            self.log_message("unable to find move " + san +
                             ". adding it to the opening chess tree.")
            ChessboardSound.RESULT_BAD.play()
            copy_board = Board(fen=fen)
            copy_board.push_san(san)
            self.moves_played.append(san)
            node.add(Move(self.tree, san, get_reduced_fen_from_board(
                copy_board), source=SourceType.QUIZ_EXPLORATION))
            return
        cp_loss = node.get_cp_loss(move)
        if not node.is_acceptable_move(move):
            self.log_message(
                "this move is not acceptable. CP loss = " + str(cp_loss))
            ChessboardSound.RESULT_BAD.play()
            return
        else:
            self.log_message(
                "good move. CP loss = " + str(cp_loss))
        self.board.push_san(san)
        previous_node = node
        node = self.tree.get(get_reduced_fen_from_board(self.board))
        self.chess_board_widget.display(
            self.board, last_move=move, previous_node=previous_node, node=node, play_sound=True)
        self.player_turn = False
        self.apply_opponent_move()

    def apply_opponent_move(self):
        """ this method is called when the opponent makes a move. it will choose a move from the opening tree (if known) by proportion of known moves
        or a random move otherwise (known by the given tree). if there is no more move known then the quiz stops.

        Raises:
            Exception: if this method is called during the players turn
        """
        if not self.quiz_started:
            return
        if self.player_turn:
            raise Exception(
                "this method can only be called during the opponents turn")
        time.sleep(0.7)
        fen = get_reduced_fen_from_board(self.board)
        node = self.tree.get(fen)
        if not node.has_move():
            black_node = self.opening_tree.black_opening_tree.get(fen)
            white_node = self.opening_tree.white_opening_tree.get(fen)
            if black_node.has_move():
                node = black_node
            elif white_node.has_move():
                node = white_node
            else:
                self.finish_quiz(node, "no moves for opponent known")
                return
        op_tree = self.opening_tree.black_opening_tree
        if self.opponent_color == "black":
            op_tree = self.opening_tree.white_opening_tree
        op_node = op_tree.get(node.state)
        move = None
        if op_node.has_frequency():
            move = op_node.random_move(random, True)
        else:
            move = node.random_move(random)
        self.moves_played.append(move.san)
        self.board.push_san(move.san)
        self.player_turn = True
        previous_node = node
        node = self.tree.get(get_reduced_fen_from_board(self.board))
        self.chess_board_widget.display(
            self.board, last_move=move, previous_node=previous_node, node=node, show_last_move_icon=False, last_move_is_opponent_move=True, play_sound=True)
        if not node.has_acceptable_move():
            self.finish_quiz(
                node, "opponent moved, no more acceptable moves for player known")

    def finish_quiz(self, node: Node, reason: str):
        """ this method is called when the quiz is finished. it will log the reason of termination, the moves played and the moves left in the node (if any).

        Args:
            node (Node): the node that that was reached when the quiz was finished
            reason (str): the reason why the quiz was finished

        Raises:
            Exception: if the quiz has not been started yet
        """
        if not self.quiz_started:
            raise Exception("cannot finish quiz that has not been started yet")
        self.log_message("quiz finished with reason: " + reason)
        self.log_message("line played: " +
                         moves_to_pgn(self.moves_played, True))
        if node.has_move():
            moves = []
            for move in node.moves:
                moves.append(str(move.san) +
                             " (" + str(node.get_cp_loss(move)) + ")")
            self.log_message("moves left in node " +
                             node.state + ": " + ", ".join(moves))
        self.quiz_started = False
        ChessboardSound.GAME_END.play()

    def on_piece_movement(self, piece_movement: PieceMovement):
        """ this method is called when the user makes a move on the chessboard. it will dispatch apply_movement for this piece movement on the
        threadpool of the main application (because this method is called from the gui thread and apply_movement may take some time to complete).

        Args:
            piece_movement (PieceMovement): the movement to apply
        """
        if not self.about_to_close():
            self.app.threadpool.start(QuizMovementAction(self, piece_movement))

    def reset(self):
        """ this method resets the board to the starting position and resets the quiz state.
        """
        self.quiz_started = False
        self.board = Board()
        self.chess_board_widget.display(self.board)

    def explore(self):
        """ opens the explorer module and sets the board of the explorer to the board of the quiz.
        """
        self.explorer.focus()
        self.explorer.set_board(self.board)

    def start(self):
        """ this method starts the quiz. it will randomly choose a color for the player and displays the board from the perspective of the player.
        """
        if self.quiz_started:
            return
        self.focus()
        self.player_turn = random.randint(0, 1) % 2 == 0
        self.opponent_color = "white"
        self.chess_board_widget.view_black()
        if self.player_turn:
            self.opponent_color = "black"
            self.chess_board_widget.view_white()
        self.board = Board()
        self.chess_board_widget.display(self.board)
        self.moves_played = []
        self.quiz_started = True
        ChessboardSound.GAME_START.play()
        if not self.player_turn:
            self.apply_opponent_move()


class QuizMovementAction(QRunnable):
    """ this class is a runnable that is used to apply a piece movement to the quiz (@see on_piece_movement). it is used to run apply_movement
    on the threadpool of the main application.
    """

    def __init__(self, quiz: Quiz, piece_movement: PieceMovement):
        """initializes the runnable

        Args:
            quiz (Quiz): the quiz to apply the movement to
            piece_movement (PieceMovement): the movement to apply
        """
        super().__init__()
        self.quiz = quiz
        self.piece_movement = piece_movement

    def run(self):
        """ applies the movement to the quiz
        """
        self.quiz.apply_movement(self.piece_movement)
