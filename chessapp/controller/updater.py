from chessapp.model.chesstree import ChessTree, get_fen_from_board
from chessapp.model.sourcetype import SourceType
from pathlib import Path
import os
from chess import Board, IllegalMoveError
from chess.pgn import read_game
import io
from chessapp.model.move import Move
from chessapp.view.module import Module, create_method_action
from os.path import join
from chessapp.util.paths import get_openings_folder


class Updater(Module):
    def __init__(self, app, tree: ChessTree):
        super().__init__(app, "Update", [create_method_action(
            app, "Update Openings", self.update_openings)])
        self.tree = tree
        self.app = app

    def update_openings(self):
        self.log_message("updating...")
        for key in SourceType._member_map_:
            path = join(get_openings_folder(), key)
            Path(path).mkdir(parents=True, exist_ok=True)
            import_pgn_from_folder_path(self.app, self.tree, SourceType.from_str(
                key), path, self.about_to_close, False)
        self.log_message("updating done")


def import_from_file(app, tree, file_path, source, about_to_close, count_frequency: bool = False):
    app.show_status_message(
        "importing pgn from file \"" + file_path + "\"")
    pgn = ""
    with open(file_path, "r", encoding="utf-8") as file:
        pgn = file.read()
    import_pgn(app, tree, pgn, source, about_to_close, count_frequency)


def import_pgn_from_folder_path(app, tree, source: SourceType, folder_path: str, about_to_close, count_frequency: bool = False):
    # https://stackoverflow.com/questions/19587118/iterating-through-directories-with-python
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = str(os.path.join(root, file))
            if file_path.endswith(".pgn"):
                import_from_file(app, tree, file_path,
                                 source, about_to_close, count_frequency)
        for dir in dirs:
            import_pgn_from_folder_path(app, tree, source, os.path.join(
                root, dir), about_to_close, count_frequency)


def import_pgn(app, tree: ChessTree, pgn: str, source: SourceType, about_to_close, count_frequency: bool = False):
    lines = extract_lines(pgn, about_to_close)
    for line in lines:
        app.show_status_message("found line: " + str(line))
        board = Board()
        for san in line:
            fen = get_fen_from_board(board)
            tree.assure(fen)
            try:
                board.push_san(san)
            except IllegalMoveError:
                print(
                    "cannot perform board.push_san(san) because an illegal move was performed")
                return
            move = Move(tree, san, get_fen_from_board(
                board), source=source)
            equivalent_move = tree.get(fen).get_equivalent_move(move)
            if equivalent_move == None:
                tree.get(fen).add(move)
                equivalent_move = move
            elif equivalent_move.source.value < source.value:
                equivalent_move.source = source
            equivalent_move.frequency = equivalent_move.frequency + 1
        fen = get_fen_from_board(board)
        tree.assure(fen)


def extract_lines_from_node(base_line, board, node, about_to_close):
    move_line = base_line.copy()
    move_line.append(board.san(node.move))
    if len(node.variations) == 0:
        return [move_line]
    board.push(node.move)
    lines = []
    for n in node.variations:
        if about_to_close():
            break
        for line in extract_lines_from_node(move_line, board, n, about_to_close):
            if about_to_close():
                break
            lines.append(line)
    board.pop()
    return lines


def extract_lines(pgn: str, about_to_close):
    input_str = io.StringIO(pgn)
    game = read_game(input_str)
    lines = []
    while game != None and not about_to_close():
        for node in game.variations:
            for line in extract_lines_from_node([], Board(), node, about_to_close):
                lines.append(line)
        game = read_game(input_str)
    return lines
