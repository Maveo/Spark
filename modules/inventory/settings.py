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

inventory_image = ImageStackResolveString('''<defs>
<linearGradient id="color1">
	<stop offset="0" stop-color="#d88d4c"/>
	<stop offset="1" stop-color="#ffdd02"/>
</linearGradient>
{% for item in items %}
<linearGradient id="bgcolor{{ loop.index }}">
	<stop offset="0%" stop-color="rgb{{item.rarity_background_color[0]}}" />
	<stop offset="100%" stop-color="rgb{{item.rarity_background_color[1]}}" />
</linearGradient>
<linearGradient id="fgcolor{{ loop.index }}">
	<stop offset="0%" stop-color="rgb{{item.rarity_foreground_color[0]}}" />
	<stop offset="100%" stop-color="rgb{{item.rarity_foreground_color[1]}}" />
</linearGradient>
{% endfor %}
</defs>
<rect width="1400" height="{{ (((items | length + 1) / 2) | int) * 220 + 290 }}" fill="#303237" rx="50" ry="50" />
<rect x="50" y="50" width="1300" height="140" stroke-width="10" rx="40" ry="40" stroke="url(#color1)" fill="none" />
<text x="700" y="150" text-anchor="middle" font-size="100" font-family="Product Sans" font-weight="bold" fill="#ffffff">Inventory</text>
<rect x="50" y="230" width="1300" height="{{ (((items | length + 1) / 2) | int) * 220 + 30 }}" fill="#393b41" rx="50" ry="50" />
{% for item in items %}
<rect x="{{ ((loop.index + 1) % 2) * 620 + 100 }}" y="{{ ((loop.index + 1) / 2) | int * 220 + 50 }}" width="580" height="180" fill="#454951" rx="30" ry="30" />
<text x="{{ ((loop.index + 1) % 2) * 620 + 390 }}" y="{{ ((loop.index + 1) / 2) | int * 220 + 120 }}" text-anchor="middle" width="580" height="180" fill="#ffffff" font-size="50" font-family="Product Sans" font-weight="bold">{{item.item_name}}</text>
<rect x="{{ ((loop.index + 1) % 2) * 620 + 120 }}" y="{{ ((loop.index + 1) / 2) | int * 220 + 160 }}" width="360" height="50" fill="url(#bgcolor{{ loop.index }})" rx="15" ry="15" />
<text x="{{ ((loop.index + 1) % 2) * 620 + 300 }}" y="{{ ((loop.index + 1) / 2) | int * 220 + 194 }}" text-anchor="middle" font-size="30" font-family="Product Sans" fill="url(#fgcolor{{ loop.index }})">{{ item.rarity_name }}</text>
<rect x="{{ ((loop.index + 1) % 2) * 620 + 490 }}" y="{{ ((loop.index + 1) / 2) | int * 220 + 160 }}" width="170" height="50" fill="#303237" rx="15" ry="15" />
<text x="{{ ((loop.index + 1) % 2) * 620 + 575 }}" y="{{ ((loop.index + 1) / 2) | int * 220 + 194 }}" text-anchor="middle" font-size="30" font-family="Product Sans" fill="#ffffff">{{ "{:,g}".format(item.item_amount) }}</text>
{% endfor %}''')

SETTINGS = {
    'RARITY_IMAGE': Setting(
        value=rarity_image,
        description='The image for rarities',
        categories=['Image', 'Inventory'],
        itype='text',
        preview_call='rarity-image'
    ),
    'INVENTORY_IMAGE': Setting(
        value=inventory_image,
        description='The image for the inventory',
        categories=['Image', 'Inventory'],
        itype='text',
        preview_call='inventory-image'
    ),
}
