import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from controllers.note_controller import NoteController
from controllers.search_controller import SearchController
from controllers.tag_controller import TagController
from controllers.task_controller import TaskController


class MainWindow:
    def __init__(self, master, app, on_new_note_callback, on_new_image_note_callback):
        self.master = master
        self.app = app
        self.on_new_note = on_new_note_callback
        self.on_new_image_note = on_new_image_note_callback
        self.task_ctrl = TaskController()
        self.tag_ctrl = TagController()
        self.search_ctrl = SearchController()
        self.note_ctrl = NoteController()

        # 排序状态
        self.sort_column = None  # 当前排序的列
        self.sort_reverse = False  # 是否降序

        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== 顶部区域 ==========
        top_frame = tk.Frame(self.frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # 第一行：按钮区域
        btn_frame = tk.Frame(top_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        # 便签下拉菜单
        self.note_menu_btn = tk.Menubutton(btn_frame, text="便签", width=12, relief=tk.RAISED)
        self.note_menu = tk.Menu(self.note_menu_btn, tearoff=0)
        self.note_menu.add_command(label="新建便签", command=self.new_note)
        self.note_menu.add_command(label="新建图片便签", command=self.new_image_note)
        self.note_menu.add_command(label="清空所有便签", command=self.clear_all_notes)
        self.note_menu.add_separator()
        self.note_menu.add_command(label="显示所有便签", command=self.show_all_notes)
        self.note_menu.add_command(label="隐藏所有便签", command=self.hide_all_notes)
        self.note_menu_btn.config(menu=self.note_menu)
        self.note_menu_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 任务下拉菜单
        self.task_menu_btn = tk.Menubutton(btn_frame, text="任务", width=12, relief=tk.RAISED)
        self.task_menu = tk.Menu(self.task_menu_btn, tearoff=0)
        self.task_menu.add_command(label="新建任务", command=self.new_task_dialog)
        self.task_menu.add_command(label="批量删除任务", command=self.batch_delete_tasks)
        self.task_menu.add_command(label="删除已完成任务", command=self.clear_completed_tasks)
        self.task_menu.add_command(label="删除已过期任务", command=self.delete_expired_tasks)
        self.task_menu_btn.config(menu=self.task_menu)
        self.task_menu_btn.pack(side=tk.LEFT)

        tk.Button(btn_frame, text="文本片段", command=self.open_snippets, width=12).pack(side=tk.LEFT, padx=(5, 0))

        # 移除原来的新建便签、新建任务、设置按钮，设置按钮可保留或移到别处，这里先保留设置按钮在右侧
        # 可选：添加一个“设置”按钮单独放在右边
        tk.Button(btn_frame, text="设置", command=self.open_settings, width=12).pack(side=tk.RIGHT, padx=(5, 0))

        # 第二行：搜索框
        search_frame = tk.Frame(top_frame)
        search_frame.pack(fill=tk.X)
        tk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # ========== 中间区域：任务列表 ==========
        # 创建Treeview - 移除编辑和删除列
        self.tree = ttk.Treeview(self.frame, columns=("id", "title", "priority", "due", "completed"), show="headings")

        # 设置表头并绑定点击排序事件
        self.tree.heading("id", text="ID", command=lambda: self.sort_by_column("id", False))
        self.tree.heading("title", text="任务", command=lambda: self.sort_by_column("title", False))
        self.tree.heading("priority", text="优先级(1-5)", command=lambda: self.sort_by_column("priority", False))
        self.tree.heading("due", text="截止日期", command=lambda: self.sort_by_column("due", False))
        self.tree.heading("completed", text="完成", command=lambda: self.sort_by_column("completed", False))

        # 设置列宽
        self.tree.column("id", width=50)
        self.tree.column("title", width=250)
        self.tree.column("priority", width=100)
        self.tree.column("due", width=150)
        self.tree.column("completed", width=80)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 绑定点击事件（用于切换完成状态）
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
        # 绑定右键菜单
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.refresh_task_list()

    def show_context_menu(self, event):
        """显示右键菜单"""
        # 获取点击位置的行
        item = self.tree.identify_row(event.y)
        if not item:
            return

        # 选中该行
        self.tree.selection_set(item)
        values = self.tree.item(item, "values")
        task_id = int(values[0])
        task_title = values[1]

        # 创建右键菜单
        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="编辑任务", command=lambda: self.edit_task(task_id))
        menu.add_separator()
        menu.add_command(label="删除任务", command=lambda: self.delete_task(task_id, task_title))

        # 显示菜单
        menu.post(event.x_root, event.y_root)

    def delete_task(self, task_id, task_title):
        """删除任务（带二次确认）"""
        if messagebox.askyesno("删除任务", f"确定要删除任务「{task_title}」吗？\n删除后无法恢复。"):
            self.task_ctrl.delete_task(task_id)
            self.refresh_task_list()

    def sort_by_column(self, col, reverse):
        """
        按指定列排序
        col: 列名 (id, title, priority, due, completed)
        reverse: 是否降序（True=降序，False=升序）
        """
        # 如果点击的是同一列，则切换排序方向
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = reverse

        # 获取所有任务
        tasks = self.task_ctrl.get_all_tasks()

        # 根据列排序
        if col == "id":
            tasks.sort(key=lambda x: x.id, reverse=self.sort_reverse)
        elif col == "title":
            tasks.sort(key=lambda x: x.title.lower(), reverse=self.sort_reverse)
        elif col == "priority":
            tasks.sort(key=lambda x: x.priority, reverse=self.sort_reverse)
        elif col == "due":
            # 处理空日期（None值排在最后）
            tasks.sort(key=lambda x: x.due_date if x.due_date else datetime.max, reverse=self.sort_reverse)
        elif col == "completed":
            tasks.sort(key=lambda x: x.is_completed, reverse=self.sort_reverse)

        # 刷新显示
        self.display_tasks(tasks)

        # 更新表头显示排序状态
        self.update_heading_style()

    def update_heading_style(self):
        """更新表头显示排序状态"""
        # 重置所有表头文本
        headings = {
            "id": "ID",
            "title": "任务",
            "priority": "优先级(1-5)",
            "due": "截止日期",
            "completed": "完成"
        }

        for col, text in headings.items():
            if self.sort_column == col:
                # 添加排序箭头
                arrow = " ▼" if self.sort_reverse else " ▲"
                self.tree.heading(col, text=text + arrow)
            else:
                self.tree.heading(col, text=text)

    def display_tasks(self, tasks):
        """显示任务列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for t in tasks:
            due_str = t.due_date.strftime("%Y-%m-%d %H:%M") if t.due_date else ""
            completed_str = "✓" if t.is_completed else "✗"
            # 根据优先级设置背景色（可选）
            tags = ()
            if t.priority == 1:
                tags = ('high_priority',)
            elif t.priority == 5:
                tags = ('low_priority',)

            self.tree.insert("", tk.END, values=(t.id, t.title, t.priority, due_str, completed_str), tags=tags)

        # 配置优先级颜色标签
        self.tree.tag_configure('high_priority', background='#FFE5E5')  # 高优先级浅红色背景
        self.tree.tag_configure('low_priority', background='#E5FFE5')  # 低优先级浅绿色背景

    def refresh_task_list(self):
        """刷新任务列表（保持当前排序）"""
        tasks = self.task_ctrl.get_all_tasks()

        # 如果有排序，则应用排序
        if self.sort_column:
            if self.sort_column == "id":
                tasks.sort(key=lambda x: x.id, reverse=self.sort_reverse)
            elif self.sort_column == "title":
                tasks.sort(key=lambda x: x.title.lower(), reverse=self.sort_reverse)
            elif self.sort_column == "priority":
                tasks.sort(key=lambda x: x.priority, reverse=self.sort_reverse)
            elif self.sort_column == "due":
                tasks.sort(key=lambda x: x.due_date if x.due_date else datetime.max, reverse=self.sort_reverse)
            elif self.sort_column == "completed":
                tasks.sort(key=lambda x: x.is_completed, reverse=self.sort_reverse)

        self.display_tasks(tasks)

    def open_settings(self):
        """打开设置窗口"""
        from ui.settings_dialog import SettingsDialog
        SettingsDialog(self.master, self.on_settings_changed, self.app.format_all_data)

    def on_settings_changed(self, settings):
        """设置改变时的回调"""
        pass

    def on_tree_click(self, event):
        """处理表格点击事件：完成列切换状态"""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        if not item:
            return
        values = self.tree.item(item, "values")
        task_id = int(values[0])

        # 列索引：#1 id, #2 title, #3 priority, #4 due, #5 completed
        if column == "#5":  # 完成列：切换完成状态
            self.task_ctrl.toggle_completed(task_id)
            self.refresh_task_list()

    def edit_task(self, task_id):
        """弹出编辑对话框，修改任务"""
        tasks = self.task_ctrl.get_all_tasks()
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            return

        dialog = tk.Toplevel(self.master)
        dialog.title("编辑任务")
        dialog.geometry("400x450")
        dialog.transient(self.master)
        dialog.grab_set()

        # 标题
        tk.Label(dialog, text="标题:", font=("微软雅黑", 10)).pack(pady=5)
        title_entry = tk.Entry(dialog, width=40, font=("微软雅黑", 10))
        title_entry.insert(0, task.title)
        title_entry.pack()

        # 描述
        tk.Label(dialog, text="描述:", font=("微软雅黑", 10)).pack(pady=5)
        desc_text = tk.Text(dialog, height=4, width=40, font=("微软雅黑", 10))
        desc_text.insert("1.0", task.description)
        desc_text.pack()

        # 优先级（数字 1-5）
        tk.Label(dialog, text="优先级 (1-5，1为最高):", font=("微软雅黑", 10)).pack(pady=5)
        priority_frame = tk.Frame(dialog)
        priority_frame.pack()
        priority_var = tk.IntVar(value=task.priority)
        for i in range(1, 6):
            tk.Radiobutton(priority_frame, text=str(i), variable=priority_var, value=i,
                           font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)

        # 截止日期 - 使用下拉选择框
        tk.Label(dialog, text="截止日期:", font=("微软雅黑", 10)).pack(pady=5)
        date_frame = tk.Frame(dialog)
        date_frame.pack(pady=5)

        # 年
        current_year = datetime.now().year
        year_var = tk.StringVar()
        year_combo = ttk.Combobox(date_frame, textvariable=year_var, width=6,
                                  values=[str(y) for y in range(current_year, current_year + 10)])
        year_combo.set(str(current_year))
        year_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="年", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 月
        month_var = tk.StringVar()
        month_combo = ttk.Combobox(date_frame, textvariable=month_var, width=4, values=[str(m) for m in range(1, 13)])
        month_combo.set("1")
        month_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="月", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 日
        day_var = tk.StringVar()
        day_combo = ttk.Combobox(date_frame, textvariable=day_var, width=4, values=[str(d) for d in range(1, 32)])
        day_combo.set("1")
        day_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="日", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 时
        hour_var = tk.StringVar()
        hour_combo = ttk.Combobox(date_frame, textvariable=hour_var, width=4, values=[str(h) for h in range(0, 24)])
        hour_combo.set("0")
        hour_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="时", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 分
        minute_var = tk.StringVar()
        minute_combo = ttk.Combobox(date_frame, textvariable=minute_var, width=4, values=[str(m) for m in range(0, 60)])
        minute_combo.set("0")
        minute_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="分", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 提前提醒（分钟）
        tk.Label(dialog, text="提前提醒（分钟）:", font=("微软雅黑", 10)).pack(pady=5)
        remind_frame = tk.Frame(dialog)
        remind_frame.pack()
        remind_var = tk.IntVar(value=task.remind_minutes)
        tk.Spinbox(remind_frame, from_=0, to=1440, textvariable=remind_var, width=10).pack(side=tk.LEFT)
        tk.Label(remind_frame, text="（0表示截止时间提醒）", font=("微软雅黑", 8)).pack(side=tk.LEFT, padx=5)

        # 如果有现有日期，填充到选择框
        if task.due_date:
            year_combo.set(str(task.due_date.year))
            month_combo.set(str(task.due_date.month))
            day_combo.set(str(task.due_date.day))
            hour_combo.set(str(task.due_date.hour))
            minute_combo.set(str(task.due_date.minute))

        def save():
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showerror("错误", "标题不能为空")
                return
            new_desc = desc_text.get("1.0", tk.END).strip()
            new_priority = priority_var.get()
            remind_minutes = remind_var.get()  # 获取提前提醒分钟数（新增）

            # 构建截止日期
            try:
                year = int(year_var.get())
                month = int(month_var.get())
                day = int(day_var.get())
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                new_due = datetime(year, month, day, hour, minute)
            except ValueError:
                new_due = None

            task.title = new_title
            task.description = new_desc
            task.priority = new_priority
            task.due_date = new_due
            task.remind_minutes = remind_minutes  # 保存提醒分钟数（新增）
            self.task_ctrl.update_task(task)
            self.refresh_task_list()
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save, width=15, font=("微软雅黑", 10)).pack(pady=10)

    def on_search(self, event):
        keyword = self.search_var.get()
        if not keyword:
            self.refresh_task_list()
            return
        notes, tasks = self.search_ctrl.search(keyword)
        self.display_tasks(tasks)

    def new_note(self):
        self.on_new_note()

    def new_task_dialog(self):
        """新建任务对话框 - 使用下拉选择日期时间"""
        dialog = tk.Toplevel(self.master)
        dialog.title("新建任务")
        dialog.geometry("400x400")
        dialog.transient(self.master)
        dialog.grab_set()

        # 标题
        tk.Label(dialog, text="标题:", font=("微软雅黑", 10)).pack(pady=5)
        title_entry = tk.Entry(dialog, width=40, font=("微软雅黑", 10))
        title_entry.pack()

        # 优先级（数字 1-5）
        tk.Label(dialog, text="优先级 (1-5，1为最高):", font=("微软雅黑", 10)).pack(pady=5)
        priority_frame = tk.Frame(dialog)
        priority_frame.pack()
        priority_var = tk.IntVar(value=3)  # 默认中优先级
        for i in range(1, 6):
            tk.Radiobutton(priority_frame, text=str(i), variable=priority_var, value=i,
                           font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)

        # 截止日期 - 使用下拉选择框
        tk.Label(dialog, text="截止日期 (可选):", font=("微软雅黑", 10)).pack(pady=5)
        date_frame = tk.Frame(dialog)
        date_frame.pack(pady=5)

        # 年
        current_year = datetime.now().year
        year_var = tk.StringVar()
        year_combo = ttk.Combobox(date_frame, textvariable=year_var, width=6,
                                  values=[str(y) for y in range(current_year, current_year + 10)])
        year_combo.set(str(current_year))
        year_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="年", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 月
        month_var = tk.StringVar()
        month_combo = ttk.Combobox(date_frame, textvariable=month_var, width=4, values=[str(m) for m in range(1, 13)])
        month_combo.set("1")
        month_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="月", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 日
        day_var = tk.StringVar()
        day_combo = ttk.Combobox(date_frame, textvariable=day_var, width=4, values=[str(d) for d in range(1, 32)])
        day_combo.set("1")
        day_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="日", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 时
        hour_var = tk.StringVar()
        hour_combo = ttk.Combobox(date_frame, textvariable=hour_var, width=4, values=[str(h) for h in range(0, 24)])
        hour_combo.set("0")
        hour_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="时", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 分
        minute_var = tk.StringVar()
        minute_combo = ttk.Combobox(date_frame, textvariable=minute_var, width=4, values=[str(m) for m in range(0, 60)])
        minute_combo.set("0")
        minute_combo.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="分", font=("微软雅黑", 10)).pack(side=tk.LEFT)

        # 提前提醒（分钟）
        tk.Label(dialog, text="提前提醒（分钟）:", font=("微软雅黑", 10)).pack(pady=5)
        remind_frame = tk.Frame(dialog)
        remind_frame.pack()
        remind_var = tk.IntVar(value=0)
        tk.Spinbox(remind_frame, from_=0, to=1440, textvariable=remind_var, width=10).pack(side=tk.LEFT)
        tk.Label(remind_frame, text="（0表示截止时间提醒）", font=("微软雅黑", 8)).pack(side=tk.LEFT, padx=5)

        def save():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("错误", "标题不能为空")
                return
            priority = priority_var.get()
            remind_minutes = remind_var.get()  # 移到外面，确保总是有值

            # 构建截止日期
            try:
                year = int(year_var.get())
                month = int(month_var.get())
                day = int(day_var.get())
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                due_date = datetime(year, month, day, hour, minute)
            except ValueError:
                due_date = None

            self.task_ctrl.create_task(title, priority=priority, due_date=due_date, remind_minutes=remind_minutes)
            self.refresh_task_list()
            dialog.destroy()

        tk.Button(dialog, text="保存", command=save, width=15, font=("微软雅黑", 10)).pack(pady=10)

    def clear_all_notes(self):
        """清空所有便签（包括文本便签和图片便签）"""
        if messagebox.askyesno("清空便签", "确定要清空所有便签吗？\n此操作不可恢复。"):
            # 清空文本便签数据
            self.note_ctrl.delete_all_notes()
            # 清空图片便签数据
            self.app.image_note_ctrl.delete_all_image_notes()
            # 关闭所有已打开的文本便签窗口
            if hasattr(self.app, 'note_windows'):
                for note_id, win in list(self.app.note_windows.items()):
                    win.window.destroy()
                self.app.note_windows.clear()
            # 关闭所有已打开的图片便签窗口
            if hasattr(self.app, 'image_note_windows'):
                for note_id, win in list(self.app.image_note_windows.items()):
                    win.window.destroy()
                self.app.image_note_windows.clear()
            messagebox.showinfo("完成", "所有便签已清空")

    def show_all_notes(self):
        """显示所有便签窗口（包括文本便签和图片便签）"""
        # 显示文本便签
        if hasattr(self.app, 'note_windows'):
            for win in self.app.note_windows.values():
                try:
                    win.window.deiconify()
                except:
                    pass
        # 显示图片便签
        if hasattr(self.app, 'image_note_windows'):
            for win in self.app.image_note_windows.values():
                try:
                    win.window.deiconify()
                except:
                    pass

    def hide_all_notes(self):
        """隐藏所有便签窗口（包括文本便签和图片便签）"""
        # 隐藏文本便签
        if hasattr(self.app, 'note_windows'):
            for win in self.app.note_windows.values():
                try:
                    win.window.withdraw()
                except:
                    pass
        # 隐藏图片便签
        if hasattr(self.app, 'image_note_windows'):
            for win in self.app.image_note_windows.values():
                try:
                    win.window.withdraw()
                except:
                    pass

    def batch_delete_tasks(self):
        """批量删除任务：带复选框列表，支持全选"""
        tasks = self.task_ctrl.get_all_tasks()
        if not tasks:
            messagebox.showinfo("提示", "没有任务可删除")
            return

        # 创建对话框
        dialog = tk.Toplevel(self.master)
        dialog.title("批量删除任务")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        dialog.grab_set()

        # 全选变量
        select_all_var = tk.BooleanVar(value=False)

        # 顶部全选框
        top_frame = tk.Frame(dialog)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Checkbutton(top_frame, text="全选", variable=select_all_var,
                       command=lambda: toggle_all()).pack(anchor=tk.W)

        # 创建带滚动条的画布
        canvas = tk.Canvas(dialog)
        scrollbar = tk.Scrollbar(dialog, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 存储每个任务的复选框变量
        check_vars = {}
        for task in tasks:
            var = tk.BooleanVar(value=False)
            check_vars[task.id] = var
            due_str = task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else "无截止日期"
            text = f"ID:{task.id}  {task.title} (优先级:{task.priority}) 截止:{due_str}"
            cb = tk.Checkbutton(scrollable_frame, text=text, variable=var, anchor="w", justify=tk.LEFT)
            cb.pack(fill=tk.X, pady=2)

        def toggle_all():
            """全选/取消全选"""
            for var in check_vars.values():
                var.set(select_all_var.get())

        def do_delete():
            selected_ids = [tid for tid, var in check_vars.items() if var.get()]
            if not selected_ids:
                messagebox.showwarning("警告", "请至少选择一个任务")
                return
            if messagebox.askyesno("确认删除", f"确定要删除 {len(selected_ids)} 个任务吗？\n此操作不可恢复。"):
                for tid in selected_ids:
                    self.task_ctrl.delete_task(tid)
                self.refresh_task_list()
                dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="删除选中", command=do_delete, width=12).pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_frame, text="取消", command=dialog.destroy, width=12).pack(side=tk.RIGHT, padx=5)

    def clear_completed_tasks(self):
        """清空所有已完成的任务"""
        if messagebox.askyesno("删除已完成任务", "确定要删除所有已完成的任务吗？"):
            tasks = self.task_ctrl.get_all_tasks()
            deleted = 0
            for task in tasks:
                if task.is_completed:
                    self.task_ctrl.delete_task(task.id)
                    deleted += 1
            self.refresh_task_list()
            messagebox.showinfo("完成", f"已删除 {deleted} 个已完成任务")

    def delete_expired_tasks(self):
        """删除所有已过期的任务（截止日期早于当前时间）"""
        tasks = self.task_ctrl.get_all_tasks()
        now = datetime.now()
        expired = [task for task in tasks if task.due_date and task.due_date < now]

        if not expired:
            messagebox.showinfo("提示", "没有已过期的任务")
            return

        msg = f"找到 {len(expired)} 个已过期任务，确定要全部删除吗？\n\n"
        for task in expired[:5]:  # 预览前5个
            msg += f"• {task.title} (截止: {task.due_date.strftime('%Y-%m-%d %H:%M')})\n"
        if len(expired) > 5:
            msg += f"... 等共 {len(expired)} 个"

        if messagebox.askyesno("删除过期任务", msg):
            for task in expired:
                self.task_ctrl.delete_task(task.id)
            self.refresh_task_list()
            messagebox.showinfo("完成", f"已删除 {len(expired)} 个过期任务")

    def new_image_note(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"), ("所有文件", "*.*")]
        )
        if file_path:
            self.on_new_image_note(file_path)

    def open_snippets(self):
        from ui.snippets_window import SnippetsWindow
        SnippetsWindow(self.master)