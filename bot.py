import discord
from discord.ext import commands
from discord.utils import get

from helpers import tools, imgtools

import sqlite3
import asyncio
import types
import os
import time
import random
import string
from ast import literal_eval


class ENUMS:
    BOOST_SUCCESS = 0
    BOOSTING_YOURSELF_FORBIDDEN = 1
    BOOST_NOT_EXPIRED = 2


class DiscordBot:
    def __init__(self,
                 db_conn,
                 update_voice_xp_interval=-1,
                 command_prefix='>',
                 description='',
                 default_guild_settings=None,
                 image_creator=None,
                 print_logging=False,
                 use_slash_commands=False
                 ):

        if default_guild_settings is None:
            default_guild_settings = {}

        self.default_guild_settings = default_guild_settings

        intents = discord.Intents.default()
        intents.members = True
        intents.reactions = True

        self.print_logging = print_logging

        self.update_voice_xp_interval = update_voice_xp_interval

        self.db_conn = db_conn

        def _dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.db_conn.row_factory = _dict_factory
        cur = self.db_conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                uid INTEGER,
                gid INTEGER,
                lvl REAL NOT NULL,
                xp_multiplier REAL NOT NULL,
                joined INTEGER NOT NULL,
                blacklist INTEGER NOT NULL,
                PRIMARY KEY (uid, gid)
            );''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS lvlsys (
                lsid INTEGER PRIMARY KEY,
                gid INTEGER NOT NULL,
                lvl INTEGER NOT NULL,
                rid INTEGER NOT NULL
            );''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS settings (
              gid INTEGER NOT NULL,
              skey TEXT NOT NULL,
              svalue TEXT NOT NULL,
              PRIMARY KEY (gid, skey)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS boosts (
              uid INTEGER NOT NULL, 
              gid INTEGER NOT NULL, 
              boostedid INTEGER NOT NULL,
              expires INTEGER NOT NULL,
              PRIMARY KEY (uid, gid)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS promos (
              uid INTEGER NOT NULL, 
              gid INTEGER NOT NULL,
              code TEXT NOT NULL,
              expires INTEGER NOT NULL,
              PRIMARY KEY (uid, gid),
              UNIQUE (gid, code)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS promo_boosts (
                  uid INTEGER NOT NULL, 
                  gid INTEGER NOT NULL, 
                  pid INTEGER NOT NULL,
                  expires INTEGER NOT NULL,
                  PRIMARY KEY (uid, gid)
                );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS reactions (
                  gid INTEGER NOT NULL, 
                  trigger TEXT NOT NULL,
                  reaction TEXT NOT NULL,
                  PRIMARY KEY (gid, trigger)
                );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS msgreactions (
                  gid INTEGER NOT NULL,
                  msgid INTEGER NOT NULL,
                  reaction TEXT NOT NULL,
                  actiontype TEXT NOT NULL,
                  action TEXT NOT NULL
                );
        ''')

        self.db_conn.commit()

        self.bot = commands.Bot(command_prefix=command_prefix,
                                description=description,
                                intents=intents,
                                help_command=None)

        self.events = self.Events(self)
        self.commands = self.Commands(self)

        self.bot.add_cog(self.events)
        self.bot.add_cog(self.commands)

        if use_slash_commands:
            from discord_slash import cog_ext, SlashCommand, SlashContext
            from discord_slash.utils.manage_commands import create_option

            self.slash = SlashCommand(self.bot, sync_commands=True)

            def _slash_callback(command):
                async def call(ctx: SlashContext, args=''):
                    async def _none(*_):
                        pass

                    class _Channel:
                        def __init__(self, cid=None):
                            self.id = cid

                    class _Message:
                        def __init__(self, author=None, channel_id=None):
                            self.author = author
                            self.guild = None
                            try:
                                self.guild = author.guild
                            except AttributeError:
                                pass
                            self.channel = _Channel(cid=channel_id)

                    ctx.trigger_typing = types.MethodType(_none, ctx)
                    ctx.message = _Message(author=ctx.author, channel_id=ctx.channel_id)

                    cargs = [ctx] + ([] if args == '' else args.split(' '))
                    try:
                        if await command.can_run(ctx):
                            await command.callback(self.commands, *cargs)
                    except commands.CommandError as error:
                        await self.events.on_command_error(ctx, error)

                return call

            for c in self.bot.commands:
                self.slash.add_slash_command(cmd=_slash_callback(c),
                                             name=c.name,
                                             description=c.help,
                                             options=[
                                                 create_option(
                                                     name="args",
                                                     description="Arguments",
                                                     option_type=3,
                                                     required=False
                                                 )
                                             ])

        self.image_creator = image_creator

    def set_image_creator(self, image_creator):
        self.image_creator = image_creator

    def run(self, token):
        async def _update_vc_xp():
            if self.update_voice_xp_interval > 0:
                while True:
                    await asyncio.sleep(self.update_voice_xp_interval)
                    await self.update_all_voice_users(time.time())

        self.bot.loop.create_task(_update_vc_xp())
        self.bot.run(token)

    def lprint(self, *args):
        if self.print_logging:
            print(*args)

    @staticmethod
    def get_lvl(lvl):
        if lvl < 0:
            return int(lvl) - 1
        else:
            return int(lvl)

    @staticmethod
    def max_xp_for(lvl):
        return max(100, DiscordBot.get_lvl(lvl) * 10 + 90)

    @staticmethod
    def xp_for(xp, boost):
        return round(xp * boost, 2)

    @staticmethod
    def lvl_xp_add(xp, lvl):
        return xp / DiscordBot.max_xp_for(lvl)

    @staticmethod
    def lvl_get_xp(lvl):
        return int((abs(lvl) % 1) * DiscordBot.max_xp_for(lvl))

    @staticmethod
    async def search_member(ctx, search):
        if search[:2] == '<@' and search[-1] == '>':
            search = search[2:-1]
            if search[0] == '!':
                search = search[1:]
        if search.isnumeric():
            member = get(ctx.message.guild.members, id=int(search))
            if member is not None and not member.bot:
                return member
        member = get(ctx.message.guild.members, nick=search)
        if member is not None and not member.bot:
            return member
        member = get(ctx.message.guild.members, name=search)
        if member is not None and not member.bot:
            return member
        return None

    @staticmethod
    async def search_text_channel(ctx, search):
        if search.isnumeric():
            channel = get(ctx.author.guild.channels, name=int(search), type=discord.ChannelType.text)
            if channel is not None:
                return channel
        channel = get(ctx.author.guild.channels, name=search, type=discord.ChannelType.text)
        if channel is not None:
            return channel
        return None

    async def xp_multiplier_adds(self, member_id, guild_id):
        xp_adds = 0
        cur = self.db_conn.cursor()

        # user boosts by >boost
        cur.execute('SELECT COUNT(*) as count FROM boosts WHERE gid=? AND boostedid=? AND expires>?',
                    (guild_id, member_id, time.time(),))
        xp_adds += cur.fetchone()['count'] * await self.get_setting(guild_id, 'BOOST_ADD_XP_MULTIPLIER')

        # boosted by promo code
        cur.execute('SELECT COUNT(*) as count FROM promo_boosts WHERE gid=? AND pid=? AND expires>?',
                    (guild_id, member_id, time.time(),))
        xp_adds += cur.fetchone()['count'] * await self.get_setting(guild_id, 'PROMO_BOOST_ADD_XP_MULTIPLIER')

        return xp_adds

    async def info_get_embed(self, member):
        await self.check_member(member)
        embed = discord.Embed(title=member.display_name,
                              description='',
                              color=discord.Color.green())
        embed.set_thumbnail(url=member.avatar_url)
        data = await self.get_user(member)

        embed.add_field(name='ID', value='{}'.format(data['uid']), inline=False)
        embed.add_field(name='Level', value='{:.2f}'.format(data['lvl']), inline=False)
        base_xp_mult = data['xp_multiplier']
        embed.add_field(name='Base XP Multiplier', value='{:.2f}'.format(base_xp_mult), inline=False)
        xp_mult = base_xp_mult + await self.xp_multiplier_adds(member.id, member.guild.id)
        embed.add_field(name='Current XP Multiplier', value='{:.2f}'.format(xp_mult), inline=False)

        if data['joined'] < 0:
            embed.add_field(name='Last XP Update',
                            value='None',
                            inline=False)
        else:
            embed.add_field(name='Last XP Update',
                            value='{}s ago'.format(int(time.time() - data['joined'])),
                            inline=False)

        embed.add_field(name='Blacklisted', value='{}'.format(bool(data['blacklist'])), inline=False)

        boost_data = await self.boost_get_infos(member)

        if boost_data['boosting'] is None:
            embed.add_field(name='Boosting',
                            value='None',
                            inline=False)
        else:
            embed.add_field(name='Boosting',
                            value='*{}*, expires in **{}** days **{}** hours'
                            .format(boost_data['boosting_name'],
                                    boost_data['boosting_remaining_days'],
                                    boost_data['boosting_remaining_hours']),
                            inline=False)

        def _get_value(arr):
            if len(arr) > 0:
                return '\n'.join(arr)
            return 'Empty'

        embed.add_field(name='Boosts',
                        value=_get_value(boost_data['boosts']),
                        inline=False)

        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM promo_boosts WHERE gid=? AND uid=?',
                    (member.guild.id,
                     member.id
                     ))
        promo = cur.fetchone()

        if promo is None:
            embed.add_field(name='Promoted By',
                            value='None',
                            inline=False)
        else:
            promoted_by_name = 'A USER WHO LEFT'
            promoted_by_user = get(member.guild.members, id=promo['pid'])
            if promoted_by_user is not None:
                promoted_by_name = promoted_by_user.display_name
            embed.add_field(name='Promoted By',
                            value='*{}*'.format(promoted_by_name),
                            inline=False)

        embed.add_field(name='Promo Boosts',
                        value=_get_value(boost_data['promo_boosts']),
                        inline=False)

        def _format_date(date):
            if date is None:
                return 'None'
            return date.strftime("%d.%m.%Y %H:%M")

        embed.add_field(name='Joined At',
                        value='{}'.format(_format_date(member.joined_at)),
                        inline=False)

        embed.add_field(name='Boosting Server since',
                        value='{}'.format(_format_date(member.premium_since)),
                        inline=False)

        hype_squad = None
        if member.public_flags.hypesquad_bravery:
            hype_squad = 'Brave'
        elif member.public_flags.hypesquad_brilliance:
            hype_squad = 'Brilliant'
        elif member.public_flags.hypesquad_balance:
            hype_squad = 'Balanced'

        if hype_squad is not None:
            embed.add_field(name='Hype',
                            value=hype_squad,
                            inline=False)

        return embed

    async def add_msg_reaction(self, guild_id, msg_id, reaction, action_type, action):
        cur = self.db_conn.cursor()
        cur.execute('INSERT INTO msgreactions(gid, msgid, reaction, actiontype, action)'
                    'VALUES(?, ?, ?, ?, ?);',
                    (guild_id, msg_id, reaction, action_type, action))
        self.db_conn.commit()

    async def remove_msg_reaction(self, guild_id, msg_id, reaction):
        cur = self.db_conn.cursor()
        cur.execute('DELETE FROM msgreactions WHERE gid=? AND msgid=? AND reaction=?',
                    (guild_id, msg_id, reaction,))
        self.db_conn.commit()

    async def get_all_msg_reactions(self, guild_id):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM msgreactions WHERE gid=?',
                    (guild_id,))
        return cur.fetchall()

    async def get_msg_reactions(self, guild_id, msg_id):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM msgreactions WHERE gid=? AND msgid=?',
                    (guild_id, msg_id,))
        return cur.fetchall()

    async def get_msg_reactions_by_reaction(self, guild_id, msg_id, reaction):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM msgreactions WHERE gid=? AND msgid=? AND reaction=?',
                    (guild_id, msg_id, reaction,))
        return cur.fetchall()

    async def msg_reaction_event(self, member, msg_id, emoji):
        actions = await self.get_msg_reactions_by_reaction(member.guild.id, msg_id, str(emoji))
        for action in actions:
            if action['actiontype'] == 'add-role':
                await self.give_role(member.guild, member, int(action['action']))
            elif action['actiontype'] == 'dm':
                await member.send(action['action'])

    async def set_reaction(self, guild_id, trigger, reaction):
        cur = self.db_conn.cursor()
        cur.execute('INSERT OR REPLACE INTO reactions(gid, trigger, reaction)'
                    'VALUES(?, ?, ?);',
                    (guild_id, str(trigger), str(reaction),))
        self.db_conn.commit()

    async def remove_reaction(self, guild_id, trigger):
        cur = self.db_conn.cursor()
        cur.execute('DELETE FROM reactions WHERE gid=? AND trigger=?',
                    (guild_id, str(trigger),))
        self.db_conn.commit()

    async def get_reactions(self, guild_id):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM reactions WHERE gid=?', (guild_id,))
        return cur.fetchall()

    async def get_reaction(self, guild_id, trigger):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM reactions WHERE gid=? AND trigger=?', (guild_id, str(trigger),))
        return cur.fetchone()

    async def get_boosted_by(self, member, ctime):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM boosts WHERE gid=? AND boostedid=? AND expires>?',
                    (member.guild.id, member.id, ctime,))
        return cur.fetchall()

    async def get_boost_user(self, member, ctime):
        cur = self.db_conn.cursor()

        cur.execute('SELECT * FROM boosts WHERE uid=? AND gid=? AND expires>?',
                    (member.id, member.guild.id, ctime,))
        return cur.fetchone()

    async def set_boost_user(self, member, user_to_boost):
        if member.id == user_to_boost.id:
            return ENUMS.BOOSTING_YOURSELF_FORBIDDEN
        current_time = int(time.time())
        previous_boost = await self.get_boost_user(member, current_time)
        if previous_boost is None:
            cur = self.db_conn.cursor()
            cur.execute('INSERT OR REPLACE INTO boosts(uid, gid, boostedid, expires)'
                        'VALUES(?, ?, ?, ?);',
                        (member.id, member.guild.id, user_to_boost.id, current_time
                         + (await self.get_setting(member.guild.id, 'BOOST_EXPIRES_DAYS')) * 24 * 60 * 60,))
            self.db_conn.commit()
            return ENUMS.BOOST_SUCCESS
        return ENUMS.BOOST_NOT_EXPIRED

    async def create_promo_code(self, member):
        cur = self.db_conn.cursor()
        cur.execute('DELETE FROM promos WHERE (uid=? AND gid=?) OR expires<?',
                    (member.id, member.guild.id, time.time(),))

        for i in range(5):
            promo_code = ''.join([
                random.choice(string.ascii_letters)
                for _ in range(int(await self.get_setting(member.guild.id, 'PROMO_CODE_LENGTH')))
            ])
            try:
                cur.execute('INSERT INTO promos(uid, gid, code, expires)'
                            'VALUES(?, ?, ?, ?);',
                            (member.id,
                             member.guild.id,
                             promo_code,
                             int(time.time() + (
                                 await self.get_setting(member.guild.id, 'PROMO_CODE_EXPIRES_HOURS')) * 60 * 60),
                             ))
                self.db_conn.commit()
                return promo_code
            except sqlite3.IntegrityError:
                pass
        return None

    async def get_promo_boosted_by(self, member, ctime):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM promo_boosts WHERE gid=? AND pid=? AND expires>?',
                    (member.guild.id,
                     member.id,
                     ctime,
                     ))
        return cur.fetchall()

    async def get_promo_code(self, member, promo_code):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM promos WHERE gid=? AND code=? AND expires>? AND uid!=?',
                    (member.guild.id,
                     promo_code,
                     int(time.time()),
                     member.id,
                     ))
        return cur.fetchone()

    async def use_promo_code(self, member, promo):
        await self.check_member(member)
        cur = self.db_conn.cursor()
        try:
            cur.execute('INSERT INTO promo_boosts(uid, gid, pid, expires)'
                        'VALUES(?, ?, ?, ?);',
                        (member.id,
                         member.guild.id,
                         promo['uid'],
                         int(time.time() + (
                             await self.get_setting(member.guild.id, 'PROMO_BOOST_EXPIRES_DAYS')) * 24 * 60 * 60),
                         ))
            self.db_conn.commit()

            data = await self.get_user(member)
            if bool(data['blacklist']) is True:
                return False

            promo_lvl = await self.get_setting(member.guild.id, 'PROMO_USER_SET_LEVEL')
            if promo_lvl > data['lvl']:
                await self.member_set_lvl(member, promo_lvl, old_level=data['lvl'])

            return True

        except sqlite3.IntegrityError:
            pass

        return False

    async def boost_get_infos(self, member):
        current_time = time.time()

        boosting = await self.get_boost_user(member, current_time)

        data = {'boosting': boosting}

        id_names = {}

        def _get_name(uid):
            uid = int(uid)
            if uid in id_names:
                return id_names[uid]
            m = get(member.guild.members, id=uid)
            name = 'A USER WHO LEFT'
            if m is not None:
                name = m.display_name
            id_names[uid] = name
            return name

        def _get_days_hours(expires):
            br = (expires - current_time) / (24 * 60 * 60)
            brd = int(br)
            brh = int((br - brd) * 24)
            return brd, brh

        if boosting is not None:
            member_name = _get_name(boosting['boostedid'])

            data['boosting_name'] = member_name

            boost_remaining_days, boost_remaining_hours = _get_days_hours(boosting['expires'])

            data['boosting_remaining_days'] = boost_remaining_days
            data['boosting_remaining_hours'] = boost_remaining_hours

        def _boost_to_str(boost):
            brd, brh = _get_days_hours(boost['expires'])
            return 'By *{}* expires in **{}** days **{}** hours'.format(_get_name(boost['uid']), brd, brh)

        boosted_by = await self.get_boosted_by(member, current_time)

        data['boosts'] = list(map(_boost_to_str, boosted_by))

        promo_boosted_by = await self.get_promo_boosted_by(member, current_time)

        data['promo_boosts'] = list(map(_boost_to_str, promo_boosted_by))

        return data

    async def boost_get_embed(self, member):
        data = await self.boost_get_infos(member)

        embed = discord.Embed(title='Boosts',
                              description='You are currently boosting no one!\n'
                                          'Use **"boost {member}"** to start boosting!',
                              color=discord.Color.gold())

        if data['boosting'] is not None:
            embed = discord.Embed(title='Boosts',
                                  description='You are boosting **{}**!\n'
                                              'Boost expires in **{}** days **{}** hours!'
                                  .format(data['boosting_name'],
                                          data['boosting_remaining_days'],
                                          data['boosting_remaining_hours']),
                                  color=discord.Color.gold())

        if len(data['boosts']) > 0:
            embed.add_field(name='Your Boosts (x{})'
                            .format(await self.get_setting(member.guild.id,
                                                           'BOOST_ADD_XP_MULTIPLIER')),
                            value='\n'.join(data['boosts']),
                            inline=False)

        if len(data['promo_boosts']) > 0:
            embed.add_field(name='Your Promo Boosts (x{})'
                            .format(await self.get_setting(member.guild.id,
                                                           'PROMO_BOOST_ADD_XP_MULTIPLIER')),
                            value='\n'.join(data['promo_boosts']),
                            inline=False)
        return embed

    async def get_users(self, guild):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM users WHERE gid=?', (guild.id,))
        return cur.fetchall()

    async def check_member(self, member):
        if not member.bot:
            user = await self.get_user(member)
            if user is None:
                await self.update_user(member, {
                    'lvl': 1.0,
                    'xp_multiplier': 1.0,
                    'blacklist': False
                })

    async def get_setting(self, guild_id, key):
        if key not in self.default_guild_settings:
            raise KeyError('Key "{}" not found in default guild settings!'.format(key))

        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM settings WHERE gid=? AND skey=?', (guild_id, key,))
        guild_setting = cur.fetchone()
        if guild_setting is not None:
            try:
                # TO-DO: don't use literal eval
                return type(self.default_guild_settings[key])(literal_eval(guild_setting['svalue']))
            except TypeError or ValueError:
                pass

        return self.default_guild_settings[key]

    async def get_settings(self, guild_id):
        settings = {}
        for key in self.default_guild_settings.keys():
            settings[key] = await self.get_setting(guild_id, key)
        return settings

    async def remove_setting(self, guild_id, key):
        cur = self.db_conn.cursor()
        cur.execute('DELETE FROM settings WHERE gid=? AND skey=?', (guild_id, key,))
        self.db_conn.commit()

    async def set_setting(self, guild_id, key, value):
        if key not in self.default_guild_settings:
            raise KeyError('Key "{}" not found in default guild settings!'.format(key))

        try:
            # TO-DO: don't use literal eval
            type(self.default_guild_settings[key])(literal_eval(value))
        except TypeError or ValueError:
            return False

        cur = self.db_conn.cursor()
        cur.execute('INSERT OR REPLACE INTO settings(gid, skey, svalue)'
                    'VALUES(?, ?, ?);',
                    (guild_id, key, value,))
        self.db_conn.commit()
        return True

    async def get_user(self, member):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM users WHERE uid=? AND gid=?', (member.id, member.guild.id,))
        return cur.fetchone()

    async def update_user(self, member, data):
        user = await self.get_user(member)
        if user is None:
            user = {
                'lvl': await self.get_setting(member.guild.id, 'NEW_USER_LEVEL'),
                'xp_multiplier': await self.get_setting(member.guild.id, 'NEW_USER_XP_MULTIPLIER'),
                'blacklist': False,
                'joined': -1
            }
        for k, v in data.items():
            user[k] = v
        cur = self.db_conn.cursor()
        cur.execute('INSERT OR REPLACE INTO users(uid, gid, lvl, xp_multiplier, joined, blacklist)'
                    'VALUES(?, ?, ?, ?, ?, ?);',
                    (member.id, member.guild.id, user['lvl'], user['xp_multiplier'], user['joined'], user['blacklist'],
                     ))
        self.db_conn.commit()

    async def remove_member(self, member):
        cur = self.db_conn.cursor()
        cur.execute('DELETE FROM users WHERE uid=? AND gid=?', (member.id, member.guild.id,))
        self.db_conn.commit()

    async def get_blacklisted_users(self, guild):
        users = await self.get_users(guild)
        return filter(lambda x: bool(x['blacklist']), users)

    async def get_ranking(self, guild):
        users = await self.get_users(guild)
        users = sorted(users, key=lambda x: x['lvl'], reverse=True)
        for i in range(len(users)):
            users[i]['rank'] = i + 1
        return users

    async def update_all_voice_users(self, ctime):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM users WHERE joined >= 0')
        users = cur.fetchall()

        for user in users:
            if bool(user['blacklist']) is True:
                user['joined'] = ctime
            else:
                guild = self.bot.get_guild(user['gid'])
                member = get(guild.members, id=int(user['uid']))
                if member.voice is None or member.voice.channel is None:
                    user['joined'] = 0
                else:
                    xp_earned = self.xp_for((ctime - user['joined'])
                                            * await self.get_setting(guild.id, 'VOICE_XP_PER_MINUTE') / 60,
                                            user['xp_multiplier']
                                            + await self.xp_multiplier_adds(user['uid'], user['gid']))

                    user['joined'] = ctime

                    old_level = self.get_lvl(user['lvl'])

                    user['lvl'] += self.lvl_xp_add(xp_earned, user['lvl'])

                    previous_role = member.top_role
                    await self.member_role_manage(member, user['lvl'])
                    await self.check_send_rank_level_image(member, user['lvl'], old_level, previous_role)

        cur.executemany('INSERT OR REPLACE INTO users(uid, gid, lvl, xp_multiplier, joined, blacklist)'
                        'VALUES(?, ?, ?, ?, ?, ?);',
                        map(lambda x: (x['uid'],
                                       x['gid'],
                                       x['lvl'],
                                       x['xp_multiplier'],
                                       x['joined'],
                                       x['blacklist'],), users))

        self.db_conn.commit()

    async def get_ranking_rank(self, member):
        return list(map(lambda x: x['uid'], await self.get_ranking(member.guild))).index(member.id) + 1

    async def member_create_profile_image(self, member):
        await self.check_member(member)

        #
        # Retrieve user data
        #
        data = await self.get_user(member)
        name = member.display_name

        data_xp_multiplier = data['xp_multiplier'] + await self.xp_multiplier_adds(data['uid'], data['gid'])
        data_xp = int(self.lvl_get_xp(data['lvl']))
        data_max_xp = int(self.max_xp_for(data['lvl']))
        data_percentage = data_xp / data_max_xp
        data_rank = await self.get_ranking_rank(member)

        data_obj = {'member': member,
                    'name': name,
                    'color': imgtools.rgb_to_bgr(member.color.to_rgb()),
                    'lvl': self.get_lvl(data['lvl']),
                    'xp': data_xp,
                    'max_xp': data_max_xp,
                    'xp_percentage': data_percentage,
                    'rank': data_rank,
                    'xp_multiplier': data_xp_multiplier,
                    'avatar_url': str(member.avatar_url_as(format="png"))}

        img_buf = await self.image_creator.create(
            (await self.get_setting(member.guild.id, 'PROFILE_IMAGE'))(data_obj))
        return discord.File(filename="member.png", fp=img_buf)

    async def member_create_welcome_image(self, member):
        name = member.display_name
        data_obj = {'member': member,
                    'name': name,
                    'avatar_url': str(member.avatar_url_as(format="png")),
                    'guild_icon_url': str(member.guild.icon_url_as(format="png"))}
        img_buf = await self.image_creator.create(
            (await self.get_setting(member.guild.id, 'WELCOME_IMAGE'))(data_obj))
        return discord.File(filename="welcome.png", fp=img_buf)

    async def member_create_lvl_image(self, member, old_lvl, new_lvl):
        name = member.display_name

        data_obj = {'member': member,
                    'old_lvl': self.get_lvl(old_lvl),
                    'new_lvl': self.get_lvl(new_lvl),
                    'color': imgtools.rgb_to_bgr(member.color.to_rgb()),
                    'name': name}

        img_buf = await self.image_creator.create(
            (await self.get_setting(member.guild.id, 'LEVEL_UP_IMAGE'))(data_obj))
        return discord.File(filename="lvlup.png", fp=img_buf)

    async def member_create_rank_up_image(self, member, old_lvl, new_lvl, old_role, new_role):
        name = member.display_name

        data_obj = {'member': member,
                    'old_lvl': self.get_lvl(old_lvl),
                    'new_lvl': self.get_lvl(new_lvl),
                    'old_role': old_role,
                    'new_role': new_role,
                    'old_color': imgtools.rgb_to_bgr(old_role.color.to_rgb()),
                    'new_color': imgtools.rgb_to_bgr(new_role.color.to_rgb()),
                    'name': name}

        img_buf = await self.image_creator.create(
            (await self.get_setting(member.guild.id, 'RANK_UP_IMAGE'))(data_obj))
        return discord.File(filename="rankup.png", fp=img_buf)

    async def create_ranking_image(self, member, ranked_users):
        data_obj = []
        for user in ranked_users:
            member = get(member.guild.members, id=int(user['uid']))
            if member is not None and not member.bot:
                name = member.display_name
                data_obj.append({
                    'member': member,
                    'rank': user['rank'],
                    'lvl': self.get_lvl(user['lvl']),
                    'name': name,
                    'color': imgtools.rgb_to_bgr(member.color.to_rgb())
                })

        img_buf = await self.image_creator.create(
            (await self.get_setting(member.guild.id, 'RANKING_IMAGE'))(data_obj), max_size=(-1, 8000))
        return discord.File(filename="ranking.png", fp=img_buf)

    async def create_leaderboard_image(self, member):
        ranking = await self.get_ranking(member.guild)
        return await self.create_ranking_image(member, ranking[:10])

    async def check_send_rank_level_image(self, member, lvl, old_level, old_role):
        if old_level is not None and self.get_lvl(old_level) < self.get_lvl(lvl):
            if old_role != member.top_role:
                return await member.guild.system_channel.send(
                    file=await self.member_create_rank_up_image(member,
                                                                old_level,
                                                                lvl,
                                                                old_role,
                                                                member.top_role))
            await member.guild.system_channel.send(
                file=await self.member_create_lvl_image(member,
                                                        old_level,
                                                        lvl))

    async def member_set_lvl(self, member, lvl, old_level=None):
        if not member.bot:
            await self.update_user(member, {'lvl': lvl})

            ilvl = self.get_lvl(lvl)
            previous_role = member.top_role
            await self.member_role_manage(member, ilvl)
            await self.check_send_rank_level_image(member, lvl, old_level, previous_role)

    async def update_member(self, member):
        await self.check_member(member)
        data = await self.get_user(member)
        await self.member_role_manage(member, data['lvl'])

    async def blacklist_get_embed(self, guild):
        description = []
        for user in await self.get_blacklisted_users(guild):
            member = get(guild.members, id=int(user['uid']))
            if member is not None:
                description.append(str(member))
        return discord.Embed(title="Blacklist",
                             description='\n'.join(description),
                             color=discord.Color.green())

    async def member_set_xp_multiplier(self, member, xp_multiplier):
        await self.check_member(member)
        await self.update_user(member, {'xp_multiplier': xp_multiplier})

    async def member_set_blacklist(self, member, blacklist):
        await self.check_member(member)
        await self.update_user(member, {'blacklist': blacklist})

    async def member_joined_vc(self, member, t):
        await self.check_member(member)
        await self.update_user(member, {'joined': t})

    async def member_left_vc(self, member, t):
        await self.check_member(member)
        data = await self.get_user(member)
        if bool(data['blacklist']) is True:
            return
        xp_multiplier = data['xp_multiplier'] + await self.xp_multiplier_adds(data['uid'], data['gid'])
        if data['joined'] >= 0:
            xp_earned = self.xp_for((t - data['joined'])
                                    * await self.get_setting(member.guild.id, 'VOICE_XP_PER_MINUTE') / 60,
                                    xp_multiplier)
            old_level = data['lvl']
            data['lvl'] += self.lvl_xp_add(xp_earned, data['lvl'])
            await self.member_set_lvl(member, data['lvl'], old_level)
            await self.update_user(member, {'joined': -1})

    async def member_message_xp(self, member):
        await self.check_member(member)
        data = await self.get_user(member)
        if bool(data['blacklist']) is True:
            return
        xp_multiplier = data['xp_multiplier'] + await self.xp_multiplier_adds(data['uid'], data['gid'])
        xp_earned = self.xp_for(await self.get_setting(member.guild.id, 'MESSAGE_XP'), xp_multiplier)
        old_level = data['lvl']
        data['lvl'] += self.lvl_xp_add(xp_earned, data['lvl'])
        await self.member_set_lvl(member, data['lvl'], old_level)

    @staticmethod
    async def give_role(guild, member, role_id):
        role = get(guild.roles, id=role_id)
        if role is not None:
            for r in member.roles:
                if r.id == role.id:
                    return
            await member.add_roles(role)

    @staticmethod
    async def remove_role(guild, member, role_id):
        role = get(guild.roles, id=role_id)
        if role is not None and role in member.roles:
            for r in member.roles:
                if r.id == role.id:
                    return await member.remove_roles(role)

    async def member_role_manage(self, member, lvl):
        data = await self.lvlsys_get(member.guild.id)
        lvlsys_list = sorted(map(lambda x: (int(x['lvl']), x['rid']), data), key=lambda x: x[0])
        role_to_give = None
        roles_to_remove = []
        for i in range(len(lvlsys_list)):
            is_last = i == len(lvlsys_list) - 1
            if (is_last and lvl >= lvlsys_list[i][0]) or \
                    ((not is_last) and lvlsys_list[i][0] <= lvl < lvlsys_list[i + 1][0]):
                role_to_give = lvlsys_list[i][1]
            else:
                roles_to_remove.append(lvlsys_list[i][1])

        if role_to_give is None and len(lvlsys_list) != 0:
            role_to_give = lvlsys_list[0][1]
            roles_to_remove.remove(role_to_give)

        await self.give_role(member.guild, member, role_to_give)

        for role in roles_to_remove:
            if role != role_to_give:
                await self.remove_role(member.guild, member, role)

    async def lvlsys_get(self, guild_id):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM lvlsys WHERE gid=?', (guild_id,))
        return cur.fetchall()

    async def lvlsys_set(self, guild_id, role_id, lvl):
        cur = self.db_conn.cursor()
        cur.execute('INSERT OR REPLACE INTO lvlsys(gid, lvl, rid)'
                    'VALUES(?, ?, ?);',
                    (guild_id, lvl, role_id,))
        self.db_conn.commit()

    async def lvlsys_remove(self, guild_id, lvl):
        cur = self.db_conn.cursor()
        cur.execute('DELETE FROM lvlsys WHERE gid=? AND lvl=?', (guild_id, lvl,))
        self.db_conn.commit()

    async def lvlsys_get_embed(self, guild):
        embed = discord.Embed(title='Error',
                              description='level system empty for this server',
                              color=discord.Color.red())

        data = await self.lvlsys_get(guild.id)
        if data is not None and len(data) > 0:
            description = []
            for lvl, role_id in reversed(sorted(map(lambda x: (x['lvl'], x['rid']), data), key=lambda x: x[0])):
                role = get(guild.roles, id=role_id)
                if role is None:
                    await self.lvlsys_remove(guild.id, lvl)
                else:
                    description.append('Level: ' + str(lvl) + ' | Role: ' + str(role.name) + ' | ID: ' + str(role.id))
            embed = discord.Embed(title='Level System',
                                  description='\n'.join(description),
                                  color=discord.Color.green())
        return embed

    class Commands(commands.Cog):
        def __init__(self, parent):
            self.parent = parent

        async def cog_check(self, ctx):
            if ctx.message.guild is not None and not ctx.message.author.bot:
                if await self.parent.get_setting(ctx.message.guild.id, 'PROMO_CHANNEL_ID') \
                        == str(ctx.message.channel.id):
                    await ctx.send('Commands not allowed in Promo Channel!')
                    return False
            return True

        @commands.command(name='profile',
                          aliases=['p', 'P'],
                          description='show user profile',
                          help=' - Zeigt eure Profilkarte\n - profile {username} kann auch andere User anzeigen')
        async def _profile(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()
            await ctx.trigger_typing()

            if len(args) == 0:
                return await ctx.send(file=await self.parent.member_create_profile_image(ctx.message.author))
            else:
                member = await self.parent.search_member(ctx, ' '.join(args))
                if member is not None:
                    return await ctx.send(file=await self.parent.member_create_profile_image(member))

            return await ctx.send(embed=discord.Embed(title='Error',
                                                      description='No user was found!',
                                                      color=discord.Color.red()))

        @commands.command(name='promo',
                          aliases=['pr'],
                          description='get your promo code',
                          help=' - Hol dir deinen Promo-Code')
        async def _promo(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()

            promo_code = await self.parent.create_promo_code(ctx.message.author)
            if promo_code is None:
                return await ctx.send(embed=discord.Embed(title='Oops...',
                                                          description='Something went wrong with your promo code!',
                                                          color=discord.Color.red()))
            await ctx.message.author.send(
                embed=discord.Embed(title='',
                                    description='This is your Promo-Code for **{}**\n'
                                                'Expires in **{}** hours\n'
                                                '```{}```'
                                    .format(ctx.message.author.guild.name,
                                            int(
                                                await self.parent.get_setting(ctx.guild.id, 'PROMO_CODE_EXPIRES_HOURS')
                                            ),
                                            promo_code),
                                    color=discord.Color.blue())
            )
            await ctx.send(
                embed=discord.Embed(title='',
                                    description='Your Promo-Code was sent to you!',
                                    color=discord.Color.green())
            )

        @commands.command(name='boost',
                          aliases=['b', 'boosts'],
                          description='everything boosting your xp',
                          help=' - Alles zu XP - Boosts')
        async def _boost(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()
            await ctx.trigger_typing()
            if len(args) == 0:
                embed = await self.parent.boost_get_embed(ctx.message.author)

                return await ctx.send(embed=embed)

            member = await self.parent.search_member(ctx, ' '.join(args))
            if member is None:
                return await ctx.send(embed=discord.Embed(title='',
                                                          description='No matching user was found',
                                                          color=discord.Color.red()))

            res = await self.parent.set_boost_user(ctx.message.author, member)
            if res == ENUMS.BOOST_SUCCESS:
                return await ctx.send(embed=discord.Embed(title='',
                                                          description='You are boosting {} now!'
                                                          .format(member.display_name),
                                                          color=discord.Color.green()))
            elif res == ENUMS.BOOSTING_YOURSELF_FORBIDDEN:
                return await ctx.send(embed=discord.Embed(title='',
                                                          description='You cannot boost yourself!',
                                                          color=discord.Color.red()))
            return await ctx.send(embed=discord.Embed(title='',
                                                      description='Your boost has not expired yet!',
                                                      color=discord.Color.red()))

        @commands.command(name='leaderboard',
                          aliases=[],
                          description='show the leaderboard',
                          help=' - Zeigt die Top 10 des Servers')
        async def _leaderboard(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()
            await ctx.trigger_typing()
            await ctx.send(file=await self.parent.create_leaderboard_image(ctx.message.author))

        @commands.command(name='ranking-all',
                          aliases=[],
                          description='show the ranking',
                          help=' - Zeigt alle Profilkarten des Servers')
        @commands.has_permissions(administrator=True)
        async def _ranking(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()
            lb = await self.parent.get_ranking(ctx.message.guild)
            for user in lb:
                member = get(ctx.message.guild.members, id=int(user['uid']))
                if member is not None and not member.bot:
                    await ctx.trigger_typing()
                    await ctx.send(file=await self.parent.member_create_profile_image(member))
                else:
                    pass

        @commands.command(name='send',
                          aliases=['s'],
                          description='send through the bot',
                          help=' - Sprich durch den Bot')
        @commands.has_permissions(administrator=True)
        async def _send(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()
            if len(args) == 0:
                return await ctx.send(embed=discord.Embed(title='Help',
                                                          description='"send {msg}" to send into the system channel\n'
                                                                      '"send {channel_id} {msg}" to send '
                                                                      'into a specific channel',
                                                          color=discord.Color.gold()))
            elif len(args) == 1:
                return await ctx.author.guild.system_channel.send(args[0])
            else:
                try:
                    channel = get(ctx.guild.text_channels, id=int(args[0]))
                    if channel is not None:
                        return await channel.send(' '.join(args[1:]))
                except ValueError:
                    pass
                channel = get(ctx.guild.text_channels, name=args[0])
                if channel is not None:
                    return await channel.send(' '.join(args[1:]))
                return await ctx.send(embed=discord.Embed(title='Error',
                                                          description='Channel "{}" was not found!'.format(args[0]),
                                                          color=discord.Color.red()))

        @commands.command(name='setlvl',
                          aliases=['setlevel', 'sl'],
                          description='set level command',
                          help=' - Bestimme das Level eines Users')
        @commands.has_permissions(administrator=True)
        async def _setlvl(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()
            if len(args) == 0:
                return await ctx.send(embed=discord.Embed(title='Help',
                                                          description='"setlvl {level}" to set your level\n'
                                                                      '"setlvl {level} {search}" to set a level for a '
                                                                      'specific user',
                                                          color=discord.Color.gold()))

            async def __setlvl(m):
                try:
                    lvl = int(args[0])
                    await self.parent.member_set_lvl(m, lvl, None)
                    await ctx.send(embed=discord.Embed(title='Success',
                                                       description='Level was set successfully!',
                                                       color=discord.Color.green()))
                    await ctx.send(file=await self.parent.member_create_profile_image(m))
                except ValueError:
                    await ctx.send(embed=discord.Embed(title='Error',
                                                       description='Level must be an integer!',
                                                       color=discord.Color.red()))

            if len(args) == 1:
                return await __setlvl(ctx.message.author)
            else:
                member = await self.parent.search_member(ctx, ' '.join(args[1:]))
                if member is not None:
                    return await __setlvl(member)

            return await ctx.send(embed=discord.Embed(title='Error',
                                                      description='No user was found!',
                                                      color=discord.Color.red()))

        @commands.command(name='settings',
                          aliases=['setting'],
                          description='settings commands',
                          help=' - Alles ein-zu-stellen')
        @commands.has_permissions(administrator=True)
        async def _settings(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()

            if len(args) == 0:
                pass
            elif args[0] in ['reset'] and len(args) >= 2:
                key = ' '.join(args[1:])
                if key not in self.parent.default_guild_settings:
                    return await ctx.send(embed=discord.Embed(title='Error',
                                                              description='the key "{}" was not found in the settings'
                                                              .format(key),
                                                              color=discord.Color.red()))
                await self.parent.remove_setting(ctx.message.author.guild.id, key)
                return await ctx.send(embed=discord.Embed(title='',
                                                          description='Successfully reset setting "{}"!'
                                                          .format(key),
                                                          color=discord.Color.green()))

            elif args[0] in ['set', 's'] and len(args) >= 3:
                key = args[1]
                value = ' '.join(args[2:])
                try:
                    if not await self.parent.set_setting(ctx.message.author.guild.id, key, value):
                        return await ctx.send(embed=discord.Embed(title='Ups...',
                                                                  description='Something went wrong!'
                                                                  .format(key),
                                                                  color=discord.Color.red()))
                    embed = discord.Embed(title='Settings',
                                          description='',
                                          color=discord.Color.gold())

                    embed.add_field(name='{}'.format(key),
                                    value='"{}"'.format(
                                        await self.parent.get_setting(ctx.message.author.guild.id, key)),
                                    inline=False)
                    return await ctx.send(embed=embed)
                except KeyError:
                    return await ctx.send(embed=discord.Embed(title='Error',
                                                              description='the key "{}" was not found in the settings'
                                                              .format(key),
                                                              color=discord.Color.red()))
            elif args[0] in ['get', 'g']:
                embed = discord.Embed(title='Settings',
                                      description='',
                                      color=discord.Color.gold())

                if len(args) > 1:
                    try:
                        key = ' '.join(args[1:])
                        res = await self.parent.get_setting(ctx.message.author.guild.id, key)
                        embed.add_field(name='{}'.format(key),
                                        value='"{}"'.format(res),
                                        inline=False)
                        return await ctx.send(embed=embed)
                    except KeyError:
                        pass

                for key, value in (await self.parent.get_settings(ctx.message.author.guild.id)).items():
                    res = '"{}"'.format(value)
                    embed.add_field(name='{}'.format(key),
                                    value=(res[:80] + '...') if len(str(res)) > 80 else res,
                                    inline=False)
                return await ctx.send(embed=embed)

            await ctx.send(embed=discord.Embed(title='Help',
                                               description='"settings get" to display the settings\n'
                                                           '"settings get {key}" to display a setting\n'
                                                           '"settings reset {key}" to reset a setting\n'
                                                           '"settings set {key} {value}" to set a setting\n',
                                               color=discord.Color.gold()))

        @commands.command(name='info',
                          aliases=[],
                          description='user infos',
                          help=' - Lass dir Infos zu einem Benuter anzeigen')
        async def _info(self, ctx, *args):
            if len(args) == 0:
                return await ctx.send(embed=await self.parent.info_get_embed(ctx.message.author))
            search = ' '.join(args)
            member = await self.parent.search_member(ctx, search)
            if member is not None:
                return await ctx.send(embed=await self.parent.info_get_embed(member))
            return await ctx.send(embed=discord.Embed(title='',
                                                      description='User {} was not found!'
                                                      .format(search),
                                                      color=discord.Color.red()))

        @commands.command(name='mreact',
                          aliases=[],
                          description='message reaction commands',
                          help=' - Lasse den Bot auf Message Reactions reagieren')
        @commands.has_permissions(administrator=True)
        async def _msg_reaction(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()

            if len(args) == 0:
                pass

            elif args[0] in ['add']:
                if len(args) >= 3:
                    try:
                        msg_id = int(args[1])
                        message = await ctx.fetch_message(msg_id)

                    except ValueError or discord.NotFound:
                        return await ctx.send(
                            embed=discord.Embed(title='',
                                                description='Message ID was invalid!',
                                                color=discord.Color.red()))

                    reaction_emoji = args[2]

                    try:
                        await message.add_reaction(reaction_emoji)
                    except discord.HTTPException:
                        return await ctx.send(
                            embed=discord.Embed(title='',
                                                description='Reaction is invalid!',
                                                color=discord.Color.red()))

                    if len(args) >= 5:
                        if args[3] == 'add-role':
                            action_type = 'add-role'
                            try:
                                action = int(args[4])
                                role = get(ctx.message.guild.roles, id=action)
                                if role is None:
                                    raise ValueError('Role-ID is invalid')

                            except ValueError:
                                return await ctx.send(
                                    embed=discord.Embed(title='',
                                                        description='Role-ID is invalid!',
                                                        color=discord.Color.red()))

                        elif args[3] == 'dm':
                            action_type = 'dm'
                            action = ' '.join(args[4:])

                        else:
                            return await ctx.send(
                                embed=discord.Embed(title='',
                                                    description='Unknown action: {}'.format(args[3]),
                                                    color=discord.Color.red()))

                        await self.parent.add_msg_reaction(ctx.guild.id,
                                                           message.id,
                                                           reaction_emoji,
                                                           action_type,
                                                           action)

                    return await ctx.send(
                        embed=discord.Embed(title='',
                                            description='Successfully added reaction\n',
                                            color=discord.Color.green()))

                return await ctx.send(
                    embed=discord.Embed(title='Help "mreact add"',
                                        description='"mreact add {msg_id} {reaction_emoji} to just add a emoji"\n'
                                                    '"mreact add {msg_id} {reaction_emoji} add-role {role_id}" '
                                                    'to setup adding a role on a reaction\n'
                                                    '"mreact add {msg_id} {reaction_emoji} dm {dm_content}" '
                                                    'to setup sending a dm on a reaction\n',
                                        color=discord.Color.gold()))

            elif args[0] in ['remove', 'delete', 'rm', 'del'] and len(args) >= 2:
                try:
                    msg_id = int(args[1])
                    await self.parent.remove_msg_reaction(ctx.guild.id, msg_id, args[2])
                    message = await ctx.fetch_message(msg_id)

                except ValueError or discord.NotFound:
                    return await ctx.send(
                        embed=discord.Embed(title='',
                                            description='Message ID is invalid!',
                                            color=discord.Color.red()))

                try:
                    await message.clear_reaction(args[2])
                except discord.HTTPException:
                    return await ctx.send(
                        embed=discord.Embed(title='',
                                            description='Reaction is invalid!',
                                            color=discord.Color.red()))

                return await ctx.send(
                    embed=discord.Embed(title='',
                                        description='Successfully removed reaction\n',
                                        color=discord.Color.green()))

            elif args[0] in ['get']:
                if len(args) >= 2:
                    msg_id = ' '.join(args[1:])
                    reactions = await self.parent.get_msg_reactions(ctx.guild.id, msg_id)
                    if len(reactions) == 0:
                        return await ctx.send(
                            embed=discord.Embed(title='',
                                                description='Reaction to "{}" is not found!'.format(msg_id),
                                                color=discord.Color.red()))
                    embed = discord.Embed(title='Message "{}" Reactions'.format(msg_id), color=discord.Color.green())
                    for reaction in reactions:
                        embed.add_field(name='Reaction: {}'.format(reaction['reaction']),
                                        value='type: {}\naction: {}'
                                        .format(reaction['actiontype'], reaction['action']),
                                        inline=False)
                    return await ctx.send(embed=embed)

                reactions = await self.parent.get_all_msg_reactions(ctx.guild.id)
                embed = discord.Embed(title='Message Reactions', color=discord.Color.green())
                for reaction in reactions:
                    embed.add_field(name='ID: {}'.format(reaction['msgid']),
                                    value='reaction: {}\ntype: {}\naction: {}'
                                    .format(reaction['reaction'], reaction['actiontype'], reaction['action']),
                                    inline=False)
                return await ctx.send(embed=embed)

            return await ctx.send(
                embed=discord.Embed(title='Help',
                                    description='"mreact get" to show all message reactions\n'
                                                '"mreact add" to show more information how to setup msg reactions\n'
                                                '"reaction remove {msg_id} {reaction_emoji}" '
                                                'to remove a message reaction\n',
                                    color=discord.Color.gold()))

        @commands.command(name='reaction',
                          aliases=['reactions'],
                          description='reaction commands',
                          help=' - Lasse den Bot auf Nachrichten reagieren')
        @commands.has_permissions(administrator=True)
        async def _reaction(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()

            await ctx.trigger_typing()

            if len(args) == 0:
                pass
            elif args[0] in ['get']:
                reactions = await self.parent.get_reactions(ctx.guild.id)
                embed = discord.Embed(title='Reactions', color=discord.Color.green())

                for reaction in reactions:
                    embed.add_field(name=reaction['trigger'], value=reaction['reaction'], inline=False)

                return await ctx.send(embed=embed)

            elif args[0] in ['add'] and len(args) >= 3:
                trigger = args[1]
                reaction = ' '.join(args[2:])
                await self.parent.set_reaction(ctx.guild.id, trigger, reaction)
                return await ctx.send(
                    embed=discord.Embed(title='',
                                        description='Now reacting to "{}" with "{}"'.format(trigger, reaction),
                                        color=discord.Color.green()))

            elif args[0] in ['remove', 'rm', 'delete', 'del'] and len(args) >= 2:
                trigger = ' '.join(args[1:])
                await self.parent.remove_reaction(ctx.guild.id, trigger)
                return await ctx.send(
                    embed=discord.Embed(title='',
                                        description='Reaction to {} was removed'.format(trigger),
                                        color=discord.Color.green()))

            return await ctx.send(
                embed=discord.Embed(title='Help',
                                    description='"reaction get" to show all reactions\n'
                                                '"reaction add {trigger} {reaction}" to add a reaction\n'
                                                '"reaction remove {trigger}" to remove a reaction\n',
                                    color=discord.Color.gold()))

        @commands.command(name='lvlsys',
                          aliases=['levelsystem', 'lvlsystem', 'levelsys', 'ls'],
                          description='level system commands',
                          help=' - Alles über das Levelsystem')
        @commands.has_permissions(administrator=True)
        async def _lvlsys(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()

            await ctx.trigger_typing()

            embed = discord.Embed(title='Help',
                                  description='"lvlsys update" to update the users to the new levelsystem\n'
                                              '"lvlsys boost {multiplier} {search}" to boost a user\n'
                                              '"lvlsys get" to display the levelsystem\n'
                                              '"lvlsys set {level} {role_id}" to set a role for a level\n'
                                              '"lvlsys remove {level}" to remove the level\n'
                                              '"lvlsys blacklist {search}" to blacklist a user\n'
                                              '"lvlsys whitelist {search}" to whitelist a user\n',
                                  color=discord.Color.gold())

            if len(args) == 0:
                pass

            elif args[0] in ['update', 'u']:
                for member in ctx.message.guild.members:
                    if not member.bot:
                        await self.parent.update_member(member)
                return await ctx.send(embed=discord.Embed(title='',
                                                          description='Successfully updated levelsystem!',
                                                          color=discord.Color.green()))

            elif args[0] in ['get']:
                return await ctx.send(embed=await self.parent.lvlsys_get_embed(ctx.message.guild))

            elif args[0] in ['set']:
                if len(args) == 3 and args[1].isnumeric() and args[2].isnumeric():
                    rid = int(args[2])
                    for role in ctx.message.guild.roles:
                        if role.id == rid:
                            await self.parent.lvlsys_set(ctx.message.guild.id, role.id, int(args[1]))

                            embed = discord.Embed(title='',
                                                  description='Role-Level was set!',
                                                  color=discord.Color.green())
                            await ctx.send(embed=embed)
                            return await ctx.send(embed=await self.parent.lvlsys_get_embed(ctx.message.guild))

                    embed = discord.Embed(title='Error',
                                          description='Role-ID was not found!',
                                          color=discord.Color.red())

            elif args[0] in ['boost', 'xpboost', 'mult']:
                async def __multiplier(m):
                    try:
                        await self.parent.member_set_xp_multiplier(m, float(args[1]))
                        await ctx.send(embed=discord.Embed(title='',
                                                           description='Successfully set multiplier!',
                                                           color=discord.Color.green()))
                        await ctx.send(file=await self.parent.member_create_profile_image(m))
                    except ValueError:
                        await ctx.send(embed=discord.Embed(title='Error',
                                                           description='Multiplier must be in the format x.xx!',
                                                           color=discord.Color.red()))

                if len(args) == 1:
                    pass
                elif len(args) == 2:
                    return await __multiplier(ctx.message.author)
                else:
                    member = await self.parent.search_member(ctx, ' '.join(args[2:]))
                    if member is not None:
                        return await __multiplier(member)

                return await ctx.send(embed=discord.Embed(title='Error',
                                                          description='No multiplier was given or no user was found!',
                                                          color=discord.Color.red()))

            elif args[0] in ['remove', 'rm', 'del', 'delete']:
                if len(args) == 2 and args[1].isnumeric():
                    await self.parent.lvlsys_remove(ctx.message.guild.id, int(args[1]))
                    embed = discord.Embed(title='',
                                          description='Role-Level was removed!',
                                          color=discord.Color.green())
                    await ctx.send(embed=embed)
                    return await ctx.send(embed=await self.parent.lvlsys_get_embed(ctx.message.guild))

            elif args[0] in ['blacklist', 'whitelist']:
                async def __blacklist(m):
                    await self.parent.member_set_blacklist(m, args[0] == 'blacklist')
                    await ctx.send(embed=discord.Embed(title='',
                                                       description='Successfully edited blacklist!',
                                                       color=discord.Color.green()))
                    await ctx.send(embed=await self.parent.blacklist_get_embed(ctx.message.guild))

                if len(args) == 1:
                    return await __blacklist(ctx.message.author)
                else:
                    member = await self.parent.search_member(ctx, ' '.join(args[1:]))
                    if member is not None:
                        return await __blacklist(member)

                return await ctx.send(embed=discord.Embed(title='Error',
                                                          description='No user was found!',
                                                          color=discord.Color.red()))

            await ctx.send(embed=embed)

        @commands.command(name='clear',
                          aliases=[],
                          description='Clear messages in a text channel!',
                          help=' - Löscht Nachrichten in einem Text-Channel!')
        @commands.has_permissions(administrator=True)
        async def _clear(self, ctx, *args):
            if ctx.guild is None:
                raise commands.NoPrivateMessage()

            await ctx.trigger_typing()
            if len(args) == 0:
                pass
            elif len(args) >= 1:
                async def _clear_by(limit):
                    if len(args) == 1:
                        await ctx.channel.purge(limit=limit + 1, bulk=False)
                        return await ctx.send(embed=discord.Embed(title='',
                                                                  description='Successfully deleted messages!',
                                                                  color=discord.Color.green()))
                    search = ' '.join(args[1:])
                    channel = await self.parent.search_text_channel(ctx, search)
                    if channel is None:
                        return await ctx.send(embed=discord.Embed(title='',
                                                                  description='Channel "{}" was '
                                                                              'not found!'.format(search),
                                                                  color=discord.Color.red()))
                    await channel.purge(limit=limit, bulk=False)
                    return await ctx.send(embed=discord.Embed(title='',
                                                              description='Successfully deleted messages!',
                                                              color=discord.Color.green()))

                if args[0].isnumeric():
                    return await _clear_by(int(args[0]))

            await ctx.send(embed=discord.Embed(title='Error',
                                               description='Please provide a number of messages to delete or use '
                                                           'clear all to delete all messages in this channel!',
                                               color=discord.Color.red()))

        @commands.command(name='coinflip',
                          aliases=['cf', 'coin'],
                          description='Toss a coin to your Witcher!',
                          help=' - Toss a coin to your Witcher!')
        async def _coinflip(self, ctx, *args):
            if random.randint(0, 1) == 0:
                res = 'kopf'
            else:
                res = 'zahl'

            prev_author = ctx.message.author

            message = await ctx.send(file=discord.File(os.path.join('images', '{}.gif'.format(res))))

            voice_client = None
            if hasattr(prev_author, 'guild'):
                if random.random() < await self.parent.get_setting(prev_author.guild.id, 'COIN_FLIP_AUDIO_CHANCE'):
                    if prev_author.voice is not None and prev_author.voice.channel is not None:
                        try:
                            voice_channel = prev_author.voice.channel
                            voice_client = await voice_channel.connect()
                            audio_source = discord.FFmpegPCMAudio(os.path.join('audio', 'tossacoin.mp3'))
                            voice_client.play(audio_source)
                        except discord.ClientException:
                            self.parent.lprint('Bot is alreardy connect to a voice channel')
                        except RuntimeError as e:
                            self.parent.lprint(e)

            await asyncio.sleep(13)

            await message.delete()
            await ctx.send(file=discord.File(os.path.join('images', '{}.png'.format(res))))

            if voice_client is not None:
                await voice_client.disconnect()

        @commands.command(name='dice',
                          aliases=[],
                          description='Roll a dice to your Witcher!',
                          help=' - Würfelt eine Zahl zwischen 1-6')
        async def _dice(self, ctx, *args):
            await ctx.send(file=discord.File(os.path.join('images', '{}.gif'.format(random.randint(1, 6)))))

        @commands.command(name='random',
                          aliases=[],
                          description='Generate a random number',
                          help=' - Generiert eine zufällige Zahl')
        async def _random(self, ctx, *args):
            random_string = 'Random **{}**'
            if len(args) == 0:
                return await ctx.send(embed=discord.Embed(
                    description=random.choice(
                        await self.parent.get_setting(ctx.message.author.guild.id, 'COMMAND_NOT_FOUND_RESPONSES')),
                    color=discord.Color.red()))

            if len(args) == 1:
                if args[0].isnumeric():
                    return await ctx.send(random_string.format(random.randint(1, int(args[0]))))

            if len(args) == 2:
                if args[0].isnumeric() and args[1].isnumeric():
                    opts = [int(args[0]), int(args[1])]
                    return await ctx.send(random_string.format(random.randint(min(opts), max(opts))))

            await ctx.send(random_string.format(random.choice(args)))

        @commands.command(name='help',
                          aliases=['h'],
                          description="gives you help",
                          help=' - Ist offenbar schon bekannt...')
        async def _help(self, ctx, *args):
            embed = discord.Embed(title='Help',
                                  description='',
                                  color=discord.Color.gold())

            for command in sorted(self.parent.bot.commands, key=lambda x: x.name):
                try:
                    if await command.can_run(ctx):
                        embed.add_field(name=str(command.name), value='{}'.format(command.help), inline=False)
                except commands.CommandError:
                    pass
            await ctx.send(embed=embed)

    class Events(commands.Cog):
        def __init__(self, parent):
            self.parent = parent

        @commands.Cog.listener()
        async def on_command_error(self, ctx, error):
            guild_id = None
            try:
                guild_id = ctx.message.author.guild.id
            except AttributeError:
                pass

            if isinstance(error, commands.NoPrivateMessage):
                await ctx.send('This command does not work via Private Message')
            elif isinstance(error, commands.CommandNotFound):
                await ctx.send(embed=discord.Embed(description=random.choice(
                    await self.parent.get_setting(guild_id, 'COMMAND_NOT_FOUND_RESPONSES')),
                    color=discord.Color.red()))
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send(embed=discord.Embed(description=random.choice(
                    await self.parent.get_setting(guild_id, 'MISSING_PERMISSIONS_RESPONSES')),
                    color=discord.Color.red()))
            elif isinstance(error, commands.CheckFailure):
                pass
            else:
                self.parent.lprint(error)

        @commands.Cog.listener()
        async def on_ready(self):
            self.parent.lprint('Bot is ready')

        @commands.Cog.listener()
        async def on_member_join(self, member):
            if await self.parent.get_setting(member.guild.id, 'SEND_WELCOME_IMAGE'):
                await member.send(file=await self.parent.member_create_welcome_image(member))

        @commands.Cog.listener()
        async def on_member_remove(self, member):
            await self.parent.remove_member(member)

        @commands.Cog.listener()
        async def on_message(self, message):
            if message.guild is not None:
                if not message.author.bot:
                    await self.parent.member_message_xp(message.author)

                    reaction = await self.parent.get_reaction(message.guild.id, message.content)
                    if reaction is not None:
                        await message.channel.send(reaction['reaction'])

                if await self.parent.get_setting(message.guild.id, 'PROMO_CHANNEL_ID') == str(message.channel.id):
                    if not message.author.bot:
                        promo = await self.parent.get_promo_code(message.author, message.content)
                        if promo is None:
                            await message.channel.send(embed=discord.Embed(title='',
                                                                           description='Invalid promo code!',
                                                                           color=discord.Color.red()))
                        else:
                            res = await self.parent.use_promo_code(message.author, promo)
                            if res:
                                await message.channel.send(
                                    embed=discord.Embed(title='',
                                                        description='Promo code used successfully!',
                                                        color=discord.Color.green()))
                            else:
                                await message.channel.send(
                                    embed=discord.Embed(title='',
                                                        description='You already used a promo code!',
                                                        color=discord.Color.red()))
                    await asyncio.sleep(5)
                    await message.delete()

        @commands.Cog.listener()
        async def on_raw_reaction_add(self, payload):
            if payload.guild_id is not None and payload.member is not None and payload.member.bot is False:
                await self.parent.msg_reaction_event(payload.member, payload.message_id, payload.emoji)

        @commands.Cog.listener()
        async def on_voice_state_update(self, member, before, after):
            if member.bot:
                return
            t = round(time.time(), 2)

            if before.channel is not None:
                # when leaving
                if member.guild.afk_channel is None or before.channel.id != member.guild.afk_channel.id:
                    await self.parent.member_left_vc(member, t)
                self.parent.lprint(member, 'left', before.channel)

            if after.channel is not None:
                # when joining
                if member.guild.afk_channel is None or after.channel.id != member.guild.afk_channel.id:
                    await self.parent.member_joined_vc(member, t)
                self.parent.lprint(member, 'joined', after.channel)


if __name__ == '__main__':
    from settings import GLOBAL_SETTINGS, DEFAULT_GUILD_SETTINGS

    if not os.path.exists('dbs'):
        os.mkdir('dbs')
    con = sqlite3.connect('dbs/bot.db')
    b = DiscordBot(con,
                   default_guild_settings=DEFAULT_GUILD_SETTINGS,
                   update_voice_xp_interval=GLOBAL_SETTINGS['UPDATE_VOICE_XP_INTERVAL'],
                   command_prefix=GLOBAL_SETTINGS['COMMAND_PREFIX'],
                   description=GLOBAL_SETTINGS['DESCRIPTION'],
                   print_logging=GLOBAL_SETTINGS['PRINT_LOGGING'],
                   use_slash_commands=GLOBAL_SETTINGS['USE_SLASH_COMMANDS']
                   )

    b.set_image_creator(imgtools.ImageCreator(fonts=GLOBAL_SETTINGS['FONTS'],
                                              load_memory=GLOBAL_SETTINGS['IMAGES_LOAD_MEMORY']))

    b.run(GLOBAL_SETTINGS['TOKEN'])
