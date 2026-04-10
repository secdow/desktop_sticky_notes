import tkinter as tk
from tkinter import messagebox
from utils.auto_start import AutoStart
from storage.file_storage import FileStorageManager

class SettingsDialog:
    def __init__(self, master):
        self.master = master
        self.storage = FileStorageManager()
        self.settings = self.storage.load("settings")
        self.dialog = tk.Toplevel(master)
        self.dialog.title("设置")
        self.dialog.geometry("300x200")
        self.dialog.transient(master)
        self.dialog.grab_set()

        # 开机自启
        self.auto_start_var = tk.BooleanVar(value=self.settings.get("auto_start", False))
        tk.Checkbutton(self.dialog, text="开机自启动", variable=self.auto_start_var).pack(anchor="w", padx=20, pady=10)

        # 提醒间隔
        frame = tk.Frame(self.dialog)
        frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(frame, text="提醒扫描间隔(秒):").pack(side=tk.LEFT)
        self.interval_var = tk.IntVar(value=self.settings.get("reminder_interval_seconds", 30))
        tk.Spinbox(frame, from_=10, to=300, textvariable=self.interval_var, width=6).pack(side=tk.LEFT, padx=5)

        # 保存按钮
        tk.Button(self.dialog, text="保存", command=self.save_settings).pack(pady=20)

    def save_settings(self):
        self.settings["auto_start"] = self.auto_start_var.get()
        self.settings["reminder_interval_seconds"] = self.interval_var.get()
        self.storage.save("settings", self.settings)
        # 设置开机自启
        AutoStart.set(self.settings["auto_start"])
        messagebox.showinfo("成功", "设置已保存，部分设置需重启应用生效")
        self.dialog.destroy()