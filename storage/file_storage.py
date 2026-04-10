import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List

class FileStorageManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.data_dir = "data"
        self.backup_dir = os.path.join(self.data_dir, "backup")
        self._ensure_directories()
        # 定义文件名映射
        self._files = {
            "notes": "notes.json",
            "tasks": "tasks.json",
            "tags": "tags.json",
            "reminders": "reminders.json",
            "settings": "settings.json"
        }
        self._initialized = True

    def _ensure_directories(self):
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

    def _get_file_path(self, name: str) -> str:
        return os.path.join(self.data_dir, self._files[name])

    #加载JSON文件
    def load(self, name: str) -> Dict[str, Any]:
        """加载指定 JSON 文件，若不存在或损坏则返回初始结构"""
        path = self._get_file_path(name)
        if not os.path.exists(path):
            return self._get_initial_structure(name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # 尝试从备份恢复
            self._restore_from_backup(name)
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

    def save(self, name: str, data: Dict[str, Any]) -> bool:
        """原子保存：先写临时文件，再替换，并创建备份"""
        path = self._get_file_path(name)
        temp_path = path + ".tmp"
        backup_path = os.path.join(self.backup_dir, f"{name}_{datetime.now():%Y%m%d%H%M%S}.json")
        try:
            #备份现有文件
            if os.path.exists(path):
                shutil.copy2(path, backup_path)
            #写入临时文件
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=self._json_serializer)
            #原子替换（Windows 上 os.replace 是原子的）
            os.replace(temp_path, path)
            #清理旧备份，保留最近5个
            self._cleanup_old_backups(name, keep=5)
            return True
        except Exception as e:
            print(f"保存 {name} 失败: {e}")
            return False

    #返回初始数据结构
    def _get_initial_structure(self, name: str) -> Dict:
        structures = {
            "notes": {"next_id": 1, "notes": []},
            "tasks": {"next_id": 1, "tasks": []},
            "tags": {"next_id": 1, "tags": []},
            "reminders": {"next_id": 1, "reminders": []},
            "settings": {
                "theme": "light",
                "auto_start": False,
                "reminder_interval_seconds": 30,
                "hotkey_new_note": "ctrl+shift+n",
                "hotkey_show_hide": "ctrl+shift+h"
            }
        }
        return structures.get(name, {})

    @staticmethod
    def _json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        raise TypeError(f"Type {type(obj)} not serializable")

    #从最近的备份恢复
    def _restore_from_backup(self, name: str):
        import glob
        pattern = os.path.join(self.backup_dir, f"{name}_*.json")
        backups = sorted(glob.glob(pattern))
        if backups:
            shutil.copy2(backups[-1], self._get_file_path(name))

    def _cleanup_old_backups(self, name: str, keep: int):
        import glob
        pattern = os.path.join(self.backup_dir, f"{name}_*.json")
        backups = sorted(glob.glob(pattern))
        for old in backups[:-keep]:
            os.remove(old)