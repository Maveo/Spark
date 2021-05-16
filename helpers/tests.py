import settings
from helpers.imgtools import *


def main():
    import numpy as np
    import cv2
    import time
    import os
    import asyncio
    import aiohttp
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
            self.image_creator = ImageCreator(loop=None,
                                              fonts=settings.FONTS,
                                              load_memory=settings.IMAGES_LOAD_MEMORY)

        # test helper
        async def test__h1(self):
            return tools.to_char(tools.from_char('✅')) == '✅' and tools.to_char(tools.from_char('🆘')) == '🆘'

        # test image creation
        async def test__h2(self):
            image_buffer = await self.image_creator.create([
                RectangleLayer(
                    pos=(0, 0),
                    line_width=-1,
                    size=(600, 150),
                    radius=20,
                    color=(55, 50, 48),
                ),
                TextLayer(
                    pos=(0, 0),
                    font='regular',
                    font_size=35,
                    text='𝕂𝔾𝕊𝟝𝟘𝟙',
                    color=(255, 255, 255),
                    max_size=(300, 35)
                )
            ])

            image = cv2.imdecode(np.frombuffer(image_buffer.read(), np.uint8), -1)

            show_image(image)
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
