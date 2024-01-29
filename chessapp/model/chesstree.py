import csv
from chessapp.model.node import Node
from chessapp.model.sourcetype import SourceType
from chessapp.model.move import Move
from chess import Board
from chessapp.util.paths import assure_file
from chessapp.configuration import STR_DEFAULT_ENCODING
from chessapp.util.fen import get_reduced_fen_from_board


class ChessTree:
    """ ChessTree is a graph (not actually a tree but commonly referred to as a tree). It is the main data structure of the application.
    Each node represents a position and each move of a node represents an arc in the graph.

    This datastructure is saved to and loaded from two csv files: position_eval.csv and moves.csv. The position_eval.csv contains the
    evaluation of each position and the moves.csv contains the known moves of each position. Both files are located in the save_folder_path
    folder. The position_eval.csv contains the following columns:\n
    - fen: the fen of the position
    - eval: the evaluation of the position
    - eval_depth: the depth of the evaluation
    - is_mate: whether the position is a mate position or not\n
    The moves.csv contains the following columns:\n
    - fen: the fen of the position
    - move: the move in san notation
    - comment: the comment of the move (optional)
    - SourceType: the source of the move (@see chessapp.model.sourcetype.SourceType)
    - frequency: the frequency of the move (how often it was played in the database)
    - result fen: the fen of the resulting position after the move is played
    """

    def __init__(self, save_folder_path: str):
        """ Creates a new ChessTree. The save_folder_path is the path where the tree will be saved to/loaded from if the corresponding
        files exist.

        Args:
            save_folder_path (str): _description_
        """
        self.nodes = {}
        self.save_folder_path = save_folder_path
        self.position_eval_file_name = "position_eval.csv"
        self.moves_file_name = "moves.csv"

    def clear(self) -> None:
        """ "forgets" all nodes
        """
        self.nodes = {}

    def get(self, fen: str) -> Node:
        """ Returns the node with the given fen. If the node does not exist, it is created.

        Args:
            fen (str): the fen

        Returns:
            Node: node with the given fen
        """
        self.assure(fen)
        return self.nodes[fen]

    def assure(self, fen: str) -> None:
        """ Creates a node with the given fen if it does not exist.

        Args:
            fen (str): the fen
        """
        if not fen in self.nodes:
            self.nodes[fen] = Node(self, fen)

    def position_evaluation_file_path(self) -> str:
        """
        Returns:
            str: the path of the position_eval.csv file
        """
        return self.save_folder_path + "/" + self.position_eval_file_name

    def moves_file_path(self) -> str:
        """
        Returns:
            str: the path of the moves.csv file
        """
        return self.save_folder_path + "/" + self.moves_file_name

    def load_position_evaluation(self, encoding: str):
        """ Loads the position_eval.csv file and creates the corresponding nodes.

        Args:
            encoding (str): the encoding of the file
        """
        assure_file(self.position_evaluation_file_path())
        with open(self.position_evaluation_file_path(), "r", encoding=encoding) as f:
            # fen; eval; eval_depth; is_mate
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                self.nodes[row[0]] = Node(self, row[0], float(
                    row[1]), int(row[2]), row[3] == "True")

    def load_moves(self, encoding: str):
        """ Loads the moves.csv file and creates the corresponding moves (and nodes if needed).

        Args:
            encoding (str): the encoding of the file
        """
        assure_file(self.moves_file_path())
        with open(self.moves_file_path(), "r", encoding=encoding) as f:
            # fen; move; comment; SourceType; frequency;result fen
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if len(row) >= 6:
                    result_fen = row[5]
                else:
                    # recover result_fen from san
                    board = Board(fen=row[0])
                    board.push_san(row[1])
                    result_fen = get_reduced_fen_from_board(board)
                move = Move(self, row[1], result_fen, row[2],
                            SourceType.from_str(row[3]), int(row[4]))
                self.get(row[0]).add(move)
                self.assure(result_fen)

    def load(self, encoding: str = STR_DEFAULT_ENCODING):
        """ loads the tree from the position_eval.csv and moves.csv files

        Args:
            encoding (str, optional): Defaults to STR_DEFAULT_ENCODING. the encoding of the files
        """
        self.load_position_evaluation(encoding)
        self.load_moves(encoding)

    def save(self):
        """ saves the tree to the position_eval.csv and moves.csv files
        """
        with open(self.moves_file_path(), "w", encoding=STR_DEFAULT_ENCODING) as file:
            for fen in self.nodes:
                for move in self.nodes[fen].moves:
                    file.write("\"" + fen + "\";\"" + move.san +
                               "\";\"" + move.comment + "\";\"" + move.source.sformat() + "\";\"" +
                               str(move.frequency) + "\";\"" + str(move.result) + "\"\n")
            file.flush()
            file.close()
        with open(self.position_evaluation_file_path(), "w", encoding=STR_DEFAULT_ENCODING) as file:
            for fen in self.nodes:
                node = self.nodes[fen]
                file.write("\"" + fen + "\";\"" + str(node.eval) +
                           "\";\"" + str(node.eval_depth) + "\";\"" + str(node.is_mate) + "\"\n")
            file.flush()
            file.close()
