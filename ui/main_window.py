import tkinter as tk
from tkinter import ttk, messagebox
from controllers.task_controller import TaskController
from controllers.tag_controller import TagController
from controllers.search_controller import SearchController
from datetime import datetime


class MainWindow:
    def __init__(self, master, on_new_note_callback):
        self.master = master
        self.on_new_note = on_new_note_callback
        self.task_ctrl = TaskController()
        self.tag_ctrl = TagController()
        self.search_ctrl = SearchController()

        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 搜索框
        search_frame = tk.Frame(self.frame)
        search_frame.pack(fill=tk.X, pady=5)
        tk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # 待办列表：列包括 id, title, priority, due, completed(可点击), edit, delete
        self.tree = ttk.Treeview(self.frame, columns=("id", "title", "priority", "due", "completed", "edit", "delete"),
                                 show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="任务")
        self.tree.heading("priority", text="优先级")
        self.tree.heading("due", text="截止日期")
        self.tree.heading("completed", text="完成")
        self.tree.heading("edit", text="编辑")
        self.tree.heading("delete", text="删除")
        self.tree.column("id", width=40)
        self.tree.column("title", width=180)
        self.tree.column("priority", width=60)
        self.tree.column("due", width=120)
        self.tree.column("completed", width=60)
        self.tree.column("edit", width=50)
        self.tree.column("delete", width=50)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

        # 按钮区域：只保留新建便签和新建任务，移除“切换完成”按钮
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="新建便签", command=self.new_note).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="新建任务", command=self.new_task_dialog).pack(side=tk.LEFT, padx=2)

        self.refresh_task_list()

    def refresh_task_list(self):
        """刷新任务列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        tasks = self.task_ctrl.get_all_tasks()
        priority_map = {0: "低", 1: "中", 2: "高"}
        for t in tasks:
            due_str = t.due_date.strftime("%Y-%m-%d %H:%M") if t.due_date else ""
            completed_str = "✓" if t.is_completed else "✗"
            self.tree.insert("", tk.END, values=(
            t.id, t.title, priority_map.get(t.priority, "中"), due_str, completed_str, "编辑", "删除"))

    def on_tree_click(self, event):
        """处理表格点击事件：完成列切换状态，编辑列打开编辑对话框，删除列二次确认删除"""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        if not item:
            return
        values = self.tree.item(item, "values")
        task_id = int(values[0])
        task_title = values[1]

        # 列索引：#1 id, #2 title, #3 priority, #4 due, #5 completed, #6 edit, #7 delete
        if column == "#5":  # 完成列：切换完成状态
            self.task_ctrl.toggle_completed(task_id)
            self.refresh_task_list()
        elif column == "#6":  # 编辑列
            self.edit_task(task_id)
        elif column == "#7":  # 删除列
            if messagebox.askyesno("删除任务", f"确定要删除任务「{task_title}」吗？\n删除后无法恢复。"):
                self.task_ctrl.delete_task(task_id)
                self.refresh_task_list()

    def edit_task(self, task_id):
        """弹出编辑对话框，修改任务"""
        tasks = self.task_ctrl.get_all_tasks()
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            return

        dialog = tk.Toplevel(self.master)
        dialog.title("编辑任务")
        dialog.geometry("350x320")
        dialog.transient(self.master)
        dialog.grab_set()

        tk.Label(dialog, text="标题:").pack(pady=5)
        title_entry = tk.Entry(dialog, width=40)
        title_entry.insert(0, task.title)
        title_entry.pack()

        tk.Label(dialog, text="描述:").pack(pady=5)
        desc_text = tk.Text(dialog, height=4, width=40)
        desc_text.insert("1.0", task.description)
        desc_text.pack()

        tk.Label(dialog, text="优先级:").pack(pady=5)
        priority_var = tk.IntVar(value=task.priority)
        frame = tk.Frame(dialog)
        frame.pack()
        tk.Radiobutton(frame, text="低", variable=priority_var, value=0).pack(side=tk.LEFT)
        tk.Radiobutton(frame, text="中", variable=priority_var, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(frame, text="高", variable=priority_var, value=2).pack(side=tk.LEFT)

        tk.Label(dialog, text="截止日期 (YYYY-MM-DD HH:MM):").pack(pady=5)
        due_entry = tk.Entry(dialog, width=30)
        if task.due_date:
            due_entry.insert(0, task.due_date.strftime("%Y-%m-%d %H:%M"))
        due_entry.pack()

        def save():
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showerror("错误", "标题不能为空")
                return
            new_desc = desc_text.get("1.0", tk.END).strip()
            new_priority = priority_var.get()
            due_str = due_entry.get().strip()
            new_due = None
            if due_str:
                try:
                    new_due = datetime.strptime(due_str, "%Y-%m-%d %H:%M")
                except:
                    messagebox.showerror("错误", "日期格式错误，请使用 YYYY-MM-DD HH:MM")
                    return
            task.title = new_title
            task.description = new_desc
            task.priority = new_priority
            task.due_date = new_due
            self.task_ctrl.update_task(task)
            self.refresh_task_list()
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save).pack(pady=10)

    def on_search(self, event):
        keyword = self.search_var.get()
        if not keyword:
            self.refresh_task_list()
            return
        notes, tasks = self.search_ctrl.search(keyword)
        for item in self.tree.get_children():
            self.tree.delete(item)
        priority_map = {0: "低", 1: "中", 2: "高"}
        for t in tasks:
            due_str = t.due_date.strftime("%Y-%m-%d %H:%M") if t.due_date else ""
            completed_str = "✓" if t.is_completed else "✗"
            self.tree.insert("", tk.END, values=(
            t.id, t.title, priority_map.get(t.priority, "中"), due_str, completed_str, "编辑", "删除"))

    def new_note(self):
        self.on_new_note()

    def new_task_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("新建任务")
        dialog.geometry("300x250")
        tk.Label(dialog, text="标题:").pack(pady=5)
        title_entry = tk.Entry(dialog, width=30)
        title_entry.pack()
        tk.Label(dialog, text="优先级:").pack(pady=5)
        priority_var = tk.IntVar(value=1)
        frame = tk.Frame(dialog)
        frame.pack()
        tk.Radiobutton(frame, text="低", variable=priority_var, value=0).pack(side=tk.LEFT)
        tk.Radiobutton(frame, text="中", variable=priority_var, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(frame, text="高", variable=priority_var, value=2).pack(side=tk.LEFT)
        tk.Label(dialog, text="截止日期 (YYYY-MM-DD HH:MM):").pack(pady=5)
        due_entry = tk.Entry(dialog, width=30)
        due_entry.pack()

        def save():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("错误", "标题不能为空")
                return
            due_str = due_entry.get().strip()
            due_date = None
            if due_str:
                try:
                    due_date = datetime.strptime(due_str, "%Y-%m-%d %H:%M")
                except:
                    messagebox.showerror("错误", "日期格式错误，请使用 YYYY-MM-DD HH:MM")
                    return
            self.task_ctrl.create_task(title, priority=priority_var.get(), due_date=due_date)
            self.refresh_task_list()
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save).pack(pady=10)