import time

from helpers import tools
from helpers.spark_module import SparkModule
import discord
import discord.commands
import discord.ext.commands
from discord.utils import get
from .settings import SETTINGS
from .web import API_PAGES


class LevelsystemModule(SparkModule):
    name = 'levelsystem'
    title = 'Levelsystem'
    description = 'Module for leveling'
    settings = SETTINGS
    api_pages = API_PAGES

    boost_origin_prefix = 'boost'
    voice_origin = 'voice'
    message_origin = 'message'

    async def lvlsys_get_embed(self, guild):
        embed = discord.Embed(title='',
                              description=self.bot.i18n.get('LEVELSYSTEM_EMPTY_ERROR'),
                              color=discord.Color.red())

        data = self.bot.db.get_levelsystem(guild.id)
        if data is not None and len(data) > 0:
            description = []
            for level, role_id in reversed(sorted(map(lambda x: (x.level, x.role_id), data), key=lambda x: x[0])):
                role = get(guild.roles, id=role_id)
                if role is None:
                    self.bot.db.remove_levelsystem_by_level(guild.id, level)
                else:
                    description.append(self.bot.i18n.get('LEVELSYSTEM_LEVEL_ROLE').format(level, role.name, role.id))
            embed = discord.Embed(title=self.bot.i18n.get('LEVELSYSTEM_TITLE'),
                                  description='\n'.join(description),
                                  color=discord.Color.green())
        return embed

    def __init__(self, bot):
        super().__init__(bot)

        @bot.has_permissions(administrator=True)
        async def get_levelsystem(ctx: discord.commands.context.ApplicationContext):
            return await ctx.respond(embed=await self.lvlsys_get_embed(ctx.guild))

        @bot.has_permissions(administrator=True)
        async def set_levelsystem(ctx: discord.commands.context.ApplicationContext,
                                  level: discord.commands.Option(
                                      int,
                                      description=bot.i18n.get('LEVELSYSTEM_SET_LEVEL_ROLE_LEVEL_OPTION'),
                                  ),
                                  role: discord.commands.Option(
                                      discord.Role,
                                      description=bot.i18n.get('LEVELSYSTEM_SET_LEVEL_ROLE_ROLE_OPTION'),
                                  )):
            self.bot.db.set_levelsystem(ctx.guild.id, level, role.id)

            await ctx.respond(embed=discord.Embed(title='',
                                                  description=self.bot.i18n.get('LEVELSYSTEM_SET_SUCCESSFUL'),
                                                  color=discord.Color.green()))
            return await ctx.respond(embed=await self.lvlsys_get_embed(ctx.guild))

        @bot.has_permissions(administrator=True)
        async def remove_levelsystem(ctx: discord.commands.context.ApplicationContext,
                                     level: discord.commands.Option(
                                         int,
                                         description=bot.i18n.get('LEVELSYSTEM_REMOVE_LEVEL_ROLE_LEVEL_OPTION'),
                                     )):
            self.bot.db.remove_levelsystem_by_level(ctx.guild.id, level)
            await ctx.respond(embed=discord.Embed(title='',
                                                  description=self.bot.i18n.get('LEVELSYSTEM_REMOVE_SUCCESSFUL'),
                                                  color=discord.Color.green()))
            return await ctx.respond(embed=await self.lvlsys_get_embed(ctx.guild))

        @bot.has_permissions(administrator=True)
        async def boost_add(ctx: discord.commands.context.ApplicationContext,
                            member: discord.commands.Option(
                                discord.Member,
                                description=bot.i18n.get('LEVELSYSTEM_BOOST_ADD_MEMBER_OPTION'),
                            ),
                            amount: discord.commands.Option(
                                float,
                                description=bot.i18n.get('LEVELSYSTEM_BOOST_ADD_AMOUNT_OPTION'),
                            )):
            if not await self.leveling_allowed(member):
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('BOT_NOT_ALLOWED_LEVELING'),
                                                             color=discord.Color.red()))
            self.bot.db.add_xp_boost(member.guild.id, member.id, amount, 'command')
            await ctx.respond(embed=discord.Embed(title='',
                                                  description=self.bot.i18n.get('LEVELSYSTEM_BOOST_ADD_SUCCESSFUL'),
                                                  color=discord.Color.green()))

        @bot.has_permissions(administrator=True)
        async def set_level(ctx: discord.commands.context.ApplicationContext,
                            member: discord.commands.Option(
                                discord.Member,
                                description=bot.i18n.get('LEVELSYSTEM_SET_LEVEL_MEMBER_OPTION'),
                            ),
                            level: discord.commands.Option(
                                float,
                                description=bot.i18n.get('LEVELSYSTEM_SET_LEVEL_LEVEL_OPTION'),
                            )):
            if not await self.leveling_allowed(member):
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('BOT_BOOSTING_NOT_ALLOWED'),
                                                             color=discord.Color.red()))
            await self.check_level_user(member)
            await self.member_set_lvl(member, level)
            await ctx.respond(embed=discord.Embed(title='',
                                                  description=self.bot.i18n.get('LEVELSYSTEM_SET_LEVEL_SUCCESSFUL')
                                                  .format(level),
                                                  color=discord.Color.green()))

        @bot.has_permissions(administrator=True)
        async def blacklist_user(ctx: discord.commands.context.ApplicationContext,
                            member: discord.commands.Option(
                                discord.Member,
                                description=bot.i18n.get('LEVELSYSTEM_BLACKLIST_MEMBER_OPTION'),
                            ),
                            blacklist: discord.commands.Option(
                                bool,
                                description=bot.i18n.get('LEVELSYSTEM_BLACKLIST_BLACKLIST_OPTION'),
                            )):

            await self.check_level_user(member)
            self.bot.db.update_level_user(member.guild.id, member.id, {
                'blacklisted': blacklist,
            })

            if blacklist:
                await ctx.respond(
                    embed=discord.Embed(title='',
                                        description=self.bot.i18n.get('LEVELSYSTEM_BLACKLIST_SUCCESSFUL'),
                                        color=discord.Color.green()))
            else:
                await ctx.respond(
                    embed=discord.Embed(title='',
                                        description=self.bot.i18n.get('LEVELSYSTEM_BLACKLIST_REMOVE_SUCCESSFUL'),
                                        color=discord.Color.green()))

        @bot.has_permissions(administrator=True)
        async def blacklisted_users(ctx: discord.commands.context.ApplicationContext):
            description = []
            for user in self.bot.db.get_blacklisted_level_users(ctx.guild.id, True):
                member = get(ctx.guild.members, id=int(user.user_id))
                if member is not None:
                    description.append(str(member))
            return await ctx.respond(embed=discord.Embed(
                title=self.bot.i18n.get('LEVELSYSTEM_BLACKLISTED_TITLE'),
                description='\n'.join(description),
                color=discord.Color.green()))

        async def profile(ctx: discord.commands.context.ApplicationContext,
                          member: discord.commands.Option(
                              discord.Member,
                              description=bot.i18n.get('LEVELSYSTEM_PROFILE_MEMBER_OPTION'),
                              default=None
                          )):
            if member is None:
                member = ctx.author
            if not await self.leveling_allowed(member):
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('BOT_NOT_ALLOWED_LEVELING'),
                                                             color=discord.Color.red()))
            await ctx.defer()

            await ctx.respond(file=await self.member_create_profile_image(member))

        async def leaderboard(ctx: discord.commands.context.ApplicationContext):
            await ctx.defer()

            await ctx.respond(file=await self.create_leaderboard_image(ctx.author))

        levelsystem = discord.SlashCommandGroup(
            name=self.bot.i18n.get('LEVELSYSTEM_COMMAND'),
            description=self.bot.i18n.get('LEVELSYSTEM_COMMAND_DESCRIPTION'),
        )
        levelsystem.subcommands.append(discord.SlashCommand(
            func=get_levelsystem,
            name=self.bot.i18n.get('LEVELSYSTEM_GET_COMMAND'),
            description=self.bot.i18n.get('LEVELSYSTEM_GET_COMMAND_DESCRIPTION'),
            parent=levelsystem
        ))
        levelsystem.subcommands.append(discord.SlashCommand(
            func=set_levelsystem,
            name=self.bot.i18n.get('LEVELSYSTEM_SET_COMMAND'),
            description=self.bot.i18n.get('LEVELSYSTEM_SET_COMMAND_DESCRIPTION'),
            parent=levelsystem
        ))
        levelsystem.subcommands.append(discord.SlashCommand(
            func=remove_levelsystem,
            name=self.bot.i18n.get('LEVELSYSTEM_REMOVE_COMMAND'),
            description=self.bot.i18n.get('LEVELSYSTEM_REMOVE_COMMAND_DESCRIPTION'),
            parent=levelsystem
        ))
        levelsystem.subcommands.append(discord.SlashCommand(
            func=boost_add,
            name=self.bot.i18n.get('LEVELSYSTEM_BOOST_ADD_COMMAND'),
            description=self.bot.i18n.get('LEVELSYSTEM_BOOST_ADD_COMMAND_DESCRIPTION'),
            parent=levelsystem
        ))
        levelsystem.subcommands.append(discord.SlashCommand(
            func=set_level,
            name=self.bot.i18n.get('LEVELSYSTEM_SET_LEVEL_COMMAND'),
            description=self.bot.i18n.get('LEVELSYSTEM_SET_LEVEL_COMMAND_DESCRIPTION'),
            parent=levelsystem
        ))
        levelsystem.subcommands.append(discord.SlashCommand(
            func=blacklist_user,
            name=self.bot.i18n.get('LEVELSYSTEM_BLACKLIST_COMMAND'),
            description=self.bot.i18n.get('LEVELSYSTEM_BLACKLIST_COMMAND_DESCRIPTION'),
            parent=levelsystem
        ))
        levelsystem.subcommands.append(discord.SlashCommand(
            func=blacklisted_users,
            name=self.bot.i18n.get('LEVELSYSTEM_BLACKLISTED_COMMAND'),
            description=self.bot.i18n.get('LEVELSYSTEM_BLACKLISTED_COMMAND_DESCRIPTION'),
            parent=levelsystem
        ))
        self.commands = [
            levelsystem,
            discord.SlashCommand(
                func=profile,
                name=self.bot.i18n.get('LEVELSYSTEM_PROFILE_COMMAND'),
                description=self.bot.i18n.get('LEVELSYSTEM_PROFILE_COMMAND_DESCRIPTION'),
            ),
            discord.SlashCommand(
                func=leaderboard,
                name=self.bot.i18n.get('LEVELSYSTEM_LEADERBOARD_COMMAND'),
                description=self.bot.i18n.get('LEVELSYSTEM_LEADERBOARD_COMMAND_DESCRIPTION'),
            )
        ]

    @staticmethod
    def get_lvl(lvl):
        if lvl < 0 and lvl % 1 != 0:
            return int(lvl) - 1
        else:
            return int(lvl)

    @staticmethod
    def max_xp_for(lvl):
        return int(max(100, LevelsystemModule.get_lvl(lvl) * 10 + 90))

    @staticmethod
    def lvl_xp_add(xp, lvl):
        return xp / LevelsystemModule.max_xp_for(lvl)

    @staticmethod
    def lvl_get_xp(lvl):
        return int((abs(lvl) % 1) * LevelsystemModule.max_xp_for(lvl))

    async def member_create_profile_image_by_template(self, member, template):
        await self.check_level_user(member)

        user = self.bot.db.get_level_user(member.guild.id, member.id)
        name = member.display_name

        data_xp_multiplier = await self.get_member_xp_multiplier(member)
        data_xp = self.lvl_get_xp(user.level)
        data_max_xp = self.max_xp_for(user.level)
        data_percentage = data_xp / data_max_xp
        data_rank = await self.get_ranking_rank(member)

        data_obj = {'member': member,
                    'name': name,
                    'color': member.color.to_rgb(),
                    'lvl': self.get_lvl(user.level),
                    'xp': data_xp,
                    'max_xp': data_max_xp,
                    'xp_percentage': data_percentage,
                    'rank': data_rank,
                    'xp_multiplier': data_xp_multiplier,
                    'avatar_url': str(member.display_avatar.with_format('png'))}

        img_buf = await self.bot.image_creator.create(template(data_obj))
        return discord.File(filename="member.png", fp=img_buf)

    async def member_create_profile_image(self, member):
        return await self.member_create_profile_image_by_template(
            member, self.bot.module_manager.settings.get(member.guild.id, 'PROFILE_IMAGE'))

    async def member_create_level_up_image_by_template(self, member, old_lvl, new_lvl, template):
        name = member.display_name

        data_obj = {'member': member,
                    'old_lvl': self.get_lvl(old_lvl),
                    'new_lvl': self.get_lvl(new_lvl),
                    'color': member.color.to_rgb(),
                    'name': name}

        img_buf = await self.bot.image_creator.create(template(data_obj))
        return discord.File(filename="lvlup.png", fp=img_buf)

    async def member_create_level_up_image(self, member, old_lvl, new_lvl):
        return await self.member_create_level_up_image_by_template(
            member, old_lvl, new_lvl, self.bot.module_manager.settings.get(member.guild.id, 'LEVEL_UP_IMAGE'))

    async def member_create_rank_up_image_by_template(self, member, old_lvl, new_lvl, old_role, new_role, template):
        name = member.display_name

        data_obj = {'member': member,
                    'old_lvl': self.get_lvl(old_lvl),
                    'new_lvl': self.get_lvl(new_lvl),
                    'old_role': old_role,
                    'new_role': new_role,
                    'old_color': old_role.color.to_rgb(),
                    'new_color': new_role.color.to_rgb(),
                    'name': name}

        img_buf = await self.bot.image_creator.create(template(data_obj))
        return discord.File(filename="rankup.png", fp=img_buf)

    async def member_create_rank_up_image(self, member, old_lvl, new_lvl, old_role, new_role):
        return await self.member_create_rank_up_image_by_template(
            member, old_lvl, new_lvl, old_role, new_role,
            self.bot.module_manager.settings.get(member.guild.id, 'RANK_UP_IMAGE'))

    async def check_send_rank_level_image(self, member, lvl, old_level, old_role):
        if old_level is not None and self.get_lvl(old_level) < self.get_lvl(lvl):
            if old_role != member.top_role:
                self.bot.bot.loop.create_task(member.guild.system_channel.send(
                    file=await self.member_create_rank_up_image(member,
                                                                old_level,
                                                                lvl,
                                                                old_role,
                                                                member.top_role)))
                return
            self.bot.bot.loop.create_task(member.guild.system_channel.send(
                file=await self.member_create_level_up_image(member,
                                                             old_level,
                                                             lvl)))

    async def create_ranking_image_by_template(self, member, ranked_users, template):
        data_obj = await self.get_advanced_user_infos(member.guild, ranked_users)

        img_buf = await self.bot.image_creator.create(template(data_obj), max_size=(-1, 8000))
        return discord.File(filename="ranking.png", fp=img_buf)

    async def create_ranking_image(self, member, ranked_users):
        return await self.create_ranking_image_by_template(
            member, ranked_users, self.bot.module_manager.settings.get(member.guild.id, 'RANKING_IMAGE'))

    async def create_leaderboard_image_by_template(self, member, template):
        ranking = await self.get_ranking(member.guild)
        return await self.create_ranking_image_by_template(
            member, ranking[:self.bot.module_manager.settings.get(member.guild.id, 'LEADERBOARD_AMOUNT')], template)

    async def create_leaderboard_image(self, member):
        ranking = await self.get_ranking(member.guild)
        return await self.create_ranking_image(
            member, ranking[:self.bot.module_manager.settings.get(member.guild.id, 'LEADERBOARD_AMOUNT')])

    async def leveling_allowed(self, member: discord.Member):
        return self.bot.module_manager.settings.get(member.guild.id, 'ALLOW_BOT_LEVELING') or not member.bot

    async def get_ranking_rank(self, member):
        return list(map(lambda x: x.user_id, await self.get_ranking(member.guild))).index(member.id) + 1

    async def get_ranking(self, guild):
        users = self.bot.db.get_level_users(guild.id)
        users = sorted(users, key=lambda x: x.level, reverse=True)
        for i in range(len(users)):
            users[i].rank = i + 1
        return users

    async def get_advanced_user_infos(self, guild, ranked_users):
        user_infos = []
        for user in ranked_users:
            member = get(guild.members, id=int(user.user_id))
            if member is not None and await self.leveling_allowed(member):
                name = member.display_name
                current_xp = self.lvl_get_xp(user.level)
                max_xp = self.max_xp_for(user.level)
                user_infos.append({
                    'member': member,
                    'rank': user.rank,
                    'lvl': self.get_lvl(user.level),
                    'xp': current_xp,
                    'max_xp': max_xp,
                    'xp_percentage': current_xp / max_xp,
                    'xp_multiplier': await self.get_member_xp_multiplier(member),
                    'name': name,
                    'color': member.color.to_rgb(),
                    'avatar_url': str(member.display_avatar.with_format('png')),
                })
        return user_infos

    async def check_level_user(self, member: discord.Member):
        if self.bot.db.get_level_user(member.guild.id, member.id) is None:
            self.bot.db.update_level_user(member.guild.id, member.id, {
                'level': self.bot.module_manager.settings.get(member.guild.id, 'NEW_USER_LEVEL'),
                'blacklisted': False,
            })

    async def get_member_xp_multiplier(self, member: discord.Member):
        boosts = self.bot.db.get_level_user_xp_boosts(member.guild.id, member.id, time.time())
        return self.bot.module_manager.settings.get(member.guild.id, 'BASE_XP_MULTIPLIER') \
            + sum(map(lambda x: x.amount, boosts))

    async def member_role_manage(self, member, lvl):
        data = self.bot.db.get_levelsystem(member.guild.id)
        lvl = self.get_lvl(lvl)
        lvlsys_list = sorted(map(lambda x: (x.level, x.role_id), data), key=lambda x: x[0])
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

        await tools.give_role(member.guild, member, role_to_give)

        for role in roles_to_remove:
            if role != role_to_give:
                await tools.remove_role(member.guild, member, role)

    async def member_set_lvl(self, member: discord.Member, new_level, old_level=None):
        self.bot.db.update_level_user(member.guild.id, member.id, {
            'level': new_level,
        })

        previous_role = member.top_role
        await self.member_role_manage(member, new_level)
        await self.check_send_rank_level_image(member, new_level, old_level, previous_role)

    async def give_xp(self, member: discord.Member, level_user, base_xp, origin):
        full_xp = base_xp * await self.get_member_xp_multiplier(member)
        old_level = level_user.level
        level_user.level += self.lvl_xp_add(full_xp, level_user.level)
        self.bot.db.add_xp_origin(member.guild.id, member.id, base_xp, origin)
        self.bot.db.add_xp_origin(member.guild.id, member.id, full_xp - base_xp,
                                  '{}:{}'.format(self.boost_origin_prefix, origin))
        await self.member_set_lvl(member, level_user.level, old_level)

    async def on_message_xp(self, message: discord.Message, member: discord.Member):
        if not await self.leveling_allowed(member):
            return
        await self.check_level_user(member)
        level_user = self.bot.db.get_level_user(member.guild.id, member.id)
        if level_user.blacklisted:
            return
        base_xp = self.bot.module_manager.settings.get(member.guild.id, 'MESSAGE_XP')
        await self.give_xp(member, level_user, base_xp, self.message_origin)

    async def voice_xp(self, member, current_time, new_joined=None):
        if not await self.leveling_allowed(member):
            return
        await self.check_level_user(member)
        level_user = self.bot.db.get_level_user(member.guild.id, member.id)

        if level_user.blacklisted:
            return

        if level_user.last_joined is None:
            self.bot.db.update_level_user(member.guild.id, member.id, {'last_joined': new_joined})
            return

        base_xp = (current_time - level_user.last_joined) \
            * self.bot.module_manager.settings.get(member.guild.id, 'VOICE_XP_PER_MINUTE') / 60
        await self.give_xp(member, level_user, base_xp, self.voice_origin)
        self.bot.db.update_level_user(member.guild.id, member.id, {'last_joined': new_joined})

    async def member_joined_vc(self, member, current_time):
        await self.check_level_user(member)
        self.bot.db.update_level_user(member.guild.id, member.id, {'last_joined': current_time})

    async def member_left_vc(self, member, current_time):
        await self.check_level_user(member)
        await self.voice_xp(member, current_time, None)

    async def on_message(self, message: discord.Message, guild: discord.Guild):
        await self.on_message_xp(message, message.author)

    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):
        if not await self.leveling_allowed(member):
            return
        t = time.time()

        if before.channel is not None:
            # when leaving
            if member.guild.afk_channel is None or before.channel.id != member.guild.afk_channel.id:
                await self.member_left_vc(member, t)
            self.bot.logger.info('{} left {}'.format(member, before.channel))

        if after.channel is not None:
            # when joining
            if member.guild.afk_channel is None or after.channel.id != member.guild.afk_channel.id:
                await self.member_joined_vc(member, t)
            self.bot.logger.info('{} joined {}'.format(member, after.channel))

    async def interval_update(self, current_time, guild: discord.Guild):
        for member in guild.members:

            last_joined = current_time
            if member.voice is None or member.voice.channel is None:
                last_joined = None

            if self.bot.db.get_level_user(member.guild.id, member.id) is None and last_joined is None:
                return

            await self.voice_xp(member, current_time, last_joined)

    async def create_extended_profile(self, member: discord.Member):
        await self.check_level_user(member)
        user = self.bot.db.get_level_user(member.guild.id, member.id)
        xp_origins = self.bot.db.get_xp_origin(member.guild.id, member.id)
        text_msg_xp = 0
        voice_xp = 0
        boost_xp = 0
        for origin in xp_origins:
            if origin[0].origin == self.message_origin:
                text_msg_xp += origin[1]
            elif origin[0].origin == self.voice_origin:
                voice_xp += origin[1]
            elif origin[0].origin.startswith(self.boost_origin_prefix):
                boost_xp += origin[1]

        return {
            'level': self.get_lvl(user.level),
            'total_xp': text_msg_xp + voice_xp + boost_xp,
            'blacklisted': user.blacklisted,
            'text_msg_xp': text_msg_xp,
            'voice_xp': voice_xp,
            'boost_xp': boost_xp,
        }
