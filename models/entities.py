from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Note:
    id: int
    title: str = ""
    content: str = ""
    color: str = "yellow"
    x: int = 100
    y: int = 150
    width: int = 260
    height: int = 200
    is_topmost: bool = False
    tag_ids: List[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "color": self.color,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "is_topmost": self.is_topmost,
            "tag_ids": self.tag_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        # 处理日期字符串转换
        created = data.get("created_at")
        updated = data.get("updated_at")
        if isinstance(created, str):
            created = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
        if isinstance(updated, str):
            updated = datetime.strptime(updated, "%Y-%m-%d %H:%M:%S")
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            content=data.get("content", ""),
            color=data.get("color", "yellow"),
            x=data.get("x", 100),
            y=data.get("y", 150),
            width=data.get("width", 260),
            height=data.get("height", 200),
            is_topmost=data.get("is_topmost", False),
            tag_ids=data.get("tag_ids", []),
            created_at=created,
            updated_at=updated,
        )


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    priority: int = 1          # 0低 1中 2高
    due_date: Optional[datetime] = None
    is_completed: bool = False
    note_id: Optional[int] = None
    tag_ids: List[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "is_completed": self.is_completed,
            "note_id": self.note_id,
            "tag_ids": self.tag_ids,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        due = data.get("due_date")
        if isinstance(due, str):
            due = datetime.strptime(due, "%Y-%m-%d %H:%M:%S") if due else None
        created = data.get("created_at")
        if isinstance(created, str):
            created = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", 1),
            due_date=due,
            is_completed=data.get("is_completed", False),
            note_id=data.get("note_id"),
            tag_ids=data.get("tag_ids", []),
            created_at=created,
        )


@dataclass
class Tag:
    id: int
    name: str
    color: str = "#CCCCCC"

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "color": self.color}

    @classmethod
    def from_dict(cls, data: dict) -> "Tag":
        return cls(id=data["id"], name=data["name"], color=data.get("color", "#CCCCCC"))


@dataclass
class Reminder:
    id: int
    target_type: str   # 'note' 或 'task'
    target_id: int
    remind_time: datetime
    message: str = ""
    is_triggered: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "remind_time": self.remind_time,
            "message": self.message,
            "is_triggered": self.is_triggered,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Reminder":
        remind = data["remind_time"]
        if isinstance(remind, str):
            remind = datetime.strptime(remind, "%Y-%m-%d %H:%M:%S")
        created = data.get("created_at")
        if isinstance(created, str):
            created = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
        return cls(
            id=data["id"],
            target_type=data["target_type"],
            target_id=data["target_id"],
            remind_time=remind,
            message=data.get("message", ""),
            is_triggered=data.get("is_triggered", False),
            created_at=created,
        )