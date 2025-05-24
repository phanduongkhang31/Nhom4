# sudoku_logic.py
import random

class SudokuGenerator:
    def __init__(self, size=9):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.solution = [[0 for _ in range(size)] for _ in range(size)]

    def _is_valid(self, grid, r, c, num):
        # Check row
        for x in range(self.size):
            if grid[r][x] == num:
                return False
        # Check column
        for x in range(self.size):
            if grid[x][c] == num:
                return False
        # Check 3x3 subgrid (assuming size 9)
        if self.size == 9:
            start_row, start_col = r - r % 3, c - c % 3
            for i in range(3):
                for j in range(3):
                    if grid[i + start_row][j + start_col] == num:
                        return False
        return True

    def _solve_sudoku(self, grid):
        for r in range(self.size):
            for c in range(self.size):
                if grid[r][c] == 0:
                    nums = list(range(1, self.size + 1))
                    random.shuffle(nums) # Randomize number choice for varied solutions
                    for num in nums:
                        if self._is_valid(grid, r, c, num):
                            grid[r][c] = num
                            if self._solve_sudoku(grid):
                                return True
                            grid[r][c] = 0 # Backtrack
                    return False
        return True
    
    def check_board_state(self, board, solution_board):
        """
        Checks if the board is complete AND correct.
        Returns a tuple (is_complete, is_correct_if_complete).
        """
        is_comp = self.is_board_complete(board)
        if not is_comp:
            return False, False # Not complete, so not correct in the final sense

        # If complete, then check correctness
        is_corr = self.is_board_correct_when_known_complete(board, solution_board) 
        return True, is_corr

    def is_board_complete(self, board):
        for r_idx in range(self.size): # Đổi tên biến để tránh trùng lặp
            for c_idx in range(self.size): # Đổi tên biến
                if board[r_idx][c_idx] == 0:
                    return False
        return True

    def is_board_correct_when_known_complete(self, board, solution_board):
        # Assumes board is already checked for completeness
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] != solution_board[r][c]:
                    return False
        return True

    def generate_puzzle(self, difficulty="medium"):
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)] 
        self._solve_sudoku(self.grid)
        self.solution = [row[:] for row in self.grid] 

        # Điều chỉnh số ô cần xóa dựa trên độ khó
        num_cells_to_remove_map = {
            "very_easy": self.size * self.size * 20 // 81, # Khoảng 20 ô cho 9x9
            "easy": self.size * self.size * 27 // 81,      # Khoảng 27 ô
            "medium": self.size * self.size * 40 // 81,    # Khoảng 40 ô
            "hard": self.size * self.size * 54 // 81,      # Khoảng 54 ô
            "expert": self.size * self.size * 60 // 81     # Khoảng 60 ô
        }
        # Mặc định là medium nếu không tìm thấy độ khó
        num_to_remove = num_cells_to_remove_map.get(difficulty.lower(), self.size * self.size * 40 // 81)

        cells_removed_count = 0
        all_cells = []
        for r_idx in range(self.size):
            for c_idx in range(self.size):
                all_cells.append((r_idx, c_idx))
        random.shuffle(all_cells)

        for r_coord, c_coord in all_cells:
            if cells_removed_count >= num_to_remove:
                break
            if self.grid[r_coord][c_coord] != 0:
                # temp_val = self.grid[r_coord][c_coord] # Giữ lại để kiểm tra tính duy nhất nếu cần
                self.grid[r_coord][c_coord] = 0
                # TODO: Thêm logic kiểm tra tính duy nhất của lời giải nếu muốn tạo puzzle chuẩn
                cells_removed_count += 1
        
        return self.grid, self.solution

    def check_move(self, board, r, c, num, solution_board):
        """Kiểm tra xem nước đi có đúng với bảng giải không."""
        if 0 < num <= self.size:
             return solution_board[r][c] == num
        if num == 0: # Xóa ô không được coi là "đúng" so với số trong bảng giải
            return False
        return False


    def is_board_correct(self, board, solution_board):
        if not self.is_board_complete(board):
            return False
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] != solution_board[r][c]:
                    return False
        return True

    def get_hint(self, current_board, solution_board):
        """
        Tìm một ô trống và trả về tọa độ cùng số đúng.
        Nếu không có ô trống, tìm một ô sai và gợi ý sửa.
        Trả về (row, col, number) hoặc None nếu không thể gợi ý (bảng đã đúng).
        """
        empty_cells = []
        incorrect_filled_cells = []

        for r in range(self.size):
            for c in range(self.size):
                if current_board[r][c] == 0:
                    empty_cells.append((r, c))
                # Chỉ kiểm tra ô đã điền số (khác 0) và khác với bảng giải
                elif current_board[r][c] != 0 and current_board[r][c] != solution_board[r][c]:
                    incorrect_filled_cells.append((r,c))
        
        if empty_cells:
            # Ưu tiên gợi ý cho ô trống trước
            r_hint, c_hint = random.choice(empty_cells)
            num_hint = solution_board[r_hint][c_hint]
            return r_hint, c_hint, num_hint
        
        if incorrect_filled_cells:
            # Nếu không có ô trống, nhưng có ô sai, gợi ý sửa
            r_hint, c_hint = random.choice(incorrect_filled_cells)
            num_hint = solution_board[r_hint][c_hint]
            return r_hint, c_hint, num_hint

        # Nếu không có ô trống và không có ô sai (tức là bảng đã hoàn thành đúng)
        return None

# Example usage (for testing)
if __name__ == "__main__":
    generator = SudokuGenerator()
    puzzle, solution = generator.generate_puzzle("easy")
    print("Puzzle:")
    for row in puzzle:
        print(row)
    print("\nSolution:")
    for row in solution:
        print(row)
    
    test_board = [p_row[:] for p_row in puzzle]
    hint = generator.get_hint(test_board, solution)
    if hint:
        print(f"\nHint for empty puzzle: Place {hint[2]} at ({hint[0]}, {hint[1]})")
    else:
        print("\nNo hint available (puzzle might be already solved or no empty cells).")