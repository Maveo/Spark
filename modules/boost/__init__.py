import time

from helpers.exceptions import BoostingYourselfForbiddenException, BoostNotExpiredException
from helpers.spark_module import SparkModule
import discord
import discord.commands
import discord.ext.commands
from discord.utils import get
from .settings import SETTINGS
from .web import API_PAGES


class BoostModule(SparkModule):
    name = 'boost'
    title = 'Boost'
    description = 'Module for boosting'
    settings = SETTINGS
    api_pages = API_PAGES
    dependencies = ['levelsystem']

    boosted_by_prefix = 'boostedby'

    async def get_boosting_user(self, member, current_time):
        boosting_user = self.bot.db.get_level_users_xp_boosts_by_origin(member.guild.id,
                                                                        '{}:{}'.format(self.boosted_by_prefix,
                                                                                       member.id),
                                                                        current_time)
        if len(boosting_user) == 0:
            return None
        if len(boosting_user) > 1:
            self.bot.logger.warning('found boosting multiple users: {}'.format(boosting_user))

        return boosting_user[0]

    async def get_boosted_by_users(self, member: discord.Member, current_time):
        boosted_by_users = self.bot.db.get_level_user_xp_boosts_by_origin_prefix(member.guild.id,
                                                                                 member.id,
                                                                                 '{}:'.format(self.boosted_by_prefix),
                                                                                 current_time)
        return boosted_by_users

    async def boost_get_infos(self, member: discord.Member):
        current_time = time.time()

        boosting = await self.get_boosting_user(member, current_time)

        data = {
            'boosting': boosting,
            'boosting_name': None,
            'boosting_remaining_days': None,
            'boosting_remaining_hours': None
        }

        id_names = {}

        def _get_member(uid):
            uid = int(uid)
            if uid in id_names:
                return id_names[uid]
            m = get(member.guild.members, id=uid)
            name = self.bot.i18n.get('LEFT_USER_NAME')
            top_role = self.bot.i18n.get('LEFT_USER_ROLE')
            if m is not None:
                name = m.display_name
                top_role = str(m.top_role.name)
            id_names[uid] = name, top_role
            return name, top_role

        def _get_days_hours(expires):
            br = (expires - current_time) / (24 * 60 * 60)
            brd = int(br)
            brh = int((br - brd) * 24)
            return brd, brh

        if boosting is not None:
            member_name, member_role = _get_member(boosting.user_id)

            data['boosting_name'] = member_role[0] + member_name

            boost_remaining_days, boost_remaining_hours = _get_days_hours(boosting.expires)

            data['boosting_remaining_days'] = boost_remaining_days
            data['boosting_remaining_hours'] = boost_remaining_hours

        def _boost_to_str(boost):
            brd, brh = _get_days_hours(boost.expires)
            return self.bot.i18n.get('BOOSTED_BY').format(
                _get_member(boost.origin[len(self.boosted_by_prefix) + 1:])[0], brd, brh
            )

        def _boost_to_data(boost):
            brd, brh = _get_days_hours(boost.expires)
            name, role = _get_member(boost.origin[len(self.boosted_by_prefix) + 1:])
            return {'name': role[0] + name, 'remaining_days': brd, 'remaining_hours': brh}

        boosted_by = await self.get_boosted_by_users(member, current_time)

        data['boosts'] = list(map(_boost_to_str, boosted_by))
        data['boosts_raw_data'] = list(map(_boost_to_data, boosted_by))

        data['boosting'] = data['boosting'] is not None

        return data

    async def boost_get_embed(self, member: discord.Member):
        data = await self.boost_get_infos(member)

        embed = discord.Embed(title=self.bot.i18n.get('BOOST_TITLE'),
                              description=self.bot.i18n.get('BOOSTING_NO_ONE'),
                              color=discord.Color.gold())

        if data['boosting']:
            embed = discord.Embed(title=self.bot.i18n.get('BOOST_TITLE'),
                                  description=self.bot.i18n.get('BOOSTING_USER')
                                  .format(data['boosting_name'],
                                          data['boosting_remaining_days'],
                                          data['boosting_remaining_hours']),
                                  color=discord.Color.gold())

        if len(data['boosts']) > 0:
            embed.add_field(name=self.bot.i18n.get('YOUR_BOOSTS')
                            .format(self.bot.module_manager.settings.get(member.guild.id, 'BOOST_ADD_XP_MULTIPLIER')),
                            value='\n'.join(data['boosts']),
                            inline=False)

        return embed

    async def boost_user(self, member: discord.Member, member_to_boost: discord.Member):
        if member.id == member_to_boost.id:
            raise BoostingYourselfForbiddenException()

        current_time = time.time()
        previous_boost = await self.get_boosting_user(member, current_time)
        if previous_boost is not None:
            raise BoostNotExpiredException()
        self.bot.db.add_xp_boost(
            member_to_boost.guild.id,
            member_to_boost.id,
            self.bot.module_manager.settings.get(member.guild.id, 'BOOST_ADD_XP_MULTIPLIER'),
            '{}:{}'.format(self.boosted_by_prefix, member.id),
            current_time + (self.bot.module_manager.settings.get(member.guild.id, 'BOOST_EXPIRES_DAYS') * 24 * 60 * 60)
        )

    def __init__(self, bot):
        super().__init__(bot)

        async def boost(ctx: discord.ApplicationContext,
                        member: discord.commands.Option(
                            discord.Member,
                            description=bot.i18n.get('BOOST_MEMBER_OPTION'),
                            default=None
                        )):
            if member is None:
                embed = await self.boost_get_embed(ctx.author)
                return await ctx.respond(embed=embed)

            if not await self.get_dependency('levelsystem').leveling_allowed(member):
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('BOT_NOT_ALLOWED_LEVELING'),
                                                             color=discord.Color.red()))

            try:
                await self.boost_user(ctx.author, member)
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('BOOSTING_NOW')
                                                             .format(member.display_name),
                                                             color=discord.Color.green()))
            except BoostingYourselfForbiddenException:
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('BOOSTING_SELF_FORBIDDEN'),
                                                             color=discord.Color.red()))
            except BoostNotExpiredException:
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('BOOST_NOT_EXPIRED'),
                                                             color=discord.Color.red()))

        self.commands = [
            discord.SlashCommand(
                func=boost,
                name=self.bot.i18n.get('BOOST_COMMAND'),
                description=self.bot.i18n.get('BOOST_DESCRIPTION')
            )
        ]

    async def create_extended_profile(self, member: discord.Member):
        data = await self.boost_get_infos(member)
        data['boost_xp_multiplier'] = self.bot.module_manager.settings.get(member.guild.id, 'BOOST_ADD_XP_MULTIPLIER')
        return data
