import tkinter as tk
from tkinter import messagebox

from controllers.note_controller import NoteController
from models.entities import Note


class StickyNote:
    COLORS = {
        "yellow": "#FFFFCC",
        "blue": "#CCE5FF",
        "green": "#CCFFCC",
        "pink": "#FFCCFF"
    }

    def __init__(self, note: Note, on_close_callback):
        self.note = note
        self.on_close = on_close_callback
        self.controller = NoteController()

        self.window = tk.Toplevel()
        self.window.title(note.title or "便签")
        self.window.geometry(f"{note.width}x{note.height}+{note.x}+{note.y}")
        self.window.configure(bg=self.COLORS.get(note.color, "#FFFFCC"))
        if note.is_topmost:
            self.window.attributes("-topmost", True)

        self.text = tk.Text(self.window, wrap=tk.WORD, bg=self.COLORS[note.color], font=("微软雅黑", 10))
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text.insert("1.0", note.content)
        self.text.bind("<KeyRelease>", self.auto_save)

        self.create_context_menu()
        self.window.bind("<Button-3>", self.show_menu)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def create_context_menu(self):
        self.menu = tk.Menu(self.window, tearoff=0)
        # 动态置顶/取消置顶项
        self.topmost_item_index = 0
        self.menu.add_command(label="", command=self.toggle_topmost)
        self.update_topmost_menu_text()

        self.menu.add_separator()
        color_menu = tk.Menu(self.menu, tearoff=0)
        for color_name in self.COLORS:
            color_menu.add_command(label=color_name, command=lambda c=color_name: self.change_color(c))
        self.menu.add_cascade(label="颜色", menu=color_menu)
        self.menu.add_separator()
        self.menu.add_command(label="删除便签", command=self.delete_note)

    def update_topmost_menu_text(self):
        if self.window.attributes("-topmost"):
            self.menu.entryconfig(self.topmost_item_index, label="取消置顶")
        else:
            self.menu.entryconfig(self.topmost_item_index, label="置顶")

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def toggle_topmost(self):
        current = self.window.attributes("-topmost")
        self.window.attributes("-topmost", not current)
        self.note.is_topmost = not current
        self.controller.update_note(self.note)
        self.update_topmost_menu_text()

    def change_color(self, color_name):
        self.note.color = color_name
        self.window.configure(bg=self.COLORS[color_name])
        self.text.configure(bg=self.COLORS[color_name])
        self.controller.update_note(self.note)

    def auto_save(self, event=None):
        content = self.text.get("1.0", tk.END).rstrip("\n")
        self.note.content = content
        title = content.split("\n")[0][:20] if content else "便签"
        self.window.title(title)
        self.note.title = title

        self.note.x = self.window.winfo_x()
        self.note.y = self.window.winfo_y()
        self.note.width = self.window.winfo_width()
        self.note.height = self.window.winfo_height()
        self.controller.update_note(self.note)

    def delete_note(self):
        if messagebox.askyesno("删除便签", "确定要删除此便签吗？\n删除后无法恢复。"):
            self.controller.delete_note(self.note.id)
            self.window.destroy()
            self.on_close(self.note.id)

    def close(self):
        self.auto_save()
        self.window.destroy()
        self.on_close(self.note.id)