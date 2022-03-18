import os
import logging

current_dir = os.path.dirname(os.path.realpath(__file__))

GLOBAL_SETTINGS = {
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
    'FONTS': {
        'regular': os.path.join(current_dir, 'fonts', 'Product_Sans_Regular.ttf'),
        'bold': os.path.join(current_dir, 'fonts', 'Product_Sans_Bold.ttf'),
    },
    'IMAGES_LOAD_MEMORY': [
        # DirectoryImageLoader(prefix='emojis', directory=os.path.join(current_dir, 'images', 'emojis'))
    ],
}
