import tkinter as tk
from tkinter import ttk, messagebox

from storage.file_storage import FileStorageManager
from utils.auto_start import AutoStart


class SettingsDialog:
    def __init__(self, master, on_settings_changed=None, on_format_callback=None):
        self.master = master
        self.on_settings_changed = on_settings_changed
        self.on_format_callback = on_format_callback
        self.storage = FileStorageManager()
        self.settings = self.storage.load("settings")

        self.dialog = tk.Toplevel(master)
        self.dialog.title("设置")
        self.dialog.geometry("450x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(master)
        self.dialog.grab_set()

        # 创建Notebook标签页
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 通用设置页
        self.create_general_tab()

        # 按钮区域
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="保存", command=self.save_settings, width=10).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="取消", command=self.dialog.destroy, width=10).pack(side=tk.RIGHT, padx=5)

    def create_general_tab(self):
        """通用设置标签页"""
        general_frame = tk.Frame(self.notebook)
        self.notebook.add(general_frame, text="通用")

        # 开机自启动
        frame1 = tk.Frame(general_frame)
        frame1.pack(fill=tk.X, padx=20, pady=15)

        self.auto_start_var = tk.BooleanVar(value=self.settings.get("auto_start", False))
        tk.Checkbutton(frame1, text="开机自启动", variable=self.auto_start_var,
                       font=("微软雅黑", 10)).pack(anchor="w")

        tk.Label(frame1, text="开启后，软件会在系统启动时自动运行",
                 font=("微软雅黑", 8), fg="gray").pack(anchor="w", padx=20)

        # 提醒间隔
        frame2 = tk.Frame(general_frame)
        frame2.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(frame2, text="提醒扫描间隔:", font=("微软雅黑", 10)).pack(anchor="w")
        interval_frame = tk.Frame(frame2)
        interval_frame.pack(anchor="w", pady=5)

        self.interval_var = tk.IntVar(value=self.settings.get("reminder_interval_seconds", 30))
        tk.Spinbox(interval_frame, from_=10, to=300, textvariable=self.interval_var,
                   width=10, font=("微软雅黑", 10)).pack(side=tk.LEFT)
        tk.Label(interval_frame, text="秒", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)

        # 格式化数据按钮
        frame4 = tk.Frame(general_frame)
        frame4.pack(fill=tk.X, padx=20, pady=30)
        tk.Button(frame4, text="格式化数据（清空所有数据）", command=self.format_data,
                  bg="#FF4444", fg="white", width=25).pack()

    def format_data(self):
        """格式化数据：清空所有数据"""
        if messagebox.askyesno("警告", "格式化将清空所有数据（包括便签、任务、图片等），且不可恢复！\n\n确定要继续吗？"):
            if self.on_format_callback:
                self.on_format_callback()
            # 如果没有回调，什么也不做（或打印警告）

    def save_settings(self):
        """保存设置"""
        # 保存通用设置
        self.settings["auto_start"] = self.auto_start_var.get()
        self.settings["reminder_interval_seconds"] = self.interval_var.get()

        # 保存到文件
        self.storage.save("settings", self.settings)

        # 设置开机自启动
        AutoStart.set(self.settings["auto_start"])

        # 通知主程序设置已更改
        if self.on_settings_changed:
            self.on_settings_changed(self.settings)

        messagebox.showinfo("成功", "设置已保存！\n部分设置需要重启程序才能生效。")
        self.dialog.destroy()