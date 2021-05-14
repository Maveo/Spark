from helpers import tools
import numpy as np
import cv2
import pygame
import pygame.freetype
import io
import os
import aiohttp

os.environ['SDL_AUDIODRIVER'] = 'dsp'

pygame.init()


class SingleColor(np.ndarray):
    def __new__(cls, color):
        if len(color) == 1:
            color = (color, color, color, 255)
        elif len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        color = [max(0, min(255, x)) for x in color]
        return np.array(color).view(cls)

    def lightened(self, factor):
        return SingleColor([self[0] * factor, self[1] * factor, self[2] * factor, self[3]])

    def darkened(self, factor):
        return self.lightened(1 - factor)

    def create(self, size):
        return np.full((size[0], size[1], self.shape[0]), self, dtype=np.uint8)


class LinearGradientColor:
    def __init__(self, color1, color2, axis=0):
        self.color1 = SingleColor(color1)
        self.color2 = SingleColor(color2)
        self.direction_axis = axis

    def color_mix(self, mix):
        return (1 - mix) * self.color1 + mix * self.color2

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


def progress_bar(size, radius, color_creator):
    start_pos = (radius, radius)
    end_pos = (size[0] + radius, size[1] + radius)

    progress_crop = 2

    alpha_color = (255, 255, 255, 255)
    lineType = cv2.LINE_4

    diameter = radius * 2
    hard_radius = int(radius)

    progress_bar_size = (end_pos[1] - start_pos[1] + diameter + progress_crop,
                         end_pos[0] - start_pos[0] + diameter + progress_crop)

    img = np.zeros((progress_bar_size[0], progress_bar_size[1], 4), dtype=np.uint8)

    if hard_radius > 0:
        cv2.circle(img, start_pos, hard_radius, alpha_color, -1, lineType=lineType)

    cv2.line(img, start_pos, end_pos, alpha_color, diameter, lineType=lineType)

    if hard_radius > 0:
        cv2.circle(img, end_pos, hard_radius, alpha_color, -1, lineType=lineType)

    bar_color_overlay = np.zeros(img.shape, dtype=np.uint8)
    bar_color = color_creator.create(progress_bar_size)
    bar_color_overlay[
        start_pos[1] - radius:end_pos[1] + radius + progress_crop,
        start_pos[0] - radius:end_pos[0] + radius + progress_crop,
        :
    ] = bar_color

    img[np.where(img == alpha_color)] = bar_color_overlay[np.where(img == alpha_color)]

    return img


def overlay(background, foreground, x, y, align):
    if background is None:
        return foreground

    if align == 'right':
        h, w = foreground.shape[0], foreground.shape[1]
        by_start = y
        bx_start = max(0, x-w)
        by_end = min(y+h, background.shape[0])
        bx_end = min(x, background.shape[1])
        fy_start = 0
        fx_start = 0
        fy_end = by_end-y
        fx_end = bx_end
    else:
        h, w = foreground.shape[0], foreground.shape[1]
        by_start = y
        bx_start = x
        by_end = min(y+h, background.shape[0])
        bx_end = min(x+w, background.shape[1])
        fy_start = 0
        fx_start = 0
        fy_end = by_end-y
        fx_end = bx_end-x

    if by_end - by_start < 0 or bx_end - bx_start < 0:
        return background

    overlay_image = foreground[fy_start:fy_end, fx_start:fx_end, :]
    mask = overlay_image[..., 3:] / 255.0

    background[
        by_start:by_end,
        bx_start:bx_end
    ] = (1.0 - mask) * background[
                        by_start:by_end,
                        bx_start:bx_end
                       ] + mask * overlay_image

    return background


class ImageLoader:
    def load_into(self, func):
        raise Exception('Raw usage of Image Loader forbidden, use FileImageLoader')


class FileImageLoader(ImageLoader):
    def __init__(self, file=None, prefix=''):
        self.file = file
        self.prefix = prefix

    def load_into(self, func):
        img = cv2.imread(self.file, cv2.IMREAD_UNCHANGED)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
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


class AlignLayer:
    def get_kwarg(self, key, default=None):
        if default is not None and key not in self.kwargs:
            return default
        return self.kwargs[key]

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.pos = self.get_kwarg('pos', (0, 0))
        self.align = self.get_kwarg('align', 'left')

    async def create(self, **kwargs):
        raise Exception('Raw usage of Align Layer forbidden!')

    async def overlay(self, **kwargs):
        layer = await self.create(**kwargs)
        return overlay(kwargs['background'], layer, self.pos[0], self.pos[1], self.align)


class ColorLayer(AlignLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize = self.get_kwarg('resize', (1, 1))
        self.color = SingleColor(self.get_kwarg('color', (0, 0, 0, 0)))

    async def create(self, **kwargs):
        return np.full((self.resize[1], self.resize[0], 4), self.color, dtype=np.uint8)


class EmptyLayer(ColorLayer):
    def __init__(self, **kwargs):
        kwargs['color'] = (0, 0, 0, 0)
        super().__init__(**kwargs)


class ImageLayer(AlignLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize = self.get_kwarg('resize', False)

    def validated(self, img):
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
        return img

    def resized(self, img):
        if self.resize == False:
            return img
        return cv2.resize(img, self.resize)

    async def create(self, **kwargs):
        raise Exception('Raw usage of Image Layer forbidden, use File Image Layer')


class FileImageLayer(ImageLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = self.get_kwarg('file')

    async def create(self, **kwargs):
        img = cv2.imread(self.file, cv2.IMREAD_UNCHANGED)
        img = self.validated(img)
        return self.resized(img)


class MemoryImageLayer(ImageLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.memory = self.get_kwarg('memory')

    async def create(self, **kwargs):
        img = kwargs['image_memory'][self.memory]
        img = self.validated(img)
        return self.resized(img)


class EmojiLayer(MemoryImageLayer):
    def __init__(self, **kwargs):
        kwargs['memory'] = ''
        super().__init__(**kwargs)
        self.emoji = self.get_kwarg('emoji')

    async def create(self, **kwargs):
        emoji_id = tools.from_char(self.emoji)
        if 'emojis/' + emoji_id + '.png' not in kwargs['image_memory']:
            emoji_id = '0'
        self.memory = 'emojis/' + emoji_id + '.png'
        return await super().create(**kwargs)


class WebImageLayer(ImageLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = self.get_kwarg('url')

    async def create(self, **kwargs):
        async with kwargs['session'].get(self.url) as response:
            img_bytes = await response.read()
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
        img = self.validated(img)
        return self.resized(img)


class TextLayer(AlignLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font = self.get_kwarg('font')
        self.font_size = self.get_kwarg('font_size', 16)
        self.text_align = self.get_kwarg('text_align', 'left')
        self.text = self.get_kwarg('text')
        self.color = SingleColor(self.get_kwarg('color', (0, 0, 0)))
        self.max_size = self.get_kwarg('max_size')

    async def create(self, **kwargs):
        text_full = np.zeros((self.max_size[1], self.max_size[0], 4), dtype=np.uint8)

        if self.font not in kwargs['fonts']:
            raise Exception('Error font: "' + self.font + '" was not found!')
        text_surf, _ = kwargs['fonts'][self.font].render(self.text, self.color, size=self.font_size)

        text_img_t = pygame.surfarray.pixels3d(text_surf).swapaxes(0, 1)
        text_img = np.zeros((text_img_t.shape[0], text_img_t.shape[1], 4), dtype=np.uint8)
        text_alpha = pygame.surfarray.pixels_alpha(text_surf).swapaxes(0, 1)
        text_img[:, :, 3] = text_alpha
        text_img[:, :, :3] = text_img_t
        text_size = (min(text_img.shape[1], self.max_size[0]), min(text_img.shape[0], self.max_size[1]))
        if self.text_align == 'right':
            text_full[
                :text_size[1],
                self.max_size[0] - text_size[0]:,
                :
            ] = text_img[:text_size[1], :text_size[0], :]
        else:
            text_full[
                :text_size[1],
                :text_size[0],
                :
            ] = text_img[:text_size[1], :text_size[0], :]
        return text_full


class ProgressLayer(AlignLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.percentage = self.get_kwarg('percentage')
        self.width = self.get_kwarg('width')
        self.size = self.get_kwarg('size')
        self.color = self.get_kwarg('color')

    async def create(self, **kwargs):
        adj_size = (int(self.size[0] * self.percentage), int(self.size[1] * self.percentage))
        return progress_bar(adj_size, self.width, self.color)


class ImageCreator:
    def __init__(self, loop=None, fonts=None, load_memory=None):
        self.loop = loop
        self.session = None

        self.fonts = {}
        if fonts is not None:
            for k, v in fonts.items():
                self.fonts[k] = pygame.freetype.Font(v)
                self.fonts[k].antialiased = True

        if load_memory is None:
            load_memory = []

        self.image_memory = {}
        for loader in load_memory:
            loader.load_into(self.add_to_memory)

    def add_to_memory(self, name, img):
        if name in self.image_memory:
            raise Exception('image with same name was loaded before! Use a prefix')
        self.image_memory[name] = img

    async def create(self, layers):
        img = None
        for layer in layers:
            if self.session is None:
                self.session = aiohttp.ClientSession(loop=self.loop)
            img = await layer.overlay(background=img,
                                      session=self.session,
                                      image_memory=self.image_memory,
                                      fonts=self.fonts)

        is_success, buffer = cv2.imencode('.png', img)
        io_buf = io.BytesIO(buffer)
        return io_buf
