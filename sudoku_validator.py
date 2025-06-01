def is_valid_board(board):
    if not board or len(board) != 9 or any(len(row) != 9 for row in board):
        raise ValueError("Invalid 9x9 board")
    for r in range(9):
        row = [n for n in board[r] if n != 0]
        if len(row) != len(set(row)):
            return False
    for c in range(9):
        col = [board[r][c] for r in range(9) if board[r][c] != 0]
        if len(col) != len(set(col)):
            return False
    for sr in range(0, 9, 3):
        for sc in range(0, 9, 3):
            block = [board[sr+i][sc+j] for i in range(3) for j in range(3) if board[sr+i][sc+j] != 0]
            if len(block) != len(set(block)):
                return False
    return True

if __name__ == "__main__":
    sample_board = [[0]*9 for _ in range(9)]
    print("Valid board:", is_valid_board(sample_board))