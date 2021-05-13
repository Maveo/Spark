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

    diameter = radius*2
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

    background_width = background.shape[1]
    background_height = background.shape[0]

    if align == 'right':
        if x < 0 or y >= background_height:
            return background
    else:
        if x >= background_width or y >= background_height:
            return background

    h, w = foreground.shape[0], foreground.shape[1]

    overlay_image = foreground[..., :]
    mask = foreground[..., 3:] / 255.0

    if align == 'right':
        background[y:y+h, x-w:x] = (1.0 - mask) * background[y:y+h, x-w:x] + mask * overlay_image
    else:
        background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    return background


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

        for opt in load_memory:
            if 'directory' in opt:
                for f in os.listdir(opt['directory']):
                    if f.endswith('.png'):
                        img = cv2.imread(os.path.join(opt['directory'], f), cv2.IMREAD_UNCHANGED)
                        img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
                        self.add_to_memory(opt['prefix']+'/'+f, img)
            elif 'file' in opt:
                img = cv2.imread(opt['file'], cv2.IMREAD_UNCHANGED)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
                self.add_to_memory(opt['prefix'] + '/' + os.path.basename(opt['file']), img)
            else:
                raise Exception('I do not know what to load: {}'.format(opt))

    def add_to_memory(self, name, img):
        if name in self.image_memory:
            raise Exception('image with same name was loaded before! Use a prefix')
        self.image_memory[name] = img

    async def get_raw_image(self, options):
        if 'file' in options:
            return cv2.imread(os.path.join(options['file']), cv2.IMREAD_UNCHANGED)
        elif 'url' in options:
            if self.session is None:
                self.session = aiohttp.ClientSession(loop=self.loop)
            async with self.session.get(options['url']) as response:
                img_bytes = await response.read()
            return cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
        elif 'memory' in options:
            return self.image_memory[options['memory']]
        elif 'emoji' in options:
            emoji_id = tools.from_char(options['emoji'])
            if 'emojis/'+emoji_id+'.png' not in self.image_memory:
                emoji_id = '0'
            return self.image_memory['emojis/'+emoji_id+'.png']
        elif 'empty' in options:
            return np.zeros((1, 1, 4), dtype=np.uint8)
        else:
            raise Exception('Could not parse image options {}'.format(options))

    async def get_image(self, options):
        img = await self.get_raw_image(options)
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
        if 'resize' in options:
            img = cv2.resize(img, options['resize'])
        return img

    def get_progress_bar(self, options):
        adj_size = (int(options['size'][0]*options['percentage']), int(options['size'][1]*options['percentage']))
        return progress_bar(adj_size, options['width'], options['color'])

    def get_text(self, options):
        text_full = np.zeros((options['max_size'][1], options['max_size'][0], 4), dtype=np.uint8)
        text_surf, _ = self.fonts[options['font']].render(options['text'],
                                                          options['color'],
                                                          size=options['font_size'])
        text_img_t = pygame.surfarray.pixels3d(text_surf).swapaxes(0, 1)
        text_img = np.zeros((text_img_t.shape[0], text_img_t.shape[1], 4), dtype=np.uint8)
        text_alpha = pygame.surfarray.pixels_alpha(text_surf).swapaxes(0, 1)
        text_img[:, :, 3] = text_alpha
        text_img[:, :, :3] = text_img_t
        text_size = (min(text_img.shape[1], options['max_size'][0]), min(text_img.shape[0], options['max_size'][1]))
        if 'text_align' in options and options['text_align']:
            text_full[
                :text_size[1],
                options['max_size'][0]-text_size[0]:,
                :
            ] = text_img[:text_size[1], :text_size[0], :]
        else:
            text_full[
                :text_size[1],
                :text_size[0],
                :
            ] = text_img[:text_size[1], :text_size[0], :]
        return text_full

    async def get_layer(self, layer):
        if 'image' in layer:
            return await self.get_image(layer['image'])
        elif 'progress' in layer:
            return self.get_progress_bar(layer['progress'])
        elif 'text' in layer:
            return self.get_text(layer['text'])
        else:
            raise Exception('Could not parse layer options {}'.format(layer))

    async def overlay_layer(self, img, layer):
        pos = (0, 0)
        if 'pos' in layer:
            pos = layer['pos']
        align = 'left'
        if 'align' in layer:
            align = layer['align']
        return overlay(img, await self.get_layer(layer), pos[0], pos[1], align)

    async def create(self, layers):
        img = None
        for layer in layers:
            img = await self.overlay_layer(img, layer)

        is_success, buffer = cv2.imencode('.png', img)
        io_buf = io.BytesIO(buffer)
        return io_buf
