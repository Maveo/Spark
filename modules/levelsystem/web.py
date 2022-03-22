import discord
from flask import jsonify, request, send_file
from imagestack import VisitorHtml

from helpers.dummys import RoleDummy
from helpers.exceptions import WrongInputException
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import LevelsystemModule


async def get_ranking(module: 'LevelsystemModule',
                      guild: discord.Guild,
                      member: discord.Member):
    users = await module.users_get_advanced_infos(guild, await module.get_ranking(guild))

    total_amount = len(users)
    if 'offset' in request.args:
        users = users[int(request.args['offset']):]
    if 'amount' in request.args:
        users = users[:int(request.args['amount'])]

    res = {
        'images': [module.bot.image_creator.create_raw_html(
            (await module.get_dependency('profile').member_get_profile_image_template(u['member']))(u)
        ) for u in users],
        'total_amount': total_amount
    }

    if 'style_wanted' in request.args:
        res['style'] = VisitorHtml(module.bot.image_creator).style_html()

    return jsonify(res), 200


async def ranking_image(module: 'LevelsystemModule',
                        guild: discord.Guild,
                        member: discord.Member):
    json = request.get_json()
    if json is None or 'preview' not in json:
        img = await module.create_leaderboard_image(member)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'RANKING_IMAGE', json['preview'])
    except:
        raise WrongInputException('setting preview not correct')

    img = await module.create_leaderboard_image_by_template(member, preview)
    return send_file(
        img.fp,
        attachment_filename=img.filename,
        mimetype='image/png'
    )


async def level_up_image(module: 'LevelsystemModule',
                         guild: discord.Guild,
                         member: discord.Member):
    json = request.get_json()
    if json is None or 'preview' not in json:
        img = await module.member_create_level_up_image(member, 42, 69)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'LEVEL_UP_IMAGE', json['preview'])
    except:
        raise WrongInputException('setting preview not correct')

    img = await module.member_create_level_up_image_by_template(member, 42, 69, preview)
    return send_file(
        img.fp,
        attachment_filename=img.filename,
        mimetype='image/png'
    )


async def rank_up_image(module: 'LevelsystemModule',
                        guild: discord.Guild,
                        member: discord.Member):
    json = request.get_json()
    role = RoleDummy()
    if json is None or 'preview' not in json:
        img = await module.member_create_rank_up_image(member, 42, 69, role, role)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'LEVEL_UP_IMAGE', json['preview'])
    except:
        raise WrongInputException('setting preview not correct')

    img = await module.member_create_rank_up_image_by_template(member, 42, 69, role, role, preview)
    return send_file(
        img.fp,
        attachment_filename=img.filename,
        mimetype='image/png'
    )


API_PAGES = [
    Page(path='ranking', view_func=get_ranking, methods=['GET']),
    Page(path='ranking-image', view_func=ranking_image, methods=['POST']),
    Page(path='level-up-image', view_func=level_up_image, methods=['POST']),
    Page(path='rank-up-image', view_func=rank_up_image, methods=['POST']),
]
