<<<<<<< HEAD
# main.py
import tkinter as tk
from tkinter import messagebox
import json
import os
from sudoku_logic import SudokuGenerator
# Đảm bảo đã import NewGameDialog từ ui.py
from ui import MainMenuScreen, GameScreenUI, NewGameDialog, COLOR_CELL_SELECTED_BG, COLOR_GRID_BACKGROUND, COLOR_CELL_HINT_FILL

SAVE_FILE_PATH = "sudoku_save.json"
TIMER_INTERVAL_MS = 1000

class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku Game")
        self.geometry("600x800")
        self.configure(bg="#F0F2F5")

        self.sudoku_generator = SudokuGenerator()
        self.current_frame = None

        self.classic_game_state = {}
        self.is_classic_game_active = False
        self._classic_timer_job = None
        self.selected_cell_classic = None

        self.load_classic_game()

        self.sudoku_client = None
        self.is_multiplayer_game_active = False

        self.show_main_menu()
        self.protocol("WM_DELETE_WINDOW", self.quit_application)

    def switch_frame(self, frame_class, *args, **kwargs):
        # print(f"DEBUG APP: switch_frame CALLED for {frame_class.__name__}")
        if self.current_frame:
            # print(f"DEBUG APP: Destroying current frame: {type(self.current_frame).__name__}")
            self.stop_any_active_timers()
            self.current_frame.destroy()
        
        # print(f"DEBUG APP: Creating new frame: {frame_class.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            self.current_frame = frame_class(self, self, *args, **kwargs)
            self.current_frame.pack(fill=tk.BOTH, expand=True)
            # print(f"DEBUG APP: New frame {type(self.current_frame).__name__} packed successfully.")
        except Exception as e:
            print(f"!!!!!!!!!!!!!! ERROR APP: Exception during frame creation or packing for {frame_class.__name__} !!!!!!!!!!!!!!")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi nghiêm trọng", f"Lỗi khi tạo màn hình {frame_class.__name__}:\n{e}", parent=self)
            self.after(100, self.show_main_menu) 


    def show_main_menu(self):
        print("DEBUG APP: show_main_menu CALLED")
        self.is_classic_game_active = False
        self.is_multiplayer_game_active = False
        self.stop_any_active_timers()
        if self.sudoku_client and self.sudoku_client.is_connected:
            # print("DEBUG APP: MainMenu - Disconnecting client.")
            self.sudoku_client.disconnect(); self.sudoku_client = None
        self.switch_frame(MainMenuScreen)
        if isinstance(self.current_frame, MainMenuScreen):
            # print("DEBUG APP: MainMenuScreen instance confirmed. Updating continue button.")
            self.current_frame.update_continue_button_state(
                self.classic_game_state if self.classic_game_state.get('board_data') else None
            )
        else:
            print("CRITICAL ERROR APP: self.current_frame is NOT MainMenuScreen after switch_frame in show_main_menu!")


    def stop_any_active_timers(self):
        if self._classic_timer_job:
            self.after_cancel(self._classic_timer_job); self._classic_timer_job = None
            # print("DEBUG APP: Classic timer job cancelled.")

    def show_new_classic_game_dialog(self):
        print("DEBUG APP: show_new_classic_game_dialog() CALLED")
        dialog = NewGameDialog(self, title="Game Cổ Điển Mới")
        
        # Sau khi dialog.wait_window(self) kết thúc (dialog đã đóng)
        # Kiểm tra dialog.ok_pressed và dialog.result
        if hasattr(dialog, 'ok_pressed') and dialog.ok_pressed and hasattr(dialog, 'result') and dialog.result:
            selected_difficulty_internal = dialog.result # Lấy tên nội bộ từ dialog.result
            print(f"DEBUG APP: Difficulty selected via OK (internal name from dialog.result): {selected_difficulty_internal}")
            self.start_new_classic_game(selected_difficulty_internal)
        else:
            # In ra trạng thái của các thuộc tính nếu không hợp lệ để debug
            ok_pressed_val = getattr(dialog, 'ok_pressed', 'N/A')
            result_val = getattr(dialog, 'result', 'N/A')
            print(f"DEBUG APP: New game dialog was cancelled or closed without valid selection (dialog.ok_pressed: {ok_pressed_val}, dialog.result: {result_val}).")


    def start_new_classic_game(self, difficulty="medium"):
        print(f"DEBUG APP: start_new_classic_game with difficulty: {difficulty}")
        puzzle, solution = self.sudoku_generator.generate_puzzle(difficulty)
        if not puzzle:
            messagebox.showerror("Lỗi", "Không thể tạo bảng Sudoku.", parent=self); # print("DEBUG APP: Puzzle generation FAILED."); 
            return
        # print("DEBUG APP: Puzzle generated successfully.")

        max_mistakes_allowed = 0
        if difficulty.lower() in ["hard", "expert"]: 
            max_mistakes_allowed = 3
        else: 
            max_mistakes_allowed = 10

        self.classic_game_state = {
            'board_data': [row[:] for row in puzzle], 
            'solution_data': solution,
            'fixed_mask': [[(puzzle[r][c] != 0) for c in range(9)] for r in range(9)],
            'difficulty': difficulty, 
            'mistakes': 0, 
            'max_mistakes': max_mistakes_allowed, 
            'time_played': 0, 
            'score': 1500,
            'pencil_data': {}, 
            'history': []
        }
        self.selected_cell_classic = None
        self.is_classic_game_active = True; self.is_multiplayer_game_active = False
        self.save_classic_game()
        self.switch_frame(GameScreenUI, game_mode="classic")
        if isinstance(self.current_frame, GameScreenUI):
            # print("DEBUG APP: GameScreenUI instance confirmed after switch_frame.")
            ui = self.current_frame; gs = self.classic_game_state
            # print("DEBUG APP: Calling ui.reset_ui_for_new_game()")
            ui.reset_ui_for_new_game()
            # print(f"DEBUG APP: Setting UI properties: difficulty={gs['difficulty']}, score={gs.get('score',0)}")
            ui.difficulty_ui_text = gs['difficulty']; ui.score_ui = gs.get('score',0)
            ui.mistakes_count_ui = gs['mistakes']; ui.time_seconds_ui = gs['time_played']
            ui.max_mistakes_ui = gs['max_mistakes'] 
            # print("DEBUG APP: Calling ui.update_board_display()")
            ui.update_board_display(gs['board_data'], gs['fixed_mask'], pencil_data=gs.get('pencil_data', {}))
            # print("DEBUG APP: Calling ui.update_info_display() for initial setup.")
            ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
            # print("DEBUG APP: Calling self.start_classic_timer()")
            self.start_classic_timer()
            # print("DEBUG APP: start_new_classic_game FINISHED processing GameScreenUI setup.")
        else: print("CRITICAL ERROR APP: self.current_frame is NOT GameScreenUI after switch_frame in start_new_classic_game!")


    def continue_classic_game(self):
        # print("DEBUG APP: continue_classic_game CALLED")
        if self.classic_game_state.get('board_data'):
            self.is_classic_game_active = True; self.is_multiplayer_game_active = False
            gs = self.classic_game_state 
            
            if 'max_mistakes' not in gs:
                if gs['difficulty'].lower() in ["hard", "expert"]:
                    gs['max_mistakes'] = 3
                else:
                    gs['max_mistakes'] = 10
                self.save_classic_game() 

            self.switch_frame(GameScreenUI, game_mode="classic")
            if isinstance(self.current_frame, GameScreenUI):
                ui = self.current_frame
                ui.reset_ui_for_new_game()
                ui.difficulty_ui_text = gs['difficulty']; ui.score_ui = gs.get('score',0)
                ui.mistakes_count_ui = gs['mistakes']; ui.time_seconds_ui = gs['time_played']
                ui.max_mistakes_ui = gs['max_mistakes'] 
                ui.update_board_display(gs['board_data'], gs['fixed_mask'],
                    error_cells=self._get_error_cells_classic(), pencil_data=gs.get('pencil_data', {}))
                ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
                self.start_classic_timer()
        else: messagebox.showinfo("Thông báo", "Không có game nào để tiếp tục.", parent=self); # print("DEBUG APP: No game to continue.")

    def start_classic_timer(self):
        self.stop_any_active_timers()
        if self.is_classic_game_active and self.classic_game_state.get('board_data'): 
            gs = self.classic_game_state
            gs['time_played'] += 1
            if gs['time_played'] % 10 == 0 : gs['score'] = max(0, gs.get('score',0) - 1)
            
            if isinstance(self.current_frame, GameScreenUI):
                ui = self.current_frame
                ui.time_seconds_ui = gs['time_played']; ui.mistakes_count_ui = gs['mistakes']
                ui.score_ui = gs.get('score',0); ui.difficulty_ui_text = gs['difficulty']
                ui._update_timer_display() 
            self._classic_timer_job = self.after(TIMER_INTERVAL_MS, self.start_classic_timer)
        elif not self.classic_game_state.get('board_data'): 
            self.stop_any_active_timers()

    def save_classic_game(self):
        if not self.classic_game_state or not self.classic_game_state.get('board_data'):
            if os.path.exists(SAVE_FILE_PATH):
                try: os.remove(SAVE_FILE_PATH); # print("Đã xóa file save.")
                except Exception as e: print(f"Lỗi xóa file save: {e}")
            return
        try:
            with open(SAVE_FILE_PATH, 'w') as f:
                save_state = self.classic_game_state.copy()
                save_state['pencil_data'] = {str(k): list(v) for k, v in save_state.get('pencil_data', {}).items()}
                json.dump(save_state, f, indent=4)
                # print(f"DEBUG APP: Game saved to {SAVE_FILE_PATH}")
        except Exception as e: print(f"Lỗi khi lưu game: {e}")

    def load_classic_game(self):
        self.classic_game_state = {} 
        if os.path.exists(SAVE_FILE_PATH):
            try:
                with open(SAVE_FILE_PATH, 'r') as f:
                    loaded_state = json.load(f)
                    if loaded_state and loaded_state.get('board_data'):
                        loaded_state['pencil_data'] = {eval(k): set(v) for k, v in loaded_state.get('pencil_data', {}).items()}
                        
                        if 'max_mistakes' not in loaded_state:
                            difficulty = loaded_state.get('difficulty', 'medium')
                            if difficulty.lower() in ["hard", "expert"]:
                                loaded_state['max_mistakes'] = 3
                            else:
                                loaded_state['max_mistakes'] = 10
                        
                        self.classic_game_state = loaded_state; # print("Game đã lưu được tải.")
                    # else: print("File save rỗng hoặc không hợp lệ.")
            except Exception as e: print(f"Lỗi khi tải game: {e}")
        # else: print("Không tìm thấy file save.")

    def _add_to_history(self, r, c, old_val_or_set, new_val_or_set, is_pencil_change):
        gs = self.classic_game_state
        gs['history'].append(((r,c), old_val_or_set, new_val_or_set, is_pencil_change))
        if len(gs['history']) > 50: gs['history'].pop(0)

    def undo_move(self):
        # print("DEBUG APP: undo_move CALLED")
        if not self.is_classic_game_active or not self.classic_game_state.get('history'): return
        
        (r,c), old_val_or_set, new_val_or_set, is_pencil_change = self.classic_game_state['history'].pop()
        gs = self.classic_game_state; ui = self.current_frame
        if isinstance(ui, GameScreenUI):
            if is_pencil_change:
                gs['pencil_data'][(r,c)] = old_val_or_set if old_val_or_set else set()
                ui.update_cell_display(r, c, gs['board_data'][r][c], gs['fixed_mask'][r][c], False, gs['pencil_data'].get((r,c)))
            else: 
                gs['board_data'][r][c] = old_val_or_set
                ui.update_board_display(gs['board_data'], gs['fixed_mask'],
                    error_cells=self._get_error_cells_classic(), pencil_data=gs.get('pencil_data', {}))
                ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
            self.select_cell(r,c); self.save_classic_game()

    def _get_error_cells_classic(self):
        errors = set(); gs = self.classic_game_state
        if not gs.get('board_data'): return errors
        for r_idx in range(9):
            for c_idx in range(9):
                if gs['board_data'][r_idx][c_idx] != 0 and not gs['fixed_mask'][r_idx][c_idx] and \
                   gs['board_data'][r_idx][c_idx] != gs['solution_data'][r_idx][c_idx]:
                    errors.add((r_idx, c_idx))
        return errors

    def get_related_coords_for_highlight(self, r, c):
        if not self.classic_game_state.get('board_data') and not self.is_multiplayer_game_active: return []
        coords = set(); size = 9; subgrid_size = 3 
        for i in range(size): coords.add((r, i)); coords.add((i, c))
        sr, sc = r - r % subgrid_size, c - c % subgrid_size 
        for i in range(subgrid_size):
            for j in range(subgrid_size): coords.add((sr + i, sc + j))
        return list(coords)

    def select_cell(self, r, c):
        ui = self.current_frame
        if not isinstance(ui, GameScreenUI): # print("DEBUG APP WARN: select_cell - current_frame not GameScreenUI"); 
            return
        # print(f"DEBUG APP: select_cell({r},{c}) called.")
        if self.is_classic_game_active:
            self.selected_cell_classic = (r, c)
            # print(f"DEBUG APP: self.selected_cell_classic is now ({r},{c})")
            related_coords = self.get_related_coords_for_highlight(r,c)
            # print(f"DEBUG APP: Highlighting cell ({r},{c}) and {len(related_coords)} related cells.")
            ui.highlight_selected_cell(r, c, related_coords)
        elif self.is_multiplayer_game_active:
            ui.selected_cell_coords = (r,c) 
            ui._highlight_selected_cell() 
        # else:
            # print("DEBUG APP WARN: select_cell - No active game mode.")

    def input_number(self, num, is_pencil_mode_on_ui):
        ui = self.current_frame
        if not isinstance(ui, GameScreenUI): # print("DEBUG APP ERROR: input_number - current_ui not GameScreenUI."); 
            return
        # print(f"DEBUG APP: input_number({num}, pencil_mode={is_pencil_mode_on_ui}) called.")

        if self.is_classic_game_active:
            if not self.selected_cell_classic:
                # print("DEBUG APP: input_number - No cell selected for classic mode.")
                ui.show_message("Thông báo", "Vui lòng chọn một ô trước khi nhập số.", "warning"); return
            r, c = self.selected_cell_classic; gs = self.classic_game_state
            # print(f"DEBUG APP: input_number - Selected classic cell: ({r},{c})")
            if gs['fixed_mask'][r][c]:
                # print(f"DEBUG APP: input_number - Cell ({r},{c}) is fixed."); 
                ui.show_message("Thông báo", "Không thể thay đổi ô số cố định.", "warning"); return

            if is_pencil_mode_on_ui:
                # print(f"DEBUG APP: input_number - Pencil mode ON for ({r},{c}), number {num}")
                old_set = gs['pencil_data'].get((r,c), set()).copy(); current_set = gs['pencil_data'].setdefault((r,c), set())
                if num in current_set: current_set.remove(num)
                else: current_set.add(num)
                self._add_to_history(r,c, old_set, current_set.copy(), True)
                if gs['board_data'][r][c] != 0: self._add_to_history(r,c, gs['board_data'][r][c], 0, False); gs['board_data'][r][c] = 0
                # print(f"DEBUG APP: Updating UI for pencil marks at ({r},{c}) with {current_set}")
                ui.update_cell_display(r,c, 0, False, False, current_set)
            else: 
                # print(f"DEBUG APP: input_number - Main number mode for ({r},{c}), number {num}")
                old_val = gs['board_data'][r][c]
                if old_val == num: # print(f"DEBUG APP: input_number - No change for cell ({r},{c})."); 
                    return
                
                self._add_to_history(r,c, old_val, num, False); gs['board_data'][r][c] = num
                # print(f"DEBUG APP: gs['board_data'][{r}][{c}] set to {num}")
                if (r,c) in gs['pencil_data'] and gs['pencil_data'][(r,c)]: self._add_to_history(r,c, gs['pencil_data'][(r,c)].copy(), set(), True); gs['pencil_data'][(r,c)].clear()
                
                is_error = (num != 0 and num != gs['solution_data'][r][c]) 
                # print(f"DEBUG APP: is_error for ({r},{c}) with num {num} is {is_error}")

                if is_error: 
                    if old_val != num: 
                        gs['mistakes'] += 1
                    gs['score'] = max(0, gs.get('score',0) - 50)
                elif not is_error and num != 0: 
                    if old_val != 0 and old_val != gs['solution_data'][r][c]: 
                        gs['score'] = gs.get('score',0) + 20 
                    elif old_val == 0: 
                        gs['score'] = gs.get('score',0) + 10
                
                ui.mistakes_count_ui = gs['mistakes']; ui.score_ui = gs.get('score',0)
                ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
                
                # print(f"DEBUG APP: Updating UI for main number at ({r},{c}) with {num}, error for display: {is_error and num != 0}")
                ui.update_cell_display(r,c, num, False, (is_error and num != 0), None) 
                ui.update_number_pad_counts(gs['board_data'])
                
                complete, correct = self.sudoku_generator.check_board_state(gs['board_data'], gs['solution_data'])
                if complete and correct:
                    self.stop_any_active_timers()
                    gs['score'] = gs.get('score',0) + 1000 
                    ui.show_message("Chúc mừng!", f"Bạn đã thắng!\nLỗi: {gs['mistakes']}/{gs['max_mistakes']}\nThời gian: {gs['time_played']//60:02d}:{gs['time_played']%60:02d}\nĐiểm: {gs.get('score',0):,}")
                    self.classic_game_state = {}; self.save_classic_game(); self.show_main_menu()
                    return 

                if gs['mistakes'] >= gs['max_mistakes']:
                    self.stop_any_active_timers()
                    ui.show_message("Game Over", f"Bạn đã mắc quá nhiều lỗi ({gs['mistakes']}/{gs['max_mistakes']}).\nGame kết thúc.", "error")
                    self.classic_game_state = {}; self.save_classic_game(); self.show_main_menu()
                    return 
            
            self.save_classic_game()
        elif self.is_multiplayer_game_active and self.sudoku_client:
            # print(f"DEBUG APP: input_number - MP mode, selected: {ui.selected_cell_coords}, pencil: {is_pencil_mode_on_ui}")
            if ui.selected_cell_coords and not is_pencil_mode_on_ui:
                r_mp, c_mp = ui.selected_cell_coords
                self.sudoku_client.submit_player_move(r_mp, c_mp, num)
            elif is_pencil_mode_on_ui: ui.show_message("Thông báo", "Viết chì không dùng trong chơi mạng.", "warning")
        # else: print("DEBUG APP WARN: input_number - No active game mode.")


    def erase_selected(self):
        # print("DEBUG APP: erase_selected CALLED")
        ui = self.current_frame
        if not isinstance(ui, GameScreenUI): return
        if self.is_classic_game_active:
            if not self.selected_cell_classic: # print("DEBUG APP: erase_selected - No cell selected."); 
                return
            r, c = self.selected_cell_classic; gs = self.classic_game_state
            if gs['fixed_mask'][r][c]: # print(f"DEBUG APP: erase_selected - Cell ({r},{c}) is fixed."); 
                return
            changed = False
            if gs['board_data'][r][c] != 0: self._add_to_history(r,c, gs['board_data'][r][c], 0, False); gs['board_data'][r][c] = 0; changed = True
            if gs['pencil_data'].get((r,c)): self._add_to_history(r,c, gs['pencil_data'][(r,c)].copy(), set(), True); gs['pencil_data'][(r,c)].clear(); changed = True
            if changed:
                # print(f"DEBUG APP: Erased cell ({r},{c}). Updating UI.")
                ui.update_cell_display(r,c, 0, False, False, set()) 
                ui.update_number_pad_counts(gs['board_data'])
                self.save_classic_game()
        elif self.is_multiplayer_game_active and self.sudoku_client:
            if ui.selected_cell_coords: r_mp, c_mp = ui.selected_cell_coords; self.sudoku_client.submit_player_move(r_mp, c_mp, 0)


    def request_hint(self):
        # print("DEBUG APP: request_hint CALLED")
        ui = self.current_frame
        if not isinstance(ui, GameScreenUI): return
        if self.is_classic_game_active:
            gs = self.classic_game_state
            if int(ui.hints_remaining_var.get()) <= 0: ui.show_message("Gợi ý", "Hết lượt gợi ý.", "warning"); return
            hint = self.sudoku_generator.get_hint(gs['board_data'], gs['solution_data'])
            if hint:
                r_h, c_h, num_h = hint
                # print(f"DEBUG APP: Hint received for ({r_h},{c_h}) -> {num_h}")
                ui.hints_remaining_var.set(str(int(ui.hints_remaining_var.get()) - 1))
                gs['score'] = max(0, gs.get('score',0) - 100) 
                ui.score_ui = gs.get('score',0)
                ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
                
                self.select_cell(r_h,c_h) 
                if ui.is_pencil_mode_on: ui._toggle_pencil_mode() 
                
                self.input_number(num_h, is_pencil_mode_on_ui=False) 

                if (r_h, c_h) in ui.cells_widgets:
                    ui.update_cell_display(r_h,c_h,num_h, False, False, None, is_hint_fill=True)
                    def clear_visual_hint():
                        if not self.is_classic_game_active or not gs.get('board_data'): return 
                        current_val_in_board = gs['board_data'][r_h][c_h]
                        current_is_error = False 
                        current_pencil = gs['pencil_data'].get((r_h,c_h))
                        ui.update_cell_display(r_h,c_h,current_val_in_board, gs['fixed_mask'][r_h][c_h], 
                                               current_is_error, current_pencil, is_hint_fill=False)
                        if self.selected_cell_classic: 
                             scr,scc = self.selected_cell_classic
                             ui.highlight_selected_cell(scr,scc,self.get_related_coords_for_highlight(scr,scc))
                        else: ui._clear_all_highlights()
                    self.after(1200, clear_visual_hint)
            else: ui.show_message("Gợi ý", "Không tìm thấy gợi ý (Bảng đã đúng hoặc không có ô trống dễ gợi ý).", "info")
        elif self.is_multiplayer_game_active: ui.show_message("Gợi ý", "Gợi ý không có trong chơi mạng.", "info")


    def connect_to_multiplayer_server(self):
        # print("DEBUG APP: connect_to_multiplayer_server CALLED")
        from client import SudokuClient 
        if self.sudoku_client and self.sudoku_client.is_connected:
            messagebox.showinfo("Thông báo", "Đã kết nối server.", parent=self); return
        
        self.sudoku_client = SudokuClient(app_controller=self)
        if self.sudoku_client.connect():
            self.is_classic_game_active=False; self.is_multiplayer_game_active=True
            self.stop_any_active_timers() 
            self.switch_frame(GameScreenUI, game_mode="multiplayer")
            if isinstance(self.current_frame, GameScreenUI) and self.sudoku_client:
                self.sudoku_client.set_game_ui(self.current_frame)
                self.current_frame.reset_ui_for_new_game() 
                self.current_frame.difficulty_ui_text = "Multiplayer" 
                self.current_frame.update_info_display(0,0,"Multiplayer",0, max_mistakes=0) 
        else: 
            self.sudoku_client=None; self.is_multiplayer_game_active=False


    def quit_application(self):
        # print("DEBUG APP: quit_application CALLED")
        self.stop_any_active_timers()
        if self.is_classic_game_active and self.classic_game_state.get('board_data'): self.save_classic_game()
        if self.sudoku_client and self.sudoku_client.is_connected: self.sudoku_client.disconnect()
        self.destroy()

if __name__ == "__main__":
    # print("DEBUG APP: Starting SudokuApp...")
    app = SudokuApp()
    app.mainloop()
    # print("DEBUG APP: SudokuApp mainloop finished.")
=======
# main.py
import tkinter as tk
from tkinter import messagebox
import json
import os
from sudoku_logic import SudokuGenerator
from ui import MainMenuScreen, GameScreenUI, NewGameDialog, COLOR_CELL_SELECTED_BG, COLOR_GRID_BACKGROUND, COLOR_CELL_HINT_FILL

SAVE_FILE_PATH = "sudoku_save.json"
TIMER_INTERVAL_MS = 1000

class SudokuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku Game")
        self.geometry("600x800")
        self.configure(bg="#F0F2F5")

        self.sudoku_generator = SudokuGenerator()
        self.current_frame = None

        self.classic_game_state = {}
        self.is_classic_game_active = False
        self._classic_timer_job = None
        self.selected_cell_classic = None

        self.load_classic_game()

        self.sudoku_client = None
        self.is_multiplayer_game_active = False

        self.show_main_menu()
        self.protocol("WM_DELETE_WINDOW", self.quit_application)

    def switch_frame(self, frame_class, *args, **kwargs):
        print(f"DEBUG APP: switch_frame CALLED for {frame_class.__name__}")
        if self.current_frame:
            print(f"DEBUG APP: Destroying current frame: {type(self.current_frame).__name__}")
            self.stop_any_active_timers()
            self.current_frame.destroy()
        
        print(f"DEBUG APP: Creating new frame: {frame_class.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            self.current_frame = frame_class(self, self, *args, **kwargs)
            self.current_frame.pack(fill=tk.BOTH, expand=True)
            print(f"DEBUG APP: New frame {type(self.current_frame).__name__} packed successfully.")
        except Exception as e:
            print(f"!!!!!!!!!!!!!! ERROR APP: Exception during frame creation or packing for {frame_class.__name__} !!!!!!!!!!!!!!")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi nghiêm trọng", f"Lỗi khi tạo màn hình {frame_class.__name__}:\n{e}", parent=self)
            self.after(100, self.show_main_menu) 


    def show_main_menu(self):
        print("DEBUG APP: show_main_menu CALLED")
        self.is_classic_game_active = False
        self.is_multiplayer_game_active = False
        self.stop_any_active_timers()
        if self.sudoku_client and self.sudoku_client.is_connected:
            print("DEBUG APP: MainMenu - Disconnecting client.")
            self.sudoku_client.disconnect(); self.sudoku_client = None
        self.switch_frame(MainMenuScreen)
        if isinstance(self.current_frame, MainMenuScreen):
            print("DEBUG APP: MainMenuScreen instance confirmed. Updating continue button.")
            self.current_frame.update_continue_button_state(
                self.classic_game_state if self.classic_game_state.get('board_data') else None
            )
        else:
            print("CRITICAL ERROR APP: self.current_frame is NOT MainMenuScreen after switch_frame in show_main_menu!")


    def stop_any_active_timers(self):
        if self._classic_timer_job:
            self.after_cancel(self._classic_timer_job); self._classic_timer_job = None
            print("DEBUG APP: Classic timer job cancelled.")

    def show_new_classic_game_dialog(self):
        print("DEBUG APP: show_new_classic_game_dialog() CALLED")
        dialog = NewGameDialog(self, title="Game Cổ Điển Mới")
        
        if hasattr(dialog, 'ok_pressed') and dialog.ok_pressed:
            if hasattr(dialog, 'selected_difficulty') and dialog.selected_difficulty:
                print(f"DEBUG APP: Difficulty selected via OK: {dialog.selected_difficulty}")
                self.start_new_classic_game(dialog.selected_difficulty)
            else:
                print("DEBUG APP: OK pressed but no valid difficulty (dialog.selected_difficulty is None or empty).")
        else:
            print("DEBUG APP: New game dialog was cancelled or closed without OK (dialog.ok_pressed is False).")


    def start_new_classic_game(self, difficulty="medium"):
        print(f"DEBUG APP: start_new_classic_game with difficulty: {difficulty}")
        puzzle, solution = self.sudoku_generator.generate_puzzle(difficulty)
        if not puzzle:
            messagebox.showerror("Lỗi", "Không thể tạo bảng Sudoku.", parent=self); print("DEBUG APP: Puzzle generation FAILED."); return
        print("DEBUG APP: Puzzle generated successfully.")

        max_mistakes_allowed = 0
        if difficulty.lower() in ["hard", "expert"]: # "Khó", "Chuyên gia"
            max_mistakes_allowed = 3
        else: # "very_easy", "easy", "medium"
            max_mistakes_allowed = 10

        self.classic_game_state = {
            'board_data': [row[:] for row in puzzle], 
            'solution_data': solution,
            'fixed_mask': [[(puzzle[r][c] != 0) for c in range(9)] for r in range(9)],
            'difficulty': difficulty, 
            'mistakes': 0, 
            'max_mistakes': max_mistakes_allowed, # ADDED
            'time_played': 0, 
            'score': 1500,
            'pencil_data': {}, 
            'history': []
        }
        self.selected_cell_classic = None
        self.is_classic_game_active = True; self.is_multiplayer_game_active = False
        self.save_classic_game()
        self.switch_frame(GameScreenUI, game_mode="classic")
        if isinstance(self.current_frame, GameScreenUI):
            print("DEBUG APP: GameScreenUI instance confirmed after switch_frame.")
            ui = self.current_frame; gs = self.classic_game_state
            print("DEBUG APP: Calling ui.reset_ui_for_new_game()")
            ui.reset_ui_for_new_game()
            print(f"DEBUG APP: Setting UI properties: difficulty={gs['difficulty']}, score={gs.get('score',0)}")
            ui.difficulty_ui_text = gs['difficulty']; ui.score_ui = gs.get('score',0)
            ui.mistakes_count_ui = gs['mistakes']; ui.time_seconds_ui = gs['time_played']
            # Pass max_mistakes to ui:
            ui.max_mistakes_ui = gs['max_mistakes'] 
            print("DEBUG APP: Calling ui.update_board_display()")
            ui.update_board_display(gs['board_data'], gs['fixed_mask'], pencil_data=gs.get('pencil_data', {}))
            print("DEBUG APP: Calling ui.update_info_display() for initial setup.")
            ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
            print("DEBUG APP: Calling self.start_classic_timer()")
            self.start_classic_timer()
            print("DEBUG APP: start_new_classic_game FINISHED processing GameScreenUI setup.")
        else: print("CRITICAL ERROR APP: self.current_frame is NOT GameScreenUI after switch_frame in start_new_classic_game!")


    def continue_classic_game(self):
        print("DEBUG APP: continue_classic_game CALLED")
        if self.classic_game_state.get('board_data'):
            self.is_classic_game_active = True; self.is_multiplayer_game_active = False
            gs = self.classic_game_state # For convenience
            
            # Ensure max_mistakes is present, e.g., for older save files
            if 'max_mistakes' not in gs:
                if gs['difficulty'].lower() in ["hard", "expert"]:
                    gs['max_mistakes'] = 3
                else:
                    gs['max_mistakes'] = 10
                self.save_classic_game() # Save updated state

            self.switch_frame(GameScreenUI, game_mode="classic")
            if isinstance(self.current_frame, GameScreenUI):
                ui = self.current_frame
                ui.reset_ui_for_new_game()
                ui.difficulty_ui_text = gs['difficulty']; ui.score_ui = gs.get('score',0)
                ui.mistakes_count_ui = gs['mistakes']; ui.time_seconds_ui = gs['time_played']
                ui.max_mistakes_ui = gs['max_mistakes'] # Pass max_mistakes to ui
                ui.update_board_display(gs['board_data'], gs['fixed_mask'],
                    error_cells=self._get_error_cells_classic(), pencil_data=gs.get('pencil_data', {}))
                ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
                self.start_classic_timer()
        else: messagebox.showinfo("Thông báo", "Không có game nào để tiếp tục.", parent=self); print("DEBUG APP: No game to continue.")

    def start_classic_timer(self):
        self.stop_any_active_timers()
        if self.is_classic_game_active and self.classic_game_state.get('board_data'): # Ensure game is active
            gs = self.classic_game_state
            gs['time_played'] += 1
            if gs['time_played'] % 10 == 0 : gs['score'] = max(0, gs.get('score',0) - 1)
            
            if isinstance(self.current_frame, GameScreenUI):
                ui = self.current_frame
                ui.time_seconds_ui = gs['time_played']; ui.mistakes_count_ui = gs['mistakes']
                ui.score_ui = gs.get('score',0); ui.difficulty_ui_text = gs['difficulty']
                # ui.max_mistakes_ui should already be set from game start/load
                # _update_timer_display will use the UI's stored max_mistakes_ui
                ui._update_timer_display() 
            self._classic_timer_job = self.after(TIMER_INTERVAL_MS, self.start_classic_timer)
        elif not self.classic_game_state.get('board_data'): # Game ended, stop timer
            self.stop_any_active_timers()

    def save_classic_game(self):
        if not self.classic_game_state or not self.classic_game_state.get('board_data'):
            if os.path.exists(SAVE_FILE_PATH):
                try: os.remove(SAVE_FILE_PATH); print("Đã xóa file save.")
                except Exception as e: print(f"Lỗi xóa file save: {e}")
            return
        try:
            with open(SAVE_FILE_PATH, 'w') as f:
                save_state = self.classic_game_state.copy()
                save_state['pencil_data'] = {str(k): list(v) for k, v in save_state.get('pencil_data', {}).items()}
                json.dump(save_state, f, indent=4)
                print(f"DEBUG APP: Game saved to {SAVE_FILE_PATH}")
        except Exception as e: print(f"Lỗi khi lưu game: {e}")

    def load_classic_game(self):
        self.classic_game_state = {} 
        if os.path.exists(SAVE_FILE_PATH):
            try:
                with open(SAVE_FILE_PATH, 'r') as f:
                    loaded_state = json.load(f)
                    if loaded_state and loaded_state.get('board_data'):
                        loaded_state['pencil_data'] = {eval(k): set(v) for k, v in loaded_state.get('pencil_data', {}).items()}
                        
                        # Ensure max_mistakes is present for older save files
                        if 'max_mistakes' not in loaded_state:
                            difficulty = loaded_state.get('difficulty', 'medium')
                            if difficulty.lower() in ["hard", "expert"]:
                                loaded_state['max_mistakes'] = 3
                            else:
                                loaded_state['max_mistakes'] = 10
                        
                        self.classic_game_state = loaded_state; print("Game đã lưu được tải.")
                    else: print("File save rỗng hoặc không hợp lệ.")
            except Exception as e: print(f"Lỗi khi tải game: {e}")
        else: print("Không tìm thấy file save.")

    def _add_to_history(self, r, c, old_val_or_set, new_val_or_set, is_pencil_change):
        gs = self.classic_game_state
        gs['history'].append(((r,c), old_val_or_set, new_val_or_set, is_pencil_change))
        if len(gs['history']) > 50: gs['history'].pop(0)

    def undo_move(self):
        print("DEBUG APP: undo_move CALLED")
        if not self.is_classic_game_active or not self.classic_game_state.get('history'): return
        
        (r,c), old_val_or_set, new_val_or_set, is_pencil_change = self.classic_game_state['history'].pop()
        gs = self.classic_game_state; ui = self.current_frame
        if isinstance(ui, GameScreenUI):
            if is_pencil_change:
                gs['pencil_data'][(r,c)] = old_val_or_set if old_val_or_set else set()
                ui.update_cell_display(r, c, gs['board_data'][r][c], gs['fixed_mask'][r][c], False, gs['pencil_data'].get((r,c)))
            else: 
                gs['board_data'][r][c] = old_val_or_set
                # If an error was undone, potentially revert mistake count - complex, simpler to not revert mistake count on undo for now.
                # Or, store mistakes at each history step. For now, let's keep it simple.
                ui.update_board_display(gs['board_data'], gs['fixed_mask'],
                    error_cells=self._get_error_cells_classic(), pencil_data=gs.get('pencil_data', {}))
                ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
            self.select_cell(r,c); self.save_classic_game()

    def _get_error_cells_classic(self):
        errors = set(); gs = self.classic_game_state
        if not gs.get('board_data'): return errors
        for r_idx in range(9):
            for c_idx in range(9):
                if gs['board_data'][r_idx][c_idx] != 0 and not gs['fixed_mask'][r_idx][c_idx] and \
                   gs['board_data'][r_idx][c_idx] != gs['solution_data'][r_idx][c_idx]:
                    errors.add((r_idx, c_idx))
        return errors

    def get_related_coords_for_highlight(self, r, c):
        if not self.classic_game_state.get('board_data') and not self.is_multiplayer_game_active: return []
        coords = set(); size = 9; subgrid_size = 3 
        for i in range(size): coords.add((r, i)); coords.add((i, c))
        sr, sc = r - r % subgrid_size, c - c % subgrid_size 
        for i in range(subgrid_size):
            for j in range(subgrid_size): coords.add((sr + i, sc + j))
        return list(coords)

    def select_cell(self, r, c):
        ui = self.current_frame
        if not isinstance(ui, GameScreenUI): print("DEBUG APP WARN: select_cell - current_frame not GameScreenUI"); return
        print(f"DEBUG APP: select_cell({r},{c}) called.")
        if self.is_classic_game_active:
            self.selected_cell_classic = (r, c)
            print(f"DEBUG APP: self.selected_cell_classic is now ({r},{c})")
            related_coords = self.get_related_coords_for_highlight(r,c)
            print(f"DEBUG APP: Highlighting cell ({r},{c}) and {len(related_coords)} related cells.")
            ui.highlight_selected_cell(r, c, related_coords)
        elif self.is_multiplayer_game_active:
            ui.selected_cell_coords = (r,c) 
            ui._highlight_selected_cell() 
        else:
            print("DEBUG APP WARN: select_cell - No active game mode.")

    def input_number(self, num, is_pencil_mode_on_ui):
        ui = self.current_frame
        if not isinstance(ui, GameScreenUI): print("DEBUG APP ERROR: input_number - current_ui not GameScreenUI."); return
        print(f"DEBUG APP: input_number({num}, pencil_mode={is_pencil_mode_on_ui}) called.")

        if self.is_classic_game_active:
            if not self.selected_cell_classic:
                print("DEBUG APP: input_number - No cell selected for classic mode.")
                ui.show_message("Thông báo", "Vui lòng chọn một ô trước khi nhập số.", "warning"); return
            r, c = self.selected_cell_classic; gs = self.classic_game_state
            print(f"DEBUG APP: input_number - Selected classic cell: ({r},{c})")
            if gs['fixed_mask'][r][c]:
                print(f"DEBUG APP: input_number - Cell ({r},{c}) is fixed."); ui.show_message("Thông báo", "Không thể thay đổi ô số cố định.", "warning"); return

            if is_pencil_mode_on_ui:
                print(f"DEBUG APP: input_number - Pencil mode ON for ({r},{c}), number {num}")
                old_set = gs['pencil_data'].get((r,c), set()).copy(); current_set = gs['pencil_data'].setdefault((r,c), set())
                if num in current_set: current_set.remove(num)
                else: current_set.add(num)
                self._add_to_history(r,c, old_set, current_set.copy(), True)
                if gs['board_data'][r][c] != 0: self._add_to_history(r,c, gs['board_data'][r][c], 0, False); gs['board_data'][r][c] = 0
                print(f"DEBUG APP: Updating UI for pencil marks at ({r},{c}) with {current_set}")
                ui.update_cell_display(r,c, 0, False, False, current_set)
            else: # Main number mode
                print(f"DEBUG APP: input_number - Main number mode for ({r},{c}), number {num}")
                old_val = gs['board_data'][r][c]
                if old_val == num: print(f"DEBUG APP: input_number - No change for cell ({r},{c})."); return
                
                self._add_to_history(r,c, old_val, num, False); gs['board_data'][r][c] = num
                print(f"DEBUG APP: gs['board_data'][{r}][{c}] set to {num}")
                if (r,c) in gs['pencil_data'] and gs['pencil_data'][(r,c)]: self._add_to_history(r,c, gs['pencil_data'][(r,c)].copy(), set(), True); gs['pencil_data'][(r,c)].clear()
                
                is_error = (num != 0 and num != gs['solution_data'][r][c]) # num=0 (erase) is not an error for mistake counting
                print(f"DEBUG APP: is_error for ({r},{c}) with num {num} is {is_error}")

                if is_error: # Check for actual error, not just a different number than before if old_val was also an error
                    if old_val != num: # Count as mistake only if the number actually changed to a new wrong number
                        gs['mistakes'] += 1
                    gs['score'] = max(0, gs.get('score',0) - 50)
                elif not is_error and num != 0: # Correct move
                    if old_val != 0 and old_val != gs['solution_data'][r][c]: # Was an error, now corrected
                        gs['score'] = gs.get('score',0) + 20 
                    elif old_val == 0: # Was empty, now correct
                        gs['score'] = gs.get('score',0) + 10
                
                ui.mistakes_count_ui = gs['mistakes']; ui.score_ui = gs.get('score',0)
                # Update info display, including max_mistakes
                ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
                
                print(f"DEBUG APP: Updating UI for main number at ({r},{c}) with {num}, error for display: {is_error and num != 0}")
                ui.update_cell_display(r,c, num, False, (is_error and num != 0), None) # is_error for coloring
                ui.update_number_pad_counts(gs['board_data'])
                
                # CHECK FOR GAME OVER (WIN OR MISTAKE LIMIT)
                complete, correct = self.sudoku_generator.check_board_state(gs['board_data'], gs['solution_data'])
                if complete and correct:
                    self.stop_any_active_timers()
                    gs['score'] = gs.get('score',0) + 1000 # Win bonus
                    ui.show_message("Chúc mừng!", f"Bạn đã thắng!\nLỗi: {gs['mistakes']}/{gs['max_mistakes']}\nThời gian: {gs['time_played']//60:02d}:{gs['time_played']%60:02d}\nĐiểm: {gs.get('score',0):,}")
                    self.classic_game_state = {}; self.save_classic_game(); self.show_main_menu()
                    return # Important: exit after game over

                if gs['mistakes'] >= gs['max_mistakes']:
                    self.stop_any_active_timers()
                    ui.show_message("Game Over", f"Bạn đã mắc quá nhiều lỗi ({gs['mistakes']}/{gs['max_mistakes']}).\nGame kết thúc.", "error")
                    self.classic_game_state = {}; self.save_classic_game(); self.show_main_menu()
                    return # Important: exit after game over
            
            self.save_classic_game()
        elif self.is_multiplayer_game_active and self.sudoku_client:
            print(f"DEBUG APP: input_number - MP mode, selected: {ui.selected_cell_coords}, pencil: {is_pencil_mode_on_ui}")
            if ui.selected_cell_coords and not is_pencil_mode_on_ui:
                r_mp, c_mp = ui.selected_cell_coords
                self.sudoku_client.submit_player_move(r_mp, c_mp, num)
            elif is_pencil_mode_on_ui: ui.show_message("Thông báo", "Viết chì không dùng trong chơi mạng.", "warning")
        else: print("DEBUG APP WARN: input_number - No active game mode.")


    def erase_selected(self):
        print("DEBUG APP: erase_selected CALLED")
        ui = self.current_frame
        if not isinstance(ui, GameScreenUI): return
        if self.is_classic_game_active:
            if not self.selected_cell_classic: print("DEBUG APP: erase_selected - No cell selected."); return
            r, c = self.selected_cell_classic; gs = self.classic_game_state
            if gs['fixed_mask'][r][c]: print(f"DEBUG APP: erase_selected - Cell ({r},{c}) is fixed."); return
            changed = False
            if gs['board_data'][r][c] != 0: self._add_to_history(r,c, gs['board_data'][r][c], 0, False); gs['board_data'][r][c] = 0; changed = True
            if gs['pencil_data'].get((r,c)): self._add_to_history(r,c, gs['pencil_data'][(r,c)].copy(), set(), True); gs['pencil_data'][(r,c)].clear(); changed = True
            if changed:
                print(f"DEBUG APP: Erased cell ({r},{c}). Updating UI.")
                # Erasing a cell does not count as a mistake or fix one. Color should be neutral.
                ui.update_cell_display(r,c, 0, False, False, set()) 
                ui.update_number_pad_counts(gs['board_data'])
                self.save_classic_game()
        elif self.is_multiplayer_game_active and self.sudoku_client:
            if ui.selected_cell_coords: r_mp, c_mp = ui.selected_cell_coords; self.sudoku_client.submit_player_move(r_mp, c_mp, 0)


    def request_hint(self):
        print("DEBUG APP: request_hint CALLED")
        ui = self.current_frame
        if not isinstance(ui, GameScreenUI): return
        if self.is_classic_game_active:
            gs = self.classic_game_state
            if int(ui.hints_remaining_var.get()) <= 0: ui.show_message("Gợi ý", "Hết lượt gợi ý.", "warning"); return
            hint = self.sudoku_generator.get_hint(gs['board_data'], gs['solution_data'])
            if hint:
                r_h, c_h, num_h = hint
                print(f"DEBUG APP: Hint received for ({r_h},{c_h}) -> {num_h}")
                ui.hints_remaining_var.set(str(int(ui.hints_remaining_var.get()) - 1))
                gs['score'] = max(0, gs.get('score',0) - 100) # Penalty for hint
                ui.score_ui = gs.get('score',0)
                # Update info display with new score and potentially other stats
                ui.update_info_display(gs['mistakes'], gs['time_played'], gs['difficulty'], gs.get('score',0), gs['max_mistakes'])
                
                self.select_cell(r_h,c_h) # Select the cell to be hinted
                if ui.is_pencil_mode_on: ui._toggle_pencil_mode() # Turn off pencil mode for hint input
                
                # Check if the hinted cell was previously an error and adjust mistake count if hint corrects it
                # This logic can be complex. A simpler approach is that a hint *reveals* the correct number,
                # it doesn't count as a mistake, nor does it fix a prior mistake for scoring purposes of mistakes.
                # The `input_number` function handles the board update and history.
                # A hint should not increment the mistake counter.
                
                # Temporarily store current mistakes before input_number potentially changes it
                # mistakes_before_hint = gs['mistakes']

                self.input_number(num_h, is_pencil_mode_on_ui=False) # Input the hinted number

                # After input_number, if it's a hint, ensure mistake count is not penalized for this action
                # if gs['mistakes'] > mistakes_before_hint:
                #     gs['mistakes'] = mistakes_before_hint # Revert mistake if input_number incremented it for the hint
                # The current input_number logic only adds mistakes if `is_error` is true. 
                # Since a hint provides the correct number, `is_error` will be false, so mistakes won't increment.

                if (r_h, c_h) in ui.cells_widgets:
                    ui.update_cell_display(r_h,c_h,num_h, False, False, None, is_hint_fill=True)
                    def clear_visual_hint():
                        if not self.is_classic_game_active or not gs.get('board_data'): return # Game might have ended
                        current_val_in_board = gs['board_data'][r_h][c_h]
                        # A hint always places the correct number, so no error.
                        current_is_error = False 
                        current_pencil = gs['pencil_data'].get((r_h,c_h))
                        ui.update_cell_display(r_h,c_h,current_val_in_board, gs['fixed_mask'][r_h][c_h], 
                                               current_is_error, current_pencil, is_hint_fill=False)
                        if self.selected_cell_classic: 
                             scr,scc = self.selected_cell_classic
                             ui.highlight_selected_cell(scr,scc,self.get_related_coords_for_highlight(scr,scc))
                        else: ui._clear_all_highlights()
                    self.after(1200, clear_visual_hint)
            else: ui.show_message("Gợi ý", "Không tìm thấy gợi ý (Bảng đã đúng hoặc không có ô trống dễ gợi ý).", "info")
        elif self.is_multiplayer_game_active: ui.show_message("Gợi ý", "Gợi ý không có trong chơi mạng.", "info")


    def connect_to_multiplayer_server(self):
        print("DEBUG APP: connect_to_multiplayer_server CALLED")
        from client import SudokuClient # Late import if client.py has Tkinter too
        if self.sudoku_client and self.sudoku_client.is_connected:
            messagebox.showinfo("Thông báo", "Đã kết nối server.", parent=self); return
        
        self.sudoku_client = SudokuClient(app_controller=self)
        if self.sudoku_client.connect():
            self.is_classic_game_active=False; self.is_multiplayer_game_active=True
            self.stop_any_active_timers() # Stop classic timer if any
            self.switch_frame(GameScreenUI, game_mode="multiplayer")
            if isinstance(self.current_frame, GameScreenUI) and self.sudoku_client:
                self.sudoku_client.set_game_ui(self.current_frame)
                self.current_frame.reset_ui_for_new_game() # Resets to default UI state
                self.current_frame.difficulty_ui_text = "Multiplayer" # Set mode text
                # For multiplayer, mistakes/max_mistakes are usually not shown or handled by client this way
                self.current_frame.update_info_display(0,0,"Multiplayer",0, max_mistakes=0) # Or hide max_mistakes
                # self.current_frame.show_message("Chơi mạng", "Kết nối thành công! Chờ tạo hoặc tham gia game.", "info")
                # The server will send 'connected_ack', client handles further UI updates.
        else: 
            self.sudoku_client=None; self.is_multiplayer_game_active=False
            # Error message already shown by client.connect()


    def quit_application(self):
        print("DEBUG APP: quit_application CALLED")
        self.stop_any_active_timers()
        if self.is_classic_game_active and self.classic_game_state.get('board_data'): self.save_classic_game()
        if self.sudoku_client and self.sudoku_client.is_connected: self.sudoku_client.disconnect()
        self.destroy()

if __name__ == "__main__":
    print("DEBUG APP: Starting SudokuApp...")
    app = SudokuApp()
    app.mainloop()
    print("DEBUG APP: SudokuApp mainloop finished.")
>>>>>>> 25ece6d (123)
