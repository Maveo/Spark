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
    def __init__(self, author=MemberDummy(0), guild=GuildDummy(0)):
        self.author = author
        self.guild = guild


def main():
    from bot import DiscordBot
    from tinydb import TinyDB, Query, operations
    from tinydb.storages import MemoryStorage
    import numpy as np
    import cv2
    import time
    import os
    import asyncio
    import aiohttp

    SHOW_IMAGES = False

    def show_image(img):
        if SHOW_IMAGES:
            try:
                cv2.imshow('test', img)
                cv2.waitKey(0)
            except:
                pass

    class Tests:
        def __init__(self, bot, user_db, lvlsys_db):
            self.bot = bot
            self.user_db = user_db
            self.lvlsys_db = lvlsys_db

        # test init
        async def test_1_init(self):
            return self.user_db.all() == []

        # test user joined server
        async def test_2_user_joined(self):
            m = MemberDummy()
            await self.bot.events.on_member_join(m)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and user['lvl'] == 1 and user['xp'] == 0 and len(m.messages) == 1

        # test user left server
        async def test_3_user_left(self):
            m = MemberDummy()
            await self.bot.events.on_member_join(m)
            await self.bot.events.on_member_remove(m)
            try:
                await self.bot.get_user(m)
                return False
            except KeyError:
                return True

        # test write message
        async def test_4_user_writes_message(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            msg = MessageDummy(author=m)
            await self.bot.events.on_message(msg)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and user['lvl'] == 1 and user['xp'] == 2.5

        # test bot writes message
        async def test_5_bot_writes_message(self):
            g = GuildDummy()
            m = MemberDummy(guild=g, bot=True)
            msg = MessageDummy(author=m)
            await self.bot.events.on_message(msg)
            try:
                await self.bot.get_user(m)
                return False
            except TypeError:
                return True

        # test user join vc
        async def test_6_user_join_voice_channel(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            await self.bot.events.on_voice_state_update(m, ChannelDummy(), ChannelDummy(1))
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and user['lvl'] == 1 and user['xp'] == 0

        # test bot join vc
        async def test_7_bot_join_voice_channel(self):
            g = GuildDummy()
            m = MemberDummy(guild=g, bot=True)
            await self.bot.events.on_voice_state_update(m, ChannelDummy(), ChannelDummy(1))
            try:
                await self.bot.get_user(m)
                return False
            except TypeError:
                return True

        # test user leave vc
        async def test_8_user_leave_voice_channel(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            await self.bot.member_joined_vc(m, 0)
            await self.bot.member_left_vc(m, 60 * 60 * 1)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and user['lvl'] == 1 and user['xp'] == 60

        # test bot leave vc
        async def test_9_bot_leave_voice_channel(self):
            g = GuildDummy()
            m = MemberDummy(guild=g, bot=True)
            await self.bot.events.on_voice_state_update(m, ChannelDummy(), ChannelDummy(1))
            await self.bot.events.on_voice_state_update(m, ChannelDummy(1), ChannelDummy())
            try:
                await self.bot.get_user(m)
                return False
            except TypeError:
                return True

        # test user leveling
        async def test_10_leveling(self):
            m = MemberDummy()
            await self.bot.member_joined_vc(m, 0)
            await self.bot.member_left_vc(m, 60 * 60 * 5)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and user['lvl'] == 3 and user['xp'] == 90

        # test set lvlsys point
        async def test_11_set_lvlsys_point(self):
            await self.bot.lvlsys_set(0, 0, 5)
            return self.lvlsys_db.all() == [{'gid': 0, 'lvlsys': {'5': 0}}]

        # test remove lvlsys point
        async def test_12_remove_lvlsys_point(self):
            await self.bot.lvlsys_set(0, 0, 5)
            await self.bot.lvlsys_set(0, 0, 6)
            await self.bot.lvlsys_remove(0, 5)
            return self.lvlsys_db.all() == [{'gid': 0, 'lvlsys': {'6': 0}}]

        # test giving role
        async def test_13_giving_role(self):
            await self.bot.lvlsys_set(0, 0, 0)
            await self.bot.lvlsys_set(0, 1, 2)
            await self.bot.lvlsys_set(0, 2, 5)
            g = GuildDummy(roles=[
                RoleDummy(0),
                RoleDummy(1),
                RoleDummy(2)
            ])
            m = MemberDummy(0, guild=g)
            await self.bot.member_joined_vc(m, 0)
            await self.bot.update_user(m, {'uid': 0, 'lvl': 3, 'xp': 0, 'xp_multiplier': 1})
            await self.bot.member_left_vc(m, 0)
            return m.roles == {1: True}

        # test ranking
        async def test_14_ranking(self):
            g = GuildDummy()
            m0 = MemberDummy(0, guild=g)
            m1 = MemberDummy(1, guild=g)
            await self.bot.member_joined_vc(m0, 0)
            await self.bot.member_joined_vc(m1, 0)
            await self.bot.member_left_vc(m0, 60 * 60 * 1)
            await self.bot.member_left_vc(m1, 60 * 60 * 5)

            l = await self.bot.get_ranking(g)
            return l[0]['uid'] == 1 and l[1]['uid'] == 0

        # test profile image creation
        async def test_15_profile_image(self):
            m = MemberDummy()
            await self.bot.member_joined_vc(m, 0)
            await self.bot.member_set_lvl_xp(m, 5, 50)
            image_buffer = (await self.bot.member_create_profile_image(m)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test level up image creation
        async def test_16_level_up_image(self):
            m = MemberDummy()
            image_buffer = (await self.bot.member_create_lvl_image(m, 1, 2)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test rank up image creation
        async def test_17_rank_up_image(self):
            m = MemberDummy()
            r1 = RoleDummy()
            r2 = RoleDummy()
            image_buffer = (await self.bot.member_create_rank_up_image(m, 1, 2, r1, r2)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test leaderboard image creation
        async def test_18_leaderboard_image(self):
            g = GuildDummy()
            m = [MemberDummy(x, guild=g) for x in range(10)]
            [await self.bot.check_member(x) for x in m]

            image_buffer = (await self.bot.create_leaderboard_image(m[0])).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

    async def run_test(method, test_number, test_name):
        user_db = TinyDB(storage=MemoryStorage)
        lvlsys_db = TinyDB(storage=MemoryStorage)

        b = DiscordBot(user_db, lvlsys_db)
        b.image_creator.session = aiohttp.ClientSession()

        t = Tests(b, user_db, lvlsys_db)

        print("TEST {:03d}: ".format(test_number), end='')

        start = time.time()
        if await getattr(t, method)():
            print("SUCCESS! elapsed {}ms | {}".format(round((time.time() - start) * 1000, 1), test_name))
        else:
            print("FAILED! elapsed {}ms | {}".format(round((time.time() - start) * 1000, 1), test_name))

        await b.image_creator.session.close()

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    tests = []
    for method_name in sorted(dir(Tests)):
        if callable(getattr(Tests, method_name)) and method_name[:5] == 'test_':
            splitted_name = method_name[5:].split('_')
            tests.append({'method_name': method_name,
                          'test_number': int(splitted_name[0]),
                          'test_name': ' '.join(splitted_name[1:])})

    for test in sorted(tests, key=lambda x: x['test_number']):
        asyncio.run(run_test(test['method_name'], test['test_number'], test['test_name']))


if __name__ == '__main__':
    main()
