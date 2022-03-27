from imagestack_svg.imageresolve import ImageStackResolveString

from helpers.settings_manager import Setting


welcome_image = ImageStackResolveString('''<image x="0" y="0" width="600" height="324" xlink:href="{{'https://raw.githubusercontent.com/skillor/Spark/v1.3.1/images/welcome_template.png' | web_image}}"/>
<image x="85" y="35" width="60" height="60" xlink:href="{{ guild_icon_url | web_image}}"/>
<path fill-rule="evenodd" fill="rgb(48, 50, 55)" d="m85,35 l60,0 l0,60 l-60,0 l0,-60 m30,0 a30,30 0 0 0 -30 30 a30,30 0 0 0 30 30 a30,30 0 0 0 30 -30 a30,30 0 0 0 -30 -30" />
<image x="15" y="130" width="80" height="80" xlink:href="{{ avatar_url | web_image}}"/>
<path fill-rule="evenodd" fill="rgb(48, 50, 55)" d="m15,130 l80,0 l0,80 l-80,0 l0,-80 m40,0 a40,40 0 0 0 -40 40 a40,40 0 0 0 40 40 a40,40 0 0 0 40 -40 a40,40 0 0 0 -40 -40" />
<text x="110" y="185" font-family="Product Sans" font-weight="bold" font-size="42" fill="rgb(255, 255, 255)">{{ name }}</text>''')

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
