class RoleDummy:
    def __init__(self, uid):
        self.id = uid


class MemberDummy:
    def __init__(self, uid):
        self.id = uid
        self.roles = {}

    def add_roles(self, role):
        self.roles[role.id] = True

    def remove_roles(self, role):
        if role.id in self.roles:
            del self.roles[role.id]


class GuildDummy:
    def __init__(self, uid, roles=None):
        self.id = uid
        self.roles = roles
        if self.roles is None:
            self.roles = []


class Tests:
    def __init__(self, bot, user_db, lvlsys_db):
        self.bot = bot
        self.user_db = user_db
        self.lvlsys_db = lvlsys_db

    # test init
    def test_1(self):
        return self.user_db.all() == []

    # test join
    def test_2(self):
        self.bot.member_joined_vc(MemberDummy(0), 0)
        return self.user_db.all() == [{'uid': 0, 'lvl': 1, 'xp': 0, 'xp_multiplier': 1, 'joined': 0}]

    # test leveling 1
    def test_3(self):
        self.bot.member_joined_vc(MemberDummy(0), 0)
        self.bot.member_left_vc(GuildDummy(0), MemberDummy(0), 60 * 60 * 1)
        return self.user_db.all() == [{'uid': 0, 'lvl': 1, 'xp': 60.0, 'xp_multiplier': 1, 'joined': 0}]

    # test leveling 2
    def test_4(self):
        self.bot.member_joined_vc(MemberDummy(0), 0)
        self.bot.member_left_vc(GuildDummy(0), MemberDummy(0), 60 * 60 * 5)
        return self.user_db.all() == [{'uid': 0, 'lvl': 3, 'xp': 90.0, 'xp_multiplier': 1, 'joined': 0}]

    # test set lvlsys point
    def test_5(self):
        self.bot.lvlsys_set(0, 0, 5)
        return self.lvlsys_db.all() == [{'gid': 0, 'lvlsys': {'5': 0}}]

    # test remove lvlsys point
    def test_6(self):
        self.bot.lvlsys_set(0, 0, 5)
        self.bot.lvlsys_set(0, 0, 6)
        self.bot.lvlsys_remove(0, 5)
        return self.lvlsys_db.all() == [{'gid': 0, 'lvlsys': {'6': 0}}]

    # test role
    def test_7(self):
        self.bot.lvlsys_set(0, 0, 0)
        self.bot.lvlsys_set(0, 1, 2)
        self.bot.lvlsys_set(0, 2, 5)
        self.user_db.insert({'uid': 0, 'lvl': 3, 'xp': 0, 'xp_multiplier': 1})
        m = MemberDummy(0)
        self.bot.member_joined_vc(m, 0)
        self.bot.member_left_vc(GuildDummy(0, [
            RoleDummy(0),
            RoleDummy(1),
            RoleDummy(2)
        ]), m, 0)
        return m.roles == {1: True}


def main():
    for method_name in dir(Tests):
        if callable(getattr(Tests, method_name)) and method_name[:5] == 'test_':

            user_db = TinyDB(storage=MemoryStorage)
            lvlsys_db = TinyDB(storage=MemoryStorage)

            b = DiscordBot(user_db, lvlsys_db)

            t = Tests(b, user_db, lvlsys_db)

            start = time.time()
            if getattr(t, method_name)():
                print("TEST {}: SUCCESS! elapsed {}ms".format(method_name[5:], round((time.time() - start) * 1000, 1)))
            else:
                print("TEST {}: FAILED! elapsed {}ms".format(method_name[5:], round((time.time() - start) * 1000, 1)))


if __name__ == '__main__':
    from bot import DiscordBot
    from tinydb import TinyDB, Query, operations
    from tinydb.storages import MemoryStorage
    import time

    main()
