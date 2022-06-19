import sys

import discord

import os
import importlib.util

from helpers.exceptions import WrongInputException
from helpers.module_api_pages_manager import ModuleApiPagesManager
from helpers.module_hook_manager import ModuleHookManager
from helpers.module_settings_manager import ModuleSettingsManager
from helpers.spark_module import SparkModule


from typing import *

from helpers.tools import underscore_to_camelcase

if TYPE_CHECKING:
    from bot import DiscordBot


class ModuleManager:
    def __init__(self, bot: 'DiscordBot'):
        self.bot = bot
        self.optional_modules: List[str] = []
        self.modules: Dict[str, SparkModule] = {}
        self.settings = ModuleSettingsManager(self)
        self.api_pages = ModuleApiPagesManager(self)
        self.hooks = ModuleHookManager(self)

    def initialize(self):
        module_path = os.path.join(self.bot.current_dir, 'modules')
        modules = []
        for module in os.listdir(module_path):
            if not module.startswith('_')\
                    and os.path.isdir(os.path.join(module_path, module))\
                    and os.path.isfile(os.path.join(module_path, module, '__init__.py')):
                try:
                    class_name = '{}Module'.format(underscore_to_camelcase(module))
                    spec = importlib.util.spec_from_file_location(module, os.path.join(module_path, module, '__init__.py'))
                    imodule = importlib.util.module_from_spec(spec)
                    sys.modules[module] = imodule
                    spec.loader.exec_module(imodule)
                    modules.append(getattr(imodule, class_name))
                except AttributeError and ModuleNotFoundError as e:
                    self.bot.logger.error(e)
        self.settings.initialize(modules)
        self.api_pages.initialize(modules)

        self.optional_modules = [module.get_name() for module in modules if module.optional]
        self.modules = {
            module.get_name(): module(self.bot) for module in modules
        }
        for module in self.modules.values():
            for dep in module.dependencies:
                if dep not in self.modules.keys():
                    raise ValueError('dependency {} of {} is not found'.format(dep, module.get_name()))
                if self.modules[dep].dependency_for is None:
                    self.modules[dep].dependency_for = [module.get_name()]
                else:
                    self.modules[dep].dependency_for.append(module.get_name())

    async def fix_dependencies(self, guild_id):
        activated_modules = self.get_activated_modules(guild_id)
        for module in activated_modules:
            for missing_dependency in self.missing_dependencies(guild_id, module):
                self.bot.logger.warning('guild {} is missing {}, activating...'.format(guild_id, missing_dependency))
                await self.activate_module(guild_id, missing_dependency, False, False, activate_dependencies=True)

    def get(self, module_key: str):
        return self.modules[module_key]

    def keys(self):
        return self.modules.keys()

    def items(self):
        return self.modules.items()

    def values(self):
        return self.modules.values()

    def is_optional(self, module_key):
        return module_key in self.bot.module_manager.optional_modules

    async def activate_module(self, guild_id, module_key, sync_as_task=False, sync=True, activate_dependencies=False):
        if not self.bot.module_manager.is_optional(module_key):
            raise WrongInputException(detail='module "{}" not found!'.format(module_key))

        missing_dependencies = self.bot.module_manager.missing_dependencies(guild_id, module_key)
        if activate_dependencies:
            for missing_dependency in missing_dependencies:
                await self.activate_module(guild_id, missing_dependency, False, False, True)
        elif missing_dependencies:
            raise WrongInputException(detail='module "{}" misses dependencies: {}'.format(
                module_key,
                ', '.join(missing_dependencies))
            )

        self.bot.logger.info('guild {} activates module {}'.format(guild_id, module_key))
        self.bot.db.activate_module(guild_id, module_key)
        if not sync:
            return
        if sync_as_task:
            self.bot.bot.loop.create_task(self.bot.sync_commands())
        else:
            await self.bot.sync_commands()

    async def deactivate_module(self, guild_id, module_key, sync_as_task=False, sync=True):
        if not self.bot.module_manager.is_optional(module_key):
            raise WrongInputException(detail='module "{}" not found!'.format(module_key))

        dependency_for = self.bot.module_manager.is_dependency_for(guild_id, module_key)
        if dependency_for:
            raise WrongInputException(detail='module "{}" is dependency for: {} (disable them first)'.format(
                module_key,
                ', '.join(dependency_for)
            ))

        self.bot.logger.info('guild {} deactivates module {}'.format(guild_id, module_key))
        self.bot.db.deactivate_module(guild_id, module_key)
        if not sync:
            return
        if sync_as_task:
            self.bot.bot.loop.create_task(self.bot.sync_commands())
        else:
            await self.bot.sync_commands()

    def missing_dependencies(self, guild_id, module_key):
        dependencies = self.modules[module_key].dependencies
        if dependencies:
            active_modules = self.get_activated_modules(guild_id)
            return list(filter(lambda d: d not in active_modules, dependencies))
        return list()

    def is_dependency_for(self, guild_id, module_key):
        dependency_for = self.modules[module_key].dependency_for
        if dependency_for:
            active_modules = self.get_activated_modules(guild_id)
            return list(filter(lambda d: d in active_modules, dependency_for))
        return list()

    def get_activated_modules(self, guild_id):
        return list(filter(lambda x: x not in self.optional_modules, self.modules.keys())) \
               + list(filter(lambda x: x in self.optional_modules, self.bot.db.get_activated_modules(guild_id)))

    def get_deactivatable_modules(self, guild_id):
        return list(filter(lambda x: x in self.optional_modules, self.bot.db.get_activated_modules(guild_id)))

    def get_activatable_modules(self, guild_id):
        return list(filter(lambda x: x not in self.get_deactivatable_modules(guild_id), self.optional_modules))

    async def create_extended_profile(self, member: discord.Member):
        data = {}
        for module in self.get_activated_modules(member.guild.id):
            for key, value in (await self.modules[module].create_extended_profile(member)).items():
                if key in data:
                    self.bot.logger.warning('duplicate extended profile key: {}'.format(key))
                else:
                    data[key] = value
        return data

    async def interval_update(self, current_time, guild):
        for module in self.get_activated_modules(guild.id):
            await self.modules[module].interval_update(current_time, guild)

    async def on_message(self, message: discord.Message):
        if message.guild is not None:
            for module in self.get_activated_modules(message.guild.id):
                await self.modules[module].on_message(message, message.guild)

    async def on_member_join(self, member: discord.Member):
        if member.guild is not None:
            for module in self.get_activated_modules(member.guild.id):
                await self.modules[module].on_member_join(member)

    async def on_member_remove(self, member: discord.Member):
        if member.guild is not None:
            for module in self.get_activated_modules(member.guild.id):
                await self.modules[module].on_member_remove(member)

    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):
        if member.guild is not None:
            for module in self.get_activated_modules(member.guild.id):
                await self.modules[module].on_voice_state_update(member, before, after)

    async def on_application_command_error(self,
                                           ctx: discord.ApplicationContext,
                                           error: discord.ApplicationCommandError):
        if ctx.author.guild is not None:
            for module in self.get_activated_modules(ctx.author.guild.id):
                await self.modules[module].on_application_command_error(ctx, error)

    async def on_autocomplete_error(self,
                                    ctx: discord.AutocompleteContext,
                                    error: discord.DiscordException):
        if ctx.interaction.user.guild is not None:
            for module in self.get_activated_modules(ctx.interaction.user.guild.id):
                r = await self.modules[module].on_autocomplete_error(ctx, error)
                if r:
                    return r

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is not None:
            for module in self.get_activated_modules(payload.guild_id):
                await self.modules[module].on_raw_reaction_add(payload)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is not None:
            for module in self.get_activated_modules(payload.guild_id):
                await self.modules[module].on_raw_reaction_remove(payload)
