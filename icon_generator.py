import os
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    """创建一个简单的CAD转换器图标"""
    # 创建一个512x512的透明背景图像
    img = Image.new('RGBA', (512, 512), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆形背景
    draw.ellipse((0, 0, 512, 512), fill=(30, 144, 255, 255))
    
    # 绘制CAD文字
    try:
        # 尝试加载系统字体
        font = ImageFont.truetype("arial.ttf", 120)
    except IOError:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
    
    draw.text((120, 150), "CAD", fill=(255, 255, 255, 255), font=font)
    
    # 绘制箭头
    arrow_points = [
        (150, 300),  # 左上
        (250, 300),  # 右上
        (250, 350),  # 右中上
        (350, 250),  # 箭头尖
        (250, 150),  # 右中下
        (250, 200),  # 右下
        (150, 200),  # 左下
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255, 255))
    
    # 保存为ICO文件
    img.save("cad_converter_icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    
    print(f"图标已创建: {os.path.abspath('cad_converter_icon.ico')}")

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageFont
        create_icon()
    except ImportError:
        print("错误: 需要安装Pillow库来创建图标")
        print("请运行: pip install pillow")