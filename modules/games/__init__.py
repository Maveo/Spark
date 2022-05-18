import discord
import discord.commands
import discord.ext.commands

from helpers.spark_module import SparkModule
from .tictactoe import TicTacToeViewHolder
from .chess import ChessViewHolder


class GamesModule(SparkModule):
    name = 'games'
    title = 'Games'
    description = 'Module for Gamers'

    def __init__(self, bot):
        super().__init__(bot)

        async def tic_tac_toe(ctx: discord.ApplicationContext):
            await TicTacToeViewHolder(bot, ctx).start()

        async def chess(ctx: discord.ApplicationContext):
            await ChessViewHolder(self.bot, ctx).start()

        self.commands = [
            # discord.SlashCommand(
            #     func=tic_tac_toe,
            #     name=self.bot.i18n.get('GAMES_TIC_TAC_TOE_COMMAND'),
            #     description=self.bot.i18n.get('GAMES_TIC_TAC_TOE_COMMAND_DESCRIPTION')
            # ),
            # discord.SlashCommand(
            #     func=chess,
            #     name=self.bot.i18n.get('GAMES_CHESS_COMMAND'),
            #     description=self.bot.i18n.get('GAMES_CHESS_COMMAND_DESCRIPTION')
            # ),
        ]
