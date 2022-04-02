import os
import sqlite3

from bot import DiscordBot
from helpers.db import Database


def main(token=None):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    old_db_file = os.path.join(current_dir, '..', 'dbs', 'bot.db')
    new_db_file = os.path.join(current_dir, '..', 'dbs', 'merged.db')
    if not os.path.exists(old_db_file):
        print('{} not found'.format(old_db_file))
        quit()

    if os.path.exists(new_db_file):
        print('{} already exists, not merging!'.format(new_db_file))
        quit()

    def _dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    con_old = sqlite3.connect(old_db_file)
    con_old.row_factory = _dict_factory
    cur_old = con_old.cursor()

    print('starting discord bot...')

    def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * (iteration / total))
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)

    async def merge(bot):
        print('Activating Modules...')

        modules = [
            'levelsystem'
            'boost',
            'promo',
            'messaging',
            'message_reactions',
            'emoji_reactions',
        ]

        guilds_len = len(bot.bot.guilds)
        for i, guild in enumerate(bot.bot.guilds):
            print_progress_bar(i + 1, guilds_len, length=50, print_end="")
            for module in modules:
                bot.db.activate_module(guild.id, module)
        print(f'\r')

        print('Merging users table...')

        cur_old.execute('SELECT * FROM users')
        users = cur_old.fetchall()

        users_len = len(users)

        for i, user in enumerate(users):
            print_progress_bar(i + 1, users_len, length=50, print_end="")

            bot.db.update_level_user(user['gid'], user['uid'], {'level': user['lvl'], 'blacklisted': user['blacklist']})

        print(f'\r')

        print('Merging levelsystem table...')

        cur_old.execute('SELECT * FROM lvlsys')
        lvlsys = cur_old.fetchall()

        lvlsys_len = len(lvlsys)

        for i, lvlr in enumerate(lvlsys):
            print_progress_bar(i + 1, lvlsys_len, length=50, print_end="")

            bot.db.set_levelsystem(lvlr['gid'], lvlr['lvl'], lvlr['rid'])

        print(f'\r')

        print('Merging settings table...')

        cur_old.execute('SELECT * FROM settings')
        settings = cur_old.fetchall()

        settings_len = len(settings)

        for i, setting in enumerate(settings):
            print_progress_bar(i + 1, settings_len, length=50, print_end="")

            bot.db.set_setting(setting['gid'], setting['skey'], setting['svalue'])

        print(f'\r')

        print('Merging boosts table...')

        cur_old.execute('SELECT * FROM boosts')
        boosts = cur_old.fetchall()

        boosts_len = len(boosts)

        for i, boost in enumerate(boosts):
            print_progress_bar(i + 1, boosts_len, length=50, print_end="")

            amount = bot.db.get_setting(boost['gid'], 'BOOST_ADD_XP_MULTIPLIER')
            if amount is None:
                amount = bot.module_manager.settings.get_default('BOOST_ADD_XP_MULTIPLIER')

            bot.db.add_xp_boost(boost['gid'],
                                boost['boostedid'],
                                amount,
                                'boostedby:{}'.format(boost['uid']),
                                boost['expires'])

        print(f'\r')

        print('Merging promo boosts table...')

        cur_old.execute('SELECT * FROM promo_boosts')
        promo_boosts = cur_old.fetchall()

        promo_boost_len = len(promo_boosts)

        for i, promo_boost in enumerate(promo_boosts):
            print_progress_bar(i + 1, promo_boost_len, length=50, print_end="")

            amount = bot.db.get_setting(promo_boost['gid'], 'PROMO_BOOST_ADD_XP_MULTIPLIER')
            if amount is None:
                amount = bot.module_manager.settings.get_default('PROMO_BOOST_ADD_XP_MULTIPLIER')

            bot.db.add_xp_boost(promo_boost['gid'],
                                promo_boost['pid'],
                                amount,
                                'promoby:{}'.format(promo_boost['uid']),
                                promo_boost['expires'])

        print(f'\r')

        print('Merging message reactions table...')

        cur_old.execute('SELECT * FROM reactions')
        message_reactions = cur_old.fetchall()

        message_reactions_len = len(message_reactions)

        for i, message_reaction in enumerate(message_reactions):
            print_progress_bar(i + 1, message_reactions_len, length=50, print_end="")

            bot.db.set_message_reaction(message_reaction['gid'], message_reaction['trigger'],
                                        message_reaction['reaction'])

        print(f'\r')

        print('Merging emoji reactions table...')

        cur_old.execute('SELECT * FROM msgreactions')
        emoji_reactions = cur_old.fetchall()

        emoji_reactions_len = len(emoji_reactions)

        for i, emoji_reaction in enumerate(emoji_reactions):
            print_progress_bar(i, emoji_reactions_len, length=50, print_end="")

            guild = bot.bot.get_guild(int(emoji_reaction['gid']))
            if guild is None:
                print(f'\r')
                print('Guild {} not found, skipping reaction'.format(emoji_reaction['gid']))
                continue

            text_channels_len = len(guild.text_channels)
            for j, channel in enumerate(guild.text_channels):
                print_progress_bar(i + (j/text_channels_len), emoji_reactions_len, length=50, print_end="")

                message = None
                try:
                    message = await channel.fetch_message(int(emoji_reaction['msgid']))
                except:
                    pass
                if message is not None:
                    if emoji_reaction['actiontype'] == 'dm':
                        emoji_reaction['actiontype'] = 'send-dm'

                    bot.db.set_emoji_reaction(guild.id,
                                              channel.id,
                                              message.id,
                                              emoji_reaction['reaction'],
                                              emoji_reaction['actiontype'],
                                              emoji_reaction['action'])
        print(f'\r')

        print('Merging to "{}" completed successfully, quitting now...'.format(new_db_file))

        bot.bot.loop.run_until_complete(bot.bot.close())
        quit()

    class MDiscordBot(DiscordBot):
        async def _on_ready(self):
            print('bot is ready, starting merge...')
            await merge(self)

    b = MDiscordBot(
        Database('{protocol}://{hostname}/{path}'.format(protocol='sqlite',
                                                         hostname='',
                                                         path=new_db_file)),
        current_dir=os.path.join(current_dir, '..')
    )

    b.run(token)


if __name__ == '__main__':
    from settings import GLOBAL_SETTINGS
    main(GLOBAL_SETTINGS['TOKEN'])
