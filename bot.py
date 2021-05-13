from settings import *

import discord
from discord.ext import commands
from discord.utils import get

from tinydb import TinyDB, Query, operations

from helpers import tools, imgtools

import os
import time
import random
import aiohttp
import numpy as np
import cv2
import pygame
import pygame.freetype
import io

os.environ['SDL_AUDIODRIVER'] = 'dsp'

pygame.init()

query = Query()


class DiscordBot:
    def __init__(self, user_db, lvlsys_db, print_logging=False):
        intents = discord.Intents.default()
        intents.members = True

        self.print_logging = print_logging

        self.user_db = user_db
        self.lvlsys_db = lvlsys_db

        self.bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, intents=intents, help_command=None)

        self.session = None

        self.bot.add_cog(self.Events(self))
        self.bot.add_cog(self.Commands(self))

        self.fonts = {
            'default': pygame.freetype.Font(os.path.join('fonts', 'Product_Sans_Regular.ttf'))
        }
        for font in self.fonts.values():
            font.antialiased = True

        self.emojis = {}
        emoji_path = os.path.join('images', 'emojis')
        for f in os.listdir(emoji_path):
            if f.endswith('.png'):
                img = cv2.imread(os.path.join(emoji_path, f), cv2.IMREAD_UNCHANGED)
                img = cv2.resize(img, (PROFILE_EMOJI_POSITION[3], PROFILE_EMOJI_POSITION[2]))
                img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
                self.emojis[f[:-4]] = img

    async def stop(self):
        if self.session is not None:
            await self.session.close()

    def run(self, token):
        self.bot.run(token)

    def lprint(self, *args):
        if self.print_logging:
            print(*args)

    @staticmethod
    def max_xp_for(lvl):
        return (lvl - 1) * 10 + 100

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

    async def get_leaderboard(self):
        return sorted(self.user_db.all(), key=lambda x: (x['lvl'], x['xp']), reverse=True)

    async def get_leaderboard_rank(self, member):
        return list(map(lambda x: x['uid'], await self.get_leaderboard())).index(member.id) + 1

    async def member_create_get_image(self, member):
        await self.check_member(member)

        #
        # Retrieve user data
        #
        data = self.user_db.get(query.uid == member.id)
        name = member.name
        if member.nick is not None:
            name = member.nick

        data_xp_multiplier = data['xp_multiplier']
        data_xp = int(data['xp'])
        data_max_xp = int(self.max_xp_for(data['lvl']))
        data_percentage = data_xp / data_max_xp
        data_rank = await self.get_leaderboard_rank(member)

        #
        # Load Template Image
        #
        img = cv2.imread(os.path.join('images', 'profile_template.png'), cv2.IMREAD_UNCHANGED)
        mask = img[:, :, 3]

        #
        # Add Avatar to Image
        #
        if self.session is None:
            self.session = aiohttp.ClientSession(loop=self.bot.loop)

        async with self.session.get(str(member.avatar_url_as(format="png"))) as response:
            avatar_bytes = await response.read()
        avatar_image = cv2.imdecode(np.frombuffer(avatar_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

        avatar_image = cv2.resize(avatar_image, (PROFILE_AVATAR_POSITION[3], PROFILE_AVATAR_POSITION[2]))
        if avatar_image.shape[2] == 3:
            avatar_image = cv2.cvtColor(avatar_image, cv2.COLOR_RGB2RGBA)

        avatar_full = np.zeros(img.shape, dtype=np.uint8)
        avatar_full[
            PROFILE_AVATAR_POSITION[1]:PROFILE_AVATAR_POSITION[3] + PROFILE_AVATAR_POSITION[1],
            PROFILE_AVATAR_POSITION[0]:PROFILE_AVATAR_POSITION[2] + PROFILE_AVATAR_POSITION[0],
            :
        ] = avatar_image[:, :, :]

        img[np.where(mask == 0)] = avatar_full[np.where(mask == 0)]

        #
        # Add Progress Bar to Image
        #
        progress_img = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.uint8)

        start_pos = (PROFILE_PROGRESS_POSITION[0], PROFILE_PROGRESS_POSITION[1])
        end_pos = (int(PROFILE_PROGRESS_POSITION[0] + (PROFILE_PROGRESS_POSITION[2] * data_percentage)),
                   int(PROFILE_PROGRESS_POSITION[1] + (PROFILE_PROGRESS_POSITION[3] * data_percentage)))

        progress_img = imgtools.progress_bar(progress_img,
                                             start_pos,
                                             end_pos,
                                             PROFILE_PROGRESS_RADIUS,
                                             imgtools.LinearGradientColor((255, 0, 0, 255), (0, 255, 0, 255), 1))

        mask = progress_img[:, :, 3]
        img[np.where(mask != 0)] = progress_img[np.where(mask != 0)]

        #
        # Add Emoji To Image
        #
        emoji_id = tools.from_char(member.top_role.name[0])
        if emoji_id not in self.emojis:
            emoji_id = '0'
        img[
            PROFILE_EMOJI_POSITION[1]:PROFILE_EMOJI_POSITION[3] + PROFILE_EMOJI_POSITION[1],
            PROFILE_EMOJI_POSITION[0]:PROFILE_EMOJI_POSITION[2] + PROFILE_EMOJI_POSITION[0],
            :
        ] = self.emojis[emoji_id]

        #
        # Add Texts to Image
        #
        for text_call in PROFILE_TEXTS:
            text_obj = text_call({'name': name,
                                  'color': member.color.to_rgb(),
                                  'lvl': data['lvl'],
                                  'xp': data_xp,
                                  'max_xp': data_max_xp,
                                  'rank': data_rank,
                                  'xp_multiplier': data_xp_multiplier})
            text_full = np.zeros(img.shape, dtype=np.uint8)
            text_surf, _ = self.fonts[text_obj['font']].render(text_obj['text'],
                                                               imgtools.rgb_to_bgr(text_obj['color']),
                                                               size=text_obj['size'])
            text_img_t = pygame.surfarray.pixels3d(text_surf).swapaxes(0, 1)
            text_img = np.zeros((text_img_t.shape[0], text_img_t.shape[1], 4), dtype=np.uint8)
            text_alpha = pygame.surfarray.pixels_alpha(text_surf).swapaxes(0, 1)
            text_img[:, :, 3] = text_alpha
            text_img[:, :, :3] = text_img_t
            if 'align_right' in text_obj and text_obj['align_right']:
                text_full[
                    text_obj['pos'][1]:text_obj['pos'][1] + text_img.shape[0],
                    text_obj['pos'][0] - text_img.shape[1]:text_obj['pos'][0],
                    :
                ] = text_img[:, :, :]
            else:
                text_full[
                    text_obj['pos'][1]:text_obj['pos'][1] + text_img.shape[0],
                    text_obj['pos'][0]:text_obj['pos'][0] + text_img.shape[1],
                    :
                ] = text_img[:, :, :]
            mask = text_full[:, :, 3]
            img[np.where(mask != 0)] = text_full[np.where(mask != 0)]

        is_success, buffer = cv2.imencode('.png', img)
        io_buf = io.BytesIO(buffer)
        return discord.File(filename="member.png", fp=io_buf)

    async def check_member(self, member):
        if not member.bot and not self.user_db.contains(query.uid == member.id):
            self.user_db.insert({'uid': member.id, 'lvl': 1, 'xp': 0, 'xp_multiplier': 1, 'blacklist': False})

    async def member_set_lvl_xp(self, guild, member, lvl, xp=0):
        if not member.bot:
            self.user_db.update_multiple([
                (operations.set('xp', xp), query.uid == member.id),
                (operations.set('lvl', lvl), query.uid == member.id)
            ])
            await self.member_role_manage(guild, member, lvl)

    async def update_member(self, guild, member):
        await self.check_member(member)
        data = self.user_db.get(query.uid == member.id)
        await self.member_role_manage(guild, member, data['lvl'])

    async def blacklist_get_embed(self, members):
        description = []
        for user in self.user_db.search(query.blacklist == True):
            member = get(members, id=int(user['uid']))
            if member is not None:
                description.append(str(member))
        return discord.Embed(title="Blacklist",
                             description='\n'.join(description),
                             color=discord.Color.green())

    async def member_set_xp_multiplier(self, member, xp_multiplier):
        await self.check_member(member)
        self.user_db.update(operations.set('xp_multiplier', xp_multiplier), query.uid == member.id)

    async def member_set_blacklist(self, member, blacklist):
        await self.check_member(member)
        self.user_db.update(operations.set('blacklist', blacklist), query.uid == member.id)

    async def member_joined_vc(self, member, t):
        await self.check_member(member)
        self.user_db.update(operations.set('joined', t), query.uid == member.id)

    async def member_left_vc(self, guild, member, t):
        await self.check_member(member)
        data = self.user_db.get(query.uid == member.id)
        if 'blacklist' in data and data['blacklist'] is True:
            return
        xp_multiplier = 1
        if 'xp_multiplier' in data:
            xp_multiplier = data['xp_multiplier']
        if 'joined' in data:
            xp_earned = self.xp_for((t - data['joined']) / 60, xp_multiplier)
            data['xp'] += xp_earned
            while data['xp'] > self.max_xp_for(data['lvl']):
                data['xp'] -= self.max_xp_for(data['lvl'])
                data['lvl'] += 1
            await self.member_set_lvl_xp(guild, member, data['lvl'], data['xp'])

    async def member_message_xp(self, guild, member):
        await self.check_member(member)
        data = self.user_db.get(query.uid == member.id)
        if 'blacklist' in data and data['blacklist'] is True:
            return
        xp_multiplier = 1
        if 'xp_multiplier' in data:
            xp_multiplier = data['xp_multiplier']
        xp_earned = self.xp_for(2.5, xp_multiplier)
        data['xp'] += xp_earned
        while data['xp'] > self.max_xp_for(data['lvl']):
            data['xp'] -= self.max_xp_for(data['lvl'])
            data['lvl'] += 1
        await self.member_set_lvl_xp(guild, member, data['lvl'], data['xp'])

    @staticmethod
    async def give_role(guild, member, role_id):
        role = get(guild.roles, id=role_id)
        if role is not None:
            await member.add_roles(role)

    @staticmethod
    async def remove_role(guild, member, role_id):
        role = get(guild.roles, id=role_id)
        if role is not None:
            await member.remove_roles(role)

    async def member_role_manage(self, guild, member, lvl):
        data = self.lvlsys_db.get(query.gid == guild.id)
        if data is None:
            data = {}
        if 'lvlsys' not in data:
            data['lvlsys'] = {}
        lvlsys_list = sorted(map(lambda x: (int(x[0]), x[1]), data['lvlsys'].items()), key=lambda x: x[0])
        role_to_give = None
        for i in range(len(lvlsys_list)):
            is_last = i == len(lvlsys_list) - 1
            if (is_last and lvl >= lvlsys_list[i][0]) or (
                    (not is_last) and lvlsys_list[i][0] <= lvl < lvlsys_list[i + 1][0]):
                role_to_give = lvlsys_list[i][1]
            else:
                await self.remove_role(guild, member, lvlsys_list[i][0])
        if role_to_give is not None:
            await self.give_role(guild, member, role_to_give)

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
            for lvl, role_id in data['lvlsys'].items():
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
                return await ctx.send(file=await self.parent.member_create_get_image(ctx.message.author))
            else:
                member = await self.parent.search_member(ctx, ' '.join(args))
                if member is not None:
                    return await ctx.send(file=await self.parent.member_create_get_image(member))

            return await ctx.send(embed=discord.Embed(title='Error',
                                                      description='No user was found!',
                                                      color=discord.Color.red()))

        @commands.command(name='setlvl',
                          aliases=['setlevel', 'sl'],
                          description="set level command")
        @commands.has_permissions(administrator=True)
        async def _setlvl(self, ctx, *args):
            if len(args) == 0 or not args[0].isnumeric():
                return await ctx.send(embed=discord.Embed(title='Help',
                                                          description='"setlvl {level}" to set your level\n'
                                                                      '"setlvl {level} {search}" to set a level for a '
                                                                      'specific user',
                                                          color=discord.Color.red()))

            async def __setlvl(m):
                lvl = int(args[0])
                await self.parent.member_set_lvl_xp(ctx.message.guild, m, lvl, xp=0)
                await ctx.send(embed=discord.Embed(title='Success',
                                                   description='Level was set successfully!',
                                                   color=discord.Color.green()))
                await ctx.send(file=await self.parent.member_create_get_image(m))

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
                        await self.parent.update_member(ctx.message.guild, member)
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
                        await ctx.send(file=await self.parent.member_create_get_image(m))
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
                    await ctx.send(embed=await self.parent.blacklist_get_embed(ctx.message.guild.members))

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
                await ctx.send(file=discord.File(os.path.join('images', 'kopf.gif')))
            else:
                await ctx.send(file=discord.File(os.path.join('images', 'zahl.gif')))

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
            await self.parent.update_member(member.guild, member)
            await member.send('Private message')

        @commands.Cog.listener()
        async def on_message(self, message):
            await self.parent.member_message_xp(message.guild, message.author)

        @commands.Cog.listener()
        async def on_voice_state_update(self, member, before, after):
            t = round(time.time(), 2)
            if before.channel is None and after.channel is not None:
                # when joining
                await self.parent.member_joined_vc(member, t)
                self.parent.lprint(member, 'joined', after.channel)
            elif before.channel is not None and after.channel is None:
                # when leaving
                await self.parent.member_left_vc(before.channel.guild, member, t)
                self.parent.lprint(member, 'left', before.channel)
            else:
                # when moving
                self.parent.lprint(member, 'moved from', before.channel, 'to', after.channel)


if __name__ == '__main__':
    b = DiscordBot(TinyDB('dbs/users.json'), TinyDB('dbs/lvlsys.json'), PRINT_LOGGING)
    b.run(TOKEN)
