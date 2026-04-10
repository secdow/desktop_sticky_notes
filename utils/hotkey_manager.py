import keyboard
import threading

class HotkeyManager:
    def __init__(self):
        self.hotkeys = {}

    #设置全局热键
    def register(self, hotkey, callback):
        try:
            keyboard.add_hotkey(hotkey, callback)
            self.hotkeys[hotkey] = callback
            return True
        except Exception as e:
            print(f"注册热键 {hotkey} 失败: {e}")
            return False

    def unregister_all(self):
        keyboard.unhook_all()
        self.hotkeys.clear()