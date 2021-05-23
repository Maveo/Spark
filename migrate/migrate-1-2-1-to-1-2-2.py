import os
import sqlite3

from shutil import copyfile


async def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    old_db = os.path.join(current_dir, '..', 'dbs', 'bot.db')
    new_db = os.path.join(current_dir, '..', 'dbs', 'merged.db')

    copyfile(old_db, new_db)

    con_old = sqlite3.connect(old_db)
    con_new = sqlite3.connect(new_db)

    cur_old = con_old.cursor()
    cur_new = con_new.cursor()

    cur_new.execute('DROP TABLE users;')

    cur_new.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    uid INTEGER,
                    gid INTEGER,
                    lvl REAL NOT NULL,
                    xp_multiplier REAL NOT NULL,
                    joined INTEGER NOT NULL,
                    blacklist INTEGER NOT NULL,
                    PRIMARY KEY (uid, gid)
                );''')

    con_new.commit()

    cur_old.execute('SELECT * FROM users')
    users = cur_old.fetchall()

    cur_new.executemany('INSERT OR REPLACE INTO users(uid, gid, lvl, xp_multiplier, joined, blacklist)'
                        'VALUES(?, ?, ?, ?, ?, ?);',
                        users)

    con_new.commit()

    print('Merging finished! Written To File: {}'.format(new_db))


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
