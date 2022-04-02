import os
import logging

current_dir = os.path.dirname(os.path.realpath(__file__))

GLOBAL_SETTINGS = {
    'DATABASE_URL': '{protocol}://{hostname}/{path}'.format(protocol='sqlite',
                                                            hostname='',
                                                            path=os.path.join(current_dir, 'dbs', 'bot.db')),
    'APPLICATION_ID': '',
    'APPLICATION_SECRET': '',
    'ACTIVATE_WEBSERVER': True,
    'OAUTH2_REDIRECT_URI': '',
    'WEBSERVER_SECRET': '',
    'WEBSERVER_PORT': 4004,
    'WEBSERVER_STATIC_PATH': os.path.join('webserver', 'static'),
    'WEBSERVER_DEBUG': True,
    'LOGGING_LEVEL': logging.WARNING,
    'WEBSERVER_LOGGING_LEVEL': logging.WARNING,
    'TOKEN': '',
    'DESCRIPTION': 'This is a KGS501 Productions bot!',
    'INTERVAL_TIME': 30,  # in seconds
    'DOWNLOAD_EMOJIS': True,
    'SAVE_EMOJIS': True,
    'EMOJIS_PATH': os.path.join(current_dir, 'images', 'emojis'),
    'FONTS': [
        os.path.join(current_dir, 'fonts', 'Product_Sans_Regular.ttf'),
        os.path.join(current_dir, 'fonts', 'Product_Sans_Bold.ttf')
    ],
}
