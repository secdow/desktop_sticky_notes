from typing import List

from models.entities import Tag
from storage.file_storage import FileStorageManager


class TagController:
    def __init__(self):
        self.storage = FileStorageManager()

    def get_all_tags(self) -> List[Tag]:
        data = self.storage.load("tags")
        return [Tag.from_dict(t) for t in data.get("tags", [])]

    def create_tag(self, name: str, color="#CCCCCC") -> Tag:
        data = self.storage.load("tags")
        next_id = data["next_id"]
        new_tag = Tag(id=next_id, name=name, color=color)
        data["tags"].append(new_tag.to_dict())
        data["next_id"] = next_id + 1
        self.storage.save("tags", data)
        return new_tag

    def delete_tag(self, tag_id: int) -> bool:
        data = self.storage.load("tags")
        new_tags = [t for t in data["tags"] if t["id"] != tag_id]
        if len(new_tags) == len(data["tags"]):
            return False
        data["tags"] = new_tags
        self.storage.save("tags", data)
        return True