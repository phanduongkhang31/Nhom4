import tkinter as tk
from tkinter import messagebox

FONT_CELL = ("Segoe UI", 16)
FONT_BTN = ("Segoe UI", 12)
COLOR_BG = "#f8f9fa"
COLOR_CELL_BG = "white"
COLOR_CELL_SELECTED = "#cce5ff"
COLOR_CELL_FIXED = "#dee2e6"
COLOR_GRID_BORDER = "#adb5bd"
COLOR_BTN = "#0d6efd"
COLOR_BTN_TEXT = "white"
COLOR_BTN_HOVER = "#0b5ed7"
COLOR_ERASE = "#dc3545"
COLOR_ERASE_HOVER = "#bb2d3b"

class SudokuCell(tk.Label):
    def __init__(self, master, ui, r, c):
        super().__init__(master, width=4, height=2, borderwidth=1, relief="solid", font=FONT_CELL, bg=COLOR_CELL_BG, anchor="center")
        self.ui = ui
        self.r = r
        self.c = c
        self.value = 0
        self.fixed = False
        self.selected = False
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        self.ui.select_cell(self.r, self.c)

    def set_value(self, val, fixed=False):
        self.value = val
        self.fixed = fixed
        self.update_display()

    def update_display(self):
        self.config(text=str(self.value) if self.value != 0 else "")
        if self.selected:
            self.config(bg=COLOR_CELL_SELECTED)
        elif self.fixed:
            self.config(bg=COLOR_CELL_FIXED)
        else:
            self.config(bg=COLOR_CELL_BG)

class SudokuUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG)
        self.grid_cells = []
        self.selected_cell = None
        self.board_data = [[0]*9 for _ in range(9)]
        self.fixed_mask = [[False]*9 for _ in range(9)]
        self.create_widgets()
        self.pack(padx=10, pady=10)

    def create_widgets(self):
        grid_frame = tk.Frame(self, bg=COLOR_GRID_BORDER, padx=2, pady=2)
        grid_frame.pack(pady=10)

        for r in range(9):
            row_cells = []
            for c in range(9):
                cell_frame = tk.Frame(
                    grid_frame,
                    bg=COLOR_GRID_BORDER,
                    highlightthickness=1,
                    highlightbackground=COLOR_GRID_BORDER
                )
                # Thêm padding lớn giữa các nhóm 3x3
                padx = (2 if c % 3 == 0 else 0)
                pady = (2 if r % 3 == 0 else 0)
                cell_frame.grid(row=r, column=c, padx=(padx, 1), pady=(pady, 1))

                cell = SudokuCell(cell_frame, self, r, c)
                cell.pack()
                row_cells.append(cell)
            self.grid_cells.append(row_cells)

        btn_frame = tk.Frame(self, bg=COLOR_BG)
        btn_frame.pack(pady=5)

        for num in range(1, 10):
            b = tk.Button(
                btn_frame, text=str(num), width=4, height=1, font=FONT_BTN,
                bg=COLOR_BTN, fg=COLOR_BTN_TEXT, relief="flat",
                command=lambda n=num: self.input_number(n)
            )
            b.grid(row=0, column=num-1, padx=3, pady=3)
            b.bind("<Enter>", lambda e, b=b: b.config(bg=COLOR_BTN_HOVER))
            b.bind("<Leave>", lambda e, b=b: b.config(bg=COLOR_BTN))

        erase_btn = tk.Button(
            self, text="🗑️ Xóa số", width=10, font=FONT_BTN,
            bg=COLOR_ERASE, fg="white", relief="flat",
            command=self.erase_selected
        )
        erase_btn.pack(pady=8)
        erase_btn.bind("<Enter>", lambda e: erase_btn.config(bg=COLOR_ERASE_HOVER))
        erase_btn.bind("<Leave>", lambda e: erase_btn.config(bg=COLOR_ERASE))

    def select_cell(self, r, c):
        if self.selected_cell:
            pr, pc = self.selected_cell
            self.grid_cells[pr][pc].selected = False
            self.grid_cells[pr][pc].update_display()

        self.selected_cell = (r, c)
        self.grid_cells[r][c].selected = True
        self.grid_cells[r][c].update_display()

    def input_number(self, num):
        if not self.selected_cell:
            messagebox.showwarning("Thông báo", "Vui lòng chọn một ô trước khi nhập số.")
            return
        r, c = self.selected_cell
        if self.fixed_mask[r][c]:
            messagebox.showwarning("Thông báo", "Không thể thay đổi ô số cố định.")
            return
        self.board_data[r][c] = num
        self.grid_cells[r][c].set_value(num)

    def erase_selected(self):
        if not self.selected_cell:
            return
        r, c = self.selected_cell
        if self.fixed_mask[r][c]:
            return
        self.board_data[r][c] = 0
        self.grid_cells[r][c].set_value(0)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sudoku - Giao Diện Hiện Đại 🎯")
    root.configure(bg=COLOR_BG)
    root.resizable(False, False)
    app = SudokuUI(root)
    root.mainloop()
