from enum import Enum
from PyQt5.QtMultimedia import QSound
from chessapp.util.paths import get_audio_folder
from os.path import join


class SoundAttributes:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.sound = None

# https://stackoverflow.com/questions/35567724/how-to-define-custom-properties-in-enumeration-in-python-javascript-like
# https://stackoverflow.com/questions/9861592/play-sound-file-in-pyqt


class ChessboardSound(Enum):

    CAPTURE_PIECE = SoundAttributes("capture.wav")
    MOVE_CHECK = SoundAttributes("move-check.wav")
    MOVE_OPPONENT = SoundAttributes("move-opponent.wav")
    MOVE_SELF = SoundAttributes("move-self.wav")
    MOVE_ILLEGAL = SoundAttributes("illegal.wav")
    GAME_START = SoundAttributes("game-start.wav")
    GAME_END = SoundAttributes("game-end.wav")
    RESULT_BAD = SoundAttributes("result-bad-2-15.wav")
    MOVE_CASTLE = SoundAttributes("castle.wav")

    def register(self):
        self.value.sound = QSound(
            join(get_audio_folder(), "chessboard", self.value.file_name))

    def play(self):
        if self.value.sound:
            self.value.sound.play()


def register_all_sounds():
    for sound in ChessboardSound:
        sound.register()
