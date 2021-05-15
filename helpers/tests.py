import settings
from helpers.imgtools import *


class ColorDummy:
    def __init__(self, rgb=(0, 255, 0)):
        self.rgb = rgb

    def to_rgb(self):
        return self.rgb


class RoleDummy:
    def __init__(self, uid=0, name='✅DummyRole', color=ColorDummy()):
        self.id = uid
        self.name = name
        self.color = color


class ChannelDummy:
    def __init__(self, channel=None):
        self.channel = channel
        self.messages = []

    async def send(self, *args, **kwargs):
        self.messages.append((args, kwargs))


class GuildDummy:
    def __init__(self, uid=0, roles=None, system_channel=ChannelDummy()):
        self.id = uid
        self.roles = roles
        self.members = []
        if self.roles is None:
            self.roles = []
        self.system_channel = system_channel

    def member_join(self, member):
        self.members.append(member)


class MemberDummy:
    def __init__(self, uid=0, name='Dummy', nick='Dummy', guild=GuildDummy(0), bot=False):
        self.id = uid
        self.name = name
        self.nick = nick
        self.avatar_url = 'https://cdn.discordapp.com/emojis/722162010514653226.png?v=1'
        self.roles = {}
        self.top_role = RoleDummy(0)
        self.guild = guild
        self.guild.member_join(self)
        self.bot = bot
        self.color = ColorDummy()
        self.messages = []

    async def send(self, msg):
        self.messages.append(msg)

    async def add_roles(self, role):
        self.roles[role.id] = True

    async def remove_roles(self, role):
        if role.id in self.roles:
            del self.roles[role.id]

    def avatar_url_as(self, *args, **kwargs):
        return self.avatar_url


class MessageDummy:
    def __init__(self, author=MemberDummy(0)):
        self.author = author


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
