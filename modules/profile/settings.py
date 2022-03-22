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


SETTINGS = {
    'PROFILE_IMAGE': Setting(
        value=profile_image,
        description='Template to create the profile image upon',
        itype='text',
        categories=['Image'],
        preview_call='profile-image'
    ),
}
