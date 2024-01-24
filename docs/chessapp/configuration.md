# configuration

# Source
```python
from pathlib import Path
from chessapp.model.sourcetype import SourceType

ROOT_DIR: Path = Path(__file__).parent.parent
STR_DEFAULT_ENCODING: str = "utf-8"
DEFAULT_STYLESHEET: str = "background-color: black; color: green;"
MAX_EVALBAR_VALUE_ABS: int = 10
SQUARE_ICON_SQUARE_PERCENTAGE: float = 1 / 3
QUIZ_ACCEPT_EVAL_DIFF: float = 0.25
QUIZ_ACCEPT_EVAL_DIFF_RELAXED: float = 0.35
QUIZ_ACCEPT_RELAXED_SOURCES = [SourceType.THEORY_VIDEO,
                               SourceType.BOOK, SourceType.GM_GAME]
PIECES_IMAGES_FOLDER_NAME: str = "default"
```
