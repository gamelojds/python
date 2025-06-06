import sys
import os

# 设置 FreeCAD 安装路径（根据你的实际安装路径修改）
freecad_path = r"D:\FreeCAD\bin"  # 注意：0.21 替换为你的版本号

# 添加到系统路径
sys.path.append(freecad_path)

# 解决 DLL 加载问题（重要！）
os.environ['PATH'] = freecad_path + ';' + os.environ['PATH']

# 现在可以导入 FreeCAD 模块
import FreeCAD
import Part
import FreeCADGui

# 设置无图形界面模式（适用于脚本运行）
FreeCADGui.setupWithoutGUI()

print(f"FreeCAD 版本: {'.'.join(FreeCAD.Version())}")