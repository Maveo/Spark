import sys

import discord

from helpers import tools
import json
import os
import importlib.util

from helpers.exceptions import WrongInputException, ModuleNotActivatedException
from helpers.settings_manager import Setting
from helpers.spark_module import SparkModule


import itertools
from typing import *

from helpers.tools import underscore_to_camelcase
from webserver import Page

if TYPE_CHECKING:
    from bot import DiscordBot


class ModuleManager:
    def __init__(self, bot: 'DiscordBot'):
        self.bot = bot
        self.optional_modules: List[str] = []
        self.modules: Dict[str, SparkModule] = {}
        self.settings = ModuleSettingsManager(self)
        self.api_pages = ModuleApiPagesManager(self)

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
            raise WrongInputException('module "{}" not found!'.format(module_key))

        missing_dependencies = self.bot.module_manager.missing_dependencies(guild_id, module_key)
        if activate_dependencies:
            for missing_dependency in missing_dependencies:
                await self.activate_module(guild_id, missing_dependency, False, False, True)
        elif missing_dependencies:
            raise WrongInputException('module "{}" misses dependencies: {}'.format(
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

    async def deactivate_module(self, guild_id, module_key, sync_as_task=False):
        if not self.bot.module_manager.is_optional(module_key):
            raise WrongInputException('module "{}" not found!'.format(module_key))

        dependency_for = self.bot.module_manager.is_dependency_for(guild_id, module_key)
        if dependency_for:
            raise WrongInputException('module "{}" is dependency for: {} (disable them first)'.format(
                module_key,
                ', '.join(dependency_for)
            ))

        self.bot.logger.info('guild {} deactivates module {}'.format(guild_id, module_key))
        self.bot.db.deactivate_module(guild_id, module_key)
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


class ModuleSettingsManager:
    def __init__(self, module_manager: ModuleManager):
        self.module_manager = module_manager
        self.default_settings: Dict[str, Setting] = {}

    def initialize(self, modules: List[SparkModule]):
        settings_keys: Dict[str, str] = {}
        for module in modules:
            if not isinstance(module.get_settings(), dict):
                raise RuntimeError('settings of module {} not dict'.format(module.get_name()))
            for key, value in module.get_settings().items():
                if not isinstance(value, Setting):
                    raise RuntimeError('setting {} of module {} is not of type Setting'.format(key, module.get_name()))
                if key in settings_keys:
                    raise RuntimeError('duplicate settings key ({}) in modules {} and {}'.format(
                        key, module.get_name(), settings_keys[key]
                    ))
                else:
                    settings_keys[key] = module.get_name()
                    self.default_settings[key] = value

    def keys(self, guild_id=None):
        if guild_id is None:
            return self.default_settings.keys()
        return list(itertools.chain(*map(lambda module: self.module_manager.modules[module].settings.keys(),
                                         self.module_manager.get_activated_modules(guild_id))))

    def all(self, guild_id):
        return {k: self.get(guild_id, k) for k in self.keys(guild_id)}

    def get_default(self, key):
        if key not in self.keys():
            raise KeyError('Key "{}" not found in default settings!'.format(key))
        return self.default_settings[key].value

    def get(self, guild_id, key):
        keys = self.keys(guild_id)
        if key not in keys:
            raise KeyError('Key "{}" not found in guild settings!'.format(key))

        guild_setting = self.module_manager.bot.db.get_setting(guild_id, key)
        if guild_setting is not None:
            try:
                default_type = type(self.default_settings[key].value)
                return tools.simple_eval(default_type, json.loads(guild_setting))
            except Exception as e:
                self.module_manager.bot.logger.warning(e)

        return self.default_settings[key].value

    def preview(self, guild_id, key, value):
        if key not in self.keys(guild_id):
            raise KeyError('Key "{}" not found in default settings!'.format(key))

        value = json.dumps(value)
        default_type = type(self.default_settings[key].value)
        return tools.simple_eval(default_type, json.loads(value))

    def set(self, guild_id, key, value):
        if key not in self.keys(guild_id):
            raise KeyError('Key "{}" not found in default settings!'.format(key))

        value = json.dumps(value)
        try:
            self.preview(guild_id, key, value)
        except Exception as e:
            self.module_manager.bot.logger.warning(e)
            return False

        self.module_manager.bot.db.set_setting(guild_id, key, value)
        return True

    def remove(self, guild_id, key):
        if key not in self.keys(guild_id):
            raise KeyError('Key "{}" not found in default settings!'.format(key))
        self.module_manager.bot.db.remove_setting(guild_id, key)

    def categories(self, guild_id):
        return list(dict.fromkeys(
            [cat for key in self.keys(guild_id) for cat in self.default_settings[key].categories]
        ))

    def all_as_dict(self, guild_id):
        return {
            key: self.default_settings[key].new_value_dict(self.get(guild_id, key)) for key in self.keys(guild_id)
        }


class ModuleApiPagesManager:
    def __init__(self, module_manager: ModuleManager):
        self.module_manager = module_manager
        self.default_api_pages: Dict[str, Page] = {}

    def initialize(self, modules: List[SparkModule]):
        pages_keys: Dict[str, str] = {}
        for module in modules:
            if not isinstance(module.get_api_pages(), list):
                raise RuntimeError('api pages of module {} not list'.format(module.get_name()))
            for api_page in module.get_api_pages():
                if not isinstance(api_page, Page):
                    raise RuntimeError('api page {} of module {} is not of type Page'.format(api_page.path,
                                                                                             module.get_name()))
                if api_page.path in pages_keys:
                    raise RuntimeError('duplicate pages path ({}) in modules {} and {}'.format(
                        api_page.path, module.get_name(), pages_keys[api_page.path]
                    ))
                else:
                    pages_keys[api_page.path] = module.get_name()
                    self.default_api_pages[api_page.path] = api_page.new(
                        view_func=self.module_wrapper(api_page.view_func, module)
                    )

    def module_wrapper(self, func, module):
        async def _call(guild: discord.Guild, member: discord.Member, *args, **kwargs):
            activated_modules = self.module_manager.get_activated_modules(guild.id)
            if module.get_name() not in activated_modules:
                raise ModuleNotActivatedException('module "{}" not activated'.format(module.get_name()))
            return await func(self.module_manager.get(module.get_name()), guild, member, *args, **kwargs)

        return _call

    def all(self):
        return self.default_api_pages.values()
