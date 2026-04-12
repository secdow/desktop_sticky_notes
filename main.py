import tkinter as tk
from tkinter import messagebox
import threading
import sys
import shutil
import os
from storage.file_storage import FileStorageManager
from controllers.note_controller import NoteController
from controllers.task_controller import TaskController
from controllers.reminder_controller import ReminderController
from controllers.image_note_controller import ImageNoteController
from ui.main_window import MainWindow
from ui.sticky_note import StickyNote
from ui.image_note import ImageNoteWindow
from utils.tray_manager import TrayManager
from utils.logger import setup_logger

class App:
    def __init__(self):
        self.logger = setup_logger()
        self.storage = FileStorageManager()
        self.note_ctrl = NoteController()
        self.task_ctrl = TaskController()
        self.image_note_ctrl = ImageNoteController()

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("桌面便签")
        self.root.geometry("500x400")
        self.root.minsize(500, 400)
        self.root.protocol("WM_DELETE_WINDOW", self.on_main_window_close)

        # 主窗口界面（传入两个回调：新建文本便签、新建图片便签）
        self.main_window = MainWindow(
            self.root, self,
            self.create_new_note,
            self.create_new_image_note
        )

        # 托盘
        self.tray = TrayManager(self.create_new_note, self.toggle_main_window, self.quit_app)

        # 提醒线程
        self.reminder_ctrl = ReminderController(self.show_reminder_notification)
        self.reminder_ctrl.start()

        # 加载已有的文本便签
        self.load_existing_notes()
        # 加载已有的图片便签
        self.load_existing_image_notes()

        # 启动托盘（单独线程）
        self.tray_thread = threading.Thread(target=self.tray.run, daemon=True)
        self.tray_thread.start()

    # ------------------ 文本便签 ------------------
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

    # ------------------ 图片便签 ------------------
    def load_existing_image_notes(self):
        notes = self.image_note_ctrl.get_all_image_notes()
        self.image_note_windows = {}
        for note in notes:
            win = ImageNoteWindow(self.root, note, self.on_image_note_closed)
            self.image_note_windows[note.id] = win

    def create_new_image_note(self, image_path):
        note = self.image_note_ctrl.create_image_note(image_path)
        win = ImageNoteWindow(self.root, note, self.on_image_note_closed)
        self.image_note_windows[note.id] = win

    def on_image_note_closed(self, note_id):
        if note_id in self.image_note_windows:
            del self.image_note_windows[note_id]

    # ------------------ 主窗口控制 ------------------
    def toggle_main_window(self):
        if self.root.state() == "withdrawn":
            self.root.deiconify()
            self.root.lift()
        else:
            self.root.withdraw()

    def on_main_window_close(self):
        """主窗口关闭时确认退出（不再询问保留便签）"""
        if messagebox.askyesno("退出", "确定要退出程序吗？"):
            self.quit_app()

    # ------------------ 提醒 ------------------
    def show_reminder_notification(self, message):
        self.tray.show_notification("提醒", message)

    # ------------------ 退出程序 ------------------
    def quit_app(self):
        # 关闭所有文本便签窗口
        for note_id, win in list(self.note_windows.items()):
            try:
                win.window.destroy()
            except:
                pass
        self.note_windows.clear()
        # 关闭所有图片便签窗口
        for note_id, win in list(self.image_note_windows.items()):
            try:
                win.window.destroy()
            except:
                pass
        self.image_note_windows.clear()
        # 停止提醒线程
        self.reminder_ctrl.stop()
        # 停止托盘
        self.tray.stop()
        # 退出主循环
        self.root.quit()
        sys.exit(0)

    def format_all_data(self):
        """清空所有数据并退出程序（包括备份文件）"""
        # 清空文本便签
        self.note_ctrl.delete_all_notes()
        # 清空图片便签
        self.image_note_ctrl.delete_all_image_notes()
        # 清空任务、标签、提醒
        tasks_data = {"next_id": 1, "tasks": []}
        self.storage.save("tasks", tasks_data)
        tags_data = {"next_id": 1, "tags": []}
        self.storage.save("tags", tags_data)
        reminders_data = {"next_id": 1, "reminders": []}
        self.storage.save("reminders", reminders_data)

        # 清空 backup 文件夹
        backup_dir = os.path.join("data", "backup")
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)  # 删除整个文件夹
            os.makedirs(backup_dir)  # 重新创建空文件夹

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()