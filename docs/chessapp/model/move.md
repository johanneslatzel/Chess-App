# move

# Source
```python
from .sourcetype import SourceType


class Move:
    def __init__(self, tree, san: str, result: str, comment: str = "", source=SourceType.default_vale(), frequency: int = 0):
        self.tree = tree
        self.san: str = san
        self.result: str = result
        self.comment: str = comment
        self.source: SourceType = source
        self.frequency: int = frequency

    def is_equivalent_to(self, other) -> bool:
        return other != None and self.san == other.san and self.result == other.result

    def __eq__(self, other) -> str:
        return self.is_equivalent_to(other) and self.comment == other.comment

    def get_info(self, node):
        info: str = self.san + " with eval " + str(self.eval()) + " at depth " + str(self.eval_depth(
        )) + " (cp loss = " + str(node.get_cp_loss(self)) + ") from source " + self.source.sformat()
        return info

    def eval(self) -> float:
        return self.tree.get(self.result).eval

    def eval_depth(self) -> int:
        return self.tree.get(self.result).eval_depth

    def __str__(self) -> str:
        return "san = " + self.san + ", result = " + self.result + ", source = " + self.source.sformat() + ", frequency = " + str(self.frequency) + ", " + self.comment
```
