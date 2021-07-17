# %%
from PIL import Image, ImageDraw, ImageFont
import matplotlib.font_manager as fm

edge = 320
font = fm.fontManager.ttflist[125]
font = ImageFont.truetype(font.fname, edge)
TRANSPARENT = (255, 255, 255, 0)
RGBA = 'RGBA'

class Stamp:
    def __init__(self, contents, size, font):
        self.contents = contents
        self.size = size
        self.font = font
        self.image = self._generate_stamp()

    def _generate_stamp(self):
        image = self._string_to_image(self.contents, self.font)
        return self._circle(image)

    def _character_to_image(self, character, font):
        image = Image.new(RGBA, (font.size, font.size), TRANSPARENT)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), character, font=font, fill='red')
        return image
    
    def _concat_chars(self, chars):
        height = sum([c.height for c in chars])
        width = max([c.width for c in chars])
        image = Image.new(RGBA, (width, height), TRANSPARENT)
        x, y = 0, 0
        for char in chars:
            image.paste(char, (x, y))
            x = 0
            y = char.height
        return image
    
    def _string_to_image(self, string, font):
        char_images = []
        for char in string:
            char_image = self._character_to_image(char, font)
            char_images.append(char_image)
        string_image = self._concat_chars(char_images)
        return string_image
    
    def _circle(self, image):
        # rescale
        edge = min(image.height, image.width)
        rescaled = image.resize((edge, edge))
        # circle
        draw = ImageDraw.Draw(rescaled)
        draw.ellipse((edge, edge, edge, edge), outline='red', width=6)
        draw.ellipse((0, 0, edge, edge), outline='red', width=6)
        trimmed = self._trim_circle(rescaled)
        return trimmed
    
    def _trim_circle(self, image):
        # generate mask
        disk_mask = Image.new(RGBA, (image.width, image.height), TRANSPARENT)
        mask_draw = ImageDraw.Draw(disk_mask)
        mask_draw.ellipse(
            (0, 0, image.width, image.height),
            outline='black', fill='black'
        )
        # 合成するイメージ生成
        transparent = Image.new(RGBA, (image.width, image.height), TRANSPARENT)
        # 合成
        return Image.composite(image, transparent, disk_mask)

stmp = Stamp('小堀', edge, font)
stmp.image
# %%
