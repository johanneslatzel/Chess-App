# chessboardsound

::: chessapp.sound.chessboardsound.ChessboardSound
    options:
        show_root_heading: true
        show_source: true

# Source
```python
from dataclasses import dataclass
from enum import Enum
from PyQt5.QtMultimedia import QSound
from chessapp.util.paths import get_audio_folder
from os.path import join


@dataclass
class SoundAttributes:
    """ this class is used to store the file name and the sound object associated with a sound.
    """
    file_name: str
    sound: QSound = None


class ChessboardSound(Enum):
    """ this class enables the use of typical sounds in a chess game associated with actions on a chessboard. Refer to 
    [Stackoverflow: How to define custom properties in enumeration in Python](https://stackoverflow.com/questions/35567724/how-to-define-custom-properties-in-enumeration-in-python-javascript-like) and 
    [Stackoverflow: Play Sound File in PyQt](https://stackoverflow.com/questions/9861592/play-sound-file-in-pyqt)
    for more information on the methods used in this implementation.
    """

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
        """ This method tries to load the sound file associated with the enumeration value.
        """
        self.value.sound = QSound(
            join(get_audio_folder(), "chessboard", self.value.file_name))

    def play(self):
        """ plays the sound (if it was loaded successfully)
        """
        if self.value.sound:
            self.value.sound.play()


def register_all_sounds():
    """ call this method at some point before using the sounds in the application. This should be called by the main
    application during startup. 
    """
    for sound in ChessboardSound:
        sound.register()
```
