import base64

import discord
from flask import jsonify, request, send_file
import json as jsone

from helpers import tools
from helpers.exceptions import WrongInputException
from helpers.module_hook_manager import INVENTORY_ITEM_ACTION_HOOK
from helpers.module_pages import has_permissions
from helpers.tools import make_linear_gradient
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import InventoryModule


@has_permissions(administrator=True)
async def add_rarity(module: 'InventoryModule',
                     guild: discord.Guild,
                     member: discord.Member):
    json = request.get_json()
    if json is None or 'rarity_name' not in json \
            or 'rarity_foreground_color' not in json or 'rarity_background_color' not in json:
        raise WrongInputException('name or color not provided')
    await module.add_rarity(guild,
                            json['rarity_name'],
                            json['rarity_foreground_color'],
                            json['rarity_background_color'])
    return jsonify({'msg': 'success'}), 200


@has_permissions(administrator=True)
async def remove_rarity(module: 'InventoryModule',
                        guild: discord.Guild,
                        member: discord.Member):
    json = request.get_json()
    if json is None or 'rarity_id' not in json:
        raise WrongInputException('rarity_id not provided')
    module.bot.db.remove_rarity(guild.id, json['rarity_id'])
    return jsonify({'msg': 'success'}), 200


@has_permissions(administrator=True)
async def set_rarity_order(module: 'InventoryModule',
                           guild: discord.Guild,
                           member: discord.Member):
    json = request.get_json()
    if json is None or 'rarity_order' not in json:
        raise WrongInputException('rarity_order not provided')
    module.bot.db.set_rarity_order(guild.id, json['rarity_order'])
    return jsonify({'msg': 'success'}), 200


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

    return jsonify({
        'msg': 'success',
        'rarities': rarities,
    }), 200


async def rarity_image(module: 'InventoryModule',
                       guild: discord.Guild,
                       member: discord.Member):
    json = request.get_json()

    rarity = {
        'id': '-1',
        'name': 'Legendary',
        'foreground_color': make_linear_gradient('(255,255,255)'),
        'background_color': make_linear_gradient('LinearGradientColor((241, 110, 24),(255, 222, 7),1)'),
    }

    if json is None or 'preview' not in json:
        img = await module.create_rarity_image(guild.id, rarity)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'RARITY_IMAGE', json['preview'])
    except:
        raise WrongInputException('setting preview not correct')

    img = await module.create_rarity_image_by_template(rarity, preview)
    return send_file(
        img.fp,
        attachment_filename=img.filename,
        mimetype='image/png'
    )


@has_permissions(administrator=True)
async def get_item_action_options(module: 'InventoryModule',
                                  guild: discord.Guild,
                                  member: discord.Member):
    return jsonify({
        'msg': 'success',
        'actions': {action_id: {
            'name': action['name'],
            'options': {k: {
                'type': v['type'].__name__,
                'description': v['description']
            }
                for k, v in action['options'].items()}}
            for action_id, action in
            module.bot.module_manager.hooks.get(guild.id, INVENTORY_ITEM_ACTION_HOOK).items()}
    }), 200


@has_permissions(administrator=True)
async def create_item_type(module: 'InventoryModule',
                           guild: discord.Guild,
                           member: discord.Member):
    json = request.get_json()
    if json is None:
        raise WrongInputException('missing parameters')
    try:
        actions = module.bot.module_manager.hooks.get(guild.id, INVENTORY_ITEM_ACTION_HOOK)
        if json['item_action'] == '':
            action_options_json = '{}'
        elif json['item_action'] not in actions:
            raise WrongInputException('action "{}" not found'.format(json['item_action']))
        else:
            action_options_json = jsone.dumps({k: json['item_action_options'][k]['value']
                                               for k, v in actions[json['item_action']]['options'].items()})
        module.bot.db.add_inventory_item_type(
            guild.id,
            json['item_name'],
            json['item_rarity'],
            json['item_always_visible'],
            json['item_tradable'],
            json['item_useable'],
            json['item_expiration'],
            json['item_action'],
            action_options_json,
        )
        return jsonify({
            'msg': 'success',
        }), 200
    except KeyError:
        raise WrongInputException('missing parameter')


@has_permissions(administrator=True)
async def get_item_types(module: 'InventoryModule',
                         guild: discord.Guild,
                         member: discord.Member):
    return jsonify({
        'msg': 'success',
        'item_types': module.bot.db.get_item_types(guild.id),
    }), 200


@has_permissions(administrator=True)
async def remove_item_type(module: 'InventoryModule',
                           guild: discord.Guild,
                           member: discord.Member):
    json = request.get_json()
    if json is None or 'item_type_id' not in json:
        raise WrongInputException('item_type_id not provided')
    module.bot.db.remove_item_type(guild.id, json['item_type_id'])
    return jsonify({'msg': 'success'}), 200


API_PAGES = [
    Page(path='add-rarity', view_func=add_rarity, methods=['POST']),
    Page(path='remove-rarity', view_func=remove_rarity, methods=['POST']),
    Page(path='set-rarity-order', view_func=set_rarity_order, methods=['POST']),
    Page(path='rarities', view_func=get_rarities),
    Page(path='rarity-image', view_func=rarity_image, methods=['POST']),
    Page(path='item-action-options', view_func=get_item_action_options),
    Page(path='item-types', view_func=get_item_types),
    Page(path='create-item-type', view_func=create_item_type, methods=['POST']),
    Page(path='remove-item-type', view_func=remove_item_type, methods=['POST'])
]
