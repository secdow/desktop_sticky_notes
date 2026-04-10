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

        # 创建窗口
        self.window = tk.Toplevel()
        self.window.title(note.title or "便签")
        self.window.geometry(f"{note.width}x{note.height}+{note.x}+{note.y}")
        self.window.configure(bg=self.COLORS.get(note.color, "#FFFFCC"))
        if note.is_topmost:
            self.window.attributes("-topmost", True)

        # 顶部工具栏：放置置顶复选框和颜色按钮（可选）
        self.toolbar = tk.Frame(self.window, bg=self.COLORS.get(note.color, "#FFFFCC"))
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)

        # 置顶复选框（第一眼可见）
        self.topmost_var = tk.BooleanVar(value=note.is_topmost)
        self.topmost_cb = tk.Checkbutton(
            self.toolbar,
            text="置顶",
            variable=self.topmost_var,
            command=self.toggle_topmost,
            bg=self.COLORS.get(note.color, "#FFFFCC"),
            activebackground=self.COLORS.get(note.color, "#FFFFCC")
        )
        self.topmost_cb.pack(side=tk.LEFT, padx=5)

        # 可选：添加一个颜色快捷按钮（快速切换颜色）
        self.color_btn = tk.Menubutton(self.toolbar, text="颜色", relief=tk.RAISED,
                                       bg=self.COLORS.get(note.color, "#FFFFCC"))
        self.color_menu = tk.Menu(self.color_btn, tearoff=0)
        for color_name in self.COLORS:
            self.color_menu.add_command(label=color_name, command=lambda c=color_name: self.change_color(c))
        self.color_btn.config(menu=self.color_menu)
        self.color_btn.pack(side=tk.LEFT, padx=5)

        # 文本编辑区域
        self.text = tk.Text(self.window, wrap=tk.WORD, bg=self.COLORS[note.color], font=("微软雅黑", 10))
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text.insert("1.0", note.content)
        self.text.bind("<KeyRelease>", self.auto_save)

        # 右键菜单（仅保留颜色选项，因为置顶已有可见控件，删除选项已移除）
        self.create_context_menu()

        # 绑定关闭事件（点击 X）
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def create_context_menu(self):
        """右键菜单只包含颜色切换（可选，如果觉得工具栏的颜色按钮已够用，可以完全去掉右键菜单）"""
        self.menu = tk.Menu(self.window, tearoff=0)
        color_menu = tk.Menu(self.menu, tearoff=0)
        for color_name in self.COLORS:
            color_menu.add_command(label=color_name, command=lambda c=color_name: self.change_color(c))
        self.menu.add_cascade(label="颜色", menu=color_menu)
        self.window.bind("<Button-3>", self.show_menu)

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def toggle_topmost(self):
        """切换置顶状态（由复选框触发）"""
        is_topmost = self.topmost_var.get()
        self.window.attributes("-topmost", is_topmost)
        self.note.is_topmost = is_topmost
        self.controller.update_note(self.note)

    def change_color(self, color_name):
        """更改便签背景颜色"""
        self.note.color = color_name
        new_bg = self.COLORS[color_name]
        self.window.configure(bg=new_bg)
        self.toolbar.configure(bg=new_bg)
        self.topmost_cb.configure(bg=new_bg, activebackground=new_bg)
        self.color_btn.configure(bg=new_bg)
        self.text.configure(bg=new_bg)
        self.controller.update_note(self.note)

    def auto_save(self, event=None):
        """自动保存便签内容、位置和大小"""
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

    def close(self):
        """点击 X 关闭按钮时弹出确认删除对话框"""
        if messagebox.askyesno("删除便签", "确定要删除此便签吗？\n删除后无法恢复。"):
            self.auto_save()
            self.controller.delete_note(self.note.id)
            self.window.destroy()
            self.on_close(self.note.id)