from helpers.imgtools import *

current_dir = os.path.dirname(os.path.realpath(__file__))

GLOBAL_SETTINGS = {
    'APPLICATION_ID': '',
    'TOKEN': '',
    'COMMAND_PREFIX': '>',
    'DESCRIPTION': 'This is a KGS501 Productions bot!',
    'PRINT_LOGGING': True,
    'USE_SLASH_COMMANDS': False,
    'UPDATE_VOICE_XP_INTERVAL': 30,  # in seconds
    'FONTS': {
        'regular': os.path.join(current_dir, 'fonts', 'Product_Sans_Regular.ttf'),
        'bold': os.path.join(current_dir, 'fonts', 'Product_Sans_Bold.ttf'),
    },
    'IMAGES_LOAD_MEMORY': [
        DirectoryImageLoader(prefix='emojis', directory=os.path.join(current_dir, 'images', 'emojis'))
    ]
}


def profile_image(x): return [
    RectangleLayer(
        pos=(0, 0),
        line_width=-1,
        size=(600, 150),
        radius=20,
        color=(55, 50, 48),
    ),

    WebImageLayer(
        pos=(15, 15),
        resize=(120, 120),
        url=x['avatar_url']
    ),

    RectangleLayer(
        pos=(15, 15),
        size=(120, 120),
        color=(55, 50, 48),
        radius=-60,
    ),

    # Emoji
    EmojiLayer(
        pos=(147, 15),
        resize=(40, 40),
        emoji=x['member'].top_role.name[0]
    ),

    # Pregressbar BG
    ProgressLayer(
        pos=(150, 115),
        percentage=1,
        line_width=-1,
        direction='x',
        size=(430, 20),
        radius=10,
        color=(87, 87, 87)
    ),

    # Progressbar
    ProgressLayer(
        pos=(150, 115),
        percentage=x['xp_percentage'],
        line_width=-1,
        direction='x',
        size=(430, 20),
        radius=10,
        color=LinearGradientColor((24, 110, 241, 255),
                                  (7, 222, 255, 255),
                                  1)
    ),

    # Username
    TextLayer(
        pos=(200, 39),
        align_y='center',
        font='regular',
        font_size=min(35, max(10, int(520 / len(str(x['name']))))),
        text=str(x['name']),
        color=x['color'],
        max_size=(280, 35)
    ),

    # Lvl.
    TextLayer(
        pos=(150, 92),
        font='regular',
        font_size=22,
        text='Lvl.',
        color=(103, 103, 103),
        max_size=(30, 22)
    ),

    # Lvl-value
    TextLayer(
        pos=(188, 87),
        font='regular',
        font_size=28,
        text=str(x['lvl']),
        color=(255, 255, 255),
        max_size=(100, 28)
    ),

    # Rank
    TextLayer(
        pos=(578, 24),
        align_x='right',
        font='bold',
        font_size=35,
        text='#' + str(x['rank']),
        color=x['color'],
        max_size=(90, 30)
    ),

    # Xp Multiplier
    TextLayer(
        pos=(580, 72),
        align_x='right',
        font='regular',
        font_size=20,
        text='{:.2f}x'.format(x['xp_multiplier']) if x['xp_multiplier'] != 1 else '',
        color=(102, 172, 47) if x['xp_multiplier'] > 1 else (
            (60, 20, 220) if x['xp_multiplier'] < 0 else (0, 128, 255)),
        max_size=(150, 20)
    ),

    TextLayer(
        pos=(580, 95),
        align_x='right',
        font='regular',
        font_size=18,
        text=str(x['xp']) + ' / ' + str(x['max_xp']) + ' XP',
        color=(170, 170, 170),
        max_size=(280, 18)
    )
]


def level_up_image(x): return [
    RectangleLayer(
        pos=(0, 0),
        line_width=-1,
        size=(200, 100),
        radius=20,
        color=(55, 50, 48),
    ),

    RectangleLayer(
        pos=(0, 0),
        line_width=2,
        size=(200, 100),
        radius=20,
        color=LinearGradientColor(SingleColor(x['color']).darkened(0.5),
                                  SingleColor(x['color']),
                                  1)
    ),

    # LEVELUP
    TextLayer(
        pos=(57, 13),
        font='bold',
        font_size=22,
        text='LEVELUP',
        color=LinearGradientColor(SingleColor(x['color']).darkened(0.5),
                                  SingleColor(x['color']),
                                  1),
        max_size=(170, 25)
    ),

    EmojiLayer(
        pos=(58, 70),
        resize=(16, 16),
        emoji=x['member'].top_role.name[0],
    ),

    EmojiLayer(
        pos=(125, 70),
        resize=(16, 16),
        emoji=x['member'].top_role.name[0],
    ),

    ProgressLayer(
        pos=(82, 77),
        percentage=1,
        line_width=-1,
        size=(34, 4),
        radius=2,
        color=LinearGradientColor(SingleColor(x['color']).alpha(0),
                                  SingleColor(x['color']),
                                  1)
    ),

    TextLayer(
        pos=(53, 73),
        align_x='right',
        font='regular',
        font_size=12,
        text='Lvl. ' + str(x['old_lvl']),
        color=x['color'],
        max_size=(50, 22)
    ),

    TextLayer(
        pos=(145, 73),
        font='regular',
        font_size=12,
        text='Lvl. ' + str(x['new_lvl']),
        color=x['color'],
        max_size=(50, 22)
    ),

    TextLayer(
        pos=(100, 42),
        font='regular',
        font_size=13,
        align_x='center',
        text=x['name'],
        color=(255, 255, 255),
        max_size=(180, 16)
    ),
]


def rank_up_image(x): return [
    # BG
    RectangleLayer(
        pos=(0, 0),
        line_width=-1,
        size=(200, 100),
        radius=20,
        color=(55, 50, 48),
    ),

    # BG Border
    RectangleLayer(
        pos=(0, 0),
        line_width=2,
        size=(200, 100),
        radius=20,
        color=LinearGradientColor(SingleColor(x['old_color']),
                                  SingleColor(x['new_color']),
                                  1),
    ),

    # RANKUP
    TextLayer(
        pos=(58, 13),
        font='bold',
        font_size=22,
        text='RANKUP',
        color=LinearGradientColor(SingleColor(x['old_color']),
                                  SingleColor(x['new_color']),
                                  1),
        max_size=(170, 25)
    ),

    EmojiLayer(
        pos=(58, 70),
        resize=(16, 16),
        emoji=x['old_role'].name[0],
    ),

    EmojiLayer(
        pos=(125, 70),
        resize=(16, 16),
        emoji=x['new_role'].name[0],
    ),

    ProgressLayer(
        pos=(82, 77),
        percentage=1,
        line_width=-1,
        size=(34, 4),
        radius=2,
        color=LinearGradientColor(SingleColor(x['old_color']),
                                  SingleColor(x['new_color']),
                                  1)
    ),

    TextLayer(
        pos=(53, 73),
        align_x='right',
        font='regular',
        font_size=12,
        text='Lvl. ' + str(x['old_lvl']),
        color=x['old_color'],
        max_size=(50, 22)
    ),

    TextLayer(
        pos=(145, 73),
        font='regular',
        font_size=12,
        text='Lvl. ' + str(x['new_lvl']),
        color=x['new_color'],
        max_size=(50, 22)
    ),

    TextLayer(
        pos=(100, 42),
        font='regular',
        font_size=13,
        align_x='center',
        text=x['name'],
        color=(255, 255, 255),
        max_size=(180, 16)
    ),
]


def ranking_image(x):
    height = len(x) * 85 + 410
    layers = [

        # Background
        RectangleLayer(
            pos=(0, 0),
            line_width=-1,
            size=(1200, height),
            radius=55,
            color=(55, 50, 48),
        ),

        # Leaderboard Text Border
        RectangleLayer(
            pos=(30, 40),
            line_width=10,
            size=(1140, 180),
            radius=45,
            color=LinearGradientColor((76, 142, 217),
                                      (7, 222, 255),
                                      1)
        ),

        # Leaderboard Text
        TextLayer(
            pos=(310, 93),
            font='bold',
            font_size=100,
            text='Leaderboard',
            color=(255, 255, 255),
            max_size=(900, 100)
        ),

        # Name Header Text
        TextLayer(
            pos=(90, 255),
            font='regular',
            font_size=65,
            text='Name',
            color=(87, 87, 87),
            max_size=(300, 50)
        ),

        # Level Header Text
        TextLayer(
            pos=(1025, 255),
            font='regular',
            font_size=65,
            text='Lvl.',
            color=(87, 87, 87),
            max_size=(300, 50)
        ),

        # Members Background
        RectangleLayer(
            pos=(37, 320),
            line_width=-1,
            size=(1100, height - 355),
            radius=55,
            color=(65, 59, 57),
        ),

        # Levels Background
        RectangleLayer(
            pos=(978, 320),
            line_width=-1,
            size=(185, height - 355),
            radius=45,
            color=LinearGradientColor((130, 214, 254),
                                      (49, 177, 232),
                                      1)
        ),
    ]

    for i in range(len(x)):
        pos_y = i * 85 + 370
        layers.append(TextLayer(
            pos=(150, pos_y + 2),
            font='bold',
            align_x='center',
            font_size=60,
            text='#' + str(x[i]['rank']),
            color=(255, 255, 255),
            max_size=(200, 150)
        ))
        layers.append(EmojiLayer(
            pos=(240, pos_y - 10),
            resize=(60, 60),
            emoji=x[i]['member'].top_role.name[0]
        ))
        layers.append(TextLayer(
            pos=(323, pos_y),
            font='regular',
            font_size=60,
            text=x[i]['name'],
            color=(255, 255, 255),
            max_size=(600, 150)
        ))
        layers.append(TextLayer(
            pos=(1069, pos_y + 2),
            font='regular',
            align_x='center',
            font_size=60,
            text=str(x[i]['lvl']),
            color=(29, 29, 29),
            max_size=(250, 150)
        ))
    return layers


def welcome_image(x): return [
    FileImageLayer(
        file=os.path.join(current_dir, 'images', 'welcome_template.png')
    ),
    WebImageLayer(
        pos=(85, 35),
        resize=(60, 60),
        url=x['guild_icon_url']
    ),
    RectangleLayer(
        pos=(85, 35),
        size=(60, 60),
        color=(55, 50, 48),
        radius=-30,
    ),
    WebImageLayer(
        pos=(15, 130),
        resize=(80, 80),
        url=x['avatar_url']
    ),
    RectangleLayer(
        pos=(15, 130),
        size=(80, 80),
        color=(55, 50, 48),
        radius=-40,
    ),
    TextLayer(
        pos=(110, 170),
        align_y='center',
        font='bold',
        font_size=min(42, max(20, int(700 / len(str(x['name']))))),
        text=str(x['name']),
        color=(255, 255, 255),
        max_size=(460, 50)
    ),
]


DEFAULT_GUILD_SETTINGS = {
    'NEW_USER_LEVEL': 1.0,
    'NEW_USER_XP_MULTIPLIER': 1.0,
    'MESSAGE_XP': 0.2,
    'VOICE_XP_PER_MINUTE': 2.0,
    'BOOST_EXPIRES_DAYS': 7.0,
    'BOOST_ADD_XP_MULTIPLIER': 0.25,
    'SEND_WELCOME_IMAGE': True,
    'PROMO_CHANNEL_ID': '',
    'PROMO_CODE_LENGTH': 6,
    'PROMO_CODE_EXPIRES_HOURS': 24.0,
    'PROMO_BOOST_EXPIRES_DAYS': 7.0,
    'PROMO_BOOST_ADD_XP_MULTIPLIER': 2.0,
    'PROMO_USER_SET_LEVEL': 2.0,
    'COIN_FLIP_AUDIO_CHANCE': 0.01,  # chance as percentage
    'COMMAND_NOT_FOUND_RESPONSES': [
        'Kenn ich nicht, den command',
        '??',
        'Kann grad nicht, sorry...',
        'Wat willste jetzt von mir?',
        'Sicher, dass du das richtig geschrieben hast?',
        'ham wir leider nicht im Angebot',
        'ERROR: User hat einen unbekannten command verwendet, oh gott was mache ich jetzt??',
        'Nope',
        'Kenn ich nicht, kann ich nicht...',
        'Hä, was nochmal?',
        'Den command scheint es nicht zu geben. Moment ich schaue nochmal nach.',
        'Ding Dong, command ist gone',
        'Was genau sollte der command jetzt machen?',
        'Command konnte nicht gefunden werden',
        'Vielen Dank für ihren Anruf, aber dieser command hat heute leider keine Zeit für Sie.'
        'Versuchen Sie es doch erneut, wenn wir ihn implementiert haben.',
        'Der command ist leider nicht im Sortiment...',
        'Dafür bin ich nicht der richtige Ansprechpartner',
    ],
    'MISSING_PERMISSIONS_RESPONSES': [
        'Das darfst du leider nicht schreiben',
        'Lass mich kurz nachgucken... Aha! Ne haste keine Rechte zu',
        'Mach nen Abgang du Hobby Hacker!',
        'Überlass das lieber den Admins...',
        '🤨Warum genau sollte ich dich sowas ausführen lassen?',
        'Keine Rechte für dich, Kollege!',
        'Halt mal schön die Füße still',
        'Lass besser die Finger von solchen commands, sonst hole ich den Admin!',
        'Ohoh, wenn das der Admin sieht...',
        'Diesen command darfst du leider nicht benutzen',
        'Nene lass bloß die Finger davon!',
        'Frag lieber nochmal nach, ob du sowas benutzen darfst. Ich frag auch nochmal...',
        'Beep boop beep. Keine Berechtigung',
        'HALT STOP!'
    ],
    'PROFILE_IMAGE': profile_image,
    'LEVEL_UP_IMAGE': level_up_image,
    'RANK_UP_IMAGE': rank_up_image,
    'RANKING_IMAGE': ranking_image,
    'WELCOME_IMAGE': welcome_image,
}
