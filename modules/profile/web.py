import discord
from fastapi import Body

from helpers.exceptions import WrongInputException
from webserver import Page

from typing import TYPE_CHECKING, Union

from webserver.responses import BytesFileResponse

if TYPE_CHECKING:
    from . import ProfileModule


async def profile_image(module: 'ProfileModule',
                        guild: discord.Guild,
                        member: discord.Member,
                        preview: Union[str, None] = Body(default=None, embed=True),
                        ):
    if preview is None:
        img = await module.member_create_profile_image(member)
        return BytesFileResponse(
            img.fp,
            filename=img.filename,
            media_type='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'PROFILE_IMAGE', preview)
    except:
        raise WrongInputException(detail='setting preview not correct')

    img = await module.member_create_profile_image_by_template(member, preview)
    return BytesFileResponse(
        img.fp,
        filename=img.filename,
        media_type='image/png'
    )


API_PAGES = [
    Page(path='profile-image', view_func=profile_image, methods=['POST']),
]
