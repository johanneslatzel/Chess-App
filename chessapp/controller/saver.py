from chessapp.model.chesstree import ChessTree
from chessapp.view.module import Module, create_method_action

class Saver(Module):

    def __init__(self, app, tree: ChessTree):
        super().__init__(app, "Saver", [create_method_action(app, "Save", self.save)])
        self.tree: ChessTree = tree
        self.app = app
    
    def save(self):
        self.log_message("saving...")
        self.tree.save()
        self.log_message("saving done")
