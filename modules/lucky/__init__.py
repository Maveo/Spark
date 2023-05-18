import asyncio
import os
import random

from helpers.spark_module import SparkModule
from .settings import SETTINGS

import discord
import discord.commands
import discord.ext.commands


class LuckyModule(SparkModule):
    name = 'lucky'
    title = 'Lucky'
    description = 'Module for when you are feeling lucky'
    settings = SETTINGS

    def __init__(self, bot):
        super().__init__(bot)

        async def coinflip(ctx: discord.ApplicationContext):
            res = random.choice(['heads', 'tails'])
            message = await ctx.respond(file=discord.File(
                os.path.join(self.bot.current_dir, 'images', '{}.gif'.format(res))))

            if random.random() < self.bot.module_manager.settings.get(ctx.author.guild.id, 'COIN_FLIP_AUDIO_CHANCE'):
                if ctx.author.voice is not None and ctx.author.voice.channel is not None:
                    await self.bot.play_audio(
                        discord.FFmpegPCMAudio(os.path.join(self.bot.current_dir, 'audio', 'tossacoin.mp3')),
                        ctx.author.voice.channel
                    )

            await asyncio.sleep(13)

            await ctx.edit(file=discord.File(os.path.join(self.bot.current_dir, 'images', '{}.png'.format(res))))

        async def dice(ctx: discord.ApplicationContext):
            await ctx.respond(file=discord.File(
                os.path.join(self.bot.current_dir, 'images', '{}.gif'.format(random.randint(1, 6)))))

        async def random_command(ctx: discord.ApplicationContext,
                                 args: discord.Option(str,
                                                      description=bot.i18n.get('RANDOM_ARGS_OPTION')
                                                      )):
            random_string = self.bot.i18n.get('RANDOM_COMMAND_RESULT')

            if len(args) == 1:
                if args[0].isnumeric():
                    return await ctx.send(random_string.format(random.randint(1, int(args[0]))))

            if len(args) == 2:
                if args[0].isnumeric() and args[1].isnumeric():
                    opts = [int(args[0]), int(args[1])]
                    return await ctx.send(random_string.format(random.randint(min(opts), max(opts))))

            await ctx.send(random_string.format(random.choice(args)))

        self.commands = [
            discord.SlashCommand(
                func=coinflip,
                name=self.bot.i18n.get('COINFLIP_COMMAND'),
                description=self.bot.i18n.get('COINFLIP_COMMAND_DESCRIPTION'),
            ),
            discord.SlashCommand(
                func=dice,
                name=self.bot.i18n.get('DICE_COMMAND'),
                description=self.bot.i18n.get('DICE_COMMAND_DESCRIPTION'),
            ),
            discord.SlashCommand(
                func=random_command,
                name=self.bot.i18n.get('RANDOM_COMMAND'),
                description=self.bot.i18n.get('RANDOM_COMMAND_DESCRIPTION'),
            )
        ]
