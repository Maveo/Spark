import types


class ColorDummy:
    def __init__(self, rgb=(0, 255, 0)):
        self.rgb = rgb

    def to_rgb(self):
        return self.rgb


class RoleDummy:
    def __init__(self, uid=0, name='✅DummyRole', color=None):
        self.id = uid
        self.name = name
        if color is None:
            color = ColorDummy()
        self.color = color


class ChannelDummy:
    def __init__(self, uid=0):
        self.id = uid
        self.messages = []

    async def send(self, *args, **kwargs):
        self.messages.append((args, kwargs))


class GuildDummy:
    def __init__(self, uid=0, roles=None, system_channel=None):
        self.id = uid
        self.roles = roles
        self.members = []
        if self.roles is None:
            self.roles = []
        if system_channel is None:
            system_channel = ChannelDummy()
        self.system_channel = system_channel
        self.icon_url = 'https://cdn.discordapp.com/icons/188893186435973121/a_71ba803956e5189b9dab7d5d2d6b331f.png'

    def member_join(self, member):
        self.members.append(member)

    def icon_url_as(self, *args, **kwargs):
        return self.icon_url


class VoiceDummy:
    def __init__(self, channel=None):
        if channel is None:
            channel = ChannelDummy()
        self.channel = channel


class MemberDummy:
    def __init__(self,
                 uid=0,
                 name='Dummy',
                 nick='Dummy',
                 display_name='Dummy',
                 guild=None,
                 bot=False,
                 voice=None):
        self.id = uid
        self.name = name
        self.nick = nick
        self.display_name = display_name
        self.avatar_url = 'https://cdn.discordapp.com/emojis/722162010514653226.png?v=1'
        self.roles = {}
        self.top_role = RoleDummy(0)
        if guild is None:
            guild = GuildDummy()
        self.guild = guild
        self.guild.member_join(self)
        if voice is None:
            voice = VoiceDummy()
        self.voice = voice
        self.bot = bot
        self.color = ColorDummy()
        self.messages = []

    async def send(self, *args, **kwargs):
        self.messages.append((args, kwargs))

    async def add_roles(self, role):
        self.roles[role.id] = True

    async def remove_roles(self, role):
        if role.id in self.roles:
            del self.roles[role.id]

    def avatar_url_as(self, *args, **kwargs):
        return self.avatar_url


class MessageDummy:
    def __init__(self, uid=0, content='', author=None, guild=None, channel=None):
        self.id = uid
        self.content = content
        if author is None:
            author = MemberDummy()
        self.author = author
        if guild is None:
            guild = GuildDummy()
        self.guild = guild
        if channel is None:
            channel = ChannelDummy()
        self.channel = channel


def main():
    from bot import DiscordBot, ENUMS
    from helpers.imgtools import ImageCreator, TextLayer, EmptyLayer
    import sqlite3
    import numpy as np
    import cv2
    import time
    import os
    import asyncio

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

            self.bot.default_guild_settings['SEND_WELCOME_IMAGE'] = False

            await self.bot.events.on_member_join(m)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and float_match(user['lvl'], 1.0)

        # test user left server
        async def test_3_user_left(self):
            m = MemberDummy()

            self.bot.default_guild_settings['SEND_WELCOME_IMAGE'] = False

            await self.bot.events.on_member_join(m)
            await self.bot.events.on_member_remove(m)
            user = await self.bot.get_user(m)
            return user is None

        # test write message
        async def test_4_user_writes_message(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            msg = MessageDummy(author=m)

            self.bot.default_guild_settings['MESSAGE_XP'] = 10

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

            self.bot.default_guild_settings['VOICE_XP_PER_MINUTE'] = 60

            await self.bot.member_joined_vc(m, 0)
            await self.bot.member_left_vc(m, 60 * 1 * 1)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and int(user['lvl']) == 1 and self.bot.lvl_get_xp(user['lvl']
                                                                                      ) == 60 and user['joined'] == -1

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
            g = GuildDummy()
            m = MemberDummy(guild=g)

            self.bot.default_guild_settings['LEVEL_UP_IMAGE'] = lambda x: []

            self.bot.default_guild_settings['VOICE_XP_PER_MINUTE'] = 60

            await self.bot.member_joined_vc(m, g.id)
            await self.bot.member_left_vc(m, 60 * 1 * 62)
            user = await self.bot.get_user(m)
            return user['uid'] == 0 and int(user['lvl']) == 38 and self.bot.lvl_get_xp(user['lvl']) == 94 and len(
                g.system_channel.messages) == 1

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

            self.bot.default_guild_settings['MESSAGE_XP'] = 1

            await self.bot.events.on_message(msg)
            user = await self.bot.get_user(m)

            return self.bot.get_lvl(user['lvl']) == -2 and self.bot.lvl_get_xp(user['lvl']) == 50

        # test update all voice users
        async def test_20_update_all_voice_users(self):
            g = GuildDummy(uid=0)

            mbs = [MemberDummy(x, guild=g) for x in range(5)]
            [await self.bot.member_joined_vc(x, 0) for x in mbs]

            self.bot.default_guild_settings['VOICE_XP_PER_MINUTE'] = 60

            t = 60 * 1 * 6

            self.bot.bot.get_guild = types.MethodType(lambda *args: g, self.bot.bot)

            await self.bot.update_all_voice_users(t)
            users = [await self.bot.get_user(x) for x in mbs]
            return False not in map(lambda x: float_match(x['lvl'], 4.6) and x['joined'] == t, users) and len(g.system_channel.messages) == 5

        # test update all voice users
        async def test_21_all_blacklisted_users_no_voice_update(self):
            mbs = [MemberDummy(x) for x in range(5)]
            [await self.bot.member_joined_vc(x, 0) for x in mbs]
            [await self.bot.member_set_blacklist(x, True) for x in mbs]

            self.bot.default_guild_settings['VOICE_XP_PER_MINUTE'] = 60

            t = 60 * 1 * 1

            await self.bot.update_all_voice_users(t)
            users = [await self.bot.get_user(x) for x in mbs]
            return False not in map(lambda x: float_match(x['lvl'], 1.0) and x['joined'] == t, users)

        # test set guild setting
        async def test_22_set_guild_settings(self):
            await self.bot.set_setting(0, 'VOICE_XP_PER_MINUTE', '10')
            await self.bot.set_setting(0, 'VOICE_XP_PER_MINUTE', '70')
            await self.bot.set_setting(0, 'MESSAGE_XP', '50')
            return await self.bot.get_setting(0, 'VOICE_XP_PER_MINUTE') == 70\
                and await self.bot.get_setting(0, 'MESSAGE_XP') == 50

        # test multiple guilds same user
        async def test_23_multiple_guilds_same_user(self):
            g0 = GuildDummy(0)
            g1 = GuildDummy(1)
            m0 = MemberDummy(guild=g0)
            m1 = MemberDummy(guild=g1)
            await self.bot.events.on_member_join(m0)
            await self.bot.events.on_member_join(m1)
            await self.bot.member_set_blacklist(m0, True)
            user0 = await self.bot.get_user(m0)
            user1 = await self.bot.get_user(m1)
            return user0['blacklist'] == 1 and user1['blacklist'] == 0

        # test boost user
        async def test_24_boost_user(self):
            g = GuildDummy()
            m0 = MemberDummy(0, guild=g)
            m1 = MemberDummy(1, guild=g)

            self.bot.default_guild_settings['BOOST_EXPIRES_DAYS'] = 60

            await self.bot.set_boost_user(m0, m1)
            user_boost = await self.bot.get_boost_user(m0, time.time())
            return user_boost['boostedid'] == 1\
                and 59.9 < (user_boost['expires'] - time.time()) / (24 * 60 * 60) < 60.1

        # test boosting yourself
        async def test_25_boost_yourself(self):
            g = GuildDummy()
            m0 = MemberDummy(0, guild=g)

            self.bot.default_guild_settings['BOOST_EXPIRES_DAYS'] = 60

            boost_result = await self.bot.set_boost_user(m0, m0)
            user_boost = await self.bot.get_boost_user(m0, time.time())
            return boost_result == ENUMS.BOOSTING_YOURSELF_FORBIDDEN and user_boost is None

        # test boost while boost has not ended
        async def test_26_boost_while_boost_not_ended(self):
            g = GuildDummy()
            m0 = MemberDummy(0, guild=g)
            m1 = MemberDummy(1, guild=g)
            m2 = MemberDummy(2, guild=g)

            self.bot.default_guild_settings['BOOST_EXPIRES_DAYS'] = 60

            await self.bot.set_boost_user(m0, m1)

            boost_succes = await self.bot.set_boost_user(m0, m2)

            user_boost = await self.bot.get_boost_user(m0, time.time())

            return boost_succes == ENUMS.BOOST_NOT_EXPIRED and user_boost['boostedid'] == 1

        # test boost adds xp multiplier
        async def test_27_boost_adds_xp_multiplier(self):
            g = GuildDummy()
            m0 = MemberDummy(0, guild=g)
            m1 = MemberDummy(1, guild=g)
            m2 = MemberDummy(2, guild=g)

            self.bot.default_guild_settings['BOOST_EXPIRES_DAYS'] = 60
            self.bot.default_guild_settings['BOOST_ADD_XP_MULTIPLIER'] = 5

            await self.bot.set_boost_user(m1, m0)
            await self.bot.set_boost_user(m2, m0)
            adds = await self.bot.xp_multiplier_adds(m0.id, g.id)
            return adds == 10

        # test boost xp multiplier expires
        async def test_28_boost_xp_multiplier_expires(self):
            g = GuildDummy()
            m0 = MemberDummy(0, guild=g)
            m1 = MemberDummy(1, guild=g)
            m2 = MemberDummy(2, guild=g)

            self.bot.default_guild_settings['BOOST_EXPIRES_DAYS'] = -1
            self.bot.default_guild_settings['BOOST_ADD_XP_MULTIPLIER'] = 5

            await self.bot.set_boost_user(m1, m0)
            await self.bot.set_boost_user(m2, m0)
            adds = await self.bot.xp_multiplier_adds(m0.id, g.id)
            return adds == 0

        # test create promo code
        async def test_29_create_promo_code(self):
            g = GuildDummy()
            m0 = MemberDummy(0, guild=g)
            m1 = MemberDummy(1, guild=g)

            self.bot.default_guild_settings['PROMO_CODE_EXPIRES_HOURS'] = 60

            promo_code = await self.bot.create_promo_code(m0)

            promo = await self.bot.get_promo_code(m1, promo_code)

            return promo['uid'] == 0 and 59.9 < (promo['expires'] - time.time()) / (60 * 60) < 60.1

        # test promo code expires
        async def test_30_promo_code_expires(self):
            g = GuildDummy()
            m0 = MemberDummy(0, guild=g)
            m1 = MemberDummy(1, guild=g)

            self.bot.default_guild_settings['PROMO_CODE_EXPIRES_HOURS'] = -1

            promo_code = await self.bot.create_promo_code(m0)

            result = await self.bot.get_promo_code(m1, promo_code)

            return result is None

        # test promo code boosts
        async def test_31_promo_code_boosts(self):
            g = GuildDummy()
            m0 = MemberDummy(0, guild=g)
            m1 = MemberDummy(1, guild=g)
            m2 = MemberDummy(2, guild=g)

            self.bot.default_guild_settings['PROMO_CODE_EXPIRES_HOURS'] = 5
            self.bot.default_guild_settings['PROMO_BOOST_EXPIRES_DAYS'] = 60.0
            self.bot.default_guild_settings['PROMO_BOOST_ADD_XP_MULTIPLIER'] = 99.0
            self.bot.default_guild_settings['PROMO_USER_SET_LEVEL'] = 99.0

            promo_code = await self.bot.create_promo_code(m0)

            promo1 = await self.bot.get_promo_code(m1, promo_code)
            promo2 = await self.bot.get_promo_code(m2, promo_code)

            await self.bot.use_promo_code(m1, promo1)
            await self.bot.use_promo_code(m2, promo2)

            adds = await self.bot.xp_multiplier_adds(m0.id, g.id)

            user1 = await self.bot.get_user(m1)
            user2 = await self.bot.get_user(m2)

            return adds == 198 and user1['lvl'] == 99 and user2['lvl'] == 99

        # test reaction system
        async def test_32_reaction_system(self):
            g = GuildDummy()
            m = MemberDummy(guild=g)
            c = ChannelDummy()
            msg = MessageDummy(author=m, content='ping', channel=c)
            await self.bot.set_reaction(g.id, msg.content, 'pong')
            await self.bot.events.on_message(msg)
            return c.messages == [(('pong',), {})]

        # test message reactions
        async def test_33_message_reaction(self):
            r = RoleDummy(0)
            g = GuildDummy(roles=[r])
            m = MemberDummy(guild=g)
            msg = MessageDummy()
            emoji = '😁'
            await self.bot.add_msg_reaction(g.id, msg.id, emoji, 'add-role', r.id)
            await self.bot.add_msg_reaction(g.id, msg.id, emoji, 'dm', 'test')
            await self.bot.msg_reaction_event(m, msg.id, emoji)
            return m.roles == {0: True} and m.messages == [(('test',), {})]

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

        # test boost embed
        async def test_802_boost_get_embed(self):
            g = GuildDummy()
            m0 = MemberDummy(0, display_name='User0', guild=g)
            m1 = MemberDummy(1, display_name='User1', guild=g)

            self.bot.default_guild_settings['BOOST_EXPIRES_DAYS'] = 7.0
            self.bot.default_guild_settings['BOOST_ADD_XP_MULTIPLIER'] = 5

            await self.bot.set_boost_user(m0, m1)
            embed = await self.bot.boost_get_embed(m1)
            return embed.fields[0].value == 'By *User0* expires in **6** days **23** hours'

        # test profile image creation
        async def test_901_profile_image(self):
            m = MemberDummy()
            await self.bot.member_joined_vc(m, 0)
            await self.bot.member_set_lvl(m, 5.5)

            image_buffer = (await self.bot.member_create_profile_image(m)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test level up image creation
        async def test_902_level_up_image(self):
            m = MemberDummy()

            image_buffer = (await self.bot.member_create_lvl_image(m, 1, 2)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test rank up image creation
        async def test_903_rank_up_image(self):
            m = MemberDummy()
            r1 = RoleDummy()
            r2 = RoleDummy()

            image_buffer = (await self.bot.member_create_rank_up_image(m, 1, 2, r1, r2)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test leaderboard image creation
        async def test_904_leaderboard_image(self):
            g = GuildDummy()
            m = [MemberDummy(x, guild=g) for x in range(10)]
            [await self.bot.check_member(x) for x in m]

            image_buffer = (await self.bot.create_leaderboard_image(m[0])).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

        # test welcome image creation
        async def test_905_welcome_image(self):
            m = MemberDummy(display_name='skillor')
            image_buffer = (await self.bot.member_create_welcome_image(m)).fp.getbuffer()
            image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), -1)

            show_image(image)
            return True

    async def run_test(method, test_number, test_name):
        con = sqlite3.connect(":memory:")

        from settings import GLOBAL_SETTINGS, DEFAULT_GUILD_SETTINGS

        b = DiscordBot(con, use_slash_commands=False, default_guild_settings=DEFAULT_GUILD_SETTINGS.copy())

        b.set_image_creator(ImageCreator(fonts=GLOBAL_SETTINGS['FONTS'],
                                         load_memory=GLOBAL_SETTINGS['IMAGES_LOAD_MEMORY']))

        t = Tests(b, con)

        print("TEST {:03d}: ".format(test_number), end='')

        error = 'Test Failed'

        start = time.time()
        try:
            if await getattr(t, method)():
                print("SUCCESS! elapsed {}ms | {}".format(round((time.time() - start) * 1000, 1), test_name))
                return True
        except Exception as e:
            error = str(e)

        print("FAILED! elapsed {}ms | {} | Error: {}"
              .format(round((time.time() - start) * 1000, 1), test_name, error))
        return False

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
    start_time = time.time()
    for test in sorted(tests, key=lambda x: x['test_number']):
        res = asyncio.run(run_test(test['method_name'], test['test_number'], test['test_name']))
        results.append((test, res))

    run_time = time.time() - start_time

    failed_tests = list(filter(lambda x: not x[1], results))
    print('Total amount of Tests: {} | Total time: {}s | Tests Failed: {} [{}]'.format(
        len(tests),
        round(run_time, 1),
        len(failed_tests),
        ', '.join(map(lambda x: 'TEST {} ({})'.format(
            x[0]['test_number'],
            x[0]['test_name']
        ), failed_tests))))

    if len(failed_tests) > 0:
        exit(1)


if __name__ == '__main__':
    main()
