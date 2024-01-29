# sourcetype

::: chessapp.model.sourcetype.SourceType
    options:
        show_root_heading: true
        show_source: true

# Source
```python
from enum import Enum


class SourceType(Enum):
    """ represents the type of sources a move or node can have. This is meant as an annotation to hint at the quality of the move or node.
    For example a move that was played in a GM game is more likely to be a good move than a move that was played in an amateur game. This
    can be used to prioritize moves in the quiz or to filter moves in the explorer. Also analsying moves of a high quality in high depth
    might be more useful than analysing low quality moves in low depth (for example blundering a queen usually is not worth while except
    very rare cases that are sometimes seen by GMs). The source types are ordered by quality ascending.
    """

    UNKNOWN = -3  # default value
    ENGINE_SYNTHETIC = -2  # created by an engine
    QUIZ_EXPLORATION = -1  # explored move during quiz
    MANUAL_EXPLORATION = 0  # explored move in explorer
    MANUAL = 1  # manually curated moves
    AMATEUR_GAME = 2  # online or otb
    INTERMEDIATE_GAME = 3  # online or otb
    PROFESSIONAL_GAME = 4  # otb
    MASTER_GAME = 5  # online or otb
    GM_GAME = 6  # otb
    THEORY_VIDEO = 7  # videos about opening theory
    COURSE = 8  # opening course
    BOOK = 9  # opening book

    @staticmethod
    def default_value():
        """ returns the default value for a source type

        Returns:
            SourceType: the default value
        """
        return SourceType.UNKNOWN

    def sformat(self) -> str:
        """ saveable format of the source type

        Returns:
            _str_: the saveable format
        """
        return str(self)[len("SourceType."):]

    @staticmethod
    def from_str(s: str):
        """ creates a source type from a string in saveable format (@see sformat)

        Args:
            s (str): the string

        Raises:
            Exception: if the string is not a valid source type

        Returns:
            SourceType: the source type
        """
        match s:
            case "ENGINE_SYNTHETIC":
                return SourceType.ENGINE_SYNTHETIC
            case "MANUAL":
                return SourceType.MANUAL
            case "AMATEUR_GAME":
                return SourceType.AMATEUR_GAME
            case "INTERMEDIATE_GAME":
                return SourceType.INTERMEDIATE_GAME
            case "PROFESSIONAL_GAME":
                return SourceType.PROFESSIONAL_GAME
            case "GM_GAME":
                return SourceType.GM_GAME
            case "THEORY_VIDEO":
                return SourceType.THEORY_VIDEO
            case "COURSE":
                return SourceType.COURSE
            case "BOOK":
                return SourceType.BOOK
            case "MASTER_GAME":
                return SourceType.MASTER_GAME
            case "QUIZ_EXPLORATION":
                return SourceType.QUIZ_EXPLORATION
            case "MANUAL_EXPLORATION":
                return SourceType.MANUAL_EXPLORATION
            case "UNKNOWN":
                return SourceType.UNKNOWN
            case _:
                raise Exception("source \"" + s + "\" not found")
```
