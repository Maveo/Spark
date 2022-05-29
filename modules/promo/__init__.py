import asyncio
import secrets
import time

from discord.utils import get

from helpers.exceptions import LevelingBlacklistedUserException, PromotingYourselfForbiddenException, \
    PromoCodeNotFoundException, UnknownException
from helpers.spark_module import SparkModule
from .settings import SETTINGS
from .web import API_PAGES

import discord
import discord.commands
import discord.ext.commands


class PromoModule(SparkModule):
    name = 'promo'
    title = 'Promo'
    description = 'Module for promoting users'
    settings = SETTINGS
    api_pages = API_PAGES
    dependencies = ['levelsystem']

    promo_by_prefix = 'promoby'

    def get_promo_codes(self, guild_id):
        if guild_id not in self.guild_promo_codes:
            return {}
        return self.guild_promo_codes[guild_id]

    def add_guild_promo_code(self, guild_id, key, value):
        if guild_id not in self.guild_promo_codes:
            self.guild_promo_codes[guild_id] = {key: value}
            return
        self.guild_promo_codes[guild_id][key] = value

    def clean_promo_codes(self, current_time):
        for promo_codes in self.guild_promo_codes.values():
            for promo_code in promo_codes:
                if promo_codes[promo_code]['expires'] < current_time:
                    promo_codes.pop(promo_code)

    async def can_redeem_promo_code(self, member: discord.Member):
        channel_id = self.bot.module_manager.settings.get(member.guild.id, 'PROMO_CHANNEL_ID')
        if channel_id == '':
            return False
        try:
            channel = get(member.guild.channels, id=int(channel_id))
        except ValueError:
            return False
        if channel is None:
            return False
        return channel.permissions_for(member).send_messages

    async def create_promo_code(self, member: discord.Member):
        length = max(6, min(32, self.bot.module_manager.settings.get(member.guild.id, 'PROMO_CODE_LENGTH')))
        for i in range(5):
            promo_code = secrets.token_urlsafe(length)
            if promo_code not in self.get_promo_codes(member.guild.id):

                expires = int(time.time() + (self.bot.module_manager.settings.get(
                    member.guild.id, 'PROMO_CODE_EXPIRES_HOURS') * 60 * 60))

                self.add_guild_promo_code(member.guild.id, promo_code, {
                    'expires': expires, 'created_by_member_id': member.id})
                return promo_code

        self.bot.logger.warning('promo code (length {}) full 5 times in {}'.format(length, member.guild))
        return None

    async def redeem_promo_code(self, member: discord.Member, code: str, current_time):
        self.clean_promo_codes(current_time)

        level_user = self.bot.db.get_level_user(member.guild.id, member.id)
        if level_user.blacklisted:
            raise LevelingBlacklistedUserException()

        codes = self.get_promo_codes(member.guild.id)
        if code not in codes:
            raise PromoCodeNotFoundException()

        promo = codes[code]

        if member.id == promo['created_by_member_id']:
            raise PromotingYourselfForbiddenException()

        self.bot.db.add_xp_boost(
            member.guild.id,
            promo['created_by_member_id'],
            self.bot.module_manager.settings.get(member.guild.id, 'PROMO_BOOST_ADD_XP_MULTIPLIER'),
            '{}:{}'.format(self.promo_by_prefix, member.id),
            int(current_time + (self.bot.module_manager.settings.get(
                member.guild.id, 'PROMO_BOOST_EXPIRES_DAYS')) * 24 * 60 * 60),
        )

        await self.get_dependency('levelsystem').member_set_lvl(
            member, self.bot.module_manager.settings.get(member.guild.id, 'PROMO_USER_SET_LEVEL'))

    async def get_boosted_by_users(self, member: discord.Member, current_time):
        boosted_by_users = self.bot.db.get_level_user_xp_boosts_by_origin_prefix(member.guild.id,
                                                                                 member.id,
                                                                                 '{}:'.format(self.promo_by_prefix),
                                                                                 current_time)
        return boosted_by_users

    async def boost_get_infos(self, member: discord.Member):
        current_time = time.time()
        promo_boosted_by = await self.get_boosted_by_users(member, current_time)

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

        def _boost_to_str(boost):
            brd, brh = _get_days_hours(boost.expires)
            return self.bot.i18n.get('BOOSTED_BY').format(
                _get_member(boost.origin[len(self.promo_by_prefix) + 1:])[0], brd, brh
            )

        def _boost_to_data(boost):
            brd, brh = _get_days_hours(boost.expires)
            name, role = _get_member(boost.origin[len(self.promo_by_prefix) + 1:])
            return {'name': role[0] + name, 'remaining_days': brd, 'remaining_hours': brh}

        return {
            'promo_boosts': list(map(_boost_to_str, promo_boosted_by)),
            'promo_boosts_raw_data': list(map(_boost_to_data, promo_boosted_by))
        }

    def __init__(self, bot):
        super().__init__(bot)

        self.guild_promo_codes = {}

        async def promo(ctx: discord.ApplicationContext, *args):
            promo_code = await self.create_promo_code(ctx.author)
            if promo_code is None:
                raise UnknownException('Promo code not found')

            try:
                await ctx.author.send(
                    embed=discord.Embed(title='',
                                        description=self.bot.i18n.get('PROMO_CODE_PRIVATE_MESSAGE')
                                        .format(ctx.author.guild.name,
                                                self.bot.module_manager.settings.get(
                                                    ctx.author.guild.id, 'PROMO_CODE_EXPIRES_HOURS'
                                                ),
                                                promo_code),
                                        color=discord.Color.blue()),
                )
                await ctx.respond(
                    embed=discord.Embed(title='',
                                        description=self.bot.i18n.get('PROMO_CODE_CREATE_SUCCESSFUL'),
                                        color=discord.Color.green()),
                    ephemeral=True,
                )
            except discord.Forbidden:
                await ctx.respond(
                    embed=discord.Embed(title='',
                                        description=self.bot.i18n.get('DIRECT_MESSAGE_FORBIDDEN'),
                                        color=discord.Color.red()),
                    ephemeral=True,
                )

        self.commands = [
            discord.SlashCommand(
                func=promo,
                name=self.bot.i18n.get('PROMO_COMMAND'),
                description=self.bot.i18n.get('PROMO_COMMAND_DESCRIPTION'),
            )
        ]

    async def check_promo_code_message(self, message: discord.Message):
        if not await self.get_dependency('levelsystem').leveling_allowed(message.author):
            return

        try:
            await self.redeem_promo_code(message.author, message.content, time.time())
            await message.channel.send(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('PROMO_CODE_USE_SUCCESSFUL'),
                                    color=discord.Color.green()))

        except PromoCodeNotFoundException:
            return await message.channel.send(embed=discord.Embed(title='',
                                                                  description=self.bot.i18n.get('PROMO_CODE_INVALID'),
                                                                  color=discord.Color.red()))

        except LevelingBlacklistedUserException:
            return await message.channel.send(embed=discord.Embed(title='',
                                                                  description=self.bot.i18n.get('YOU_ARE_BLACKLISTED'),
                                                                  color=discord.Color.red()))
        except PromotingYourselfForbiddenException:
            return await message.channel.send(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('PROMOTING_YOURSELF_FORBIDDEN'),
                                    color=discord.Color.red()))

    async def on_message(self, message: discord.Message, guild: discord.Guild):
        if self.bot.module_manager.settings.get(message.guild.id, 'PROMO_CHANNEL_ID') != str(message.channel.id):
            return

        await self.check_promo_code_message(message)

        timeout = self.bot.module_manager.settings.get(message.guild.id, 'PROMO_CHANNEL_DELETE_MESSAGES_SECONDS')
        if timeout >= 0:
            await asyncio.sleep(timeout)
            await message.delete()

    async def create_extended_profile(self, member: discord.Member):
        data = await self.boost_get_infos(member)
        data['promo_boost_xp_multiplier'] = self.bot.module_manager.settings.get(member.guild.id,
                                                                                 'PROMO_BOOST_ADD_XP_MULTIPLIER')
        data['promo_code_expires_hours'] = self.bot.module_manager.settings.get(member.guild.id,
                                                                                'PROMO_CODE_EXPIRES_HOURS')
        data['can_redeem_promo_code'] = await self.can_redeem_promo_code(member)
        data['promo_user_set_level'] = self.bot.module_manager.settings.get(member.guild.id, 'PROMO_USER_SET_LEVEL')
        return data
