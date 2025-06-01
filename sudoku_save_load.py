import json

def save_game_to_file(state, filename="sudoku_save.json"):
    try:
        with open(filename, 'w') as f:
            json.dump(state, f, indent=4)
        print(f"Game saved to {filename}")
    except Exception as e:
        print(f"Save error: {e}")

def load_game_from_file(filename="sudoku_save.json"):
    try:
        with open(filename, 'r') as f:
            state = json.load(f)
        print(f"Game loaded from {filename}")
        return state
    except Exception as e:
        print(f"Load error: {e}")
        return None

if __name__ == "__main__":
    test_state = {"board_data": [[0]*9 for _ in range(9)], "score": 0}
    save_game_to_file(test_state, "test_save.json")
    loaded = load_game_from_file("test_save.json")
    print("Loaded data:", loaded)