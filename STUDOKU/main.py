import customtkinter as ctk
from tkinter import messagebox, StringVar, colorchooser
import json
import os
import uuid # For unique game IDs

# --- Local Module Imports ---
from ui import MainMenuScreen, GameScreenUI, NewGameDialog, SettingsScreen, StatisticsScreen
from sudoku_logic import SudokuGenerator
from client import SudokuClient # For multiplayer functionality

# --- Constants ---
SAVE_FILE_PATH = "sudoku_save.json"         # Stores saved classic game state
SETTINGS_FILE_PATH = "sudoku_settings.json" # Stores app settings (theme, custom colors)
USER_STATS_FILE_PATH = "sudoku_user_stats.json" # Stores user game statistics
TIMER_INTERVAL_MS = 1000                    # Interval for the classic game timer (1 second)

class SudokuApp(ctk.CTk):
    """
    The main application class for Sudoku Pro Deluxe.
    Inherits from customtkinter.CTk to create the main window.
    Handles UI switching, game logic, state management, and file I/O.
    """
    def __init__(self):
        super().__init__()
        self.title("Sudoku Pro Deluxe")
        self.minsize(750, 850) # Minimum window size
        self.resizable(True, True)

        # --- Application Settings & Appearance ---
        self.appearance_setting = "dark" # Default theme
        self.board_colors_config = {}    # Stores custom board colors from settings
        self.load_app_settings()         # Load theme and custom colors from file
        ctk.set_appearance_mode(self.appearance_setting)
        ctk.set_default_color_theme("blue") # Default CTk theme

        # --- Game Logic & State ---
        self.sudoku_generator = SudokuGenerator() # For generating new puzzles
        self.current_frame = None                 # Holds the currently displayed UI screen
        
        # Multiplayer State
        self.sudoku_client = None # Instance of SudokuClient, created when needed
        self.is_multiplayer = False # Flag for multiplayer mode

        # Classic Game State
        self.classic_game_state = {} # Stores all data for an ongoing classic game
                                     # e.g., board, solution, time, mistakes
        self.is_classic_game_active = False # Flag for active classic game
        self._classic_timer_job = None      # Stores the 'after' job ID for the classic timer
        self.selected_cell_classic = None   # (r, c) of selected cell in classic mode
        self.undo_stack = []                # Stack for undo functionality in classic mode

        # User Statistics
        self.user_stats = {} # Stores player statistics (wins, best times, etc.)
        self.just_won_classic_game = False # Flag to prevent win streak reset if returning to menu after win
        self.load_user_stats() # Load stats from file

        # --- Initialization ---
        self.load_classic_game() # Load any saved classic game
        self.show_main_menu()    # Display the main menu on startup
        self.protocol("WM_DELETE_WINDOW", self.quit_application) # Handle window close button

    # --- User Statistics Management ---
    def _default_user_stats(self):
        """Returns a dictionary with the default structure for user statistics."""
        difficulties = ["very_easy", "easy", "medium", "hard", "expert"]
        return {
            "games_won_total": 0,
            "perfect_wins_total": 0, # Wins with 0 mistakes, 0 hints
            "current_win_streak": 0,
            "best_win_streak": 0,
            "best_times": {d: float('inf') for d in difficulties}, # Best time per difficulty
            "games_won_by_difficulty": {d: 0 for d in difficulties},
            "perfect_wins_by_difficulty": {d: 0 for d in difficulties},
        }

    def load_user_stats(self):
        """Loads user statistics from USER_STATS_FILE_PATH."""
        default_stats = self._default_user_stats()
        if os.path.exists(USER_STATS_FILE_PATH):
            try:
                with open(USER_STATS_FILE_PATH, 'r') as f:
                    loaded_stats = json.load(f)
                
                # Merge loaded stats with defaults to ensure all keys exist and handle new stats
                self.user_stats = default_stats.copy()
                for key, value in loaded_stats.items():
                    if key in self.user_stats:
                        if isinstance(self.user_stats[key], dict) and isinstance(value, dict):
                            self.user_stats[key].update(value) # Merge dictionaries (e.g., best_times)
                        else:
                            self.user_stats[key] = value # Overwrite simple values
            except Exception as e:
                print(f"Error loading user stats: {e}. Using defaults.")
                self.user_stats = default_stats
        else:
            print("User stats file not found. Initializing.")
            self.user_stats = default_stats
            self.save_user_stats() # Create the file with defaults

    def save_user_stats(self):
        """Saves current user statistics to USER_STATS_FILE_PATH."""
        try:
            with open(USER_STATS_FILE_PATH, 'w') as f:
                json.dump(self.user_stats, f, indent=2)
        except Exception as e:
            print(f"Error saving user stats: {e}")

    def update_stats_on_win(self, difficulty, time_played, mistakes_made, hints_used_count):
        """Updates user statistics after a classic game win."""
        stats = self.user_stats
        stats["games_won_total"] += 1
        stats["games_won_by_difficulty"][difficulty] = stats["games_won_by_difficulty"].get(difficulty, 0) + 1
        
        is_perfect_win = (mistakes_made == 0 and hints_used_count == 0)
        if is_perfect_win:
            stats["perfect_wins_total"] += 1
            stats["perfect_wins_by_difficulty"][difficulty] = stats["perfect_wins_by_difficulty"].get(difficulty, 0) + 1
            
        stats["current_win_streak"] += 1
        stats["best_win_streak"] = max(stats["best_win_streak"], stats["current_win_streak"])
        
        if difficulty in stats["best_times"]:
            stats["best_times"][difficulty] = min(stats["best_times"].get(difficulty, float('inf')), time_played)
            
        self.just_won_classic_game = True # Set flag
        self.save_user_stats()

    # --- Application Settings Management (Theme, Custom Colors) ---
    def get_default_board_colors_for_theme(self):
        """Gets default board colors based on the current UI theme."""
        from ui import ColorScheme # Local import to avoid potential circular dependency at module level
        temp_scheme = ColorScheme().get_colors() # Gets base colors for current theme
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        return {
            "cell_default_bg_custom": temp_scheme['cell_default'],
            "cell_selected_custom": temp_scheme['cell_selected'],
            "cell_related_custom": temp_scheme['cell_related'],
            "cell_same_number_custom": temp_scheme['cell_same_number'],
            "cell_hint_fill_custom": temp_scheme['cell_hint'],
            "cell_fixed_text_custom": temp_scheme['cell_fixed'][1] if is_dark else temp_scheme['cell_fixed'][0],
            "cell_user_text_custom": temp_scheme['cell_user'][1] if is_dark else temp_scheme['cell_user'][0],
            "cell_error_text_custom": temp_scheme['cell_error'][1] if is_dark else temp_scheme['cell_error'][0],
        }

    def load_app_settings(self):
        """Loads application settings (theme, custom board colors) from file."""
        try:
            if os.path.exists(SETTINGS_FILE_PATH):
                with open(SETTINGS_FILE_PATH, 'r') as f:
                    settings = json.load(f)
                self.appearance_setting = settings.get("appearance_mode", "dark")
                self.board_colors_config = settings.get("board_colors", {})
            else: # No settings file, use defaults and save
                self.appearance_setting = "dark"
                self.board_colors_config = {}
                self.save_app_settings()
        except Exception as e:
            print(f"Error loading app settings: {e}. Using defaults.")
            self.appearance_setting = "dark"
            self.board_colors_config = {}

    def save_app_settings(self):
        """Saves current application settings to file."""
        try:
            settings = {
                "appearance_mode": self.appearance_setting,
                "board_colors": self.board_colors_config
            }
            with open(SETTINGS_FILE_PATH, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving app settings: {e}")

    def get_current_board_colors_config(self):
        """Returns the currently loaded custom board colors."""
        return self.board_colors_config

    def update_board_colors_config(self, new_config):
        """Updates and saves new custom board colors. Refreshes UI if needed."""
        self.board_colors_config = new_config.copy()
        self.save_app_settings()
        
        # If game screen is active, update its board colors immediately
        if isinstance(self.current_frame, GameScreenUI) and self.is_classic_game_active and self.classic_game_state.get('board_data'):
            # GameScreenUI needs to re-fetch colors with the new config
            self.current_frame.board_specific_colors = self.current_frame.controller.ui.ColorScheme().get_colors(self.board_colors_config)
            self.current_frame.update_board_display(
                self.classic_game_state['board_data'],
                self.classic_game_state['fixed_mask'],
                self.classic_game_state.get('error_cells'),
                self.classic_game_state.get('pencil_data')
            )
        # If settings screen is active, repopulate color inputs
        elif isinstance(self.current_frame, SettingsScreen):
            self.current_frame._populate_board_color_inputs()


    def apply_appearance_mode(self, mode):
        """Applies a new appearance mode (light/dark) and refreshes the UI."""
        if mode not in ["light", "dark"] or self.appearance_setting == mode:
            # If already in the mode, or invalid mode, just ensure SettingsScreen UI is correct
            if isinstance(self.current_frame, SettingsScreen):
                self.current_frame._update_theme_button_styles()
                self.current_frame._populate_board_color_inputs() # Colors might depend on theme
            return

        self.appearance_setting = mode
        ctk.set_appearance_mode(self.appearance_setting)
        self.save_app_settings()
        
        # To properly re-render all CTk widgets with the new theme,
        # it's often easiest to rebuild the current screen.
        current_screen_type = type(self.current_frame)
        if current_screen_type:
            args, kwargs = [], {} # Arguments for re-initializing the screen
            if isinstance(self.current_frame, GameScreenUI):
                kwargs['game_mode'] = self.current_frame.game_mode # Preserve game mode
            self.switch_frame(current_screen_type, *args, **kwargs)


    # --- UI Navigation and Screen Management ---
    def switch_frame(self, frame_class, *args, **kwargs):
        """Destroys the current screen and displays a new one."""
        if self.current_frame:
            self.stop_any_timers() # Stop timers before destroying frame that might use them
            self.current_frame.pack_forget()
            self.current_frame.destroy()
        
        self.current_frame = frame_class(self, self, *args, **kwargs) # Pass self (app) and self (as controller)
        self.current_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def show_main_menu(self):
        """Switches to the MainMenuScreen."""
        # Disconnect multiplayer if returning to menu
        if self.is_multiplayer and self.sudoku_client and self.sudoku_client.is_connected:
            self.sudoku_client.disconnect()
            self.sudoku_client = None
        
        # Reset win streak if abandoning a classic game
        if self.is_classic_game_active and not self.just_won_classic_game:
            self.user_stats["current_win_streak"] = 0
            self.save_user_stats()
            print("Win streak reset: abandoned classic game.")

        self.is_classic_game_active = False
        self.is_multiplayer = False
        self.stop_any_timers() # Ensure classic timer is stopped
        self.switch_frame(MainMenuScreen)
        
        # Update "Continue" button state on main menu
        if isinstance(self.current_frame, MainMenuScreen):
            self.current_frame.update_continue_button_state(
                self.classic_game_state if self.classic_game_state.get('board_data') else None
            )

    def show_settings_screen(self):
        """Switches to the SettingsScreen."""
        self.is_classic_game_active = False # Not in game when in settings
        self.is_multiplayer = False
        self.stop_any_timers()
        self.switch_frame(SettingsScreen)

    def show_statistics_screen(self):
        """Switches to the StatisticsScreen."""
        self.is_classic_game_active = False
        self.is_multiplayer = False
        self.stop_any_timers()
        self.switch_frame(StatisticsScreen)

    def show_new_classic_game_dialog(self):
        """Displays the dialog to choose difficulty for a new classic game."""
        dialog = NewGameDialog(self, title="Tạo Game Mới")
        self.wait_window(dialog) # Wait for dialog to close
        
        if hasattr(dialog, 'ok_pressed') and dialog.ok_pressed and dialog.result:
            self.start_new_classic_game(dialog.result) # Start game with selected difficulty

    # --- Classic Game Mode Logic ---
    def start_new_classic_game(self, difficulty):
        """Starts a new classic Sudoku game with the given difficulty."""
        # Reset win streak if starting new while another game was active (and not just won)
        if self.is_classic_game_active and not self.just_won_classic_game:
            self.user_stats["current_win_streak"] = 0
            self.save_user_stats()

        self.just_won_classic_game = False # Reset flag for new game
        self.is_classic_game_active = True
        self.is_multiplayer = False
        self.undo_stack = [] # Clear undo history

        # Determine game parameters based on difficulty
        max_m = 3 if difficulty.lower() in ["hard", "expert"] else 5 # Max mistakes
        hints_r = 6 # Hints available

        board, solution = self.sudoku_generator.generate_puzzle(difficulty)
        if not board or not solution:
            messagebox.showerror("Lỗi", "Không thể tạo bảng Sudoku.", parent=self)
            return

        fixed_mask = [[(board[r][c] != 0) for c in range(9)] for r in range(9)]
        
        # Initialize classic_game_state
        self.classic_game_state = {
            'board_data': board,
            'solution_data': solution,
            'fixed_mask': fixed_mask,
            'pencil_data': {},
            'time_played': 0,
            'mistakes': 0,
            'max_mistakes': max_m,
            'difficulty': difficulty,
            'score': 0,
            'error_cells': set(), # Stores (r,c) of cells with incorrect numbers
            'game_id': str(uuid.uuid4()), # Unique ID for this game instance
            'hints_available': hints_r,
            'hints_used_count': 0
        }
        self.selected_cell_classic = None
        
        self.switch_frame(GameScreenUI, game_mode="classic")
        if isinstance(self.current_frame, GameScreenUI):
            ui = self.current_frame
            gs = self.classic_game_state
            ui.reset_ui_for_new_game() # Prepare UI
            # Update UI with new game data
            ui.difficulty_ui_text = gs['difficulty']
            ui.score_ui = gs.get('score',0)
            ui.mistakes_count_ui = gs['mistakes']
            ui.time_seconds_ui = gs['time_played']
            ui.max_mistakes_ui = gs['max_mistakes']
            if hasattr(ui, 'hints_remaining_var'): # Ensure var exists
                ui.hints_remaining_var.set(f"💡 Gợi ý ({gs['hints_available']})")
            
            ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs.get('pencil_data',{}))
            ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
            
            self.start_classic_timer()
            self.save_classic_game() # Save progress

    def continue_classic_game(self):
        """Continues a previously saved classic game."""
        if not self.classic_game_state.get('board_data'):
            messagebox.showinfo("Thông báo", "Không có game nào để tiếp tục.", parent=self)
            return

        self.is_classic_game_active = True
        self.is_multiplayer = False
        gs = self.classic_game_state
        
        # Ensure defaults for older save files if keys are missing
        gs.setdefault('max_mistakes', 3 if gs.get('difficulty', 'medium').lower() in ["hard", "expert"] else 5)
        gs.setdefault('hints_available', 6)
        gs.setdefault('hints_used_count', 0)

        self.switch_frame(GameScreenUI, game_mode="classic")
        if isinstance(self.current_frame, GameScreenUI):
            ui = self.current_frame
            ui.reset_ui_for_new_game()
            # Update UI with loaded game data
            ui.difficulty_ui_text = gs['difficulty']
            ui.score_ui = gs.get('score',0)
            ui.mistakes_count_ui = gs['mistakes']
            ui.time_seconds_ui = gs['time_played']
            ui.max_mistakes_ui = gs['max_mistakes']
            if hasattr(ui, 'hints_remaining_var'):
                ui.hints_remaining_var.set(f"💡 Gợi ý ({gs['hints_available']})")

            ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs.get('error_cells', set()), gs.get('pencil_data', {}))
            ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
            
            self.start_classic_timer() # Resume timer

    def select_cell(self, r, c):
        """Handles cell selection in both classic and multiplayer modes."""
        if not self.is_classic_game_active and not self.is_multiplayer:
            return # No game active
        
        current_ui = self.current_frame
        if not isinstance(current_ui, GameScreenUI):
            return

        if self.is_classic_game_active:
            self.selected_cell_classic = (r, c)
            related_coords = self.get_related_coords_for_highlight(r, c)
            current_ui.highlight_selected_cell(r, c, related_coords)
        elif self.is_multiplayer:
            # In multiplayer, selection is simpler, just for input focus.
            # Server might have its own concept of "active cell" if turn-based highlighting is desired.
            current_ui.selected_cell_coords = (r,c) # GameScreenUI tracks its own selected_cell for MP input
            current_ui.highlight_selected_cell(r, c, []) # Basic highlight

    def input_number(self, num_to_input, is_pencil_mode):
        """Handles number input from the number pad."""
        current_ui = self.current_frame
        if not isinstance(current_ui, GameScreenUI): return

        # --- Classic Mode Input ---
        if self.is_classic_game_active:
            if not self.selected_cell_classic: return # No cell selected
            r, c = self.selected_cell_classic
            gs = self.classic_game_state # Game State shorthand
            
            if gs['fixed_mask'][r][c]: return # Cannot change fixed cells

            # Save current state for Undo
            prev_board_state = [row[:] for row in gs['board_data']]
            prev_pencil_state = {k: v.copy() for k, v in gs.get('pencil_data', {}).items()}
            prev_error_state = gs.get('error_cells', set()).copy()
            prev_mistakes = gs.get('mistakes', 0)
            prev_score = gs.get('score', 0)
            self.undo_stack.append({
                'board_data': prev_board_state, 'pencil_data': prev_pencil_state,
                'error_cells': prev_error_state, 'mistakes': prev_mistakes, 'score': prev_score
            })
            if len(self.undo_stack) > 50: self.undo_stack.pop(0) # Limit undo stack size

            # Pencil Mode Logic
            if is_pencil_mode:
                pencil_marks_for_cell = gs['pencil_data'].setdefault((r, c), set())
                if num_to_input in pencil_marks_for_cell:
                    pencil_marks_for_cell.remove(num_to_input)
                else:
                    pencil_marks_for_cell.add(num_to_input)
                if not pencil_marks_for_cell: # If set becomes empty
                    del gs['pencil_data'][(r,c)]
                
                # Clear main number and error if placing pencil marks
                if gs['board_data'][r][c] != 0:
                    gs['board_data'][r][c] = 0
                    gs['error_cells'].discard((r,c)) # Clear error from this cell
            
            # Normal Number Input Logic
            else:
                old_number_in_cell = gs['board_data'][r][c]
                gs['board_data'][r][c] = num_to_input # Place the number
                
                if (r,c) in gs['pencil_data']: del gs['pencil_data'][(r,c)] # Clear pencil marks
                gs['error_cells'].discard((r,c)) # Clear previous error on this cell

                if num_to_input != 0: # If not erasing
                    # Check if the number is incorrect
                    if num_to_input != gs['solution_data'][r][c]:
                        gs['error_cells'].add((r,c)) # Mark as error
                    
                    # Update mistakes and score
                    if old_number_in_cell != num_to_input and num_to_input != gs['solution_data'][r][c]: # Made a mistake
                        gs['mistakes'] += 1
                        gs['score'] = max(0, gs.get('score', 0) - 50) # Penalty
                    elif num_to_input == gs['solution_data'][r][c]: # Corrected a mistake or filled empty
                        if old_number_in_cell != 0 and old_number_in_cell != num_to_input: # Corrected a wrong number
                            gs['score'] = gs.get('score', 0) + 20
                        elif old_number_in_cell == 0 : # Filled an empty cell correctly
                            gs['score'] = gs.get('score', 0) + 10
            
            # Update UI display
            current_ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs['pencil_data'])
            current_ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])

            # Check for Game Over (too many mistakes)
            if not is_pencil_mode and num_to_input != 0 and gs['mistakes'] >= gs.get('max_mistakes', 3) and gs.get('max_mistakes', 3) > 0:
                current_ui.show_message("Game Over", "Bạn đã mắc quá nhiều lỗi!", "error")
                self.stop_any_timers()
                self.is_classic_game_active = False
                self.user_stats["current_win_streak"] = 0 # Reset streak on loss
                self.save_user_stats()
                self.save_classic_game() # Save the lost game state (can be reviewed)
                return

            # Check for Win Condition
            if not is_pencil_mode and self.is_board_complete_and_correct():
                self.stop_any_timers()
                gs['score'] = gs.get('score', 0) + 1000 # Win bonus
                self.update_stats_on_win(gs['difficulty'], gs['time_played'], gs['mistakes'], gs.get('hints_used_count', 0))
                current_ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
                current_ui.show_message("Chúc Mừng!", "Bạn đã giải thành công Sudoku!", "info")
                self.classic_game_state = {} # Clear current game
                self.save_classic_game()     # This will effectively delete the save file
                self.show_main_menu()
                return
            
            self.save_classic_game() # Save progress after each move

        # --- Multiplayer Mode Input ---
        elif self.is_multiplayer and self.sudoku_client and current_ui.selected_cell_coords and not is_pencil_mode:
            # In MP, GameScreenUI tracks selected_cell_coords for its own input focus
            r_mp, c_mp = current_ui.selected_cell_coords
            self.sudoku_client.submit_player_move(r_mp, c_mp, num_to_input) # Send move to server
        elif self.is_multiplayer and is_pencil_mode:
            current_ui.show_message("Thông báo", "Viết chì không dùng trong chơi mạng.", "warning")

    def erase_selected(self):
        """Erases the number or pencil marks from the selected cell."""
        current_ui = self.current_frame
        if not isinstance(current_ui, GameScreenUI): return

        if self.is_classic_game_active and self.selected_cell_classic:
            r, c = self.selected_cell_classic
            gs = self.classic_game_state
            if gs['fixed_mask'][r][c]: return # Cannot erase fixed cells

            # If there's a number, erasing is like inputting 0
            if gs['board_data'][r][c] != 0:
                self.input_number(0, False) # is_pencil_mode = False
                return
            # If there are pencil marks, clear them
            elif (r,c) in gs.get('pencil_data', {}):
                # Save state for Undo (only for pencil mark removal)
                prev_b = [row[:] for row in gs['board_data']]; prev_p = {k: v.copy() for k, v in gs.get('pencil_data', {}).items()}; prev_e = gs.get('error_cells', set()).copy(); prev_m = gs.get('mistakes', 0); prev_s = gs.get('score', 0)
                self.undo_stack.append({'board_data': prev_b, 'pencil_data': prev_p, 'error_cells': prev_e, 'mistakes': prev_m, 'score': prev_s});
                if len(self.undo_stack) > 50: self.undo_stack.pop(0)

                if (r,c) in gs['pencil_data']: del gs['pencil_data'][(r,c)]
                current_ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs['pencil_data'])
                self.save_classic_game()
        
        elif self.is_multiplayer and self.sudoku_client and current_ui.selected_cell_coords:
            # In MP, erase is also submitting 0 to the server
            r_mp, c_mp = current_ui.selected_cell_coords
            self.sudoku_client.submit_player_move(r_mp, c_mp, 0)

    def undo_move(self):
        """Reverts the last move in classic mode."""
        if not self.undo_stack or not self.is_classic_game_active:
            # Optionally: current_ui.show_message("Thông báo", "Không có gì để hoàn tác.", "info")
            return False
            
        current_ui = self.current_frame
        if not isinstance(current_ui, GameScreenUI): return False

        prev_state = self.undo_stack.pop()
        gs = self.classic_game_state
        gs.update(prev_state) # Restore game state attributes
        
        current_ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs['pencil_data'])
        current_ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
        self.save_classic_game()
        return True

    def request_hint(self):
        """Provides a hint for the selected cell in classic mode."""
        ui = self.current_frame
        if not isinstance(ui, GameScreenUI): return

        if self.is_classic_game_active:
            if not self.selected_cell_classic :
                ui.show_message("Gợi ý", "Vui lòng chọn một ô.", "warning")
                return
            
            gs = self.classic_game_state
            if gs.get('hints_available', 0) <= 0:
                ui.show_message("Gợi ý", "Hết lượt gợi ý!", "warning")
                return
            
            r, c = self.selected_cell_classic
            # Don't give hint for fixed cells or already correct cells
            if gs['fixed_mask'][r][c] or \
               (gs['board_data'][r][c] != 0 and gs['board_data'][r][c] == gs['solution_data'][r][c]):
                ui.show_message("Gợi ý", "Ô này không cần gợi ý.", "info")
                return

            # Save state for Undo before applying hint
            prev_b = [row[:] for row in gs['board_data']]; prev_p = {k: v.copy() for k, v in gs.get('pencil_data', {}).items()}; prev_e = gs.get('error_cells', set()).copy(); prev_m = gs.get('mistakes', 0); prev_s = gs.get('score', 0)
            self.undo_stack.append({'board_data': prev_b, 'pencil_data': prev_p, 'error_cells': prev_e, 'mistakes': prev_m, 'score': prev_s});
            if len(self.undo_stack) > 50: self.undo_stack.pop(0)

            correct_number = gs['solution_data'][r][c]
            gs['board_data'][r][c] = correct_number
            if (r,c) in gs['pencil_data']: del gs['pencil_data'][(r,c)] # Clear pencil marks
            gs['error_cells'].discard((r,c)) # Clear error state
            gs['hints_available'] -= 1
            gs['hints_used_count'] = gs.get('hints_used_count', 0) + 1
            gs['score'] = max(0, gs.get('score', 0) - 75) # Penalty for hint
            
            if hasattr(ui, 'hints_remaining_var'):
                 ui.hints_remaining_var.set(f"💡 Gợi ý ({gs['hints_available']})")

            ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs['pencil_data'])
            ui.update_cell_display(r, c, correct_number, False, False, None, is_hint_fill=True) # Special hint fill
            ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])

            # Temporarily highlight the hint, then revert to normal cell display
            def clear_visual_hint():
                if not self.is_classic_game_active or not gs.get('board_data') or not ui.winfo_exists(): return
                is_err = (r,c) in gs['error_cells'] # Recheck error status after hint
                ui.update_cell_display(r, c, gs['board_data'][r][c], gs['fixed_mask'][r][c], is_err, gs['pencil_data'].get((r,c)), is_hint_fill=False)
                if self.selected_cell_classic == (r,c): # Re-apply selection highlight
                    rel = self.get_related_coords_for_highlight(r,c)
                    ui.highlight_selected_cell(r,c,rel)
            self.after(1200, clear_visual_hint) # Clear visual hint after 1.2 seconds

            self.save_classic_game()
            
            # Check for win after hint
            if self.is_board_complete_and_correct():
                self.stop_any_timers()
                gs['score'] = gs.get('score', 0) + 1000 # Win bonus (already penalized for hint)
                self.update_stats_on_win(gs['difficulty'], gs['time_played'], gs['mistakes'], gs.get('hints_used_count', 0))
                ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
                ui.show_message("Chúc Mừng!", "Bạn đã giải thành công!", "info")
                self.classic_game_state = {}; self.save_classic_game(); self.show_main_menu()
        
        elif self.is_multiplayer:
            ui.show_message("Gợi ý", "Gợi ý không có trong chơi mạng.", "info")

    def is_board_complete_and_correct(self):
        """Checks if the classic game board is fully and correctly filled."""
        gs = self.classic_game_state
        if not gs or not gs.get('board_data') or not gs.get('solution_data'):
            return False
        for r in range(9):
            for c in range(9):
                if gs['board_data'][r][c] == 0 or \
                   gs['board_data'][r][c] != gs['solution_data'][r][c]:
                    return False
        return True

    def get_related_coords_for_highlight(self, r, c):
        """Returns a list of coordinates related to (r,c) for highlighting."""
        rel = set()
        # Row and Column
        for i in range(9):
            rel.add((r, i))
            rel.add((i, c))
        # Subgrid (3x3 box)
        sr, sc = (r // 3) * 3, (c // 3) * 3 # Top-left of subgrid
        for i in range(3):
            for j in range(3):
                rel.add((sr + i, sc + j))
        return list(rel)

    def start_classic_timer(self):
        """Starts or continues the timer for classic games."""
        if self._classic_timer_job: # Cancel existing job if any
            self.after_cancel(self._classic_timer_job)
            self._classic_timer_job = None
            
        if self.is_classic_game_active and self.classic_game_state.get('board_data'):
            gs = self.classic_game_state
            gs['time_played'] += 1
            if isinstance(self.current_frame, GameScreenUI):
                # Update UI directly for responsiveness
                self.current_frame.time_seconds_ui = gs['time_played']
                self.current_frame._update_timer_display() # Call GameScreenUI's method
            
            self._classic_timer_job = self.after(TIMER_INTERVAL_MS, self.start_classic_timer)

    def stop_any_timers(self):
        """Stops any active game timers (currently only classic timer)."""
        if self._classic_timer_job:
            self.after_cancel(self._classic_timer_job)
            self._classic_timer_job = None

    # --- File I/O for Game State ---
    def load_classic_game(self):
        """Loads a saved classic game state from SAVE_FILE_PATH."""
        try:
            if os.path.exists(SAVE_FILE_PATH):
                with open(SAVE_FILE_PATH, 'r') as f:
                    data = json.load(f)
                if data and data.get('board_data'): # Basic check for valid save data
                    # Convert pencil_data keys from "r,c" strings to (r,c) tuples
                    pencil_data = {tuple(map(int, k.split(','))): set(v)
                                   for k, v in data.get('pencil_data', {}).items()}
                    # Convert error_cells from list of lists to set of tuples
                    error_cells = set(map(tuple, data.get('error_cells', [])))
                    
                    self.classic_game_state = {**data, 'pencil_data': pencil_data, 'error_cells': error_cells}
                    self.classic_game_state.setdefault('hints_used_count', 0) # For older saves
            else:
                self.classic_game_state = {} # No save file
        except Exception as e:
            print(f"Lỗi tải game: {e}")
            self.classic_game_state = {}

    def save_classic_game(self):
        """Saves the current classic game state to SAVE_FILE_PATH."""
        try:
            # If no active game or board, remove save file (game finished or reset)
            if not self.classic_game_state or not self.classic_game_state.get('board_data'):
                if os.path.exists(SAVE_FILE_PATH):
                    try: os.remove(SAVE_FILE_PATH)
                    except Exception as e: print(f"Lỗi xóa file save cũ: {e}")
                return

            data_to_save = self.classic_game_state.copy()
            # Convert pencil_data keys (tuples) to strings for JSON compatibility
            data_to_save['pencil_data'] = {f"{k[0]},{k[1]}": list(v)
                                           for k, v in data_to_save.get('pencil_data', {}).items()}
            # Convert error_cells (set of tuples) to list of lists for JSON
            data_to_save['error_cells'] = [list(cell) for cell in data_to_save.get('error_cells', set())]
            
            with open(SAVE_FILE_PATH, 'w') as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            print(f"Lỗi lưu game: {e}")

    # --- Multiplayer Mode Logic ---
    def ensure_client_connected(self):
        """Ensures the SudokuClient is initialized and connected to the server."""
        if not self.sudoku_client or not self.sudoku_client.is_connected:
            self.sudoku_client = SudokuClient(app_controller=self) # Pass self as app_controller
        
        if not self.sudoku_client.connect():
            messagebox.showerror("Lỗi Kết Nối", "Không thể kết nối tới server Sudoku.", parent=self)
            self.sudoku_client = None # Connection failed
            return False
        return True

    def action_create_multiplayer_game(self):
        """Handles the 'Create Multiplayer Game' action from the UI."""
        if not self.ensure_client_connected():
            return

        diff_mp = "medium" # Default or allow selection
        self.is_multiplayer = True
        self.is_classic_game_active = False # Not in classic mode
        self.stop_any_timers()
        
        self.switch_frame(GameScreenUI, game_mode="multiplayer")
        if isinstance(self.current_frame, GameScreenUI) and self.sudoku_client:
            self.sudoku_client.set_game_ui(self.current_frame) # Link client to GameScreenUI
            self.current_frame.reset_ui_for_new_game()
            self.current_frame.show_message("Chế Độ Mạng", f"Đang tạo phòng chơi (độ khó: {diff_mp})...", "info")
            self.sudoku_client.request_new_multiplayer_game(diff_mp)

    def action_join_multiplayer_game(self):
        """Handles the 'Join Multiplayer Game' action from the UI."""
        if not self.ensure_client_connected():
            return

        dialog = ctk.CTkInputDialog(text="Nhập ID Phòng:", title="Tham Gia Phòng Chơi")
        game_id_to_join = dialog.get_input()

        if game_id_to_join and game_id_to_join.strip():
            self.is_multiplayer = True
            self.is_classic_game_active = False
            self.stop_any_timers()
            
            self.switch_frame(GameScreenUI, game_mode="multiplayer")
            if isinstance(self.current_frame, GameScreenUI) and self.sudoku_client:
                self.sudoku_client.set_game_ui(self.current_frame)
                self.current_frame.reset_ui_for_new_game()
                self.current_frame.show_message("Chế Độ Mạng", f"Đang tham gia phòng '{game_id_to_join}'...", "info")
                self.sudoku_client.request_join_game(game_id_to_join.strip())
        # Else: User cancelled or entered nothing.

    # --- Application Lifecycle ---
    def quit_application(self):
        """Handles application shutdown procedures."""
        self.save_classic_game() # Save any ongoing classic game
        self.stop_any_timers()   # Stop all timers
        
        # Disconnect from multiplayer server if connected
        if self.sudoku_client and self.sudoku_client.is_connected:
            self.sudoku_client.disconnect()
            
        self.destroy() # Close the Tkinter window

# --- Main Execution ---
if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()