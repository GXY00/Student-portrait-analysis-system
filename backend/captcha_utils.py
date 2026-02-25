from PIL import Image, ImageDraw, ImageFont
import string
import random

class CaptchaGenerator:
    def __init__(self, width=120, height=40, font_size=30):
        """
        初始化验证码生成器。

        Args:
        - width (int): 图片宽度，默认为120像素。
        - height (int): 图片高度，默认为40像素。
        - font_size (int): 字体大小，默认为30像素。
        """
        self.width = width
        self.height = height
        self.font_size = font_size
        self.chars = string.ascii_letters + string.digits  # 验证码字符集合
        self.bgcolor = (255, 255, 255)  # 图片背景颜色
        self.linecolor = (random.randint(0, 128), random.randint(0, 128), random.randint(0, 128))  # 干扰线颜色
        self.dotcolor = (random.randint(0, 128), random.randint(0, 128), random.randint(0, 128))  # 干扰点颜色
        self.fontcolor = (random.randint(0, 128), random.randint(0, 128), random.randint(0, 128))  # 字体颜色

    def generate_captcha(self):
        """
        生成验证码图片和文本。

        Returns:
        - image (PIL.Image.Image): 生成的验证码图片对象。
        - captcha_text (str): 生成的验证码文本。
        """
        captcha_text = ''.join(random.choice(self.chars) for _ in range(4))  # 随机生成验证码文本
        image = Image.new('RGB', (self.width, self.height), self.bgcolor)  # 创建RGB模式的空白图片
        draw = ImageDraw.Draw(image)  # 创建可在图像上绘图的对象

        # 尝试加载默认字体，如果失败或需要更好效果，可以替换为具体的 TTF 文件路径
        try:
            # Pillow 10.0.0+ 支持 font_variant
            font = ImageFont.load_default()
            # 如果能调整大小最好，但默认字体是位图字体可能不支持调整大小，或者需要 font_variant
            # 为了兼容性，这里先尝试简单加载，实际生产环境建议使用 ImageFont.truetype("arial.ttf", size)
        except Exception:
            font = ImageFont.load_default()

        # 绘制干扰线
        for i in range(5):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            draw.line((x1, y1, x2, y2), fill=self.linecolor, width=2)

        # 绘制干扰点
        for i in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            draw.point((x, y), fill=self.dotcolor)

        # 绘制验证码文字
        # 由于默认字体可能比较小，我们这里只是简单绘制。
        # 如果需要调整大小，建议使用 truetype 字体。
        # 这里为了确保代码能跑通，我们使用默认字体，并适当调整位置。
        
        # 为了演示效果，我们尝试使用 truetype 如果系统有的话，或者回退到默认
        # 在 Windows 上通常有 arial.ttf
        try:
            font = ImageFont.truetype("arial.ttf", self.font_size)
        except IOError:
            font = ImageFont.load_default()

        for i, char in enumerate(captcha_text):
            shadow_offset = random.randint(0, 2)
            shadow_color = (180, 180, 180)
            # 计算位置，使其居中
            char_x = 10 + i * (self.width - 20) / 4
            char_y = (self.height - self.font_size) / 2
            
            draw.text((char_x + shadow_offset, char_y + shadow_offset), char, font=font, fill=shadow_color)  # 绘制阴影效果的文字
            draw.text((char_x, char_y), char, font=font, fill=self.fontcolor)  # 绘制文字

        return image, captcha_text

# captcha_gen=CaptchaGenerator()
# captcha_image,captcha_teXt=captcha_gen.generate_captcha()
# captcha_image.show()