from controllers.note_controller import NoteController
from controllers.task_controller import TaskController

class SearchController:
    def __init__(self):
        self.note_ctrl = NoteController()
        self.task_ctrl = TaskController()

    def search(self, keyword: str):
        keyword = keyword.lower()
        notes = self.note_ctrl.get_all_notes()
        tasks = self.task_ctrl.get_all_tasks()

        matched_notes = [n for n in notes if keyword in n.title.lower() or keyword in n.content.lower()]
        matched_tasks = [t for t in tasks if keyword in t.title.lower() or keyword in t.description.lower()]
        return matched_notes, matched_tasks