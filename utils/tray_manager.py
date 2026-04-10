import pystray
from PIL import Image, ImageDraw
import threading

class TrayManager:
    def __init__(self, on_new_note, on_show_hide, on_quit):
        self.on_new_note = on_new_note
        self.on_show_hide = on_show_hide
        self.on_quit = on_quit
        self.icon = None
        self.running = False

    def create_image(self):
        # 生成一个简单的图标（你也可以加载外部图片）
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill=(255, 255, 0), outline=(0, 0, 0))
        return image

    def run(self):
        menu = pystray.Menu(
            pystray.MenuItem("新建便签", lambda: self.on_new_note()),
            pystray.MenuItem("显示/隐藏主窗口", lambda: self.on_show_hide()),
            pystray.MenuItem("退出", lambda: self.on_quit())
        )
        self.icon = pystray.Icon("sticky_notes", self.create_image(), "桌面便签", menu)
        self.running = True
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()
        self.running = False

    def show_notification(self, title, message):
        if self.icon:
            self.icon.notify(message, title)