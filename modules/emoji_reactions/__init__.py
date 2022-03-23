import json
import math
from typing import *

import discord
import discord.commands
import discord.ext.commands
from discord.utils import get

from helpers import tools
from helpers.exceptions import UnknownException
from helpers.spark_module import SparkModule
from helpers.view_helpers import ViewPaginator, CustomButton
from .settings import SETTINGS


class CustomDropdown(discord.ui.Select):
    def __init__(self,
                 callback: Callable[['CustomDropdown', discord.Interaction], Coroutine],
                 placeholder: str,
                 options: List[discord.SelectOption]):
        self.custom_callback = callback

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await self.custom_callback(self, interaction)


class CustomModal(discord.ui.Modal):
    def __init__(self,
                 callback: Callable[['CustomModal', discord.Interaction], Coroutine],
                 title: str):
        self.custom_callback = callback
        super().__init__(title)

    async def callback(self, interaction: discord.Interaction):
        await self.custom_callback(self, interaction)


class EmojiReactionsModule(SparkModule):
    name = 'emoji_reactions'
    title = 'Emoji Reactions'
    description = 'Module for emoji reactions'
    settings = SETTINGS

    ADD_ROLE = 'add-role'
    TRIGGER_ROLE = 'trigger-role'
    SEND_DM = 'send-dm'
    CUSTOM_EMOJI = 'custom-emoji'

    def __init__(self, bot):
        super().__init__(bot)

        self.reaction_types = {
            self.ADD_ROLE: 'EMOJI_REACTIONS_ADD_ROLE',
            self.TRIGGER_ROLE: 'EMOJI_REACTIONS_TRIGGER_ROLE',
            self.SEND_DM: 'EMOJI_REACTIONS_SEND_DM',
        }

        self.activating_reactions = {}

        @bot.has_permissions(administrator=True)
        async def add_emoji_action(ctx: discord.commands.context.ApplicationContext,
                                   message: discord.Message):
            async def custom_emoji_response(button: CustomButton, interaction1: discord.Interaction):
                m = await ctx.send(embed=discord.Embed(
                    description=self.bot.i18n.get('EMOJI_REACTIONS_CUSTOM_EMOJI_MESSAGE'),
                    color=discord.Color.blue()))

                await ctx.edit(embed=discord.Embed(title=self.bot.i18n.get('EMOJI_REACTIONS_REACT_TO'),
                                                   description=m.jump_url), view=None)

                self.activating_reactions[(m.channel.id, m.id)] = (ctx.author.id, ctx, message)

            async def response(dropdown1: CustomDropdown, interaction1: discord.Interaction):
                emoji = get(ctx.guild.emojis, id=int(dropdown1.values[0]))
                if not emoji:
                    raise UnknownException('Emoji not found')
                await self.add_emoji_reaction_action(ctx.guild, ctx, message, emoji)

            options = [
                          discord.SelectOption(label=str(emoji.name),
                                               emoji=str(emoji),
                                               value=str(emoji.id)) for emoji in ctx.guild.emojis
                      ]

            pages = []
            for i in range(math.ceil(len(options) / 25)):
                view = discord.ui.View()
                view.add_item(
                    CustomButton(custom_emoji_response,
                                 label=bot.i18n.get('EMOJI_REACTIONS_CUSTOM_EMOJI_LABEL'),
                                 emoji=bot.i18n.get('EMOJI_REACTIONS_CUSTOM_EMOJI')))
                view.add_item(
                    CustomDropdown(response,
                                   bot.i18n.get('EMOJI_REACTIONS_CHOOSE_EMOJI_PLACEHOLDER'),
                                   options[i*25:(i+1)*25]))
                pages.append(view)

            paginator = ViewPaginator(pages, hide_empty=True)

            await ctx.respond(view=paginator.view(), ephemeral=True)

        @bot.has_permissions(administrator=True)
        async def get_emoji_reactions(ctx: discord.commands.context.ApplicationContext):
            reactions = self.bot.db.get_emoji_reactions(ctx.guild.id)
            embed = discord.Embed(title=self.bot.i18n.get('EMOJI_REACTIONS_TITLE'), color=discord.Color.green())

            for reaction in reactions:
                val = 'Not Found'
                if reaction.action_type == self.ADD_ROLE or reaction.action_type == self.TRIGGER_ROLE:
                    r = ctx.guild.get_role(int(reaction.action))
                    if r is not None:
                        val = r.name
                elif reaction.action_type == self.SEND_DM:
                    val = json.dumps(reaction.action if len(reaction.action) < 40 else reaction.action[:37] + '...')

                embed.add_field(name=self.bot.i18n.get('EMOJI_REACTIONS_IDENTIFIER').format(
                    reaction.id,
                    reaction.emoji,
                    self.bot.i18n.get(self.reaction_types[reaction.action_type]),
                    val),
                    value='https://discord.com/channels/{}/{}/{}'.format(
                        reaction.guild_id, reaction.channel_id, reaction.message_id),
                    inline=False)

            return await ctx.respond(embed=embed)

        @bot.has_permissions(administrator=True)
        async def remove_emoji_reaction_autocomplete(ctx: discord.AutocompleteContext):
            reactions = []
            for reaction in self.bot.db.get_emoji_reactions(ctx.interaction.guild.id):
                val = 'Not Found'
                if reaction.action_type == self.ADD_ROLE or reaction.action_type == self.TRIGGER_ROLE:
                    r = ctx.interaction.guild.get_role(int(reaction.action))
                    if r is not None:
                        val = r.name
                elif reaction.action_type == self.SEND_DM:
                    val = json.dumps(reaction.action if len(reaction.action) < 20 else reaction.action[:20] + '...')

                reactions.append('ID: {} | {} | {} | {}'.format(
                    reaction.id,
                    discord.PartialEmoji.from_str(reaction.emoji).name,
                    self.bot.i18n.get(self.reaction_types[reaction.action_type]),
                    val))

            return tools.autocomplete_match(ctx.value, reactions)

        @bot.has_permissions(administrator=True)
        async def remove_emoji_reaction(ctx: discord.commands.context.ApplicationContext,
                                        reaction: discord.commands.Option(
                                            str,
                                            description=bot.i18n.get('REMOVE_REACTION_OPTION'),
                                            autocomplete=remove_emoji_reaction_autocomplete,
                                        )):
            try:
                reaction_id = int(reaction[4:].split(' ')[0])
            except:
                raise UnknownException('Reaction ID not found')
            self.bot.db.remove_emoji_reaction(ctx.author.guild.id, reaction_id)
            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('EMOJI_REACTIONS_REMOVE_SUCCESSFUL')
                                    .format(reaction),
                                    color=discord.Color.green()))

        emoji_reactions = discord.SlashCommandGroup(
            name=self.bot.i18n.get('EMOJI_REACTIONS_COMMAND'),
            description=self.bot.i18n.get('EMOJI_REACTIONS_COMMAND_DESCRIPTION'),
        )

        emoji_reactions.subcommands.append(discord.SlashCommand(
            func=get_emoji_reactions,
            name=self.bot.i18n.get('EMOJI_REACTIONS_GET_COMMAND'),
            description=self.bot.i18n.get('EMOJI_REACTIONS_GET_COMMAND_DESCRIPTION'),
            parent=emoji_reactions
        ))
        emoji_reactions.subcommands.append(discord.SlashCommand(
            func=remove_emoji_reaction,
            name=self.bot.i18n.get('EMOJI_REACTIONS_REMOVE_COMMAND'),
            description=self.bot.i18n.get('EMOJI_REACTIONS_REMOVE_COMMAND_DESCRIPTION'),
            parent=emoji_reactions
        ))

        self.commands = [
            discord.MessageCommand(
                func=add_emoji_action,
                name=self.bot.i18n.get('EMOJI_REACTIONS_ADD_COMMAND'),
            ),
            emoji_reactions
        ]

    async def add_emoji_reaction_action(self,
                                        guild: discord.Guild,
                                        ctx: discord.commands.ApplicationContext,
                                        message_to_react: discord.Message,
                                        emoji: discord.PartialEmoji or discord.Emoji):

        async def response(dropdown: CustomDropdown, interaction: discord.Interaction):
            await ctx.edit(embed=discord.Embed(title=self.bot.i18n.get('LOADING')), view=None)
            v = dropdown.values[0]
            if v == self.SEND_DM:
                async def response2(modal2: CustomModal, interaction2: discord.Interaction):
                    await ctx.edit(embed=discord.Embed(title=self.bot.i18n.get('EMOJI_REACTIONS_SETTING_ACTION').format(
                        self.bot.i18n.get(self.reaction_types[self.SEND_DM])
                    )))

                    self.bot.db.set_emoji_reaction(message_to_react.guild.id,
                                                   message_to_react.channel.id,
                                                   message_to_react.id,
                                                   str(emoji),
                                                   v,
                                                   modal2.children[0].value
                                                   )

                    await message_to_react.add_reaction(str(emoji))
                    await interaction2.response.send_message(
                        embed=discord.Embed(
                            title=self.bot.i18n.get('EMOJI_REACTIONS_SETTING_ACTION_SUCCESS').format(
                                self.bot.i18n.get(self.reaction_types[v])
                            ),
                            color=discord.Color.green()
                        ),
                        ephemeral=True)

                modal = CustomModal(response2, self.bot.i18n.get('EMOJI_REACTIONS_SEND_DM_MODAL_TITLE'))
                modal.add_item(discord.ui.InputText(label=self.bot.i18n.get('EMOJI_REACTIONS_SEND_DM_MODAL_FIELD'),
                                                    style=discord.InputTextStyle.long))
                await interaction.response.send_modal(modal)
                await ctx.edit(embed=discord.Embed(
                    title=self.bot.i18n.get('EMOJI_REACTIONS_SEND_DM_MODAL_INFO_MESSAGE')))

            elif v == self.ADD_ROLE or v == self.TRIGGER_ROLE:
                async def response2(dropdown2: CustomDropdown, interaction2: discord.Interaction):
                    await ctx.edit(embed=discord.Embed(title=self.bot.i18n.get('LOADING')), view=None)
                    self.bot.db.set_emoji_reaction(message_to_react.guild.id,
                                                   message_to_react.channel.id,
                                                   message_to_react.id,
                                                   str(emoji),
                                                   v,
                                                   dropdown2.values[0]
                                                   )

                    await message_to_react.add_reaction(str(emoji))
                    await ctx.edit(embed=discord.Embed(
                        title=self.bot.i18n.get('EMOJI_REACTIONS_SETTING_ACTION_SUCCESS').format(
                            self.bot.i18n.get(self.reaction_types[v])
                        ),
                        color=discord.Color.green()),
                        view=None)

                options = []

                for role in guild.roles:
                    role_emoji = tools.only_emojis(role.name[0])
                    role_name = role.name[1:]
                    if not role_emoji:
                        role_emoji = None
                        role_name = role.name
                    options.append(discord.SelectOption(label=role_name, emoji=role_emoji, value=str(role.id)))

                pages = []
                for i in range(math.ceil(len(options) / 25)):
                    view = discord.ui.View()

                    view.add_item(
                        CustomDropdown(response2,
                                       self.bot.i18n.get('EMOJI_REACTIONS_CHOOSE_ROLE_PLACEHOLDER'),
                                       options[i * 25:(i + 1) * 25]))
                    pages.append(view)

                paginator = ViewPaginator(pages, hide_empty=True)

                await ctx.edit(embed=discord.Embed(title=self.bot.i18n.get('EMOJI_REACTIONS_CHOOSE_ROLE_TITLE')
                                                   .format(str(emoji), self.bot.i18n.get(self.reaction_types[v]))),
                               view=paginator.view())

            else:
                raise UnknownException('emoji action not found')

        options = []

        for reaction_type, i18n_key in self.reaction_types.items():
            e = self.bot.i18n.get(i18n_key + '_EMOJI')
            if e == '':
                e = None
            options.append(discord.SelectOption(label=self.bot.i18n.get(i18n_key),
                                                emoji=e,
                                                value=reaction_type))

        view = discord.ui.View()
        view.add_item(CustomDropdown(response, self.bot.i18n.get('EMOJI_REACTIONS_ACTION_TYPE_PLACEHOLDER'), options))
        await ctx.edit(
            embed=discord.Embed(title=self.bot.i18n.get('EMOJI_REACTIONS_ACTION_TYPE_TITLE').format(str(emoji))),
            view=view)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member.id == self.bot.bot.user.id:
            return
        try:
            r = self.activating_reactions[(payload.channel_id, payload.message_id)]
            if r[0] == payload.member.id:
                c = await payload.member.guild.fetch_channel(payload.channel_id)
                m = await c.fetch_message(payload.message_id)
                await m.delete()
                await self.add_emoji_reaction_action(payload.member.guild,
                                                     r[1],
                                                     r[2],
                                                     payload.emoji)
                self.activating_reactions.pop((payload.channel_id, payload.message_id))
        except KeyError:
            pass

        if not self.bot.module_manager.settings.get(payload.member.guild.id, 'ALLOW_BOT_EMOJI_REACTIONS') \
                and payload.member.bot:
            return

        actions = self.bot.db.get_emoji_reactions_by_payload(payload.member.guild.id,
                                                             payload.channel_id,
                                                             payload.message_id,
                                                             str(payload.emoji))
        for action in actions:
            try:
                if action.action_type == self.ADD_ROLE or action.action_type == self.TRIGGER_ROLE:
                    await tools.give_role(payload.member.guild, payload.member, int(action.action))
                elif action.action_type == self.SEND_DM:
                    await payload.member.send(action.action)
            except Exception as e:
                self.bot.logger.error(e)
                pass

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.bot.get_guild(payload.guild_id)
        member = get(guild.members, id=payload.user_id)
        if member is None or member.guild is None:
            return
        if not self.bot.module_manager.settings.get(member.guild.id, 'ALLOW_BOT_EMOJI_REACTIONS') \
                and member.bot:
            return
        actions = self.bot.db.get_emoji_reactions_by_payload(member.guild.id,
                                                             payload.channel_id,
                                                             payload.message_id,
                                                             str(payload.emoji))
        for action in actions:
            try:
                if action.action_type == self.TRIGGER_ROLE:
                    await tools.remove_role(member.guild, member, int(action.action))
            except Exception as e:
                self.bot.logger.warning('{} for user {} in {}'.format(e, member, member.guild))
