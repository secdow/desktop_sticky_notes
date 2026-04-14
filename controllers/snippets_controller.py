import os
import glob
from datetime import datetime

class SnippetsController:
    def __init__(self):
        self.snippets_dir = os.path.join("data", "snippets")
        os.makedirs(self.snippets_dir, exist_ok=True)

    def list_snippets(self):
        """返回所有片段文件名（不含扩展名）和修改时间"""
        files = glob.glob(os.path.join(self.snippets_dir, "*.txt"))
        snippets = []
        for f in files:
            name = os.path.basename(f)[:-4]
            mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")
            snippets.append({"name": name, "mtime": mtime, "path": f})
        return sorted(snippets, key=lambda x: x["mtime"], reverse=True)

    def get_snippet_content(self, name):
        path = os.path.join(self.snippets_dir, f"{name}.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def save_snippet(self, name, content):
        path = os.path.join(self.snippets_dir, f"{name}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def delete_snippet(self, name):
        path = os.path.join(self.snippets_dir, f"{name}.txt")
        if os.path.exists(path):
            os.remove(path)
            return True
        return False