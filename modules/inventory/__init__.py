import json

import discord
import discord.commands

from helpers.exceptions import WrongInputException, UnknownException, ItemNotUsableException, ItemNotFoundException
from helpers.module_hook_manager import INVENTORY_ITEM_ACTION_HOOK, INVENTORY_ADD_ITEM_HOOK, \
    INVENTORY_EQUIPPED_ITEMS_HOOK
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
            return await ctx.respond(file=await self.create_inventory_image(
                ctx.author.guild.id, await self.get_inventory(ctx.author)),
                                     ephemeral=True)

        async def list_inventory(ctx: discord.commands.context.ApplicationContext):
            embed = discord.Embed(title=bot.i18n.get('INVENTORY_TITLE').format(ctx.author.display_name),
                                  description='',
                                  color=discord.Color.gold())
            prev_rarity = None
            items_in_rarity = []
            for item in self.bot.db.get_user_items(ctx.author.guild.id, ctx.author.id):
                if prev_rarity != item.InventoryRarity.name and len(items_in_rarity) > 0:
                    embed.add_field(name=prev_rarity,
                                    value='\n'.join(items_in_rarity),
                                    inline=False)
                    items_in_rarity = []
                items_in_rarity.append(self.bot.i18n.get('INVENTORY_ITEM').format(item.InventoryItemType.name,
                                                                                  item.UserInventoryItem.amount))
                prev_rarity = item.InventoryRarity.name
            if len(items_in_rarity) > 0:
                embed.add_field(name=prev_rarity,
                                value='\n'.join(items_in_rarity),
                                inline=False)

            return await ctx.respond(embed=embed, ephemeral=True)

        async def use_item_autocomplete(ctx: discord.AutocompleteContext):
            return autocomplete_match(ctx.value, list(map(
                lambda item: 'ID: {} Rarity: {} Name: {} Amount: {:g}'.format(
                    item.InventoryItemType.id,
                    item.InventoryRarity.name,
                    item.InventoryItemType.name,
                    item.UserInventoryItem.amount
                ),
                self.bot.db.get_user_useable_items(ctx.interaction.guild.id, ctx.interaction.user.id))))

        async def use_item(ctx: discord.commands.context.ApplicationContext,
                           item: discord.commands.Option(
                               str,
                               description=bot.i18n.get('INVENTORY_USE_ITEM_OPTION'),
                               autocomplete=use_item_autocomplete
                           )
                           ):
            try:
                item_type_id = int(item[4:].split(' ')[0])
            except:
                raise ItemNotFoundException()
            res = await self.use_item(ctx.author, item_type_id, 1)
            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('INVENTORY_USE_ITEM_SUCCESSFUL').format(res),
                                    color=discord.Color.green()), ephemeral=True)

        async def equip_item_autocomplete(ctx: discord.AutocompleteContext):
            return autocomplete_match(ctx.value, list(map(
                lambda item: 'ID: {} Rarity: {} Name: {} Amount: {:g}'.format(
                    item.InventoryItemType.id,
                    item.InventoryRarity.name,
                    item.InventoryItemType.name,
                    item.UserInventoryItem.amount
                ),
                self.bot.db.get_user_equippable_items(ctx.interaction.guild.id, ctx.interaction.user.id))))

        async def equip_item(ctx: discord.commands.context.ApplicationContext,
                             item: discord.commands.Option(
                                 str,
                                 description=bot.i18n.get('INVENTORY_EQUIP_ITEM_OPTION'),
                                 autocomplete=equip_item_autocomplete
                             )
                             ):
            try:
                item_type_id = int(item[4:].split(' ')[0])
            except:
                raise ItemNotFoundException()
            res = await self.use_item(ctx.author, item_type_id, 1)
            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('INVENTORY_EQUIP_ITEM_SUCCESSFUL').format(res),
                                    color=discord.Color.green()), ephemeral=True)

        async def unequip_item_autocomplete(ctx: discord.AutocompleteContext):
            return autocomplete_match(ctx.value, list(map(
                lambda item: 'ID: {} Rarity: {} Name: {} Amount: {:g}'.format(
                    item.InventoryItemType.id,
                    item.InventoryRarity.name,
                    item.InventoryItemType.name,
                    item.UserInventoryItem.amount
                ),
                self.bot.db.get_user_equipped_items(ctx.interaction.guild.id, ctx.interaction.user.id))))

        async def unequip_item(ctx: discord.commands.context.ApplicationContext,
                               item: discord.commands.Option(
                                   str,
                                   description=bot.i18n.get('INVENTORY_UNEQUIP_ITEM_OPTION'),
                                   autocomplete=unequip_item_autocomplete
                               )
                               ):
            try:
                item_type_id = int(item[4:].split(' ')[0])
            except:
                raise ItemNotFoundException()
            res = await self.use_item(ctx.author, item_type_id, 1)
            return await ctx.respond(
                embed=discord.Embed(title='',
                                    description=self.bot.i18n.get('INVENTORY_UNEQUIP_ITEM_SUCCESSFUL').format(res),
                                    color=discord.Color.green()), ephemeral=True)

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
                raise ItemNotFoundException()
            await self.give_item(member, item_type_id, amount)
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
            func=list_inventory,
            name=self.bot.i18n.get('INVENTORY_LIST_COMMAND'),
            description=self.bot.i18n.get('INVENTORY_LIST_COMMAND_DESCRIPTION'),
            parent=inventory
        ))

        inventory.subcommands.append(discord.SlashCommand(
            func=use_item,
            name=self.bot.i18n.get('INVENTORY_USE_COMMAND'),
            description=self.bot.i18n.get('INVENTORY_USE_COMMAND_DESCRIPTION'),
            parent=inventory
        ))

        inventory.subcommands.append(discord.SlashCommand(
            func=equip_item,
            name=self.bot.i18n.get('INVENTORY_EQUIP_COMMAND'),
            description=self.bot.i18n.get('INVENTORY_EQUIP_COMMAND_DESCRIPTION'),
            parent=inventory
        ))

        inventory.subcommands.append(discord.SlashCommand(
            func=unequip_item,
            name=self.bot.i18n.get('INVENTORY_UNEQUIP_COMMAND'),
            description=self.bot.i18n.get('INVENTORY_UNEQUIP_COMMAND_DESCRIPTION'),
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

        self.bot.module_manager.hooks.add(self, INVENTORY_ADD_ITEM_HOOK, 'inventory', callback=self.give_item)
        self.bot.module_manager.hooks.add(self, INVENTORY_EQUIPPED_ITEMS_HOOK, 'inventory',
                                          callback=self.equipped_items)

    async def equipped_items(self, member: discord.Member, item_action: str):
        actions = []
        for item in self.bot.db.get_user_equipped_items_by_action(member.guild.id, member.id, item_action):
            iactions = json.loads(item.InventoryItemType.actions)
            for action in iactions:
                if action['action'] == item_action:
                    actions.append(action['action_options'])
        return actions

    async def get_inventory(self, member: discord.Member):
        return list(map(lambda item: {
            'item_name': item.InventoryItemType.name,
            'item_amount': item.UserInventoryItem.amount,
            'item_equipped': item.UserInventoryItem.equipped,
            'item_equippable': item.InventoryItemType.equippable,
            'rarity_name': item.InventoryRarity.name,
            'rarity_foreground_color': make_linear_gradient(item.InventoryRarity.foreground_color),
            'rarity_background_color': make_linear_gradient(item.InventoryRarity.background_color)
        }, self.bot.db.get_user_items(member.guild.id, member.id)))

    async def give_item(self, member: discord.Member, item_type_id, amount):
        item_type = self.bot.db.get_item_type_by_id(member.guild.id, item_type_id)
        self.bot.db.add_user_item(member.guild.id, member.id, item_type_id, amount)
        if item_type.useable == -1:
            await self.use_item(member, item_type_id, amount)

    async def use_item(self, member: discord.Member, item_type_id, amount):
        success, item = self.bot.db.use_inventory_item(member.guild.id, member.id, item_type_id, amount)
        if not success:
            raise ItemNotUsableException('item not useable')
        item_type = item.InventoryItemType
        loaded_actions = json.loads(item_type.actions)
        for action in loaded_actions:
            hooks = self.bot.module_manager.hooks.get(member.guild.id, INVENTORY_ITEM_ACTION_HOOK)
            if action['action'] not in hooks:
                raise UnknownException('Item action not found')

            await hooks[action['action']]['callback'](member,
                                                      amount,
                                                      item.UserInventoryItem.equipped,
                                                      action['action_options'])
        return item_type.name

    async def create_rarity_image_by_template(self, rarity, template):
        img_buf = await self.bot.image_creator.create_bytes(template(**rarity))
        return discord.File(filename=f"rarity-{rarity['name']}.png", fp=img_buf)

    async def create_rarity_image(self, guild_id, rarity):
        return await self.create_rarity_image_by_template(
            rarity, self.bot.module_manager.settings.get(guild_id, 'RARITY_IMAGE'))

    async def create_inventory_image_by_template(self, inventory, template):
        img_buf = await self.bot.image_creator.create_bytes(template(items=inventory))
        return discord.File(filename='inventory.png', fp=img_buf)

    async def create_inventory_image(self, guild_id, inventory):
        return await self.create_inventory_image_by_template(
            inventory, self.bot.module_manager.settings.get(guild_id, 'INVENTORY_IMAGE'))

    async def edit_rarity(self, guild: discord.Guild, rarity):
        try:
            if len(rarity['name']) > 20:
                raise WrongInputException('name can only be 20 characters long')

            try:
                make_linear_gradient(rarity['foreground_color'])
                make_linear_gradient(rarity['background_color'])
            except:
                raise WrongInputException('wrong format for color')
            self.bot.db.edit_rarity(guild.id,
                                    rarity['id'] if 'id' in rarity else None,
                                    rarity['name'],
                                    rarity['foreground_color'],
                                    rarity['background_color'])
        except KeyError:
            raise WrongInputException('missing parameter')

    async def get_rarities(self, guild: discord.Guild):
        return {r.order: {'id': r.id,
                          'name': r.name,
                          'foreground_color': r.foreground_color,
                          'background_color': r.background_color,
                          }
                for r in self.bot.db.get_rarities(guild.id)}

    async def edit_item_type(self, guild: discord.Guild, item_type):
        try:
            actions = self.bot.module_manager.hooks.get(guild.id, INVENTORY_ITEM_ACTION_HOOK)
            item_actions = []
            for item_action in item_type['actions']:
                if item_action['action'] not in actions:
                    raise WrongInputException('action "{}" not found'.format(item_type['action']))

                item_actions.append({'action': item_action['action'], 'action_options': {
                    k: item_action['action_options'][k]['value']
                    for k, v in actions[item_action['action']]['options'].items()}
                })

            self.bot.db.edit_inventory_item_type(
                guild.id,
                item_type['id'] if 'id' in item_type else None,
                item_type['name'],
                item_type['rarity_id'],
                item_type['always_visible'],
                item_type['tradable'],
                item_type['equippable'],
                item_type['useable'],
                json.dumps(item_actions)
            )
        except KeyError:
            raise WrongInputException('missing parameter')
