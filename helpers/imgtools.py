import threading
import time
import copy


from helpers import tools
import numpy as np
import cv2
import unicodedata
import io
import os
from PIL import Image, ImageDraw, ImageFont
import warnings
import asyncio
import requests
from math import *
from textwrap import wrap

ALPHA_COLOR = (255, 255, 255, 255)
LINE_TYPE = cv2.LINE_AA


class ColorInterface:
    @staticmethod
    def validated(color):
        if issubclass(type(color), VariableInterface) or issubclass(type(color), ColorInterface):
            return color
        return SingleColor(color)

    def create(self, size):
        raise Exception('Raw usage of ColorInterface forbidden!')


class SingleColor(ColorInterface, np.ndarray):
    def __new__(cls, color):
        if len(color) == 1:
            color = (color, color, color, 255)
        elif len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        color = [max(0, min(255, x)) for x in color]
        return np.array(color).view(cls)

    def get(self):
        return self

    def lightened(self, factor):
        return SingleColor([self[0] * factor, self[1] * factor, self[2] * factor, self[3]])

    def darkened(self, factor):
        return self.lightened(1 - factor)

    def alpha(self, alpha):
        return SingleColor([self[0], self[1], self[2], alpha])

    def create(self, size):
        return np.full((size[0], size[1], self.shape[0]), self, dtype=np.uint8)


class LinearGradientColor(ColorInterface):
    def __init__(self, color1, color2, axis=0):
        self.color1 = self.validated(color1)
        self.color2 = self.validated(color2)
        self.direction_axis = axis

    def color_mix(self, mix):
        return (1 - mix) * self.color1.get() + mix * self.color2.get()

    def create(self, size):
        if self.direction_axis == 0:
            size = (size[1], size[0])

        lin = np.linspace(0, 1, size[1], dtype=np.float16)
        color_gradient = np.array(list(map(self.color_mix, lin)), dtype=np.uint8)
        color_gradient = np.repeat(color_gradient[:, np.newaxis], size[0], axis=1)

        if self.direction_axis == 1:
            color_gradient = color_gradient.swapaxes(0, 1)

        return color_gradient


def rgb_to_bgr(rgb):
    return rgb[2], rgb[1], rgb[0]


def rotate_image(iimage, angle, bg_color=(0, 0, 0, 0), padding=False):
    if padding:
        diagonal_length = int(ceil(sqrt(iimage.shape[0]**2 + iimage.shape[1]**2)))
        image = np.zeros((diagonal_length, diagonal_length, iimage.shape[2]), dtype=np.uint8)

        image_center = (int(image.shape[0] * 0.5), int(image.shape[1] * 0.5))

        ho1, wo1 = int(iimage.shape[0] * 0.5), int(iimage.shape[1] * 0.5)
        ho2, wo2 = iimage.shape[0] - ho1, iimage.shape[1] - wo1

        image[
            image_center[0] - ho1:image_center[0] + ho2,
            image_center[1] - wo1:image_center[1] + wo2
        ] = iimage

    else:
        image = iimage
        image_center = tuple(np.array(image.shape[1::-1]) * 0.5)

    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)

    bg_color = list(reversed(bg_color[:3])) + list(bg_color[3:])

    result = cv2.warpAffine(image,
                            rot_mat,
                            image.shape[1::-1],
                            flags=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_CONSTANT,
                            borderValue=bg_color
                            )
    return result


def overlay_matching(background, foreground):
    fg_image = Image.fromarray(foreground)
    bg_image = Image.fromarray(background)
    bg_image.paste(fg_image, (0, 0), fg_image)
    return np.array(bg_image)


def point_on_circle(angle=0, radius=1, center=(0, 0)):
    angle = radians(int(angle))
    x = center[0] + (radius * cos(angle))
    y = center[1] + (radius * sin(angle))
    return int(x), int(y)


def overlay(background, foreground, x=0, y=0, max_size=(-1, -1), align_x='left', align_y='top'):
    if background is None:
        return foreground

    if foreground is None:
        return background

    h, w = foreground.shape[0], foreground.shape[1]

    if align_y == 'bottom':
        n_h = h
        if max_size[1] >= 0:
            n_h = min(max_size[1], h)
        by_start = max(0, y - n_h)
        by_end = min(y, background.shape[0])
        fy_start = h - n_h
        fy_end = by_end
    elif align_y == 'center':
        n_h = h
        if max_size[1] >= 0:
            n_h = min(max_size[1], h)
        hh_a = int(n_h * 0.5)
        hh_b = n_h - hh_a
        by_start = max(0, y - hh_a)
        by_end = min(y + hh_b, background.shape[0])
        fy_start = 0
        fy_end = by_end - by_start
    # Default alignment top
    else:
        if max_size[1] >= 0:
            h = min(max_size[1], h)
        by_start = max(0, y)
        by_end = min(y + h, background.shape[0])
        fy_start = 0
        fy_end = by_end - by_start

    if align_x == 'right':
        n_w = w
        if max_size[0] >= 0:
            n_w = min(max_size[0], w)
        bx_start = max(0, x - n_w)
        bx_end = min(x, background.shape[1])
        fx_start = w - n_w
        fx_end = bx_end

    elif align_x == 'center':
        n_w = w
        if max_size[0] >= 0:
            n_w = min(max_size[0], w)
        hw_a = int(n_w * 0.5)
        hw_b = n_w - hw_a
        bx_start = max(0, x - hw_a)
        bx_end = min(x + hw_b, background.shape[1])
        fx_start = 0
        fx_end = bx_end - bx_start

    # Default alignment left
    else:
        if max_size[0] >= 0:
            w = min(max_size[0], w)
        bx_start = max(0, x)
        bx_end = min(x + w, background.shape[1])
        fx_start = 0
        fx_end = bx_end - bx_start

    if by_end - by_start < 0 or bx_end - bx_start < 0:
        return background

    background = background.copy()

    background[
        by_start:by_end,
        bx_start:bx_end
    ] = overlay_matching(background[by_start:by_end, bx_start:bx_end],
                         foreground[fy_start:fy_end, fx_start:fx_end])

    return background


class VariableInterface:
    @staticmethod
    def get_variable(variable):
        if issubclass(type(variable), VariableInterface):
            return variable.get()
        if isinstance(variable, list) or isinstance(variable, tuple):
            return [VariableInterface.get_variable(v) for v in variable]
        return variable

    @staticmethod
    def one_key_to_var(key, value):
        if key is None:
            return value
        if issubclass(type(key), VariableInterface):
            key.set(value)
            return key.get()
        if isinstance(key, str) and hasattr(value, key):
            return getattr(value, key)
        return value[key]

    @staticmethod
    def key_to_var(key, value):
        if isinstance(key, list) or isinstance(key, tuple):
            v = value
            for k in key:
                v = VariableInterface.one_key_to_var(k, v)
            return v
        return VariableInterface.one_key_to_var(key, value)

    def set(self, value_dict):
        raise Exception('Raw Usage of VariableInterface forbidden')

    def get(self):
        raise Exception('Raw Usage of VariableInterface forbidden')


class Variable(VariableInterface):
    def __init__(self, key=None):
        self.key = key
        self.value = None
        self.operations = []
        self.after_operations = []

    def add_operation(self, op_name, args, kwargs):
        self.operations.append((op_name, (args, kwargs)))

    def add_after_operation(self, op):
        self.after_operations.append(op)

    def set(self, value):
        self.set_value(self.key_to_var(self.key, value))

    def set_value(self, value):
        self.value = value
        for op in self.operations:
            self.value = getattr(self.value, op[0])(*op[1][0], **op[1][1])

    def get(self):
        v = self.get_variable(self.value)
        for op in self.after_operations:
            v = op(v)
        return v

    def formatted(self, s):
        self.add_after_operation(lambda x: s.format(x))
        return self

    # TO-DO: implement all necessary requests

    def __add__(self, *args, **kwargs):
        self.add_operation('__add__', args, kwargs)
        return self

    def __mul__(self, *args, **kwargs):
        self.add_operation('__mul__', args, kwargs)
        return self

    def __sub__(self, *args, **kwargs):
        self.add_operation('__sub__', args, kwargs)
        return self

    def __truediv__(self, *args, **kwargs):
        self.add_operation('__truediv__', args, kwargs)
        return self

    def __floordiv__(self, *args, **kwargs):
        self.add_operation('__floordiv__', args, kwargs)
        return self

    def __getitem__(self, *args, **kwargs):
        self.add_operation('__getitem__', args, kwargs)
        return self


class EqualityVariable(Variable):
    def __init__(self, key, compare, on_equals, on_greater, on_smaller=None):
        super().__init__(key)
        self.compare = compare
        self.on_equals = on_equals
        self.on_greater = on_greater
        self.on_smaller = on_smaller

    def set(self, value):
        super().set(value)
        for v in [self.on_equals, self.on_greater, self.on_smaller]:
            if issubclass(type(v), VariableInterface):
                v.set(value)

    def get(self):
        if self.value == self.compare:
            return VariableInterface.get_variable(self.on_equals)
        if self.on_smaller is None or self.value > self.compare:
            return VariableInterface.get_variable(self.on_greater)
        return VariableInterface.get_variable(self.on_smaller)


class LengthVariable(Variable):
    def set(self, value):
        super().set_value(len(self.key_to_var(self.key, value)))

    def get(self):
        return super().get()


class IteratorVariable(Variable):
    current_i = 0
    max_i = 0
    iterable = None
    after_key = None

    def set(self, value):
        self.iterable = self.key_to_var(self.key, value)
        self.max_i = len(self.iterable)

    def get(self):
        if self.current_i < self.max_i:
            self.set_value(self.key_to_var(self.after_key, self.iterable[self.current_i]))
            self.current_i += 1
        return super().get()

    def __call__(self, key=None):
        self.after_key = key
        return self


class SingleColorVariable(Variable):
    def __init__(self, key):
        super().__init__(key)
        self.operations = []

    def set(self, value):
        super().set_value(SingleColor(self.key_to_var(self.key, value)))

    def lightened(self, *args, **kwargs):
        self.add_operation('lightened', args, kwargs)
        return self

    def darkened(self, *args, **kwargs):
        self.add_operation('darkened', args, kwargs)
        return self

    def alpha(self, *args, **kwargs):
        self.add_operation('alpha', args, kwargs)
        return self


class FormattedVariables(VariableInterface):
    def __init__(self, keys, vformat):
        self.vars = [Variable(key) for key in keys]
        self.vformat = vformat

    def set(self, value):
        for var in self.vars:
            var.set(value)

    def get(self):
        return self.vformat.format(*[v.get() for v in self.vars])


class VariableKwargManager:
    def used_kwarg(self, key):
        self.used_kwargs.append(key)

    def get_kwarg(self, key, default=None):
        if default is not None and key not in self.kwargs:
            return default
        if key not in self.kwargs:
            raise Exception('"{}" was not found in {}'.format(key, type(self).__name__))
        self.used_kwargs.append(key)
        value = self.kwargs[key]
        return VariableInterface.get_variable(value)

    def get_raw_kwarg(self, key):
        if key not in self.kwargs:
            raise Exception('"{}" was not found in {}'.format(key, type(self).__name__))
        self.used_kwargs.append(key)
        return self.kwargs[key]

    def set_kwarg(self, key, value):
        self.kwargs[key] = value

    def __init__(self, **kwargs):
        self.used_kwargs = []
        self.kwargs = kwargs

    def _init_finished(self):
        if 'no-check' in self.kwargs and self.kwargs['no-check'] is True:
            return
        for key in self.kwargs.keys():
            if key not in self.used_kwargs:
                warnings.warn('{} "{}" was not used'.format(type(self).__name__, key))


class Createable:
    async def create(self, *args, **kwargs):
        raise Exception('Raw usage of Createable is forbidden!')


class AlignLayer(VariableKwargManager, Createable):
    def _init(self):
        self.pos = self.get_kwarg('pos', (0, 0))
        self.align_x = self.get_kwarg('align_x', 'left')
        self.align_y = self.get_kwarg('align_y', 'top')
        self.max_size = self.get_kwarg('max_size', (-1, -1))

    async def overlay(self, **kwargs):
        layer = await self.create(**kwargs)
        return overlay(kwargs['background'], layer, self.pos[0], self.pos[1], self.max_size, self.align_x, self.align_y)


class ColoredLayer(AlignLayer):
    def _init(self):
        super()._init()
        self.color = self.get_kwarg('color', (0, 0, 0, 0))
        if not issubclass(type(self.color), ColorInterface):
            self.color = SingleColor(self.color)

    async def create(self, **kwargs):
        raise Exception('Raw usage of Colored Layer forbidden, use Color Layer!')

    def colored(self, img):
        color_overlay = self.color.create(img.shape)
        color_overlay[..., 3] = img[..., 3] * (color_overlay[..., 3] / 255.0)
        return color_overlay


class ColorLayer(ColoredLayer):
    def _init(self):
        super()._init()
        self.resize = self.get_kwarg('resize', (1, 1))
        super()._init_finished()

    async def create(self, **kwargs):
        return self.colored(np.full((self.resize[1], self.resize[0], 4), ALPHA_COLOR, dtype=np.uint8))


class EmptyLayer(ColorLayer):
    def _init__(self):
        self.set_kwarg('color', (0, 0, 0, 0))
        super()._init()


class ImageLayer(AlignLayer):
    def _init(self):
        super()._init()
        self.resize = self.get_kwarg('resize', False)

    def validated(self, img):
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
        elif img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
        return img

    def resized(self, img):
        if self.resize is False:
            return img
        return cv2.resize(img, self.resize)

    async def create(self, **kwargs):
        raise Exception('Raw usage of Image Layer forbidden, use File Image Layer')


class FileImageLayer(ImageLayer):
    def _init(self):
        super()._init()
        self.file = self.get_kwarg('file')
        super()._init_finished()

    async def create(self, **kwargs):
        img = cv2.imread(self.file, cv2.IMREAD_UNCHANGED)
        img = self.validated(img)
        return self.resized(img)


class MemoryImageLayer(ImageLayer):
    def _init(self):
        super()._init()
        self.memory = self.get_kwarg('memory')
        super()._init_finished()

    async def create(self, **kwargs):
        img = kwargs['image_creator'].image_memory[self.memory]
        img = self.validated(img)
        return self.resized(img)


class EmojiLayer(ImageLayer):
    base_emoji_url = 'http://emojipedia.org/'

    def _init(self):
        super()._init()
        self.emoji = self.get_kwarg('emoji')
        super()._init_finished()

    def get_emoji_image_url(self, provider):
        r = requests.get(self.base_emoji_url + self.emoji)
        for x in r.text.split('data-src="')[1:]:
            url = x.split('"')[0]
            if '/{}/'.format(provider) in url:
                return url

    async def create(self, **kwargs):
        emoji_id = tools.from_char(self.emoji)

        file = os.path.join(kwargs['image_creator'].emoji_path, emoji_id + '.png')
        img = None
        if os.path.exists(file):
            img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        elif kwargs['image_creator'].download_emojis:
            url = self.get_emoji_image_url(kwargs['image_creator'].download_emoji_provider)
            if url is None:
                warnings.warn('Emoji "{}" was not found on "{}"!'.format(self.emoji, self.base_emoji_url))
            else:
                img_bytes = requests.get(url).content
                img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
                if kwargs['image_creator'].save_downloaded_emojis:
                    cv2.imwrite(file, img)

        if img is None:
            if kwargs['image_creator'].emoji_not_found_image is not None and \
                    os.path.exists(kwargs['image_creator'].emoji_not_found_image):
                img = cv2.imread(kwargs['image_creator'].emoji_not_found_image, cv2.IMREAD_UNCHANGED)
            else:
                return None

        img = self.validated(img)
        return self.resized(img)


class WebImageLayer(ImageLayer):
    def _init(self):
        super()._init()
        self.url = self.get_kwarg('url')
        super()._init_finished()

    async def create(self, **kwargs):
        img_bytes = requests.get(self.url).content
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
        img = self.validated(img)
        return self.resized(img)


class TextLayer(ColoredLayer):
    def _init(self):
        super()._init()
        self.font = self.get_kwarg('font', 'default')
        self.font_size = self.get_kwarg('font_size', 16)

        self.line_margin = self.get_kwarg('line_margin', 0)

        self.text_align = self.get_kwarg('text_align', 'left')

        self.text_lines = self.get_kwarg('text_lines', False)
        if self.text_lines is False:
            self.text = self.get_kwarg('text')
            self.text = unicodedata.normalize('NFKC', str(self.text))
            self.wrap_limit = self.get_kwarg('wrap_limit', -1)

            if self.wrap_limit > 0:
                self.text_lines = wrap(self.text, self.wrap_limit)
            else:
                self.text_lines = [self.text]

        super()._init_finished()

    def get_text_dimensions(self, font):
        ascent, descent = font.getmetrics()

        line_heights = [
            font.getmask(text_line).getbbox()[3] + self.line_margin
            for text_line in self.text_lines[:-1]
        ]

        line_heights.append(font.getmask(self.text_lines[-1]).getbbox()[3])

        line_widths = [
            font.getmask(text_line).getbbox()[2]
            for text_line in self.text_lines
        ]

        total_height = sum(line_heights)

        total_width = max(line_widths)

        return total_width, total_height, line_widths, line_heights, descent

    async def create(self, **kwargs):
        if sum(map(len, self.text_lines)) == 0:
            return None

        font = kwargs['image_creator'].font_loader.load_font(self.font, self.font_size)

        total_width, total_height, line_widths, line_heights, descent = self.get_text_dimensions(font)

        img = Image.new("RGBA", (total_width, total_height), color=(0, 0, 0, 0))

        draw = ImageDraw.Draw(img)

        draw.fontmode = "L"

        y = 0
        for i in range(len(self.text_lines)):
            x = 0
            if self.text_align == 'center':
                x = int(total_width / 2 - line_widths[i] / 2)
            elif self.text_align == 'right':
                x = total_width - line_widths[i]
            draw.text((x, y - descent), self.text_lines[i], ALPHA_COLOR, font=font)
            y += line_heights[i]

        return self.colored(np.array(img))


class LineLayer(ColoredLayer):
    def _init(self):
        super()._init()
        self.target = self.get_kwarg('target')
        self.line_width = self.get_kwarg('line_width', -1)
        super()._init_finished()

    async def create(self, **kwargs):
        src = np.zeros((abs(self.target[1]), abs(self.target[0]), 4), dtype=np.uint8)
        start = [0, 0]
        end = [abs(self.target[0]), abs(self.target[1])]
        if self.target[0] < 0:
            start[0] = end[0]
            end[0] = 0
        if self.target[1] < 0:
            start[1] = end[1]
            end[1] = 0

        cv2.line(src, start, end, ALPHA_COLOR, self.line_width, LINE_TYPE)
        return self.colored(src)


class RectangleLayer(ColoredLayer):
    def _init(self):
        super()._init()
        self.size = self.get_kwarg('size', (0, 0))
        self.radius = self.get_kwarg('radius', 0)
        self.line_width = self.get_kwarg('line_width', -1)
        super()._init_finished()

    async def create(self, **kwargs):
        diameter = self.radius * 2

        thick_offset = max(0, self.line_width)
        double_thickoff = max(1, thick_offset * 2)

        mthick_offset = max(1, thick_offset)
        top_left = (thick_offset, thick_offset)
        bottom_right = (max(1, diameter - mthick_offset, self.size[1] - mthick_offset),
                        max(1, diameter - mthick_offset, self.size[0] - mthick_offset))

        src = np.zeros((bottom_right[0] + double_thickoff, bottom_right[1] + double_thickoff, 4), dtype=np.uint8)

        #  corners:
        #  p1 - p2
        #  |     |
        #  p4 - p3

        p1 = top_left
        p2 = (bottom_right[1], top_left[1])
        p3 = (bottom_right[1], bottom_right[0])
        p4 = (top_left[0], bottom_right[0])

        corner_radius = abs(self.radius)
        thickness = self.line_width

        if thickness < 0:
            # big rect
            start_pos = (p1[0] + corner_radius, p1[1])
            end_pos = (p3[0] - corner_radius, p3[1])
            cv2.rectangle(src, start_pos, end_pos, ALPHA_COLOR, thickness=thickness, lineType=LINE_TYPE)
            start_pos = (p1[0], p1[1] + corner_radius)
            end_pos = (p3[0], p3[1] - corner_radius)
            cv2.rectangle(src, start_pos, end_pos, ALPHA_COLOR, thickness=thickness, lineType=LINE_TYPE)

        else:
            # draw straight lines
            cv2.line(src, (p1[0] + corner_radius, p1[1]), (p2[0] - corner_radius, p2[1]), ALPHA_COLOR, thickness,
                     LINE_TYPE)
            cv2.line(src, (p2[0], p2[1] + corner_radius), (p3[0], p3[1] - corner_radius), ALPHA_COLOR, thickness,
                     LINE_TYPE)
            cv2.line(src, (p3[0] - corner_radius, p4[1]), (p4[0] + corner_radius, p3[1]), ALPHA_COLOR, thickness,
                     LINE_TYPE)
            cv2.line(src, (p4[0], p4[1] - corner_radius), (p1[0], p1[1] + corner_radius), ALPHA_COLOR, thickness,
                     LINE_TYPE)

        if corner_radius > 0:
            # draw arcs
            cv2.ellipse(src, (p1[0] + corner_radius, p1[1] + corner_radius), (corner_radius, corner_radius),
                        180.0, 0, 90, ALPHA_COLOR, thickness, LINE_TYPE)
            cv2.ellipse(src, (p2[0] - corner_radius, p2[1] + corner_radius), (corner_radius, corner_radius),
                        270.0, 0, 90, ALPHA_COLOR, thickness, LINE_TYPE)
            cv2.ellipse(src, (p3[0] - corner_radius, p3[1] - corner_radius), (corner_radius, corner_radius),
                        0.0, 0, 90, ALPHA_COLOR, thickness, LINE_TYPE)
            cv2.ellipse(src, (p4[0] + corner_radius, p4[1] - corner_radius), (corner_radius, corner_radius),
                        90.0, 0, 90, ALPHA_COLOR, thickness, LINE_TYPE)

        if self.radius < 0:
            src = 255 - src

        return self.colored(src)


class ProgressLayer(RectangleLayer):
    def _init(self):
        direction = self.get_kwarg('direction', 'x')
        percentage = self.get_kwarg('percentage', 1)

        size = self.get_kwarg('size')
        if direction == 'y':
            self.set_kwarg('size', (size[0], int(size[1] * percentage)))
        else:
            self.set_kwarg('size', (int(size[0] * percentage), size[1]))

        super()._init()


class PieLayer(ColoredLayer):
    def _init(self):
        super()._init()
        self.radius = self.get_kwarg('radius', 0)
        self.pieces = self.get_kwarg('pieces', 5)
        self.border_width = self.get_kwarg('border_width', 1)
        self.line_width = self.get_kwarg('line_width', 1)
        self.choices = self.get_kwarg('choices')
        self.choices_radius = self.get_kwarg('choices_radius', (self.radius - self.border_width) * 0.75)
        self.rotate_choices = self.get_kwarg('rotate_choices', True)
        super()._init_finished()

    async def create(self, **kwargs):
        angle_offset = 270

        diameter = self.radius * 2
        radius = self.radius
        half_border_width = int(self.border_width * 0.5)

        adjusted_radius = radius - half_border_width - 1

        center = (radius, radius)

        src = np.zeros((diameter, diameter, 4), dtype=np.uint8)

        slices = len(self.choices)
        slice_size = int(360 / slices)
        half_slice_size = int(slice_size * 0.5)

        cv2.circle(src,
                   center,
                   adjusted_radius,
                   ALPHA_COLOR,
                   self.border_width)

        for i in range(slices):
            start = point_on_circle(angle=slice_size * i + angle_offset,
                                    radius=adjusted_radius,
                                    center=center)

            cv2.line(src,
                     start,
                     center,
                     ALPHA_COLOR,
                     self.line_width,
                     LINE_TYPE)

        img = self.colored(src)

        for i in range(slices):
            c = point_on_circle(angle=slice_size * i + half_slice_size + angle_offset,
                                radius=int(self.choices_radius),
                                center=center)

            cimg = await self.choices[i].create(**kwargs)

            if self.rotate_choices:
                cimg = rotate_image(cimg, angle=-(slice_size * i + half_slice_size), padding=True)

            ho1, wo1 = int(cimg.shape[0] * 0.5), int(cimg.shape[1] * 0.5)
            ho2, wo2 = cimg.shape[0] - ho1, cimg.shape[1] - wo1
            img[c[1] - ho1:c[1] + ho2, c[0] - wo1:c[0] + wo2] = cimg

        return img


class ListLayer(AlignLayer):
    def _init(self):
        super()._init()
        self.repeat = self.get_kwarg('repeat')
        self.template = self.get_kwarg('template')
        self.direction = self.get_kwarg('direction', 'y')
        self.margin = self.get_kwarg('margin', 0)
        super()._init_finished()

    def concat(self, img1, img2):
        if img1 is None:
            return img2
        elif img2 is None:
            return img1
        if self.direction == 'x':
            return cv2.hconcat([img1, img2])
        return cv2.vconcat([img1, img2])

    def concat_margin(self, img):
        if self.direction == 'x':
            return cv2.hconcat([img, np.zeros((img.shape[0], self.margin, img.shape[2]), dtype=np.uint8)])
        return cv2.vconcat([img, np.zeros((self.margin, img.shape[1], img.shape[2]), dtype=np.uint8)])

    async def create(self, **kwargs):
        img = None
        for i in range(self.repeat):
            self.template._init()
            img = self.concat(img, await self.template.create(**kwargs))
            if i < self.repeat - 1:
                img = self.concat_margin(img)

        return img


class ImageStack(Createable, VariableKwargManager):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if len(args) > 1:
            self.set_kwarg('layers', list(args))
        elif len(args) == 1 and isinstance(args[0], list):
            self.set_kwarg('layers', args[0])

    def _init(self):
        self.layers = self.get_kwarg('layers', [])
        for layer in self.layers:
            layer._init()
        super()._init_finished()

    async def create(self, **kwargs):
        img = None
        if len(self.layers) == 0:
            img = await EmptyLayer().create()
        for layer in self.layers:
            kwargs['background'] = img
            img = await layer.overlay(**kwargs)

        if 'max_size' in kwargs:
            max_size = kwargs['max_size']
            resize_factor = 1
            if 0 < max_size[0] < img.shape[1]:
                resize_factor = max_size[0] / img.shape[1]
            if 0 < max_size[1] < img.shape[0]:
                resize_factor = min(resize_factor, max_size[1] / img.shape[0])

            if resize_factor < 1:
                img = cv2.resize(img, (int(img.shape[1] * resize_factor), int(img.shape[0] * resize_factor)))
        return img

    async def create_bytes(self, **kwargs):
        img = await self.create(**kwargs)

        is_success, buffer = cv2.imencode('.png', img)
        return io.BytesIO(buffer)


class AnimatedImageStack(Createable, VariableKwargManager):
    def _init(self):
        self.rotate = self.get_kwarg('rotate')
        self.static_fg = self.get_kwarg('static_fg', False)
        self.static_bg = self.get_kwarg('static_bg', False)
        self.seconds = self.get_kwarg('seconds', 5)
        self.fps = self.get_kwarg('fps', 5)
        self.rotation_func = self.get_kwarg('rotation_func', lambda i: self.get_kwarg('rotation', None) * i)
        self.loop = self.get_kwarg('loop', 1)
        self.bg_color = self.get_kwarg('bg_color', (0, 0, 0, 0))
        if len(self.bg_color) == 3:
            self.bg_color = self.bg_color[0], self.bg_color[1], self.bg_color[2], 255

    async def create(self, image_creator, **kwargs):
        rimage = await self.rotate.raw_create(image_creator, **kwargs)
        rimage = cv2.cvtColor(rimage, cv2.COLOR_RGBA2BGRA)

        fgimage = None
        if self.static_fg is not False:
            fgimage = await self.static_fg.raw_create(image_creator, **kwargs)
            fgimage = cv2.cvtColor(fgimage, cv2.COLOR_RGBA2BGRA)

        bgimage = None
        if self.static_bg is not False:
            bgimage = await self.static_bg.raw_create(image_creator, **kwargs)
            bgimage = cv2.cvtColor(bgimage, cv2.COLOR_RGBA2BGRA)

        def normalize_angle(a):
            a = int(a)
            while a < 0:
                a += 360
            while a >= 360:
                a -= 360
            return a

        buffered_images = {}

        image_data = []
        for i in np.arange(0, 1, 1 / (self.fps * self.seconds)):
            angle = normalize_angle(self.rotation_func(i))
            hit = None
            if len(buffered_images) > 0:
                hit = min(buffered_images.keys(), key=lambda x: abs(x-angle))
            if hit is not None and abs(angle-hit) <= 1:
                image_data.append(buffered_images[hit])
            else:
                t = rotate_image(rimage, angle, bg_color=self.bg_color)
                t = overlay(bgimage, t)
                t = overlay(t, fgimage)

                t = Image.fromarray(t)

                buffered_images[angle] = t

                image_data.append(t)

        gif_image_bytes = io.BytesIO()

        kwargs = {
            'fp': gif_image_bytes,
            'format': 'gif',
            'save_all': True,
            'append_images': image_data[1:],
            'duration': int(1000/self.fps),
            # 'transparency': 0,
            'disposal': 3,
        }
        if self.loop != 1:
            kwargs['loop'] = self.loop

        image_data[0].save(**kwargs)

        gif_image_bytes.seek(0)

        is_success, last_image_bytes = cv2.imencode('.png', cv2.cvtColor(np.array(image_data[-1]), cv2.COLOR_RGBA2BGRA))

        return gif_image_bytes, io.BytesIO(last_image_bytes)


class ImageStackResolve:
    def __init__(self, creatable):
        self.untouched_creatable = creatable
        self.current_arg = None

    def _resolve_list(self, x):
        for value in x:
            self._resolve(value)

    def _resolve_dict(self, d):
        for key, value in d.items():
            self._resolve(value)

    def _resolve(self, i):
        if isinstance(i, list) or isinstance(i, tuple):
            self._resolve_list(i)
        elif isinstance(i, dict):
            self._resolve_dict(i)
        elif issubclass(type(i), VariableKwargManager):
            self._resolve_dict(i.kwargs)
        elif isinstance(i, LinearGradientColor):
            self._resolve(i.color1)
            self._resolve(i.color2)
        elif issubclass(type(i), VariableInterface):
            i.set(self.current_arg)

    def _resolve_variables(self):
        self._resolve(self.creatable)

    def _resolve_init(self):
        self.creatable._init()

    def __call__(self, arg):
        self.current_arg = arg
        self.creatable = copy.deepcopy(self.untouched_creatable)
        self.to_init = []
        self._resolve_variables()
        self._resolve_init()
        self.current_arg = None
        return self.creatable


class ImageLoader:
    def load_into(self, func):
        raise Exception('Raw usage of Image Loader forbidden, use FileImageLoader')


class FileImageLoader(ImageLoader):
    def __init__(self, file=None, prefix=''):
        self.file = file
        self.prefix = prefix

    def load_into(self, func):
        img = cv2.imread(self.file, cv2.IMREAD_UNCHANGED)
        func(self.prefix + '/' + os.path.basename(self.file), img)


class DirectoryImageLoader(ImageLoader):
    def __init__(self, directory=None, prefix=''):
        self.directory = directory
        self.prefix = prefix

    def load_into(self, func):
        for f in os.listdir(self.directory):
            if f.endswith('.png'):
                img = cv2.imread(os.path.join(self.directory, f), cv2.IMREAD_UNCHANGED)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
                func(self.prefix + '/' + f, img)


class FontLoader:
    def __init__(self, fonts=None, max_fonts_loaded=10):
        self.registered_fonts = {}
        self.loaded_fonts = {}
        self.max_fonts_loaded = max_fonts_loaded

        if fonts is not None:
            for k, v in fonts.items():
                self.registered_fonts[k] = v

    def load_font(self, font_name, size):
        if font_name not in self.registered_fonts:
            raise Exception('Error font: "' + font_name + '" was not found!')

        if (font_name, size) not in self.loaded_fonts:

            if len(self.loaded_fonts) >= self.max_fonts_loaded:
                del self.loaded_fonts[min(self.loaded_fonts.items(), key=lambda x: x[1][1])[0]]

            font = ImageFont.truetype(self.registered_fonts[font_name], size)
            self.loaded_fonts[(font_name, size)] = [font, 1]
            return font
        else:
            self.loaded_fonts[(font_name, size)][1] += 1
            return self.loaded_fonts[(font_name, size)][0]


class AsyncEvent(asyncio.Event):
    def set(self):
        # TODO: _loop is not documented
        self._loop.call_soon_threadsafe(super().set)


class ImageCreator:
    def __init__(self,
                 fonts=None,
                 load_memory=None,
                 emoji_path=None,
                 emoji_not_found_image=None,
                 download_emojis=False,
                 save_downloaded_emojis=True,
                 download_emoji_provider='microsoft'
                 ):
        self.font_loader = FontLoader(fonts)

        if emoji_path is None:
            emoji_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      '..',
                                                      'images',
                                                      'emojis'))
        self.emoji_path = emoji_path

        if emoji_not_found_image is None:
            emoji_not_found_image = os.path.join(emoji_path, '0.png')

        self.emoji_not_found_image = emoji_not_found_image
        self.download_emojis = download_emojis
        self.save_downloaded_emojis = save_downloaded_emojis
        self.download_emoji_provider = download_emoji_provider

        if load_memory is None:
            load_memory = []

        self.image_memory = {}
        for loader in load_memory:
            loader.load_into(self.add_to_memory)

    def add_to_memory(self, name, img):
        if name in self.image_memory:
            raise Exception('image with same name was loaded before! Use a prefix')
        self.image_memory[name] = img

    async def create(self, stack, max_size=(-1, -1)):
        if stack is None:
            return None

        class _CreateImage:
            def __init__(_self, event):
                _self.result = None
                _self.event = event

            def create(_self):
                loop = asyncio.new_event_loop()
                loop.run_until_complete(_self._async_create())

            async def _async_create(_self):
                _self.result = await stack.create_bytes(image_creator=self, max_size=max_size)
                _self.event.set()

        e = AsyncEvent()
        ci = _CreateImage(e)

        threading.Thread(target=ci.create).start()
        await e.wait()

        return ci.result
