import time

import discord
from flask import jsonify, request

from helpers.exceptions import WrongInputException
from helpers.module_pages import has_permissions
from helpers.tools import make_linear_gradient
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import WheelspinModule


async def get_wheelspin(module: 'WheelspinModule',
                        guild: discord.Guild,
                        member: discord.Member):
    wheelspin = []
    for x in module.bot.db.get_wheelspin(guild.id):
        foreground_color_id = 'fgcolor{}'.format(x.WheelspinProbability.id)
        foreground_color = make_linear_gradient(x.InventoryRarity.foreground_color)
        background_color_id = 'bgcolor{}'.format(x.WheelspinProbability.id)
        background_color = make_linear_gradient(x.InventoryRarity.background_color)
        wheelspin.append({
            'id': x.WheelspinProbability.id,
            'name': x.InventoryItemType.name,
            'foreground_color_id': foreground_color_id,
            'foreground_color_svg': foreground_color.svg_color_definition_with_id(foreground_color_id),
            'foreground_color_html': foreground_color.html_color(),
            'background_color_id': background_color_id,
            'background_color_svg': background_color.svg_color_definition_with_id(background_color_id),
            'background_color_html': background_color.html_color(),
            'sound': x.WheelspinProbability.sound
        })
    return jsonify({
        'msg': 'success',
        'wheelspin': wheelspin
    }), 200


async def can_wheelspin(module: 'WheelspinModule',
                        guild: discord.Guild,
                        member: discord.Member):
    available = module.bot.db.get_wheelspin_available(guild.id, member.id)
    free_wheelspin = 0
    if available is not None:
        free_wheelspin = - time.time() + available.last_free + \
                         (module.bot.module_manager.settings.get(guild.id, 'WHEELSPIN_FREE_RESET_HOURS') * 60 * 60)
    return jsonify({
        'msg': 'success',
        'wheelspins_available': 0 if available is None else available.amount,
        'free_wheelspin_in': free_wheelspin
    }), 200


async def spin_wheel(module: 'WheelspinModule',
                     guild: discord.Guild,
                     member: discord.Member):

    return jsonify({
        'msg': 'success',
        'result': (await module.spin_wheel(member)).WheelspinProbability.id,
    }), 200


@has_permissions(administrator=True)
async def get_wheelspin_admin(module: 'WheelspinModule',
                              guild: discord.Guild,
                              member: discord.Member):
    return jsonify({'msg': 'success',
                    'wheelspin': list(map(lambda x: x.WheelspinProbability, module.bot.db.get_wheelspin(guild.id)))}), \
           200


@has_permissions(administrator=True)
async def set_wheelspin(module: 'WheelspinModule',
                        guild: discord.Guild,
                        member: discord.Member):
    json = request.get_json()
    if json is None or 'wheelspin' not in json:
        raise WrongInputException('wheelspin not provided')
    await module.set_wheelspin(guild, json['wheelspin'])
    return jsonify({'msg': 'success'}), 200


API_PAGES = [
    Page(path='get-wheelspin', view_func=get_wheelspin),
    Page(path='spin-wheel', view_func=spin_wheel, methods=['POST']),
    Page(path='can-wheelspin', view_func=can_wheelspin),
    Page(path='get-wheelspin-admin', view_func=get_wheelspin_admin),
    Page(path='set-wheelspin', view_func=set_wheelspin, methods=['POST']),
]
