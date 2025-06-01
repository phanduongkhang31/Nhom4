def determine_difficulty(board):
    if not board or len(board) != 9 or any(len(row) != 9 for row in board):
        raise ValueError("Bảng Sudoku không hợp lệ")
    filled = sum(1 for row in board for cell in row if cell != 0)
    ratio = filled / 81
    if ratio >= 0.6:
        return "very easy"
    elif ratio >= 0.45:
        return "easy"
    elif ratio >= 0.3:
        return "medium"
    elif ratio >= 0.2:
        return "hard"
    else:
        return "expert"

if __name__ == "__main__":
    board = [[0]*9 for _ in range(9)]
    print(determine_difficulty(board))