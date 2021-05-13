class ColorDummy:
    def __init__(self):
        self.rgb = (0, 255, 0)

    def to_rgb(self):
        return self.rgb


class RoleDummy:
    def __init__(self, uid, name='✅DummyRole'):
        self.id = uid
        self.name = name


class MemberDummy:
    def __init__(self, uid, name='Dummy', nick='Dummy', bot=False):
        self.id = uid
        self.name = name
        self.nick = nick
        self.avatar_url = 'https://cdn.discordapp.com/emojis/722162010514653226.png?v=1'
        self.roles = {}
        self.top_role = RoleDummy(0)
        self.bot = bot
        self.color = ColorDummy()

    async def add_roles(self, role):
        self.roles[role.id] = True

    async def remove_roles(self, role):
        if role.id in self.roles:
            del self.roles[role.id]

    def avatar_url_as(self, *args, **kwargs):
        return self.avatar_url


class GuildDummy:
    def __init__(self, uid, roles=None):
        self.id = uid
        self.roles = roles
        if self.roles is None:
            self.roles = []


class Tests:
    def __init__(self, bot, user_db, lvlsys_db):
        self.bot = bot
        self.user_db = user_db
        self.lvlsys_db = lvlsys_db

    # test helper
    async def test__h1(self):
        return tools.to_char(tools.from_char('✅')) == '✅' and tools.to_char(tools.from_char('🆘')) == '🆘'

    # test init
    async def test_b1(self):
        return self.user_db.all() == []

    # test join
    async def test_b2(self):
        await self.bot.member_joined_vc(MemberDummy(0), 0)
        return self.user_db.all() == [{'uid': 0, 'lvl': 1, 'xp': 0, 'xp_multiplier': 1, 'blacklist': False, 'joined': 0}]

    # test leveling 1
    async def test_b3(self):
        m = MemberDummy(0)
        await self.bot.member_joined_vc(m, 0)
        await self.bot.member_left_vc(GuildDummy(0), m, 60 * 60 * 1)
        return self.user_db.all() == [{'uid': 0, 'lvl': 1, 'xp': 60.0, 'xp_multiplier': 1, 'blacklist': False, 'joined': 0}]

    # test leveling 2
    async def test_b4(self):
        m = MemberDummy(0)
        await self.bot.member_joined_vc(m, 0)
        await self.bot.member_left_vc(GuildDummy(0), m, 60 * 60 * 5)
        return self.user_db.all() == [{'uid': 0, 'lvl': 3, 'xp': 90.0, 'xp_multiplier': 1, 'blacklist': False, 'joined': 0}]

    # test set lvlsys point
    async def test_b5(self):
        await self.bot.lvlsys_set(0, 0, 5)
        return self.lvlsys_db.all() == [{'gid': 0, 'lvlsys': {'5': 0}}]

    # test remove lvlsys point
    async def test_b6(self):
        await self.bot.lvlsys_set(0, 0, 5)
        await self.bot.lvlsys_set(0, 0, 6)
        await self.bot.lvlsys_remove(0, 5)
        return self.lvlsys_db.all() == [{'gid': 0, 'lvlsys': {'6': 0}}]

    # test role
    async def test_b7(self):
        await self.bot.lvlsys_set(0, 0, 0)
        await self.bot.lvlsys_set(0, 1, 2)
        await self.bot.lvlsys_set(0, 2, 5)
        self.user_db.insert({'uid': 0, 'lvl': 3, 'xp': 0, 'xp_multiplier': 1})
        m = MemberDummy(0)
        await self.bot.member_joined_vc(m, 0)
        await self.bot.member_left_vc(GuildDummy(0, [
            RoleDummy(0),
            RoleDummy(1),
            RoleDummy(2)
        ]), m, 0)
        return m.roles == {1: True}

    # test leaderboard
    async def test_b8(self):
        g = GuildDummy(0)
        m0 = MemberDummy(0)
        m1 = MemberDummy(1)
        await self.bot.member_joined_vc(m0, 0)
        await self.bot.member_joined_vc(m1, 0)
        await self.bot.member_left_vc(g, m0, 60 * 60 * 1)
        await self.bot.member_left_vc(g, m1, 60 * 60 * 5)
        l = await self.bot.get_leaderboard()
        return l[0]['uid'] == 1 and l[1]['uid'] == 0

    # test leaderboard rank
    async def test_b9(self):
        g = GuildDummy(0)
        m0 = MemberDummy(0)
        m1 = MemberDummy(1)
        await self.bot.member_joined_vc(m0, 0)
        await self.bot.member_joined_vc(m1, 0)
        await self.bot.member_left_vc(g, m0, 60 * 60 * 1)
        await self.bot.member_left_vc(g, m1, 60 * 60 * 5)
        rank = await self.bot.get_leaderboard_rank(m0)
        return rank == 2

    # test image creation
    async def test_b_1(self):
        m = MemberDummy(0)
        self.user_db.insert({'uid': 0, 'lvl': 3, 'xp': 0, 'xp_multiplier': 1.5})
        image = await self.bot.member_create_get_image(m)
        # print(dir(image))
        # print(image.fp)
        # with open("output.png", "wb") as f:
        #     f.write(image.fp.getbuffer())
        return True


async def run_test(test_name):
    user_db = TinyDB(storage=MemoryStorage)
    lvlsys_db = TinyDB(storage=MemoryStorage)

    b = DiscordBot(user_db, lvlsys_db)
    b.session = aiohttp.ClientSession()

    t = Tests(b, user_db, lvlsys_db)

    print("TEST {}: ".format(test_name[5:]), end='')

    start = time.time()
    if await getattr(t, test_name)():
        print("SUCCESS! elapsed {}ms".format(round((time.time() - start) * 1000, 1)))
    else:
        print("FAILED! elapsed {}ms".format(round((time.time() - start) * 1000, 1)))

    await b.stop()


def main():
    for method_name in sorted(dir(Tests)):
        if callable(getattr(Tests, method_name)) and method_name[:5] == 'test_':
            asyncio.run(run_test(method_name))


if __name__ == '__main__':
    from bot import DiscordBot
    from tinydb import TinyDB, Query, operations
    from tinydb.storages import MemoryStorage
    import time
    import os
    import asyncio
    import aiohttp
    from helpers import tools

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    main()
