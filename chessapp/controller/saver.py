from chessapp.model.chesstree import ChessTree
from chessapp.view.module import LogModule, create_method_action


class Saver(LogModule):
    """the saver module is responsible for saving the tree to disk
    """

    def __init__(self, app, tree: ChessTree):
        """ initialises the saver with the given app and tree. the saver has one action: save.

        Args:
            app (Chessapp): the main application
            tree (ChessTree): the tree to save
        """
        super().__init__(app, "Saver", [
            create_method_action(app, "Save", self.save)])
        self.tree: ChessTree = tree
        self.app = app

    def save(self):
        """saves the tree to disk
        """
        self.log_message("saving...")
        self.tree.save()
        self.log_message("saving done")
