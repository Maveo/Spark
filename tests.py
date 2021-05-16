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
    from helpers.imgtools import ImageCreator, TextLayer, EmptyLayer
    import sqlite3
    import numpy as np
    import cv2
    import time
    import os
    import asyncio
    import aiohttp

    SHOW_IMAGES = False

    EPS = 0.00000001

    def show_image(img):
        if SHOW_IMAGES:
            try:
                cv2.imshow('test', img)
                cv2.waitKey(0)
            except:
                pass

    def float_match(f1, f2):
        return f1 - EPS < f2 < f1 + EPS

    class Tests:
        def __init__(self, bot, con):
            self.bot = bot
            self.db_conn = con

        # test init
        async def test_1_init(self):
            cur = self.db_conn.cursor()
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
            cur.execute("SELECT * FROM lvlsys")
            lvlsys = cur.fetchall()
            return users == [] and lvlsys == []

        # test user joined server
        async def test_2_user_joined(self):
            m = MemberDummy()
            await self.bot.events.on_member_join(m)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and float_match(user['lvl'], 1.0)

        # test user left server
        async def test_3_user_left(self):
            m = MemberDummy()
            await self.bot.events.on_member_join(m)
            await self.bot.events.on_member_remove(m)
            user = await self.bot.get_user(m)
            return user is None

        # test write message
        async def test_4_user_writes_message(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            msg = MessageDummy(author=m)
            self.bot.message_give_xp = 10
            await self.bot.events.on_message(msg)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and float_match(1.1, user['lvl'])

        # test bot writes message
        async def test_5_bot_writes_message(self):
            g = GuildDummy()
            m = MemberDummy(guild=g, bot=True)
            msg = MessageDummy(author=m)
            await self.bot.events.on_message(msg)
            user = await self.bot.get_user(m)
            return user is None

        # test user join vc
        async def test_6_user_join_voice_channel(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            await self.bot.member_joined_vc(m, 10)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and float_match(user['lvl'], 1.0) and float_match(user['joined'], 10)

        # test bot join vc
        async def test_7_bot_join_voice_channel(self):
            g = GuildDummy()
            m = MemberDummy(guild=g, bot=True)
            await self.bot.events.on_voice_state_update(m, ChannelDummy(), ChannelDummy(1))
            user = await self.bot.get_user(m)
            return user is None

        # test user leave vc
        async def test_8_user_leave_voice_channel(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)

            self.bot.voice_xp_per_minute = 1

            await self.bot.member_joined_vc(m, 0)
            await self.bot.member_left_vc(m, 60 * 60 * 1)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and int(user['lvl']) == 1 and self.bot.lvl_get_xp(user['lvl']) == 60

        # test bot leave vc
        async def test_9_bot_leave_voice_channel(self):
            g = GuildDummy()
            m = MemberDummy(guild=g, bot=True)
            await self.bot.events.on_voice_state_update(m, ChannelDummy(), ChannelDummy(1))
            await self.bot.events.on_voice_state_update(m, ChannelDummy(1), ChannelDummy())
            user = await self.bot.get_user(m)
            return user is None

        # test user leveling
        async def test_10_leveling(self):
            m = MemberDummy()

            self.bot.voice_xp_per_minute = 1

            await self.bot.member_joined_vc(m, 0)
            await self.bot.member_left_vc(m, 60 * 60 * 62)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and int(user['lvl']) == 38 and self.bot.lvl_get_xp(user['lvl']) == 94

        # test set lvlsys point
        async def test_11_set_lvlsys_point(self):
            await self.bot.lvlsys_set(0, 4, 5)
            await self.bot.lvlsys_set(0, 6, 7)
            lvlsys = await self.bot.lvlsys_get(0)
            return lvlsys == [{'lsid': 1, 'gid': 0, 'lvl': 5, 'rid': 4}, {'lsid': 2, 'gid': 0, 'lvl': 7, 'rid': 6}]

        # test remove lvlsys point
        async def test_12_remove_lvlsys_point(self):
            await self.bot.lvlsys_set(0, 3, 5)
            await self.bot.lvlsys_set(0, 4, 6)
            await self.bot.lvlsys_remove(0, 5)
            lvlsys = await self.bot.lvlsys_get(0)
            return lvlsys == [{'lsid': 2, 'gid': 0, 'lvl': 6, 'rid': 4}]

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

        # test blacklist
        async def test_15_get_blacklist(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            await self.bot.member_set_blacklist(m, True)
            users = list(await self.bot.get_blacklisted_users(g))
            return users == [{'uid': 0, 'gid': 0, 'lvl': 1.0, 'xp_multiplier': 1.0, 'joined': -1, 'blacklist': 1}]

        # test blacklist no message xp gain
        async def test_16_blacklist_no_message_xp_gain(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            await self.bot.member_set_blacklist(m, True)
            msg = MessageDummy(author=m)
            await self.bot.events.on_message(msg)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and int(user['lvl']) == 1 and self.bot.lvl_get_xp(user['lvl']) == 0

        # test blacklist no voice call xp gain
        async def test_16_blacklist_no_voice_xp_gain(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            await self.bot.member_set_blacklist(m, True)
            await self.bot.member_joined_vc(m, 0)
            await self.bot.member_left_vc(m, 60 * 60 * 1)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and int(user['lvl']) == 1 and self.bot.lvl_get_xp(user['lvl']) == 0

        # test leveling equality
        async def test_17_leveling_equality(self):
            lvl1 = 1
            lvl1 += self.bot.lvl_xp_add(60, lvl1)
            lvl2 = 1
            lvl2 += self.bot.lvl_xp_add(30, lvl2)
            lvl2 += self.bot.lvl_xp_add(30, lvl2)
            return float_match(lvl1, lvl2)

        # test xp boost
        async def test_18_xp_boost(self):
            m1 = MemberDummy(uid=1)

            m2 = MemberDummy(uid=2)

            await self.bot.update_user(m1, {'xp_multiplier': 2.0})

            msg = MessageDummy(author=m1)
            await self.bot.events.on_message(msg)

            msg = MessageDummy(author=m2)
            await self.bot.events.on_message(msg)

            user1 = await self.bot.get_user(m1)
            user2 = await self.bot.get_user(m2)
            return user1['lvl'] > user2['lvl']

        # test negative xp boost
        async def test_19_negative_xp_boost(self):
            m = MemberDummy()

            await self.bot.update_user(m, {'xp_multiplier': -250.0})

            msg = MessageDummy(author=m)

            self.bot.message_give_xp = 1

            await self.bot.events.on_message(msg)
            user = await self.bot.get_user(m)

            return self.bot.get_lvl(user['lvl']) == -2 and self.bot.lvl_get_xp(user['lvl']) == 50

        # test lvlsys embed
        async def test_801_lvlsys_get_embed(self):
            roles = [
                RoleDummy(1),
                RoleDummy(10),
                RoleDummy(5),
                RoleDummy(3),
            ]
            [await self.bot.lvlsys_set(0, role.id, role.id) for role in roles]
            g = GuildDummy(uid=0, roles=roles)
            embed = await self.bot.lvlsys_get_embed(g)
            return embed.description.split('\n')[0] == 'Level: 10 | Role: ✅DummyRole | ID: 10'

        # test profile image creation
        async def test_901_profile_image(self):
            m = MemberDummy()
            await self.bot.member_joined_vc(m, 0)
            await self.bot.member_set_lvl_xp(m, 5.5)

            def _profile_image(x):
                d = list(x.items())
                layers = [
                    EmptyLayer(resize=(900, len(d)*20 + 20)),
                    TextLayer(pos=(0, 0), color=(255, 255, 255), text='PROFILE IMAGE')
                ]
                for i in range(len(d)):
                    layers.append(TextLayer(pos=(0, i*20+20), color=(255, 255, 255), text=str(d[i])))
                return layers

            self.bot.profile_image = _profile_image

            image_buffer = (await self.bot.member_create_profile_image(m)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test level up image creation
        async def test_902_level_up_image(self):
            m = MemberDummy()

            def _level_up_image(x):
                d = list(x.items())
                layers = [
                    EmptyLayer(resize=(900, len(d)*20 + 20)),
                    TextLayer(pos=(0, 0), color=(255, 255, 255), text='LEVEL UP IMAGE')
                ]
                for i in range(len(d)):
                    layers.append(TextLayer(pos=(0, i*20+20), color=(255, 255, 255), text=str(d[i])))
                return layers

            self.bot.level_up_image = _level_up_image

            image_buffer = (await self.bot.member_create_lvl_image(m, 1, 2)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test rank up image creation
        async def test_903_rank_up_image(self):
            m = MemberDummy()
            r1 = RoleDummy()
            r2 = RoleDummy()

            def _rank_up_image(x):
                d = list(x.items())
                layers = [
                    EmptyLayer(resize=(900, len(d)*20)),
                    TextLayer(pos=(0, 0), color=(255, 255, 255), text='RANK UP IMAGE')
                ]
                for i in range(len(d)):
                    layers.append(TextLayer(pos=(0, i*20+20), color=(255, 255, 255), text=str(d[i])))
                return layers

            self.bot.rank_up_image = _rank_up_image

            image_buffer = (await self.bot.member_create_rank_up_image(m, 1, 2, r1, r2)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test leaderboard image creation
        async def test_904_leaderboard_image(self):
            g = GuildDummy()
            m = [MemberDummy(x, guild=g) for x in range(10)]
            [await self.bot.check_member(x) for x in m]

            def _ranking_image(x):
                d = x
                layers = [
                    EmptyLayer(resize=(1500, len(d)*20 + 20)),
                    TextLayer(pos=(0, 0), color=(255, 255, 255), text='RANKING IMAGE')
                ]
                for i in range(len(d)):
                    layers.append(TextLayer(pos=(0, i*20+20), color=(255, 255, 255), text=str(d[i])))
                return layers

            self.bot.ranking_image = _ranking_image

            image_buffer = (await self.bot.create_leaderboard_image(m[0])).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

    async def run_test(method, test_number, test_name):
        con = sqlite3.connect(":memory:")

        b = DiscordBot(con, use_slash_commands=False)

        b.set_image_creator(ImageCreator(loop=b.bot.loop, fonts={}, load_memory=[]))

        b.image_creator.session = aiohttp.ClientSession()

        t = Tests(b, con)

        print("TEST {:03d}: ".format(test_number), end='')

        result = False
        start = time.time()
        if await getattr(t, method)():
            print("SUCCESS! elapsed {}ms | {}".format(round((time.time() - start) * 1000, 1), test_name))
            result = True
        else:
            print("FAILED! elapsed {}ms | {}".format(round((time.time() - start) * 1000, 1), test_name))

        await b.image_creator.session.close()
        return result

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    tests = []
    for method_name in sorted(dir(Tests)):
        if callable(getattr(Tests, method_name)) and method_name[:5] == 'test_':
            splitted_name = method_name[5:].split('_')
            tests.append({'method_name': method_name,
                          'test_number': int(splitted_name[0]),
                          'test_name': ' '.join(splitted_name[1:])})

    results = []
    for test in sorted(tests, key=lambda x: x['test_number']):
        res = asyncio.run(run_test(test['method_name'], test['test_number'], test['test_name']))
        results.append((test, res))

    failed_tests = list(filter(lambda x: not x[1], results))
    print('Total amount of Tests: {} | Tests Failed: {} [{}]'.format(
        len(tests),
        len(failed_tests),
        ', '.join(map(lambda x: 'TEST {} ({})'.format(x[0]['test_number'], x[0]['test_name']), failed_tests))))


if __name__ == '__main__':
    main()
