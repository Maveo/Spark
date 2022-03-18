import discord
from flask import jsonify, request

from helpers.exceptions import WrongInputException
from helpers.tools import search_member
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import BoostModule


async def boost_user(module: 'BoostModule',
                     guild: discord.Guild,
                     member: discord.Member):
    json = request.get_json()
    if json is None or 'username' not in json:
        raise WrongInputException('username not provided')
    boost_member = search_member(guild, json['username'])
    if boost_member is None:
        raise WrongInputException('user not found')

    await module.boost_user(member, boost_member)
    return jsonify({'msg': 'success'}), 200


API_PAGES = [
    Page(path='boost', view_func=boost_user, methods=['POST']),
]
