import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import webbrowser
from converter import CADConverter

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
            webbrowser.open(url)
        except Exception:
            messagebox.showinfo("信息", f"请访问以下网址下载ODA File Converter:\n{url}")