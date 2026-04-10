import os
import sys
import winreg

class AutoStart:
    @staticmethod
    def set(enabled: bool):
        """设置开机自启动（Windows）"""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "StickyNotes"
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enabled:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"设置开机自启失败: {e}")