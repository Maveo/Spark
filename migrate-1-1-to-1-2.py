from tinydb import TinyDB

import sqlite3


async def main():
    def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * (iteration / total))
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)

    new_db = 'dbs/merged.db'

    con = sqlite3.connect(new_db)

    cur = con.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY,
            gid INTEGER NOT NULL,
            lvl REAL NOT NULL,
            xp_multiplier REAL NOT NULL,
            joined INTEGER NOT NULL,
            blacklist INTEGER NOT NULL
        );''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS lvlsys (
            lsid INTEGER PRIMARY KEY,
            gid INTEGER NOT NULL,
            lvl INTEGER NOT NULL,
            rid INTEGER NOT NULL
        );''')

    con.commit()

    print('Merging user db...')
    user_db = TinyDB('dbs/users.json')

    for guild in user_db.all():
        print('Merging Guild: {}'.format(guild['gid']))
        i = 0
        user_items = guild['users'].items()
        for uid, user in user_items:
            user['joined'] = -1
            print_progress_bar(i+1, len(user_items), length=50, print_end="")

            cur = con.cursor()
            cur.execute('INSERT OR REPLACE INTO users(uid, gid, lvl, xp_multiplier, joined, blacklist)'
                        'VALUES(?, ?, ?, ?, ?, ?);',
                        (user['uid'],
                         guild['gid'],
                         user['lvl'],
                         user['xp_multiplier'],
                         user['joined'],
                         user['blacklist'],
                         ))
            i += 1

        print(f'\r')

        con.commit()

        print('Merged {} Users'.format(i))

    print('Merging level system db...')
    lvlsys_db = TinyDB('dbs/lvlsys.json')
    for guild in lvlsys_db.all():
        print('Merging Guild: {}'.format(guild['gid']))
        i = 0
        lvlsys_items = guild['lvlsys'].items()
        for lvl, rid in guild['lvlsys'].items():
            print_progress_bar(i+1, len(lvlsys_items), length=50, print_end="")

            cur = con.cursor()
            cur.execute('INSERT OR REPLACE INTO lvlsys(gid, lvl, rid)'
                        'VALUES(?, ?, ?);',
                        (guild['gid'], lvl, rid,))
            i += 1

        print(f'\r')

        con.commit()

        print('Merged {} Roles'.format(i))

    print('Merging finished! Written To File: {}'.format(new_db))


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
