from imagestack import ImageStackResolveString

from helpers.settings_manager import Setting


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
