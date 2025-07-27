# Moves.py  – drop-in replacement
import pathlib
from typing import List, Tuple
class Moves:
    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """Initialize moves with rules from text file and board dimensions."""
        self.dims = dims  # Dimensions of the board (rows, cols)
        self.rules = self._load_rules(txt_path)  # Load movement rules from file
        self.piece_type = self._get_piece_type_from_path(txt_path)  # זיהוי סוג הכלי
        
    def _get_piece_type_from_path(self, txt_path: pathlib.Path) -> str:
        """Extract piece type from the file path."""
        # נתיב כמו: pieces/PB/moves.txt -> PB
        return txt_path.parent.name
        
    def _load_rules(self, txt_path: pathlib.Path) -> List[Tuple[int, int]]:
        """Load movement rules from a text file."""
        rules = []
        try:
            with txt_path.open('r') as file:
                for line in file:
                    # Parse each line as a tuple of integers (e.g., "1,2" -> (1, 2))
                    parts = line.strip().split(',')
                    if len(parts) != 2:
                        raise ValueError(f"Invalid format on line: {line}")
                    rules.append((int(parts[0]), int(parts[1])))
        except Exception as e:
            raise ValueError(f"Error loading rules from {txt_path}: {e}")
        return rules
        
    def get_moves(self, r: int, c: int, has_moved: bool = False, pos_to_piece: dict = None) -> List[Tuple[int, int]]:
        """Get all possible moves from a given position."""
        possible_moves = []
        
        # לוגיקה מיוחדת לפיונים
        if self.piece_type.startswith('P'):  # פיון (PW או PB)
            direction = 1 if self.piece_type == 'PB' else -1  # PB זז למטה, PW זז למעלה
            
            # תנועות קדימה - בסדר עולה של מרחק
            # צריך לבדוק שכל הדרך ריקה
            forward_moves = [(dr, dc) for dr, dc in self.rules if dc == 0]
            forward_moves.sort(key=lambda x: abs(x[0]))  # מיון לפי מרחק
            
            for dr, dc in forward_moves:
                # תנועה של 2 צעדים רק אם לא זז עדיין
                if abs(dr) == 2 and has_moved:
                    continue
                
                new_r, new_c = r + dr, c + dc
                # בדיקה שבתוך הלוח
                if 0 <= new_r < self.dims[0] and 0 <= new_c < self.dims[1]:
                    target_cell = (new_r, new_c)
                    
                    # אם יש כלי במקום - לא יכול לזוז לשם ולא מעבר לזה
                    if pos_to_piece is not None and target_cell in pos_to_piece:
                        break  # עוצר את כל התנועות הקדימה הבאות
                    
                    # אם המקום ריק - יכול לזוז
                    possible_moves.append(target_cell)
            
            # תנועות אכילה (אלכסונית וקדימה)
            if pos_to_piece is not None:
                # אכילה אלכסונית
                for dc in [-1, 1]:  # שמאל וימין
                    capture_r, capture_c = r + direction, c + dc
                    
                    if 0 <= capture_r < self.dims[0] and 0 <= capture_c < self.dims[1]:
                        target_cell = (capture_r, capture_c)
                        
                        if target_cell in pos_to_piece:
                            target_piece = pos_to_piece[target_cell]
                            # בדיקה שזה יריב (צבע שונה)
                            if target_piece.get_id()[1] != self.piece_type[1]:
                                possible_moves.append(target_cell)
                
                # אכילה קדימה
                capture_r, capture_c = r + direction, c
                if 0 <= capture_r < self.dims[0] and 0 <= capture_c < self.dims[1]:
                    target_cell = (capture_r, capture_c)
                    
                    if target_cell in pos_to_piece:
                        target_piece = pos_to_piece[target_cell]
                        # בדיקה שזה יריב (צבע שונה)
                        if target_piece.get_id()[1] != self.piece_type[1]:
                            possible_moves.append(target_cell)
        
        else:
            # לוגיקה רגילה לכלים שאינם פיונים
            for dr, dc in self.rules:
                new_r, new_c = r + dr, c + dc
                if 0 <= new_r < self.dims[0] and 0 <= new_c < self.dims[1]:
                    possible_moves.append((new_r, new_c))
                
        return possible_moves

