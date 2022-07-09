import asyncio
import time

import discord
from fastapi import Body

from helpers.exceptions import WrongInputException
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import PromoModule


async def get_promo_code(module: 'PromoModule',
                         guild: discord.Guild,
                         member: discord.Member):
    return {'promo_code': await module.create_promo_code(member)}


async def redeem_promo_code(module: 'PromoModule',
                            guild: discord.Guild,
                            member: discord.Member,
                            promo_code: str = Body(embed=True),
                            ):
    if not await module.can_redeem_promo_code(member):
        raise WrongInputException(detail='promo code usage forbidden')
    asyncio.run_coroutine_threadsafe(
        module.redeem_promo_code(member, promo_code, time.time()), module.bot.bot.loop).result()
    return {'msg': 'success'}


API_PAGES = [
    Page(path='promo', view_func=get_promo_code, methods=['GET']),
    Page(path='redeem', view_func=redeem_promo_code, methods=['POST']),
]
