from imagestack_svg.imageresolve import ImageStackResolveString

from helpers.settings_manager import Setting

rarity_image = ImageStackResolveString('''<defs>
<linearGradient id="bgcolor">
	<stop offset="0%" stop-color="rgb{{background_color[0]}}" />
	<stop offset="100%" stop-color="rgb{{background_color[1]}}" />
</linearGradient>
<linearGradient id="fgcolor">
	<stop offset="0%" stop-color="rgb{{foreground_color[0]}}" />
	<stop offset="100%" stop-color="rgb{{foreground_color[1]}}" />
</linearGradient>
</defs>
<rect width="250" height="40" rx="10" ry="10" fill="url(#bgcolor)" />
<text x="125" y="27" text-anchor="middle" font-family="Product Sans" font-weight="bold" font-size="25" fill="url(#fgcolor)" >{{ name}}</text>
''')

SETTINGS = {
    'RARITY_IMAGE': Setting(
        value=rarity_image,
        description='The image for rarities',
        categories=['Image', 'Inventory'],
        itype='text',
        preview_call='rarity-image'
    ),
}
