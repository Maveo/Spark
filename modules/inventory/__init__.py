import discord
import discord.commands

from helpers.exceptions import WrongInputException
from helpers.spark_module import SparkModule
from helpers.tools import make_linear_gradient, autocomplete_match
from .settings import SETTINGS
from .web import API_PAGES


class InventoryModule(SparkModule):
    name = 'inventory'
    title = 'Inventory Module'
    description = 'The module for the inventory system'
    api_pages = API_PAGES
    settings = SETTINGS

    def __init__(self, bot):
        super().__init__(bot)

        async def get_inventory(ctx: discord.commands.context.ApplicationContext):
            items = []
            for item in self.bot.db.get_user_items(ctx.author.guild.id, ctx.author.id):
                items.append('Rarity: {} Name: {} Amount: {:g}'.format(
                    item.InventoryRarity.name,
                    item.InventoryItemType.name,
                    item.UserInventoryItem.amount
                ))
            return await ctx.respond(
                embed=discord.Embed(title='Inventory',
                                    description='\n'.join(items),
                                    color=discord.Color.green()))

        @bot.has_permissions(administrator=True)
        async def admin_item_type_autocomplete(ctx: discord.AutocompleteContext):
            return autocomplete_match(
                ctx.value, list(map(lambda x: 'ID: {} Name: {}'.format(x.id, x.name),
                                    self.bot.db.get_item_types(ctx.interaction.guild.id))))

        @bot.has_permissions(administrator=True)
        async def admin_give_item(ctx: discord.commands.context.ApplicationContext,
                                  member: discord.Member,
                                  item_type: discord.commands.Option(
                                      str,
                                      description=bot.i18n.get('INVENTORY_ADMIN_GIVE_ITEM_OPTION_DESCRIPTION'),
                                      autocomplete=admin_item_type_autocomplete
                                  ),
                                  amount: float):
            try:
                item_type_id = int(item_type[4:].split(' ')[0])
            except:
                return await ctx.respond(embed=discord.Embed(title='',
                                                             description=self.bot.i18n.get('UNKNOWN_ERROR'),
                                                             color=discord.Color.red()))
            self.bot.db.add_user_item(member.guild.id, member.id, item_type_id, amount)
            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('INVENTORY_ADMIN_GIVE_COMMAND_SUCCESS')
                                    .format(amount, item_type),
                                    color=discord.Color.green()))

        inventory = discord.SlashCommandGroup(
            name=self.bot.i18n.get('INVENTORY_COMMAND'),
            description=self.bot.i18n.get('INVENTORY_COMMAND_DESCRIPTION'),
        )

        inventory.subcommands.append(discord.SlashCommand(
            func=get_inventory,
            name=self.bot.i18n.get('INVENTORY_GET_COMMAND'),
            description=self.bot.i18n.get('INVENTORY_GET_COMMAND_DESCRIPTION'),
            parent=inventory
        ))

        inventory.subcommands.append(discord.SlashCommand(
            func=admin_give_item,
            name=self.bot.i18n.get('INVENTORY_ADMIN_GIVE_COMMAND'),
            description=self.bot.i18n.get('INVENTORY_ADMIN_GIVE_COMMAND_DESCRIPTION'),
            parent=inventory
        ))

        self.commands = [
            inventory
        ]

    async def create_rarity_image_by_template(self, rarity, template):
        img_buf = await self.bot.image_creator.create(template(rarity))
        return discord.File(filename=f"rarity-{rarity['name']}.png", fp=img_buf)

    async def create_rarity_image(self, guild_id, rarity):
        img_buf = await self.bot.image_creator.create(
            (self.bot.module_manager.settings.get(guild_id, 'RARITY_IMAGE'))(rarity))
        return discord.File(filename=f"rarity-{rarity['name']}.png", fp=img_buf)

    async def add_rarity(self, guild: discord.Guild, name, foreground_color_string, background_color_string):
        if len(name) > 20:
            raise WrongInputException('name can only be 20 characters long')

        try:
            make_linear_gradient(foreground_color_string)
            make_linear_gradient(background_color_string)
        except:
            raise WrongInputException('wrong format for color')
        self.bot.db.add_rarity(guild.id, name, foreground_color_string, background_color_string)

    async def get_rarities(self, guild: discord.Guild):
        return {r.order:  {'id': r.id,
                           'name': r.name,
                           'foreground_color': r.foreground_color,
                           'background_color': r.background_color,
                           }
                for r in self.bot.db.get_rarities(guild.id)}
