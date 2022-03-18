from helpers.dummys import *
from helpers.i18n_manager import I18nManager


def main():
    from bot import DiscordBot
    from imagestack import ImageCreator, ImageStackResolveString
    from helpers.db import Database
    import numpy as np
    import cv2
    import time
    import os
    import asyncio
    import traceback
    import types

    SHOW_IMAGES = False
    PRINT_TRACEBACK = False

    EPS = 0.00000001

    async def wait_for_tasks():
        pending = asyncio.all_tasks()
        for task in pending:
            try:
                await task
            except RuntimeError:
                pass

    def show_image(img):
        if SHOW_IMAGES:
            try:
                cv2.imshow('test', img)
                cv2.waitKey(0)
            except:
                pass

    def float_match(f1, f2):
        return f1 - EPS < f2 < f1 + EPS

    class Tests:
        def __init__(self, bot, db: Database):
            self.bot = bot
            self.db = db

        # test init
        async def test_1_activated_modules(self):
            g = GuildDummy()
            self.db.activate_module(g.id, 'levelsystem')
            if self.db.get_activated_modules(g.id) != ['levelsystem']:
                return False
            self.db.deactivate_module(g.id, 'levelsystem')
            if self.db.get_activated_modules(g.id):
                return False
            return True

    async def run_test(method, test_number, test_name):
        from settings_example import GLOBAL_SETTINGS

        db = Database('')
        i18n = I18nManager(data={})

        b = DiscordBot(db,
                       i18n,
                       image_creator=ImageCreator(fonts=GLOBAL_SETTINGS['FONTS'],
                                                  load_memory=GLOBAL_SETTINGS['IMAGES_LOAD_MEMORY'],
                                                  emoji_path=GLOBAL_SETTINGS['EMOJIS_PATH']))

        t = Tests(b, db)

        print("TEST {:03d}: ".format(test_number), end='')

        error = 'Test Failed'

        start = time.time()
        try:
            if await getattr(t, method)():
                print("SUCCESS! elapsed {}ms | {}".format(round((time.time() - start) * 1000, 1), test_name))
                return True
        except Exception as e:
            if PRINT_TRACEBACK:
                traceback.print_tb(e.__traceback__)
            error = str(e)

        print("FAILED! elapsed {}ms | {} | Error: {}"
              .format(round((time.time() - start) * 1000, 1), test_name, error))
        return False

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    tests = []
    for method_name in sorted(dir(Tests)):
        if callable(getattr(Tests, method_name)) and method_name[:5] == 'test_':
            splitted_name = method_name[5:].split('_')
            tests.append({'method_name': method_name,
                          'test_number': int(splitted_name[0]),
                          'test_name': ' '.join(splitted_name[1:])})

    results = []
    start_time = time.time()
    for test in sorted(tests, key=lambda x: x['test_number']):
        res = asyncio.run(run_test(test['method_name'], test['test_number'], test['test_name']))
        results.append((test, res))

    run_time = time.time() - start_time

    failed_tests = list(filter(lambda x: not x[1], results))
    print('Total amount of Tests: {} | Total time: {}s | Tests Failed: {} [{}]'.format(
        len(tests),
        round(run_time, 1),
        len(failed_tests),
        ', '.join(map(lambda x: 'TEST {} ({})'.format(
            x[0]['test_number'],
            x[0]['test_name']
        ), failed_tests))))

    if len(failed_tests) > 0:
        exit(1)


if __name__ == '__main__':
    main()
