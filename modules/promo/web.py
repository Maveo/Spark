import asyncio
import time

import discord
from flask import jsonify, request

from helpers.exceptions import WrongInputException
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import PromoModule


async def get_promo_code(module: 'PromoModule',
                         guild: discord.Guild,
                         member: discord.Member):
    return jsonify({'promo_code': await module.create_promo_code(member)}), 200


async def redeem_promo_code(module: 'PromoModule',
                            guild: discord.Guild,
                            member: discord.Member):
    if not await module.can_redeem_promo_code(member):
        raise WrongInputException('promo code usage forbidden')
    json = request.get_json()
    if json is None or 'promo_code' not in json:
        raise WrongInputException('promo_code not provided')
    asyncio.run_coroutine_threadsafe(
        module.redeem_promo_code(member, json['promo_code'], time.time()), module.bot.bot.loop).result()
    return jsonify({'msg': 'success'}), 200


API_PAGES = [
    Page(path='promo', view_func=get_promo_code, methods=['GET']),
    Page(path='redeem', view_func=redeem_promo_code, methods=['POST']),
]
