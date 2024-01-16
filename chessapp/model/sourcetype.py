from enum import Enum


class SourceType(Enum):
    UNKNOWN = -3 # default value
    ENGINE_SYNTHETIC = -2 # created by an engine
    QUIZ_EXPLORATION = -1 # explored move during quiz
    MANUAL_EXPLORATION = 0 # explored move in explorer
    MANUAL = 1 # manually curated moves
    AMATEUR_GAME = 2 # online or otb
    INTERMEDIATE_GAME = 3 # online or otb
    PROFESSIONAL_GAME = 4 # otb
    MASTER_GAME = 5 # online or otb
    GM_GAME = 6 # otb
    THEORY_VIDEO = 7 # videos about opening theory
    COURSE = 8 # opening course
    BOOK = 9 # opening book
    
    def default_vale():
        return SourceType.UNKNOWN

    def sformat(self) -> str:
        return str(self)[len("SourceType."):]

    @staticmethod
    def from_str(s: str):
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
