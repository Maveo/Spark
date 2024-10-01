from imagestack_svg.imageresolve import ImageStackResolveString

from helpers.settings_manager import Setting

level_up_image = ImageStackResolveString('''<defs>
<linearGradient id="color1">
	<stop offset="0%" stop-color="rgb({{ color[0] / 2 }}, {{ color[1] / 2 }}, {{ color[2] / 2 }})" />
	<stop offset="100%" stop-color="rgb{{ color[0:3] }}" />
</linearGradient>
<linearGradient id="color2">
	<stop offset="0%" stop-color="rgb{{ color[0:3] }}" stop-opacity="0" />
	<stop offset="100%" stop-color="rgb{{ color[0:3] }}" />
</linearGradient>
</defs>
<rect x="0" y="0" width="200" height="100" rx="20" ry="20" fill="rgb(48, 50, 55)" />
<rect x="2" y="0" width="196" height="100" rx="20" ry="20" stroke-width="3" fill="none" stroke="url(#color1)" />
<text x="57" y="30" font-family="Product Sans" font-weight="bold" font-size="22" fill="url(#color1)">LEVELUP</text>
<image x="58" y="70" width="16" height="16" xlink:href="{{ member.top_role.name[0] | emoji }}"/>
<image x="125" y="70" width="16" height="16" xlink:href="{{ member.top_role.name[0] | emoji }}"/>
<rect x="82" y="77" width="34" height="4" rx="2" ry="2" fill="url(#color2)" />
<text x="53" y="82" text-anchor="end" font-family="Product Sans" font-size="12" fill="rgb{{ color[0:3] }}">Lvl. {{old_lvl}}</text>
<text x="145" y="82" font-family="Product Sans" font-size="12" fill="rgb{{ color[0:3] }}">Lvl. {{new_lvl}}</text>
<text x="100" y="55" text-anchor="middle" font-family="Product Sans" font-size="13" fill="rgb(255, 255, 255)">{{name}}</text>''')

rank_up_image = ImageStackResolveString('''<defs>
<linearGradient id="color1">
	<stop offset="0%" stop-color="rgb{{old_color}}" />
	<stop offset="100%" stop-color="rgb{{new_color}}" />
</linearGradient>
</defs>
<rect x="0" y="0" width="200" height="100" rx="20" ry="20" fill="rgb(48, 50, 55)" />
<rect x="2" y="0" width="196" height="100" rx="20" ry="20" stroke-width="3" fill="none" stroke="url(#color1)" />
<text x="57" y="30" font-family="Product Sans" font-weight="bold" font-size="22" fill="url(#color1)">RANKUP</text>
<image x="58" y="70" width="16" height="16" xlink:href="{{ old_role.name[0] | emoji }}"/>
<image x="125" y="70" width="16" height="16" xlink:href="{{ new_role.name[0] | emoji }}"/>
<rect x="82" y="77" width="34" height="4" rx="2" ry="2" fill="url(#color1)" />
<text x="53" y="82" text-anchor="end" font-family="Product Sans" font-size="12" fill="rgb{{ old_color }}">Lvl. {{old_lvl}}</text>
<text x="145" y="82" font-family="Product Sans" font-size="12" fill="rgb{{ new_color }}">Lvl. {{new_lvl}}</text>
<text x="100" y="55" text-anchor="middle" font-family="Product Sans" font-size="13" fill="rgb(255, 255, 255)">{{name}}</text>''')

ranking_image = ImageStackResolveString('''<defs>
<linearGradient id="color1">
	<stop offset="0%" stop-color="rgb(217, 142, 76)" />
	<stop offset="100%" stop-color="rgb(255, 222, 7)" />
</linearGradient>
<linearGradient id="color2">
	<stop offset="0%" stop-color="rgb(254, 214, 130)" />
	<stop offset="100%" stop-color="rgb(232, 177, 49)" />
</linearGradient>
</defs>
<rect x="0" y="0" width="1200" height="{{ (users | length) * 85 + 410 }}" rx="20" ry="20" fill="rgb(48, 50, 55)" />
<rect x="30" y="40" width="1140" height="180" rx="45" ry="45" fill="none" stroke="url(#color1)" stroke-width="10" />
<text x="310" y="163" font-family="Product Sans" font-weight="bold" font-size="100" fill="rgb(255, 255, 255)">Leaderboard</text>
<text x="90" y="300" font-family="Product Sans" font-size="65" fill="rgb(87, 87, 87)">Name</text>
<text x="1025" y="300" font-family="Product Sans" font-size="65" fill="rgb(87, 87, 87)">Lvl.</text>
<rect x="37" y="320" width="1100" height="{{ (users | length) * 85 + 410 - 355 }}" rx="55" ry="55" fill="rgb(57, 59, 65)" />
<rect x="978" y="320" width="185" height="{{ (users | length) * 85 + 410 - 355 }}" rx="45" ry="45" fill="url(#color2)" />
{% for user in users %}
	<text x="135" y="{{ (loop.index * 85) + 325 }}" text-anchor="middle" font-family="Product Sans" font-weight="bold" font-size="60" fill="rgb(255, 255, 255)">#{{ user.rank }}</text>
	<image x="240" y="{{ (loop.index * 85) + 272 }}" width="60" height="60" xlink:href="{{ user.member.top_role.name[0] | emoji }}"/>
	<text x="323" y="{{ (loop.index * 85) + 325 }}" font-family="Product Sans" font-size="60" fill="rgb(255, 255, 255)">{{ user.name }}</text>
	<text x="1069" y="{{ (loop.index * 85) + 325 }}" text-anchor="middle" font-family="Product Sans" font-size="60" fill="rgb(29, 29, 29)">{{ user.lvl }}</text>
{% endfor %}''')

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
    'SERVER_BOOSTER_ADD_XP_MULTIPLIER': Setting(
        value=2.0,
        description='the xp multiplier which is added for server boosters',
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
        categories=['Levelsystem', 'Image'],
        preview_call='level-up-image'
    ),
    'RANK_UP_IMAGE': Setting(
        value=rank_up_image,
        description='Template to create a rank up image upon',
        itype='text',
        categories=['Levelsystem', 'Image'],
        preview_call='rank-up-image'
    ),
    'RANKING_IMAGE': Setting(
        value=ranking_image,
        description='Template to create a ranking image upon',
        itype='text',
        categories=['Levelsystem', 'Image'],
        preview_call='ranking-image'
    ),
    'LEADERBOARD_AMOUNT': Setting(
        value=10,
        description='the amount of users in the leaderboard',
        itype='int',
        categories=['Levelsystem']
    ),
}
