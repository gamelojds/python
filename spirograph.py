import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import math
from PIL import Image, ImageDraw, ImageTk
import os
from datetime import datetime

class SpirographApp:
    def __init__(self, root):
        self.root = root
        self.root.title("万花尺绘图工具")
        self.root.geometry("900x600")
        
        # 设置默认参数
        self.R = 100  # 固定圆半径
        self.r = 40   # 移动圆半径
        self.d = 50   # 画笔到移动圆心的距离
        self.color = "#FF0000"  # 默认红色
        self.steps = 1000  # 绘制的点数
        self.line_width = 1  # 线条粗细
        self.bg_color = "#FFFFFF"  # 背景颜色
        
        # 创建StringVar变量
        self.R_value = tk.StringVar(value=str(self.R))
        self.r_value = tk.StringVar(value=str(self.r))
        self.d_value = tk.StringVar(value=str(self.d))
        self.steps_value = tk.StringVar(value=str(self.steps))
        self.line_width_value = tk.StringVar(value=str(self.line_width))
        self.status_var = tk.StringVar(value="就绪")
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建控制面板
        self.create_control_panel(main_frame)
        
        # 创建画布
        self.create_canvas(main_frame)
        
        # 创建预设面板
        self.create_presets_panel(main_frame)
        
        # 创建状态栏
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始绘制
        self.draw_spirograph()

    def create_control_panel(self, parent):
        # 控制面板框架
        control_frame = ttk.LabelFrame(parent, text="参数控制", padding="10")
        control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # 添加说明文本
        info_text = "万花尺是一种绘图工具，通过调整参数可以创建各种精美的几何图案。\n\n" + \
                   "R: 固定圆半径 - 控制整体图案大小\n" + \
                   "r: 移动圆半径 - 影响图案的形状\n" + \
                   "d: 偏移距离 - 决定图案的复杂度\n" + \
                   "步数: 控制图案的精细度\n" + \
                   "线宽: 控制线条的粗细"
        info_label = ttk.Label(control_frame, text=info_text, wraplength=250, justify="left")
        info_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=10)

        # R滑块（固定圆半径）
        ttk.Label(control_frame, text="固定圆半径 (R):").grid(row=1, column=0, sticky="w")
        R_slider = ttk.Scale(control_frame, from_=50, to=200, orient="horizontal",
                           command=lambda x: self.update_param('R', float(x)))
        R_slider.set(self.R)
        R_slider.grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Label(control_frame, textvariable=self.R_value, width=5).grid(row=1, column=2, sticky="w")

        # r滑块（移动圆半径）
        ttk.Label(control_frame, text="移动圆半径 (r):").grid(row=2, column=0, sticky="w")
        r_slider = ttk.Scale(control_frame, from_=10, to=100, orient="horizontal",
                           command=lambda x: self.update_param('r', float(x)))
        r_slider.set(self.r)
        r_slider.grid(row=2, column=1, sticky="ew", padx=5)
        ttk.Label(control_frame, textvariable=self.r_value, width=5).grid(row=2, column=2, sticky="w")

        # d滑块（偏移距离）
        ttk.Label(control_frame, text="偏移距离 (d):").grid(row=3, column=0, sticky="w")
        d_slider = ttk.Scale(control_frame, from_=10, to=100, orient="horizontal",
                           command=lambda x: self.update_param('d', float(x)))
        d_slider.set(self.d)
        d_slider.grid(row=3, column=1, sticky="ew", padx=5)
        ttk.Label(control_frame, textvariable=self.d_value, width=5).grid(row=3, column=2, sticky="w")
        
        # 步数滑块
        ttk.Label(control_frame, text="步数:").grid(row=4, column=0, sticky="w")
        steps_slider = ttk.Scale(control_frame, from_=100, to=5000, orient="horizontal",
                               command=lambda x: self.update_param('steps', int(float(x))))
        steps_slider.set(self.steps)
        steps_slider.grid(row=4, column=1, sticky="ew", padx=5)
        ttk.Label(control_frame, textvariable=self.steps_value, width=5).grid(row=4, column=2, sticky="w")
        
        # 线宽滑块
        ttk.Label(control_frame, text="线宽:").grid(row=5, column=0, sticky="w")
        line_width_slider = ttk.Scale(control_frame, from_=1, to=5, orient="horizontal",
                                    command=lambda x: self.update_param('line_width', int(float(x))))
        line_width_slider.set(self.line_width)
        line_width_slider.grid(row=5, column=1, sticky="ew", padx=5)
        ttk.Label(control_frame, textvariable=self.line_width_value, width=5).grid(row=5, column=2, sticky="w")

        # 颜色选择区域
        color_frame = ttk.Frame(control_frame)
        color_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Label(color_frame, text="线条颜色:").grid(row=0, column=0, sticky="w")
        self.color_preview = tk.Canvas(color_frame, width=20, height=20, bg=self.color)
        self.color_preview.grid(row=0, column=1, padx=5)
        ttk.Button(color_frame, text="选择", command=self.choose_color).grid(row=0, column=2, padx=5)
        
        ttk.Label(color_frame, text="背景颜色:").grid(row=1, column=0, sticky="w", pady=5)
        self.bg_color_preview = tk.Canvas(color_frame, width=20, height=20, bg=self.bg_color)
        self.bg_color_preview.grid(row=1, column=1, padx=5)
        ttk.Button(color_frame, text="选择", command=self.choose_bg_color).grid(row=1, column=2, padx=5)

        # 操作按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="保存图案", command=self.save_image).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="重置参数", command=self.reset_params).grid(row=0, column=1, padx=5)

    def create_canvas(self, parent):
        # 创建画布框架
        canvas_frame = ttk.LabelFrame(parent, text="预览", padding="10")
        canvas_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5, sticky="nsew")

        # 创建画布
        self.canvas_size = 500
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_size, height=self.canvas_size,
                              bg=self.bg_color)
        self.canvas.grid(row=0, column=0)

    def create_presets_panel(self, parent):
        # 预设面板框架
        presets_frame = ttk.LabelFrame(parent, text="预设图案", padding="10")
        presets_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # 预设配置
        presets = [
            ("花瓣型", {"R": 150, "r": 60, "d": 80}),
            ("星形", {"R": 120, "r": 40, "d": 70}),
            ("螺旋", {"R": 180, "r": 30, "d": 90}),
            ("圆环", {"R": 100, "r": 50, "d": 50}),
            ("复杂型", {"R": 160, "r": 70, "d": 100})
        ]

        # 创建预设按钮
        for i, (name, params) in enumerate(presets):
            btn = ttk.Button(presets_frame, text=name,
                           command=lambda p=params: self.apply_preset(p))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")

    def apply_preset(self, params):
        for param, value in params.items():
            setattr(self, param, value)
            # 更新滑块值
            if param == 'R':
                self.R_value.set(str(value))
            elif param == 'r':
                self.r_value.set(str(value))
            elif param == 'd':
                self.d_value.set(str(value))
        self.draw_spirograph()
        self.status_var.set(f"已应用预设图案")

    def update_param(self, param, value):
        setattr(self, param, value)
        # 更新显示的数值
        if param == 'R':
            self.R_value.set(str(int(value)))
        elif param == 'r':
            self.r_value.set(str(int(value)))
        elif param == 'd':
            self.d_value.set(str(int(value)))
        elif param == 'steps':
            self.steps_value.set(str(value))
        elif param == 'line_width':
            self.line_width_value.set(str(value))
        self.draw_spirograph()

    def choose_color(self):
        color = colorchooser.askcolor(color=self.color)[1]
        if color:
            self.color = color
            self.color_preview.configure(bg=color)
            self.draw_spirograph()

    def choose_bg_color(self):
        color = colorchooser.askcolor(color=self.bg_color)[1]
        if color:
            self.bg_color = color
            self.bg_color_preview.configure(bg=color)
            self.canvas.configure(bg=color)
            self.draw_spirograph()

    def reset_params(self):
        # 重置所有参数为默认值
        self.R = 100
        self.r = 40
        self.d = 50
        self.steps = 1000
        self.line_width = 1
        self.color = "#FF0000"
        self.bg_color = "#FFFFFF"
        
        # 更新显示的数值
        self.R_value.set(str(self.R))
        self.r_value.set(str(self.r))
        self.d_value.set(str(self.d))
        self.steps_value.set(str(self.steps))
        self.line_width_value.set(str(self.line_width))
        
        # 更新颜色预览
        self.color_preview.configure(bg=self.color)
        self.bg_color_preview.configure(bg=self.bg_color)
        self.canvas.configure(bg=self.bg_color)
        
        self.draw_spirograph()
        self.status_var.set("已重置所有参数")

    def draw_spirograph(self):
        # 创建新的图像
        image = Image.new('RGB', (self.canvas_size, self.canvas_size), self.bg_color)
        draw = ImageDraw.Draw(image)

        # 计算中心点
        center_x = self.canvas_size // 2
        center_y = self.canvas_size // 2

        # 计算点的坐标
        points = []
        for i in range(self.steps):
            t = (2 * math.pi * i) / self.steps
            x = center_x + (self.R - self.r) * math.cos(t) + self.d * math.cos((self.R - self.r) * t / self.r)
            y = center_y + (self.R - self.r) * math.sin(t) - self.d * math.sin((self.R - self.r) * t / self.r)
            points.append((x, y))

        # 绘制线条
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=self.color, width=self.line_width)

        # 显示在画布上
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        
        self.status_var.set("图案已更新")

    def save_image(self):
        try:
            # 创建保存目录
            if not os.path.exists("spirograph_images"):
                os.makedirs("spirograph_images")
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"spirograph_images/spirograph_{timestamp}.png"
            
            # 创建高分辨率图像
            image_size = 2000
            image = Image.new('RGB', (image_size, image_size), self.bg_color)
            draw = ImageDraw.Draw(image)

            # 计算中心点
            center_x = image_size // 2
            center_y = image_size // 2

            # 计算点的坐标
            scale = image_size / self.canvas_size
            points = []
            for i in range(self.steps):
                t = (2 * math.pi * i) / self.steps
                x = center_x + scale * ((self.R - self.r) * math.cos(t) + self.d * math.cos((self.R - self.r) * t / self.r))
                y = center_y + scale * ((self.R - self.r) * math.sin(t) - self.d * math.sin((self.R - self.r) * t / self.r))
                points.append((x, y))

            # 绘制线条
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=self.color, width=int(self.line_width * scale))

            # 保存图像
            image.save(filename)
            messagebox.showinfo("保存成功", f"图案已保存至:\n{filename}")
            self.status_var.set(f"图案已保存: {filename}")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存图案时出错:\n{str(e)}")
            self.status_var.set("保存图案失败")

def main():
    root = tk.Tk()
    app = SpirographApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()