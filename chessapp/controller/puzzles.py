from os.path import isdir, isfile, join
from os import listdir
from chessapp.view.module import ChessboardAndLogModule, create_method_action
from chessapp.controller.explorer import Explorer
from chessapp.model.chesstree import get_fen_from_board
from chess import Board
from chessapp.view.chessboardwidget import PieceMovement
import json
from chessapp.controller.updater import extract_lines
from chessapp.model.chesstree import reduce_fen, get_fen_from_board
from chessapp.util.paths import get_puzzles_folder
from random import choice
import traceback
import chessapp.model.move
import chess
from time import sleep
from chessapp.sound.chessboardsound import ChessboardSound


class PuzzleNode:
    """ a node in a puzzle is a double linked list node with a fen and a san. the san represents the expected 
    move on a board with the given fen.
    """

    def __init__(self, fen: str, san: str) -> None:
        """initializes a puzzle node. the previous and next nodes are None by default.

        Args:
            fen (str): fen of the board
            san (str): move expected to be played by the turn player
        """
        self.fen: str = fen
        self.san: str = san
        self.previous: PuzzleNode = None
        self.next: PuzzleNode = None


class Puzzle:
    """ A puzzle is a sequence of moves. The puzzle is represented by a double linked list of puzzle nodes. The last node
    has a None san. The puzzle is done when the current node has a None san. Use reset to reset the puzzle to its initial state. Use
    is_done to check if the puzzle is done. Use apply_move to apply a san-move to the puzzle (which is only accepted when it is the expected
    move of the current node). Use perform_next_move to perform the next move (without specificying the move).
    """

    def __init__(self, pgn: str, fen: str, moves: [], about_to_close) -> None:
        """ Initializes a puzzle. The pgn is the pgn of the game the puzzle is extracted from. The fen is the fen of the board at the start of the puzzle.
        moves is a list of moves in san format. about_to_close is a function that returns True if the application is about to close (this is used for
        the extraction of the lines from the pgn, @see extract_lines in updater.py)

        Args:
            pgn (str): pgn of the game the puzzle is extracted from
            fen (str): fen of the board at the start of the puzzle
            moves ([str]): expected moves in san format
            about_to_close (() -> bool): function that returns True if the application is about to close 
        """
        self.about_to_close = about_to_close
        self.pgn: str = pgn
        self.fen: str = reduce_fen(fen)
        self.puzzle_nodes = []
        self.board = Board()
        self.moves = moves.split(" ")
        self.current_node: PuzzleNode = None
        self.reset()

    def is_done(self) -> bool:
        """ checks if the puzzle is done

        Returns:
            bool: if the puzzle is done
        """
        return self.current_node.san == None

    def apply_move(self, san: str) -> bool:
        """ Checks if the given san is the expected move of the current node. If so, the move is applied to the board and
        the current node is set to the next node.

        Args:
            san (str): a san move

        Returns:
            bool: True if the move was applied, False otherwise
        """
        if self.current_node.san != san:
            return False
        self.board.push_san(san)
        self.current_node = self.current_node.next
        return True

    def perform_next_move(self) -> str:
        """ Performs the next move (without specifying the move). The move is applied to the board and the current node is set to the next node.

        Returns:
            str: san of the move performed
        """
        san: str = self.current_node.san
        self.board.push_san(self.current_node.san)
        self.current_node = self.current_node.next
        return san

    def reset(self):
        """ Resets the puzzle to its initial state. The board is set to the fen of the puzzle. The current node is set to the first node of the puzzle.
        Beware that the first node of the puzzle is not the first node of the double linked list of PuzzleNodes. Instead the first node of the double
        linked list represents the move that was played just before the board state of the puzzle was reached. This is done to display the last_move arrows
        on the ChessBoardWidget, @see display in ChessBoardWidget.

        Raises:
            Exception: if the pgn of the puzzle does not contain exactly one line
            Exception: if the fen of the puzzle is never reached from the moves in the pgn
        """
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
        first_move = self.board.pop()
        first_move_san = self.board.san(first_move)
        base_node = PuzzleNode(get_fen_from_board(self.board), first_move_san)
        self.board.push(first_move)
        self.current_node = base_node
        copy_board = Board(self.board.fen())
        for san in self.moves:
            next_node = PuzzleNode(get_fen_from_board(copy_board), san)
            copy_board.push_san(san)
            self.current_node.next = next_node
            next_node.previous = self.current_node
            self.current_node = next_node
        self.current_node.next = PuzzleNode(
            get_fen_from_board(copy_board), None)
        self.current_node.next.previous = self.current_node
        self.current_node = base_node.next


class Puzzles(ChessboardAndLogModule):
    """ The puzzles module allows the user to solve hand-picked puzzles. The puzzles are loaded from the puzzles folder. Add new puzzles by creating a json file
    in the puzzles folder. The json file must contain a list of puzzles and a pgn. Each puzzle must contain a fen and a list of moves. 
    The fen is the state of the board at the start of the puzzle. The moves are the moves that must be played to solve the puzzle (the player always has the
    first move and the oppenents move are automatically played by the application). The pgn is the pgn of the game the puzzle is extracted from.
    """

    def __init__(self, app, explorer: Explorer, tree):
        """ initializes the puzzles module with the given explorer and tree. it has the following actions: explore, retry, and start

        Args:
            app (chessapp.chessapp.Chessapp): the main application
            explorer (Explorer): the explorer module
            tree (chessapp.model.chesstree.Chesstree): the tree containing the moves and positions
        """
        super().__init__(app, "Puzzles", [
            create_method_action(app, "Explore", self.explore),
            create_method_action(app, "Retry", self.retry),
            create_method_action(app, "Start", self.start)
        ])
        self.is_started = False
        self.explorer = explorer
        self.puzzles = []
        self.current_puzzle: Puzzle = None
        self.tree = tree

    def on_register(self):
        """ @see ChessboardAndLogModule.on_register
        this method calls load_puzzles in a threadpool
        """
        super().on_register()
        self.dispatch_threadpool(self.load_puzzles)

    def load_puzzle(self, file_path: str):
        """loads a puzzle from the given file path

        Args:
            file_path (str): path to the puzzle file
        """
        try:
            with open(file_path, mode="r") as f:
                data = json.loads(f.read())
        except:
            print("error while loading puzzle " + file_path)
            print(traceback.format_exc())
            return
        for puzzle in data["puzzles"]:
            try:
                loaded_puzzle = Puzzle(
                    data["pgn"], puzzle["fen"], puzzle["moves"], self.about_to_close)
            except:
                print("error while loading puzzle " +
                      file_path + " with fen " + puzzle["fen"])
                print(traceback.format_exc())
                continue
            self.puzzles.append(loaded_puzzle)

    def load_puzzles(self, folder=get_puzzles_folder()):
        """loads all puzzles from the given folder (and its subfolders). the default folder is the puzzles folder, @see chessapp.util.paths.get_puzzles_folder()

        Args:
            folder (Path|str, optional): Defaults to get_puzzles_folder(). path to the folder containing the puzzles
        """
        for name in listdir(folder):
            path: str = join(folder, name)
            if isdir(path):
                self.load_puzzles(path)
            elif isfile(path) and path.endswith(".json"):
                self.load_puzzle(path)

    def finish_puzzle(self):
        """called when a puzzle is done. prepares the puzzles module for a new puzzle
        """
        self.log_message("puzzle done")
        self.is_started = False
        ChessboardSound.GAME_END.play()

    def apply_next_move(self, is_opponent_move: bool = False):
        """ if the puzzle is done, finish_puzzle is called.
        if the puzzle is not done, the next move is performed and the display is updated. if the puzzle is done after the move is performed,
        finish_puzzle is called.

        Args:
            is_opponent_move (bool, optional): Defaults to False. indicates if the move is performed by the opponent (True) or the player (False)
        """
        if not self.is_started:
            return
        if not self.current_puzzle.is_done():
            sleep(0.5)
            san: str = self.current_puzzle.perform_next_move()
            self.log_message("opponent played: " + san)
            self.display(play_sound=True,
                         last_move_is_opponent_move=is_opponent_move)
            if self.current_puzzle.is_done():
                self.dispatch_threadpool(self.finish_puzzle)
        else:
            self.dispatch_threadpool(self.finish_puzzle)

    def on_piece_movement(self, piece_movement: PieceMovement):
        """ @see ChessboardAndLogModule.on_piece_movement()
        if the puzzle is not done, the piece movement (understood as a uci move) is applied to the puzzle (@see Puzzle.apply_move) and the display is updated.
        if the puzzle is done after the move is applied, finish_puzzle is called. If the wrong move is applied, the log is updated and a sound is played.

        Args:
            piece_movement (PieceMovement): _description_
        """
        if not self.is_started:
            return
        san: str = self.current_puzzle.board.san(
            chess.Move.from_uci(piece_movement.uci_format()))
        if self.current_puzzle.apply_move(san):
            self.log_message("correct move: " + san)
            self.display(play_sound=True, last_move_is_opponent_move=False)
            self.dispatch_threadpool(self.apply_next_move)
        else:
            self.log_message("wrong move: " + san)
            ChessboardSound.RESULT_BAD.play()

    def retry(self):
        """retries the current puzzle if there is one
        """
        if self.current_puzzle:
            self.start(keep_puzzle=True)
        else:
            self.log_message("no puzzle to retry")

    def start(self, keep_puzzle: bool = False):
        """ starts a new puzzle. if keep_puzzle is True and the current puzzle is not None, the current puzzle is kept.
        otherwise a new puzzle is chosen from the puzzles list. the board is set to the fen of the puzzle. the display is updated. a sound is played.
        After calling this method the user can interact with the puzzle (and solve it).

        Args:
            keep_puzzle (bool, optional): Defaults to False. if True, the current puzzle is kept (if possible). if False, a new puzzle is chosen from the puzzles list.
        """
        if self.is_started:
            return
        self.focus()
        if not self.current_puzzle or not keep_puzzle:
            self.current_puzzle = choice(self.puzzles)
        self.current_puzzle.reset()
        if 'w' in self.current_puzzle.current_node.fen:
            self.chess_board_widget.view_white()
        else:
            self.chess_board_widget.view_black()
        self.display(play_sound=False, last_move_is_opponent_move=True)
        ChessboardSound.GAME_START.play()
        self.is_started = True

    def display(self, play_sound: bool = True, last_move_is_opponent_move: bool = False):
        """ displays the current puzzle's board state.

        Args:
            play_sound (bool, optional): Defaults to True. if True, a sound is played.
            last_move_is_opponent_move (bool, optional): Defaults to False. if True, the last move is considered to be played by the opponent.

        Raises:
            Exception: if the current puzzle is None
            Exception: if the current node of the current puzzle is None
        """
        previous_node = None
        if not self.current_puzzle:
            raise Exception("current_puzzle is None")
        if not self.current_puzzle.current_node:
            raise Exception("current node is None")
        current_fen = get_fen_from_board(self.current_puzzle.board)
        last_move = chessapp.model.move.Move(
            self.tree, self.current_puzzle.current_node.previous.san, current_fen)
        if self.current_puzzle.current_node.previous:
            previous_node = self.tree.get(
                self.current_puzzle.current_node.previous.fen)
        self.chess_board_widget.display(
            self.current_puzzle.board,
            node=self.tree.get(current_fen),
            previous_node=previous_node,
            last_move=last_move,
            show_last_move_icon=False,
            last_move_is_opponent_move=last_move_is_opponent_move,
            play_sound=play_sound
        )

    def explore(self):
        """ opens the explorer module and sets the board of the explorer to the board of the current puzzle
        """
        if self.current_puzzle:
            self.explorer.set_board(self.current_puzzle.board)
            self.explorer.focus()
