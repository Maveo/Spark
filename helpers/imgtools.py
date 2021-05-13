import cv2
import numpy as np


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


def progress_bar(img, start_pos, end_pos, radius, color_creator):
    alpha_color = (255, 255, 255, 255)
    lineType = cv2.LINE_4

    diameter = radius*2
    hard_radius = int(radius)

    cv2.circle(img, start_pos, hard_radius, alpha_color, -1, lineType=lineType)

    cv2.line(img, start_pos, end_pos, alpha_color, hard_radius * 2, lineType=lineType)

    cv2.circle(img, end_pos, hard_radius, alpha_color, -1, lineType=lineType)

    progress_crop = 2
    progress_crop_half = 1

    progress_bar_size = (end_pos[1] - start_pos[1] + diameter + progress_crop,
                         end_pos[0] - start_pos[0] + diameter + progress_crop)

    bar_color_overlay = np.zeros(img.shape, dtype=np.uint8)
    bar_color = color_creator.create(progress_bar_size)
    bar_color_overlay[
        start_pos[1] - radius - progress_crop_half:end_pos[1] + radius + progress_crop_half,
        start_pos[0] - radius - progress_crop_half:end_pos[0] + radius + progress_crop_half,
        :
    ] = bar_color

    img[np.where(img == alpha_color)] = bar_color_overlay[np.where(img == alpha_color)]

    return img
