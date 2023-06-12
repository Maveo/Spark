import discord
from helpers.dummys import RoleDummy
from helpers.exceptions import WrongInputException

from helpers.module_pages import has_permissions
from webserver import Page

from fastapi import Body


from typing import TYPE_CHECKING, Union

from webserver.responses import BytesFileResponse

if TYPE_CHECKING:
    from . import TournamentsModule

async def ko_tournament_image(module: 'TournamentsModule',
                              guild: discord.Guild,
                              member: discord.Member,
                              preview: Union[str, None] = Body(default=None, embed=True),
                             ):
    tree = [['Winner', 12], ['Winner', 1], ['Loser', 1]]

    if preview is None:
        img = await module.create_ko_tournament_image(guild.id, tree)
        return BytesFileResponse(
            img.fp,
            filename=img.filename,
            media_type='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'KO_TOURNAMENT_IMAGE', preview)
    except:
        raise WrongInputException(detail='setting preview not correct')

    img = await module.create_ko_tournament_image_by_template(tree, preview)
    return BytesFileResponse(
        img.fp,
        filename=img.filename,
        media_type='image/png'
    )


API_PAGES = [
    Page(path='ko-tournament-image', view_func=ko_tournament_image, methods=['POST']),
]
