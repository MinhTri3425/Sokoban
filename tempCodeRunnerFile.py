    def undo_move(self):
        if self.game.stack_matrix:
            self.game.matrix = self.game.stack_matrix.pop()
            if self.move_count > 0:
                self.move_count -= 1
            self.game_completed = self.game.is_completed(self.dock_list)