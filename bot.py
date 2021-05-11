from settings import *

import discord
from discord.ext import commands
from discord.utils import get

from tinydb import TinyDB, Query, operations

import time

query = Query()


class DiscordBot:
    def __init__(self, user_db, lvlsys_db, print_logging=False):
        intents = discord.Intents.default()
        intents.members = True

        self.print_logging = print_logging

        self.user_db = user_db
        self.lvlsys_db = lvlsys_db

        self.bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, intents=intents)
        self.bot.add_cog(self.Events(self))
        self.bot.add_cog(self.Commands(self))

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
        return round((ctime * boost) / 60, 2)

    def member_get_embed(self, member):
        self.check_member(member)
        data = self.user_db.get(query.uid == member.id)
        name = member.name
        if member.nick is not None:
            name = member.nick
        description = 'LVL: ' + str(data['lvl']) \
                      + '\nXP: ' + str(data['xp']) + ' / ' + str(self.max_xp_for(data['lvl'])) \
                      + '\nXP Multiplier: ' + str(data['xp_multiplier']) + 'x' \
                      + '\nJoin Date: ' + str(member.joined_at)
        embed = discord.Embed(title=str(name), description=description,
                              color=discord.Color.green())
        embed.set_footer(text='ID: ' + str(member.id))
        embed.set_thumbnail(url=member.avatar_url)
        return embed

    def check_member(self, member):
        if not self.user_db.contains(query.uid == member.id):
            self.user_db.insert({'uid': member.id, 'lvl': 1, 'xp': 0, 'xp_multiplier': 1})

    def member_joined_vc(self, member, t):
        self.check_member(member)
        self.user_db.update(operations.set('joined', t), query.uid == member.id)

    def member_left_vc(self, guild, member, t):
        self.check_member(member)
        data = self.user_db.get(query.uid == member.id)
        xp_multiplier = 1
        if 'xp_multiplier' in data:
            xp_multiplier = data['xp_multiplier']
        if 'joined' in data:
            xp_earned = self.xp_for(t - data['joined'], xp_multiplier)
            data['xp'] += xp_earned
            while data['xp'] > self.max_xp_for(data['lvl']):
                data['xp'] -= self.max_xp_for(data['lvl'])
                data['lvl'] += 1
            self.user_db.update_multiple([
                (operations.set('xp', data['xp']), query.uid == member.id),
                (operations.set('lvl', data['lvl']), query.uid == member.id)
            ])
            self.member_role_manage(guild, member, data['lvl'])

    @staticmethod
    def give_role(guild, member, role_id):
        role = get(guild.roles, id=role_id)
        if role is not None:
            member.add_roles(role)

    @staticmethod
    def remove_role(guild, member, role_id):
        role = get(guild.roles, id=role_id)
        if role is not None:
            member.remove_roles(role)

    def member_role_manage(self, guild, member, lvl):
        data = self.lvlsys_db.get(query.gid == guild.id)
        if data is None:
            data = {}
        if 'lvlsys' not in data:
            data['lvlsys'] = {}
        lvlsys_list = sorted(map(lambda x: (int(x[0]), x[1]), data['lvlsys'].items()), key=lambda x: x[0])
        for i in range(len(lvlsys_list)):
            if i == len(lvlsys_list) - 1:
                if lvl >= lvlsys_list[i][0]:
                    self.give_role(guild, member, lvlsys_list[i][1])
                    return
            else:
                if lvlsys_list[i][0] <= lvl < lvlsys_list[i + 1][0]:
                    self.give_role(guild, member, lvlsys_list[i][1])
                    return
            self.remove_role(guild, member, lvlsys_list[i][0])

    def lvlsys_set(self, guild_id, role_id, lvl):
        lvl = str(lvl)
        data = self.lvlsys_db.get(query.gid == guild_id)
        if data is None:
            self.lvlsys_db.insert({'gid': guild_id, 'lvlsys': {lvl: role_id}})
        else:
            if 'lvlsys' not in data:
                data['lvlsys'] = {}
            data['lvlsys'][lvl] = role_id
            self.lvlsys_db.update(operations.set('lvlsys', data['lvlsys']), query.gid == guild_id)

    def lvlsys_remove(self, guild_id, lvl):
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

    def lvlsys_get_embed(self, guild):
        embed = discord.Embed(title='Error',
                              description='level system empty for this server',
                              color=discord.Color.red())

        data = self.lvlsys_db.get(query.gid == guild.id)
        if data is not None and 'lvlsys' in data:
            description = []
            for lvl, role_id in data['lvlsys'].items():
                role = get(guild.roles, id=role_id)
                if role is None:
                    self.lvlsys_remove(guild.id, lvl)
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
                return await(ctx.send(embed=self.parent.member_get_embed(ctx.message.author)))
            else:
                search = ' '.join(args)
                if search.isnumeric():
                    member = get(ctx.message.guild.members, id=int(search))
                    if member is not None:
                        return await(ctx.send(embed=self.parent.member_get_embed(member)))
                member = get(ctx.message.guild.members, nick=search)
                if member is not None:
                    return await(ctx.send(embed=self.parent.member_get_embed(member)))
                member = get(ctx.message.guild.members, name=search)
                if member is not None:
                    return await(ctx.send(embed=self.parent.member_get_embed(member)))

            return await(ctx.send(embed=discord.Embed(title='Error',
                                                      description='No user was found!',
                                                      color=discord.Color.red())))

        @commands.command(name='lvlsys',
                          aliases=['levelsystem', 'lvlsystem', 'levelsys'],
                          description="level system commands")
        @commands.has_permissions(manage_roles=True)
        async def _lvlsys(self, ctx, *args):
            await ctx.trigger_typing()

            embed = discord.Embed(title='Help',
                                  description='"lvlsys get" to display the levelsystem\n'
                                              '"lvlsys set {level} {role_id}" to set a role for a level\n'
                                              '"lvlsys remove {level}" to remove the level\n',
                                  color=discord.Color.red())

            if len(args) == 0:
                pass

            elif args[0] in ['get']:
                return await ctx.send(embed=self.parent.lvlsys_get_embed(ctx.message.guild))

            elif args[0] in ['set']:
                if len(args) == 3 and args[1].isnumeric() and args[2].isnumeric():
                    rid = int(args[2])
                    for role in ctx.message.guild.roles:
                        if role.id == rid:
                            self.parent.lvlsys_set(ctx.message.guild.id, role.id, int(args[1]))

                            embed = discord.Embed(title='',
                                                  description='Role-Level was set!',
                                                  color=discord.Color.green())
                            await ctx.send(embed=embed)
                            return await(ctx.send(embed=self.parent.lvlsys_get_embed(ctx.message.guild)))

                    embed = discord.Embed(title='Error',
                                          description='Role-ID was not found!',
                                          color=discord.Color.red())

            elif args[0] in ['remove', 'rm', 'del', 'delete']:
                if len(args) == 2 and args[1].isnumeric():
                    self.parent.lvlsys_remove(ctx.message.guild.id, int(args[1]))
                    embed = discord.Embed(title='',
                                          description='Role-Level was removed!',
                                          color=discord.Color.green())
                    await ctx.send(embed=embed)
                    return await(ctx.send(embed=self.parent.lvlsys_get_embed(ctx.message.guild)))

            await ctx.send(embed=embed)

        @commands.command(name='member',
                          aliases=['user', 'player'],
                          description="member system commands")
        async def _member(self, ctx, *args):
            pass

    class Events(commands.Cog):
        def __init__(self, parent):
            self.parent = parent

        @commands.Cog.listener()
        async def on_ready(self):
            self.parent.lprint('Bot is ready')

        @commands.Cog.listener()
        async def on_voice_state_update(self, member, before, after):
            t = round(time.time(), 2)
            if before.channel is None and after.channel is not None:
                # when joining
                self.parent.member_joined_vc(member, t)
                self.parent.lprint(member, 'joined', after.channel)
            elif before.channel is not None and after.channel is None:
                # when leaving
                self.parent.member_left_vc(before.channel.guild, member, t)
                self.parent.lprint(member, 'left', before.channel)
            else:
                # when moving
                self.parent.lprint(member, 'moved from', before.channel, 'to', after.channel)


if __name__ == '__main__':
    b = DiscordBot(TinyDB('dbs/users.json'), TinyDB('dbs/lvlsys.json'), PRINT_LOGGING)
    b.run(TOKEN)
