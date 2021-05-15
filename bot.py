import asyncio

from settings import *

import discord
from discord.ext import commands
from discord.utils import get

from tinydb import TinyDB, Query, operations

from helpers import tools, imgtools

import os
import time
import random

query = Query()


class DiscordBot:
    def __init__(self, user_db, lvlsys_db, print_logging=False):
        intents = discord.Intents.default()
        intents.members = True

        self.print_logging = print_logging

        self.user_db = user_db
        self.lvlsys_db = lvlsys_db

        self.bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, intents=intents, help_command=None)

        self.events = self.Events(self)
        self.commands = self.Commands(self)

        self.bot.add_cog(self.events)
        self.bot.add_cog(self.commands)

        self.image_creator = imgtools.ImageCreator(loop=self.bot.loop, fonts=FONTS, load_memory=IMAGES_LOAD_MEMORY)

    def run(self, token):
        self.bot.run(token)

    def lprint(self, *args):
        if self.print_logging:
            print(*args)

    @staticmethod
    def max_xp_for(lvl):
        return max(100, (lvl - 1) * 10 + 100)

    @staticmethod
    def xp_for(ctime, boost):
        return round(ctime * boost, 2)

    @staticmethod
    async def search_member(ctx, search):
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

    async def get_users(self, guild):
        return self.user_db.get(query.gid == guild.id)['users']

    async def get_user(self, member):
        data = await self.get_users(member.guild)
        return data[str(member.id)]

    async def update_user(self, member, data):
        users_data = await self.get_users(member.guild)
        str_uid = str(member.id)
        if str_uid not in users_data:
            users_data[str_uid] = {}
        for k, v in data.items():
            users_data[str_uid][k] = v
        self.user_db.update(
            operations.set('users', users_data),
            query.gid == member.guild.id
        )

    async def remove_member(self, member):
        users_data = await self.get_users(member.guild)
        str_uid = str(member.id)
        if str_uid in users_data:
            del users_data[str_uid]
        self.user_db.update(
            operations.set('users', users_data),
            query.gid == member.guild.id
        )

    async def check_guild(self, guild):
        if not self.user_db.contains(query.gid == guild.id):
            self.user_db.insert({'gid': guild.id, 'users': {}})

    async def get_blacklisted_users(self, guild):
        users = await self.get_users(guild)
        return filter(lambda x: x['blacklist'], users.values())

    async def get_ranking(self, guild):
        users = await self.get_users(guild)
        return sorted(users.values(), key=lambda x: (x['lvl'], x['xp']), reverse=True)

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
        data_xp = int(data['xp'])
        data_max_xp = int(self.max_xp_for(data['lvl']))
        data_percentage = data_xp / data_max_xp
        data_rank = await self.get_ranking_rank(member)

        data_obj = {'member': member,
                    'name': name,
                    'color': imgtools.rgb_to_bgr(member.color.to_rgb()),
                    'lvl': data['lvl'],
                    'xp': data_xp,
                    'max_xp': data_max_xp,
                    'xp_percentage': data_percentage,
                    'rank': data_rank,
                    'xp_multiplier': data_xp_multiplier,
                    'avatar_url': str(member.avatar_url_as(format="png"))}

        img_buf = await self.image_creator.create(PROFILE_IMAGE(data_obj))
        return discord.File(filename="member.png", fp=img_buf)

    async def member_create_lvl_image(self, member, old_lvl, new_lvl):
        name = member.name
        if member.nick is not None:
            name = member.nick

        data_obj = {'member': member,
                    'old_lvl': old_lvl,
                    'color': imgtools.rgb_to_bgr(member.color.to_rgb()),
                    'new_lvl': new_lvl,
                    'name': name}

        img_buf = await self.image_creator.create(LEVEL_UP_IMAGE(data_obj))
        return discord.File(filename="lvlup.png", fp=img_buf)

    async def member_create_rank_up_image(self, member, old_lvl, new_lvl, old_role, new_role):
        name = member.name
        if member.nick is not None:
            name = member.nick

        data_obj = {'member': member,
                    'old_lvl': old_lvl,
                    'new_lvl': new_lvl,
                    'old_role': old_role,
                    'new_role': new_role,
                    'old_color': imgtools.rgb_to_bgr(old_role.color.to_rgb()),
                    'new_color': imgtools.rgb_to_bgr(new_role.color.to_rgb()),
                    'name': name}

        img_buf = await self.image_creator.create(RANK_UP_IMAGE(data_obj))
        return discord.File(filename="rankup.png", fp=img_buf)

    async def create_ranking_image(self, member, ranked_users):
        ranking_obj = []
        for user in ranked_users:
            member = get(member.guild.members, id=int(user['uid']))
            if member is not None and not member.bot:
                name = member.name
                if member.nick is not None:
                    name = member.nick
                ranking_obj.append({
                    'member': member,
                    'lvl': user['lvl'],
                    'name': name,
                    'color': imgtools.rgb_to_bgr(member.color.to_rgb())
                })

        img_buf = await self.image_creator.create(RANKGING_IMAGE(ranking_obj), max_size=(-1, 8000))
        return discord.File(filename="ranking.png", fp=img_buf)

    async def create_leaderboard_image(self, member):
        ranking = await self.get_ranking(member.guild)
        return await self.create_ranking_image(member, ranking[:10])

    async def check_member(self, member):
        await self.check_guild(member.guild)
        users = await self.get_users(member.guild)
        if not member.bot and str(member.id) not in users:
            await self.update_user(member,
                                   {'uid': member.id, 'lvl': 1, 'xp': 0, 'xp_multiplier': 1, 'blacklist': False})

    async def member_set_lvl_xp(self, member, lvl, xp=0):
        if not member.bot:
            previous_level = int(lvl)

            while xp > self.max_xp_for(lvl):
                xp -= self.max_xp_for(lvl)
                lvl += 1
            while xp < 0:
                lvl -= 1
                xp += self.max_xp_for(lvl)

            await self.update_user(member, {'xp': xp, 'lvl': lvl})

            previous_role = member.top_role
            await self.member_role_manage(member, lvl)

            if previous_level < lvl:
                if previous_role != member.top_role:
                    return await member.guild.system_channel.send(
                        file=await self.member_create_rank_up_image(member,
                                                                    previous_level,
                                                                    lvl,
                                                                    previous_role,
                                                                    member.top_role))
                await member.guild.system_channel.send(
                    file=await self.member_create_lvl_image(member,
                                                            previous_level,
                                                            lvl))

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
        if 'blacklist' in data and data['blacklist'] is True:
            return
        xp_multiplier = 1
        if 'xp_multiplier' in data:
            xp_multiplier = data['xp_multiplier']
        if 'joined' in data:
            xp_earned = self.xp_for((t - data['joined']) / 60, xp_multiplier)
            data['xp'] += xp_earned
            await self.member_set_lvl_xp(member, data['lvl'], data['xp'])

    async def member_message_xp(self, member):
        await self.check_member(member)
        data = await self.get_user(member)
        if 'blacklist' in data and data['blacklist'] is True:
            return
        xp_multiplier = 1
        if 'xp_multiplier' in data:
            xp_multiplier = data['xp_multiplier']
        xp_earned = self.xp_for(2.5, xp_multiplier)
        data['xp'] += xp_earned
        await self.member_set_lvl_xp(member, data['lvl'], data['xp'])

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
        data = self.lvlsys_db.get(query.gid == member.guild.id)
        if data is None:
            data = {}
        if 'lvlsys' not in data:
            data['lvlsys'] = {}
        lvlsys_list = sorted(map(lambda x: (int(x[0]), x[1]), data['lvlsys'].items()), key=lambda x: x[0])
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

    async def lvlsys_set(self, guild_id, role_id, lvl):
        lvl = str(lvl)
        data = self.lvlsys_db.get(query.gid == guild_id)
        if data is None:
            self.lvlsys_db.insert({'gid': guild_id, 'lvlsys': {lvl: role_id}})
        else:
            if 'lvlsys' not in data:
                data['lvlsys'] = {}
            data['lvlsys'][lvl] = role_id
            self.lvlsys_db.update(operations.set('lvlsys', data['lvlsys']), query.gid == guild_id)

    async def lvlsys_remove(self, guild_id, lvl):
        lvl = str(lvl)
        data = self.lvlsys_db.get(query.gid == guild_id)
        if data is None:
            self.lvlsys_db.insert({'gid': guild_id, 'lvlsys': {}})
        else:
            if 'lvlsys' not in data:
                data['lvlsys'] = {}
            if lvl in data['lvlsys']:
                del data['lvlsys'][lvl]
            self.lvlsys_db.update(operations.set('lvlsys', data['lvlsys']), query.gid == guild_id)

    async def lvlsys_get_embed(self, guild):
        embed = discord.Embed(title='Error',
                              description='level system empty for this server',
                              color=discord.Color.red())

        data = self.lvlsys_db.get(query.gid == guild.id)
        if data is not None and 'lvlsys' in data:
            description = []
            for lvl, role_id in reversed(sorted(data['lvlsys'].items(), key=lambda x: x[0])):
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
                          aliases=['p'],
                          description="show user profile")
        async def _profile(self, ctx, *args):
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
                          description="show the leaderboard")
        async def _leaderboard(self, ctx, *args):
            await ctx.trigger_typing()
            await ctx.send(file=await self.parent.create_leaderboard_image(ctx.message.author))

        @commands.command(name='ranking',
                          aliases=[],
                          description="show the ranking")
        async def _ranking(self, ctx, *args):
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
                          description="send through the bot")
        @commands.has_permissions(administrator=True)
        async def _send(self, ctx, *args):
            if len(args) == 0:
                return await ctx.send(embed=discord.Embed(title='Help',
                                                          description='"send {msg}" to send into the system channel\n'
                                                                      '"send {channel_id} {msg}" to send'
                                                                      'into a specific channel',
                                                          color=discord.Color.red()))
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
                          description="set level command")
        @commands.has_permissions(administrator=True)
        async def _setlvl(self, ctx, *args):
            if len(args) == 0:
                return await ctx.send(embed=discord.Embed(title='Help',
                                                          description='"setlvl {level}" to set your level\n'
                                                                      '"setlvl {level} {search}" to set a level for a '
                                                                      'specific user',
                                                          color=discord.Color.red()))

            async def __setlvl(m):
                try:
                    lvl = int(args[0])
                    await self.parent.member_set_lvl_xp(m, lvl, xp=0)
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
                          description="level system commands")
        @commands.has_permissions(administrator=True)
        async def _lvlsys(self, ctx, *args):
            await ctx.trigger_typing()

            embed = discord.Embed(title='Help',
                                  description='"lvlsys update" to update the users to the new levelsystem\n'
                                              '"lvlsys boost {multiplier} {search}" to boost a user\n'
                                              '"lvlsys get" to display the levelsystem\n'
                                              '"lvlsys set {level} {role_id}" to set a role for a level\n'
                                              '"lvlsys remove {level}" to remove the level\n'
                                              '"lvlsys blacklist {search}" to blacklist a user\n'
                                              '"lvlsys whitelist {search}" to whitelist a user\n',
                                  color=discord.Color.red())

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

        @commands.command(name='coinflip', aliases=['cf', 'coin'], description="Toss a coin to your Witcher!")
        async def _coinflip(self, ctx):
            if random.randint(0, 1) == 0:
                res = 'kopf'
            else:
                res = 'zahl'
            message = await ctx.send(file=discord.File(os.path.join('images', '{}.gif'.format(res))))
            await asyncio.sleep(5)
            await message.delete()
            await ctx.send(file=discord.File(os.path.join('images', '{}.png'.format(res))))

        @commands.command(name='dice', aliases=[], description="Roll a dice to your Witcher!")
        async def _dice(self, ctx, *args):
            dice_string = 'Rolled a **{}**'
            if len(args) == 1:
                if args[0].isnumeric():
                    return await ctx.send(dice_string.format(random.randint(1, int(args[0]))))
            elif len(args) == 2:
                if args[0].isnumeric() and args[1].isnumeric():
                    opts = [int(args[0]), int(args[1])]
                    return await ctx.send(dice_string.format(random.randint(min(opts), max(opts))))
            await ctx.send(file=discord.File(os.path.join('images', '{}.png'.format(random.randint(1, 6)))))

        @commands.command(name='help', aliases=['h'], description="gives you help")
        async def _help(self, ctx):
            embed = discord.Embed(title='Help',
                                  description='',
                                  color=discord.Color.red())
            for command in sorted(self.parent.bot.commands, key=lambda x: x.name):
                embed.add_field(name=str(command.name), value=' - ' + str(command.description), inline=False)
            await ctx.send(embed=embed)

    class Events(commands.Cog):
        def __init__(self, parent):
            self.parent = parent

        @commands.Cog.listener()
        async def on_ready(self):
            self.parent.lprint('Bot is ready')

        @commands.Cog.listener()
        async def on_member_join(self, member):
            await self.parent.update_member(member)
            await member.send('Private message')

        @commands.Cog.listener()
        async def on_member_remove(self, member):
            await self.parent.remove_member(member)

        @commands.Cog.listener()
        async def on_message(self, message):
            if not message.author.bot:
                await self.parent.member_message_xp(message.author)

        @commands.Cog.listener()
        async def on_voice_state_update(self, member, before, after):
            t = round(time.time(), 2)
            if before.channel is None and after.channel is not None:
                # when joining
                await self.parent.member_joined_vc(member, t)
                self.parent.lprint(member, 'joined', after.channel)
            elif before.channel is not None and after.channel is None:
                # when leaving
                await self.parent.member_left_vc(member, t)
                self.parent.lprint(member, 'left', before.channel)
            else:
                # when moving
                self.parent.lprint(member, 'moved from', before.channel, 'to', after.channel)


if __name__ == '__main__':
    b = DiscordBot(TinyDB('dbs/users.json'), TinyDB('dbs/lvlsys.json'), PRINT_LOGGING)
    b.run(TOKEN)
