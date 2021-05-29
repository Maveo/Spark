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
            image = ImageStackResolveString('''ImageStack([
    # Background
    RectangleLayer(
        pos=(0, 0),
        line_width=-1,
        size=(1200, LengthVariable() * 85 + 410),
        radius=55,
        color=(55, 50, 48),
    ),
    # Leaderboard Text Border
    RectangleLayer(
        pos=(30, 40),
        line_width=10,
        size=(1140, 180),
        radius=45,
        color=LinearGradientColor((76, 142, 217),
                                  (7, 222, 255),
                                  1)
    ),
    # Leaderboard Text
    TextLayer(
        pos=(310, 93),
        font='bold',
        font_size=100,
        text='Leaderboard',
        color=(255, 255, 255),
        max_size=(900, 100)
    ),
    # Name Header Text
    TextLayer(
        pos=(90, 255),
        font='regular',
        font_size=65,
        text='Name',
        color=(87, 87, 87),
        max_size=(300, 50)
    ),

    # Level Header Text
    TextLayer(
        pos=(1025, 255),
        font='regular',
        font_size=65,
        text='Lvl.',
        color=(87, 87, 87),
        max_size=(300, 50)
    ),

    # Members Background
    RectangleLayer(
        pos=(37, 320),
        line_width=-1,
        size=(1100, LengthVariable() * 85 + 410 - 355),
        radius=55,
        color=(65, 59, 57),
    ),

    # Levels Background
    RectangleLayer(
        pos=(978, 320),
        line_width=-1,
        size=(185, LengthVariable() * 85 + 410 - 355),
        radius=45,
        color=LinearGradientColor((130, 214, 254),
                                  (49, 177, 232),
                                  1)
    ),

    # All Users
    ListLayer(
        pos=(0, 360),
        repeat=LengthVariable(),
        template=ImageStack(
            EmptyLayer(
              resize=(1200, 85)
            ),
            TextLayer(
                pos=(135, 8),
                font='bold',
                align_x='center',
                font_size=60,
                text=IteratorVariable()('rank').formatted('#{}'),
                color=(255, 255, 255),
                max_size=(200, -1),
            ),
            EmojiLayer(
                pos=(240, 0),
                resize=(60, 60),
                emoji=IteratorVariable()(('member', 'top_role', 'name', 0,)),
            ),
            TextLayer(
                pos=(323, 8),
                font='regular',
                font_size=60,
                text=IteratorVariable()('name'),
                color=(255, 255, 255),
                max_size=(600, -1)
            ),
            TextLayer(
                pos=(1069, 8),
                font='regular',
                align_x='center',
                font_size=60,
                text=IteratorVariable()('lvl'),
                color=(29, 29, 29),
                max_size=(250, -1)
            )
        )
    )
])''')

            image_buffer = await self.image_creator.create(image({'cool': 'cool'}))
            image_res = cv2.imdecode(np.frombuffer(image_buffer.read(), np.uint8), -1)
            show_image(image_res)

            image_buffer = await self.image_creator.create(image({'cool': 'nice'}))
            image_res = cv2.imdecode(np.frombuffer(image_buffer.read(), np.uint8), -1)
            show_image(image_res)

            return True

        # test image creation
        async def test__h3(self):
            # obj = {'choices': ['🥇' for _ in range(10)], 'result': random.randint(0, 10)}
            #
            # gif_image_buffer, last_image_buffer =\
            #     await self.image_creator.create(DEFAULT_GUILD_SETTINGS['WHEEL_SPIN_IMAGE'](obj))
            #
            # with open('test.gif', 'wb') as f:
            #     f.write(gif_image_buffer.read())
            #
            # image = cv2.imdecode(np.frombuffer(gif_image_buffer.read(), np.uint8), -1)
            #
            # show_image(image)
            return True

        # test download emoji
        async def test__h4(self):
            image = ImageStack([
                EmptyLayer(
                    resize=(300, 300)
                ),
                EmojiLayer(
                    emoji='🥱',
                    pos=(150, 150),
                    resize=(30, 30)
                )
            ])

            self.image_creator.download_emojis = True
            self.image_creator.save_downloaded_emojis = False

            image_buffer = await self.image_creator.create(image)

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
