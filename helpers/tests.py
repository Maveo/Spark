from settings import GLOBAL_SETTINGS
from helpers.imgtools import *


def main():
    import numpy as np
    import cv2
    import time
    import os
    import asyncio
    from helpers import tools

    SHOW_IMAGES = True

    def show_image(img):
        if SHOW_IMAGES:
            try:
                cv2.imshow('test', img)
                cv2.waitKey(0)
            except:
                pass

    class Tests:
        def __init__(self):
            self.image_creator = ImageCreator(fonts=GLOBAL_SETTINGS['FONTS'],
                                              load_memory=GLOBAL_SETTINGS['IMAGES_LOAD_MEMORY'])

        # test helper
        async def test__h1(self):
            return tools.to_char(tools.from_char('✅')) == '✅' and tools.to_char(tools.from_char('🆘')) == '🆘'

        # test image creation
        async def test__h2(self):
            rotation = 1440.0 - 10
            spin_func = lambda x: (3 * (x ** 2) - 2 * (x ** 3)) * rotation

            image = AnimatedImage(
                bg_color=(128, 128, 128),
                rotate=ImageStack([
                    ColorLayer(
                        pos=(0, 0),
                        resize=(300, 300),
                        color=SingleColor(
                            (128, 128, 128)
                        ),
                    ),
                    PieLayer(
                        align_x='center',
                        align_y='center',
                        pos=(150, 150),
                        radius=140,
                        color=LinearGradientColor(
                            color1=(0, 255, 0),
                            color2=(0, 0, 255)
                        ),
                        line_width=3,
                        border_width=10,
                        choices=[
                            EmojiLayer(
                                emoji='✅',
                                resize=(20, 20)
                            ) for _ in range(10)
                        ]
                    )
                ]),
                static_fg=ImageStack([
                    EmptyLayer(
                        resize=(300, 300)
                    ),
                    ColorLayer(
                        pos=(140, 0),
                        resize=(20, 30),
                        color=(126, 127, 0)
                    )
                ]),
                # rotation=360,
                rotation_func=spin_func,
                fps=30,
                seconds=7,
            )

            image_buffer = await self.image_creator.create(image)

            with open('test.gif', 'wb') as f:
                f.write(image_buffer.read())

            # image = cv2.imdecode(np.frombuffer(image_buffer.read(), np.uint8), -1)

            # show_image(image)
            return True

    async def run_test(test_name):
        t = Tests()

        print("TEST {}: ".format(test_name[5:]), end='')

        start = time.time()
        if await getattr(t, test_name)():
            print("SUCCESS! elapsed {}ms".format(round((time.time() - start) * 1000, 1)))
        else:
            print("FAILED! elapsed {}ms".format(round((time.time() - start) * 1000, 1)))

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    for method_name in sorted(dir(Tests)):
        if callable(getattr(Tests, method_name)) and method_name[:5] == 'test_':
            asyncio.run(run_test(method_name))


if __name__ == '__main__':
    main()
