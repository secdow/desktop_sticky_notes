from datetime import datetime
from typing import List

from models.entities import Note
from storage.file_storage import FileStorageManager


class NoteController:
    def __init__(self):
        self.storage = FileStorageManager()

    def get_all_notes(self) -> List[Note]:
        data = self.storage.load("notes")
        return [Note.from_dict(n) for n in data.get("notes", [])]

    def create_note(self, title="", content="", x=100, y=150) -> Note:
        data = self.storage.load("notes")
        next_id = data["next_id"]
        new_note = Note(
            id=next_id,
            title=title,
            content=content,
            x=x, y=y,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        data["notes"].append(new_note.to_dict())
        data["next_id"] = next_id + 1
        self.storage.save("notes", data)
        return new_note

    def update_note(self, note: Note) -> bool:
        note.updated_at = datetime.now()
        data = self.storage.load("notes")
        for i, n in enumerate(data["notes"]):
            if n["id"] == note.id:
                data["notes"][i] = note.to_dict()
                self.storage.save("notes", data)
                return True
        return False

    def delete_note(self, note_id: int) -> bool:
        data = self.storage.load("notes")
        original_count = len(data["notes"])
        data["notes"] = [n for n in data["notes"] if n["id"] != note_id]
        if len(data["notes"]) == original_count:
            return False
        self.storage.save("notes", data)
        return True

    def delete_all_notes(self) -> bool:
        """删除所有便签"""
        data = self.storage.load("notes")
        data["notes"] = []
        data["next_id"] = 1
        self.storage.save("notes", data)
        return True