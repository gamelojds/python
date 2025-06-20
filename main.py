import tkinter as tk
from gui import CADConverterGUI

def main():
    """程序入口点"""
    # 创建主窗口
    root = tk.Tk()
    
    try:
        # 设置窗口图标（如果存在）
        root.iconbitmap("icon.ico")
    except:
        pass  # 如果图标文件不存在，忽略错误
    
    # 创建应用程序实例
    app = CADConverterGUI(root)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()