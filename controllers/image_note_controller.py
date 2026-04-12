import os
import shutil
from datetime import datetime
from typing import List

from models.entities import ImageNote
from storage.file_storage import FileStorageManager


class ImageNoteController:
    def __init__(self):
        self.storage = FileStorageManager()
        self.images_dir = os.path.join("data", "images")
        os.makedirs(self.images_dir, exist_ok=True)

    def get_all_image_notes(self) -> List[ImageNote]:
        data = self.storage.load("image_notes")
        return [ImageNote.from_dict(n) for n in data.get("image_notes", [])]

    def create_image_note(self, source_image_path: str, x=100, y=150) -> ImageNote:
        """新建图片便签，复制图片到本地目录"""
        # 生成唯一文件名
        ext = os.path.splitext(source_image_path)[1]
        new_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(source_image_path)}"
        dest_path = os.path.join(self.images_dir, new_filename)
        shutil.copy2(source_image_path, dest_path)
        relative_path = f"images/{new_filename}"

        data = self.storage.load("image_notes")
        next_id = data.get("next_id", 1)
        new_note = ImageNote(
            id=next_id,
            image_path=relative_path,
            title=os.path.basename(source_image_path),
            x=x, y=y,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        data["image_notes"] = data.get("image_notes", [])
        data["image_notes"].append(new_note.to_dict())
        data["next_id"] = next_id + 1
        self.storage.save("image_notes", data)
        return new_note

    def update_image_note(self, note: ImageNote) -> bool:
        note.updated_at = datetime.now()
        data = self.storage.load("image_notes")
        for i, n in enumerate(data.get("image_notes", [])):
            if n["id"] == note.id:
                data["image_notes"][i] = note.to_dict()
                self.storage.save("image_notes", data)
                return True
        return False

    def delete_image_note(self, note_id: int) -> bool:
        data = self.storage.load("image_notes")
        original = data.get("image_notes", [])
        new_list = [n for n in original if n["id"] != note_id]
        if len(new_list) == len(original):
            return False
        # 删除图片文件
        for n in original:
            if n["id"] == note_id:
                img_path = os.path.join("data", n["image_path"])
                if os.path.exists(img_path):
                    os.remove(img_path)
                break
        data["image_notes"] = new_list
        self.storage.save("image_notes", data)
        return True

    def delete_all_image_notes(self) -> bool:
        """清空所有图片便签并删除所有图片文件"""
        data = self.storage.load("image_notes")
        for n in data.get("image_notes", []):
            img_path = os.path.join("data", n["image_path"])
            if os.path.exists(img_path):
                os.remove(img_path)
        data["image_notes"] = []
        data["next_id"] = 1
        self.storage.save("image_notes", data)
        return True