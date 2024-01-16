from chessapp.model.chesstree import ChessTree
from chessapp.controller.engine import Engine
from chessapp.model.sourcetype import SourceType
from chess import Board, WHITE
from chessapp.view.module import Module, create_method_action


s_analyse_desired_depth = 20
s_analyse_desired_time_seconds = 60
s_analyse_max_positions = 1000
s_analyse_break_every_position_amount = 10
s_max_depth = 30
s_source_to_depth_map = {
    SourceType.BOOK: s_max_depth,
    SourceType.THEORY_VIDEO: 28,
    SourceType.QUIZ_EXPLORATION: 25,
    SourceType.MANUAL_EXPLORATION: 23,
    SourceType.MANUAL: 23,
    SourceType.ENGINE_SYNTHETIC: -1,
    SourceType.GM_GAME: 25
}


class Analyser(Module):
    def __init__(self, app, tree: ChessTree):
        super().__init__(app, "Analyser", [
            create_method_action(app, "Analyse", self.analyse),
            create_method_action(app, "Statistics", self.print_statistics)])
        self.tree: ChessTree = tree
        self.app = app
        self.engine = Engine()

    def print_statistics(self):
        self.log_message("gathering data for statistics")
        depth_map = {}
        source_depth_total = {}
        source_depth_amount = {}
        source_depth_below_preferal = {}
        source_depth_preferal = {}
        for source in SourceType:
            source_depth_total[source] = 0
            source_depth_amount[source] = 0
            source_depth_below_preferal[source] = 0
            source_depth_preferal[source] = s_analyse_desired_depth
            if source in s_source_to_depth_map:
                source_depth_preferal[source] = s_source_to_depth_map[source]
        self.log_message("number of nodes in tree: " +
                         str(len(self.tree.nodes)))
        for fen in self.tree.nodes:
            node = self.tree.nodes[fen]
            if node.is_mate:
                continue
            if not node.eval_depth in depth_map:
                depth_map[node.eval_depth] = 0
            depth_map[node.eval_depth] += 1
            source_depth_total[node.source()] += node.eval_depth
            source_depth_amount[node.source()] += 1
            if node.eval_depth < source_depth_preferal[node.source()]:
                source_depth_below_preferal[node.source()] += 1
        for source in SourceType:
            if source_depth_amount[source] == 0:
                self.log_message("no nodes of source " + source.sformat())
            else:
                self.log_message("source " + source.sformat() + " has " + str(source_depth_amount[source]) + " nodes with an average depth of " + str(
                    source_depth_total[source] / source_depth_amount[source]) + " and " + str(source_depth_below_preferal[source]) + " nodes below preferred depth of " + str(source_depth_preferal[source]))
        average_depth: float = 0
        for depth in depth_map:
            self.log_message(
                "there are " + str(depth_map[depth]) + " nodes with depth " + str(depth))
            average_depth += depth_map[depth] * depth / len(self.tree.nodes)
        self.log_message("the average depth is " + str(average_depth))

    def analyse(self):
        self.log_message("analysing...")
        self.log_message(
            " ".join(("analysing up to", str(s_analyse_max_positions), "positions")))
        max_positions = s_analyse_max_positions
        while max_positions > 0 and not self.about_to_close():
            analyse_positions = min(
                max_positions, s_analyse_break_every_position_amount)
            analyed_positions = self.analyse_at_depth(
                s_analyse_desired_time_seconds, analyse_positions)
            # if no positions have been analysed or the engine aborted/closed
            if analyed_positions == 0 or analyed_positions == None:
                break
            max_positions -= analyed_positions
            self.log_message(
                " ".join((str(max_positions), "remaining")))

        self.log_message("analysing done")

    def analyse_at_depth(self, time_seconds, max_positions):
        position_count = 0
        # pre filter tree to avoid concurrent modification issues (RuntimeError: dictionary changed size during iteration)
        viable_fens = []
        for fen in self.tree.nodes:
            if not (position_count < max_positions and not self.about_to_close()):
                break
            node = self.tree.nodes[fen]
            source = node.source()
            if not node.is_mate and node.source() != SourceType.ENGINE_SYNTHETIC and ((source in s_source_to_depth_map and node.eval_depth < s_source_to_depth_map[source]) or (node.eval_depth < s_analyse_desired_depth)):
                viable_fens.append(fen)
            if len(viable_fens) >= max_positions - 1:
                break
        while position_count < max_positions and not self.about_to_close():
            found_node: bool = False
            for source in SourceType:
                if not (position_count < max_positions and not self.about_to_close()):
                    break
                if source == SourceType.ENGINE_SYNTHETIC:
                    continue
                target_depth: int = s_analyse_desired_depth
                if source in s_source_to_depth_map:
                    target_depth = s_source_to_depth_map[source]
                for fen in viable_fens:
                    if not (position_count < max_positions and not self.about_to_close()):
                        break
                    node = self.tree.nodes[fen]
                    if node.source() == source and node.eval_depth < target_depth and not node.is_mate:
                        self.log_message(" ".join(("evaluating position", str(node.state), "(" + node.source(
                        ).sformat() + ") at depth", str(target_depth), "for up to", str(time_seconds), "seconds")))
                        board = Board(fen=node.state)
                        if board.turn == WHITE:
                            self.chess_board_widget.view_white()
                        else:
                            self.chess_board_widget.view_black()
                        self.chess_board_widget.display(board)
                        try:
                            score_eval, score_depth, is_mate = self.engine.score(
                                board, time_seconds, target_depth)
                        except Exception as e:
                            print("error while analysing position in analyse")
                            print(e)
                            return
                        if is_mate or score_depth > node.eval_depth:
                            self.log_message(" ".join(
                                ("updating depth from", str(node.eval_depth), "to", str(score_depth), "and eval from", str(node.eval), "to", str(score_eval))))
                            node.update(score_eval, score_depth, is_mate)
                        else:
                            self.log_message(" ".join(("new depth of", str(target_depth),
                                                       "does not exceed", str(node.eval_depth))))
                        found_node = True
                        position_count += 1
            if not found_node:
                self.log_message("no node found, aborting")
                break
        return position_count

    def on_close(self):
        self.engine.close()
