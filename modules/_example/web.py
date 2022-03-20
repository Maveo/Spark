import discord
from flask import jsonify

from helpers.module_pages import has_permissions
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ExampleModule


@has_permissions(administrator=True)
async def example_func(module: 'ExampleModule',
                       guild: discord.Guild,
                       member: discord.Member):
    return jsonify({'msg': 'success'}), 200


API_PAGES = [
    Page(path='example', view_func=example_func, methods=['POST']),
]
