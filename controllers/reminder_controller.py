import threading
import time
from datetime import datetime, timedelta
from storage.file_storage import FileStorageManager
from models.entities import Task
from typing import Dict

class ReminderController(threading.Thread):
    def __init__(self, callback_notify):
        super().__init__(daemon=True)
        self.storage = FileStorageManager()
        self.callback_notify = callback_notify
        self.running = True
        self.last_remind_time: Dict[int, datetime] = {}   # 记录每个任务上次提醒的时间

    def run(self):
        while self.running:
            self.check_task_reminders()
            settings = self.storage.load("settings")
            interval = settings.get("reminder_interval_seconds", 30)
            time.sleep(interval)

    def check_task_reminders(self):
        data = self.storage.load("tasks")
        tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        now = datetime.now()
        settings = self.storage.load("settings")
        repeat_minutes = settings.get("reminder_repeat_minutes", 5)  # 重复提醒间隔（分钟），默认5分钟

        for task in tasks:
            if task.is_completed:
                continue
            if task.due_date is None:
                continue

            # 计算本次提醒时间（截止时间减去提前分钟数）
            remind_time = task.due_date - timedelta(minutes=task.remind_minutes)
            if now < remind_time:
                continue   # 还没到提醒时间

            # 检查是否应该重复提醒
            last_time = self.last_remind_time.get(task.id)
            if last_time is None:
                # 从未提醒过，立即提醒
                should_remind = True
            else:
                # 距离上次提醒是否超过重复间隔
                elapsed = (now - last_time).total_seconds() / 60.0
                should_remind = elapsed >= repeat_minutes

            if should_remind:
                self.last_remind_time[task.id] = now
                if task.remind_minutes > 0:
                    msg = f"任务「{task.title}」将在 {task.remind_minutes} 分钟后到期"
                else:
                    msg = f"任务「{task.title}」已到截止时间"
                self.callback_notify(msg)

    def stop(self):
        self.running = False