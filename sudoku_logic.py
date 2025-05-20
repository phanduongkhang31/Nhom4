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
        is_corr = self.is_board_correct_when_known_complete(board, solution_board) # Hoặc self.is_board_correct(board, solution_board)
        return True, is_corr

    def is_board_complete(self, board):
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] == 0:
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
        # 1. Fill the grid completely with a valid solution
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)] # Reset grid
        self._solve_sudoku(self.grid)
        self.solution = [row[:] for row in self.grid] # Save the solution

        # 2. Remove numbers based on difficulty
        if difficulty == "easy":
            num_to_remove = self.size * self.size // 3 # Remove 1/3
        elif difficulty == "medium":
            num_to_remove = self.size * self.size // 2 # Remove 1/2
        elif difficulty == "hard":
            num_to_remove = self.size * self.size * 2 // 3 # Remove 2/3
        else: # very_easy or custom
            num_to_remove = self.size * self.size // 4

        count = 0
        while count < num_to_remove:
            r, c = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if self.grid[r][c] != 0:
                # Simple removal, no check for multiple solutions yet
                self.grid[r][c] = 0
                count += 1
        
        return self.grid, self.solution

    def check_move(self, board, r, c, num, solution_board):
        """Checks if the number is correct according to the solution."""
        if solution_board[r][c] == num:
            return True
        return False

    def is_board_complete(self, board):
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] == 0:
                    return False
        return True

    def is_board_correct(self, board, solution_board):
        if not self.is_board_complete(board):
            return False
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] != solution_board[r][c]:
                    return False
        return True

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