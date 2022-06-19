import logging
import os
import shutil
import subprocess
import sys
import threading

from imagestack_svg.imagecreator import ImageCreator
from imagestack_svg.loaders import FontLoader, EmojiLoader

from bot import DiscordBot
from helpers.db import Database
from helpers.i18n_manager import I18nManager

from settings import GLOBAL_SETTINGS
from helpers.settings_manager import GlobalSettingsValidator
from webserver import WebServer

logging.basicConfig()

current_dir = os.path.dirname(os.path.realpath(__file__))

global_settings = GlobalSettingsValidator.validate(GLOBAL_SETTINGS)

bot = DiscordBot(
    db=Database(global_settings['DATABASE_URL']),
    i18n=I18nManager(path=global_settings['I18N_FILE']),
    current_dir=current_dir,
    interval_time=global_settings['INTERVAL_TIME'],
    description=global_settings['DESCRIPTION'],
    super_admins=global_settings['SUPER_ADMINS'],
    image_creator=ImageCreator(font_loader=FontLoader(
        global_settings['FONTS']),
        emoji_loader=EmojiLoader(
            emoji_path=global_settings['EMOJIS_PATH'],
            download_emojis=global_settings['DOWNLOAD_EMOJIS'],
            save_downloaded_emojis=global_settings['SAVE_EMOJIS']
        )),
    logging_level=global_settings['LOGGING_LEVEL'],
)

webserver_static_path = os.path.join(current_dir, global_settings['WEBSERVER_STATIC_PATH'])
if not os.path.exists(webserver_static_path):
    os.mkdir(webserver_static_path)

build_frontend = False
skip_check = False
install = False

if '--install' in sys.argv[1:]:
    install = True

if '--skip-check' in sys.argv[1:]:
    skip_check = True

if not build_frontend and '--build' in sys.argv[1:]:
    build_frontend = True

if not skip_check and not build_frontend and len(os.listdir(webserver_static_path)) == 0:
    i = input('webserver path ({}) is empty. Do you want to build the frontend into that folder? [y/N] '
              .format(webserver_static_path))
    if i.upper() == 'Y':
        build_frontend = True

if build_frontend:
    if install:
        print('installing node packages...')
        code = subprocess.Popen('npm i',
                                cwd=os.path.join(current_dir, 'frontend'),
                                shell=True).wait()
        if code != 0:
            print('An error occurred while installing!')
            quit(code)

    print('building frontend...')

    code = subprocess.Popen('npm run build',
                            cwd=os.path.join(current_dir, 'frontend'),
                            shell=True).wait()
    if code != 0:
        print('An error occurred while building!')
        quit(code)

    if os.path.join(current_dir, 'frontend', 'dist') != webserver_static_path:
        shutil.rmtree(webserver_static_path)
        shutil.copytree(os.path.join(current_dir, 'frontend', 'dist'), webserver_static_path)

web = WebServer(
    oauth2_client_id=global_settings['APPLICATION_ID'],
    oauth2_client_secret=global_settings['APPLICATION_SECRET'],
    oauth2_redirect_uri=global_settings['OAUTH2_REDIRECT_URI'],
    webserver_secret=global_settings['WEBSERVER_SECRET'],
    discord_bot=bot,
    static_path=webserver_static_path,
    debug=global_settings['WEBSERVER_DEBUG'],
)

app = web.app

if __name__ == '__main__':
    t = threading.Thread(target=web.run)
    t.daemon = True
    t.start()
    bot.run(global_settings['TOKEN'])

else:
    import asyncio

    def run_bot():
        bot.bot.loop = asyncio.new_event_loop()
        bot.run(global_settings['TOKEN'])

    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
