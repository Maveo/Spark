from imagestack_svg.imageresolve import ImageStackResolveString

from helpers.settings_manager import Setting


profile_image = ImageStackResolveString('''<defs>
<linearGradient id="color1">
	<stop offset="0%" stop-color="rgb({{ color[0] / 2 }}, {{ color[1] / 2 }}, {{ color[2] / 2 }})" />
	<stop offset="100%" stop-color="rgb{{ color[0:3] }}" />
</linearGradient>
<linearGradient id="color2">
	<stop offset="0%" stop-color="rgb(241, 110, 24)" />
	<stop offset="100%" stop-color="rgb(255, 222, 7)" />
</linearGradient>
</defs>
<rect x="0" y="0" width="600" height="150" rx="20" ry="20" fill="rgb(48, 50, 55)" />
<image x="15" y="15" width="120" height="120" xlink:href="{{ avatar_url | web_image }}"/>
<path fill-rule="evenodd" fill="rgb(48, 50, 55)" d="m15,15 l120,0 l0,120 l-120,0 l0,-120 m60,0 a60,60 0 0 0 -60 60 a60,60 0 0 0 60 60 a60,60 0 0 0 60 -60 a60,60 0 0 0 -60 -60" />
<image id="userEmoji" x="147" y="15" width="40" height="40" xlink:href="{{ member.top_role.name[0] | emoji }}"/>
<rect x="150" y="115" width="430" height="20" rx="10" ry="10" fill="rgb(87, 87, 87)" />
<rect x="150" y="115" width="{{ xp_percentage * 430 }}" height="20" rx="10" ry="10" fill="url(#color2)" />
<text x="200" y="48" font-family="Product Sans" font-size="35" fill="rgb{{ color }}">{{ name }}</text>
<text id="userTitle" x="150" y="76" font-family="Product Sans" font-size="20" fill="white"></text>
<text x="150" y="108" font-family="Product Sans" font-size="22" fill="rgb(103, 103, 103)">Lvl.</text>
<text x="188" y="108" font-family="Product Sans" font-size="28" fill="rgb(255, 255, 255)">{{lvl}}</text>
<text x="578" y="48" text-anchor="end" font-family="Product Sans" font-weight="bold" font-size="35" fill="rgb{{ color }}">#{{rank}}</text>
{% if xp_multiplier > 1 %}
<text x="580" y="86" text-anchor="end" font-family="Product Sans" font-size="20" fill="rgb(47, 172, 102)">{{"%.2f"|format(xp_multiplier)}}x</text>
{% endif %}
{% if xp_multiplier < 1 %}
{% if xp_multiplier > 0 %}
<text x="580" y="86" text-anchor="end" font-family="Product Sans" font-size="20" fill="rgb(255, 128, 0)">{{"%.2f"|format(xp_multiplier)}}x</text>
{% endif %}
{% if xp_multiplier < 0 %}
<text x="580" y="86" text-anchor="end" font-family="Product Sans" font-size="20" fill="rgb(220, 20, 60)">{{"%.2f"|format(xp_multiplier)}}x</text>
{% endif %}
{% endif %}
<text x="580" y="108" text-anchor="end" font-family="Product Sans" font-size="18" fill="rgb(170, 170, 170)">{{ xp }} / {{ max_xp }} XP</text>
''')


SETTINGS = {
    'PROFILE_IMAGE': Setting(
        value=profile_image,
        description='Template to create the profile image upon',
        itype='text',
        categories=['Image'],
        preview_call='profile-image'
    ),
}
