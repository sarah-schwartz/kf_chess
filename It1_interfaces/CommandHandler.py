from Board import Board
from Command import Command

class CommandHandler:
    def __init__(self, board: Board, pos_to_piece: dict):
        self.board = board
        self.pos_to_piece = pos_to_piece

    def handle_command(self, cmd: Command, now: int):
        src_cell = self.board.algebraic_to_cell(cmd.params[0])
        dst_cell = self.board.algebraic_to_cell(cmd.params[1])

        if src_cell not in self.pos_to_piece:
            print("Source cell empty. Command ignored.")
            return

        moving_piece = self.pos_to_piece[src_cell]

        # בדיקת תנועות חוקיות - כולל לוגיקת פיונים
        legal_moves = moving_piece._state._moves.get_moves(*src_cell, moving_piece._has_moved, self.pos_to_piece)
        if dst_cell not in legal_moves:
            print(f"Illegal move: {cmd.params[0]} to {cmd.params[1]}")
            return

        # בדיקה: אם בתא היעד יש כלי ששייך לאותו שחקן, אין לעבד את הפקודה
        if dst_cell in self.pos_to_piece:
            target_piece = self.pos_to_piece[dst_cell]
            if target_piece.get_id()[1] == moving_piece.get_id()[1]:
                print("Move blocked: Destination occupied by friendly piece.")
                return

        # בדיקה אם יש חיילים בדרך
        if not self._is_path_clear(src_cell, dst_cell):
            print("Move blocked: Path is obstructed.")
            return

        # אם כל הבדיקות עוברות, נעביר את הפקודה לכלי המתאים
        moving_piece.on_command(cmd, now)

    def _is_path_clear(self, src_cell, dst_cell):
        dx = dst_cell[1] - src_cell[1]
        dy = dst_cell[0] - src_cell[0]
        
        step_x = 0
        if dx != 0:
            step_x = dx // abs(dx)
        
        step_y = 0
        if dy != 0:
            step_y = dy // abs(dy)

        # נבדוק רק אם התנועה היא בקו ישר
        if (step_x != 0 or step_y != 0) and (abs(dx) == abs(dy) or dx == 0 or dy == 0):
            cur_cell = (src_cell[0] + step_y, src_cell[1] + step_x)
            while cur_cell != dst_cell:
                if cur_cell in self.pos_to_piece:
                    return False
                cur_cell = (cur_cell[0] + step_y, cur_cell[1] + step_x)
        
        return True
