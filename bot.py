import discord
from discord.ext import commands
from discord.utils import get

from helpers import tools, imgtools

import asyncio
import types
import os
import time
import random


class DiscordBot:
    def __init__(self,
                 db_conn,
                 message_give_xp=0.5,
                 voice_xp_per_minute=1,
                 update_voice_xp_interval=-1,
                 command_prefix='>',
                 description='',
                 missing_permission_responses=('Missing Permission',),
                 command_not_found_responses=('Command not found',),
                 image_creator=None,
                 profile_image=None,
                 level_up_image=None,
                 rank_up_image=None,
                 ranking_image=None,
                 print_logging=False,
                 use_slash_commands=False
                 ):
        intents = discord.Intents.default()
        intents.members = True

        self.print_logging = print_logging
        self.message_give_xp = message_give_xp
        self.voice_xp_per_minute = voice_xp_per_minute

        self.update_voice_xp_interval = update_voice_xp_interval

        self.missing_permission_responses = missing_permission_responses
        self.command_not_found_responses = command_not_found_responses

        self.profile_image = profile_image
        self.level_up_image = level_up_image
        self.rank_up_image = rank_up_image
        self.ranking_image = ranking_image

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
                uid INTEGER PRIMARY KEY,
                gid INTEGER NOT NULL,
                lvl REAL NOT NULL,
                xp_multiplier REAL NOT NULL,
                joined INTEGER NOT NULL,
                blacklist INTEGER NOT NULL
            );''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS lvlsys (
                lsid INTEGER PRIMARY KEY,
                gid INTEGER NOT NULL,
                lvl INTEGER NOT NULL,
                rid INTEGER NOT NULL
            );''')

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

                    class _Message:
                        def __init__(self, author=None):
                            self.author = author
                            self.guild = author.guild

                    ctx.trigger_typing = types.MethodType(_none, ctx)
                    ctx.message = _Message(author=ctx.author)
                    cargs = [ctx] + ([] if args == '' else args.split(' '))
                    try:
                        if await command.can_run(ctx):
                            await command.callback(self.commands, *cargs)
                    except commands.CommandError:
                        await ctx.send(embed=discord.Embed(description=random.choice(self.missing_permission_responses),
                                                           color=discord.Color.red()))

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

    async def get_user(self, member):
        cur = self.db_conn.cursor()
        cur.execute('SELECT * FROM users WHERE uid=? AND gid=?', (member.id, member.guild.id,))
        return cur.fetchone()

    async def update_user(self, member, data):
        user = await self.get_user(member)
        if user is None:
            user = {
                'lvl': 1.0,
                'xp_multiplier': 1.0,
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
            if bool(user['blacklist']):
                user['joined'] = ctime
            else:
                guild = self.bot.get_guild(user['gid'])
                member = get(guild.members, id=int(user['uid']))
                if member.voice is None or member.voice.channel is None:
                    user['joined'] = 0
                else:
                    xp_earned = self.xp_for((ctime - user['joined']) * self.voice_xp_per_minute / 60,
                                            user['xp_multiplier'])

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
        name = member.name
        if member.nick is not None:
            name = member.nick

        data_xp_multiplier = data['xp_multiplier']
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

        img_buf = await self.image_creator.create(self.profile_image(data_obj))
        return discord.File(filename="member.png", fp=img_buf)

    async def member_create_lvl_image(self, member, old_lvl, new_lvl):
        if self.level_up_image is not None:
            name = member.name
            if member.nick is not None:
                name = member.nick

            data_obj = {'member': member,
                        'old_lvl': self.get_lvl(old_lvl),
                        'new_lvl': self.get_lvl(new_lvl),
                        'color': imgtools.rgb_to_bgr(member.color.to_rgb()),
                        'name': name}

            img_buf = await self.image_creator.create(self.level_up_image(data_obj))
            return discord.File(filename="lvlup.png", fp=img_buf)

    async def member_create_rank_up_image(self, member, old_lvl, new_lvl, old_role, new_role):
        if self.rank_up_image is not None:
            name = member.name
            if member.nick is not None:
                name = member.nick

            data_obj = {'member': member,
                        'old_lvl': self.get_lvl(old_lvl),
                        'new_lvl': self.get_lvl(new_lvl),
                        'old_role': old_role,
                        'new_role': new_role,
                        'old_color': imgtools.rgb_to_bgr(old_role.color.to_rgb()),
                        'new_color': imgtools.rgb_to_bgr(new_role.color.to_rgb()),
                        'name': name}

            img_buf = await self.image_creator.create(self.rank_up_image(data_obj))
            return discord.File(filename="rankup.png", fp=img_buf)

    async def create_ranking_image(self, member, ranked_users):
        if self.ranking_image is not None:
            ranking_obj = []
            for user in ranked_users:
                member = get(member.guild.members, id=int(user['uid']))
                if member is not None and not member.bot:
                    name = member.name
                    if member.nick is not None:
                        name = member.nick
                    ranking_obj.append({
                        'member': member,
                        'rank': user['rank'],
                        'lvl': self.get_lvl(user['lvl']),
                        'name': name,
                        'color': imgtools.rgb_to_bgr(member.color.to_rgb())
                    })

            img_buf = await self.image_creator.create(self.ranking_image(ranking_obj), max_size=(-1, 8000))
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

    async def member_set_lvl_xp(self, member, lvl, old_level=None):
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
        xp_multiplier = data['xp_multiplier']
        if data['joined'] >= 0:
            xp_earned = self.xp_for((t - data['joined']) * self.voice_xp_per_minute / 60, xp_multiplier)
            old_level = data['lvl']
            data['lvl'] += self.lvl_xp_add(xp_earned, data['lvl'])
            await self.member_set_lvl_xp(member, data['lvl'], old_level)
            await self.update_user(member, {'joined': -1})

    async def member_message_xp(self, member):
        await self.check_member(member)
        data = await self.get_user(member)
        if bool(data['blacklist']) is True:
            return
        xp_multiplier = data['xp_multiplier']
        xp_earned = self.xp_for(self.message_give_xp, xp_multiplier)
        old_level = data['lvl']
        data['lvl'] += self.lvl_xp_add(xp_earned, data['lvl'])
        await self.member_set_lvl_xp(member, data['lvl'], old_level)

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
                                                                      '"send {channel_id} {msg}" to send'
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
                    await self.parent.member_set_lvl_xp(m, lvl, None)
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
            await ctx.trigger_typing()
            if len(args) == 0:
                pass
            elif len(args) >= 1:
                async def _clear_by(limit):
                    if len(args) == 1:
                        await ctx.channel.purge(limit=limit+1, bulk=True)
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
                    await channel.purge(limit=limit, bulk=True)
                    return await ctx.send(embed=discord.Embed(title='',
                                                              description='Successfully deleted messages!',
                                                              color=discord.Color.green()))

                if args[0] == 'all':
                    return await _clear_by(999999999)  # TO-DO: don't use a number
                elif args[0].isnumeric():
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
            message = await ctx.send(file=discord.File(os.path.join('images', '{}.gif'.format(res))))
            await asyncio.sleep(5)
            await message.delete()
            await ctx.send(file=discord.File(os.path.join('images', '{}.png'.format(res))))

        @commands.command(name='dice',
                          aliases=[],
                          description='Roll a dice to your Witcher!',
                          help=' - Würfelt eine Zahl zwischen 1-6')
        async def _dice(self, ctx, *args):
            await ctx.send(file=discord.File(os.path.join('images', '{}.png'.format(random.randint(1, 6)))))

        @commands.command(name='random',
                          aliases=[],
                          description='Generate a random number',
                          help=' - Generiert eine zufällige Zahl')
        async def _random(self, ctx, *args):
            random_string = 'Random **{}**'
            if len(args) == 0:
                return await ctx.send(embed=discord.Embed(
                    description=random.choice(self.parent.command_not_found_responses), color=discord.Color.red()))

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
            if isinstance(error, commands.CommandNotFound):
                await ctx.send(embed=discord.Embed(description=random.choice(self.parent.command_not_found_responses),
                                                   color=discord.Color.red()))
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send(embed=discord.Embed(description=random.choice(self.parent.missing_permission_responses),
                                                   color=discord.Color.red()))
            else:
                self.parent.lprint(error)

        @commands.Cog.listener()
        async def on_ready(self):
            self.parent.lprint('Bot is ready')

        @commands.Cog.listener()
        async def on_member_join(self, member):
            if not member.bot:
                await self.parent.update_member(member)
            # send a private message on join
            # await member.send('Private message')

        @commands.Cog.listener()
        async def on_member_remove(self, member):
            await self.parent.remove_member(member)

        @commands.Cog.listener()
        async def on_message(self, message):
            if message.guild is not None and not message.author.bot:
                await self.parent.member_message_xp(message.author)

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
    from settings import *
    import sqlite3

    if not os.path.exists('dbs'):
        os.mkdir('dbs')
    con = sqlite3.connect('dbs/bot.db')
    b = DiscordBot(con,
                   message_give_xp=MESSAGE_XP,
                   voice_xp_per_minute=VOICE_XP_PER_MINUTE,
                   update_voice_xp_interval=UPDATE_VOICE_XP_INTERVAL,
                   command_prefix=COMMAND_PREFIX,
                   description=DESCRIPTION,
                   missing_permission_responses=MISSING_PERMISSIONS_RESPONSES,
                   command_not_found_responses=COMMAND_NOT_FOUND_RESPONSES,
                   profile_image=PROFILE_IMAGE,
                   level_up_image=LEVEL_UP_IMAGE,
                   rank_up_image=RANK_UP_IMAGE,
                   ranking_image=RANKGING_IMAGE,
                   print_logging=PRINT_LOGGING,
                   use_slash_commands=USE_SLASH_COMMANDS
                   )

    b.set_image_creator(imgtools.ImageCreator(fonts=FONTS, load_memory=IMAGES_LOAD_MEMORY))

    b.run(TOKEN)
