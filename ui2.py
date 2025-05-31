<<<<<<< HEAD
# ui.py
import tkinter as tk
from tkinter import messagebox, font, simpledialog

# --- UI Constants ---
# (Keep existing constants)
COLOR_BACKGROUND = "#F0F2F5"
COLOR_BACKGROUND_GAME = "#E8F5E9"
COLOR_PRIMARY_BUTTON = "#007AFF"
COLOR_PRIMARY_BUTTON_TEXT = "white"
COLOR_SECONDARY_BUTTON = "#FFFFFF"
COLOR_SECONDARY_BUTTON_TEXT = "#007AFF"
COLOR_SECONDARY_BUTTON_BORDER = "#007AFF"
COLOR_TEXT_DARK_MM = "#333333"
COLOR_TEXT_LIGHT_MM = "#777777"

FONT_TITLE_MM = ("Arial", 28, "bold")
FONT_SUBTITLE_MM = ("Arial", 18)
FONT_BUTTON_MM = ("Arial", 12, "bold")

COLOR_TEXT_DARK = "#2E7D32"
COLOR_TEXT_LIGHT = "#757575"
COLOR_GRID_BACKGROUND = "white"
COLOR_GRID_LINES = "#A5D6A7"
COLOR_GRID_THICK_LINES = "#66BB6A"
COLOR_CELL_FIXED_TEXT = "#333333"
COLOR_CELL_USER_TEXT = "#1B5E20"
COLOR_CELL_ERROR_TEXT = "#D32F2F"
COLOR_CELL_SELECTED_BG = "#C8E6C9"
COLOR_CELL_HIGHLIGHT_BG = "#DCEDC8"
COLOR_CELL_HINT_FILL = "#66BB6A" 
COLOR_PENCIL_MARK_TEXT = "#757575"

FONT_GAME_INFO_LARGE = ("Arial", 16, "bold")
FONT_GAME_INFO_SMALL = ("Arial", 10)
FONT_BUTTON_ACTION = ("Arial", 10)
FONT_CELL_NUMBER = ("Arial", 20, "bold")
FONT_PENCIL_MARK = ("Arial", 7)
FONT_NUMBER_PAD = ("Arial", 22, "bold")
FONT_NUMBER_PAD_COUNT = ("Arial", 9)


class BaseScreen(tk.Frame):
    def __init__(self, master_app, controller):
        super().__init__(master_app)
        self.master_app = master_app
        self.controller = controller


class MainMenuScreen(BaseScreen):
    def __init__(self, master_app, controller):
        super().__init__(master_app, controller)
        self.configure(bg=COLOR_BACKGROUND)
        print("DEBUG UI: MainMenuScreen __init__ CALLED")

        tk.Label(self, text="Cổ điển Sudoku", font=FONT_TITLE_MM, bg=COLOR_BACKGROUND, fg=COLOR_TEXT_DARK_MM).pack(pady=(60, 10))
        tk.Label(self, text="Chọn một tùy chọn:", font=FONT_SUBTITLE_MM, bg=COLOR_BACKGROUND, fg=COLOR_TEXT_LIGHT_MM).pack(pady=(0, 30))

        self.continue_button_text_var = tk.StringVar()
        self.continue_button = tk.Button(self, textvariable=self.continue_button_text_var,
                                    command=self.controller.continue_classic_game,
                                    font=FONT_BUTTON_MM, relief=tk.FLAT,
                                    width=25, height=3, compound=tk.CENTER, justify=tk.CENTER)
        self.continue_button.pack(pady=10)
        
        new_game_button = tk.Button(self, text="Trò chơi mới (Cổ điển)",
                                     command=self.controller.show_new_classic_game_dialog,
                                     bg=COLOR_SECONDARY_BUTTON, fg=COLOR_SECONDARY_BUTTON_TEXT,
                                     font=FONT_BUTTON_MM, relief=tk.SOLID,
                                     borderwidth=2, width=25, height=2,
                                     highlightbackground=COLOR_SECONDARY_BUTTON_BORDER, highlightthickness=2)
        new_game_button.pack(pady=10)

        multiplayer_button = tk.Button(self, text="Chơi mạng (Kết nối Server)",
                                     command=self.controller.connect_to_multiplayer_server,
                                     bg=COLOR_PRIMARY_BUTTON, fg=COLOR_PRIMARY_BUTTON_TEXT,
                                     font=FONT_BUTTON_MM, relief=tk.FLAT, width=25, height=2)
        multiplayer_button.pack(pady=10)

        quit_button = tk.Button(self, text="Thoát Game",
                                command=self.master_app.quit_application,
                                bg="#FF3B30", fg="white", font=FONT_BUTTON_MM, relief=tk.FLAT, width=15)
        quit_button.pack(side=tk.BOTTOM, pady=20)
        print("DEBUG UI: MainMenuScreen widgets CREATED.")


    def update_continue_button_state(self, game_data):
        print(f"DEBUG UI: MainMenuScreen update_continue_button_state CALLED with game_data: {bool(game_data and game_data.get('board_data'))}")
        if game_data and game_data.get('board_data'):
            time_played = game_data.get('time_played', 0)
            difficulty = game_data.get('difficulty', "N/A")
            mistakes = game_data.get('mistakes', 0)
            max_mistakes = game_data.get('max_mistakes', 0) # Get max mistakes
            minutes = time_played // 60
            seconds = time_played % 60
            
            mistake_text = f"{mistakes}/{max_mistakes}" if max_mistakes > 0 else f"{mistakes}"
            self.continue_button_text_var.set(f"Tiếp tục ({difficulty.capitalize()})\n{minutes:02d}:{seconds:02d} - Lỗi: {mistake_text}")
            self.continue_button.config(state=tk.NORMAL, bg=COLOR_PRIMARY_BUTTON, fg=COLOR_PRIMARY_BUTTON_TEXT)
        else:
            self.continue_button_text_var.set("Tiếp tục\n(Không có game)")
            self.continue_button.config(state=tk.DISABLED, bg="#AAAAAA", fg="#555555")


class NewGameDialog(simpledialog.Dialog):
    def __init__(self, parent, title="Trò chơi mới"):
        print("DEBUG UI: NewGameDialog __init__ CALLED")
        self.selected_difficulty = "medium" 
        self.ok_pressed = False
        self.difficulties_map = { # Key: Display name, Value: internal name
            "Rất Dễ": "very_easy", 
            "Dễ": "easy", 
            "Bình thường": "medium",
            "Khó": "hard", 
            "Chuyên gia": "expert" 
        }
        self.dialog_font = ("Arial", 11)
        super().__init__(parent, title)

    def body(self, master):
        print("DEBUG UI: NewGameDialog body() CALLED")
        tk.Label(master, text="Chọn độ khó:", font=self.dialog_font).pack(pady=(10,5))
        self.difficulty_var = tk.StringVar(master)
        # Find the display name for the default "medium" internal name
        default_display = next((k for k, v in self.difficulties_map.items() if v == "medium"), "Bình thường")
        self.difficulty_var.set(default_display) 
        
        first_rb = None
        for display_name, internal_name in self.difficulties_map.items():
            rb = tk.Radiobutton(master, text=display_name, variable=self.difficulty_var,
                                value=display_name, # Store display name in var
                                font=self.dialog_font, anchor="w")
            rb.pack(fill=tk.X, padx=20, pady=2)
            if first_rb is None: first_rb = rb
        return first_rb 

    def buttonbox(self):
        print("DEBUG UI: NewGameDialog buttonbox() CALLED")
        box = tk.Frame(self)
        tk.Button(box, text="OK", width=10, command=self.ok_pressed_action, default=tk.ACTIVE).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text="Hủy", width=10, command=self.cancel_action).pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", lambda event: self.ok_pressed_action())
        self.bind("<Escape>", lambda event: self.cancel_action())
        box.pack(pady=5)

    def ok_pressed_action(self):
        print("DEBUG UI: NewGameDialog OK pressed")
        if not self.validate(): return # simpledialog's validate, usually returns True
        self.ok_pressed = True
        self.withdraw(); self.update_idletasks() # Hide dialog
        self.apply() # Process data
        super().ok() # Calls destroy, sets self.result

    def cancel_action(self):
        print("DEBUG UI: NewGameDialog Cancel pressed")
        self.ok_pressed = False # Ensure ok_pressed is false
        super().cancel() # Calls destroy, sets self.result to None

    def apply(self): # Called by self.ok() if ok_pressed_action leads to super().ok()
        print("DEBUG UI: NewGameDialog apply() CALLED, ok_pressed:", self.ok_pressed)
        if self.ok_pressed:
            display_name = self.difficulty_var.get()
            self.selected_difficulty = self.difficulties_map.get(display_name, "medium") # Get internal name
            print(f"DEBUG UI: apply() - Selected difficulty (internal): {self.selected_difficulty}")
            # self.result = self.selected_difficulty # simpledialog.Dialog.ok() sets self.result from apply's return
        # else:
            # self.selected_difficulty = None # Handled by self.result being None if cancel is pressed
        # return self.selected_difficulty # This would be set as self.result by simpledialog.Dialog.ok()
                                        # but we set self.selected_difficulty directly for clarity and access
                                        # The controller will check self.ok_pressed and self.selected_difficulty


class GameScreenUI(BaseScreen):
    def __init__(self, master_app, controller, game_mode="classic"):
        print(f"DEBUG UI: GameScreenUI __init__ CALLED. Mode: {game_mode}")
        try:
            super().__init__(master_app, controller)
            self.configure(bg=COLOR_BACKGROUND_GAME)
            self.game_mode = game_mode; self.grid_size = 9; self.subgrid_size = 3
            self.cells_widgets = {}; self.num_labels = {}; self.pencil_labels = {}
            self.selected_cell_coords = None; self.is_pencil_mode_on = False
            
            self.mistakes_count_ui = 0
            self.max_mistakes_ui = 0 # ADDED for UI display
            self.time_seconds_ui = 0
            self.score_ui = 0
            self.difficulty_ui_text = "N/A"
            
            self.number_counts_vars = {i: tk.StringVar(value="9") for i in range(1, 10)}
            self.hints_remaining_var = tk.StringVar(value="6") # Default for classic
            self._timer_ui_job = None 
            print("DEBUG UI: GameScreenUI __init__ - properties initialized. Calling _create_widgets().")
            self._create_widgets()
            print("DEBUG UI: GameScreenUI __init__ - _create_widgets() FINISHED.")
        except Exception as e:
            print(f"!!!!!!!!!!!!!! ERROR UI: Exception in GameScreenUI __init__ !!!!!!!!!!!!!!")
            import traceback
            traceback.print_exc()

    def _create_widgets(self):
        print("DEBUG UI: GameScreenUI _create_widgets CALLED.")
        try:
            # Top Bar (Back Button)
            top_bar = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); top_bar.pack(fill=tk.X, pady=5, padx=10)
            tk.Button(top_bar, text="← Quay lại", font=("Arial", 12), command=self.controller.show_main_menu,
                      bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_DARK, relief=tk.FLAT, activebackground="#B9DAB9").pack(side=tk.LEFT, padx=(0,15))
            
            # Info Area (Score, Mistakes/Difficulty, Time)
            info_area = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); info_area.pack(fill=tk.X, pady=5, padx=20)
            info_area.columnconfigure(0, weight=1); info_area.columnconfigure(1, weight=1); info_area.columnconfigure(2, weight=1)

            score_frame = tk.Frame(info_area, bg=COLOR_BACKGROUND_GAME); score_frame.grid(row=0, column=0, sticky="nws")
            tk.Label(score_frame, text="Điểm số:", font=FONT_GAME_INFO_SMALL, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_LIGHT).pack(anchor="w")
            self.score_label = tk.Label(score_frame, text="0", font=FONT_GAME_INFO_LARGE, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_DARK); self.score_label.pack(anchor="w")

            center_info_frame = tk.Frame(info_area, bg=COLOR_BACKGROUND_GAME); center_info_frame.grid(row=0, column=1, sticky="n")
            self.mistakes_label = tk.Label(center_info_frame, text="Lỗi: 0/0", font=FONT_GAME_INFO_SMALL, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_LIGHT); self.mistakes_label.pack()
            self.difficulty_label = tk.Label(center_info_frame, text="N/A", font=FONT_GAME_INFO_LARGE, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_DARK); self.difficulty_label.pack() # Larger font for difficulty

            time_frame = tk.Frame(info_area, bg=COLOR_BACKGROUND_GAME); time_frame.grid(row=0, column=2, sticky="nes")
            tk.Label(time_frame, text="Thời gian:", font=FONT_GAME_INFO_SMALL, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_LIGHT).pack(anchor="e")
            self.time_label = tk.Label(time_frame, text="00:00", font=FONT_GAME_INFO_LARGE, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_DARK); self.time_label.pack(anchor="e") # Larger font for time
            
            # Grid Container
            grid_container = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); grid_container.pack(pady=15)
            self.grid_frame_widget = tk.Frame(grid_container, bg=COLOR_GRID_THICK_LINES, bd=1); self.grid_frame_widget.pack() # bd for outer border
            
            cell_pixel_size = 42 # Adjusted for better fit with lines
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    # This simplified cell creation relies on Frame padding for lines
                    # For more precise lines, a Canvas would be better.
                    padx_val, pady_val = (1,1)
                    if (c + 1) % self.subgrid_size == 0 and c < self.grid_size - 1: padx_val = (1,2) # Thicker line on right
                    if (r + 1) % self.subgrid_size == 0 and r < self.grid_size - 1: pady_val = (1,2) # Thicker line on bottom

                    cell_frame_container = tk.Frame(self.grid_frame_widget, bg=COLOR_GRID_LINES) # This frame's bg acts as thin line
                    cell_frame_container.grid(row=r, column=c, padx=0, pady=0) # No space between line containers

                    cell_inner_frame = tk.Frame(cell_frame_container, bg=COLOR_GRID_BACKGROUND, 
                                                width=cell_pixel_size, height=cell_pixel_size)
                    cell_inner_frame.pack_propagate(False)
                    cell_inner_frame.pack(padx=padx_val, pady=pady_val) # Padding inside container shows container's bg as line

                    cell_inner_frame.bind("<Button-1>", lambda e, r_bind=r, c_bind=c: self._on_cell_click(r_bind, c_bind))
                    self.cells_widgets[(r,c)] = cell_inner_frame # Store the inner frame for bg changes

                    pencil_lbl = tk.Label(cell_inner_frame, text="", font=FONT_PENCIL_MARK, bg=COLOR_GRID_BACKGROUND, fg=COLOR_PENCIL_MARK_TEXT, justify=tk.CENTER, anchor="center")
                    pencil_lbl.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)
                    pencil_lbl.bind("<Button-1>", lambda e, r_bind=r, c_bind=c: self._on_cell_click(r_bind, c_bind))
                    self.pencil_labels[(r,c)] = pencil_lbl

                    num_lbl = tk.Label(cell_inner_frame, text="", font=FONT_CELL_NUMBER, bg=COLOR_GRID_BACKGROUND)
                    num_lbl.place(relx=0.5, rely=0.5, anchor="center")
                    num_lbl.bind("<Button-1>", lambda e, r_bind=r, c_bind=c: self._on_cell_click(r_bind, c_bind))
                    self.num_labels[(r,c)] = num_lbl
            
            # Action Buttons Row
            action_buttons_row = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); action_buttons_row.pack(pady=10)
            # Config: (Display Text, Icon (optional), command, mode_availability ('classic', 'multiplayer', 'both'))
            actions_config = [
                ("Hoàn tác", "↺", self.controller.undo_move, "classic"), 
                ("Xóa", "⌫", self._erase_selected_cell, "both"),
                ("Viết chì", "✏️", self._toggle_pencil_mode, "classic"), # Pencil only for classic
                ("Gợi ý", "💡", self.controller.request_hint, "classic") # Hint only for classic
            ]
            self.action_buttons_map = {}

            for text, icon_char, cmd, mode_avail in actions_config:
                if mode_avail == "both" or \
                   (mode_avail == "classic" and self.game_mode == "classic") or \
                   (mode_avail == "multiplayer" and self.game_mode == "multiplayer"):
                    
                    btn_frame = tk.Frame(action_buttons_row, bg=COLOR_BACKGROUND_GAME); btn_frame.pack(side=tk.LEFT, padx=8, pady=5)
                    
                    actual_text = f"{icon_char} {text}" if icon_char else text
                    font_size = 12 if len(icon_char) > 1 else 16 # Smaller font for emoji/longer icons

                    # Combined button for icon and text
                    btn = tk.Button(btn_frame, text=actual_text, font=("Arial", font_size), 
                                    command=cmd, bg="#FFFFFF", fg=COLOR_TEXT_DARK, 
                                    relief=tk.SOLID, borderwidth=1, padx=8, pady=4,
                                    activebackground="#E0E0E0")
                    btn.pack()

                    if text == "Viết chì": 
                        self.action_buttons_map["pencil_mode_button"] = btn 
            
            # Number Pad Container
            number_pad_container = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); number_pad_container.pack(pady=(5,15))
            for i in range(1, 10):
                num_btn_frame = tk.Frame(number_pad_container, bg=COLOR_SECONDARY_BUTTON, borderwidth=1, relief=tk.RAISED, cursor="hand2"); num_btn_frame.pack(side=tk.LEFT, padx=3, ipady=3, ipadx=5)
                num_btn_frame.bind("<Button-1>", lambda e, num=i: self._on_number_press(num))
                
                lbl_num = tk.Label(num_btn_frame, text=str(i), font=FONT_NUMBER_PAD, bg=COLOR_SECONDARY_BUTTON, fg=COLOR_TEXT_DARK); lbl_num.pack()
                lbl_num.bind("<Button-1>", lambda e, num=i: self._on_number_press(num))
                
                lbl_count = tk.Label(num_btn_frame, textvariable=self.number_counts_vars[i], font=FONT_NUMBER_PAD_COUNT, bg=COLOR_SECONDARY_BUTTON, fg=COLOR_TEXT_LIGHT); lbl_count.pack(pady=(0,1))
                lbl_count.bind("<Button-1>", lambda e, num=i: self._on_number_press(num))

            # Multiplayer specific controls (placeholder, shown conditionally)
            if self.game_mode == "multiplayer":
                mp_controls_frame = tk.Frame(self, bg=COLOR_BACKGROUND_GAME)
                mp_controls_frame.pack(pady=5)
                
                tk.Button(mp_controls_frame, text="Tạo Game Mới (MP)", 
                          command=lambda: self.controller.sudoku_client.request_new_multiplayer_game() if self.controller.sudoku_client else None,
                          font=FONT_BUTTON_MM, bg=COLOR_PRIMARY_BUTTON, fg=COLOR_PRIMARY_BUTTON_TEXT, relief=tk.FLAT
                          ).pack(side=tk.LEFT, padx=5)
                
                self.join_game_id_var = tk.StringVar()
                tk.Entry(mp_controls_frame, textvariable=self.join_game_id_var, width=10, font=FONT_GAME_INFO_SMALL).pack(side=tk.LEFT, padx=5)
                tk.Button(mp_controls_frame, text="Tham gia Game (MP)", 
                          command=lambda: self.controller.sudoku_client.request_join_game(self.join_game_id_var.get()) if self.controller.sudoku_client and self.join_game_id_var.get() else None,
                           font=FONT_BUTTON_MM, bg=COLOR_PRIMARY_BUTTON, fg=COLOR_PRIMARY_BUTTON_TEXT, relief=tk.FLAT
                          ).pack(side=tk.LEFT, padx=5)


            print("DEBUG UI: GameScreenUI _create_widgets - All widgets created and packed.")
        except Exception as e:
            print(f"!!!!!!!!!!!!!! ERROR UI: Exception in GameScreenUI _create_widgets !!!!!!!!!!!!!!")
            import traceback
            traceback.print_exc()

    def _on_cell_click(self, r, c): 
        print(f"DEBUG UI: Cell ({r},{c}) clicked.")
        self.selected_cell_coords = (r,c) # Store selected coords for UI internal use too
        self.controller.select_cell(r, c) # Call controller to handle game logic selection

    def _on_number_press(self, num): 
        print(f"DEBUG UI: Number {num} pressed. Pencil mode: {self.is_pencil_mode_on}")
        self.controller.input_number(num, self.is_pencil_mode_on)
    
    def _erase_selected_cell(self): 
        self.controller.erase_selected()
    
    def _toggle_pencil_mode(self):
        if self.game_mode != "classic": # Pencil mode only for classic
            self.show_message("Thông báo", "Viết chì chỉ dùng cho game cổ điển.", "info")
            return

        self.is_pencil_mode_on = not self.is_pencil_mode_on
        pencil_button = self.action_buttons_map.get("pencil_mode_button")
        if pencil_button:
            icon = "✏️"
            if self.is_pencil_mode_on:
                pencil_button.config(text=f"{icon} Viết chì (ON)", relief=tk.SUNKEN, bg="#D0E0D0")
            else:
                pencil_button.config(text=f"{icon} Viết chì (OFF)", relief=tk.RAISED, bg="#FFFFFF")
    
    def highlight_selected_cell(self, r_selected, c_selected, related_coords=None):
        self._clear_all_highlights()
        related_coords = related_coords or [] # Ensure it's a list

        current_board_values = {}
        if self.game_mode == "classic" and self.controller.classic_game_state.get('board_data'):
            board = self.controller.classic_game_state['board_data']
            for r_idx in range(self.grid_size):
                for c_idx in range(self.grid_size):
                    if board[r_idx][c_idx] != 0:
                        current_board_values[(r_idx, c_idx)] = board[r_idx][c_idx]
        elif self.game_mode == "multiplayer" and self.controller.sudoku_client and self.controller.sudoku_client.server_board_state:
            board = self.controller.sudoku_client.server_board_state
            for r_idx in range(self.grid_size):
                for c_idx in range(self.grid_size):
                    if board[r_idx][c_idx] != 0:
                        current_board_values[(r_idx, c_idx)] = board[r_idx][c_idx]
        
        selected_val = current_board_values.get((r_selected, c_selected))

        for r_idx in range(self.grid_size):
            for c_idx in range(self.grid_size):
                cell_frame = self.cells_widgets.get((r_idx, c_idx))
                num_lbl = self.num_labels.get((r_idx,c_idx))
                pencil_lbl = self.pencil_labels.get((r_idx,c_idx))
                if not cell_frame: continue

                bg_color = COLOR_GRID_BACKGROUND # Default
                if (r_idx,c_idx) == (r_selected,c_selected):
                    bg_color = COLOR_CELL_SELECTED_BG
                elif (r_idx,c_idx) in related_coords:
                    bg_color = COLOR_CELL_HIGHLIGHT_BG
                
                # Highlight same numbers
                if selected_val and selected_val != 0 and current_board_values.get((r_idx,c_idx)) == selected_val:
                     bg_color = COLOR_CELL_HIGHLIGHT_BG if bg_color == COLOR_GRID_BACKGROUND else bg_color # Keep selected color if it is

                cell_frame.config(bg=bg_color)
                if num_lbl: num_lbl.config(bg=bg_color)
                if pencil_lbl: pencil_lbl.config(bg=bg_color)

    def _highlight_selected_cell(self): # For multiplayer, uses internal selected_cell_coords
        if self.selected_cell_coords:
            r, c = self.selected_cell_coords
            related = []
            if self.controller.sudoku_client and self.controller.sudoku_client.server_board_state: # Basic highlight for MP
                for i in range(self.grid_size): related.append((r, i)); related.append((i, c))
                sr, sc = r - r % self.subgrid_size, c - c % self.subgrid_size 
                for i in range(self.subgrid_size):
                    for j in range(self.subgrid_size): related.append((sr + i, sc + j))
            self.highlight_selected_cell(r,c, related)


    def _clear_all_highlights(self):
        for r_idx in range(self.grid_size):
            for c_idx in range(self.grid_size):
                cell_frame = self.cells_widgets.get((r_idx, c_idx))
                num_lbl = self.num_labels.get((r_idx,c_idx))
                pencil_lbl = self.pencil_labels.get((r_idx,c_idx))
                
                if cell_frame: cell_frame.config(bg=COLOR_GRID_BACKGROUND)
                if num_lbl: num_lbl.config(bg=COLOR_GRID_BACKGROUND)
                if pencil_lbl: pencil_lbl.config(bg=COLOR_GRID_BACKGROUND)
    
    def update_cell_display(self, r, c, number, is_fixed, is_error=False, pencil_marks_set=None, is_hint_fill=False):
        num_lbl = self.num_labels.get((r,c))
        pencil_lbl = self.pencil_labels.get((r,c))
        cell_frame = self.cells_widgets.get((r,c)) # This is the inner_frame

        if not (num_lbl and pencil_lbl and cell_frame): 
            print(f"WARN UI: Widget not found for cell ({r},{c}) during update_cell_display"); return

        current_bg_of_cell = cell_frame.cget("bg") # Get current bg (might be highlighted)
        fg_color = COLOR_CELL_USER_TEXT # Default for user numbers

        if is_hint_fill: # Hint fill overrides other colors temporarily
            # The actual bg change for hint_fill should be managed by highlight logic if desired
            # Here, we just set text color. The actual cell bg is set by highlight_selected_cell
            # Forcing hint fill bg here can be problematic with selection highlights.
            # Let's assume hint_fill primarily affects text color and the cell itself is selected.
            fg_color = "white" # Text color on hint_fill
            # If you want to force cell_frame bg: cell_frame.config(bg=COLOR_CELL_HINT_FILL)
            # but this will be overridden by selection logic.
            # A better way for hint fill is for highlight_selected_cell to know about it.
            # For now, update_cell_display makes the number prominent on the existing bg.
            if current_bg_of_cell != COLOR_CELL_SELECTED_BG: # if cell not selected, make it hint color
                 cell_frame.config(bg=COLOR_CELL_HINT_FILL)
                 num_lbl.config(bg=COLOR_CELL_HINT_FILL)
                 pencil_lbl.config(bg=COLOR_CELL_HINT_FILL)

        elif is_fixed: 
            fg_color = COLOR_CELL_FIXED_TEXT
        elif is_error: 
            fg_color = COLOR_CELL_ERROR_TEXT
        
        num_lbl.config(fg=fg_color)
        # pencil_lbl.config(bg=current_bg_of_cell) # Pencil label uses cell's background

        if number != 0:
            num_lbl.config(text=str(number))
            pencil_lbl.config(text="") # Clear pencil marks
        else: # Number is 0, display pencil marks if any
            num_lbl.config(text="")
            if pencil_marks_set and len(pencil_marks_set) > 0:
                # Create a 3x3 grid string for pencil marks
                lines = []
                for i in range(1, 10, 3): # 1, 4, 7
                    line_str = ""
                    for j in range(3): # 0, 1, 2 for offset
                        mark = i + j
                        line_str += str(mark) if mark in pencil_marks_set else " "
                        if j < 2: line_str += " " # Space between numbers in a row
                    lines.append(line_str.strip())
                pencil_lbl.config(text="\n".join(lines))
            else:
                pencil_lbl.config(text="")

    def update_board_display(self, board_data, fixed_mask, error_cells=None, pencil_data=None):
        print("DEBUG UI: update_board_display CALLED")
        error_cells = error_cells or set()
        pencil_data = pencil_data or {}
        
        for r_idx in range(self.grid_size):
            for c_idx in range(self.grid_size):
                is_err = (r_idx,c_idx) in error_cells if board_data[r_idx][c_idx] != 0 else False
                self.update_cell_display(r_idx, c_idx, board_data[r_idx][c_idx], 
                                         fixed_mask[r_idx][c_idx],
                                         is_error=is_err,
                                         pencil_marks_set=pencil_data.get((r_idx,c_idx), set()))
        self.update_number_pad_counts(board_data)
        
        # Re-apply selection highlight after board update
        if self.selected_cell_coords:
            sr,sc = self.selected_cell_coords
            # Determine related_coords based on game mode
            related = []
            if self.game_mode == "classic":
                related = self.controller.get_related_coords_for_highlight(sr,sc)
            elif self.game_mode == "multiplayer": # Basic related for MP
                 for i in range(self.grid_size): related.append((sr, i)); related.append((i, sr))
                 s_r, s_c = sr - sr % self.subgrid_size, sc - sc % self.subgrid_size 
                 for i in range(self.subgrid_size):
                    for j in range(self.subgrid_size): related.append((s_r + i, s_c + j))
            self.highlight_selected_cell(sr,sc,related)
        else:
            self._clear_all_highlights()
        print("DEBUG UI: update_board_display FINISHED")
    
    def update_number_pad_counts(self, board_data):
        counts = {i:0 for i in range(1,10)}
        for r_row in board_data:
            for num_val_cell in r_row:
                if 1 <= num_val_cell <= 9: 
                    counts[num_val_cell] += 1
        
        for num_key, count_var in self.number_counts_vars.items():
            remaining = self.grid_size - counts.get(num_key,0)
            count_var.set(str(remaining if remaining > 0 else "✓")) # Show checkmark if all placed
            # Optionally, disable number pad button if remaining is 0 (NYI)

    def show_message(self, title, message, message_type="info"):
        # Ensure messages are shown on top of the main app window
        # parent=self.master_app is good
        if message_type=="error": messagebox.showerror(title, message, parent=self.master_app)
        elif message_type=="warning": messagebox.showwarning(title, message, parent=self.master_app)
        else: messagebox.showinfo(title, message, parent=self.master_app)

    def update_info_display(self, mistakes, time_seconds, difficulty_text=None, score=None, max_mistakes=None):
        self.mistakes_count_ui = mistakes
        self.time_seconds_ui = time_seconds
        if difficulty_text: self.difficulty_ui_text = difficulty_text
        if score is not None: self.score_ui = score
        if max_mistakes is not None: self.max_mistakes_ui = max_mistakes

        if self.game_mode == "classic" and self.max_mistakes_ui > 0:
            self.mistakes_label.config(text=f"Lỗi: {self.mistakes_count_ui}/{self.max_mistakes_ui}")
        elif self.game_mode == "multiplayer": # In MP, just show "Lỗi: -" or similar if not tracked by client
            self.mistakes_label.config(text="Chơi mạng") # Or hide mistakes label for MP
        else: # Default or unknown
            self.mistakes_label.config(text=f"Lỗi: {self.mistakes_count_ui}")
        
        self.difficulty_label.config(text=str(self.difficulty_ui_text).capitalize())
        minutes = self.time_seconds_ui // 60
        seconds = self.time_seconds_ui % 60
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        self.score_label.config(text=f"{self.score_ui:,}")

    def start_timer_display(self): # Called by controller if needed
        self._update_timer_display()

    def _update_timer_display(self): # Internal periodic update
        # This method uses the UI's stored values
        self.update_info_display(self.mistakes_count_ui, self.time_seconds_ui, 
                                 self.difficulty_ui_text, self.score_ui, self.max_mistakes_ui)

    def stop_timer_display(self): # Called by controller if needed
        pass # Timer job is managed by controller

    def reset_ui_for_new_game(self):
        print("DEBUG UI: reset_ui_for_new_game CALLED")
        self.selected_cell_coords = None
        self.is_pencil_mode_on = False
        
        pencil_button = self.action_buttons_map.get("pencil_mode_button")
        if pencil_button:
            pencil_button.config(text="✏️ Viết chì (OFF)", relief=tk.RAISED, bg="#FFFFFF")
        
        self._clear_all_highlights()
        
        # Reset UI state variables
        self.mistakes_count_ui = 0
        self.time_seconds_ui = 0
        self.score_ui = 0 # Default score, controller will set actual if needed
        self.max_mistakes_ui = 0 # Reset, controller will set for classic
        self.difficulty_ui_text = "N/A" # Controller will set
        
        if self.game_mode == "classic":
            self.hints_remaining_var.set("6") # Reset hints for classic
        else: # Multiplayer
            self.hints_remaining_var.set("0") # No hints in MP by default

        for i in range(1,10): self.number_counts_vars[i].set("9") # Reset number pad counts

        # Call update_info_display with reset values.
        # The controller (main.py) will call update_info_display again with actual game data
        # after this reset, so this provides a clean slate.
        self.update_info_display(self.mistakes_count_ui, self.time_seconds_ui, 
                                 self.difficulty_ui_text, self.score_ui, self.max_mistakes_ui)
        
        # Clear board display (set all to 0, no fixed, no errors, no pencil)
        empty_board = [[0 for _ in range(9)] for _ in range(9)]
        empty_mask = [[False for _ in range(9)] for _ in range(9)]
        self.update_board_display(empty_board, empty_mask, {}, {})

=======
# ui.py
import tkinter as tk
from tkinter import messagebox, font, simpledialog

# --- UI Constants ---
# (Keep existing constants)
COLOR_BACKGROUND = "#F0F2F5"
COLOR_BACKGROUND_GAME = "#E8F5E9"
COLOR_PRIMARY_BUTTON = "#007AFF"
COLOR_PRIMARY_BUTTON_TEXT = "white"
COLOR_SECONDARY_BUTTON = "#FFFFFF"
COLOR_SECONDARY_BUTTON_TEXT = "#007AFF"
COLOR_SECONDARY_BUTTON_BORDER = "#007AFF"
COLOR_TEXT_DARK_MM = "#333333"
COLOR_TEXT_LIGHT_MM = "#777777"

FONT_TITLE_MM = ("Arial", 28, "bold")
FONT_SUBTITLE_MM = ("Arial", 18)
FONT_BUTTON_MM = ("Arial", 12, "bold")

COLOR_TEXT_DARK = "#2E7D32"
COLOR_TEXT_LIGHT = "#757575"
COLOR_GRID_BACKGROUND = "white"
COLOR_GRID_LINES = "#A5D6A7"
COLOR_GRID_THICK_LINES = "#66BB6A"
COLOR_CELL_FIXED_TEXT = "#333333"
COLOR_CELL_USER_TEXT = "#1B5E20"
COLOR_CELL_ERROR_TEXT = "#D32F2F"
COLOR_CELL_SELECTED_BG = "#C8E6C9"
COLOR_CELL_HIGHLIGHT_BG = "#DCEDC8"
COLOR_CELL_HINT_FILL = "#66BB6A" 
COLOR_PENCIL_MARK_TEXT = "#757575"

FONT_GAME_INFO_LARGE = ("Arial", 16, "bold")
FONT_GAME_INFO_SMALL = ("Arial", 10)
FONT_BUTTON_ACTION = ("Arial", 10)
FONT_CELL_NUMBER = ("Arial", 20, "bold")
FONT_PENCIL_MARK = ("Arial", 7)
FONT_NUMBER_PAD = ("Arial", 22, "bold")
FONT_NUMBER_PAD_COUNT = ("Arial", 9)


class BaseScreen(tk.Frame):
    def __init__(self, master_app, controller):
        super().__init__(master_app)
        self.master_app = master_app
        self.controller = controller


class MainMenuScreen(BaseScreen):
    def __init__(self, master_app, controller):
        super().__init__(master_app, controller)
        self.configure(bg=COLOR_BACKGROUND)
        print("DEBUG UI: MainMenuScreen __init__ CALLED")

        tk.Label(self, text="Cổ điển Sudoku", font=FONT_TITLE_MM, bg=COLOR_BACKGROUND, fg=COLOR_TEXT_DARK_MM).pack(pady=(60, 10))
        tk.Label(self, text="Chọn một tùy chọn:", font=FONT_SUBTITLE_MM, bg=COLOR_BACKGROUND, fg=COLOR_TEXT_LIGHT_MM).pack(pady=(0, 30))

        self.continue_button_text_var = tk.StringVar()
        self.continue_button = tk.Button(self, textvariable=self.continue_button_text_var,
                                    command=self.controller.continue_classic_game,
                                    font=FONT_BUTTON_MM, relief=tk.FLAT,
                                    width=25, height=3, compound=tk.CENTER, justify=tk.CENTER)
        self.continue_button.pack(pady=10)
        
        new_game_button = tk.Button(self, text="Trò chơi mới (Cổ điển)",
                                     command=self.controller.show_new_classic_game_dialog,
                                     bg=COLOR_SECONDARY_BUTTON, fg=COLOR_SECONDARY_BUTTON_TEXT,
                                     font=FONT_BUTTON_MM, relief=tk.SOLID,
                                     borderwidth=2, width=25, height=2,
                                     highlightbackground=COLOR_SECONDARY_BUTTON_BORDER, highlightthickness=2)
        new_game_button.pack(pady=10)

        multiplayer_button = tk.Button(self, text="Chơi mạng (Kết nối Server)",
                                     command=self.controller.connect_to_multiplayer_server,
                                     bg=COLOR_PRIMARY_BUTTON, fg=COLOR_PRIMARY_BUTTON_TEXT,
                                     font=FONT_BUTTON_MM, relief=tk.FLAT, width=25, height=2)
        multiplayer_button.pack(pady=10)

        quit_button = tk.Button(self, text="Thoát Game",
                                command=self.master_app.quit_application,
                                bg="#FF3B30", fg="white", font=FONT_BUTTON_MM, relief=tk.FLAT, width=15)
        quit_button.pack(side=tk.BOTTOM, pady=20)
        print("DEBUG UI: MainMenuScreen widgets CREATED.")


    def update_continue_button_state(self, game_data):
        print(f"DEBUG UI: MainMenuScreen update_continue_button_state CALLED with game_data: {bool(game_data and game_data.get('board_data'))}")
        if game_data and game_data.get('board_data'):
            time_played = game_data.get('time_played', 0)
            difficulty = game_data.get('difficulty', "N/A")
            mistakes = game_data.get('mistakes', 0)
            max_mistakes = game_data.get('max_mistakes', 0) # Get max mistakes
            minutes = time_played // 60
            seconds = time_played % 60
            
            mistake_text = f"{mistakes}/{max_mistakes}" if max_mistakes > 0 else f"{mistakes}"
            self.continue_button_text_var.set(f"Tiếp tục ({difficulty.capitalize()})\n{minutes:02d}:{seconds:02d} - Lỗi: {mistake_text}")
            self.continue_button.config(state=tk.NORMAL, bg=COLOR_PRIMARY_BUTTON, fg=COLOR_PRIMARY_BUTTON_TEXT)
        else:
            self.continue_button_text_var.set("Tiếp tục\n(Không có game)")
            self.continue_button.config(state=tk.DISABLED, bg="#AAAAAA", fg="#555555")


class NewGameDialog(simpledialog.Dialog):
    def __init__(self, parent, title="Trò chơi mới"):
        print("DEBUG UI: NewGameDialog __init__ CALLED")
        self.selected_difficulty = "medium" 
        self.ok_pressed = False
        self.difficulties_map = { # Key: Display name, Value: internal name
            "Rất Dễ": "very_easy", 
            "Dễ": "easy", 
            "Bình thường": "medium",
            "Khó": "hard", 
            "Chuyên gia": "expert" 
        }
        self.dialog_font = ("Arial", 11)
        super().__init__(parent, title)

    def body(self, master):
        print("DEBUG UI: NewGameDialog body() CALLED")
        tk.Label(master, text="Chọn độ khó:", font=self.dialog_font).pack(pady=(10,5))
        self.difficulty_var = tk.StringVar(master)
        # Find the display name for the default "medium" internal name
        default_display = next((k for k, v in self.difficulties_map.items() if v == "medium"), "Bình thường")
        self.difficulty_var.set(default_display) 
        
        first_rb = None
        for display_name, internal_name in self.difficulties_map.items():
            rb = tk.Radiobutton(master, text=display_name, variable=self.difficulty_var,
                                value=display_name, # Store display name in var
                                font=self.dialog_font, anchor="w")
            rb.pack(fill=tk.X, padx=20, pady=2)
            if first_rb is None: first_rb = rb
        return first_rb 

    def buttonbox(self):
        print("DEBUG UI: NewGameDialog buttonbox() CALLED")
        box = tk.Frame(self)
        tk.Button(box, text="OK", width=10, command=self.ok_pressed_action, default=tk.ACTIVE).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text="Hủy", width=10, command=self.cancel_action).pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", lambda event: self.ok_pressed_action())
        self.bind("<Escape>", lambda event: self.cancel_action())
        box.pack(pady=5)

    def ok_pressed_action(self):
        print("DEBUG UI: NewGameDialog OK pressed")
        if not self.validate(): return # simpledialog's validate, usually returns True
        self.ok_pressed = True
        self.withdraw(); self.update_idletasks() # Hide dialog
        self.apply() # Process data
        super().ok() # Calls destroy, sets self.result

    def cancel_action(self):
        print("DEBUG UI: NewGameDialog Cancel pressed")
        self.ok_pressed = False # Ensure ok_pressed is false
        super().cancel() # Calls destroy, sets self.result to None

    def apply(self): # Called by self.ok() if ok_pressed_action leads to super().ok()
        print("DEBUG UI: NewGameDialog apply() CALLED, ok_pressed:", self.ok_pressed)
        if self.ok_pressed:
            display_name = self.difficulty_var.get()
            self.selected_difficulty = self.difficulties_map.get(display_name, "medium") # Get internal name
            print(f"DEBUG UI: apply() - Selected difficulty (internal): {self.selected_difficulty}")
            # self.result = self.selected_difficulty # simpledialog.Dialog.ok() sets self.result from apply's return
        # else:
            # self.selected_difficulty = None # Handled by self.result being None if cancel is pressed
        # return self.selected_difficulty # This would be set as self.result by simpledialog.Dialog.ok()
                                        # but we set self.selected_difficulty directly for clarity and access
                                        # The controller will check self.ok_pressed and self.selected_difficulty


class GameScreenUI(BaseScreen):
    def __init__(self, master_app, controller, game_mode="classic"):
        print(f"DEBUG UI: GameScreenUI __init__ CALLED. Mode: {game_mode}")
        try:
            super().__init__(master_app, controller)
            self.configure(bg=COLOR_BACKGROUND_GAME)
            self.game_mode = game_mode; self.grid_size = 9; self.subgrid_size = 3
            self.cells_widgets = {}; self.num_labels = {}; self.pencil_labels = {}
            self.selected_cell_coords = None; self.is_pencil_mode_on = False
            
            self.mistakes_count_ui = 0
            self.max_mistakes_ui = 0 # ADDED for UI display
            self.time_seconds_ui = 0
            self.score_ui = 0
            self.difficulty_ui_text = "N/A"
            
            self.number_counts_vars = {i: tk.StringVar(value="9") for i in range(1, 10)}
            self.hints_remaining_var = tk.StringVar(value="6") # Default for classic
            self._timer_ui_job = None 
            print("DEBUG UI: GameScreenUI __init__ - properties initialized. Calling _create_widgets().")
            self._create_widgets()
            print("DEBUG UI: GameScreenUI __init__ - _create_widgets() FINISHED.")
        except Exception as e:
            print(f"!!!!!!!!!!!!!! ERROR UI: Exception in GameScreenUI __init__ !!!!!!!!!!!!!!")
            import traceback
            traceback.print_exc()

    def _create_widgets(self):
        print("DEBUG UI: GameScreenUI _create_widgets CALLED.")
        try:
            # Top Bar (Back Button)
            top_bar = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); top_bar.pack(fill=tk.X, pady=5, padx=10)
            tk.Button(top_bar, text="← Quay lại", font=("Arial", 12), command=self.controller.show_main_menu,
                      bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_DARK, relief=tk.FLAT, activebackground="#B9DAB9").pack(side=tk.LEFT, padx=(0,15))
            
            # Info Area (Score, Mistakes/Difficulty, Time)
            info_area = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); info_area.pack(fill=tk.X, pady=5, padx=20)
            info_area.columnconfigure(0, weight=1); info_area.columnconfigure(1, weight=1); info_area.columnconfigure(2, weight=1)

            score_frame = tk.Frame(info_area, bg=COLOR_BACKGROUND_GAME); score_frame.grid(row=0, column=0, sticky="nws")
            tk.Label(score_frame, text="Điểm số:", font=FONT_GAME_INFO_SMALL, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_LIGHT).pack(anchor="w")
            self.score_label = tk.Label(score_frame, text="0", font=FONT_GAME_INFO_LARGE, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_DARK); self.score_label.pack(anchor="w")

            center_info_frame = tk.Frame(info_area, bg=COLOR_BACKGROUND_GAME); center_info_frame.grid(row=0, column=1, sticky="n")
            self.mistakes_label = tk.Label(center_info_frame, text="Lỗi: 0/0", font=FONT_GAME_INFO_SMALL, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_LIGHT); self.mistakes_label.pack()
            self.difficulty_label = tk.Label(center_info_frame, text="N/A", font=FONT_GAME_INFO_LARGE, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_DARK); self.difficulty_label.pack() # Larger font for difficulty

            time_frame = tk.Frame(info_area, bg=COLOR_BACKGROUND_GAME); time_frame.grid(row=0, column=2, sticky="nes")
            tk.Label(time_frame, text="Thời gian:", font=FONT_GAME_INFO_SMALL, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_LIGHT).pack(anchor="e")
            self.time_label = tk.Label(time_frame, text="00:00", font=FONT_GAME_INFO_LARGE, bg=COLOR_BACKGROUND_GAME, fg=COLOR_TEXT_DARK); self.time_label.pack(anchor="e") # Larger font for time
            
            # Grid Container
            grid_container = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); grid_container.pack(pady=15)
            self.grid_frame_widget = tk.Frame(grid_container, bg=COLOR_GRID_THICK_LINES, bd=1); self.grid_frame_widget.pack() # bd for outer border
            
            cell_pixel_size = 42 # Adjusted for better fit with lines
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    # This simplified cell creation relies on Frame padding for lines
                    # For more precise lines, a Canvas would be better.
                    padx_val, pady_val = (1,1)
                    if (c + 1) % self.subgrid_size == 0 and c < self.grid_size - 1: padx_val = (1,2) # Thicker line on right
                    if (r + 1) % self.subgrid_size == 0 and r < self.grid_size - 1: pady_val = (1,2) # Thicker line on bottom

                    cell_frame_container = tk.Frame(self.grid_frame_widget, bg=COLOR_GRID_LINES) # This frame's bg acts as thin line
                    cell_frame_container.grid(row=r, column=c, padx=0, pady=0) # No space between line containers

                    cell_inner_frame = tk.Frame(cell_frame_container, bg=COLOR_GRID_BACKGROUND, 
                                                width=cell_pixel_size, height=cell_pixel_size)
                    cell_inner_frame.pack_propagate(False)
                    cell_inner_frame.pack(padx=padx_val, pady=pady_val) # Padding inside container shows container's bg as line

                    cell_inner_frame.bind("<Button-1>", lambda e, r_bind=r, c_bind=c: self._on_cell_click(r_bind, c_bind))
                    self.cells_widgets[(r,c)] = cell_inner_frame # Store the inner frame for bg changes

                    pencil_lbl = tk.Label(cell_inner_frame, text="", font=FONT_PENCIL_MARK, bg=COLOR_GRID_BACKGROUND, fg=COLOR_PENCIL_MARK_TEXT, justify=tk.CENTER, anchor="center")
                    pencil_lbl.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)
                    pencil_lbl.bind("<Button-1>", lambda e, r_bind=r, c_bind=c: self._on_cell_click(r_bind, c_bind))
                    self.pencil_labels[(r,c)] = pencil_lbl

                    num_lbl = tk.Label(cell_inner_frame, text="", font=FONT_CELL_NUMBER, bg=COLOR_GRID_BACKGROUND)
                    num_lbl.place(relx=0.5, rely=0.5, anchor="center")
                    num_lbl.bind("<Button-1>", lambda e, r_bind=r, c_bind=c: self._on_cell_click(r_bind, c_bind))
                    self.num_labels[(r,c)] = num_lbl
            
            # Action Buttons Row
            action_buttons_row = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); action_buttons_row.pack(pady=10)
            # Config: (Display Text, Icon (optional), command, mode_availability ('classic', 'multiplayer', 'both'))
            actions_config = [
                ("Hoàn tác", "↺", self.controller.undo_move, "classic"), 
                ("Xóa", "⌫", self._erase_selected_cell, "both"),
                ("Viết chì", "✏️", self._toggle_pencil_mode, "classic"), # Pencil only for classic
                ("Gợi ý", "💡", self.controller.request_hint, "classic") # Hint only for classic
            ]
            self.action_buttons_map = {}

            for text, icon_char, cmd, mode_avail in actions_config:
                if mode_avail == "both" or \
                   (mode_avail == "classic" and self.game_mode == "classic") or \
                   (mode_avail == "multiplayer" and self.game_mode == "multiplayer"):
                    
                    btn_frame = tk.Frame(action_buttons_row, bg=COLOR_BACKGROUND_GAME); btn_frame.pack(side=tk.LEFT, padx=8, pady=5)
                    
                    actual_text = f"{icon_char} {text}" if icon_char else text
                    font_size = 12 if len(icon_char) > 1 else 16 # Smaller font for emoji/longer icons

                    # Combined button for icon and text
                    btn = tk.Button(btn_frame, text=actual_text, font=("Arial", font_size), 
                                    command=cmd, bg="#FFFFFF", fg=COLOR_TEXT_DARK, 
                                    relief=tk.SOLID, borderwidth=1, padx=8, pady=4,
                                    activebackground="#E0E0E0")
                    btn.pack()

                    if text == "Viết chì": 
                        self.action_buttons_map["pencil_mode_button"] = btn 
            
            # Number Pad Container
            number_pad_container = tk.Frame(self, bg=COLOR_BACKGROUND_GAME); number_pad_container.pack(pady=(5,15))
            for i in range(1, 10):
                num_btn_frame = tk.Frame(number_pad_container, bg=COLOR_SECONDARY_BUTTON, borderwidth=1, relief=tk.RAISED, cursor="hand2"); num_btn_frame.pack(side=tk.LEFT, padx=3, ipady=3, ipadx=5)
                num_btn_frame.bind("<Button-1>", lambda e, num=i: self._on_number_press(num))
                
                lbl_num = tk.Label(num_btn_frame, text=str(i), font=FONT_NUMBER_PAD, bg=COLOR_SECONDARY_BUTTON, fg=COLOR_TEXT_DARK); lbl_num.pack()
                lbl_num.bind("<Button-1>", lambda e, num=i: self._on_number_press(num))
                
                lbl_count = tk.Label(num_btn_frame, textvariable=self.number_counts_vars[i], font=FONT_NUMBER_PAD_COUNT, bg=COLOR_SECONDARY_BUTTON, fg=COLOR_TEXT_LIGHT); lbl_count.pack(pady=(0,1))
                lbl_count.bind("<Button-1>", lambda e, num=i: self._on_number_press(num))

            # Multiplayer specific controls (placeholder, shown conditionally)
            if self.game_mode == "multiplayer":
                mp_controls_frame = tk.Frame(self, bg=COLOR_BACKGROUND_GAME)
                mp_controls_frame.pack(pady=5)
                
                tk.Button(mp_controls_frame, text="Tạo Game Mới (MP)", 
                          command=lambda: self.controller.sudoku_client.request_new_multiplayer_game() if self.controller.sudoku_client else None,
                          font=FONT_BUTTON_MM, bg=COLOR_PRIMARY_BUTTON, fg=COLOR_PRIMARY_BUTTON_TEXT, relief=tk.FLAT
                          ).pack(side=tk.LEFT, padx=5)
                
                self.join_game_id_var = tk.StringVar()
                tk.Entry(mp_controls_frame, textvariable=self.join_game_id_var, width=10, font=FONT_GAME_INFO_SMALL).pack(side=tk.LEFT, padx=5)
                tk.Button(mp_controls_frame, text="Tham gia Game (MP)", 
                          command=lambda: self.controller.sudoku_client.request_join_game(self.join_game_id_var.get()) if self.controller.sudoku_client and self.join_game_id_var.get() else None,
                           font=FONT_BUTTON_MM, bg=COLOR_PRIMARY_BUTTON, fg=COLOR_PRIMARY_BUTTON_TEXT, relief=tk.FLAT
                          ).pack(side=tk.LEFT, padx=5)


            print("DEBUG UI: GameScreenUI _create_widgets - All widgets created and packed.")
        except Exception as e:
            print(f"!!!!!!!!!!!!!! ERROR UI: Exception in GameScreenUI _create_widgets !!!!!!!!!!!!!!")
            import traceback
            traceback.print_exc()

    def _on_cell_click(self, r, c): 
        print(f"DEBUG UI: Cell ({r},{c}) clicked.")
        self.selected_cell_coords = (r,c) # Store selected coords for UI internal use too
        self.controller.select_cell(r, c) # Call controller to handle game logic selection

    def _on_number_press(self, num): 
        print(f"DEBUG UI: Number {num} pressed. Pencil mode: {self.is_pencil_mode_on}")
        self.controller.input_number(num, self.is_pencil_mode_on)
    
    def _erase_selected_cell(self): 
        self.controller.erase_selected()
    
    def _toggle_pencil_mode(self):
        if self.game_mode != "classic": # Pencil mode only for classic
            self.show_message("Thông báo", "Viết chì chỉ dùng cho game cổ điển.", "info")
            return

        self.is_pencil_mode_on = not self.is_pencil_mode_on
        pencil_button = self.action_buttons_map.get("pencil_mode_button")
        if pencil_button:
            icon = "✏️"
            if self.is_pencil_mode_on:
                pencil_button.config(text=f"{icon} Viết chì (ON)", relief=tk.SUNKEN, bg="#D0E0D0")
            else:
                pencil_button.config(text=f"{icon} Viết chì (OFF)", relief=tk.RAISED, bg="#FFFFFF")
    
    def highlight_selected_cell(self, r_selected, c_selected, related_coords=None):
        self._clear_all_highlights()
        related_coords = related_coords or [] # Ensure it's a list

        current_board_values = {}
        if self.game_mode == "classic" and self.controller.classic_game_state.get('board_data'):
            board = self.controller.classic_game_state['board_data']
            for r_idx in range(self.grid_size):
                for c_idx in range(self.grid_size):
                    if board[r_idx][c_idx] != 0:
                        current_board_values[(r_idx, c_idx)] = board[r_idx][c_idx]
        elif self.game_mode == "multiplayer" and self.controller.sudoku_client and self.controller.sudoku_client.server_board_state:
            board = self.controller.sudoku_client.server_board_state
            for r_idx in range(self.grid_size):
                for c_idx in range(self.grid_size):
                    if board[r_idx][c_idx] != 0:
                        current_board_values[(r_idx, c_idx)] = board[r_idx][c_idx]
        
        selected_val = current_board_values.get((r_selected, c_selected))

        for r_idx in range(self.grid_size):
            for c_idx in range(self.grid_size):
                cell_frame = self.cells_widgets.get((r_idx, c_idx))
                num_lbl = self.num_labels.get((r_idx,c_idx))
                pencil_lbl = self.pencil_labels.get((r_idx,c_idx))
                if not cell_frame: continue

                bg_color = COLOR_GRID_BACKGROUND # Default
                if (r_idx,c_idx) == (r_selected,c_selected):
                    bg_color = COLOR_CELL_SELECTED_BG
                elif (r_idx,c_idx) in related_coords:
                    bg_color = COLOR_CELL_HIGHLIGHT_BG
                
                # Highlight same numbers
                if selected_val and selected_val != 0 and current_board_values.get((r_idx,c_idx)) == selected_val:
                     bg_color = COLOR_CELL_HIGHLIGHT_BG if bg_color == COLOR_GRID_BACKGROUND else bg_color # Keep selected color if it is

                cell_frame.config(bg=bg_color)
                if num_lbl: num_lbl.config(bg=bg_color)
                if pencil_lbl: pencil_lbl.config(bg=bg_color)

    def _highlight_selected_cell(self): # For multiplayer, uses internal selected_cell_coords
        if self.selected_cell_coords:
            r, c = self.selected_cell_coords
            related = []
            if self.controller.sudoku_client and self.controller.sudoku_client.server_board_state: # Basic highlight for MP
                for i in range(self.grid_size): related.append((r, i)); related.append((i, c))
                sr, sc = r - r % self.subgrid_size, c - c % self.subgrid_size 
                for i in range(self.subgrid_size):
                    for j in range(self.subgrid_size): related.append((sr + i, sc + j))
            self.highlight_selected_cell(r,c, related)


    def _clear_all_highlights(self):
        for r_idx in range(self.grid_size):
            for c_idx in range(self.grid_size):
                cell_frame = self.cells_widgets.get((r_idx, c_idx))
                num_lbl = self.num_labels.get((r_idx,c_idx))
                pencil_lbl = self.pencil_labels.get((r_idx,c_idx))
                
                if cell_frame: cell_frame.config(bg=COLOR_GRID_BACKGROUND)
                if num_lbl: num_lbl.config(bg=COLOR_GRID_BACKGROUND)
                if pencil_lbl: pencil_lbl.config(bg=COLOR_GRID_BACKGROUND)
    
    def update_cell_display(self, r, c, number, is_fixed, is_error=False, pencil_marks_set=None, is_hint_fill=False):
        num_lbl = self.num_labels.get((r,c))
        pencil_lbl = self.pencil_labels.get((r,c))
        cell_frame = self.cells_widgets.get((r,c)) # This is the inner_frame

        if not (num_lbl and pencil_lbl and cell_frame): 
            print(f"WARN UI: Widget not found for cell ({r},{c}) during update_cell_display"); return

        current_bg_of_cell = cell_frame.cget("bg") # Get current bg (might be highlighted)
        fg_color = COLOR_CELL_USER_TEXT # Default for user numbers

        if is_hint_fill: # Hint fill overrides other colors temporarily
            # The actual bg change for hint_fill should be managed by highlight logic if desired
            # Here, we just set text color. The actual cell bg is set by highlight_selected_cell
            # Forcing hint fill bg here can be problematic with selection highlights.
            # Let's assume hint_fill primarily affects text color and the cell itself is selected.
            fg_color = "white" # Text color on hint_fill
            # If you want to force cell_frame bg: cell_frame.config(bg=COLOR_CELL_HINT_FILL)
            # but this will be overridden by selection logic.
            # A better way for hint fill is for highlight_selected_cell to know about it.
            # For now, update_cell_display makes the number prominent on the existing bg.
            if current_bg_of_cell != COLOR_CELL_SELECTED_BG: # if cell not selected, make it hint color
                 cell_frame.config(bg=COLOR_CELL_HINT_FILL)
                 num_lbl.config(bg=COLOR_CELL_HINT_FILL)
                 pencil_lbl.config(bg=COLOR_CELL_HINT_FILL)

        elif is_fixed: 
            fg_color = COLOR_CELL_FIXED_TEXT
        elif is_error: 
            fg_color = COLOR_CELL_ERROR_TEXT
        
        num_lbl.config(fg=fg_color)
        # pencil_lbl.config(bg=current_bg_of_cell) # Pencil label uses cell's background

        if number != 0:
            num_lbl.config(text=str(number))
            pencil_lbl.config(text="") # Clear pencil marks
        else: # Number is 0, display pencil marks if any
            num_lbl.config(text="")
            if pencil_marks_set and len(pencil_marks_set) > 0:
                # Create a 3x3 grid string for pencil marks
                lines = []
                for i in range(1, 10, 3): # 1, 4, 7
                    line_str = ""
                    for j in range(3): # 0, 1, 2 for offset
                        mark = i + j
                        line_str += str(mark) if mark in pencil_marks_set else " "
                        if j < 2: line_str += " " # Space between numbers in a row
                    lines.append(line_str.strip())
                pencil_lbl.config(text="\n".join(lines))
            else:
                pencil_lbl.config(text="")

    def update_board_display(self, board_data, fixed_mask, error_cells=None, pencil_data=None):
        print("DEBUG UI: update_board_display CALLED")
        error_cells = error_cells or set()
        pencil_data = pencil_data or {}
        
        for r_idx in range(self.grid_size):
            for c_idx in range(self.grid_size):
                is_err = (r_idx,c_idx) in error_cells if board_data[r_idx][c_idx] != 0 else False
                self.update_cell_display(r_idx, c_idx, board_data[r_idx][c_idx], 
                                         fixed_mask[r_idx][c_idx],
                                         is_error=is_err,
                                         pencil_marks_set=pencil_data.get((r_idx,c_idx), set()))
        self.update_number_pad_counts(board_data)
        
        # Re-apply selection highlight after board update
        if self.selected_cell_coords:
            sr,sc = self.selected_cell_coords
            # Determine related_coords based on game mode
            related = []
            if self.game_mode == "classic":
                related = self.controller.get_related_coords_for_highlight(sr,sc)
            elif self.game_mode == "multiplayer": # Basic related for MP
                 for i in range(self.grid_size): related.append((sr, i)); related.append((i, sr))
                 s_r, s_c = sr - sr % self.subgrid_size, sc - sc % self.subgrid_size 
                 for i in range(self.subgrid_size):
                    for j in range(self.subgrid_size): related.append((s_r + i, s_c + j))
            self.highlight_selected_cell(sr,sc,related)
        else:
            self._clear_all_highlights()
        print("DEBUG UI: update_board_display FINISHED")
    
    def update_number_pad_counts(self, board_data):
        counts = {i:0 for i in range(1,10)}
        for r_row in board_data:
            for num_val_cell in r_row:
                if 1 <= num_val_cell <= 9: 
                    counts[num_val_cell] += 1
        
        for num_key, count_var in self.number_counts_vars.items():
            remaining = self.grid_size - counts.get(num_key,0)
            count_var.set(str(remaining if remaining > 0 else "✓")) # Show checkmark if all placed
            # Optionally, disable number pad button if remaining is 0 (NYI)

    def show_message(self, title, message, message_type="info"):
        # Ensure messages are shown on top of the main app window
        # parent=self.master_app is good
        if message_type=="error": messagebox.showerror(title, message, parent=self.master_app)
        elif message_type=="warning": messagebox.showwarning(title, message, parent=self.master_app)
        else: messagebox.showinfo(title, message, parent=self.master_app)

    def update_info_display(self, mistakes, time_seconds, difficulty_text=None, score=None, max_mistakes=None):
        self.mistakes_count_ui = mistakes
        self.time_seconds_ui = time_seconds
        if difficulty_text: self.difficulty_ui_text = difficulty_text
        if score is not None: self.score_ui = score
        if max_mistakes is not None: self.max_mistakes_ui = max_mistakes

        if self.game_mode == "classic" and self.max_mistakes_ui > 0:
            self.mistakes_label.config(text=f"Lỗi: {self.mistakes_count_ui}/{self.max_mistakes_ui}")
        elif self.game_mode == "multiplayer": # In MP, just show "Lỗi: -" or similar if not tracked by client
            self.mistakes_label.config(text="Chơi mạng") # Or hide mistakes label for MP
        else: # Default or unknown
            self.mistakes_label.config(text=f"Lỗi: {self.mistakes_count_ui}")
        
        self.difficulty_label.config(text=str(self.difficulty_ui_text).capitalize())
        minutes = self.time_seconds_ui // 60
        seconds = self.time_seconds_ui % 60
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        self.score_label.config(text=f"{self.score_ui:,}")

    def start_timer_display(self): # Called by controller if needed
        self._update_timer_display()

    def _update_timer_display(self): # Internal periodic update
        # This method uses the UI's stored values
        self.update_info_display(self.mistakes_count_ui, self.time_seconds_ui, 
                                 self.difficulty_ui_text, self.score_ui, self.max_mistakes_ui)

    def stop_timer_display(self): # Called by controller if needed
        pass # Timer job is managed by controller

    def reset_ui_for_new_game(self):
        print("DEBUG UI: reset_ui_for_new_game CALLED")
        self.selected_cell_coords = None
        self.is_pencil_mode_on = False
        
        pencil_button = self.action_buttons_map.get("pencil_mode_button")
        if pencil_button:
            pencil_button.config(text="✏️ Viết chì (OFF)", relief=tk.RAISED, bg="#FFFFFF")
        
        self._clear_all_highlights()
        
        # Reset UI state variables
        self.mistakes_count_ui = 0
        self.time_seconds_ui = 0
        self.score_ui = 0 # Default score, controller will set actual if needed
        self.max_mistakes_ui = 0 # Reset, controller will set for classic
        self.difficulty_ui_text = "N/A" # Controller will set
        
        if self.game_mode == "classic":
            self.hints_remaining_var.set("6") # Reset hints for classic
        else: # Multiplayer
            self.hints_remaining_var.set("0") # No hints in MP by default

        for i in range(1,10): self.number_counts_vars[i].set("9") # Reset number pad counts

        # Call update_info_display with reset values.
        # The controller (main.py) will call update_info_display again with actual game data
        # after this reset, so this provides a clean slate.
        self.update_info_display(self.mistakes_count_ui, self.time_seconds_ui, 
                                 self.difficulty_ui_text, self.score_ui, self.max_mistakes_ui)
        
        # Clear board display (set all to 0, no fixed, no errors, no pencil)
        empty_board = [[0 for _ in range(9)] for _ in range(9)]
        empty_mask = [[False for _ in range(9)] for _ in range(9)]
        self.update_board_display(empty_board, empty_mask, {}, {})

>>>>>>> 25ece6d (123)
        print("DEBUG UI: reset_ui_for_new_game FINISHED")