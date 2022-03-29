import discord

from helpers.exceptions import NoMoneyException
from helpers.module_hook_manager import INVENTORY_ADD_ITEM_HOOK
from helpers.spark_module import SparkModule
from .settings import SETTINGS
from .web import API_PAGES


class StoreModule(SparkModule):
    name = 'store'
    title = 'Store'
    description = 'Module allowing to sell and buy'
    dependencies = ['inventory']
    api_pages = API_PAGES
    settings = SETTINGS

    def __init__(self, bot):
        super().__init__(bot)

        self.commands = []

    async def buy_offer(self, member: discord.Member, offer_id: int, amount: float):
        offer = self.bot.db.get_offer(member.guild.id, offer_id)
        user_amount = self.bot.db.get_user_item_amount(member.guild.id, member.id, offer.from_item_id)
        if user_amount < offer.from_item_amount * amount:
            raise NoMoneyException('you have not enough to buy this')
        hook = self.bot.module_manager.hooks.get_one(member.guild.id, INVENTORY_ADD_ITEM_HOOK, 'inventory')
        if hook is not None:
            await hook['callback'](member, offer.from_item_id, -offer.from_item_amount * amount)
            await hook['callback'](member, offer.to_item_id, offer.to_item_amount * amount)
