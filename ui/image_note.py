import os
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from controllers.image_note_controller import ImageNoteController


class ImageNoteWindow:
    def __init__(self, master, note, on_close_callback):
        self.master = master
        self.note = note
        self.on_close = on_close_callback
        self.controller = ImageNoteController()
        self.photo = None
        self.image_label = None

        self.window = tk.Toplevel(master)
        self.window.title(self.note.title or "图片便签")
        self.window.geometry(f"{self.note.width}x{self.note.height}+{self.note.x}+{self.note.y}")
        if self.note.is_topmost:
            self.window.attributes("-topmost", True)

        # 图片显示区域（不再有顶部工具栏）
        self.image_label = tk.Label(self.window, text="加载图片中...")
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # 延迟加载图片，确保窗口已映射
        self.window.after(100, self.load_image)

        # 右键菜单
        self.create_context_menu()
        self.window.bind("<Button-3>", self.show_menu)

        # 窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind("<Configure>", self.on_configure)

    def create_context_menu(self):
        """创建右键菜单，包含动态置顶和删除"""
        self.menu = tk.Menu(self.window, tearoff=0)
        self.topmost_item_index = 0
        self.menu.add_command(label="", command=self.toggle_topmost)
        self.update_topmost_menu_text()
        self.menu.add_separator()
        self.menu.add_command(label="删除便签", command=self.delete_note)

    def update_topmost_menu_text(self):
        if self.window.attributes("-topmost"):
            self.menu.entryconfig(self.topmost_item_index, label="取消置顶")
        else:
            self.menu.entryconfig(self.topmost_item_index, label="置顶")

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def toggle_topmost(self):
        current = self.window.attributes("-topmost")
        self.window.attributes("-topmost", not current)
        self.note.is_topmost = not current
        self.controller.update_image_note(self.note)
        self.update_topmost_menu_text()

    def delete_note(self):
        if messagebox.askyesno("删除", "确定删除此图片便签吗？\n图片文件也会被删除。"):
            self.controller.delete_image_note(self.note.id)
            self.window.destroy()
            self.on_close(self.note.id)

    def load_image(self):
        full_path = os.path.join("data", self.note.image_path)
        if not os.path.exists(full_path):
            self.image_label.config(text=f"图片文件丢失\n{full_path}", fg="red")
            return

        try:
            pil_img = Image.open(full_path)
            if pil_img.mode not in ("RGB", "RGBA"):
                pil_img = pil_img.convert("RGB")
            self.display_image(pil_img)
        except Exception as e:
            self.image_label.config(text=f"图片加载失败\n{str(e)}", fg="red")

    def display_image(self, pil_img):
        win_width = self.window.winfo_width()
        win_height = self.window.winfo_height()
        if win_width <= 1:
            win_width = self.note.width
        if win_height <= 1:
            win_height = self.note.height

        img_w, img_h = pil_img.size
        scale = min(win_width / img_w, win_height / img_h, 1.0)
        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        if (new_w, new_h) != (img_w, img_h):
            resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            resized = pil_img

        self.photo = ImageTk.PhotoImage(resized)
        self.image_label.config(image=self.photo, text="")
        self.image_label.image = self.photo

    def on_configure(self, event):
        """窗口大小改变时重新缩放图片"""
        if hasattr(self, 'photo') and self.photo:
            full_path = os.path.join("data", self.note.image_path)
            if os.path.exists(full_path):
                try:
                    pil_img = Image.open(full_path)
                    if pil_img.mode not in ("RGB", "RGBA"):
                        pil_img = pil_img.convert("RGB")
                    self.display_image(pil_img)
                except:
                    pass
        # 保存位置大小
        self.note.x = self.window.winfo_x()
        self.note.y = self.window.winfo_y()
        self.note.width = self.window.winfo_width()
        self.note.height = self.window.winfo_height()
        self.controller.update_image_note(self.note)

    def close(self):
        self.note.x = self.window.winfo_x()
        self.note.y = self.window.winfo_y()
        self.note.width = self.window.winfo_width()
        self.note.height = self.window.winfo_height()
        self.controller.update_image_note(self.note)
        self.window.destroy()
        self.on_close(self.note.id)