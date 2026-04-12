from typing import List

from models.entities import Task
from storage.file_storage import FileStorageManager


class TaskController:
    def __init__(self):
        self.storage = FileStorageManager()

    def get_all_tasks(self) -> List[Task]:
        data = self.storage.load("tasks")
        return [Task.from_dict(t) for t in data.get("tasks", [])]

    def create_task(self, title: str, description="", priority=3, due_date=None, note_id=None) -> Task:
        """创建任务，优先级默认3（中）"""
        data = self.storage.load("tasks")
        next_id = data["next_id"]
        new_task = Task(
            id=next_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            note_id=note_id
        )
        data["tasks"].append(new_task.to_dict())
        data["next_id"] = next_id + 1
        self.storage.save("tasks", data)
        return new_task

    def update_task(self, task: Task) -> bool:
        data = self.storage.load("tasks")
        for i, t in enumerate(data["tasks"]):
            if t["id"] == task.id:
                data["tasks"][i] = task.to_dict()
                self.storage.save("tasks", data)
                return True
        return False

    def delete_task(self, task_id: int) -> bool:
        data = self.storage.load("tasks")
        new_tasks = [t for t in data["tasks"] if t["id"] != task_id]
        if len(new_tasks) == len(data["tasks"]):
            return False
        data["tasks"] = new_tasks
        self.storage.save("tasks", data)
        return True

    def toggle_completed(self, task_id: int) -> bool:
        tasks = self.get_all_tasks()
        for task in tasks:
            if task.id == task_id:
                task.is_completed = not task.is_completed
                return self.update_task(task)
        return False