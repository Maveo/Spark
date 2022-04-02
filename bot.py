import functools
import os
import asyncio
import subprocess
import sys
import shutil
import time

import logging
from typing import *

from helpers.db import Database
import discord
import discord.commands
import discord.ext.commands
from imagestack_svg.imagecreator import ImageCreator
from imagestack_svg.loaders import FontLoader, EmojiLoader

from helpers.i18n_manager import I18nManager
from helpers.module_manager import ModuleManager


class DiscordBot:
    def is_super_admin(self, user_id):
        return user_id in self.super_admins

    def user_missing_permissions(self, member: discord.Member,
                                 channel=None,
                                 **perms: bool) -> List[str]:
        if self.is_super_admin(member.id):
            return []

        if channel is None:
            channel = member.guild.system_channel
        permissions = channel.permissions_for(member)  # type: ignore

        missing = []
        for perm, value in perms.items():
            try:
                if getattr(permissions, perm) != value:
                    missing.append(perm)
            except AttributeError:
                missing.append(perm)

        return missing

    def has_permissions(self, **perms: bool):
        def wrapper(func):
            @functools.wraps(func)
            async def wrapped(ctx: Union[discord.commands.ApplicationContext,
                                         discord.commands.AutocompleteContext], *args, **kwargs):

                if isinstance(ctx, discord.commands.ApplicationContext):
                    missing = self.user_missing_permissions(ctx.author, ctx.channel, **perms)
                    if missing:
                        raise discord.ext.commands.MissingPermissions(missing)
                elif isinstance(ctx, discord.commands.AutocompleteContext):
                    missing = self.user_missing_permissions(ctx.interaction.user, ctx.interaction.channel, **perms)
                    if missing:
                        return await self.module_manager.on_autocomplete_error(
                            ctx, discord.ext.commands.MissingPermissions(missing))
                else:
                    self.logger.error('Unknown context: {}'.format(type(ctx)))

                return await func(ctx, *args, **kwargs)

            return wrapped

        return wrapper

    def __init__(self,
                 db: Database,
                 i18n: I18nManager = None,
                 current_dir='',
                 interval_time=-1,
                 description='',
                 image_creator: ImageCreator = None,
                 super_admins=None,
                 logging_level=logging.WARNING
                 ):
        self.current_dir = current_dir
        self.db = db

        if i18n is None:
            i18n = I18nManager(data={})
        self.i18n = i18n

        if super_admins is None:
            super_admins = []
        self.super_admins = super_admins

        self.image_creator = image_creator

        self.interval_time = interval_time

        self.logger = logging.getLogger('sparkbot')
        self.logger.setLevel(logging_level)
        # logging.getLogger('discord').setLevel(logging_level)

        intents = discord.Intents(members=True,
                                  guilds=True,
                                  guild_reactions=True,
                                  guild_messages=True,
                                  voice_states=True,
                                  message_content=True,
                                  dm_messages=True,
                                  emojis=True,
                                  )

        self.bot = discord.ext.commands.Bot(
            description=description,
            intents=intents,
            help_command=None,
            auto_sync_commands=False,
        )

        self.module_manager = ModuleManager(self)
        self.module_manager.initialize()

        self.bot.add_listener(self.module_manager.on_message, 'on_message')
        self.bot.add_listener(self.module_manager.on_member_join, 'on_member_join')
        self.bot.add_listener(self.module_manager.on_member_remove, 'on_member_remove')
        self.bot.add_listener(self.module_manager.on_voice_state_update, 'on_voice_state_update')
        self.bot.add_listener(self.module_manager.on_raw_reaction_add, 'on_raw_reaction_add')
        self.bot.add_listener(self.module_manager.on_raw_reaction_remove, 'on_raw_reaction_remove')

        self.bot.add_listener(self._on_ready, 'on_ready')

        @self.bot.event
        async def on_guild_join(guild: discord.Guild):
            try:
                await discord.bot.ApplicationCommandMixin.get_desynced_commands(self.bot, guild.id)

                if not guild.me.guild_permissions.administrator:
                    self.logger.warning('no administrator permission in {}'.format(repr(guild)))
                    await guild.system_channel.send(
                        embed=discord.Embed(title=self.i18n.get('BOT_MISSING_ADMINISTRATOR_PERMISSIONS'),
                                            color=discord.Color.red()))
            except discord.Forbidden:
                self.logger.warning('Slash commands are disabled in {}'.format(guild))
                await guild.system_channel.send(embed=discord.Embed(title=self.i18n.get('BOT_MISSING_COMMANDS_SCOPE'),
                                                                    color=discord.Color.red()))

        @self.bot.event
        async def on_error(event, *args, **kwargs):
            error = sys.exc_info()[1]
            self.logger.error('"{}" in event: {}'.format(error, event))
            # if event == 'on_raw_reaction_add':
            #     if len(args) > 0 and isinstance(args[0], discord.RawReactionActionEvent) \
            #             and args[0].member is not None and args[0].member.guild is not None:
            #         await self.module_manager.on_member_error(args[0].member, error, event, args, kwargs)
            # elif event == 'on_interaction':
            #     if len(args) > 0 and isinstance(args[0], discord.Interaction) \
            #             and args[0].user is not None and args[0].user.guild is not None:
            #         await self.module_manager.on_member_error(args[0].user, error, event, args, kwargs)

        @self.bot.event
        async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.ApplicationCommandError):
            self.logger.info('command error from {}: {}'.format(ctx.author, error))
            await self.module_manager.on_application_command_error(ctx, error)

        @self.bot.event
        async def on_interaction(interaction: discord.Interaction):
            if interaction.type not in (
                    discord.InteractionType.application_command,
                    discord.InteractionType.auto_complete,
            ):
                return

            command = None
            try:
                command = self.bot._application_commands[interaction.data["id"]]
            except KeyError:
                try:
                    guild_id = int(interaction.data.get("guild_id"))
                    for cmd in self.bot._pending_application_commands:
                        if cmd.name == interaction.data["name"] and (
                                guild_id == cmd.guild_ids or
                                (isinstance(cmd.guild_ids, list) and guild_id in cmd.guild_ids)
                        ):
                            command = cmd
                except ValueError:
                    pass

            if command is None:
                return self.bot.dispatch("unknown_application_command", interaction)

            if interaction.type is discord.InteractionType.auto_complete:
                ctx = await self.bot.get_autocomplete_context(interaction)
                ctx.command = command
                return await command.invoke_autocomplete_callback(ctx)

            ctx = await self.bot.get_application_context(interaction)
            ctx.command = command
            self.bot.dispatch("application_command", ctx)
            try:
                if await self.bot.can_run(ctx, call_once=True):
                    await ctx.command.invoke(ctx)
                else:
                    raise discord.CheckFailure("The global check once functions failed.")
            except discord.DiscordException as exc:
                await ctx.command.dispatch_error(ctx, exc)
            else:
                self.bot.dispatch("application_command_completion", ctx)

    async def play_audio(self, audio_source, voice_channel):
        async def _play_audio():
            voice_client = None
            try:
                voice_client = await voice_channel.connect()
                voice_client.play(audio_source)

                while voice_client.is_playing():
                    await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(e)
            if voice_client is not None and not voice_client.is_playing():
                await voice_client.disconnect()

        self.bot.loop.create_task(_play_audio())

    async def _interval_update(self):
        current_time = time.time()
        for guild in self.bot.guilds:
            await self.module_manager.interval_update(current_time, guild)

    async def _interval_loop(self):
        if self.interval_time > 0:
            while True:
                await asyncio.sleep(self.interval_time)
                await self._interval_update()

    async def sync_commands(self):
        self.logger.info('syncing commands...')
        self.bot._application_commands.clear()
        self.bot._pending_application_commands.clear()

        modules_to_guilds = {x: [] for x in self.module_manager.keys()}
        for guild in self.bot.guilds:
            try:
                await discord.bot.ApplicationCommandMixin.get_desynced_commands(self.bot, guild.id)

                if not guild.me.guild_permissions.administrator:
                    self.logger.warning('no administrator permission in {}'.format(repr(guild)))
                else:
                    for module in self.module_manager.get_activated_modules(guild.id):
                        modules_to_guilds[module].append(guild.id)
            except discord.Forbidden:
                self.logger.warning('Slash commands are disabled in {}'.format(guild))

        for module_name, module in self.module_manager.items():
            for command in module.commands:
                command.guild_ids = modules_to_guilds[module_name]
                self.bot.add_application_command(command)
        try:
            await self.bot.sync_commands()
            self.logger.info('synced bot command modules {}'.format(modules_to_guilds))
        except discord.HTTPException:
            self.logger.error('syncing commands {} failed'.format(modules_to_guilds))
            await self.sync_commands()

    async def _on_ready(self):
        self.logger.info('Bot is running...')

        for guild in self.bot.guilds:
            await self.module_manager.fix_dependencies(guild.id)

        self.bot.loop.create_task(self._interval_loop())
        await self.sync_commands()

    def run(self, token):
        self.bot.run(token)


def main():
    from settings import GLOBAL_SETTINGS
    from helpers.settings_manager import GlobalSettingsValidator
    from webserver import WebServer

    logging.basicConfig()

    current_dir = os.path.dirname(os.path.realpath(__file__))

    global_settings = GlobalSettingsValidator.validate(GLOBAL_SETTINGS)

    b = DiscordBot(
        db=Database(GLOBAL_SETTINGS['DATABASE_URL']),
        i18n=I18nManager(path=os.path.join(current_dir, 'i18n.json')),
        current_dir=current_dir,
        interval_time=global_settings['INTERVAL_TIME'],
        description=global_settings['DESCRIPTION'],
        super_admins=global_settings['SUPER_ADMINS'],
        image_creator=ImageCreator(font_loader=FontLoader(
                                       global_settings['FONTS']),
                                   emoji_loader=EmojiLoader(
                                       emoji_path=global_settings['EMOJIS_PATH'],
                                       download_emojis=global_settings['DOWNLOAD_EMOJIS'],
                                       save_downloaded_emojis=global_settings['SAVE_EMOJIS']
                                   )),
        logging_level=global_settings['LOGGING_LEVEL']
    )

    if global_settings['ACTIVATE_WEBSERVER']:
        webserver_static_path = os.path.join(current_dir, global_settings['WEBSERVER_STATIC_PATH'])
        if not os.path.exists(webserver_static_path):
            os.mkdir(webserver_static_path)

        build_frontend = False
        skip_check = False
        install = False

        if '--install' in sys.argv[1:]:
            install = True

        if '--skip-check' in sys.argv[1:]:
            skip_check = True

        if not build_frontend and '--build' in sys.argv[1:]:
            build_frontend = True

        if not skip_check and not build_frontend and len(os.listdir(webserver_static_path)) == 0:
            i = input('webserver path ({}) is empty. Do you want to build the frontend into that folder? [y/N] '
                      .format(webserver_static_path))
            if i.upper() == 'Y':
                build_frontend = True

        if build_frontend:
            if install:
                print('installing node packages...')
                code = subprocess.Popen('npm i',
                                        cwd=os.path.join(current_dir, 'frontend'),
                                        shell=True).wait()
                if code != 0:
                    print('An error occurred while installing!')
                    quit(code)

            print('building frontend...')

            code = subprocess.Popen('npm run build',
                                    cwd=os.path.join(current_dir, 'frontend'),
                                    shell=True).wait()
            if code != 0:
                print('An error occurred while building!')
                quit(code)

            if os.path.join(current_dir, 'frontend', 'dist') != webserver_static_path:
                shutil.rmtree(webserver_static_path)
                shutil.copytree(os.path.join(current_dir, 'frontend', 'dist'), webserver_static_path)

        web = WebServer(
            oauth2_client_id=global_settings['APPLICATION_ID'],
            oauth2_client_secret=global_settings['APPLICATION_SECRET'],
            oauth2_redirect_uri=global_settings['OAUTH2_REDIRECT_URI'],
            webserver_secret=global_settings['WEBSERVER_SECRET'],
            discord_bot=b,
            static_path=webserver_static_path,
            port=global_settings['WEBSERVER_PORT'],
            debug=global_settings['WEBSERVER_DEBUG'],
            logging_level=global_settings['WEBSERVER_LOGGING_LEVEL']
        )
        web.start()

    b.run(global_settings['TOKEN'])


if __name__ == '__main__':
    main()
