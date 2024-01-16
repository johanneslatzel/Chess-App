from chessapp.view.module import Module, create_method_action
from chessapp.controller.explorer import Explorer
from chessapp.model.chesstree import get_fen_from_board
from chess import Board
from chessapp.view.piecemovement import PieceMovement
import os
import json
from chess.pgn import read_game
import io
from chessapp.controller.updater import extract_lines
from chessapp.model.chesstree import reduce_fen, get_fen_from_board
from chessapp.util.paths import get_puzzles_folder
from os.path import join

s_puzzle_file_extension = "json"


class TreeNode:
    def __init__(self) -> None:
        self.san: str = ""
        self.next = []
        pass

    def from_tree(move_tree):
        pass

    def from_array(move_array: []):
        previous_node = None
        base_node = None
        for move in move_array:
            current_node = TreeNode()
            current_node.san = move
            if not base_node:
                base_node = current_node
            if previous_node:
                previous_node.next.append(current_node)
            previous_node = current_node
        return base_node


class VariationTree:
    def __init__(self, moves, moves_type) -> None:
        match moves_type:
            case "array":
                self.base_node = TreeNode.from_array(moves)
            case "tree":
                self.base_node = TreeNode.from_tree(moves)
            case _:
                raise Exception("cannot parse move_type: " + moves_type)
        self.current_node = self.base_node

    def available_moves(self):
        self.current_node.san


class Puzzle:
    def __init__(self, pgn: str, fen: str, moves: [], about_to_close) -> None:
        self.about_to_close = about_to_close
        self.pgn: str = pgn
        self.fen: str = reduce_fen(fen)
        # print(moves)
        # self.move_lines = extract_lines(moves, self.about_to_close, fen=fen)
        self.board = Board()
        # self.reset()

    def reset(self):
        lines = extract_lines(self.pgn, self.about_to_close)
        if len(lines) != 1:
            raise Exception(
                "number of lines found in puzzle file is not 1: " + self.pgn)
        self.board = Board()
        for san in lines[0]:
            if get_fen_from_board(self.board) == self.fen:
                break
            self.board.push_san(san)
        if get_fen_from_board(self.board) != self.fen:
            raise Exception("fen " + self.fen +
                            " never reached from moves in pgn " + self.pgn)
        print("test")


class Puzzles(Module):

    def __init__(self, app, explorer: Explorer):
        super().__init__(app, "Puzzles", [
            create_method_action(app, "Explore", self.explore),
            create_method_action(app, "Reset", self.reset),
            create_method_action(app, "Start", self.start)
        ])
        self.is_started = False
        self.explorer = explorer
        self.board = Board()
        self.last_move = None
        self.current_position = ""
        self.current_pgn = ""
        self.puzzles = {}

    def on_register(self):
        self.dispatch_threadpool(self.load_puzzles)

    def load_puzzle(self, file_path):
        with open(file_path, mode="r") as f:
            data = json.loads(f.read())
        for puzzle in data["puzzles"]:
            self.puzzles[puzzle["fen"]] = Puzzle(
                data["pgn"], puzzle["fen"], puzzle["moves"], self.about_to_close)

    def load_puzzles(self, folder=get_puzzles_folder()):
        # https://stackoverflow.com/questions/19587118/iterating-through-directories-with-python
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = str(os.path.join(root, file))
                if file_path.endswith("." + s_puzzle_file_extension):
                    self.load_puzzle(file_path)
            for dir in dirs:
                self.load_puzzles(os.path.join(root, dir))

    def choose_puzzle(self):
        pass

    def on_piece_movement(self, piece_movement: PieceMovement):
        if not self.is_started:
            return

    def reset(self):
        if not self.is_started:
            return
        self.is_started = False
        self.board = Board()
        self.chess_board_widget.display(self.board)
        self.is_started = False

    def start(self):
        if self.is_started:
            return
        self.reset()
        self.choose_puzzle()
        self.is_started = True

    def explore(self):
        self.explorer.set_board(self.board)
        self.explorer.focus()
