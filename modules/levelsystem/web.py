import discord
from fastapi import Body

from helpers.dummys import RoleDummy
from helpers.exceptions import WrongInputException
from webserver import Page

from typing import TYPE_CHECKING, Union

from webserver.responses import BytesFileResponse

if TYPE_CHECKING:
    from . import LevelsystemModule


async def get_ranking(module: 'LevelsystemModule',
                      guild: discord.Guild,
                      member: discord.Member,
                      offset: Union[int, None] = None,
                      amount: Union[int, None] = None,
                      style_wanted: bool = False,
                      ):
    users = await module.users_get_advanced_infos(guild, await module.get_ranking(guild))

    total_amount = len(users)
    if offset is not None:
        users = users[int(offset):]
    if amount is not None:
        users = users[:int(amount)]

    res = {
        'images': [await module.bot.image_creator.create_inner_svg(
            (await module.get_dependency('profile').member_get_profile_image_template(u['member']))(**u)
        ) for u in users],
        'total_amount': total_amount
    }

    if style_wanted:
        res['style'] = await module.bot.image_creator.create_style()

    return res


async def ranking_image(module: 'LevelsystemModule',
                        guild: discord.Guild,
                        member: discord.Member,
                        preview: Union[str, None] = Body(default=None, embed=True),
                        ):
    if preview is None:
        img = await module.create_leaderboard_image(member)
        return BytesFileResponse(
            img.fp,
            filename=img.filename,
            media_type='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'RANKING_IMAGE', preview)
    except:
        raise WrongInputException(detail='setting preview not correct')

    img = await module.create_leaderboard_image_by_template(member, preview)
    return BytesFileResponse(
        img.fp,
        filename=img.filename,
        media_type='image/png'
    )


async def level_up_image(module: 'LevelsystemModule',
                         guild: discord.Guild,
                         member: discord.Member,
                         preview: Union[str, None] = Body(default=None, embed=True),
                         ):
    if preview is None:
        img = await module.member_create_level_up_image(member, 42, 69)
        return BytesFileResponse(
            img.fp,
            filename=img.filename,
            media_type='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'LEVEL_UP_IMAGE', preview)
    except:
        raise WrongInputException(detail='setting preview not correct')

    img = await module.member_create_level_up_image_by_template(member, 42, 69, preview)
    return BytesFileResponse(
        img.fp,
        filename=img.filename,
        media_type='image/png'
    )


async def rank_up_image(module: 'LevelsystemModule',
                        guild: discord.Guild,
                        member: discord.Member,
                        preview: Union[str, None] = Body(default=None, embed=True),
                        ):
    role1 = RoleDummy()
    role2 = RoleDummy(color=(255, 0, 0))
    if preview is None:
        img = await module.member_create_rank_up_image(member, 42, 69, role1, role2)
        return BytesFileResponse(
            img.fp,
            filename=img.filename,
            media_type='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'LEVEL_UP_IMAGE', preview)
    except:
        raise WrongInputException(detail='setting preview not correct')

    img = await module.member_create_rank_up_image_by_template(member, 42, 69, role1, role2, preview)
    return BytesFileResponse(
        img.fp,
        filename=img.filename,
        media_type='image/png'
    )


API_PAGES = [
    Page(path='ranking', view_func=get_ranking, methods=['GET']),
    Page(path='ranking-image', view_func=ranking_image, methods=['POST']),
    Page(path='level-up-image', view_func=level_up_image, methods=['POST']),
    Page(path='rank-up-image', view_func=rank_up_image, methods=['POST']),
]
