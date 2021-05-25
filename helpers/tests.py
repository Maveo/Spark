import random

from settings import GLOBAL_SETTINGS, DEFAULT_GUILD_SETTINGS
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

        async def test__h2(self):

            image = ImageStack([
                EmptyLayer(
                    resize=(300, 300)
                ),
                TextLayer(
                    pos=(150, 150),
                    align_x='center',
                    align_y='center',
                    max_size=(300, 300),
                    font='regular',
                    font_size=35,
                    text_lines=['Hey whats up', 'What you do?', 'What'],
                    text_align='right',
                    color=(255, 0, 0)
                )
            ])

            image_buffer = await self.image_creator.create(image)

            # image = cv2.imdecode(np.frombuffer(image_buffer.read(), np.uint8), -1)

            # show_image(image)
            return True

        # test image creation
        async def test__h3(self):
            obj = {'choices': ['🥇' for _ in range(10)], 'result': random.randint(0, 10)}

            image_buffer = await self.image_creator.create(DEFAULT_GUILD_SETTINGS['WHEEL_SPIN_IMAGE'](obj))

            with open('test.gif', 'wb') as f:
                f.write(image_buffer.read())

            # image = cv2.imdecode(np.frombuffer(image_buffer.read(), np.uint8), -1)

            # show_image(image)
            return True

        # test download emoji
        async def test__h4(self):
            image = ImageStack([
                EmptyLayer(
                    resize=(300, 300)
                ),
                EmojiLayer(
                    emoji='😎',
                    pos=(150, 150),
                    resize=(30, 30)
                )
            ])

            self.image_creator.download_emojis = True

            image_buffer = await self.image_creator.create(image)

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
