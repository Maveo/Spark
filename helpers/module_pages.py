import functools
from typing import TYPE_CHECKING

import discord
import discord.ext.commands

if TYPE_CHECKING:
    from spark_module import SparkModule


def has_permissions(**perms: bool):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(module: 'SparkModule', guild: discord.Guild, member: discord.Member, *args, **kwargs):
            missing = module.bot.user_missing_permissions(member, channel=None, **perms)
            if missing:
                raise discord.ext.commands.MissingPermissions(missing)

            return await func(module, guild, member, *args, **kwargs)

        return wrapped

    return wrapper
