# node

# Source
```python
from .move import Move
from .sourcetype import SourceType
from random import Random
from chessapp.configuration import QUIZ_ACCEPT_EVAL_DIFF, QUIZ_ACCEPT_EVAL_DIFF_RELAXED, QUIZ_ACCEPT_RELAXED_SOURCES


class Backlink:
    def __init__(self, node, move: Move):
        self.node: Node = node
        self.move: Move = move


class Node:
    def __init__(self, tree, fen: str, eval: float = 0, eval_depth: int = -1, is_mate: bool = False):
        self.tree = tree
        self.state: str = fen
        self.moves = []
        self.backlinks = []
        self.eval: float = eval
        self.eval_depth: float = eval_depth
        self.is_mate: bool = is_mate

    def __str__(self):
        return "fen = " + self.state + ", eval = " + str(self.eval) + ", depth = " + str(self.eval_depth) + ", source = " + str(self.source())

    def update(self, eval: float, eval_depth: int, is_mate: bool):
        if eval_depth > self.eval_depth:
            self.eval_depth = eval_depth
            self.eval = eval
            self.is_mate = is_mate

    def add(self, move: Move):
        for m in self.moves:
            if m.is_equivalent_to(move):
                if m.source.value < move.source.value:
                    m.source = move.source
                if move.comment and not m.comment:
                    m.comment = move.comment
                return
        self.moves.append(move)
        self.tree.get(move.result).backlink(self, move)

    def backlink(self, node, move: Move):
        self.backlinks.append(Backlink(node, move))

    def knows_move(self, move: Move) -> bool:
        return self.get_equivalent_move(move) != None

    def get_equivalent_move(self, move: Move) -> Move | None:
        for m in self.moves:
            if m.is_equivalent_to(move):
                return m
        return None

    def has_move(self) -> bool:
        return len(self.moves) != 0

    def total_frequency(self) -> int:
        sum: int = 0
        for move in self.moves:
            sum += move.frequency
        return sum

    def has_frequency(self) -> bool:
        return self.total_frequency() > 0

    def random_move(self, random: Random, use_frequency: bool = False) -> Move:
        if not use_frequency:
            return self.moves[random.randint(0, len(self.moves) - 1)]
        chosen_move = None
        total = self.total_frequency()
        sum = 0
        target = random.randint(0, total - 1)
        for move in self.moves:
            if sum + move.frequency > target:
                chosen_move = move
                break
            sum += move.frequency
        if chosen_move == None:
            raise Exception(
                "cannot chose a move. check frequencies of the moves of node " + self.state)
        return chosen_move

    def is_white_turn(self) -> bool:
        return self.state.split(" ")[1] == "w"

    def get_cp_loss(self, move: Move) -> int:
        return round(abs(self.eval - move.eval()) * 100)

    def get_move_by_san(self, move_san: str) -> Move:
        for move in self.moves:
            if move.san == move_san:
                return move
        return None

    def is_acceptable_move(self, move: Move) -> bool:
        if move.eval_depth() < 0:
            return False
        eval_diff_accept = QUIZ_ACCEPT_EVAL_DIFF
        if move.source in QUIZ_ACCEPT_RELAXED_SOURCES:
            eval_diff_accept = QUIZ_ACCEPT_EVAL_DIFF_RELAXED
        # check turn player
        eval_best = self.eval
        if self.eval_depth < 0:
            best_move = self.get_best_move()
            if best_move != None:
                if best_move.eval_depth() > 0:
                    eval_best = best_move.eval()
            else:
                return True
        if self.is_white_turn():
            return eval_best - move.eval() <= eval_diff_accept
        else:
            return move.eval() - eval_best <= eval_diff_accept

    def has_acceptable_move(self) -> bool:
        for move in self.moves:
            if self.is_acceptable_move(move):
                return True
        return False

    def get_best_move(self, min_depth: int = 0) -> Move:
        if len(self.moves) == 0:
            return None
        best_move = None
        # first search for a node as a baseline that has at least a depth of min_depth
        for move in self.moves:
            if not best_move or move.eval_depth() > best_move.eval_depth():
                best_move = move
        if not best_move:
            return None
        is_white_turn = self.is_white_turn()
        # now find a move that not only satisfies with depth min_depth but also has a better eval value
        for move in self.moves:
            if move.eval_depth() >= min_depth:
                if is_white_turn:
                    if move.eval() > best_move.eval():
                        best_move = move
                else:
                    if move.eval() < best_move.eval():
                        best_move = move
        return best_move

    def source(self) -> SourceType:
        source = SourceType.ENGINE_SYNTHETIC
        for backlink in self.backlinks:
            if backlink.move.source.value > source.value:
                source = backlink.move.source
        return source
```
