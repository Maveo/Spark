import discord
from fastapi import Body

from helpers.exceptions import WrongInputException
from helpers.tools import search_member
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import BoostModule


async def boost_user(module: 'BoostModule',
                     guild: discord.Guild,
                     member: discord.Member,
                     username: str = Body(embed=True)):
    boost_member = search_member(guild, username)
    if boost_member is None:
        raise WrongInputException(detail='user not found')

    await module.boost_user(member, boost_member)
    return {'msg': 'success'}


API_PAGES = [
    Page(path='boost', view_func=boost_user, methods=['POST']),
]
