import asyncio
import unittest

from bot import DiscordBot
from helpers.db import Database
from helpers.dummys import GuildDummy
from helpers.i18n_manager import I18nManager


def call_async(cor):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(cor)
    loop.close()
    return result


class TestStringMethods(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.bot = DiscordBot(
            Database(''),
            I18nManager(data={})
        )

    async def test_activate_module(self):
        g = GuildDummy()
        self.bot.db.activate_module(g.id, 'levelsystem')
        self.assertListEqual(self.bot.db.get_activated_modules(g.id), ['levelsystem'])
        self.bot.db.deactivate_module(g.id, 'levelsystem')
        self.assertListEqual(self.bot.db.get_activated_modules(g.id), [])


if __name__ == '__main__':
    unittest.main()
