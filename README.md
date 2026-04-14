```markdown
# 桌面便签 (Desktop Sticky Notes)

一个轻量级的桌面便签与任务管理工具，支持文本便签、图片便签、任务提醒、记事本、文本片段管理等功能。所有数据本地存储，无需联网，保护隐私。

## ✨ 功能特性

- **文本便签**  
  - 多颜色主题（黄/蓝/绿/粉）  
  - 自定义标题（右键菜单修改）  
  - 窗口置顶/取消置顶  
  - 自动保存内容与位置  
  - 保存到文本片段（独立文件）

- **图片便签**  
  - 支持常见图片格式（PNG/JPG/JPEG/GIF/BMP）  
  - 图片自动缩放适应窗口  
  - 右键菜单置顶/删除  
  - 图片文件本地独立存储

- **任务管理**  
  - 优先级（1-5，数字越小越优先）  
  - 截止日期（年月日时分下拉选择）  
  - 提前提醒（分钟级，可重复提醒）  
  - 完成/未完成切换（点击完成列）  
  - 右键编辑/删除任务  
  - 批量删除、清空已完成、删除过期任务

- **记事本**  
  - 多篇独立笔记（标题+内容）  
  - 搜索笔记  
  - 双击编辑、右键删除

- **文本片段管理器**  
  - 每个片段独立为 `.txt` 文件  
  - 快速保存便签内容到片段  
  - 支持新建、编辑、删除、搜索

- **系统托盘**  
  - 显示/隐藏主窗口  
  - 退出程序

- **设置**  
  - 开机自启动  
  - 提醒扫描间隔  
  - 重复提醒间隔  
  - 格式化数据（清空所有数据）

- **全局提醒**  
  - 任务到期或提前提醒（系统气泡通知）  
  - 未完成任务重复提醒（可配置间隔）

## 📦 安装与运行

### 环境要求
- Windows 7 / 8 / 10 / 11（推荐）
- Python 3.8+（如需从源码运行）

### 从源码运行
1. 克隆或下载本项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行主程序：
   ```bash
   python main.py
   ```

## 🛠️ 打包为独立 exe

使用 PyInstaller 打包（需安装 Python 环境）：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="桌面便签" --add-data "resources;resources" --hidden-import PIL._tkinter_finder --hidden-import pystray main.py
```

打包后文件位于 `dist/桌面便签.exe`。

## 📁 数据存储

所有数据保存在程序运行目录下的 `data` 文件夹：

| 文件/目录 | 说明 |
|-----------|------|
| `data/notes.json` | 文本便签数据 |
| `data/image_notes.json` | 图片便签元数据 |
| `data/images/` | 图片便签的图片文件 |
| `data/tasks.json` | 任务数据 |
| `data/notebook.json` | 记事本数据 |
| `data/snippets/` | 文本片段（独立 .txt 文件） |
| `data/settings.json` | 用户设置 |
| `data/backup/` | 数据自动备份 |

## 🤝 贡献

欢迎提交 Issue 或 Pull Request。本项目采用 MIT 许可证。

## 📧 联系

如有问题或建议，请通过 GitHub Issues 联系。

---

**享受便捷的桌面便签与任务管理！**
```
