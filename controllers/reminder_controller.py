import threading
import time
from datetime import datetime
from storage.file_storage import FileStorageManager
from models.entities import Reminder
from typing import List

class ReminderController(threading.Thread):
    def __init__(self, callback_notify):
        """callback_notify 用于通知UI弹窗"""
        super().__init__(daemon=True)
        self.storage = FileStorageManager()
        self.callback_notify = callback_notify
        self.running = True

    def run(self):
        while self.running:
            self.check_reminders()
            # 从设置中读取扫描间隔，默认30秒
            settings = self.storage.load("settings")
            interval = settings.get("reminder_interval_seconds", 30)
            time.sleep(interval)

    def check_reminders(self):
        data = self.storage.load("reminders")
        reminders = [Reminder.from_dict(r) for r in data.get("reminders", [])]
        now = datetime.now()
        triggered = []
        for rem in reminders:
            if not rem.is_triggered and rem.remind_time <= now:
                rem.is_triggered = True
                triggered.append(rem)
        if triggered:
            # 更新存储
            for rem in triggered:
                for i, r in enumerate(data["reminders"]):
                    if r["id"] == rem.id:
                        data["reminders"][i] = rem.to_dict()
                        break
            self.storage.save("reminders", data)
            # 回调通知
            for rem in triggered:
                self.callback_notify(rem.message or f"提醒: {rem.target_type} ID {rem.target_id}")

    def add_reminder(self, target_type: str, target_id: int, remind_time: datetime, message=""):
        data = self.storage.load("reminders")
        next_id = data["next_id"]
        new_rem = Reminder(
            id=next_id,
            target_type=target_type,
            target_id=target_id,
            remind_time=remind_time,
            message=message
        )
        data["reminders"].append(new_rem.to_dict())
        data["next_id"] = next_id + 1
        self.storage.save("reminders", data)

    def stop(self):
        self.running = False