from helpers.spark_module import SparkModule

import discord
import discord.commands
import discord.ext.commands


class MessagingModule(SparkModule):
    name = 'messaging'
    title = 'Messaging'
    description = 'Module to send messages (I guess)'

    def __init__(self, bot):
        super().__init__(bot)

        @bot.has_permissions(administrator=True)
        async def send(ctx: discord.commands.context.ApplicationContext,
                       channel: discord.commands.Option(
                           discord.TextChannel,
                           description=bot.i18n.get('MESSAGING_SEND_CHANNEL_OPTION'),
                       ),
                       message: discord.commands.Option(
                           str,
                           description=bot.i18n.get('MESSAGING_SEND_MESSAGE_OPTION'),
                       )):
            await channel.send(message)
            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('MESSAGING_SEND_SUCCESSFUL'),
                                    color=discord.Color.green()))

        self.commands = [
            discord.SlashCommand(
                func=send,
                name=self.bot.i18n.get('MESSAGING_SEND_COMMAND'),
                description=self.bot.i18n.get('MESSAGING_SEND_COMMAND_DESCRIPTION'),
            )
        ]
