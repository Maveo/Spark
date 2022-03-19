from imagestack import ImageStackResolveString

from helpers.settings_manager import Setting


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

    # Progressbar BG
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


SETTINGS = {
    'NEW_USER_LEVEL': Setting(
        value=1.0,
        description='New users will be set this level (you can use floats to set the relative xp, e.g. 3.5 will '
                    'assign Level 3 and 60 xp)',
        itype='float',
        categories=['Levelsystem']
    ),
    'ALLOW_BOT_LEVELING': Setting(
        value=False,
        description='if bots should be allowed to level',
        itype='bool',
        categories=['Levelsystem']
    ),
    'BASE_XP_MULTIPLIER': Setting(
        value=1.0,
        description='the base xp multiplier always applied',
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
        description='The base-xp a user receives per minute for'
                    'being in a voice channel (AFK-channel does not give xp)',
        itype='float',
        categories=['Levelsystem']
    ),
    'PROFILE_IMAGE': Setting(
        value=profile_image,
        description='Template to create the profile image upon',
        itype='text',
        categories=['Image'],
        preview_call='profile-image'
    ),
    'LEVEL_UP_IMAGE': Setting(
        value=level_up_image,
        description='Template to create a level up image upon',
        itype='text',
        categories=['Image'],
        preview_call='level-up-image'
    ),
    'RANK_UP_IMAGE': Setting(
        value=rank_up_image,
        description='Template to create a rank up image upon',
        itype='text',
        categories=['Image'],
        preview_call='rank-up-image'
    ),
    'RANKING_IMAGE': Setting(
        value=ranking_image,
        description='Template to create a ranking image upon',
        itype='text',
        categories=['Image'],
        preview_call='ranking-image'
    ),
    'LEADERBOARD_AMOUNT': Setting(
        value=10,
        description='the amount of users in the leaderboard',
        itype='int',
        categories=['Levelsystem']
    ),
}
