import csv
from chessapp.model.node import Node
from chessapp.model.sourcetype import SourceType
from chessapp.model.move import Move
from chess import Board
from chessapp.util.paths import assure_file
from chessapp.configuration import STR_DEFAULT_ENCODING
from chessapp.util.fen import get_reduced_fen_from_board


class ChessTree:
    def __init__(self, save_folder_path: str):
        self.nodes = {}
        self.save_folder_path = save_folder_path
        self.position_eval_file_name = "position_eval.csv"
        self.moves_file_name = "moves.csv"

    def clear(self):
        self.nodes = {}

    def get(self, fen: str) -> Node:
        self.assure(fen)
        return self.nodes[fen]

    def assure(self, fen: str):
        if not fen in self.nodes:
            self.nodes[fen] = Node(self, fen)

    def position_evaluation_file_path(self) -> str:
        return self.save_folder_path + "/" + self.position_eval_file_name

    def moves_file_path(self) -> str:
        return self.save_folder_path + "/" + self.moves_file_name

    def load_position_evaluation(self, encoding: str):
        assure_file(self.position_evaluation_file_path())
        with open(self.position_evaluation_file_path(), "r", encoding=encoding) as f:
            # fen; eval; eval_depth; is_mate
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                self.nodes[row[0]] = Node(self, row[0], float(
                    row[1]), int(row[2]), row[3] == "True")

    def load_moves(self, encoding: str):
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
        self.load_position_evaluation(encoding)
        self.load_moves(encoding)

    def save(self):
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

    def find_node(self, max_depth: int = 0, min_source_type=SourceType.ENGINE_SYNTHETIC, allow_terminal_nodes: bool = False, prefer_higher_source_type: bool = False):
        node = None
        node_source = SourceType.ENGINE_SYNTHETIC.value
        for key in self.nodes:
            current_node_source = self.nodes[key].source().value
            if self.nodes[key].eval_depth <= max_depth and current_node_source >= min_source_type.value and (not self.nodes[key].is_mate or allow_terminal_nodes):
                if not node or (prefer_higher_source_type and node_source < current_node_source):
                    node = self.nodes[key]
                    node_source = current_node_source
                if node and not prefer_higher_source_type:
                    break
        return node


