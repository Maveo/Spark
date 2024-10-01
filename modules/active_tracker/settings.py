from imagestack_svg.imageresolve import ImageStackResolveString

from helpers.settings_manager import Setting

activity_image = ImageStackResolveString('''<defs>
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
<text x="310" y="163" font-family="Product Sans" font-weight="bold" font-size="100" fill="rgb(255, 255, 255)">Wall of Shame</text>
<text x="90" y="300" font-family="Product Sans" font-size="65" fill="rgb(87, 87, 87)">Name</text>
<text x="1150" y="300" text-anchor="end" font-family="Product Sans" font-size="35" fill="rgb(87, 87, 87)">Time Muted (last {{"%0d" | format(current_duration / 3600)}} hours)</text>
<rect x="37" y="320" width="1100" height="{{ (users | length) * 85 + 410 - 355 }}" rx="55" ry="55" fill="rgb(57, 59, 65)" />
<rect x="950" y="320" width="200" height="{{ (users | length) * 85 + 410 - 355 }}" rx="45" ry="45" fill="url(#color2)" />
{% for user in users %}
	<text x="135" y="{{ (loop.index * 85) + 325 }}" text-anchor="middle" font-family="Product Sans" font-weight="bold" font-size="60" fill="rgb(255, 255, 255)">#{{ user.rank }}</text>
	<image x="240" y="{{ (loop.index * 85) + 272 }}" width="60" height="60" xlink:href="{{ user.member.top_role.name[0] | emoji }}"/>
	<text x="323" y="{{ (loop.index * 85) + 325 }}" font-family="Product Sans" font-size="60" fill="rgb(255, 255, 255)">{{ user.name }}</text>
	<text x="1055" y="{{ (loop.index * 85) + 325 }}" text-anchor="middle" font-family="Product Sans" font-size="60" fill="rgb(29, 29, 29)">{{ "%d" | format(user.interval_muted_time / 60) }} m</text>
{% endfor %}''')

SETTINGS = {
    'ACTIVITY_IMAGE_INTERVAL_CHANNEL': Setting(
        value='',
        description='Sets the channel, in which the activity image will be send periodically',
        itype='string',
        categories=['Activity']
    ),
    'ACTIVITY_IMAGE_INTERVAL_HOURS': Setting(
        value=24.0,
        description='Sets the interval in hours between activity messages',
        itype='float',
        categories=['Activity']
    ),
    'ACTIVITY_IMAGE_INTERVAL_START_TIME': Setting(
        value=22.0,
        description='Sets the start time of the interval of activity messages in hours',
        itype='float',
        categories=['Activity']
    ),
    'ACTIVITY_LEADERBOARD_AMOUNT': Setting(
        value=10,
        description='the amount of users in the wall of shame',
        itype='int',
        categories=['Activity']
    ),
    'ALLOW_BOT_ACTIVE_TRACKING': Setting(
        value=False,
        description='if bots should be allowed to be actively tracked',
        itype='bool',
        categories=['Activity']
    ),
    'ACTIVITY_IMAGE': Setting(
        value=activity_image,
        description='Template to create a activity image upon',
        itype='text',
        categories=['Activity', 'Image'],
        preview_call='activity-image'
    ),
}
