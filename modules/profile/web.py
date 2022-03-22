import discord
from flask import request, send_file

from helpers.exceptions import WrongInputException
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ProfileModule


async def profile_image(module: 'ProfileModule',
                        guild: discord.Guild,
                        member: discord.Member):
    json = request.get_json()
    if json is None or 'preview' not in json:
        img = await module.member_create_profile_image(member)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'PROFILE_IMAGE', json['preview'])
    except:
        raise WrongInputException('setting preview not correct')

    img = await module.member_create_profile_image_by_template(member, preview)
    return send_file(
        img.fp,
        attachment_filename=img.filename,
        mimetype='image/png'
    )


API_PAGES = [
    Page(path='profile-image', view_func=profile_image, methods=['POST']),
]
