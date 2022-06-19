import base64

import discord
from fastapi import Body

from helpers.exceptions import WrongInputException
from helpers.module_hook_manager import INVENTORY_ITEM_ACTION_HOOK
from helpers.module_pages import has_permissions
from helpers.tools import make_linear_gradient
from webserver import Page

from typing import TYPE_CHECKING, Any, Union

from webserver.responses import BytesFileResponse

if TYPE_CHECKING:
    from . import InventoryModule


@has_permissions(administrator=True)
async def edit_rarity(module: 'InventoryModule',
                      guild: discord.Guild,
                      member: discord.Member,
                      rarity: Any = Body(embed=True)
                      ):
    await module.edit_rarity(guild, rarity)
    return {'msg': 'success'}


@has_permissions(administrator=True)
async def remove_rarity(module: 'InventoryModule',
                        guild: discord.Guild,
                        member: discord.Member,
                        rarity_id: str = Body(embed=True),
                        ):
    module.bot.db.remove_rarity(guild.id, str(rarity_id))
    return {'msg': 'success'}


@has_permissions(administrator=True)
async def set_rarity_order(module: 'InventoryModule',
                           guild: discord.Guild,
                           member: discord.Member,
                           rarity_order: Any = Body(embed=True)):
    module.bot.db.set_rarity_order(guild.id, rarity_order)
    return {'msg': 'success'}


@has_permissions(administrator=True)
async def get_rarities(module: 'InventoryModule',
                       guild: discord.Guild,
                       member: discord.Member):
    rarities = await module.get_rarities(guild)
    for key, rarity in rarities.items():
        rarities[key]['image'] = base64.b64encode((await module.create_rarity_image(guild.id, {
            'id': rarity['id'],
            'name': rarity['name'],
            'foreground_color': make_linear_gradient(rarity['foreground_color']),
            'background_color': make_linear_gradient(rarity['background_color']),
        })).fp.read()).decode('utf-8')

    return {
        'msg': 'success',
        'rarities': rarities,
    }


async def rarity_image(module: 'InventoryModule',
                       guild: discord.Guild,
                       member: discord.Member,
                       preview: Union[str, None] = Body(default=None, embed=True),
                       ):
    rarity = {
        'id': '-1',
        'name': 'Legendary',
        'foreground_color': make_linear_gradient('(255,255,255)'),
        'background_color': make_linear_gradient('LinearGradientColor((241, 110, 24),(255, 222, 7),1)'),
    }

    if preview is None:
        img = await module.create_rarity_image(guild.id, rarity)
        return BytesFileResponse(
            img.fp,
            filename=img.filename,
            media_type='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'RARITY_IMAGE', preview)
    except:
        raise WrongInputException(detail='setting preview not correct')

    img = await module.create_rarity_image_by_template(rarity, preview)
    return BytesFileResponse(
        img.fp,
        filename=img.filename,
        media_type='image/png'
    )


async def inventory_image(module: 'InventoryModule',
                          guild: discord.Guild,
                          member: discord.Member,
                          preview: Union[str, None] = Body(default=None, embed=True),
                          ):
    inventory = await module.get_inventory(member)

    if preview is None:
        img = await module.create_inventory_image(guild.id, inventory)
        return BytesFileResponse(
            img.fp,
            filename=img.filename,
            media_type='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'RARITY_IMAGE', preview)
    except:
        raise WrongInputException(detail='setting preview not correct')

    img = await module.create_inventory_image_by_template(inventory, preview)
    return BytesFileResponse(
        img.fp,
        filename=img.filename,
        media_type='image/png'
    )


@has_permissions(administrator=True)
async def get_item_action_options(module: 'InventoryModule',
                                  guild: discord.Guild,
                                  member: discord.Member):
    return {
        'msg': 'success',
        'actions': {action_id: {
            'name': action['name'],
            'options': {k: {
                'type': v['type'],
                'description': v['description']
            }
                for k, v in action['options'].items()}}
            for action_id, action in
            module.bot.module_manager.hooks.get(guild.id, INVENTORY_ITEM_ACTION_HOOK).items()}
    }


@has_permissions(administrator=True)
async def edit_item_type(module: 'InventoryModule',
                         guild: discord.Guild,
                         member: discord.Member,
                         item_type: Any = Body(embed=True),
                         ):
    await module.edit_item_type(guild, item_type)
    return {
        'msg': 'success',
    }


@has_permissions(administrator=True)
async def get_item_types(module: 'InventoryModule',
                         guild: discord.Guild,
                         member: discord.Member):
    return {
        'msg': 'success',
        'item_types': module.bot.db.get_item_types(guild.id),
    }


@has_permissions(administrator=True)
async def remove_item_type(module: 'InventoryModule',
                           guild: discord.Guild,
                           member: discord.Member,
                           item_type_id: int = Body(embed=True)
                           ):
    module.bot.db.remove_item_type(guild.id, int(item_type_id))
    return {'msg': 'success'}


async def get_inventory(module: 'InventoryModule',
                        guild: discord.Guild,
                        member: discord.Member):
    return {
        'msg': 'success',
        'inventory': await module.get_inventory(member)
    }


async def use_item(module: 'InventoryModule',
                   guild: discord.Guild,
                   member: discord.Member,
                   item_type_id: int = Body(embed=True),
                   amount: float = Body(embed=True),
                   ):
    await module.use_item(member, int(item_type_id), float(amount))
    return {
        'msg': 'success',
    }


API_PAGES = [
    Page(path='inventory', view_func=get_inventory),
    Page(path='use-item', view_func=use_item, methods=['POST']),
    Page(path='edit-rarity', view_func=edit_rarity, methods=['POST']),
    Page(path='remove-rarity', view_func=remove_rarity, methods=['POST']),
    Page(path='set-rarity-order', view_func=set_rarity_order, methods=['POST']),
    Page(path='rarities', view_func=get_rarities),
    Page(path='rarity-image', view_func=rarity_image, methods=['POST']),
    Page(path='inventory-image', view_func=inventory_image, methods=['POST']),
    Page(path='item-action-options', view_func=get_item_action_options),
    Page(path='item-types', view_func=get_item_types),
    Page(path='edit-item-type', view_func=edit_item_type, methods=['POST']),
    Page(path='remove-item-type', view_func=remove_item_type, methods=['POST'])
]
