import os
import sys
import subprocess
import traceback
import time
from preview_manager import PreviewManager

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
            r"D:\FreeCAD\bin\ODAFileConverter.exe",
            r"C:\Program Files\ODA\ODAFileConverter 26.4.0.exe",
            # 添加其他可能的路径
        ]
        
        # 检查FreeCAD可用性
        self.freecad_available = False
        self.FreeCAD = None
        self.Part = None
        self.Mesh = None
        
        try:
            import FreeCAD
            import Part
            import Mesh
            self.FreeCAD = FreeCAD
            self.Part = Part
            self.Mesh = Mesh
            self.freecad_available = True
        except ImportError:
            print("警告: FreeCAD未安装或无法导入，3D文件转换功能将不可用")
        except Exception as e:
            print(f"警告: FreeCAD初始化错误 - {str(e)}")
        
        # 初始化预览管理器
        self.preview_manager = None
        try:
            self.preview_manager = PreviewManager()
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
                    shape = self.Part.read(input_file)
                elif input_ext in ['.iges', '.igs']:
                    shape = self.Part.read(input_file)
                elif input_ext == '.stl':
                    mesh = self.Mesh.Mesh(input_file)
                    shape = self.Part.Shape()
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
            result['error'] = f"生成预览时出错: {str(e)}"
            
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