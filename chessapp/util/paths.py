from pathlib import Path
from os.path import join, exists
from chessapp.configuration import ROOT_DIR, PIECES_IMAGES_FOLDER_NAME


def get_audio_folder() -> Path:
    """path to the audio folder. audio files are used for sound effects.

    Returns:
        Path: path to the audio folder
    """
    return join(get_assets_folder(), "audio")


def get_assets_folder() -> Path:
    """path to the assets folder. assets are files that are not code, e.g. images, audio, etc.

    Returns:
        Path: path to the assets folder
    """
    return join(ROOT_DIR, "assets")


def get_images_folder() -> Path:
    """path to the folder that contains all images. images are used for the GUI.

    Returns:
        Path: path to the images folder
    """
    return join(get_assets_folder(), "img")


def get_chess_pieces_folder() -> Path:
    """path to the folder that contains all chess pieces using configuration.PIECES_IMAGES_FOLDER_NAME as subfolder in which the
    image files of the pieces are contained.

    Returns:
        Path: path to the folder that contains all chess pieces
    """
    return join(get_images_folder(), "chessboard", "pieces", PIECES_IMAGES_FOLDER_NAME)


def get_data_folder() -> Path:
    """path to the data folder. data files are used for storing data, e.g. openings, puzzles, etc.

    Returns:
        Path: path to the data folder
    """
    return join(ROOT_DIR, "data")


def get_openings_folder() -> Path:
    """path to the openings folder. openings are used for the opening tree. the subfolders also contain a lot of pgn files which are the basis
    for the opening tree.

    Returns:
        Path: path to the openings folder
    """
    return join(get_data_folder(), "openings")


def get_opening_tree_folder() -> Path:
    """the opening tree folder contains the opening tree of the opening tree module. @see chessapp.controller.openingtree

    Returns:
        Path: path to the opening tree folder
    """
    return join(get_data_folder(), "opening_tree")


def get_stockfish_exe() -> Path:
    """path to the stockfish executable file. stockfish is used for calculating the best move.

    Returns:
        Path: path to the stockfish executable file
    """
    return join(ROOT_DIR, "engine", "stockfish", "16", "stockfish-windows-x86-64-avx2.exe")


def get_puzzles_folder() -> Path:
    """path to the puzzles folder. puzzles are used for the puzzle module @see chessapp.controller.puzzles

    Returns:
        Path: path to the puzzles folder
    """
    return join(get_data_folder(), "puzzles")


def assure_folder(folder_path: str | Path):
    """ creates a folder if it does not exist

    Args:
        folder_path (str | Path): path to the folder
    """
    path: Path = Path(folder_path)
    if not exists(path):
        path.mkdir(parents=True, exist_ok=True)


def assure_file(file_path: str | Path):
    """ creates a file (and parent folders) if it does not exist

    Args:
        file_path (str | Path): path to the file
    """
    path: Path = Path(file_path)
    assure_folder(path.parent)
    if not exists(path):
        with open(path, 'w'):
            pass


def get_db_folder() -> Path:
    """path to the database folder. the database folder contains the tinydb database files.

    Returns:
        Path: path to the database folder
    """
    return join(get_data_folder(), "db")
