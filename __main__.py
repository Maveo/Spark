from settings import *

import discord
from discord.ext import commands


class Commands(commands.Cog):
    def __init__(self, dbot):
        self.bot = dbot

    @commands.command(name='members', aliases=['players', 'users'], description="streams music")
    async def play_(self, ctx):
        await ctx.trigger_typing()

        for member in ctx.message.guild.members:
            if member.id != bot.user.id:
                embed = discord.Embed(title="", description=member.name,
                                      color=discord.Color.green())
                await ctx.send(embed=embed)


def setup(dbot):
    dbot.add_cog(Commands(dbot))


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, intents=intents)


@bot.event
async def on_ready():
    print('Bot is ready')


setup(bot)
bot.run(TOKEN)
