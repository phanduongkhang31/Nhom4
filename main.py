# main.py
import customtkinter as ctk
from tkinter import messagebox, StringVar, colorchooser
from ui import MainMenuScreen, GameScreenUI, NewGameDialog, SettingsScreen, StatisticsScreen
from sudoku_logic import SudokuGenerator
from client import SudokuClient
import json
import os
import uuid

SAVE_FILE_PATH = "sudoku_save.json"
SETTINGS_FILE_PATH = "sudoku_settings.json"
USER_STATS_FILE_PATH = "sudoku_user_stats.json"
TIMER_INTERVAL_MS = 1000

# ACHIEVEMENTS constant REMOVED

class SudokuApp(ctk.CTk):
    def __init__(self):
        super().__init__(); self.title("Sudoku Pro Deluxe"); self.minsize(750, 850); self.resizable(True, True)
        # self.ACHIEVEMENTS REMOVED
        self.appearance_setting = "dark"; self.board_colors_config = {}
        self.load_app_settings(); ctk.set_appearance_mode(self.appearance_setting); ctk.set_default_color_theme("blue")
        self.sudoku_generator = SudokuGenerator(); self.current_frame = None; self.sudoku_client = None
        self.is_multiplayer = False; self.classic_game_state = {}; self.is_classic_game_active = False
        self._classic_timer_job = None; self.selected_cell_classic = None; self.undo_stack = []
        self.user_stats = {}; self.just_won_classic_game = False; self.load_user_stats()
        self.load_classic_game(); self.show_main_menu(); self.protocol("WM_DELETE_WINDOW", self.quit_application)

    def _default_user_stats(self):
        # "achievements_unlocked" key REMOVED
        return {"games_won_total": 0, "perfect_wins_total": 0, "current_win_streak": 0, "best_win_streak": 0, "best_times": {d: float('inf') for d in ["very_easy", "easy", "medium", "hard", "expert"]}, "games_won_by_difficulty": {d: 0 for d in ["very_easy", "easy", "medium", "hard", "expert"]}, "perfect_wins_by_difficulty": {d: 0 for d in ["very_easy", "easy", "medium", "hard", "expert"]}}
    def load_user_stats(self):
        # Logic for "achievements_unlocked" REMOVED
        default_stats = self._default_user_stats()
        if os.path.exists(USER_STATS_FILE_PATH):
            try:
                with open(USER_STATS_FILE_PATH, 'r') as f: loaded_stats = json.load(f)
                self.user_stats = default_stats.copy()
                for key, value in loaded_stats.items():
                    if key in self.user_stats and isinstance(self.user_stats[key], dict) and isinstance(value, dict): self.user_stats[key].update(value)
                    elif key in self.user_stats : self.user_stats[key] = value # Only load defined keys
            except Exception as e: print(f"Error loading user stats: {e}. Using defaults."); self.user_stats = default_stats
        else: print("User stats file not found. Initializing."); self.user_stats = default_stats; self.save_user_stats()
    def save_user_stats(self):
        # "achievements_unlocked" will not be saved if not in self.user_stats
        try:
            with open(USER_STATS_FILE_PATH, 'w') as f: json.dump(self.user_stats, f, indent=2)
        except Exception as e: print(f"Error saving user stats: {e}")

    # _unlock_achievement method REMOVED
    # evaluate_all_achievements method REMOVED

    def update_stats_on_win(self, difficulty, time_played, mistakes_made, hints_used_count):
        stats = self.user_stats; stats["games_won_total"] += 1
        stats["games_won_by_difficulty"][difficulty] = stats["games_won_by_difficulty"].get(difficulty, 0) + 1
        is_perfect_win = (mistakes_made == 0 and hints_used_count == 0)
        if is_perfect_win: stats["perfect_wins_total"] += 1; stats["perfect_wins_by_difficulty"][difficulty] = stats["perfect_wins_by_difficulty"].get(difficulty, 0) + 1
        stats["current_win_streak"] += 1; stats["best_win_streak"] = max(stats["best_win_streak"], stats["current_win_streak"])
        if difficulty in stats["best_times"]: stats["best_times"][difficulty] = min(stats["best_times"].get(difficulty, float('inf')), time_played)
        self.just_won_classic_game = True; self.save_user_stats()
        # Call to evaluate_all_achievements REMOVED

    # ... (Rest of SudokuApp class remains the same as the previous "final" version,
    #      but without any achievement-specific logic or references.) ...

    # Ensure methods like input_number and request_hint don't try to call achievement logic.
    # The version from your last "final" request for main.py was already correct in this regard.
    # I'll paste the relevant parts to be sure.

    def get_default_board_colors_for_theme(self):
        from ui import ColorScheme # Local import to avoid circular dependency at module level if classes are split
        temp_scheme = ColorScheme().get_colors(); is_dark = ctk.get_appearance_mode().lower() == "dark"
        return {"cell_default_bg_custom": temp_scheme['cell_default'], "cell_selected_custom": temp_scheme['cell_selected'], "cell_related_custom": temp_scheme['cell_related'], "cell_same_number_custom": temp_scheme['cell_same_number'], "cell_hint_fill_custom": temp_scheme['cell_hint'], "cell_fixed_text_custom": temp_scheme['cell_fixed'][1] if is_dark else temp_scheme['cell_fixed'][0], "cell_user_text_custom": temp_scheme['cell_user'][1] if is_dark else temp_scheme['cell_user'][0], "cell_error_text_custom": temp_scheme['cell_error'][1] if is_dark else temp_scheme['cell_error'][0]}
    def load_app_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE_PATH):
                with open(SETTINGS_FILE_PATH, 'r') as f: settings = json.load(f)
                self.appearance_setting = settings.get("appearance_mode", "dark")
                self.board_colors_config = settings.get("board_colors", {})
            else: self.appearance_setting = "dark"; self.board_colors_config = {}; self.save_app_settings()
        except Exception as e: print(f"Error loading app settings: {e}. Using defaults."); self.appearance_setting = "dark"; self.board_colors_config = {}
    def save_app_settings(self):
        try:
            settings = {"appearance_mode": self.appearance_setting, "board_colors": self.board_colors_config}
            with open(SETTINGS_FILE_PATH, 'w') as f: json.dump(settings, f, indent=2)
        except Exception as e: print(f"Error saving app settings: {e}")
    def get_current_board_colors_config(self): return self.board_colors_config
    def update_board_colors_config(self, new_config):
        self.board_colors_config = new_config.copy(); self.save_app_settings()
        if isinstance(self.current_frame, GameScreenUI) and self.is_classic_game_active and self.classic_game_state.get('board_data'):
            self.current_frame.board_specific_colors = self.current_frame.controller.ui.ColorScheme().get_colors(self.board_colors_config)
            self.current_frame.update_board_display(self.classic_game_state['board_data'],self.classic_game_state['fixed_mask'],self.classic_game_state.get('error_cells'),self.classic_game_state.get('pencil_data'))
        elif isinstance(self.current_frame, SettingsScreen): self.current_frame._populate_board_color_inputs()
    def apply_appearance_mode(self, mode):
        if mode not in ["light", "dark"] or self.appearance_setting == mode:
            if isinstance(self.current_frame, SettingsScreen): self.current_frame._update_theme_button_styles(); self.current_frame._populate_board_color_inputs()
            return
        self.appearance_setting = mode; ctk.set_appearance_mode(self.appearance_setting); self.save_app_settings()
        current_screen_type = type(self.current_frame)
        if current_screen_type:
            args, kwargs = [], {}
            if isinstance(self.current_frame, GameScreenUI): kwargs['game_mode'] = self.current_frame.game_mode
            self.switch_frame(current_screen_type, *args, **kwargs)
    def switch_frame(self, frame_class, *args, **kwargs):
        if self.current_frame: self.stop_any_timers(); self.current_frame.pack_forget(); self.current_frame.destroy()
        self.current_frame = frame_class(self, self, *args, **kwargs); self.current_frame.pack(fill="both", expand=True, padx=5, pady=5)
    def show_main_menu(self):
        if self.is_multiplayer and self.sudoku_client and self.sudoku_client.is_connected: self.sudoku_client.disconnect(); self.sudoku_client = None
        if self.is_classic_game_active and not self.just_won_classic_game: self.user_stats["current_win_streak"] = 0; self.save_user_stats(); print("Win streak reset: abandoned game.")
        self.is_classic_game_active = False; self.is_multiplayer = False; self.stop_any_timers(); self.switch_frame(MainMenuScreen)
        if isinstance(self.current_frame, MainMenuScreen): self.current_frame.update_continue_button_state(self.classic_game_state if self.classic_game_state.get('board_data') else None)
    def show_settings_screen(self): self.is_classic_game_active = False; self.is_multiplayer = False; self.stop_any_timers(); self.switch_frame(SettingsScreen)
    def show_statistics_screen(self): self.is_classic_game_active = False; self.is_multiplayer = False; self.stop_any_timers(); self.switch_frame(StatisticsScreen)
    def show_new_classic_game_dialog(self):
        dialog = NewGameDialog(self, title="Tạo Game Mới"); self.wait_window(dialog)
        if hasattr(dialog, 'ok_pressed') and dialog.ok_pressed and dialog.result: self.start_new_classic_game(dialog.result)
    def start_new_classic_game(self, difficulty):
        if self.is_classic_game_active and not self.just_won_classic_game: self.user_stats["current_win_streak"] = 0; self.save_user_stats()
        self.just_won_classic_game = False; self.is_classic_game_active = True; self.is_multiplayer = False; self.undo_stack = []
        max_m = 3 if difficulty.lower() in ["hard", "expert"] else 5; hints_r = 6
        board, solution = self.sudoku_generator.generate_puzzle(difficulty)
        if not board or not solution: messagebox.showerror("Lỗi", "Không thể tạo bảng Sudoku.", parent=self); return
        fixed_mask = [[(board[r][c] != 0) for c in range(9)] for r in range(9)]
        self.classic_game_state = {'board_data': board, 'solution_data': solution, 'fixed_mask': fixed_mask, 'pencil_data': {}, 'time_played': 0, 'mistakes': 0, 'max_mistakes': max_m, 'difficulty': difficulty, 'score': 0, 'error_cells': set(), 'game_id': str(uuid.uuid4()), 'hints_available': hints_r, 'hints_used_count': 0}
        self.selected_cell_classic = None; self.switch_frame(GameScreenUI, game_mode="classic")
        if isinstance(self.current_frame, GameScreenUI):
            ui = self.current_frame; gs = self.classic_game_state; ui.reset_ui_for_new_game()
            ui.difficulty_ui_text = gs['difficulty']; ui.score_ui = gs.get('score',0); ui.mistakes_count_ui = gs['mistakes']; ui.time_seconds_ui = gs['time_played']; ui.max_mistakes_ui = gs['max_mistakes']
            if hasattr(ui, 'hints_remaining_var'): ui.hints_remaining_var.set(f"💡 Gợi ý ({gs['hints_available']})")
            ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs.get('pencil_data',{})); ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
            self.start_classic_timer(); self.save_classic_game()
    def continue_classic_game(self):
        if not self.classic_game_state.get('board_data'): return
        self.is_classic_game_active = True; self.is_multiplayer = False; gs = self.classic_game_state
        gs.setdefault('max_mistakes', 3 if gs.get('difficulty', 'medium').lower() in ["hard", "expert"] else 5); gs.setdefault('hints_available', 6); gs.setdefault('hints_used_count', 0)
        self.switch_frame(GameScreenUI, game_mode="classic")
        if isinstance(self.current_frame, GameScreenUI):
            ui = self.current_frame; ui.reset_ui_for_new_game()
            ui.difficulty_ui_text = gs['difficulty']; ui.score_ui = gs.get('score',0); ui.mistakes_count_ui = gs['mistakes']; ui.time_seconds_ui = gs['time_played']; ui.max_mistakes_ui = gs['max_mistakes']
            if hasattr(ui, 'hints_remaining_var'): ui.hints_remaining_var.set(f"💡 Gợi ý ({gs['hints_available']})")
            ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs.get('error_cells', set()), gs.get('pencil_data', {})); ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
            self.start_classic_timer()
    def select_cell(self, r, c):
        if not self.is_classic_game_active and not self.is_multiplayer: return
        current_ui = self.current_frame
        if not isinstance(current_ui, GameScreenUI): return
        if self.is_classic_game_active: self.selected_cell_classic = (r, c); related_coords = self.get_related_coords_for_highlight(r, c); current_ui.highlight_selected_cell(r, c, related_coords)
        elif self.is_multiplayer: current_ui.selected_cell_coords = (r,c); current_ui.highlight_selected_cell(r, c, [])
    def input_number(self, num, is_pencil):
        current_ui = self.current_frame
        if not isinstance(current_ui, GameScreenUI): return
        if self.is_classic_game_active:
            if not self.selected_cell_classic: return
            r, c = self.selected_cell_classic; gs = self.classic_game_state
            if gs['fixed_mask'][r][c]: return
            prev_b = [row[:] for row in gs['board_data']]; prev_p = {k: v.copy() for k, v in gs.get('pencil_data', {}).items()}; prev_e = gs.get('error_cells', set()).copy(); prev_m = gs.get('mistakes', 0); prev_s = gs.get('score', 0)
            self.undo_stack.append({'board_data': prev_b, 'pencil_data': prev_p, 'error_cells': prev_e, 'mistakes': prev_m, 'score': prev_s});
            if len(self.undo_stack) > 50: self.undo_stack.pop(0)
            if is_pencil:
                ps = gs['pencil_data'].setdefault((r, c), set());
                if num in ps: ps.remove(num)
                else: ps.add(num)
                if not ps: del gs['pencil_data'][(r,c)]
                if gs['board_data'][r][c] != 0: gs['board_data'][r][c] = 0; gs['error_cells'].discard((r,c))
            else:
                old_n = gs['board_data'][r][c]; gs['board_data'][r][c] = num
                if (r,c) in gs['pencil_data']: del gs['pencil_data'][(r,c)]
                gs['error_cells'].discard((r,c))
                if num != 0:
                    if num != gs['solution_data'][r][c]: gs['error_cells'].add((r,c))
                    if old_n != num and num != gs['solution_data'][r][c]: gs['mistakes'] += 1; gs['score'] = max(0, gs.get('score', 0) - 50)
                    elif num == gs['solution_data'][r][c]:
                        if old_n != 0 and old_n != num: gs['score'] = gs.get('score', 0) + 20
                        elif old_n == 0 : gs['score'] = gs.get('score', 0) + 10
            current_ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs['pencil_data']); current_ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
            if not is_pencil and num != 0 and gs['mistakes'] >= gs.get('max_mistakes', 3) and gs.get('max_mistakes', 3) > 0: current_ui.show_message("Game Over", "Bạn đã mắc quá nhiều lỗi!", "error"); self.stop_any_timers(); self.is_classic_game_active = False; self.user_stats["current_win_streak"] = 0; self.save_user_stats(); self.save_classic_game(); return
            if not is_pencil and self.is_board_complete_and_correct(): self.stop_any_timers(); gs['score'] = gs.get('score', 0) + 1000; self.update_stats_on_win(gs['difficulty'], gs['time_played'], gs['mistakes'], gs.get('hints_used_count', 0)); current_ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes']); current_ui.show_message("Chúc Mừng!", "Bạn đã giải thành công Sudoku!", "info"); self.classic_game_state = {}; self.save_classic_game(); self.show_main_menu(); return
            self.save_classic_game()
        elif self.is_multiplayer and self.sudoku_client and current_ui.selected_cell_coords and not is_pencil: r_mp, c_mp = current_ui.selected_cell_coords; self.sudoku_client.submit_player_move(r_mp, c_mp, num)
        elif self.is_multiplayer and is_pencil: current_ui.show_message("Thông báo", "Viết chì không dùng trong chơi mạng.", "warning")
    def erase_selected(self):
        current_ui = self.current_frame;
        if not isinstance(current_ui, GameScreenUI): return
        if self.is_classic_game_active and self.selected_cell_classic:
            r, c = self.selected_cell_classic; gs = self.classic_game_state
            if gs['fixed_mask'][r][c]: return
            if gs['board_data'][r][c] != 0: self.input_number(0, False); return
            elif (r,c) in gs.get('pencil_data', {}):
                prev_b = [row[:] for row in gs['board_data']]; prev_p = {k: v.copy() for k, v in gs.get('pencil_data', {}).items()}; prev_e = gs.get('error_cells', set()).copy(); prev_m = gs.get('mistakes', 0); prev_s = gs.get('score', 0)
                self.undo_stack.append({'board_data': prev_b, 'pencil_data': prev_p, 'error_cells': prev_e, 'mistakes': prev_m, 'score': prev_s});
                if len(self.undo_stack) > 50: self.undo_stack.pop(0)
                if (r,c) in gs['pencil_data']: del gs['pencil_data'][(r,c)]
                current_ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs['pencil_data']); self.save_classic_game()
        elif self.is_multiplayer and self.sudoku_client and current_ui.selected_cell_coords: r_mp, c_mp = current_ui.selected_cell_coords; self.sudoku_client.submit_player_move(r_mp, c_mp, 0)
    def undo_move(self):
        if not self.undo_stack or not self.is_classic_game_active: return False
        current_ui = self.current_frame;
        if not isinstance(current_ui, GameScreenUI): return False
        prev_state = self.undo_stack.pop(); gs = self.classic_game_state
        gs.update(prev_state)
        current_ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs['pencil_data']); current_ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
        self.save_classic_game(); return True
    def request_hint(self):
        ui = self.current_frame;
        if not isinstance(ui, GameScreenUI): return
        if self.is_classic_game_active:
            if not self.selected_cell_classic : ui.show_message("Gợi ý", "Vui lòng chọn một ô.", "warning"); return
            gs = self.classic_game_state
            if gs.get('hints_available', 0) <= 0: ui.show_message("Gợi ý", "Hết lượt gợi ý!", "warning"); return
            r, c = self.selected_cell_classic
            if gs['fixed_mask'][r][c] or (gs['board_data'][r][c] != 0 and gs['board_data'][r][c] == gs['solution_data'][r][c]): ui.show_message("Gợi ý", "Ô này không cần gợi ý.", "info"); return
            prev_b = [row[:] for row in gs['board_data']]; prev_p = {k: v.copy() for k, v in gs.get('pencil_data', {}).items()}; prev_e = gs.get('error_cells', set()).copy(); prev_m = gs.get('mistakes', 0); prev_s = gs.get('score', 0)
            self.undo_stack.append({'board_data': prev_b, 'pencil_data': prev_p, 'error_cells': prev_e, 'mistakes': prev_m, 'score': prev_s});
            if len(self.undo_stack) > 50: self.undo_stack.pop(0)
            correct_number = gs['solution_data'][r][c]; gs['board_data'][r][c] = correct_number
            if (r,c) in gs['pencil_data']: del gs['pencil_data'][(r,c)]
            gs['error_cells'].discard((r,c)); gs['hints_available'] -= 1; gs['hints_used_count'] = gs.get('hints_used_count', 0) + 1; gs['score'] = max(0, gs.get('score', 0) - 75)
            if hasattr(ui, 'hints_remaining_var'): ui.hints_remaining_var.set(f"💡 Gợi ý ({gs['hints_available']})")
            ui.update_board_display(gs['board_data'], gs['fixed_mask'], gs['error_cells'], gs['pencil_data']); ui.update_cell_display(r, c, correct_number, False, False, None, is_hint_fill=True); ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes'])
            def clear_visual_hint():
                if not self.is_classic_game_active or not gs.get('board_data') or not ui.winfo_exists(): return
                is_err = (r,c) in gs['error_cells']; ui.update_cell_display(r, c, gs['board_data'][r][c], gs['fixed_mask'][r][c], is_err, gs['pencil_data'].get((r,c)), is_hint_fill=False)
                if self.selected_cell_classic == (r,c): rel = self.get_related_coords_for_highlight(r,c); ui.highlight_selected_cell(r,c,rel)
            self.after(1200, clear_visual_hint); self.save_classic_game()
            if self.is_board_complete_and_correct(): self.stop_any_timers(); gs['score'] = gs.get('score', 0) + 1000; self.update_stats_on_win(gs['difficulty'], gs['time_played'], gs['mistakes'], gs.get('hints_used_count', 0)); ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs['score'], gs['max_mistakes']); ui.show_message("Chúc Mừng!", "Bạn đã giải thành công!", "info"); self.classic_game_state = {}; self.save_classic_game(); self.show_main_menu()
        elif self.is_multiplayer: ui.show_message("Gợi ý", "Gợi ý không có trong chơi mạng.", "info")
    def is_board_complete_and_correct(self):
        gs = self.classic_game_state
        if not gs or not gs.get('board_data') or not gs.get('solution_data'): return False
        for r in range(9):
            for c in range(9):
                if gs['board_data'][r][c] == 0 or gs['board_data'][r][c] != gs['solution_data'][r][c]: return False
        return True
    def get_related_coords_for_highlight(self, r, c):
        rel = set();
        for i in range(9): rel.add((r, i)); rel.add((i, c))
        sr, sc = (r // 3) * 3, (c // 3) * 3
        for i in range(3):
            for j in range(3): rel.add((sr + i, sc + j))
        return list(rel)
    def start_classic_timer(self):
        if self._classic_timer_job: self.after_cancel(self._classic_timer_job); self._classic_timer_job = None
        if self.is_classic_game_active and self.classic_game_state.get('board_data'):
            gs = self.classic_game_state; gs['time_played'] += 1
            if isinstance(self.current_frame, GameScreenUI): self.current_frame.time_seconds_ui = gs['time_played']; self.current_frame._update_timer_display()
            self._classic_timer_job = self.after(TIMER_INTERVAL_MS, self.start_classic_timer)
    def stop_any_timers(self):
        if self._classic_timer_job: self.after_cancel(self._classic_timer_job); self._classic_timer_job = None
    def load_classic_game(self):
        try:
            if os.path.exists(SAVE_FILE_PATH):
                with open(SAVE_FILE_PATH, 'r') as f: data = json.load(f)
                if data and data.get('board_data'):
                    pencil_data = {tuple(map(int, k.split(','))): set(v) for k, v in data.get('pencil_data', {}).items()}
                    error_cells = set(map(tuple, data.get('error_cells', [])))
                    self.classic_game_state = {**data, 'pencil_data': pencil_data, 'error_cells': error_cells}
                    self.classic_game_state.setdefault('hints_used_count', 0)
            else: self.classic_game_state = {}
        except Exception as e: print(f"Lỗi tải game: {e}"); self.classic_game_state = {}
    def save_classic_game(self):
        try:
            if not self.classic_game_state or not self.classic_game_state.get('board_data'):
                if os.path.exists(SAVE_FILE_PATH):
                    try: os.remove(SAVE_FILE_PATH)
                    except Exception as e: print(f"Lỗi xóa file save cũ: {e}")
                return
            data_to_save = self.classic_game_state.copy()
            data_to_save['pencil_data'] = {f"{k[0]},{k[1]}": list(v) for k, v in data_to_save.get('pencil_data', {}).items()}
            data_to_save['error_cells'] = [list(cell) for cell in data_to_save.get('error_cells', set())]
            with open(SAVE_FILE_PATH, 'w') as f: json.dump(data_to_save, f, indent=2)
        except Exception as e: print(f"Lỗi lưu game: {e}")
    def ensure_client_connected(self):
        if not self.sudoku_client or not self.sudoku_client.is_connected: self.sudoku_client = SudokuClient(app_controller=self);
        if not self.sudoku_client.connect(): messagebox.showerror("Lỗi Kết Nối", "Không thể kết nối.", parent=self); self.sudoku_client = None; return False
        return True
    def action_create_multiplayer_game(self):
        if not self.ensure_client_connected(): return
        diff_mp = "medium"; self.is_multiplayer = True; self.is_classic_game_active = False; self.stop_any_timers(); self.switch_frame(GameScreenUI, game_mode="multiplayer")
        if isinstance(self.current_frame, GameScreenUI) and self.sudoku_client: self.sudoku_client.set_game_ui(self.current_frame); self.current_frame.reset_ui_for_new_game(); self.current_frame.show_message("Mạng", f"Tạo phòng ({diff_mp})...", "info"); self.sudoku_client.request_new_multiplayer_game(diff_mp)
    def action_join_multiplayer_game(self):
        if not self.ensure_client_connected(): return
        dialog = ctk.CTkInputDialog(text="Nhập ID Phòng:", title="Tham Gia Phòng"); game_id = dialog.get_input()
        if game_id and game_id.strip():
            self.is_multiplayer = True; self.is_classic_game_active = False; self.stop_any_timers(); self.switch_frame(GameScreenUI, game_mode="multiplayer")
            if isinstance(self.current_frame, GameScreenUI) and self.sudoku_client: self.sudoku_client.set_game_ui(self.current_frame); self.current_frame.reset_ui_for_new_game(); self.current_frame.show_message("Mạng", f"Tham gia '{game_id}'...", "info"); self.sudoku_client.request_join_game(game_id.strip())
    def quit_application(self):
        self.save_classic_game(); self.stop_any_timers()
        if self.sudoku_client and self.sudoku_client.is_connected: self.sudoku_client.disconnect()
        self.destroy()

if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()