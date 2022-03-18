from typing import *

import discord


if TYPE_CHECKING:
    from bot import DiscordBot
    from helpers.settings_manager import Setting
    from webserver import Page


class SparkModule:
    name = None
    title = None
    description = None
    optional = True
    settings: Dict[str, 'Setting'] = {}
    api_pages: List['Page'] = []
    commands: List[discord.ApplicationCommand] = []
    dependencies: List['SparkModule'] = []
    dependency_for: List['SparkModule'] = None

    def __init__(self, bot: 'DiscordBot'):
        self.bot = bot

    def get_dependency(self, module_key: str):
        return self.bot.module_manager.get(module_key)

    async def create_extended_profile(self, member: discord.Member):
        return {}

    async def interval_update(self, current_time, guild: discord.Guild):
        pass

    async def on_message(self, message: discord.Message, guild: discord.Guild):
        pass

    async def on_member_join(self, member: discord.Member):
        pass

    async def on_member_remove(self, member: discord.Member):
        pass

    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):
        pass

    async def on_application_command_error(self,
                                           ctx: discord.ApplicationContext,
                                           error: discord.ApplicationCommandError):
        pass

    async def on_autocomplete_error(self,
                                    ctx: discord.AutocompleteContext,
                                    error: discord.DiscordException):
        pass

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        pass

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        pass

    @classmethod
    def get_name(cls):
        if cls.name is None:
            raise ValueError('module {} has no name'.format(cls.__name__))
        return cls.name

    @classmethod
    def get_settings(cls):
        return cls.settings

    @classmethod
    def get_api_pages(cls):
        return cls.api_pages
