import discord
from fastapi import Body

from helpers.exceptions import WrongInputException
from helpers.module_pages import has_permissions
from webserver import Page
from webserver.responses import BytesFileResponse

from typing import TYPE_CHECKING
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import ActiveTrackerModule


async def activity_image(module: 'ActiveTrackerModule',
                        guild: discord.Guild,
                        member: discord.Member,
                        preview: Union[str, None] = Body(default=None, embed=True),
                        ):
    if preview is None:
        img = await module.create_activity_leaderboard_image(member.guild)
        return BytesFileResponse(
            img.fp,
            filename=img.filename,
            media_type='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'ACTIVITY_IMAGE', preview)
    except:
        raise WrongInputException(detail='setting preview not correct')

    img = await module.create_activity_leaderboard_image_by_template(member.guild, preview)
    return BytesFileResponse(
        img.fp,
        filename=img.filename,
        media_type='image/png'
    )


API_PAGES = [
    Page(path='activity-image', view_func=activity_image, methods=['POST']),
]
