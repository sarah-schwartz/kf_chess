import cv2
from Board import Board

class GameRenderer:
    def __init__(self, board: Board):
        self.board = board

    def draw(self, pieces: dict, focus_cell: tuple, focus_cell2: tuple, selected_source: tuple, selected_source2: tuple, now_ms: int):
        board_clone = self.board.clone()

        for piece in pieces.values():
            piece.draw_on_board(board_clone, now_ms)

        # Draw focus square for user 1 (yellow)
        if focus_cell:
            y, x = focus_cell
            x1 = x * self.board.cell_W_pix
            y1 = y * self.board.cell_H_pix
            x2 = (x + 1) * self.board.cell_W_pix
            y2 = (y + 1) * self.board.cell_H_pix
            cv2.rectangle(board_clone.img.img, (x1, y1), (x2, y2), (0, 255, 255), 2)

        # Draw focus square for user 2 (blue)
        if focus_cell2:
            y2_, x2_ = focus_cell2
            sx1 = x2_ * self.board.cell_W_pix
            sy1 = y2_ * self.board.cell_H_pix
            sx2 = (x2_ + 1) * self.board.cell_W_pix
            sy2 = (y2_ + 1) * self.board.cell_H_pix
            cv2.rectangle(board_clone.img.img, (sx1, sy1), (sx2, sy2), (255, 0, 0), 2)

        # Draw source selection square for user 1
        if selected_source:
            sy, sx = selected_source
            sx1 = sx * self.board.cell_W_pix
            sy1 = sy * self.board.cell_H_pix
            sx2 = (sx + 1) * self.board.cell_W_pix
            sy2 = (sy + 1) * self.board.cell_H_pix
            cv2.rectangle(board_clone.img.img, (sx1, sy1), (sx2, sy2), (0, 0, 255), 2)

        # Draw source selection square for user 2
        if selected_source2:
            sy, sx = selected_source2
            sx1 = sx * self.board.cell_W_pix
            sy1 = sy * self.board.cell_H_pix
            sx2 = (sx + 1) * self.board.cell_W_pix
            sy2 = (sy + 1) * self.board.cell_H_pix
            cv2.rectangle(board_clone.img.img, (sx1, sy1), (sx2, sy2), (0, 255, 0), 2)

        return board_clone.img.img

    @staticmethod
    def show(image):
        cv2.imshow("Chess", image)
        cv2.waitKey(1)

    @staticmethod
    def destroy_windows():
        cv2.destroyAllWindows()
