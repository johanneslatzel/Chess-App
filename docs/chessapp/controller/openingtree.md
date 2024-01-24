# openingtree

::: chessapp.controller.openingtree.OpeningTree
    options:
        show_root_heading: true
        show_source: true

# Source
```python
from chessapp.model.chesstree import ChessTree
from chessapp.view.module import LogModule, create_method_action
from chessapp.controller.updater import import_pgn_from_folder_path
from chessapp.model.sourcetype import SourceType
from chessapp.util.paths import get_opening_tree_folder
from os.path import join

s_source_data_folder_path: str = join(get_opening_tree_folder(), "source_data")
s_white_source_folder_path: str = s_source_data_folder_path + "/white"
s_black_source_folder_path: str = s_source_data_folder_path + "/black"
s_white_opening_tree_folder_path: str = join(
    get_opening_tree_folder(), "white")
s_black_opening_tree_folder_path: str = join(
    get_opening_tree_folder(), "black")


class OpeningTree(LogModule):
    """the opening tree module is responsible for importing and managing the opening tree that is used in the quiz module
    """

    def __init__(self, app):
        """initializes the opening tree module and imports the opening tree from the source data folder. the only action is import.

        Args:
            app (ChessApp): the main application
        """
        super().__init__(app, "OpeningTree", [
            create_method_action(app, "Import", self.import_opening_tree)])
        self.white_opening_tree: ChessTree = ChessTree(
            s_white_opening_tree_folder_path)
        self.black_opening_tree: ChessTree = ChessTree(
            s_black_opening_tree_folder_path)
        self.app = app
        self.dispatch_threadpool(self.load)

    def load(self):
        """loads the opening tree from disk (usually once called on startup of the application)
        """
        self.log_message("loading opening tree...", 60000)
        self.white_opening_tree.load()
        self.black_opening_tree.load()
        self.log_message("loading opening done")

    def import_opening_tree(self):
        """imports the opening tree from the source data folder (this may take a while and should only dispatched on a threadpool)
        """
        self.log_message("importing white opening tree...")
        self.white_opening_tree.clear()
        import_pgn_from_folder_path(self.app, self.white_opening_tree, SourceType.AMATEUR_GAME,
                                    s_white_source_folder_path, self.about_to_close, True)
        self.white_opening_tree.save()
        self.log_message("importing white opening tree done")
        self.log_message("importing black opening tree...")
        self.black_opening_tree.clear()
        import_pgn_from_folder_path(self.app, self.black_opening_tree, SourceType.AMATEUR_GAME,
                                    s_black_source_folder_path, self.about_to_close, True)
        self.black_opening_tree.save()
        self.log_message("importing black opening tree done")
```
