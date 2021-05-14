from helpers import tools
import numpy as np
import cv2
import pygame
import pygame.freetype
import io
import os
import warnings
import aiohttp

os.environ['SDL_AUDIODRIVER'] = 'dsp'

pygame.init()


ALPHA_COLOR = (255, 255, 255, 255)
LINE_TYPE = cv2.LINE_AA


class Color:
    pass


class SingleColor(Color, np.ndarray):
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

    def alpha(self, alpha):
        return SingleColor([self[0], self[1], self[2], alpha])

    def create(self, size):
        return np.full((size[0], size[1], self.shape[0]), self, dtype=np.uint8)


class LinearGradientColor(Color):
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


def overlay(background, foreground, x, y, max_size, align_x, align_y):
    if background is None:
        return foreground

    h, w = foreground.shape[0], foreground.shape[1]

    if align_y == 'bottom':
        n_h = h
        if max_size[1] >= 0:
            n_h = min(max_size[1], h)
        by_start = max(0, y-n_h)
        by_end = min(y, background.shape[0])
        fy_start = h-n_h
        fy_end = by_end
    elif align_y == 'center':
        n_h = h
        if max_size[1] >= 0:
            n_h = min(max_size[1], h)
        hh_a = int(n_h / 2)
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
        bx_start = max(0, x-n_w)
        bx_end = min(x, background.shape[1])
        fx_start = w-n_w
        fx_end = bx_end

    elif align_x == 'center':
        n_w = w
        if max_size[0] >= 0:
            n_w = min(max_size[0], w)
        hw_a = int(n_w / 2)
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
        bx_end = min(x+w, background.shape[1])
        fx_start = 0
        fx_end = bx_end - bx_start

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
        self.used_kwargs.append(key)
        return self.kwargs[key]

    def __init__(self, **kwargs):
        self.used_kwargs = []
        self.kwargs = kwargs
        self.pos = self.get_kwarg('pos', (0, 0))
        self.align_x = self.get_kwarg('align_x', 'left')
        self.align_y = self.get_kwarg('align_y', 'top')
        self.max_size = self.get_kwarg('max_size', (-1, -1))

    def _init_finished(self):
        if 'no-check' in self.kwargs and self.kwargs['no-check'] is True:
            return
        for key in self.kwargs.keys():
            if key not in self.used_kwargs:
                warnings.warn(type(self).__name__ + ' "' + key + '" was not used')

    async def create(self, **kwargs):
        raise Exception('Raw usage of Align Layer forbidden!')

    async def overlay(self, **kwargs):
        layer = await self.create(**kwargs)
        return overlay(kwargs['background'], layer, self.pos[0], self.pos[1], self.max_size, self.align_x, self.align_y)


class ColoredLayer(AlignLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = self.get_kwarg('color', (0, 0, 0, 0))
        if not issubclass(type(self.color), Color):
            self.color = SingleColor(self.color)

    async def create(self, **kwargs):
        raise Exception('Raw usage of Colored Layer forbidden, use Color Layer!')

    def colored(self, img):
        color_overlay = self.color.create(img.shape)
        color_overlay[..., 3:] = img[..., 3:]
        return color_overlay


class ColorLayer(ColoredLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize = self.get_kwarg('resize', (1, 1))
        super()._init_finished()

    async def create(self, **kwargs):
        return self.colored(np.full((self.resize[1], self.resize[0], 4), ALPHA_COLOR, dtype=np.uint8))


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
        if self.resize is False:
            return img
        return cv2.resize(img, self.resize)

    async def create(self, **kwargs):
        raise Exception('Raw usage of Image Layer forbidden, use File Image Layer')


class FileImageLayer(ImageLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = self.get_kwarg('file')
        super()._init_finished()

    async def create(self, **kwargs):
        img = cv2.imread(self.file, cv2.IMREAD_UNCHANGED)
        img = self.validated(img)
        return self.resized(img)


class MemoryImageLayer(ImageLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.memory = self.get_kwarg('memory')
        super()._init_finished()

    async def create(self, **kwargs):
        img = kwargs['image_memory'][self.memory]
        img = self.validated(img)
        return self.resized(img)


class EmojiLayer(ImageLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.emoji = self.get_kwarg('emoji')
        super()._init_finished()

    async def create(self, **kwargs):
        emoji_id = tools.from_char(self.emoji)
        if 'emojis/' + emoji_id + '.png' not in kwargs['image_memory']:
            emoji_id = '0'
        img = kwargs['image_memory']['emojis/' + emoji_id + '.png']
        img = self.validated(img)
        return self.resized(img)


class WebImageLayer(ImageLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = self.get_kwarg('url')
        super()._init_finished()

    async def create(self, **kwargs):
        async with kwargs['session'].get(self.url) as response:
            img_bytes = await response.read()
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
        img = self.validated(img)
        return self.resized(img)


class TextLayer(ColoredLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font = self.get_kwarg('font')
        self.font_size = self.get_kwarg('font_size', 16)
        self.text = self.get_kwarg('text')
        self.max_size = self.get_kwarg('max_size')
        super()._init_finished()

    async def create(self, **kwargs):
        if self.font not in kwargs['fonts']:
            raise Exception('Error font: "' + self.font + '" was not found!')

        text_surf, _ = kwargs['fonts'][self.font].render(self.text, ALPHA_COLOR, size=self.font_size)

        text_img_t = pygame.surfarray.pixels3d(text_surf).swapaxes(0, 1)
        text_img = np.zeros((text_img_t.shape[0], text_img_t.shape[1], 4), dtype=np.uint8)
        text_alpha = pygame.surfarray.pixels_alpha(text_surf).swapaxes(0, 1)
        text_img[:, :, 3] = text_alpha
        text_img[:, :, :3] = text_img_t
        return self.colored(text_img)


class RectangleLayer(ColoredLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = self.get_kwarg('size', (0, 0))
        self.radius = self.get_kwarg('radius', 0)
        self.line_width = self.get_kwarg('line_width', -1)
        super()._init_finished()

    async def create(self, **kwargs):
        top_left = (0, 0)
        diameter = self.radius * 2
        bottom_right = (max(1, diameter - 1, self.size[1] - 1), max(1, diameter - 1, self.size[0] - 1))

        src = np.zeros((bottom_right[0] + 1, bottom_right[1] + 1, 4), dtype=np.uint8)

        #  corners:
        #  p1 - p2
        #  |     |
        #  p4 - p3

        p1 = top_left
        p2 = (bottom_right[1], top_left[1])
        p3 = (bottom_right[1], bottom_right[0])
        p4 = (top_left[0], bottom_right[0])

        corner_radius = self.radius

        thickness = self.line_width

        if thickness < 0:
            # big rect
            start_pos = (p1[0]+corner_radius, p1[1])
            end_pos = (p3[0]-corner_radius, p3[1])
            cv2.rectangle(src, start_pos, end_pos, ALPHA_COLOR, thickness=thickness, lineType=LINE_TYPE)
            start_pos = (p1[0], p1[1]+corner_radius)
            end_pos = (p3[0], p3[1]-corner_radius)
            cv2.rectangle(src, start_pos, end_pos, ALPHA_COLOR, thickness=thickness, lineType=LINE_TYPE)

        else:
            # draw straight lines
            cv2.line(src, (p1[0] + corner_radius, p1[1]), (p2[0] - corner_radius, p2[1]), ALPHA_COLOR, thickness, LINE_TYPE)
            cv2.line(src, (p2[0], p2[1] + corner_radius), (p3[0], p3[1] - corner_radius), ALPHA_COLOR, thickness, LINE_TYPE)
            cv2.line(src, (p3[0] - corner_radius, p4[1]), (p4[0] + corner_radius, p3[1]), ALPHA_COLOR, thickness, LINE_TYPE)
            cv2.line(src, (p4[0], p4[1] - corner_radius), (p1[0], p1[1] + corner_radius), ALPHA_COLOR, thickness, LINE_TYPE)

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

        return self.colored(src)


# class LineLayer(RectangleLayer):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)


class ProgressLayer(RectangleLayer):
    def __init__(self, **kwargs):
        direction = 'x'
        percentage = 1
        if 'direction' in kwargs:
            direction = kwargs['direction']
        if 'percentage' in kwargs:
            percentage = kwargs['percentage']

        if direction == 'y':
            kwargs['size'] = (kwargs['size'][0],
                              int(kwargs['size'][1] * percentage))
        else:
            kwargs['size'] = (int(kwargs['size'][0] * percentage),
                              kwargs['size'][1])

        if 'percentage' in kwargs:
            del kwargs['percentage']
        if 'direction' in kwargs:
            del kwargs['direction']
        super().__init__(**kwargs)


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
