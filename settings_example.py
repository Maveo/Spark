from imagestack import *
from helpers.settings_manager import Setting
import os

current_dir = os.path.dirname(os.path.realpath(__file__))

GLOBAL_SETTINGS = {
    'APPLICATION_ID': '',
    'APPLICATION_SECRET': '',
    'ACTIVATE_WEBSERVER': True,
    'OAUTH2_REDIRECT_URI': 'http://localhost:4004/login',
    'WEBSERVER_PORT': 4004,
    'WEBSERVER_STATIC_PATH': 'static',
    'WEBSERVER_DEBUG': False,
    'TOKEN': '',
    'COMMAND_PREFIX': '>',
    'DESCRIPTION': 'This is a KGS501 Productions bot!',
    'PRINT_LOGGING': True,
    'USE_SLASH_COMMANDS': False,
    'UPDATE_VOICE_XP_INTERVAL': 30,  # in seconds
    'DOWNLOAD_EMOJIS': True,
    'SAVE_EMOJIS': True,
    'EMOJIS_PATH': os.path.join(current_dir, 'images', 'emojis'),
    'FONTS': {
        'regular': os.path.join(current_dir, 'fonts', 'Product_Sans_Regular.ttf'),
        'bold': os.path.join(current_dir, 'fonts', 'Product_Sans_Bold.ttf'),
    },
    'IMAGES_LOAD_MEMORY': [
        # DirectoryImageLoader(prefix='emojis', directory=os.path.join(current_dir, 'images', 'emojis'))
    ]
}

profile_image = ImageStackResolveString('''ImageStack([
    RectangleLayer(
        pos=(0, 0),
        line_width=-1,
        size=(600, 150),
        radius=20,
        color=(48, 50, 55),
    ),

    WebImageLayer(
        pos=(15, 15),
        resize=(120, 120),
        url=Variable('avatar_url')
    ),

    RectangleLayer(
        pos=(15, 15),
        size=(120, 120),
        color=(48, 50, 55),
        radius=-60,
    ),

    # Emoji
    EmojiLayer(
        pos=(147, 15),
        resize=(40, 40),
        emoji=Variable(('member', 'top_role', 'name', 0,))
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
        percentage=Variable('xp_percentage'),
        line_width=-1,
        direction='x',
        size=(430, 20),
        radius=10,
        color=LinearGradientColor((241, 110, 24),
                                  (255, 222, 7),
                                  1)
    ),

    # Username
    TextLayer(
        pos=(200, 39),
        align_y='center',
        font='regular',
        font_size=35,
        text=Variable('name'),
        color=Variable('color'),
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
        text=Variable('lvl'),
        color=(255, 255, 255),
        max_size=(100, 28)
    ),

    # Rank
    TextLayer(
        pos=(578, 24),
        align_x='right',
        font='bold',
        font_size=35,
        text=Variable('rank').formatted('#{}'),
        color=Variable('color'),
        max_size=(90, 30)
    ),

    # Xp Multiplier
    TextLayer(
        pos=(580, 72),
        align_x='right',
        font='regular',
        font_size=20,
        text=EqualityVariable('xp_multiplier', 1, '', Variable('xp_multiplier').formatted('{:.2f}x')),
        color=EqualityVariable('xp_multiplier', 1, (0, 0, 0), (47, 172, 102),
                               EqualityVariable('xp_multiplier', 0, (255, 128, 0), (255, 128, 0), (220, 20, 60))),
        max_size=(150, 20),
    ),

    TextLayer(
        pos=(580, 95),
        align_x='right',
        font='regular',
        font_size=18,
        text=FormattedVariables(['xp', 'max_xp'], '{} / {} XP'),
        color=(170, 170, 170),
        max_size=(280, 18)
    )
])''')


level_up_image = ImageStackResolveString('''ImageStack([
    RectangleLayer(
        pos=(0, 0),
        line_width=-1,
        size=(200, 100),
        radius=20,
        color=(48, 50, 55),
    ),

    RectangleLayer(
        pos=(0, 0),
        line_width=2,
        size=(200, 100),
        radius=20,
        color=LinearGradientColor(SingleColorVariable('color').darkened(0.5),
                                  SingleColorVariable('color'),
                                  1),
    ),

    # LEVELUP
    TextLayer(
        pos=(57, 13),
        font='bold',
        font_size=22,
        text='LEVELUP',
        color=LinearGradientColor(SingleColorVariable('color').darkened(0.5),
                                  SingleColorVariable('color'),
                                  1),
        max_size=(170, 25),
    ),

    EmojiLayer(
        pos=(58, 70),
        resize=(16, 16),
        emoji=Variable(('member', 'top_role', 'name', 0,)),
    ),

    EmojiLayer(
        pos=(125, 70),
        resize=(16, 16),
        emoji=Variable(('member', 'top_role', 'name', 0,)),
    ),

    ProgressLayer(
        pos=(82, 77),
        percentage=1,
        line_width=-1,
        size=(34, 4),
        radius=2,
        color=LinearGradientColor(SingleColorVariable('color').alpha(0),
                                  SingleColorVariable('color'),
                                  1),
    ),

    TextLayer(
        pos=(53, 73),
        align_x='right',
        font='regular',
        font_size=12,
        text=Variable('old_lvl').formatted('Lvl. {}'),
        color=Variable('color'),
        max_size=(50, 22),
    ),

    TextLayer(
        pos=(145, 73),
        font='regular',
        font_size=12,
        text=Variable('new_lvl').formatted('Lvl. {}'),
        color=Variable('color'),
        max_size=(50, 22),
    ),

    TextLayer(
        pos=(100, 42),
        font='regular',
        font_size=13,
        align_x='center',
        text=Variable('name'),
        color=(255, 255, 255),
        max_size=(180, 16),
    ),
])''')


rank_up_image = ImageStackResolveString('''ImageStack([
    # BG
    RectangleLayer(
        pos=(0, 0),
        line_width=-1,
        size=(200, 100),
        radius=20,
        color=(48, 50, 55),
    ),

    # BG Border
    RectangleLayer(
        pos=(0, 0),
        line_width=2,
        size=(200, 100),
        radius=20,
        color=LinearGradientColor(SingleColorVariable('old_color'),
                                  SingleColorVariable('new_color'),
                                  1),
    ),

    # RANKUP
    TextLayer(
        pos=(58, 13),
        font='bold',
        font_size=22,
        text='RANKUP',
        color=LinearGradientColor(SingleColorVariable('old_color'),
                                  SingleColorVariable('new_color'),
                                  1),
        max_size=(170, 25)
    ),

    EmojiLayer(
        pos=(58, 70),
        resize=(16, 16),
        emoji=Variable(('old_role', 'name', 0,)),
    ),

    EmojiLayer(
        pos=(125, 70),
        resize=(16, 16),
        emoji=Variable(('new_role', 'name', 0,)),
    ),

    ProgressLayer(
        pos=(82, 77),
        percentage=1,
        line_width=-1,
        size=(34, 4),
        radius=2,
        color=LinearGradientColor(SingleColorVariable('old_color'),
                                  SingleColorVariable('new_color'),
                                  1),
    ),

    TextLayer(
        pos=(53, 73),
        align_x='right',
        font='regular',
        font_size=12,
        text=Variable('old_lvl').formatted('Lvl. {}'),
        color=SingleColorVariable('old_color'),
        max_size=(50, 22)
    ),

    TextLayer(
        pos=(145, 73),
        font='regular',
        font_size=12,
        text=Variable('new_lvl').formatted('Lvl. {}'),
        color=SingleColorVariable('new_color'),
        max_size=(50, 22)
    ),

    TextLayer(
        pos=(100, 42),
        font='regular',
        font_size=13,
        align_x='center',
        text=Variable('name'),
        color=(255, 255, 255),
        max_size=(180, 16)
    ),
])''')


ranking_image = ImageStackResolveString('''ImageStack([
    # Background
    RectangleLayer(
        pos=(0, 0),
        line_width=-1,
        size=(1200, LengthVariable() * 85 + 410),
        radius=55,
        color=(48, 50, 55),
    ),
    # Leaderboard Text Border
    RectangleLayer(
        pos=(30, 40),
        line_width=10,
        size=(1140, 180),
        radius=45,
        color=LinearGradientColor((217, 142, 76),
                                  (255, 222, 7),
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
        max_size=(300, 65)
    ),

    # Level Header Text
    TextLayer(
        pos=(1025, 255),
        font='regular',
        font_size=65,
        text='Lvl.',
        color=(87, 87, 87),
        max_size=(300, 65)
    ),

    # Members Background
    RectangleLayer(
        pos=(37, 320),
        line_width=-1,
        size=(1100, LengthVariable() * 85 + 410 - 355),
        radius=55,
        color=(57, 59, 65),
    ),

    # Levels Background
    RectangleLayer(
        pos=(978, 320),
        line_width=-1,
        size=(185, LengthVariable() * 85 + 410 - 355),
        radius=45,
        color=LinearGradientColor((254, 214, 130),
                                  (232, 177, 49),
                                  1)
    ),

    # All Users
    ListLayer(
        pos=(0, 360),
        repeat=LengthVariable(),
        template=ImageStack(
            EmptyLayer(
              resize=(1200, 85)
            ),
            TextLayer(
                pos=(135, 8),
                font='bold',
                align_x='center',
                font_size=60,
                text=IteratorVariable()('rank').formatted('#{}'),
                color=(255, 255, 255),
                max_size=(200, -1),
            ),
            EmojiLayer(
                pos=(240, 0),
                resize=(60, 60),
                emoji=IteratorVariable()(('member', 'top_role', 'name', 0,)),
            ),
            TextLayer(
                pos=(323, 8),
                font='regular',
                font_size=60,
                text=IteratorVariable()('name'),
                color=(255, 255, 255),
                max_size=(600, -1)
            ),
            TextLayer(
                pos=(1069, 8),
                font='regular',
                align_x='center',
                font_size=60,
                text=IteratorVariable()('lvl'),
                color=(29, 29, 29),
                max_size=(250, -1)
            )
        )
    )
])''')


welcome_image = ImageStackResolveString('''ImageStack([
    WebImageLayer(
        url="https://raw.githubusercontent.com/skillor/Spark/v1.3.1/images/welcome_template.png"
    ),
    WebImageLayer(
        pos=(85, 35),
        resize=(60, 60),
        url=Variable('guild_icon_url'),
    ),
    RectangleLayer(
        pos=(85, 35),
        size=(60, 60),
        color=(48, 50, 55),
        radius=-30,
    ),
    WebImageLayer(
        pos=(15, 130),
        resize=(80, 80),
        url=Variable('avatar_url'),
    ),
    RectangleLayer(
        pos=(15, 130),
        size=(80, 80),
        color=(48, 50, 55),
        radius=-40,
    ),
    TextLayer(
        pos=(110, 170),
        align_y='center',
        font='bold',
        font_size=42,
        text=Variable('name'),
        color=(255, 255, 255),
        max_size=(460, 50)
    ),
])''')


DEFAULT_GUILD_SETTINGS = {
    'NEW_USER_LEVEL': Setting(
        value=1.0,
        description='New users will be set this level (you can use floats to set the relative xp, e.g. 3.5 will '
                    'assign Level 3 and 60 xp)',
        itype='float',
        categories=['Levelsystem']
    ),
    'NEW_USER_XP_MULTIPLIER': Setting(
        value=1.0,
        description='The default xp multiplier for new users',
        itype='float',
        categories=['Levelsystem']
    ),
    'MESSAGE_XP': Setting(
        value=0.2,
        description='The base-xp a user receives for sending a message',
        itype='float',
        categories=['Levelsystem']
    ),
    'VOICE_XP_PER_MINUTE': Setting(
        value=2.0,
        description='The base-xp a user receives per minute for being in a voice channel (AFK-channel does not give xp)',
        itype='float',
        categories=['Levelsystem']
    ),
    'BOOST_EXPIRES_DAYS': Setting(
        value=7.0,
        description='Time period after which a boost expires (in days | you can use floats to define more accurate '
                    'time periods, e.g 6.5 will set a 6 days and 12 hours expiration length)',
        itype='float',
        categories=['Boost']
    ),
    'BOOST_ADD_XP_MULTIPLIER': Setting(
        value=0.25,
        description='Configures the xp-multiplier of the >boost command',
        itype='float',
        categories=['Boost']
    ),
    'SEND_WELCOME_IMAGE': Setting(
        value=True,
        description='Enables/disables the welcome image sent by the bot via DM when a new user joins',
        itype='bool'
    ),
    'PROMO_CHANNEL_ID': Setting(
        value='',
        description='Sets one promo channel, in which users can enter promo codes (leave empty for no promo feature)',
        itype='string',
        categories=['Promo']
    ),
    'PROMO_CODE_LENGTH': Setting(
        value=6,
        description='Length of generated promo codes',
        itype='int',
        categories=['Promo']
    ),
    'PROMO_CODE_EXPIRES_HOURS': Setting(
        value=24.0,
        description='Time period after which a promo code expires (in hours | you can use floats to define more '
                    'accurate time periods, e.g 6.5 will set a 6 hours and 30 minutes expiration length)',
        itype='float',
        categories=['Promo']
    ),
    'PROMO_BOOST_EXPIRES_DAYS': Setting(
        value=7.0,
        description='Time period after which the promo xp-boost expires (in days | you can use floats to define more '
                    'accurate time periods, e.g 6.5 will set a 6 days and 12 hours expiration length)',
        itype='float',
        categories=['Promo']
    ),
    'PROMO_BOOST_ADD_XP_MULTIPLIER': Setting(
        value=2.0,
        description='Configures the xp-multiplier awarded to the user who created and distributed their promo code',
        itype='float',
        categories=['Promo']
    ),
    'PROMO_USER_SET_LEVEL': Setting(
        value=2.0,
        description='Configures the level reward given to the new user who entered someone elses promo code (again, '
                    'you can use a float)',
        itype='float',
        categories=['Promo']
    ),
    'COIN_FLIP_AUDIO_CHANCE': Setting(
        value=0.01,
        description='Set the chance at which the bot will join a voice channel and play an audio track for the '
                    'coinflip command (a float as percentage, e.g. 0.4 equals 40%)',
        itype='float'
    ),
    'COMMAND_NOT_FOUND_RESPONSES': Setting(
        value=[
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
        description='Set entire list of available response choices the bot replies with, if a unknown command was used',
        itype='list'
    ),
    'MISSING_PERMISSIONS_RESPONSES': Setting(
        value=[
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
        description='Set entire list of available response choices the bot replies with, if a user entered a command '
                    'without permission',
        itype='list'
    ),
    'PROFILE_IMAGE': Setting(
        value=profile_image,
        description='Template to create the profile image upon',
        itype='text',
        categories=['Image']
    ),
    'LEVEL_UP_IMAGE': Setting(
        value=level_up_image,
        description='Template to create a level up image upon',
        itype='text',
        categories=['Image']
    ),
    'RANK_UP_IMAGE': Setting(
        value=rank_up_image,
        description='Template to create a rank up image upon',
        itype='text',
        categories=['Image']
    ),
    'RANKING_IMAGE': Setting(
        value=ranking_image,
        description='Template to create a ranking image upon',
        itype='text',
        categories=['Image']
    ),
    'WELCOME_IMAGE': Setting(
        value=welcome_image,
        description='Template to create a welcome image upon',
        itype='text',
        categories=['Image']
    ),
}
