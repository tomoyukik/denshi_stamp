# %%
import cv2
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.pyplot import draw
from PIL import Image, ImageDraw, ImageFont

edge = 320
font = fm.fontManager.ttflist[125]
font = ImageFont.truetype(font.fname, edge)
TRANSPARENT = (255, 255, 255, 0)
RGBA = 'RGBA'

class Stamp:
    def __init__(self, contents, size, font, color='red', edge_width=6):
        self.contents = contents
        self.size = size
        self.font = font
        self.color = color
        self.edge_width = edge_width
        self.image = self._generate_stamp()

    def _generate_stamp(self):
        image = self._string_to_image(self.contents, self.font)
        image = self._circle(image)
        return image

    def _character_to_image(self, character, font):
        image = Image.new(RGBA, (font.size, font.size), TRANSPARENT)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), character, font=font, fill=self.color)
        image = self._crop(image)
        return image
    
    def _concat_chars(self, chars):
        height = sum([c.height for c in chars])
        width = max([c.width for c in chars])
        image = Image.new(RGBA, (width, height), TRANSPARENT)
        x, y = 0, 0
        for char in chars:
            x = (width - char.width) // 2
            image.paste(char, (x, y))
            y = char.height
        return image
    
    def _string_to_image(self, string, font):
        char_images = []
        for char in string:
            char_image = self._character_to_image(char, font)
            char_images.append(char_image)
        string_image = self._concat_chars(char_images)
        string_image = self._crop(string_image)
        return string_image
    
    def _circle(self, image):
        # rescale
        edge = min(image.height, image.width)
        rescaled = image.resize((edge, edge))
        rescaled = self._crop(rescaled)
        # circle
        enclosed = self._enclose(rescaled)

        trimmed = self._trim_circle(enclosed)
        return trimmed

    #
    def _enclosing_circle(self, image):
        array = np.array(image, dtype=np.uint8)
        array = cv2.cvtColor(array, cv2.COLOR_RGBA2GRAY)
        retval, array = cv2.threshold(array, array.min() + 1, 255, cv2.THRESH_BINARY)
        x0 = image.width // 2
        y0 = image.height // 2
        array = cv2.circle(array, (x0, y0), y0, 255, thickness=-1)
        contours, hierarchy = cv2.findContours(array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        (x1, y1), radius = cv2.minEnclosingCircle(contours[0])
        return (x0, y1), radius
    #
    def _enclose(self, image):
        (x, y), radius = self._enclosing_circle(image)
        diameter = int(radius * 2)
        stamp = Image.new(RGBA, (diameter, diameter), TRANSPARENT)
        stamp.paste(image, (int(radius - x), int(radius - y)))
        draw = ImageDraw.Draw(stamp)
        draw.ellipse((0, 0, diameter, diameter), outline=self.color, width=self.edge_width)
        return stamp
    
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

    def _object_range(self, bin_image, axis):
        histogram = np.any(bin_image < bin_image.max(), axis=axis)
        indices = np.where(histogram)[0]
        x_min, x_max = min(indices), max(indices)
        return x_min, x_max

    def _crop(self, image):
        array = np.array(image, dtype=np.uint8)
        array = cv2.cvtColor(array, cv2.COLOR_RGBA2GRAY)
        thres = (array.max() - array.min()) // 2
        retval, array = cv2.threshold(array, thres, 255, cv2.THRESH_BINARY)
        x_min, x_max = self._object_range(array, 0)
        y_min, y_max = self._object_range(array, 1)
        return image.crop((x_min - 1, y_min - 1, x_max + 1, y_max + 1))

if __name__ == '__main__':
    stmp = Stamp('小堀', edge, font)
    display(stmp.image)
    stmp = Stamp('堀堀', edge, font)
    display(stmp.image)
    stmp = Stamp('小小', edge, font)
    display(stmp.image)

# %%
