import random
import time

import discord

from helpers.exceptions import WheelspinForbiddenException, WheelspinEmptyException
from helpers.module_hook_manager import INVENTORY_ITEM_ACTION_HOOK, INVENTORY_ADD_ITEM_HOOK
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

        async def give_wheelspins(member: discord.Member, amount, equipped, options):
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
                'amount': {'type': 'float', 'description': self.bot.i18n.get('GIVE_WHEELSPINS_AMOUNT_DESCRIPTION')},
            },
            callback=give_wheelspins
        )

    async def set_wheelspin(self, guild: discord.Guild, wheelspin):
        self.bot.db.set_wheelspin(guild.id, wheelspin)

    async def spin_wheel(self, member: discord.Member):
        available = self.bot.db.get_wheelspin_available(member.guild.id, member.id)
        current_time = time.time()
        if available is None:
            self.bot.db.set_wheelspin_available(member.guild.id, member.id, 0, current_time)
        else:
            free_wheelspin = available.last_free + \
                             (self.bot.module_manager.settings.get(
                                 member.guild.id, 'WHEELSPIN_FREE_RESET_HOURS') * 60 * 60)
            if free_wheelspin < current_time:
                self.bot.db.set_wheelspin_available(member.guild.id, member.id, available.amount, current_time)
            elif available.amount >= 1:
                self.bot.db.set_wheelspin_available(member.guild.id, member.id,
                                                    available.amount - 1,
                                                    available.last_free)
            else:
                raise WheelspinForbiddenException()

        wheelspin = self.bot.db.get_wheelspin(member.guild.id)
        if not wheelspin:
            raise WheelspinEmptyException()

        result = random.choices(population=wheelspin,
                                weights=list(map(lambda x: x.WheelspinProbability.probability, wheelspin)))[0]

        hook = self.bot.module_manager.hooks.get_one(member.guild.id, INVENTORY_ADD_ITEM_HOOK, 'inventory')
        if hook is not None:
            await hook['callback'](member, result.WheelspinProbability.item_type_id, result.WheelspinProbability.amount)

        return result
