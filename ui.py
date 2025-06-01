# ui.py
import customtkinter as ctk
from tkinter import messagebox, StringVar, colorchooser

class ColorScheme:
    def __init__(self):
        pass

    def get_colors(self, custom_board_colors=None):
        is_dark_current = ctk.get_appearance_mode().lower() == "dark"
        base_colors = {}
        if is_dark_current:
            base_colors = {'primary': "#1e40af", 'primary_hover': "#1d4ed8", 'secondary': "#64748b", 'accent': "#06b6d4", 'success': "#10b981", 'warning': "#f59e0b", 'error': "#ef4444", 'background': "#0f172a", 'surface': "#1e293b", 'surface_variant': "#334155", 'on_surface': "#f8fafc", 'on_surface_variant': "#cbd5e1", 'outline': "#475569", 'gradient_start': "#1e40af", 'gradient_end': "#06b6d4",
                           'cell_default': "#334155", 'cell_selected': "#1e40af", 'cell_related': "#475569", 'cell_same_number': "#059669",
                           'cell_fixed': ("#6B7280", "#9CA3AF"), 'cell_user': ("#F9FAFB", "#E5E7EB"), 'cell_error': ("#EF4444", "#FCA5A5"), 'cell_hint': "#10b981",
                           'primary_selected_bg': "#0652DD"}
        else: # Light mode
            base_colors = {'primary': "#2563eb", 'primary_hover': "#1d4ed8", 'secondary': "#64748b", 'accent': "#0891b2", 'success': "#059669", 'warning': "#d97706", 'error': "#dc2626", 'background': "#f8fafc", 'surface': "#ffffff", 'surface_variant': "#f1f5f9", 'on_surface': "#0f172a", 'on_surface_variant': "#475569", 'outline': "#cbd5e1", 'gradient_start': "#2563eb", 'gradient_end': "#0891b2",
                           'cell_default': "#ffffff", 'cell_selected': "#dbeafe", 'cell_related': "#e0e7ff", 'cell_same_number': "#d1fae5",
                           'cell_fixed': ("#4B5563", "#374151"), 'cell_user': ("#1F2937", "#111827"), 'cell_error': ("#FEE2E2", "#EF4444"), 'cell_hint': "#6ee7b7",
                           'primary_selected_bg': "#BFDBFE"}

        if custom_board_colors:
            custom_map = {
                "cell_default_bg_custom": "cell_default", "cell_selected_custom": "cell_selected",
                "cell_related_custom": "cell_related", "cell_same_number_custom": "cell_same_number",
                "cell_hint_fill_custom": "cell_hint", "cell_fixed_text_custom": "cell_fixed",
                "cell_user_text_custom": "cell_user", "cell_error_text_custom": "cell_error",
            }
            for custom_key, scheme_key in custom_map.items():
                if custom_key in custom_board_colors and custom_board_colors[custom_key]:
                    custom_val = custom_board_colors[custom_key]
                    if isinstance(base_colors[scheme_key], tuple) and isinstance(custom_val, str):
                         base_colors[scheme_key] = (custom_val, custom_val)
                    else:
                        base_colors[scheme_key] = custom_val
        return base_colors

class FontSystem:
    def __init__(self):
        self.fonts = {'title_large': ctk.CTkFont(family="Segoe UI Variable Display", size=40, weight="bold"), 'title_medium': ctk.CTkFont(family="Segoe UI Variable Display", size=28, weight="bold"), 'title_small': ctk.CTkFont(family="Segoe UI Variable Text", size=20, weight="bold"), 'heading': ctk.CTkFont(family="Segoe UI Variable Text", size=18, weight="bold"), 'body_large': ctk.CTkFont(family="Segoe UI Variable Text", size=16), 'body_medium': ctk.CTkFont(family="Segoe UI Variable Text", size=14), 'body_small': ctk.CTkFont(family="Segoe UI Variable Text", size=12), 'caption': ctk.CTkFont(family="Segoe UI Variable Text", size=11), 'cell_number': ctk.CTkFont(family="JetBrains Mono NL", size=24, weight="bold"), 'cell_pencil': ctk.CTkFont(family="JetBrains Mono NL", size=9), 'number_pad': ctk.CTkFont(family="JetBrains Mono NL", size=22, weight="bold"), 'number_pad_count': ctk.CTkFont(family="JetBrains Mono NL", size=10), 'button': ctk.CTkFont(family="Segoe UI Variable Text", size=14, weight="bold"), 'button_large': ctk.CTkFont(family="Segoe UI Variable Text", size=16, weight="bold")}

class EnhancedFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        colors = ColorScheme().get_colors(); default_kwargs = {'corner_radius': 12, 'border_width': 0, 'fg_color': colors['surface']}; default_kwargs.update(kwargs); super().__init__(master, **default_kwargs)

class EnhancedButton(ctk.CTkButton):
    def __init__(self, master, style="primary", **kwargs):
        colors = ColorScheme().get_colors(); fonts = FontSystem().fonts
        style_configs = {'primary': {'fg_color': colors['primary'], 'hover_color': colors['primary_hover'], 'text_color': 'white'}, 'secondary': {'fg_color': 'transparent', 'hover_color': colors['surface_variant'], 'text_color': colors['on_surface'], 'border_width': 2, 'border_color': colors['outline']}, 'accent': {'fg_color': colors['accent'], 'hover_color': colors['primary'], 'text_color': 'white'}, 'success': {'fg_color': colors['success'], 'hover_color': colors['primary'], 'text_color': 'white'}, 'warning': {'fg_color': colors['warning'], 'hover_color': colors['error'], 'text_color': 'white'}, 'error': {'fg_color': colors['error'], 'hover_color': colors['error'], 'text_color': 'white'}}
        final_config = {'corner_radius': 8, 'height': 44, 'font': fonts['button'], **style_configs.get(style, style_configs['primary'])}
        final_config.update(kwargs)
        super().__init__(master, **final_config)

class BaseScreen(ctk.CTkFrame):
    def __init__(self, master_app, controller):
        general_colors = ColorScheme().get_colors()
        super().__init__(master_app, fg_color=general_colors['background'])
        self.master_app = master_app; self.controller = controller
        self.colors = general_colors
        self.fonts = FontSystem().fonts
    def _get_appearance_mode_color(self, color_tuple_or_str):
        if isinstance(color_tuple_or_str, (list, tuple)) and len(color_tuple_or_str) == 2: return color_tuple_or_str[0] if ctk.get_appearance_mode().lower() == "light" else color_tuple_or_str[1]
        return color_tuple_or_str

class MainMenuScreen(BaseScreen):
    def __init__(self, master_app, controller):
        super().__init__(master_app, controller)
        self._create_main_content()
    def _create_main_content(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent"); main_container.pack(expand=True, fill=ctk.BOTH, padx=30, pady=30)
        content_frame = EnhancedFrame(main_container, corner_radius=20); content_frame.pack(expand=True, fill=ctk.BOTH, padx=10, pady=10)
        ctk.CTkLabel(content_frame, text="🎯 SUDOKU CLASSIC", font=self.fonts['title_large'], text_color=self.colors['primary']).pack(pady=(30, 15))
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent"); buttons_frame.pack(fill=ctk.X, padx=30, pady=10)
        self.continue_button_text_var = StringVar()
        self.continue_button = EnhancedButton(buttons_frame, textvariable=self.continue_button_text_var, command=self.controller.continue_classic_game, style="accent", height=65, font=self.fonts['button_large']); self.continue_button.pack(fill="x", pady=(0, 10))
        EnhancedButton(buttons_frame, text="🎮 Trò Chơi Mới (Cổ Điển)", command=self.controller.show_new_classic_game_dialog, style="primary", height=50).pack(fill="x", pady=5)
        ctk.CTkFrame(buttons_frame, height=1, fg_color=self.colors['outline']).pack(fill="x", pady=15)
        ctk.CTkLabel(buttons_frame, text="🌐 MULTIPLAYER", font=self.fonts['heading'], text_color=self.colors['accent']).pack(pady=(0, 10))
        mp_buttons_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent"); mp_buttons_frame.pack(fill="x", pady=(0, 15)); mp_buttons_frame.grid_columnconfigure((0, 1), weight=1)
        EnhancedButton(mp_buttons_frame, text="🏠 Tạo Phòng", command=self.controller.action_create_multiplayer_game, style="success", height=45).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        EnhancedButton(mp_buttons_frame, text="🚪 Tham Gia", command=self.controller.action_join_multiplayer_game, style="secondary", height=45).grid(row=0, column=1, padx=(5, 0), sticky="ew")
        ctk.CTkFrame(buttons_frame, height=1, fg_color=self.colors['outline']).pack(fill="x", pady=(15,10))
        EnhancedButton(buttons_frame, text="⚙️ Cài Đặt", command=self.controller.show_settings_screen, style="secondary", height=45).pack(fill="x", pady=5)
        EnhancedButton(buttons_frame, text="📊 Thống Kê", command=self.controller.show_statistics_screen, style="secondary", height=45).pack(fill="x", pady=(5,0)) # Text updated
        bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent"); bottom_frame.pack(fill=ctk.X, side=ctk.BOTTOM, padx=30, pady=(15, 30))
        EnhancedButton(bottom_frame, text="❌ Thoát Game", command=self.master_app.quit_application, style="error", height=40).pack(fill="x")
    def update_continue_button_state(self, game_data):
        if game_data and game_data.get('board_data'):
            time_played = game_data.get('time_played', 0); difficulty = game_data.get('difficulty', "N/A"); mistakes = game_data.get('mistakes', 0); max_mistakes = game_data.get('max_mistakes', 0)
            minutes = time_played // 60; seconds = time_played % 60; mistake_text = f"{mistakes}/{max_mistakes}" if max_mistakes > 0 else f"{mistakes}"
            self.continue_button_text_var.set(f"▶️ Tiếp tục ({difficulty.capitalize()})\n⏱️ {minutes:02d}:{seconds:02d} • ❌ {mistake_text}")
            self.continue_button.configure(state=ctk.NORMAL, fg_color=self._get_appearance_mode_color(self.colors['accent']))
        else:
            self.continue_button_text_var.set("▶️ Tiếp tục\n(Chưa có game)"); self.continue_button.configure(state=ctk.DISABLED, fg_color=self.colors['surface_variant'])

class NewGameDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Trò Chơi Mới"):
        super().__init__(parent)
        self.colors = ColorScheme().get_colors(); self.fonts = FontSystem().fonts
        self.transient(parent); self.grab_set(); self.title(title); self.geometry("550x320")
        self.resizable(False, False); self.configure(fg_color=self.colors['background'])
        self.selected_difficulty_internal = "medium"; self.ok_pressed = False; self.result = None
        self.difficulties_map = {"Rất Dễ": ("very_easy", "🟢", "Người mới"), "Dễ": ("easy", "🟡", "Khởi động"), "Bình thường": ("medium", "🟠", "Cân bằng"), "Khó": ("hard", "🔴", "Thử thách"), "Chuyên gia": ("expert", "⚫", "Cao thủ")}
        self.difficulty_buttons_data = {}
        self._selected_button_display_name = self._get_display_name_from_internal(self.selected_difficulty_internal)
        self.selected_button_fg_color = self.colors['primary_selected_bg']
        self.default_button_border_color = self.colors['outline']
        self._build_enhanced_ui(); self._highlight_selected_button(); self.after(10, self._center_window); self.protocol("WM_DELETE_WINDOW", self._on_cancel)
    def _get_display_name_from_internal(self, internal_name):
        for disp_name, (intern_val, _, _) in self.difficulties_map.items():
            if intern_val == internal_name: return disp_name
        return "Bình thường"
    def _get_appearance_mode_color(self, color_tuple_or_str):
        if isinstance(color_tuple_or_str, (list, tuple)) and len(color_tuple_or_str) == 2: return color_tuple_or_str[0] if ctk.get_appearance_mode().lower() == "light" else color_tuple_or_str[1]
        return color_tuple_or_str
    def _center_window(self):
        self.update_idletasks(); parent = self.master; dialog_width = self.winfo_width(); dialog_height = self.winfo_height()
        parent_x = parent.winfo_rootx(); parent_y = parent.winfo_rooty(); parent_width = parent.winfo_width(); parent_height = parent.winfo_height()
        x = parent_x + (parent_width // 2) - (dialog_width // 2); y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f"+{x}+{y}")
    def _build_enhanced_ui(self):
        main_content_frame = EnhancedFrame(self, corner_radius=0, fg_color=self.colors['surface']); main_content_frame.pack(fill=ctk.BOTH, expand=True)
        header_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent"); header_frame.pack(fill=ctk.X, padx=20, pady=(20, 10))
        ctk.CTkLabel(header_frame, text="🎯 Chọn Độ Khó", font=self.fonts['title_medium'], text_color=self.colors['primary']).pack()
        scrollable_outer_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent"); scrollable_outer_frame.pack(fill=ctk.X, padx=20, pady=5)
        scrollable_difficulties_frame = ctk.CTkScrollableFrame(scrollable_outer_frame, fg_color="transparent", height=160, orientation="horizontal"); scrollable_difficulties_frame.pack(fill=ctk.X, expand=True)
        options_display_frame = ctk.CTkFrame(scrollable_difficulties_frame, fg_color="transparent"); options_display_frame.pack(fill=ctk.X)
        for display_name, (internal_name, icon, description) in self.difficulties_map.items():
            diff_container = EnhancedFrame(options_display_frame, corner_radius=10, fg_color="transparent", border_width=2, border_color=self.default_button_border_color, width=160)
            diff_container.pack(side=ctk.LEFT, padx=5, pady=5, fill=ctk.Y, expand=False); diff_container.pack_propagate(False)
            diff_container.bind("<Button-1>", lambda e, dn=display_name: self._select_difficulty_button_event(e, dn))
            content_in_container = ctk.CTkFrame(diff_container, fg_color="transparent"); content_in_container.pack(padx=8, pady=8, fill=ctk.BOTH, expand=True)
            for widget in [content_in_container]: widget.bind("<Button-1>", lambda e, dn=display_name: self._select_difficulty_button_event(e, dn))
            icon_label = ctk.CTkLabel(content_in_container, text=icon, font=ctk.CTkFont(size=22)); icon_label.pack(pady=(0,5)); icon_label.bind("<Button-1>", lambda e, dn=display_name: self._select_difficulty_button_event(e, dn))
            name_label = ctk.CTkLabel(content_in_container, text=display_name, font=self.fonts['body_large'], anchor="center"); name_label.pack(fill=ctk.X); name_label.bind("<Button-1>", lambda e, dn=display_name: self._select_difficulty_button_event(e, dn))
            desc_label = ctk.CTkLabel(content_in_container, text=description, font=self.fonts['caption'], text_color=self.colors['on_surface_variant'], anchor="center", wraplength=140); desc_label.pack(fill=ctk.X, pady=(3,0)); desc_label.bind("<Button-1>", lambda e, dn=display_name: self._select_difficulty_button_event(e, dn))
            self.difficulty_buttons_data[display_name] = diff_container
        button_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent"); button_frame.pack(fill=ctk.X, padx=20, pady=(10, 20)); button_frame.grid_columnconfigure((0, 1), weight=1)
        EnhancedButton(button_frame, text="❌ Hủy", command=self._on_cancel, style="secondary", height=40).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        EnhancedButton(button_frame, text="✅ Bắt Đầu", command=self._on_ok, style="primary", height=40).grid(row=0, column=1, padx=(5, 0), sticky="ew")
    def _select_difficulty_button_event(self, event, display_name): self._selected_button_display_name = display_name; self.selected_difficulty_internal = self.difficulties_map[display_name][0]; self._highlight_selected_button()
    def _highlight_selected_button(self):
        colors = ColorScheme().get_colors(); selected_fg = colors['primary_selected_bg']; default_border = colors['outline']; primary_border = colors['primary']
        for display_name, container in self.difficulty_buttons_data.items():
            if display_name == self._selected_button_display_name: container.configure(border_color=primary_border, fg_color=selected_fg)
            else: container.configure(border_color=default_border, fg_color="transparent")
    def _on_ok(self): self.ok_pressed = True; self.result = self.selected_difficulty_internal; self.destroy()
    def _on_cancel(self): self.ok_pressed = False; self.result = None; self.destroy()

class GameScreenUI(BaseScreen):
    def __init__(self, master_app, controller, game_mode="classic"):
        super().__init__(master_app, controller)
        self.board_specific_colors = ColorScheme().get_colors(self.controller.get_current_board_colors_config())
        self.game_mode = game_mode; self.grid_size = 9; self.subgrid_size = 3
        self.cells_widgets = {}; self.num_labels = {}; self.pencil_labels = {}
        self.selected_cell_coords = None; self.is_pencil_mode_on = False
        self.mistakes_count_ui = 0; self.max_mistakes_ui = 0; self.time_seconds_ui = 0
        self.score_ui = 0; self.difficulty_ui_text = "N/A"
        self.number_counts_vars = {i: StringVar(value="9") for i in range(1, 10)}
        self.hints_remaining_var = StringVar(value="💡 Gợi ý (6)")
        self.action_buttons_map = {}
        self._update_dynamic_colors(); self._create_enhanced_widgets()
    def _update_dynamic_colors(self):
        board_colors = self.board_specific_colors
        self.cell_bg_color_default = self._get_appearance_mode_color(board_colors['cell_default'])
        self.grid_line_color_thin = self._get_appearance_mode_color(self.colors['outline'])
        self.grid_line_color_thick = self._get_appearance_mode_color(self.colors['primary'])
        self.selected_cell_bg_color = self._get_appearance_mode_color(board_colors['cell_selected'])
        self.related_cell_bg_color = self._get_appearance_mode_color(board_colors['cell_related'])
        self.same_number_bg_color = self._get_appearance_mode_color(board_colors['cell_same_number'])
        self.hint_fill_bg_color = self._get_appearance_mode_color(board_colors['cell_hint'])
        self.fixed_text_color = self._get_appearance_mode_color(board_colors['cell_fixed'])
        self.user_text_color = self._get_appearance_mode_color(board_colors['cell_user'])
        self.error_text_color = self._get_appearance_mode_color(board_colors['cell_error'])
        self.pencil_text_color = self._get_appearance_mode_color(self.colors['on_surface_variant'])
    def _create_enhanced_widgets(self):
        main_container = ctk.CTkScrollableFrame(self, fg_color="transparent"); main_container.pack(fill=ctk.BOTH, expand=True, padx=0, pady=0)
        self._create_header(main_container); self._create_info_panel(main_container); self._create_game_board(main_container); self._create_action_panel(main_container); self._create_number_pad(main_container)
        if self.game_mode == "multiplayer": self._create_multiplayer_controls(main_container)
    def _create_header(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent", height=50); header_frame.pack(fill=ctk.X, pady=(0, 5), padx=10); header_frame.pack_propagate(False)
        EnhancedButton(header_frame, text="← Quay lại", command=self.controller.show_main_menu, style="secondary", width=100, height=35, font=self.fonts['body_medium']).pack(side=ctk.LEFT, pady=7)
        mode_text = f"🏆 {self.game_mode.title()} Mode" if self.game_mode == "classic" else f"🌐 {self.game_mode.title()} Mode"; ctk.CTkLabel(header_frame, text=mode_text, font=self.fonts['heading'], text_color=self.colors['accent']).pack(side=ctk.RIGHT, pady=7)
    def _create_info_panel(self, parent):
        info_panel = EnhancedFrame(parent, corner_radius=15, fg_color=self.colors['surface_variant']); info_panel.pack(fill=ctk.X, pady=(0, 10), padx=10)
        info_grid = ctk.CTkFrame(info_panel, fg_color="transparent"); info_grid.pack(fill=ctk.X, padx=15, pady=10); info_grid.grid_columnconfigure((0, 1, 2), weight=1)
        score_frame = self._create_info_item(info_grid, "💰 Điểm số", "0", 0); self.score_label = score_frame.winfo_children()[1]
        center_frame = ctk.CTkFrame(info_grid, fg_color="transparent"); center_frame.grid(row=0, column=1, sticky="ew", padx=8)
        self.mistakes_label = ctk.CTkLabel(center_frame, text="❌ Lỗi: 0/0", font=self.fonts['body_medium'], text_color=self.colors['warning']); self.mistakes_label.pack()
        self.difficulty_label = ctk.CTkLabel(center_frame, text="N/A", font=self.fonts['title_small'], text_color=self.colors['primary']); self.difficulty_label.pack(pady=(3, 0))
        time_frame = self._create_info_item(info_grid, "⏱️ Thời gian", "00:00", 2); self.time_label = time_frame.winfo_children()[1]
    def _create_info_item(self, parent, title, value, column):
        frame = ctk.CTkFrame(parent, fg_color="transparent"); frame.grid(row=0, column=column, sticky="ew")
        ctk.CTkLabel(frame, text=title, font=self.fonts['caption'], text_color=self.colors['on_surface_variant']).pack()
        ctk.CTkLabel(frame, text=value, font=self.fonts['heading'], text_color=self.colors['on_surface']).pack(pady=(1, 0)); return frame
    def _create_game_board(self, parent):
        board_outer_container = EnhancedFrame(parent, corner_radius=15, fg_color=self.colors['surface']); board_outer_container.pack(pady=10, anchor="center", padx=5)
        grid_container = ctk.CTkFrame(board_outer_container, fg_color=self.grid_line_color_thick, corner_radius=10); grid_container.pack(padx=10, pady=10)
        cell_size = 48; subgrid_spacing = 2; cell_spacing = 1
        for sr in range(self.subgrid_size):
            for sc in range(self.subgrid_size):
                subgrid_frame = ctk.CTkFrame(grid_container, fg_color=self.grid_line_color_thin, corner_radius=0); subgrid_frame.grid(row=sr, column=sc, padx=(0, subgrid_spacing if sc < self.subgrid_size -1 else 0), pady=(0, subgrid_spacing if sr < self.subgrid_size -1 else 0))
                for r_in_sub in range(self.subgrid_size):
                    for c_in_sub in range(self.subgrid_size):
                        r_abs, c_abs = sr * self.subgrid_size + r_in_sub, sc * self.subgrid_size + c_in_sub
                        cell_frame = ctk.CTkFrame(subgrid_frame, width=cell_size, height=cell_size, fg_color=self.cell_bg_color_default, corner_radius=3, border_width=0); cell_frame.grid(row=r_in_sub, column=c_in_sub, padx=(0, cell_spacing if c_in_sub < self.subgrid_size -1 else 0), pady=(0, cell_spacing if r_in_sub < self.subgrid_size -1 else 0), sticky="nsew"); cell_frame.pack_propagate(False)
                        cell_frame.bind("<Button-1>", lambda e, r_b=r_abs, c_b=c_abs: self._on_cell_click(r_b, c_b)); self.cells_widgets[(r_abs, c_abs)] = cell_frame
                        pencil_lbl = ctk.CTkLabel(cell_frame, text="", font=self.fonts['cell_pencil'], text_color=self.pencil_text_color); pencil_lbl.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, relwidth=0.95, relheight=0.95); pencil_lbl.bind("<Button-1>", lambda e, r_b=r_abs, c_b=c_abs: self._on_cell_click(r_b, c_b)); self.pencil_labels[(r_abs, c_abs)] = pencil_lbl
                        num_lbl = ctk.CTkLabel(cell_frame, text="", font=self.fonts['cell_number'], text_color=self.user_text_color); num_lbl.place(relx=0.5, rely=0.5, anchor=ctk.CENTER); num_lbl.bind("<Button-1>", lambda e, r_b=r_abs, c_b=c_abs: self._on_cell_click(r_b, c_b)); self.num_labels[(r_abs, c_abs)] = num_lbl
    def _create_action_panel(self, parent):
        action_panel = EnhancedFrame(parent, fg_color="transparent"); action_panel.pack(fill=ctk.X, pady=10)
        actions_grid = ctk.CTkFrame(action_panel, fg_color="transparent"); actions_grid.pack(padx=10, pady=5)
        actions_config = [("↺ Hoàn tác", self.controller.undo_move, "secondary", "classic"), ("⌫ Xóa", self._erase_selected_cell, "warning", "both"), ("✏️ Viết chì", self._toggle_pencil_mode, "accent", "classic"), (" Gợi ý", self.controller.request_hint, "success", "classic")]
        action_btn_font = self.fonts['button']; col = 0
        for text, cmd, style, mode_avail in actions_config:
            if mode_avail == "both" or (mode_avail == "classic" and self.game_mode == "classic"):
                if "Gợi ý" in text: btn = EnhancedButton(actions_grid, textvariable=self.hints_remaining_var, command=cmd, style=style, height=40, font=action_btn_font)
                else: btn = EnhancedButton(actions_grid, text=text, command=cmd, style=style, height=40, font=action_btn_font)
                btn.grid(row=0, column=col, padx=5, sticky="ew"); actions_grid.grid_columnconfigure(col, weight=1)
                if "Viết chì" in text: self.action_buttons_map["pencil_button"] = btn
                col += 1
    def _create_number_pad(self, parent):
        number_pad_container = EnhancedFrame(parent, fg_color="transparent"); number_pad_container.pack(pady=(5, 10))
        pad_horizontal_frame = ctk.CTkFrame(number_pad_container, fg_color="transparent"); pad_horizontal_frame.pack()
        for i in range(1, 10):
            num_btn_wrapper = ctk.CTkFrame(pad_horizontal_frame, fg_color="transparent"); num_btn_wrapper.pack(side=ctk.LEFT, padx=3, pady=3)
            btn = EnhancedButton(num_btn_wrapper, text=str(i), command=lambda num=i: self._on_number_press(num), style="primary", height=50, width=50, font=self.fonts['number_pad']); btn.pack()
            ctk.CTkLabel(num_btn_wrapper, textvariable=self.number_counts_vars[i], font=self.fonts['number_pad_count'], text_color=self.colors['on_surface_variant']).pack(pady=(1, 0))
    def _create_multiplayer_controls(self, parent):
        mp_controls_frame = EnhancedFrame(parent, fg_color="transparent"); mp_controls_frame.pack(fill=ctk.X, pady=5)
        EnhancedButton(mp_controls_frame, text="🏠 Tạo Game (MP)", command=lambda: self.controller.sudoku_client.request_new_multiplayer_game() if self.controller.sudoku_client else None, style="success", height=40).pack(side=ctk.LEFT, padx=5, expand=True, fill=ctk.X)
        self.join_game_id_var = StringVar(); ctk.CTkEntry(mp_controls_frame, textvariable=self.join_game_id_var, width=120, font=self.fonts['body_small'], placeholder_text="Game ID").pack(side=ctk.LEFT, padx=5, expand=True, fill=ctk.X)
        EnhancedButton(mp_controls_frame, text="🚪 Tham Gia (MP)", command=lambda: self.controller.sudoku_client.request_join_game(self.join_game_id_var.get()) if self.controller.sudoku_client and self.join_game_id_var.get() else None, style="secondary", height=40).pack(side=ctk.LEFT, padx=5, expand=True, fill=ctk.X)
    def _on_cell_click(self, r, c): self.selected_cell_coords = (r,c); self.controller.select_cell(r, c)
    def _on_number_press(self, num): self.controller.input_number(num, self.is_pencil_mode_on)
    def _erase_selected_cell(self): self.controller.erase_selected()
    def _toggle_pencil_mode(self):
        if self.game_mode != "classic": self.show_message("Thông báo", "Viết chì chỉ dùng cho game cổ điển.", "info"); return
        self.is_pencil_mode_on = not self.is_pencil_mode_on; pencil_btn = self.action_buttons_map.get("pencil_button")
        if pencil_btn:
            pencil_btn.configure(text=f"✏️ Viết chì ({'ON' if self.is_pencil_mode_on else 'OFF'})")
            if self.is_pencil_mode_on: pencil_btn.configure(fg_color=self.colors['success'], hover_color=self.colors['primary'])
            else: pencil_btn.configure(fg_color=self.colors['accent'], hover_color=self.colors['primary'])
    def highlight_selected_cell(self, r_selected, c_selected, related_coords=None):
        self._clear_all_highlights(); related_coords = related_coords or []
        active_board_data = None
        if self.game_mode == "classic" and self.controller.classic_game_state.get('board_data'): active_board_data = self.controller.classic_game_state['board_data']
        elif self.game_mode == "multiplayer" and self.controller.sudoku_client and self.controller.sudoku_client.server_board_state: active_board_data = self.controller.sudoku_client.server_board_state
        selected_val_on_board = 0
        if active_board_data and 0 <= r_selected < self.grid_size and 0 <= c_selected < self.grid_size and active_board_data[r_selected][c_selected] != 0: selected_val_on_board = active_board_data[r_selected][c_selected]
        for r_idx in range(self.grid_size):
            for c_idx in range(self.grid_size):
                cell_frame = self.cells_widgets.get((r_idx, c_idx))
                if not cell_frame or not cell_frame.winfo_exists(): continue
                current_cell_val = active_board_data[r_idx][c_idx] if active_board_data and 0 <= r_idx < self.grid_size and 0 <= c_idx < self.grid_size else 0
                target_bg = self.cell_bg_color_default
                if (r_idx, c_idx) == (r_selected, c_selected): target_bg = self.selected_cell_bg_color
                elif (r_idx, c_idx) in related_coords: target_bg = self.related_cell_bg_color
                if selected_val_on_board != 0 and current_cell_val == selected_val_on_board:
                    if target_bg == self.cell_bg_color_default: target_bg = self.same_number_bg_color
                cell_frame.configure(fg_color=target_bg)
    def _clear_all_highlights(self):
        for r_idx in range(self.grid_size):
            for c_idx in range(self.grid_size):
                cell_frame = self.cells_widgets.get((r_idx, c_idx))
                if cell_frame and cell_frame.winfo_exists(): cell_frame.configure(fg_color=self.cell_bg_color_default)
    def update_cell_display(self, r, c, number, is_fixed, is_error=False, pencil_marks_set=None, is_hint_fill=False):
        num_lbl, pencil_lbl, cell_frame = self.num_labels.get((r,c)), self.pencil_labels.get((r,c)), self.cells_widgets.get((r,c))
        if not (num_lbl and pencil_lbl and cell_frame and num_lbl.winfo_exists() and pencil_lbl.winfo_exists() and cell_frame.winfo_exists()): return
        current_text_color = self.user_text_color; target_cell_bg = cell_frame.cget("fg_color")
        if is_hint_fill: target_cell_bg = self.hint_fill_bg_color; current_text_color = self._get_appearance_mode_color(self.board_specific_colors.get("cell_hint_text_custom") or self.colors['on_surface'])
        elif is_fixed: current_text_color = self.fixed_text_color
        elif is_error: current_text_color = self.error_text_color
        cell_frame.configure(fg_color=target_cell_bg); num_lbl.configure(text_color=current_text_color); pencil_lbl.configure(text_color=self.pencil_text_color)
        if number != 0: num_lbl.configure(text=str(number)); pencil_lbl.configure(text="")
        else:
            num_lbl.configure(text="");
            if pencil_marks_set and len(pencil_marks_set) > 0:
                lines = [];
                for i_row in range(1, 10, 3):
                    line_str = "";
                    for j_col_in_row in range(3): mark = i_row + j_col_in_row; line_str += str(mark) if mark in pencil_marks_set else " ";
                    if j_col_in_row < 2: line_str += " "
                    lines.append(line_str.strip())
                pencil_lbl.configure(text="\n".join(lines))
            else: pencil_lbl.configure(text="")
    def update_board_display(self, board_data, fixed_mask, error_cells=None, pencil_data=None):
        self._update_dynamic_colors()
        error_cells = error_cells or set(); pencil_data = pencil_data or {}
        for r_idx in range(self.grid_size):
            for c_idx in range(self.grid_size):
                is_err = (r_idx,c_idx) in error_cells if board_data[r_idx][c_idx] != 0 else False
                self.update_cell_display(r_idx, c_idx, board_data[r_idx][c_idx], fixed_mask[r_idx][c_idx], is_error=is_err, pencil_marks_set=pencil_data.get((r_idx,c_idx), set()))
        self.update_number_pad_counts(board_data)
        if self.selected_cell_coords: sr,sc = self.selected_cell_coords; related = self.controller.get_related_coords_for_highlight(sr,sc) if self.game_mode == "classic" else []; self.highlight_selected_cell(sr,sc,related)
        else: self._clear_all_highlights()
    def update_number_pad_counts(self, board_data):
        counts = {i:0 for i in range(1,10)};
        for r_row in board_data:
            for num_val_cell in r_row:
                if 1 <= num_val_cell <= 9: counts[num_val_cell] += 1
        for num_key, count_var in self.number_counts_vars.items(): remaining = self.grid_size - counts.get(num_key,0); count_var.set(str(remaining if remaining > 0 else "✓"))
    def show_message(self, title, message, message_type="info"):
        parent_window = self.master_app
        if message_type=="error": messagebox.showerror(title, message, parent=parent_window)
        elif message_type=="warning": messagebox.showwarning(title, message, parent=parent_window)
        else: messagebox.showinfo(title, message, parent=parent_window)
    def update_info_display(self, mistakes, time_seconds, difficulty_text=None, score=None, max_mistakes=None):
        self.mistakes_count_ui = mistakes; self.time_seconds_ui = time_seconds
        if difficulty_text: self.difficulty_ui_text = difficulty_text
        if score is not None: self.score_ui = score
        if max_mistakes is not None: self.max_mistakes_ui = max_mistakes
        if hasattr(self, 'mistakes_label') and self.mistakes_label.winfo_exists():
            if self.game_mode == "classic" and self.max_mistakes_ui > 0: self.mistakes_label.configure(text=f"❌ Lỗi: {self.mistakes_count_ui}/{self.max_mistakes_ui}")
            elif self.game_mode == "multiplayer": self.mistakes_label.configure(text="🌐 Chơi mạng")
            else: self.mistakes_label.configure(text=f"❌ Lỗi: {self.mistakes_count_ui}")
        if hasattr(self, 'difficulty_label') and self.difficulty_label.winfo_exists(): self.difficulty_label.configure(text=str(self.difficulty_ui_text).capitalize())
        if hasattr(self, 'time_label') and self.time_label.winfo_exists(): minutes = self.time_seconds_ui // 60; seconds = self.time_seconds_ui % 60; self.time_label.configure(text=f"{minutes:02d}:{seconds:02d}")
        if hasattr(self, 'score_label') and self.score_label.winfo_exists(): self.score_label.configure(text=f"{self.score_ui:,}")
    def _update_timer_display(self): self.update_info_display(self.mistakes_count_ui, self.time_seconds_ui, self.difficulty_ui_text, self.score_ui, self.max_mistakes_ui)
    def reset_ui_for_new_game(self):
        self._update_dynamic_colors()
        self.selected_cell_coords = None; self.is_pencil_mode_on = False
        pencil_btn = self.action_buttons_map.get("pencil_button")
        if pencil_btn and pencil_btn.winfo_exists(): pencil_btn.configure(text="✏️ Viết chì (OFF)", fg_color=self.colors['accent'])
        self._clear_all_highlights()
        self.mistakes_count_ui = 0; self.time_seconds_ui = 0; self.score_ui = 0 ; self.max_mistakes_ui = 0; self.difficulty_ui_text = "N/A"
        if self.game_mode == "classic": self.hints_remaining_var.set("💡 Gợi ý (6)")
        else: self.hints_remaining_var.set("💡 Gợi ý (0)")
        for i in range(1,10): self.number_counts_vars[i].set("9")
        self.update_info_display(self.mistakes_count_ui, self.time_seconds_ui, self.difficulty_ui_text, self.score_ui, self.max_mistakes_ui)
        empty_board = [[0 for _ in range(9)] for _ in range(9)]; empty_mask = [[False for _ in range(9)] for _ in range(9)]
        self.update_board_display(empty_board, empty_mask, {}, {})

class SettingsScreen(BaseScreen):
    def __init__(self, master_app, controller):
        super().__init__(master_app, controller)
        self.board_color_vars = {}
        self.board_color_previews = {}
        self.current_custom_board_colors = self.controller.get_current_board_colors_config().copy()
        self._create_settings_content()
        self._update_theme_button_styles()
        self._populate_board_color_inputs()
    def _pick_color(self, key_name, entry_var, preview_widget, is_text_color_prop):
        initial_color_hex = entry_var.get()
        if not (initial_color_hex.startswith("#") and len(initial_color_hex) == 7):
            default_board_colors = self.controller.get_default_board_colors_for_theme()
            initial_color_val = default_board_colors.get(key_name)
            if isinstance(initial_color_val, tuple): initial_color_hex = initial_color_val[1 if ctk.get_appearance_mode().lower() == "dark" else 0]
            else: initial_color_hex = initial_color_val
            if not initial_color_hex: initial_color_hex = "#ffffff"
        color_code = colorchooser.askcolor(title="Chọn màu", initialcolor=initial_color_hex, parent=self)
        if color_code and color_code[1]:
            hex_color = str(color_code[1])
            entry_var.set(hex_color)
            if preview_widget:
                if is_text_color_prop: preview_widget.configure(text_color=hex_color)
                else: preview_widget.configure(fg_color=hex_color)
    def _create_settings_content(self):
        back_button_frame = ctk.CTkFrame(self, fg_color=self.colors['background']); back_button_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=30, pady=(10,20))
        EnhancedButton(back_button_frame, text="⬅️ Quay Lại Menu Chính", command=self.controller.show_main_menu, style="primary", height=45).pack(fill=ctk.X)
        main_scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent"); main_scroll_container.pack(expand=True, fill=ctk.BOTH, padx=0, pady=0)
        content_frame = ctk.CTkFrame(main_scroll_container, fg_color="transparent"); content_frame.pack(expand=True, fill=ctk.X, padx=30, pady=(20,0))
        ctk.CTkLabel(content_frame, text="⚙️ Cài Đặt", font=self.fonts['title_large'], text_color=self.colors['primary']).pack(pady=(0, 15))
        theme_options_outer_frame = EnhancedFrame(content_frame, corner_radius=10); theme_options_outer_frame.pack(pady=10, padx=0, fill=ctk.X)
        ctk.CTkLabel(theme_options_outer_frame, text="Chủ Đề Giao Diện:", font=self.fonts['heading'], text_color=self.colors['on_surface']).pack(pady=(15,5))
        theme_buttons_container = ctk.CTkFrame(theme_options_outer_frame, fg_color="transparent"); theme_buttons_container.pack(pady=(5,15), padx=20, fill=ctk.X); theme_buttons_container.grid_columnconfigure((0,1), weight=1)
        self.light_button = EnhancedButton(theme_buttons_container, text="⚪ Sáng", command=lambda: self._select_theme("light"), style="secondary", height=45, font=self.fonts['button_large']); self.light_button.grid(row=0, column=0, padx=(0,5), sticky="ew")
        self.dark_button = EnhancedButton(theme_buttons_container, text="⚫ Tối", command=lambda: self._select_theme("dark"), style="secondary", height=45, font=self.fonts['button_large']); self.dark_button.grid(row=0, column=1, padx=(5,0), sticky="ew")
        ctk.CTkFrame(content_frame, height=1, fg_color=self.colors['outline']).pack(fill="x", padx=0, pady=(20,10))
        ctk.CTkLabel(content_frame, text="🎨 Tùy Chỉnh Màu Bàn Cờ", font=self.fonts['title_medium'], text_color=self.colors['accent']).pack(pady=(5,15))
        board_color_frame = EnhancedFrame(content_frame, corner_radius=10, fg_color=self.colors['surface_variant']); board_color_frame.pack(pady=10, padx=0, fill=ctk.X)
        color_configs = [("cell_default_bg_custom", "Nền ô mặc định", False),("cell_selected_custom", "Ô được chọn (nền)", False),("cell_related_custom", "Ô liên quan (nền)", False),("cell_same_number_custom", "Ô cùng số (nền)", False),("cell_hint_fill_custom", "Ô gợi ý (nền)", False),("cell_fixed_text_custom", "Số cố định (chữ)", True),("cell_user_text_custom", "Số người chơi (chữ)", True),("cell_error_text_custom", "Số lỗi (chữ)", True)]
        for key, name, is_text in color_configs:
            item_frame = ctk.CTkFrame(board_color_frame, fg_color="transparent"); item_frame.pack(fill=ctk.X, padx=15, pady=8); item_frame.grid_columnconfigure(0, weight=1); item_frame.grid_columnconfigure(1, weight=0); item_frame.grid_columnconfigure(2, weight=0); item_frame.grid_columnconfigure(3, weight=0)
            ctk.CTkLabel(item_frame, text=name, font=self.fonts['body_medium'], anchor="w").grid(row=0, column=0, sticky="ew", padx=(0,10))
            color_var = StringVar(); entry = ctk.CTkEntry(item_frame, textvariable=color_var, width=90, font=self.fonts['body_small']); entry.grid(row=0, column=1, sticky="e"); self.board_color_vars[key] = color_var
            preview = ctk.CTkLabel(item_frame, text="Aa" if is_text else "", width=24, height=24, corner_radius=4); preview.grid(row=0, column=2, padx=5, sticky="e"); self.board_color_previews[key] = preview
            pick_button = EnhancedButton(item_frame, text="...", width=30, height=30, style="secondary", command=lambda k=key, v=color_var, p=preview, i=is_text: self._pick_color(k, v, p, i)); pick_button.grid(row=0, column=3, sticky="e")
        EnhancedButton(board_color_frame, text="Áp Dụng Màu Bàn Cờ", command=self._apply_board_colors, style="success").pack(pady=(10,15), padx=20, fill=ctk.X)
        EnhancedButton(board_color_frame, text="Đặt Lại Màu Mặc Định", command=self._reset_board_colors_to_theme, style="warning").pack(pady=(0,15), padx=20, fill=ctk.X)
    def _populate_board_color_inputs(self):
        default_board_colors = self.controller.get_default_board_colors_for_theme()
        for key, var in self.board_color_vars.items():
            color_val = self.current_custom_board_colors.get(key, default_board_colors.get(key))
            hex_color = color_val[1] if isinstance(color_val, tuple) and ctk.get_appearance_mode().lower() == "dark" else (color_val[0] if isinstance(color_val, tuple) else color_val)
            if not hex_color: hex_color = "#FFFFFF"
            var.set(hex_color)
            preview_widget = self.board_color_previews.get(key)
            if preview_widget:
                is_text_color_prop = preview_widget.cget("text") == "Aa"
                if is_text_color_prop: preview_widget.configure(text_color=hex_color, fg_color=self.colors.get('surface', "#DDDDDD") if ctk.get_appearance_mode().lower() == "light" else self.colors.get('surface', "#222222"))
                else: preview_widget.configure(fg_color=hex_color)
    def _apply_board_colors(self):
        new_colors = {}; valid_input = True
        for key, var in self.board_color_vars.items():
            hex_color = var.get().strip()
            if hex_color.startswith("#") and len(hex_color) == 7: new_colors[key] = hex_color
            else: messagebox.showwarning("Màu không hợp lệ", f"Mã màu cho '{key.replace('_custom','').replace('_',' ').title()}' không đúng: {hex_color}. Phải là #RRGGBB.", parent=self); valid_input = False; break
        if valid_input: self.controller.update_board_colors_config(new_colors); self.current_custom_board_colors = new_colors.copy(); self._populate_board_color_inputs(); messagebox.showinfo("Cài đặt màu", "Màu bàn cờ đã được cập nhật.", parent=self)
    def _reset_board_colors_to_theme(self): self.controller.update_board_colors_config({}); self.current_custom_board_colors = {}; self._populate_board_color_inputs(); messagebox.showinfo("Cài đặt màu", "Màu bàn cờ đã được đặt lại về mặc định.", parent=self)
    def _select_theme(self, mode_name): self.controller.apply_appearance_mode(mode_name)
    def _update_theme_button_styles(self):
        current_mode = ctk.get_appearance_mode().lower(); colors = ColorScheme().get_colors()
        selected_config = {'fg_color': colors['primary'], 'hover_color': colors['primary_hover'], 'text_color': self._get_appearance_mode_color(("black", "white")), 'border_width': 0}
        default_config = {'fg_color': 'transparent', 'hover_color': colors['surface_variant'], 'text_color': colors['on_surface'], 'border_width': 2, 'border_color': colors['outline']}
        if hasattr(self, 'light_button') and hasattr(self, 'dark_button'):
            if current_mode == "light": self.light_button.configure(**selected_config); self.dark_button.configure(**default_config)
            else: self.dark_button.configure(**selected_config); self.light_button.configure(**default_config)

class StatisticsScreen(BaseScreen):
    def __init__(self, master_app, controller):
        super().__init__(master_app, controller)
        self.user_stats = self.controller.user_stats
        self._create_statistics_layout()
    def _format_time(self, total_seconds):
        if total_seconds == float('inf') or total_seconds is None: return "--:--"
        minutes = int(total_seconds // 60); seconds = int(total_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    def _create_stat_item(self, parent, icon, text, value_text): # Removed achievement params
        item_frame = EnhancedFrame(parent, corner_radius=10, fg_color=self.colors['surface_variant']); item_frame.pack(fill=ctk.X, pady=6, padx=10)
        item_content_frame = ctk.CTkFrame(item_frame, fg_color="transparent"); item_content_frame.pack(fill=ctk.X, padx=15, pady=12); item_content_frame.grid_columnconfigure(1, weight=1)
        icon_label = ctk.CTkLabel(item_content_frame, text=icon, font=ctk.CTkFont(size=28), text_color=self.colors['primary']); icon_label.grid(row=0, column=0, rowspan=1, padx=(0, 12), sticky="w")
        text_label = ctk.CTkLabel(item_content_frame, text=text, font=self.fonts['body_large'], text_color=self.colors['on_surface'], anchor="w"); text_label.grid(row=0, column=1, sticky="w")
        value_label = ctk.CTkLabel(item_content_frame, text=str(value_text), font=self.fonts['heading'], text_color=self.colors['on_surface']); value_label.grid(row=0, column=2, padx=(10,0), sticky="e")
        return item_frame
    def _create_statistics_layout(self):
        back_button_frame = ctk.CTkFrame(self, fg_color=self.colors['background']); back_button_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=30, pady=(10,20))
        EnhancedButton(back_button_frame, text="⬅️ Quay Lại Menu Chính", command=self.controller.show_main_menu, style="primary", height=45).pack(fill=ctk.X)
        main_scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent"); main_scroll_container.pack(expand=True, fill=ctk.BOTH, padx=0, pady=0)
        content_container = ctk.CTkFrame(main_scroll_container, fg_color="transparent"); content_container.pack(expand=True, fill=ctk.X, padx=20, pady=(20,0))
        ctk.CTkLabel(content_container, text="📊 Thống Kê Người Chơi", font=self.fonts['title_large'], text_color=self.colors['primary']).pack(pady=(0, 15))
        ctk.CTkLabel(content_container, text="Thống Kê Chung", font=self.fonts['title_small'], text_color=self.colors['accent']).pack(pady=(10,5), anchor="w")
        stats_to_display = [("🔢", "Trò chơi đã thắng", self.user_stats.get("games_won_total", 0)), ("👍", "Thắng hoàn hảo", self.user_stats.get("perfect_wins_total", 0)), ("🏆", "Win Streak tốt nhất", self.user_stats.get("best_win_streak", 0))]
        for icon, text, value in stats_to_display: self._create_stat_item(content_container, icon, text, value)
        ctk.CTkFrame(content_container, height=1, fg_color=self.colors['outline']).pack(fill="x", padx=10, pady=(15, 10))
        ctk.CTkLabel(content_container, text="Thời Gian Tốt Nhất", font=self.fonts['title_small'], text_color=self.colors['accent']).pack(pady=(5,5), anchor="w")
        best_times = self.user_stats.get("best_times", {}); difficulty_map_display = {"very_easy": "Rất Dễ", "easy": "Dễ", "medium": "Trung Bình", "hard": "Khó", "expert": "Chuyên Gia"}
        for diff_key, display_name in difficulty_map_display.items(): self._create_stat_item(content_container, "⏱️", display_name, self._format_time(best_times.get(diff_key, float('inf'))))
        # Achievements section removed