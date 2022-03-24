import discord

from helpers.module_hook_manager import INVENTORY_ITEM_ACTION_HOOK
from helpers.spark_module import SparkModule
from .settings import SETTINGS
from .web import API_PAGES


class WheelspinModule(SparkModule):
    name = 'wheelspin'
    title = 'Wheelspin Module'
    description = 'A module for drehing am Rad'
    api_pages = API_PAGES
    settings = SETTINGS
    dependencies = ['inventory']

    def __init__(self, bot):
        super().__init__(bot)

        self.commands = []

        async def give_wheelspins(member: discord.Member, amount, options):
            available = self.bot.db.get_wheelspin_available(member.guild.id, member.id)
            amount = options['amount'] * amount
            if available is None:
                self.bot.db.set_wheelspin_available(member.guild.id, member.id, amount, 0)
            else:
                self.bot.db.set_wheelspin_available(
                    member.guild.id, member.id, available.amount + amount, available.last_free)

        self.bot.module_manager.hooks.add(
            self,
            INVENTORY_ITEM_ACTION_HOOK,
            hook_id='give-wheelspin',
            name='Give Wheelspin',
            options={
                'amount': {'type': int, 'description': self.bot.i18n.get('GIVE_WHEELSPINS_AMOUNT_DESCRIPTION')},
            },
            callback=give_wheelspins
        )
