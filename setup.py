import sys
from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = [
        'cad_converter.py',  # 主脚本
        '--name=CADConverter',  # 输出的exe名称
        '--windowed',  # 使用GUI模式
        '--onefile',  # 打包成单个exe文件
        '--clean',  # 清理临时文件
        '--noconfirm',  # 覆盖输出目录
        # 添加版本信息
        '--version-file=version.txt',
        # 指定额外的依赖项
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=PIL.Image',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        # 排除不需要的模块
        '--exclude-module=numpy',
        '--exclude-module=scipy',
        '--exclude-module=pandas',
        '--exclude-module=matplotlib',
        # 优化选项
        '--noupx',  # 禁用UPX压缩以提高稳定性
        # 调试信息
        '--debug=all',
        # 添加数据文件
        '--add-data=version.txt;.',
    ]

    # 运行PyInstaller
    run(opts)