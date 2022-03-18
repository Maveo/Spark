from imagestack import ImageStackResolveString

from helpers.settings_manager import Setting


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

SETTINGS = {
    'MISSING_PERMISSIONS_RESPONSES': Setting(
        value=['Missing permission', 'You are not allowed'],
        description='Set entire list of available response choices the bot replies with, if a user entered a command '
                    'without permission',
        itype='list'
    ),
    'WELCOME_IMAGE': Setting(
        value=welcome_image,
        description='Template to create a welcome image upon',
        itype='text',
        categories=['Image'],
        preview_call='welcome-image'
    ),
    'SEND_WELCOME_IMAGE': Setting(
        value=True,
        description='Enables/disables the welcome image sent by the bot via DM when a new user joins',
        itype='bool',
        categories=['Image']
    ),
}
