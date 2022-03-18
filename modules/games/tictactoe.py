import discord
import discord.commands

from typing import *


if TYPE_CHECKING:
    from bot import DiscordBot


# Defines a custom button that contains the logic of the game.
# The ['TicTacToe'] bit is for type hinting purposes to tell your IDE or linter
# what the type of `self.view` is. It is not required.
class TicTacToeButton(discord.ui.Button["TicTacToeView"]):
    def __init__(self, bot: 'DiscordBot', x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y
        self.bot = bot

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToeView = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            if interaction.user in view.O_players:
                return await interaction.response.send_message(
                    embed=discord.Embed(title=self.bot.i18n.get('GAMES_NOT_YOUR_TURN'), color=discord.Color.red()),
                    ephemeral=True)
            if interaction.user not in view.X_players:
                view.X_players.append(interaction.user)
            self.style = discord.ButtonStyle.danger
            self.label = view.X_label
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = self.bot.i18n.get('GAMES_TIC_TAC_TOE_TURN').format(view.O_label)
        else:
            if interaction.user in view.X_players:
                return await interaction.response.send_message(
                    embed=discord.Embed(title=self.bot.i18n.get('GAMES_NOT_YOUR_TURN'), color=discord.Color.red()),
                    ephemeral=True)
            if interaction.user not in view.O_players:
                view.O_players.append(interaction.user)
            self.style = discord.ButtonStyle.success
            self.label = view.O_label
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = self.bot.i18n.get('GAMES_TIC_TAC_TOE_TURN').format(view.X_label)

        self.disabled = True
        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = self.bot.i18n.get('GAMES_TIC_TAC_TOE_WON').format(
                    view.X_label, ', '.join(map(lambda x: x.display_name, view.X_players)))
            elif winner == view.O:
                content = self.bot.i18n.get('GAMES_TIC_TAC_TOE_WON').format(
                    view.O_label, ', '.join(map(lambda x: x.display_name, view.X_players)))
            else:
                content = self.bot.i18n.get('GAMES_TIC_TAC_TOE_TIE').format(
                    ', '.join(map(lambda x: x.display_name, view.O_players + view.X_players)))

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


# This is our actual board View
class TicTacToeView(discord.ui.View):
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, bot: 'DiscordBot'):
        super().__init__()
        self.current_player = self.X
        self.X_players = []
        self.O_players = []
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        self.X_label = bot.i18n.get('GAMES_TIC_TAC_TOE_X_LABEL')
        self.O_label = bot.i18n.get('GAMES_TIC_TAC_TOE_O_LABEL')

        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(bot, x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == -3:
                return self.X

            elif value == 3:
                return self.O
        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == -3:
            return self.X

        elif diag == 3:
            return self.O
        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


class TicTacToeViewHolder:
    def __init__(self, bot: 'DiscordBot', ctx: discord.commands.context.ApplicationContext):
        self.ctx = ctx
        self.bot = bot

    async def start(self):
        await self.ctx.respond(self.bot.i18n.get('GAMES_TIC_TAC_TOE_START'), view=TicTacToeView(self.bot))
