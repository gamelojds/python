import os
import threading
from queue import Queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import gc

class KGMConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KGM转MP3工具")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5)
        self.style.configure("TLabel", padding=5)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 初始化变量
        self.selected_files = []
        self.conversion_queue = Queue()
        self.is_converting = False
        self.is_paused = False
        self.conversion_thread = None
        self.last_directory = os.path.expanduser("~")
        
        # 创建暂停事件
        self.pause_event = threading.Event()
        self.pause_event.set()  # 初始状态为未暂停
        
        # 文件选择区域
        self.create_file_selection_area()
        
        # 转换进度区域
        self.create_progress_area()
        
        # 状态显示区域
        self.create_status_area()
        
        # 绑定关闭窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_file_selection_area(self):
        # 文件选择区域框架
        file_frame = ttk.LabelFrame(self.main_frame, text="文件选择", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=5)
        
        # 文件列表
        self.file_listbox = tk.Listbox(file_frame, height=6)
        self.file_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        # 滚动条
        scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=2, sticky="ns")
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 按钮框架
        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        # 添加文件按钮
        add_file_btn = ttk.Button(btn_frame, text="添加文件", command=self.add_files)
        add_file_btn.grid(row=0, column=0, padx=5)
        
        # 添加文件夹按钮
        add_folder_btn = ttk.Button(btn_frame, text="添加文件夹", command=self.add_folder)
        add_folder_btn.grid(row=0, column=1, padx=5)
        
        # 删除选中按钮
        remove_btn = ttk.Button(btn_frame, text="删除选中", command=self.remove_selected)
        remove_btn.grid(row=0, column=2, padx=5)
        
        file_frame.columnconfigure(0, weight=1)

    def create_progress_area(self):
        # 进度区域框架
        progress_frame = ttk.LabelFrame(self.main_frame, text="转换进度", padding="5")
        progress_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
        
        # 总体进度条
        self.total_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.total_progress.grid(row=0, column=0, columnspan=3, sticky="we", padx=5, pady=5)
        
        # 当前文件进度标签
        self.current_file_label = ttk.Label(progress_frame, text="等待开始转换...")
        self.current_file_label.grid(row=1, column=0, columnspan=3, sticky="we", padx=5)
        
        # 按钮框架
        button_frame = ttk.Frame(progress_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky="we")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        # 转换按钮
        self.convert_btn = ttk.Button(
            button_frame,
            text="开始转换",
            command=self.start_conversion
        )
        self.convert_btn.grid(row=0, column=0, padx=5, pady=10)
        
        # 暂停/继续按钮
        self.pause_btn = ttk.Button(
            button_frame,
            text="暂停",
            command=self.toggle_pause,
            state=tk.DISABLED  # 初始状态为禁用
        )
        self.pause_btn.grid(row=0, column=1, padx=5, pady=10)
        
        # 取消按钮
        self.cancel_btn = ttk.Button(
            button_frame,
            text="取消",
            command=self.cancel_conversion,
            state=tk.DISABLED  # 初始状态为禁用
        )
        self.cancel_btn.grid(row=0, column=2, padx=5, pady=10)
        
        progress_frame.columnconfigure(0, weight=1)

    def create_status_area(self):
        # 状态显示区域
        status_frame = ttk.LabelFrame(self.main_frame, text="状态信息", padding="5")
        status_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=5)
        
        # 状态文本框
        self.status_text = tk.Text(status_frame, height=6, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky="nsew")
        
        # 滚动条
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        status_frame.columnconfigure(0, weight=1)

    def add_files(self):
        """添加文件"""
        files = filedialog.askopenfilenames(
            title="选择KGM文件",
            filetypes=[("KGM文件", "*.kgm"), ("所有文件", "*.*")],
            initialdir=self.last_directory
        )
        
        if files:
            self.last_directory = os.path.dirname(files[0])
            self.selected_files.extend(files)
            self.update_file_list()

    def add_folder(self):
        """添加文件夹"""
        folder = filedialog.askdirectory(
            title="选择包含KGM文件的文件夹",
            initialdir=self.last_directory
        )
        
        if folder:
            self.last_directory = folder
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.kgm'):
                        self.selected_files.append(os.path.join(root, file))
            self.update_file_list()

    def remove_selected(self):
        """删除选中的文件"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        # 从后往前删除，避免索引变化
        for index in reversed(selection):
            del self.selected_files[index]
            
        self.update_file_list()

    def update_file_list(self):
        """更新文件列表显示"""
        self.file_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.file_listbox.insert(tk.END, os.path.basename(file))

    def update_progress(self, value):
        """更新进度条"""
        self.total_progress["value"] = value

    def update_status(self, message):
        """更新状态信息"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)

    def format_size(self, size):
        """格式化文件大小显示"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def format_time(self, seconds):
        """格式化时间显示"""
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}小时{minutes}分{seconds}秒"
        elif minutes > 0:
            return f"{minutes}分{seconds}秒"
        else:
            return f"{seconds}秒"

    def convert_kgm_to_mp3(self, input_file, output_file):
        """转换KGM文件为MP3"""
        try:
            # 读取KGM文件
            with open(input_file, 'rb') as f:
                data = f.read()
            
            # 解密数据（示例使用异或解密，实际应根据KGM格式规范实现）
            decrypted_data = bytes(b ^ 0x4C for b in data)  # 使用0x4C作为异或密钥
            
            # 写入MP3文件
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
                
        except Exception as e:
            raise Exception(f"转换失败: {str(e)}")

    def toggle_pause(self):
        """切换暂停/继续状态"""
        if not self.is_converting:
            return
            
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_event.clear()  # 暂停转换
            self.pause_btn.configure(text="继续")
            self.update_status("转换已暂停")
        else:
            self.pause_event.set()  # 继续转换
            self.pause_btn.configure(text="暂停")
            self.update_status("转换已继续")
            
    def cancel_conversion(self):
        """取消转换"""
        if not self.is_converting:
            return
            
        if messagebox.askyesno("确认取消", "确定要取消当前的转换任务吗？"):
            self.is_converting = False
            # 清空转换队列
            while not self.conversion_queue.empty():
                self.conversion_queue.get()
            self.update_status("转换已取消")
            
    def on_closing(self):
        """窗口关闭事件处理"""
        if self.is_converting:
            if messagebox.askyesno("确认退出", "正在进行转换，确定要退出吗？"):
                self.is_converting = False
                self.root.destroy()
        else:
            self.root.destroy()

    def start_conversion(self):
        """开始转换流程"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要转换的文件！")
            return
            
        # 选择输出目录
        output_dir = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.last_directory
        )
        
        if not output_dir:
            return
            
        # 更新最后访问的目录
        self.last_directory = output_dir
            
        # 将文件添加到转换队列
        for file_path in self.selected_files:
            self.conversion_queue.put((file_path, output_dir))
            
        # 更新按钮状态
        self.convert_btn.configure(state=tk.DISABLED)
        self.pause_btn.configure(state=tk.NORMAL, text="暂停")
        self.cancel_btn.configure(state=tk.NORMAL)
            
        # 重置进度条和状态
        self.total_progress["value"] = 0
        self.total_progress["maximum"] = len(self.selected_files)
        self.is_paused = False
        self.pause_event.set()
            
        # 开始转换
        self.is_converting = True
        self.conversion_thread = threading.Thread(target=self.conversion_worker)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()

    def conversion_worker(self):
        """转换工作线程"""
        converted_count = 0
        failed_files = []
        total_size = 0
        start_time = time.time()
        pause_start_time = 0
        total_pause_time = 0
        
        while not self.conversion_queue.empty() and self.is_converting:
            # 检查暂停状态
            if self.is_paused:
                if pause_start_time == 0:
                    pause_start_time = time.time()
                    self.update_status("转换已暂停")
                self.pause_event.wait()  # 等待继续信号
                if pause_start_time > 0:
                    total_pause_time += time.time() - pause_start_time
                    pause_start_time = 0
                    
            input_file, output_dir = self.conversion_queue.get()
            try:
                # 获取文件大小
                file_size = os.path.getsize(input_file)
                total_size += file_size
                size_str = self.format_size(file_size)
                
                # 更新当前处理文件显示
                self.root.after(0, self.current_file_label.configure, 
                              {"text": f"正在转换: {os.path.basename(input_file)} ({size_str})"})
                
                # 构建输出文件路径
                output_file = os.path.join(output_dir, 
                                         os.path.splitext(os.path.basename(input_file))[0] + '.mp3')
                
                # 执行转换
                if self.is_converting:  # 再次检查是否取消
                    self.convert_kgm_to_mp3(input_file, output_file)
                    
                    if self.is_converting:  # 转换完成后再次检查是否取消
                        converted_count += 1
                        
                        # 计算转换速度（不包括暂停时间）
                        elapsed_time = time.time() - start_time - total_pause_time
                        if elapsed_time > 0:
                            speed = total_size / elapsed_time
                            speed_str = f"平均速度: {self.format_size(speed)}/s"
                        else:
                            speed_str = ""
                        
                        # 更新进度和状态
                        self.root.after(0, self.update_progress, converted_count)
                        self.update_status(
                            f"成功转换: {os.path.basename(input_file)} ({size_str}) {speed_str}"
                        )
                
            except Exception as e:
                failed_files.append((input_file, str(e)))
                self.update_status(f"转换失败: {os.path.basename(input_file)} - {str(e)}")
            
            self.conversion_queue.task_done()
            
            # 定期进行垃圾回收
            if converted_count % 5 == 0:
                gc.collect()
        
        # 计算总体统计信息
        if converted_count > 0:
            total_time = time.time() - start_time - total_pause_time
            if total_time > 0:
                avg_speed = total_size / total_time
                self.update_status(
                    f"\n转换完成统计:\n"
                    f"总大小: {self.format_size(total_size)}\n"
                    f"总耗时: {self.format_time(total_time)}\n"
                    f"平均速度: {self.format_size(avg_speed)}/s"
                )
        
        # 转换完成，恢复UI状态
        self.root.after(0, self.conversion_completed, converted_count, failed_files)

    def conversion_completed(self, converted_count, failed_files):
        """转换完成后的处理"""
        self.is_converting = False
        
        # 重置按钮状态
        self.convert_btn.configure(state=tk.NORMAL)
        self.pause_btn.configure(state=tk.DISABLED)
        self.cancel_btn.configure(state=tk.DISABLED)
        
        # 更新界面显示
        self.current_file_label.configure(text="转换完成")
        
        # 显示转换结果
        if failed_files:
            failed_message = "\n失败文件列表:\n" + "\n".join(
                f"{os.path.basename(f)}: {err}" for f, err in failed_files
            )
            self.update_status(failed_message)
            
        # 如果是因为取消而完成，显示取消信息
        if self.conversion_queue.qsize() > 0:
            remaining = self.conversion_queue.qsize()
            self.update_status(f"\n转换已取消，还有 {remaining} 个文件未转换")
            # 清空剩余队列
            while not self.conversion_queue.empty():
                self.conversion_queue.get()
            
        # 清空选择的文件列表
        self.selected_files.clear()
        self.update_file_list()

def main():
    root = tk.Tk()
    app = KGMConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()