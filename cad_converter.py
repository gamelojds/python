import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import re
import time
import traceback

class CADConverter:
    """
    CAD 2020到CAD 2007文件转换器
    使用ODA File Converter进行实际转换
    """
    
    def __init__(self):
        # ODA File Converter可能的安装路径
        self.oda_paths = [
            r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"D:\FreeCAD\bin\ODAFileConverter.exe"
            r"C:\Program Files\ODA\ODAFileConverter 26.4.0.exe",
            # 添加其他可能的路径
        ]
        
        # 检查FreeCAD可用性
        self.freecad_available = False
        try:
            import FreeCAD
            import Part
            import Mesh
            self.freecad_available = True
        except ImportError:
            print("警告: FreeCAD未安装或无法导入，3D文件转换功能将不可用")
        except Exception as e:
            print(f"警告: FreeCAD初始化错误 - {str(e)}")
        
        # 初始化预览管理器
        self.preview_manager = None
        try:
            from preview_manager import PreviewManager
            self.preview_manager = PreviewManager()
        except ImportError as e:
            print(f"警告: 无法初始化预览功能 - {str(e)}")
        except Exception as e:
            print(f"警告: 预览管理器初始化错误 - {str(e)}")
        
        # 支持的输入格式
        self.input_formats = [
            ".dwg", ".dxf",  # 2D CAD格式
            ".step", ".stp", ".iges", ".igs", ".stl"  # 3D格式
        ]
        
        # 支持的输出格式
        self.output_formats = {
            # DWG格式
            "AutoCAD 2023 DWG": "ACAD2023",
            "AutoCAD 2020 DWG": "ACAD2020",
            "AutoCAD 2018 DWG": "ACAD2018",
            "AutoCAD 2017 DWG": "ACAD2017",
            "AutoCAD 2013 DWG": "ACAD2013",
            "AutoCAD 2010 DWG": "ACAD2010",
            "AutoCAD 2007 DWG": "ACAD2007",
            "AutoCAD 2004 DWG": "ACAD2004",
            "AutoCAD 2000 DWG": "ACAD2000",
            "AutoCAD R14 DWG": "ACAD14",
            "AutoCAD R12 DWG": "ACAD12",
            # DXF格式
            "AutoCAD 2023 DXF": "DXF2023",
            "AutoCAD 2020 DXF": "DXF2020",
            "AutoCAD 2018 DXF": "DXF2018",
            "AutoCAD 2017 DXF": "DXF2017",
            "AutoCAD 2013 DXF": "DXF2013",
            "AutoCAD 2010 DXF": "DXF2010",
            "AutoCAD 2007 DXF": "DXF2007",
            "AutoCAD 2004 DXF": "DXF2004",
            "AutoCAD 2000 DXF": "DXF2000",
            "AutoCAD R14 DXF": "DXF14",
            "AutoCAD R12 DXF": "DXF12",
            # 3D格式
            "STEP格式": "STEP",
            "IGES格式": "IGES",
            "STL格式": "STL"
        }
        
    def find_oda_converter(self):
        """查找ODA File Converter的安装路径"""
        # 扩展可能的安装路径
        possible_paths = [
            # 标准安装路径
            r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
            # 自定义安装路径
            r"C:\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"D:\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"C:\Program Files\Open Design Alliance\ODAFileConverter\ODAFileConverter.exe",
            r"C:\Program Files (x86)\Open Design Alliance\ODAFileConverter\ODAFileConverter.exe",
                r"C:\Program Files\ODA\ODAFileConverter 26.4.0\ODAFileConverter.exe"
            ]
        # 用户自定义路径
        possible_paths += self.oda_paths
        
        # 规范化所有路径
        normalized_paths = [os.path.normpath(path) for path in possible_paths]
        
        # 检查每个可能的路径
        for path in normalized_paths:
            if os.path.exists(path):
                if os.path.isfile(path):
                    # 验证文件扩展名
                    if path.lower().endswith('.exe'):
                        print(f"找到ODA File Converter: {path}")
                        return path
                    else:
                        print(f"警告: 找到的路径不是可执行文件: {path}")
                else:
                    print(f"警告: 找到的路径不是文件: {path}")
        
        # 未找到可执行文件时提供详细信息
        print("错误: 未找到ODA File Converter")
        print("请确保已正确安装ODA File Converter，可以从以下位置下载：")
        print("https://www.opendesign.com/guestfiles/oda_file_converter")
        print("\n已检查的路径:")
        for path in normalized_paths:
            print(f"- {path}")
        
        return None
    
    def convert_file(self, input_file, output_dir, output_format, audit=True, recursive=False, progress_callback=None):
        """
        转换单个CAD文件
        
        参数:
            input_file (str): 输入文件路径
            output_dir (str): 输出目录路径
            output_format (str): 输出格式代码
            audit (bool): 是否在转换过程中审核文件
            recursive (bool): 是否递归处理子目录
            progress_callback (function): 进度回调函数 (0-100)
        
        返回:
            bool: 转换是否成功
        """
        try:
            # 规范化路径
            input_file = os.path.normpath(input_file)
            output_dir = os.path.normpath(output_dir)
            
            # 获取文件扩展名
            file_ext = os.path.splitext(input_file)[1].lower()
            
            # 检查输入文件是否存在
            if not os.path.exists(input_file):
                print(f"错误: 输入文件不存在: {input_file}")
                return False
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 安全的进度回调包装器
            def safe_progress(value):
                if progress_callback:
                    try:
                        progress_callback(value)
                    except Exception as e:
                        print(f"警告: 进度回调失败 - {str(e)}")
            
            # 2D格式转换(DWG/DXF)
            if file_ext in ['.dwg', '.dxf']:
                return self._convert_2d_file(input_file, output_dir, output_format, audit, safe_progress)
            
            # 3D格式转换(STEP/STP/IGES/IGS/STL)
            elif file_ext in ['.step', '.stp', '.iges', '.igs', '.stl']:
                return self._convert_3d_file(input_file, output_dir, output_format, safe_progress)
            
            else:
                print(f"错误: 不支持的文件格式: {file_ext}")
                return False
                
        except Exception as e:
            print(f"错误: 文件转换过程中发生异常 - {str(e)}")
            traceback.print_exc()
            return False
    
    def _convert_2d_file(self, input_file, output_dir, output_format, audit=True, progress_callback=None):
        """使用ODA转换2D文件(DWG/DXF)"""
        oda_path = self.find_oda_converter()
        if not oda_path:
            print("错误: 未找到ODA File Converter，请确保已正确安装")
            return False
        
        try:
            if progress_callback:
                progress_callback(10)
            
            # 准备输入和输出目录的绝对路径
            input_dir = os.path.dirname(os.path.abspath(input_file))
            output_dir = os.path.abspath(output_dir)
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 准备命令行参数
            input_filename = os.path.basename(input_file)
            audit_flag = "1" if audit else "0"
            recursive_flag = "0"  # 单文件转换不需要递归
            
            # 确定输入格式
            input_ext = os.path.splitext(input_file)[1].lower()
            input_format = "DWG" if input_ext == ".dwg" else "DXF"
            
            # 构建命令
            cmd = [
                oda_path,
                input_dir,                # 输入目录
                output_dir,               # 输出目录
                output_format,            # 输出格式
                input_format,             # 输入格式
                audit_flag,               # 审核标志
                recursive_flag,           # 递归标志
                input_filename            # 输入文件名
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            
            if progress_callback:
                progress_callback(30)
            
            # 执行转换
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 读取输出流
            while True:
                if process.poll() is not None:
                    break
                if progress_callback:
                    progress_callback(50)
                time.sleep(0.1)
            
            if progress_callback:
                progress_callback(90)
            
            # 检查是否成功
            if process.returncode == 0:
                # 验证输出文件是否存在
                output_basename = os.path.splitext(input_filename)[0]
                output_ext = ".dwg" if "DWG" in output_format else ".dxf"
                expected_output = os.path.join(output_dir, output_basename + output_ext)
                
                if not os.path.exists(expected_output):
                    print(f"错误: 转换失败 - 未找到输出文件: {expected_output}")
                    return False
                
                if os.path.getsize(expected_output) == 0:
                    print(f"错误: 转换失败 - 输出文件为空: {expected_output}")
                    os.remove(expected_output)  # 删除空文件
                    return False
                
                if progress_callback:
                    progress_callback(100)
                
                print(f"成功: 文件已转换并保存到: {expected_output}")
                return True
            else:
                error_msg = process.stderr.read().decode('utf-8', errors='ignore')
                print(f"错误: ODA转换失败 (返回码: {process.returncode}) - {error_msg}")
                return False
        except Exception as e:
            print(f"错误: 执行转换时出错 - {str(e)}")
            traceback.print_exc()  # 打印详细的错误堆栈
            return False
    
    def _convert_3d_file(self, input_file, output_dir, output_format, progress_callback=None):
        """使用FreeCAD转换3D文件"""
        if not self.freecad_available:
            print("错误: FreeCAD未安装或不可用，无法转换3D文件")
            return False
            
        try:
            # 安全地调用进度回调
            def update_progress(value):
                try:
                    if progress_callback:
                        progress_callback(value)
                except Exception as e:
                    print(f"警告: 进度回调失败 - {str(e)}")
            
            update_progress(10)
            
            # 规范化路径
            input_file = os.path.normpath(input_file)
            output_dir = os.path.normpath(output_dir)
            
            # 准备输出文件路径
            input_basename = os.path.basename(input_file)
            output_basename = os.path.splitext(input_basename)[0]
            
            # 根据输出格式确定文件扩展名
            output_ext = {
                "STEP": ".step",
                "IGES": ".iges",
                "STL": ".stl"
            }.get(output_format)
            
            if not output_ext:
                print(f"错误: 不支持的3D输出格式: {output_format}")
                return False
            
            output_file = os.path.join(output_dir, output_basename + output_ext)
            
            update_progress(20)
            
            # 确保输入文件存在
            if not os.path.exists(input_file):
                print(f"错误: 输入文件不存在: {input_file}")
                return False
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 加载输入文件
            shape = None
            input_ext = os.path.splitext(input_file)[1].lower()
            
            try:
                if input_ext in ['.step', '.stp']:
                    shape = Part.read(input_file)
                elif input_ext in ['.iges', '.igs']:
                    shape = Part.read(input_file)
                elif input_ext == '.stl':
                    mesh = Mesh.Mesh(input_file)
                    shape = Part.Shape()
                    shape.makeShapeFromMesh(mesh.Topology, 0.1)
                else:
                    print(f"错误: 不支持的输入格式: {input_ext}")
                    return False
            except Exception as e:
                print(f"错误: 无法加载3D文件 - {str(e)}")
                return False
            
            update_progress(60)
            
            if not shape:
                print("错误: 无法创建3D形状")
                return False
            
            # 导出到目标格式
            try:
                if output_format == "STEP":
                    shape.exportStep(output_file)
                elif output_format == "IGES":
                    shape.exportIges(output_file)
                elif output_format == "STL":
                    shape.exportStl(output_file)
            except Exception as e:
                print(f"错误: 导出文件失败 - {str(e)}")
                return False
            
            update_progress(90)
            
            # 验证输出文件
            if not os.path.exists(output_file):
                print(f"错误: 3D转换失败 - 未生成输出文件: {output_file}")
                return False
            
            if os.path.getsize(output_file) == 0:
                print(f"错误: 3D转换失败 - 输出文件为空: {output_file}")
                os.remove(output_file)  # 删除空文件
                return False
            
            update_progress(100)
            print(f"成功: 3D文件已转换并保存到: {output_file}")
            return True
            
        except Exception as e:
            print(f"错误: 3D转换过程中发生异常 - {str(e)}")
            traceback.print_exc()  # 打印详细的错误堆栈
            return False
    
    def get_preview(self, file_path, width=256, height=256):
        """
        获取文件预览和基本信息
        
        参数:
            file_path (str): 文件路径
            width (int): 预览图宽度
            height (int): 预览图高度
            
        返回:
            dict: 包含预览图像和文件信息的字典，格式为:
            {
                'preview': PIL.Image对象或None,
                'info': {
                    'filename': str,
                    'size': int,
                    'modified': str,
                    'created': str,
                    'format': str
                },
                'error': str or None
            }
        """
        result = {
            'preview': None,
            'info': None,
            'error': None
        }
        
        if not os.path.exists(file_path):
            result['error'] = "文件不存在"
            return result
            
        if not self.preview_manager:
            result['error'] = "预览功能不可用"
            return result
            
        try:
            result['preview'] = self.preview_manager.generate_preview(file_path, width, height)
            result['info'] = self.preview_manager.get_file_info(file_path)
        except Exception as e:
            result['error'] = f"生成预览时出错: {str(e)}" # type: ignore
            
        return result

    def convert_directory(self, input_dir, output_dir, output_format, audit=True):
        """
        转换目录中的所有CAD文件
        
        参数:
            input_dir (str): 输入目录路径
            output_dir (str): 输出目录路径
            output_format (str): 输出格式代码，如"ACAD2007"
            audit (bool): 是否在转换过程中审核文件
        
        返回:
            tuple: (成功转换的文件数, 失败的文件数)
        """
        success_count = 0
        failure_count = 0
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 遍历输入目录中的所有文件
        for root, _, files in os.walk(input_dir):
            for file in files:
                # 检查文件扩展名
                if any(file.lower().endswith(ext) for ext in self.input_formats):
                    # 构建输入文件的完整路径
                    input_file = os.path.join(root, file)
                    
                    # 计算相对路径，以保持目录结构
                    rel_path = os.path.relpath(root, input_dir)
                    if rel_path == ".":
                        target_dir = output_dir
                    else:
                        target_dir = os.path.join(output_dir, rel_path)
                        os.makedirs(target_dir, exist_ok=True)
                    
                    # 转换文件
                    if self.convert_file(input_file, target_dir, output_format, audit, False):
                        success_count += 1
                    else:
                        failure_count += 1
        
        return success_count, failure_count


class CADConverterGUI:
    """CAD转换器的图形用户界面"""
    
    def __init__(self, root):
        self.root = root
        self.converter = CADConverter()
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        self.root.title("CAD 2020 到 CAD 2007 转换器")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", padding=6)
        style.configure("TFrame", padding=10)
        
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(main_frame, text="CAD 2020 到 CAD 2007 文件转换器", font=("Arial", 16))
        title_label.pack(pady=10)
        
        # 检查ODA File Converter是否已安装
        oda_path = self.converter.find_oda_converter()
        if oda_path:
            status_text = f"已找到ODA File Converter: {oda_path}"
            status_color = "green"
        else:
            status_text = "未找到ODA File Converter，请先安装"
            status_color = "red"
        
        status_label = ttk.Label(main_frame, text=status_text, foreground=status_color)
        status_label.pack(pady=5)
        
        if not oda_path:
            install_button = ttk.Button(main_frame, text="获取ODA File Converter", command=self.open_oda_website)
            install_button.pack(pady=5)
            
            info_label = ttk.Label(main_frame, text="ODA File Converter是一个免费工具，用于转换DWG/DXF文件格式")
            info_label.pack(pady=5)
        
        # 创建选项卡
        tab_control = ttk.Notebook(main_frame)
        
        # 单文件转换选项卡
        single_file_tab = ttk.Frame(tab_control)
        tab_control.add(single_file_tab, text="单文件转换")
        
        # 批量转换选项卡
        batch_tab = ttk.Frame(tab_control)
        tab_control.add(batch_tab, text="批量转换")
        
        tab_control.pack(expand=1, fill="both")
        
        # 设置单文件转换选项卡
        self.setup_single_file_tab(single_file_tab)
        
        # 设置批量转换选项卡
        self.setup_batch_tab(batch_tab)
        
        # 底部信息
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=10)
        
        footer_label = ttk.Label(footer_frame, text="提示: 转换过程中请勿关闭程序", font=("Arial", 9))
        footer_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(footer_frame, text="v1.0", font=("Arial", 9))
        version_label.pack(side=tk.RIGHT)
    
    def setup_single_file_tab(self, parent):
        """设置单文件转换选项卡"""
        # 输入文件框架
        input_frame = ttk.LabelFrame(parent, text="输入文件")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.input_file_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_file_var, width=50)
        input_entry.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(input_frame, text="浏览...", command=self.browse_input_file)
        browse_button.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # 输出目录框架
        output_frame = ttk.LabelFrame(parent, text="输出目录")
        output_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.output_dir_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50)
        output_entry.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)
        
        browse_output_button = ttk.Button(output_frame, text="浏览...", command=self.browse_output_dir)
        browse_output_button.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # 输出格式框架
        format_frame = ttk.LabelFrame(parent, text="输出格式")
        format_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.output_format_var = tk.StringVar(value="AutoCAD 2007 DWG")
        format_combo = ttk.Combobox(format_frame, textvariable=self.output_format_var, 
                                    values=list(self.converter.output_formats.keys()),
                                    state="readonly")
        format_combo.pack(padx=5, pady=10, fill=tk.X)
        
        # 选项框架
        options_frame = ttk.LabelFrame(parent, text="选项")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.audit_var = tk.BooleanVar(value=True)
        audit_check = ttk.Checkbutton(options_frame, text="审核并修复文件", variable=self.audit_var)
        audit_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # 转换按钮
        convert_button = ttk.Button(parent, text="转换文件", command=self.convert_single_file)
        convert_button.pack(pady=20)
        
        # 状态框架
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, padx=10)
        
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W)
    
    def setup_batch_tab(self, parent):
        """设置批量转换选项卡"""
        # 输入目录框架
        input_frame = ttk.LabelFrame(parent, text="输入目录")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.input_dir_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_dir_var, width=50)
        input_entry.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(input_frame, text="浏览...", command=self.browse_input_dir)
        browse_button.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # 输出目录框架
        output_frame = ttk.LabelFrame(parent, text="输出目录")
        output_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.batch_output_dir_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.batch_output_dir_var, width=50)
        output_entry.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)
        
        browse_output_button = ttk.Button(output_frame, text="浏览...", command=self.browse_batch_output_dir)
        browse_output_button.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # 输出格式框架
        format_frame = ttk.LabelFrame(parent, text="输出格式")
        format_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.batch_format_var = tk.StringVar(value="AutoCAD 2007 DWG")
        format_combo = ttk.Combobox(format_frame, textvariable=self.batch_format_var, 
                                    values=list(self.converter.output_formats.keys()),
                                    state="readonly")
        format_combo.pack(padx=5, pady=10, fill=tk.X)
        
        # 选项框架
        options_frame = ttk.LabelFrame(parent, text="选项")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.batch_audit_var = tk.BooleanVar(value=True)
        audit_check = ttk.Checkbutton(options_frame, text="审核并修复文件", variable=self.batch_audit_var)
        audit_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # 转换按钮
        convert_button = ttk.Button(parent, text="批量转换", command=self.convert_batch)
        convert_button.pack(pady=20)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # 状态框架
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, padx=10)
        
        self.batch_status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(status_frame, textvariable=self.batch_status_var)
        status_label.pack(anchor=tk.W)
    
    def browse_input_file(self):
        """浏览并选择输入文件"""
        filetypes = [("CAD文件", "*.dwg;*.dxf"), ("所有文件", "*.*")]
        filename = filedialog.askopenfilename(title="选择CAD文件", filetypes=filetypes)
        if filename:
            self.input_file_var.set(filename)
            
            # 自动设置输出目录为输入文件所在目录
            output_dir = os.path.dirname(filename)
            self.output_dir_var.set(output_dir)
    
    def browse_output_dir(self):
        """浏览并选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def browse_input_dir(self):
        """浏览并选择输入目录"""
        directory = filedialog.askdirectory(title="选择包含CAD文件的目录")
        if directory:
            self.input_dir_var.set(directory)
            
            # 自动设置输出目录为输入目录下的"converted"子目录
            output_dir = os.path.join(directory, "converted")
            self.batch_output_dir_var.set(output_dir)
    
    def browse_batch_output_dir(self):
        """浏览并选择批量转换的输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.batch_output_dir_var.set(directory)
    
    def convert_single_file(self):
        """转换单个文件"""
        input_file = self.input_file_var.get()
        output_dir = self.output_dir_var.get()
        output_format_name = self.output_format_var.get()
        audit = self.audit_var.get()
        
        # 验证输入
        if not input_file:
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", f"输入文件不存在: {input_file}")
            return
        
        # 获取输出格式代码
        output_format = self.converter.output_formats.get(output_format_name)
        if not output_format:
            messagebox.showerror("错误", f"无效的输出格式: {output_format_name}")
            return
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 更新状态
        self.status_var.set("正在转换...")
        self.root.update()
        
        # 在后台线程中执行转换
        def do_conversion():
            success = self.converter.convert_file(input_file, output_dir, output_format, audit)
            
            # 更新UI（在主线程中）
            self.root.after(0, lambda: self.conversion_completed(success, output_dir))
        
        threading.Thread(target=do_conversion, daemon=True).start()
    
    def conversion_completed(self, success, output_dir):
        """转换完成后的回调"""
        if success:
            self.status_var.set("转换成功")
            messagebox.showinfo("成功", f"文件已成功转换并保存到:\n{output_dir}")
        else:
            self.status_var.set("转换失败")
            messagebox.showerror("错误", "文件转换失败，请检查日志")
    
    def convert_batch(self):
        """批量转换文件"""
        input_dir = self.input_dir_var.get()
        output_dir = self.batch_output_dir_var.get()
        output_format_name = self.batch_format_var.get()
        audit = self.batch_audit_var.get()
        
        # 验证输入
        if not input_dir:
            messagebox.showerror("错误", "请选择输入目录")
            return
        
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        if not os.path.exists(input_dir):
            messagebox.showerror("错误", f"输入目录不存在: {input_dir}")
            return
        
        # 获取输出格式代码
        output_format = self.converter.output_formats.get(output_format_name)
        if not output_format:
            messagebox.showerror("错误", f"无效的输出格式: {output_format_name}")
            return
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 更新状态
        self.batch_status_var.set("正在扫描文件...")
        self.progress_var.set(0)
        self.root.update()
        
        # 在后台线程中执行转换
        def do_batch_conversion():
            # 计算总文件数
            total_files = 0
            for root, _, files in os.walk(input_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in self.converter.input_formats):
                        total_files += 1
            
            if total_files == 0:
                self.root.after(0, lambda: messagebox.showinfo("信息", f"在目录中未找到CAD文件: {input_dir}"))
                self.root.after(0, lambda: self.batch_status_var.set("未找到CAD文件"))
                return
            
            # 更新状态
            self.root.after(0, lambda: self.batch_status_var.set(f"正在转换 0/{total_files} 文件..."))
            
            # 转换文件
            success_count = 0
            failure_count = 0
            
            for root, _, files in os.walk(input_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in self.converter.input_formats):
                        # 构建输入文件的完整路径
                        input_file = os.path.join(root, file)
                        
                        # 计算相对路径，以保持目录结构
                        rel_path = os.path.relpath(root, input_dir)
                        if rel_path == ".":
                            target_dir = output_dir
                        else:
                            target_dir = os.path.join(output_dir, rel_path)
                            os.makedirs(target_dir, exist_ok=True)
                        
                        # 转换文件
                        if self.converter.convert_file(input_file, target_dir, output_format, audit, False):
                            success_count += 1
                        else:
                            failure_count += 1
                        
                        # 更新进度
                        progress = (success_count + failure_count) / total_files * 100
                        self.root.after(0, lambda p=progress, s=success_count, t=total_files: 
                                        (self.progress_var.set(p), 
                                         self.batch_status_var.set(f"正在转换 {s}/{t} 文件...")))
            
            # 完成后更新UI
            self.root.after(0, lambda s=success_count, f=failure_count: 
                            self.batch_conversion_completed(s, f, output_dir))
        
        threading.Thread(target=do_batch_conversion, daemon=True).start()
    
    def batch_conversion_completed(self, success_count, failure_count, output_dir):
        """批量转换完成后的回调"""
        total = success_count + failure_count
        self.progress_var.set(100)
        
        if failure_count == 0:
            self.batch_status_var.set(f"转换完成: {success_count}/{total} 文件成功")
            messagebox.showinfo("成功", f"所有文件已成功转换!\n\n成功: {success_count}\n失败: 0\n\n文件已保存到:\n{output_dir}")
        else:
            self.batch_status_var.set(f"转换完成: {success_count}/{total} 文件成功, {failure_count} 文件失败")
            messagebox.showwarning("部分成功", 
                                f"转换完成，但有些文件失败\n\n成功: {success_count}\n失败: {failure_count}\n\n文件已保存到:\n{output_dir}")
    
    def open_oda_website(self):
        """打开ODA File Converter网站"""
        url = "https://www.opendesign.com/guestfiles/oda_file_converter"
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            messagebox.showinfo("信息", f"请访问以下网址下载ODA File Converter:\n{url}")


def main():
    root = tk.Tk()
    app = CADConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()