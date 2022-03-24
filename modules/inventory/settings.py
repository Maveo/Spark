from imagestack import ImageStackResolveString

from helpers.settings_manager import Setting

rarity_image = ImageStackResolveString('''ImageStack([
    TextLayer(
        pos=(0, 0),
        font='regular',
        font_size=22,
        text=Variable('name'),
        background_color=Variable('background_color'),
        color=Variable('foreground_color'),
        background_padding=(5, 5),
        border_radius=15,
    )
])''')


SETTINGS = {
    'RARITY_IMAGE': Setting(
        value=rarity_image,
        description='The image for rarities',
        categories=['Image', 'Inventory'],
        itype='text',
        preview_call='rarity-image'
    ),
}
