import random

from helpers.exceptions import WrongInputException, UnknownException
from helpers.spark_module import SparkModule
from .settings import SETTINGS
from .web import API_PAGES

import discord
import discord.commands
import discord.ext.commands
from helpers.tools import autocomplete_match


class GeneralModule(SparkModule):
    name = 'general'
    title = 'General'
    description = 'The General of all modules'
    optional = False
    settings = SETTINGS
    api_pages = API_PAGES

    def __init__(self, bot):
        super().__init__(bot)

        def settings_embed(settings_items, max_length=80):
            embed = discord.Embed(title=self.bot.i18n.get('SETTINGS_TITLE'),
                                  description='',
                                  color=discord.Color.gold())
            for key, value in settings_items.items():
                res = '"{}"'.format(value)
                embed.add_field(name='{}'.format(key),
                                value=(res[:max_length] + '...') if len(res) > max_length else res,
                                inline=False)
            return embed

        @bot.has_permissions(administrator=True)
        async def setting_key_autocomplete_get(ctx: discord.AutocompleteContext):
            return autocomplete_match(ctx.value,
                                      ['_'] + self.bot.module_manager.settings.keys(ctx.interaction.guild.id))

        @bot.has_permissions(administrator=True)
        async def setting_key_autocomplete(ctx: discord.AutocompleteContext):
            return autocomplete_match(ctx.value, self.bot.module_manager.settings.keys(ctx.interaction.guild.id))

        @bot.has_permissions(administrator=True)
        async def set_setting(ctx: discord.ApplicationContext,
                              key: discord.Option(
                                  str,
                                  description=bot.i18n.get('SET_SETTING_KEY_OPTION'),
                                  autocomplete=setting_key_autocomplete,
                              ),
                              value: discord.Option(
                                  str,
                                  description=bot.i18n.get('SET_SETTING_VALUE_OPTION'),
                              )):
            try:
                if not self.bot.module_manager.settings.set(ctx.guild.id, key, value):
                    raise UnknownException(detail='Setting not found')
                return await ctx.respond(embed=settings_embed({
                    key: self.bot.module_manager.settings.get(ctx.guild.id, key)
                }, max_length=1020))
            except KeyError:
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('SETTING_NOT_FOUND')
                                                             .format(key),
                                                             color=discord.Color.red()))

        @bot.has_permissions(administrator=True)
        async def get_setting(ctx: discord.ApplicationContext,
                              key: discord.Option(
                                  str,
                                  description=bot.i18n.get('GET_SETTING_KEY_OPTION'),
                                  autocomplete=setting_key_autocomplete_get,
                              )):
            if key == '_':
                return await ctx.respond(
                    embed=settings_embed(self.bot.module_manager.settings.all(ctx.guild.id))
                )
            try:
                return await ctx.respond(embed=settings_embed({
                    key: self.bot.module_manager.settings.get(ctx.guild.id, key)
                }, max_length=1020))
            except KeyError:
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('SETTING_NOT_FOUND')
                                                             .format(key),
                                                             color=discord.Color.red()))

        @bot.has_permissions(administrator=True)
        async def reset_setting(ctx: discord.ApplicationContext,
                                key: discord.Option(
                                    str,
                                    description=bot.i18n.get('RESET_SETTING_KEY_OPTION'),
                                    autocomplete=setting_key_autocomplete,
                                )):
            try:
                self.bot.module_manager.settings.remove(ctx.guild.id, key)
                return await ctx.respond(
                    embed=discord.Embed(title='',
                                        description=self.bot.i18n.get('SETTING_RESET_SUCCESSFUL')
                                        .format(key),
                                        color=discord.Color.green()))
            except KeyError:
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('SETTING_NOT_FOUND')
                                                             .format(key),
                                                             color=discord.Color.red()))

        settings_command = discord.SlashCommandGroup(
            name=self.bot.i18n.get('SETTINGS_COMMAND'),
            description=self.bot.i18n.get('SETTINGS_DESCRIPTION'),
        )
        settings_command.subcommands.append(discord.SlashCommand(
            func=set_setting,
            name=self.bot.i18n.get('SETTINGS_SET_COMMAND'),
            description=self.bot.i18n.get('SET_SETTING_DESCRIPTION'),
            parent=settings_command
        ))
        settings_command.subcommands.append(discord.SlashCommand(
            func=get_setting,
            name=self.bot.i18n.get('SETTINGS_GET_COMMAND'),
            description=self.bot.i18n.get('GET_SETTING_DESCRIPTION'),
            parent=settings_command
        ))
        settings_command.subcommands.append(discord.SlashCommand(
            func=reset_setting,
            name=self.bot.i18n.get('SETTINGS_RESET_COMMAND'),
            description=self.bot.i18n.get('RESET_SETTING_DESCRIPTION'),
            parent=settings_command
        ))

        @bot.has_permissions(administrator=True)
        async def activate_module_autocomplete(ctx: discord.AutocompleteContext):
            return autocomplete_match(ctx.value,
                                      self.bot.module_manager.get_activatable_modules(ctx.interaction.guild.id))

        @bot.has_permissions(administrator=True)
        async def activate_module(ctx: discord.ApplicationContext,
                                  module: discord.Option(
                                      type=str,
                                      description=bot.i18n.get('MODULE_ACTIVATE_OPTION'),
                                      autocomplete=activate_module_autocomplete,
                                  )):
            await ctx.defer(ephemeral=True)

            try:
                await self.bot.module_manager.activate_module(ctx.guild.id, module)
            except WrongInputException as e:
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=e.detail,
                                                             color=discord.Color.red()))

            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('MODULE_ACTIVATED_SUCCESSFUL')
                                    .format(module),
                                    color=discord.Color.green()))

        @bot.has_permissions(administrator=True)
        async def deactivate_module_autocomplete(ctx: discord.AutocompleteContext):
            return autocomplete_match(ctx.value,
                                      self.bot.module_manager.get_deactivatable_modules(ctx.interaction.guild.id))

        @bot.has_permissions(administrator=True)
        async def deactivate_module(ctx: discord.ApplicationContext,
                                    module: discord.Option(
                                        str,
                                        description=bot.i18n.get('MODULE_DEACTIVATE_OPTION'),
                                        autocomplete=deactivate_module_autocomplete,
                                    )):
            await ctx.defer(ephemeral=True)

            try:
                await self.bot.module_manager.deactivate_module(ctx.guild.id, module)
            except WrongInputException as e:
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=e.detail,
                                                             color=discord.Color.red()))

            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('MODULE_DEACTIVATED_SUCCESSFUL')
                                    .format(module),
                                    color=discord.Color.green()))

        @bot.has_permissions(administrator=True)
        async def get_active_modules(ctx: discord.ApplicationContext):
            return await ctx.respond(
                embed=discord.Embed(title=self.bot.i18n.get('ACTIVE_MODULES_TITLE'),
                                    description='\n'.join(
                                        self.bot.module_manager.get_deactivatable_modules(ctx.guild.id)
                                    ),
                                    color=discord.Color.green()))

        modules = discord.SlashCommandGroup(
            name=self.bot.i18n.get('MODULES_COMMAND'),
            description=self.bot.i18n.get('MODULES_DESCRIPTION'),
        )
        modules.subcommands.append(discord.SlashCommand(
            func=deactivate_module,
            name=self.bot.i18n.get('MODULE_DEACTIVATE_COMMAND'),
            description=self.bot.i18n.get('MODULE_DEACTIVATE_DESCRIPTION'),
            parent=modules
        ))
        modules.subcommands.append(discord.SlashCommand(
            func=activate_module,
            name=self.bot.i18n.get('MODULE_ACTIVATE_COMMAND'),
            description=self.bot.i18n.get('MODULE_ACTIVATE_DESCRIPTION'),
            parent=modules
        ))
        modules.subcommands.append(discord.SlashCommand(
            func=get_active_modules,
            name=self.bot.i18n.get('MODULES_GET_ACTIVE_COMMAND'),
            description=self.bot.i18n.get('MODULES_GET_ACTIVE_DESCRIPTION'),
            parent=modules
        ))

        self.commands = [
            settings_command,
            modules
        ]

    async def member_create_welcome_image_by_template(self, member, template):
        name = member.display_name
        guild_icon_url = None
        if member.guild.icon:
            guild_icon_url = str(member.guild.icon.with_format('png'))
        data_obj = {
            'member': member,
            'name': name,
            'avatar_url': str(member.display_avatar.with_format('png')),
            'guild_icon_url': guild_icon_url
        }
        img_buf = await self.bot.image_creator.create_bytes(template(**data_obj))
        return discord.File(filename="welcome.png", fp=img_buf)

    async def member_create_welcome_image(self, member):
        return await self.member_create_welcome_image_by_template(
            member, self.bot.module_manager.settings.get(member.guild.id, 'WELCOME_IMAGE'))

    async def create_extended_profile(self, member: discord.Member):
        def _format_date(date):
            if date is None:
                return self.bot.i18n.get('EMPTY_DATE')
            return date.strftime(self.bot.i18n.get('DATE_FORMAT'))

        if member.public_flags.hypesquad_bravery:
            hype_squad = self.bot.i18n.get('BRAVE_HYPE')
        elif member.public_flags.hypesquad_brilliance:
            hype_squad = self.bot.i18n.get('BRILLIANT_HYPE')
        elif member.public_flags.hypesquad_balance:
            hype_squad = self.bot.i18n.get('BALANCED_HYPE')
        else:
            hype_squad = self.bot.i18n.get('NO_HYPE')

        return {
            'member': member,
            'is_admin': self.bot.is_super_admin(member.id) or member.guild_permissions.administrator,
            'is_super_admin': self.bot.is_super_admin(member.id),
            'created_account': _format_date(member.created_at),
            'joined_at': _format_date(member.joined_at),
            'boosting_since': _format_date(member.premium_since),
            'hype_squad': hype_squad,
        }

    def get_missing_permission_response(self, guild_id):
        responses = self.bot.module_manager.settings.get(guild_id, 'MISSING_PERMISSIONS_RESPONSES')
        if len(responses) == 0:
            return self.bot.i18n.get('GENERIC_MISSING_PERMISSION_RESPONSE')
        else:
            return random.choice(responses)

    async def on_member_join(self, member: discord.Member):
        if self.bot.module_manager.settings.get(member.guild.id, 'SEND_WELCOME_IMAGE'):
            await member.send(file=await self.member_create_welcome_image(member))

    async def on_application_command_error(self,
                                           ctx: discord.ApplicationContext,
                                           error: discord.ApplicationCommandError):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            error = error.original

        if isinstance(error, discord.ext.commands.errors.MissingPermissions):
            await ctx.respond(embed=discord.Embed(description=self.get_missing_permission_response(ctx.guild.id),
                                                  color=discord.Color.red()),
                              ephemeral=True)
        elif isinstance(error, UnknownException):
            await ctx.respond(embed=discord.Embed(title='',
                                                  description=self.bot.i18n.get('UNKNOWN_ERROR'),
                                                  color=discord.Color.red()),
                              ephemeral=True)
        elif isinstance(error, discord.Forbidden):
            await ctx.respond(embed=discord.Embed(description=f"Error({error.code}): {error.text}",
                                                  color=discord.Color.red()),
                              ephemeral=True)

    async def on_autocomplete_error(self,
                                    ctx: discord.AutocompleteContext,
                                    error: discord.DiscordException):
        if isinstance(error, discord.ext.commands.errors.MissingPermissions):
            return [self.get_missing_permission_response(ctx.interaction.user.guild.id)]
