import random
from PyQt5.QtCore import QRunnable
from chess import Board
from chessapp.model.chesstree import get_fen_from_board, ChessTree
from chessapp.view.piecemovement import PieceMovement
import time
import chess
from chessapp.model.move import Move
from chessapp.model.sourcetype import SourceType
from chessapp.view.module import Module, create_method_action
from chessapp.controller.openingtree import OpeningTree
from chessapp.controller.explorer import Explorer
from chessapp.model.node import Node
from chessapp.sound.chessboardsound import ChessboardSound

s_starting_position = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
s_quiz_start_at_fen = s_starting_position


class Quiz(Module):

    def __init__(self, app, tree: ChessTree, opening_tree: OpeningTree, explorer: Explorer):
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
        if not self.quiz_started:
            return
        if not self.player_turn:
            raise Exception(
                "this method can only be called during the players turn")
        fen = get_fen_from_board(self.board)
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
            node.add(Move(self.tree, san, get_fen_from_board(
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
        node = self.tree.get(get_fen_from_board(self.board))
        self.chess_board_widget.display(
            self.board, last_move=move, previous_node=previous_node, node=node, play_sound=True)
        self.player_turn = False
        self.apply_opponent_move()

    def apply_opponent_move(self):
        if not self.quiz_started:
            return
        if self.player_turn:
            raise Exception(
                "this method can only be called during the opponents turn")
        time.sleep(0.7)
        fen = get_fen_from_board(self.board)
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
        node = self.tree.get(get_fen_from_board(self.board))
        self.chess_board_widget.display(
            self.board, last_move=move, previous_node=previous_node, node=node, show_last_move_icon=False, last_move_is_opponent_move=True, play_sound=True)
        if not node.has_acceptable_move():
            self.finish_quiz(
                node, "opponent moved, no more acceptable moves for player known")

    def finish_quiz(self: str, node: Node, reason):
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
        if not self.about_to_close():
            self.app.threadpool.start(QuizMovementAction(self, piece_movement))

    def reset(self):
        self.quiz_started = False
        self.board = Board()
        self.chess_board_widget.display(self.board)

    def explore(self):
        self.explorer.focus()
        self.explorer.set_board(self.board)

    def start(self):
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
    def __init__(self, quiz: Quiz, piece_movement: PieceMovement):
        super().__init__()
        self.quiz = quiz
        self.piece_movement = piece_movement

    def run(self):
        self.quiz.apply_movement(self.piece_movement)


def moves_to_pgn(moves, white_first_move: bool) -> str:
    pgn = ""
    for i in range(0, len(moves)):
        if (i % 2 == 0 and white_first_move) or (i % 2 != 0 and not white_first_move):
            pgn += " " + str(i // 2 + 1) + "."
        if i == 0 and not white_first_move:
            pgn += ".."
        pgn += " " + str(moves[i])
    return pgn
