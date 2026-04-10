import tkinter as tk
from tkinter import messagebox
import threading
import sys
from storage.file_storage import FileStorageManager
from controllers.note_controller import NoteController
from controllers.reminder_controller import ReminderController
from ui.main_window import MainWindow
from ui.sticky_note import StickyNote
from utils.tray_manager import TrayManager
from utils.hotkey_manager import HotkeyManager
from utils.logger import setup_logger

class App:
    def __init__(self):
        self.logger = setup_logger()
        self.storage = FileStorageManager()
        self.note_ctrl = NoteController()
        self.root = tk.Tk()
        self.root.title("桌面便签")
        self.root.geometry("500x400")
        self.root.minsize(500, 400)
        self.root.protocol("WM_DELETE_WINDOW", self.on_main_window_close)

        # 主窗口
        self.main_window = MainWindow(self.root, self.create_new_note)

        # 托盘
        self.tray = TrayManager(self.create_new_note, self.toggle_main_window, self.quit_app)

        # 热键
        self.hotkey_mgr = HotkeyManager()
        settings = self.storage.load("settings")
        new_note_hk = settings.get("hotkey_new_note", "ctrl+shift+n")
        show_hide_hk = settings.get("hotkey_show_hide", "ctrl+shift+h")
        self.hotkey_mgr.register(new_note_hk, self.create_new_note)
        self.hotkey_mgr.register(show_hide_hk, self.toggle_main_window)

        # 提醒线程
        self.reminder_ctrl = ReminderController(self.show_reminder_notification)
        self.reminder_ctrl.start()

        # 加载已有的便签
        self.load_existing_notes()

        # 启动托盘（单独线程）
        self.tray_thread = threading.Thread(target=self.tray.run, daemon=True)
        self.tray_thread.start()

    def load_existing_notes(self):
        notes = self.note_ctrl.get_all_notes()
        self.note_windows = {}
        for note in notes:
            win = StickyNote(note, self.on_note_closed)
            self.note_windows[note.id] = win

    def create_new_note(self):
        note = self.note_ctrl.create_note()
        win = StickyNote(note, self.on_note_closed)
        self.note_windows[note.id] = win

    def on_note_closed(self, note_id):
        if note_id in self.note_windows:
            del self.note_windows[note_id]

    def toggle_main_window(self):
        if self.root.state() == "withdrawn":
            self.root.deiconify()
            self.root.lift()
        else:
            self.root.withdraw()

    def on_main_window_close(self):
        if messagebox.askyesno("退出", "是否保留当前便签？\n选择“是”将保留所有便签数据，下次启动恢复。\n选择“否”将删除所有便签数据。"):
            # 保留数据，直接退出
            self.quit_app()
        else:
            # 删除所有便签数据
            self.delete_all_data()
            self.quit_app()

    def delete_all_data(self):
        # 清空 notes.json
        notes_data = {"next_id": 1, "notes": []}
        self.storage.save("notes", notes_data)
        # 清空 tasks.json
        tasks_data = {"next_id": 1, "tasks": []}

        self.storage.save("tasks", tasks_data)
        # 清空 tags.json
        tags_data = {"next_id": 1, "tags": []}
        self.storage.save("tags", tags_data)
        # 清空 reminders.json
        reminders_data = {"next_id": 1, "reminders": []}
        self.storage.save("reminders", reminders_data)
        # settings.json 保持不变（用户设置不清除）

    def show_reminder_notification(self, message):
        self.tray.show_notification("提醒", message)

    def quit_app(self):
        # 关闭所有便签窗口
        for note_id, win in list(self.note_windows.items()):
            try:
                win.window.destroy()
            except:
                pass
        # 停止提醒线程
        self.reminder_ctrl.stop()
        # 注销热键
        self.hotkey_mgr.unregister_all()
        # 停止托盘
        self.tray.stop()
        # 退出主循环
        self.root.quit()
        sys.exit(0)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()