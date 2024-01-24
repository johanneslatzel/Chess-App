# gamedownloader

::: chessapp.controller.gamedownloader.GameDownloader
    options:
        show_root_heading: true
        show_source: true

# Source
```python

# This enables the user to login to various chess websites (like lichess and chess.com) and also connect
# to other open apis. Each GameSource has its own ChessGameDatabase associated with it for easy access to the
# games. By doing so a variety of games are available to the program and therefor the user such as their
# own (online) games but also master games and master game compilations. This module has an auto-update
# function to make sure the games of the various sources are as up to date as possible. Each source can
# be configured to only retrieve games from a certain time onwards or filter for certain players (e.g.
# create databases that feature a single players' games). To make sure the process is as automatic as
# possible authentication tokens of the user have to be saved locally. The user should always be able
# to logout (deleting the tokens) and to login afterwards.

from view.module import ChessboardAndLogModule


class GameDownloader(ChessboardAndLogModule):

    def __init__(self):
        super().__init__()```
