from chessapp.model.chesstree import ChessTree, get_fen_from_board
from chessapp.model.sourcetype import SourceType
from pathlib import Path
from chess import Board, IllegalMoveError
from chess.pgn import read_game
import io
from chessapp.model.move import Move
from chessapp.view.module import LogModule, create_method_action
from os.path import join, isfile, isdir
from chessapp.util.paths import get_openings_folder
from chessapp.model.node import Node
from os import listdir


class Updater(LogModule):
    """ Update the ChessTree from the sources folder.
    """

    def __init__(self, app, tree: ChessTree):
        """ initialize the Updater with the action "Update Openings" which updates the ChessTree from the sources folder.

        Args:
            app (ChessApp): the main application
            tree (ChessTree): the ChessTree to update
        """
        super().__init__(app, "Update", [create_method_action(
            app, "Update Openings", self.update_openings)])
        self.tree = tree
        self.app = app

    def update_openings(self):
        """ update the ChessTree from the sources folder.
        """
        self.log_message("updating...")
        for key in SourceType._member_map_:
            path = join(get_openings_folder(), "sources", key)
            Path(path).mkdir(parents=True, exist_ok=True)
            import_pgn_from_folder_path(self.app, self.tree, SourceType.from_str(
                key), path, self.about_to_close, False)
        self.log_message("updating done")


def import_from_file(app, tree: ChessTree, file_path: str | Path, source: SourceType, about_to_close, count_frequency: bool = False):
    """import lines from a pgn file into the ChessTree


    Args:
        app (ChessApp): the main apllication
        tree (ChessTree): the ChessTree to import into
        file_path (str | Path): the path to the pgn file
        source (SourceType): the source of the moves
        about_to_close (callable): callable that returns True if the module closes
        count_frequency (bool, optional): Defaults to False. if True, the frequency of the moves will be counted
    """
    app.show_status_message(
        "importing pgn from file \"" + file_path + "\"")
    print("importing pgn from file \"" + file_path + "\"")
    pgn = ""
    with open(file_path, "r", encoding="utf-8") as file:
        pgn = file.read()
    import_pgn(app, tree, pgn, source, about_to_close, count_frequency)


def import_pgn_from_folder_path(app, tree, source: SourceType, folder_path: str, about_to_close, count_frequency: bool = False):
    """import all .pgn files from a folder into the ChessTree

    Args:
        app (ChessApp): the main application
        tree (ChessTree): the ChessTree to import into
        source (SourceType): the source of the moves
        folder_path (str): the path to the folder
        about_to_close (_type_): callable that returns True if the module closes
        count_frequency (bool, optional): Defaults to False. if True, the frequency of the moves will be counted
    """
    for name in listdir(folder_path):
        path: str = join(folder_path, name)
        if isdir(path):
            import_pgn_from_folder_path(
                app, tree, source, path, about_to_close, count_frequency)
        elif isfile(path) and path.endswith(".pgn"):
            import_from_file(app, tree, path, source,
                             about_to_close, count_frequency)


def import_pgn(app, tree: ChessTree, pgn: str, source: SourceType, about_to_close, count_frequency: bool = False):
    """ import a pgn string into the ChessTree

    Args:
        app (ChessApp): the main application
        tree (ChessTree): the ChessTree to import into
        pgn (str): the pgn string
        source (SourceType): the source of the moves
        about_to_close (_type_): callable that returns True if the module closes
        count_frequency (bool, optional): Defaults to False. if True, the frequency of the moves will be counted
    """
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
            if count_frequency:
                equivalent_move.frequency += 1
        fen = get_fen_from_board(board)
        tree.assure(fen)


def extract_lines_from_node(base_line: list[str], board: Board, node: Node, about_to_close):
    """ extract all lines from a node

    Args:
        base_line (list[str]): the base line is a list of moves that was played before to reach this specific board state
        board (Board): the board having the specific board state and all the desired variations
        node (Node): the node that represents the board state
        about_to_close (callable): callable that returns True if the module closes

    Returns:
        list[list[str]]: list of lines (variations) of chess moves extracted from the board
    """
    move_line: list[str] = base_line.copy()
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
    """ extract all lines from a pgn string

    Args:
        pgn (str): the pgn string
        about_to_close (callable): callable that returns True if the module closes

    Returns:
        list[list[str]]: list of lines (variations) of chess moves extracted from the pgn string
    """
    input_str = io.StringIO(pgn)
    game = read_game(input_str)
    lines = []
    while game != None and not about_to_close():
        for node in game.variations:
            for line in extract_lines_from_node([], Board(), node, about_to_close):
                lines.append(line)
        game = read_game(input_str)
    return lines
