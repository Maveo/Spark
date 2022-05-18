from helpers.spark_module import SparkModule

import discord
import discord.commands
import discord.ext.commands

from helpers.tools import autocomplete_match


class MessageReactionsModule(SparkModule):
    name = 'message_reactions'
    title = 'Message Reactions'
    description = 'Module for reacting to message'

    def __init__(self, bot):
        super().__init__(bot)

        @bot.has_permissions(administrator=True)
        async def get_reactions(ctx: discord.ApplicationContext):
            reactions = self.bot.db.get_message_reactions(ctx.guild.id)
            embed = discord.Embed(title=self.bot.i18n.get('MESSAGE_REACTIONS_TITLE'), color=discord.Color.green())

            for reaction in reactions:
                embed.add_field(name=reaction.trigger, value=reaction.reaction, inline=False)

            return await ctx.respond(embed=embed)

        @bot.has_permissions(administrator=True)
        async def set_reaction(ctx: discord.ApplicationContext,
                               trigger: discord.commands.Option(
                                   str,
                                   description=bot.i18n.get('MESSAGE_REACTIONS_TRIGGER_OPTION_DESCRIPTION'),
                               ),
                               reaction: discord.commands.Option(
                                   str,
                                   description=bot.i18n.get('MESSAGE_REACTIONS_REACTION_OPTION_DESCRIPTION'),
                               )):
            self.bot.db.set_message_reaction(ctx.guild.id, trigger, reaction)
            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('MESSAGE_REACTIONS_ADD_SUCCESSFUL')
                                    .format(trigger, reaction),
                                    color=discord.Color.green()))

        @bot.has_permissions(administrator=True)
        async def reaction_trigger_autocomplete(ctx: discord.AutocompleteContext):
            return autocomplete_match(
                ctx.value, list(map(lambda x: x.trigger, self.bot.db.get_message_reactions(ctx.interaction.guild.id))))

        @bot.has_permissions(administrator=True)
        async def remove_reaction(ctx: discord.ApplicationContext,
                                  trigger: discord.commands.Option(
                                      str,
                                      description=bot.i18n.get('MESSAGE_REACTIONS_TRIGGER_OPTION_DESCRIPTION'),
                                      autocomplete=reaction_trigger_autocomplete
                                  )):
            self.bot.db.remove_message_reaction(ctx.guild.id, trigger)
            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('MESSAGE_REACTIONS_REMOVE_SUCCESSFUL'),
                                    color=discord.Color.green()))

        message_reactions = discord.SlashCommandGroup(
            name=self.bot.i18n.get('MESSAGE_REACTIONS_COMMAND'),
            description=self.bot.i18n.get('MESSAGE_REACTIONS_COMMAND_DESCRIPTION'),
        )
        # message_reactions.subcommands.append(discord.SlashCommand(
        #     func=get_reactions,
        #     name=self.bot.i18n.get('MESSAGE_REACTIONS_GET_COMMAND'),
        #     description=self.bot.i18n.get('MESSAGE_REACTIONS_GET_COMMAND_DESCRIPTION'),
        #     parent=message_reactions
        # ))
        message_reactions.subcommands.append(discord.SlashCommand(
            func=set_reaction,
            name=self.bot.i18n.get('MESSAGE_REACTIONS_SET_COMMAND'),
            description=self.bot.i18n.get('MESSAGE_REACTIONS_SET_COMMAND_DESCRIPTION'),
            parent=message_reactions
        ))
        message_reactions.subcommands.append(discord.SlashCommand(
            func=remove_reaction,
            name=self.bot.i18n.get('MESSAGE_REACTIONS_REMOVE_COMMAND'),
            description=self.bot.i18n.get('MESSAGE_REACTIONS_REMOVE_COMMAND_DESCRIPTION'),
            parent=message_reactions
        ))

        self.commands = [
            message_reactions
        ]

    async def on_message(self, message: discord.Message, guild: discord.Guild):
        reaction = self.bot.db.get_message_reaction(guild.id, message.content)
        if reaction is None:
            return
        await message.channel.send(reaction.reaction)
