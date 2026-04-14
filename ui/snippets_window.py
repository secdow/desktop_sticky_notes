import tkinter as tk
from tkinter import ttk, messagebox
from controllers.snippets_controller import SnippetsController

class SnippetsWindow:
    def __init__(self, master):
        self.master = master
        self.controller = SnippetsController()
        self.window = tk.Toplevel(master)
        self.window.title("文本片段管理器")
        self.window.geometry("600x400")

        # 搜索框
        top_frame = tk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(top_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(top_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # 按钮
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btn_frame, text="新建片段", command=self.new_snippet).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="删除选中", command=self.delete_selected).pack(side=tk.LEFT, padx=2)

        # 片段列表（Treeview）
        self.tree = ttk.Treeview(self.window, columns=("name", "mtime"), show="headings")
        self.tree.heading("name", text="片段名称")
        self.tree.heading("mtime", text="最后修改")
        self.tree.column("name", width=250)
        self.tree.column("mtime", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree.bind("<Double-Button-1>", self.on_double_click)
        self.tree.bind("<Delete>", self.delete_selected)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.refresh_list()

    def refresh_list(self, filter_text=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        snippets = self.controller.list_snippets()
        if filter_text:
            filter_lower = filter_text.lower()
            snippets = [s for s in snippets if filter_lower in s["name"].lower()]
        for s in snippets:
            self.tree.insert("", tk.END, values=(s["name"], s["mtime"]))

    def on_search(self, event):
        self.refresh_list(self.search_var.get())

    def new_snippet(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("新建片段")
        dialog.geometry("400x300")
        tk.Label(dialog, text="片段名称:").pack(pady=5)
        name_entry = tk.Entry(dialog, width=40)
        name_entry.pack()
        tk.Label(dialog, text="内容:").pack(pady=5)
        text_area = tk.Text(dialog, wrap=tk.WORD, height=10)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("错误", "名称不能为空")
                return
            content = text_area.get("1.0", tk.END).rstrip("\n")
            self.controller.save_snippet(name, content)
            self.refresh_list(self.search_var.get())
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save).pack(pady=10)

    def edit_snippet(self, name):
        content = self.controller.get_snippet_content(name)
        dialog = tk.Toplevel(self.window)
        dialog.title(f"编辑片段 - {name}")
        dialog.geometry("500x400")
        tk.Label(dialog, text="内容:").pack(pady=5)
        text_area = tk.Text(dialog, wrap=tk.WORD, height=20)
        text_area.insert("1.0", content)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def save():
            new_content = text_area.get("1.0", tk.END).rstrip("\n")
            self.controller.save_snippet(name, new_content)
            self.refresh_list(self.search_var.get())
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save).pack(pady=10)

    def delete_selected(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        name = item["values"][0]
        if messagebox.askyesno("删除", f"确定删除片段「{name}」吗？"):
            self.controller.delete_snippet(name)
            self.refresh_list(self.search_var.get())

    def on_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        name = item["values"][0]
        self.edit_snippet(name)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self.tree.selection_set(item)
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="编辑", command=lambda: self.on_double_click(None))
        menu.add_command(label="删除", command=self.delete_selected)
        menu.post(event.x_root, event.y_root)