import asyncio
import base64
import os
from io import BytesIO

import discord
from discord import PCMAudio, ActivityType, Status, Activity
from discord.utils import get
from fastapi import Body, UploadFile, File, Form
from imagestack_svg.helpers import is_emoji, from_char

from helpers.exceptions import WrongInputException, MethodNotAvailableException
from helpers.module_pages import has_permissions
from helpers.tools import search_text_channel, search_voice_channel, give_role, remove_role
from webserver import Page

from typing import TYPE_CHECKING, Any, Union

from webserver.responses import BytesFileResponse

AUDIO_IMPORTED = False
try:
    from pydub import AudioSegment

    AUDIO_IMPORTED = True
except ImportError:
    pass

if TYPE_CHECKING:
    from . import GeneralModule


async def get_profile(module: 'GeneralModule',
                      guild: discord.Guild,
                      member: discord.Member):
    return await module.bot.module_manager.create_extended_profile(member)


@has_permissions(administrator=True)
async def get_settings(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member):
    return {
        'categories': module.bot.module_manager.settings.categories(guild.id),
        'settings': module.bot.module_manager.settings.all_as_dict(guild.id)
    }


@has_permissions(administrator=True)
async def reset_setting(module: 'GeneralModule',
                        guild: discord.Guild,
                        member: discord.Member,
                        key: str = Body(embed=True),
                        ):
    if key not in module.bot.module_manager.settings.keys(guild.id):
        raise WrongInputException(detail='setting key not correct')
    module.bot.module_manager.settings.remove(guild.id, key)

    return {
        'msg': 'success',
        'value': module.bot.module_manager.settings.get(guild.id, key)
    }


@has_permissions(administrator=True)
async def set_setting(module: 'GeneralModule',
                      guild: discord.Guild,
                      member: discord.Member,
                      key: str = Body(embed=True),
                      value: Any = Body(embed=True),
                      ):
    if key not in module.bot.module_manager.settings.keys(guild.id):
        raise WrongInputException(detail='setting key not correct')
    if not module.bot.module_manager.settings.set(guild.id, key, value):
        raise WrongInputException(detail='setting value not correct')

    return {
        'msg': 'success',
        'value': module.bot.module_manager.settings.get(guild.id, key)
    }


@has_permissions(administrator=True)
async def get_modules(module: 'GeneralModule',
                      guild: discord.Guild,
                      member: discord.Member):
    return {
        'modules': list(module.bot.module_manager.values())
    }


@has_permissions(administrator=True)
async def set_module(module: 'GeneralModule',
                     guild: discord.Guild,
                     member: discord.Member,
                     target_module: str = Body(embed=True),
                     activate: bool = Body(embed=True),
                     ):
    if activate:
        await module.bot.module_manager.activate_module(guild.id, target_module, True)
    else:
        await module.bot.module_manager.deactivate_module(guild.id, target_module, True)
    return {'msg': 'success'}


async def welcome_image(module: 'GeneralModule',
                        guild: discord.Guild,
                        member: discord.Member,
                        preview: Union[str, None] = Body(default=None, embed=True),
                        ):
    if preview is None:
        img = await module.member_create_welcome_image(member)
        return BytesFileResponse(
            img.fp,
            filename=img.filename,
            media_type='image/png',
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'WELCOME_IMAGE', preview)
    except:
        raise WrongInputException(detail='setting preview not correct')

    img = await module.member_create_welcome_image_by_template(member, preview)
    return BytesFileResponse(
        img.fp,
        filename=img.filename,
        media_type='image/png',
    )


@has_permissions(administrator=True)
async def get_invite_links(module: 'GeneralModule',
                           guild: discord.Guild,
                           member: discord.Member):
    return {
        'invite_links': asyncio.run_coroutine_threadsafe(guild.invites(), module.bot.bot.loop).result()
    }


@has_permissions(administrator=True)
async def invite_link(module: 'GeneralModule',
                      guild: discord.Guild,
                      member: discord.Member,
                      json_body: dict = Body(default={})):
    channel = None
    if 'search_channel' in json_body:
        channel = search_text_channel(guild, json_body['search_channel'])
        del json_body['search_channel']
    if channel is None:
        channel = guild.system_channel
    return {
        'invite_link': asyncio.run_coroutine_threadsafe(
            channel.create_invite(**json_body), module.bot.bot.loop).result()
    }


@has_permissions(administrator=True)
async def text_channels(module: 'GeneralModule',
                        guild: discord.Guild,
                        member: discord.Member):
    return {
        'text_channels': guild.text_channels
    }


@has_permissions(administrator=True)
async def voice_channels(module: 'GeneralModule',
                         guild: discord.Guild,
                         member: discord.Member):
    return {
        'voice_channels': guild.voice_channels
    }


@has_permissions(administrator=True)
async def get_roles(module: 'GeneralModule',
                    guild: discord.Guild,
                    member: discord.Member):
    return {
        'roles': guild.roles
    }


@has_permissions(administrator=True)
async def set_role(module: 'GeneralModule',
                   guild: discord.Guild,
                   member: discord.Member,
                   give: bool = Body(embed=True),
                   role_id: str = Body(embed=True),
                   user_id: str = Body(embed=True),
                   ):
    member = get(guild.members, id=int(user_id))
    if member is None:
        raise WrongInputException(detail='Member not found')

    if give:
        asyncio.run_coroutine_threadsafe(give_role(guild, member, int(role_id)), module.bot.bot.loop).result()
    else:
        asyncio.run_coroutine_threadsafe(remove_role(guild, member, int(role_id)), module.bot.bot.loop).result()

    return {
        'msg': 'success',
    }


@has_permissions(administrator=True)
async def send_msg_channel(module: 'GeneralModule',
                           guild: discord.Guild,
                           member: discord.Member,
                           channel_id: str = Body(embed=True),
                           message: str = Body(embed=True),
                           ):
    channel = search_text_channel(guild, str(channel_id))
    if channel is None:
        raise WrongInputException(detail='channel not found')

    asyncio.run_coroutine_threadsafe(channel.send(str(message)), module.bot.bot.loop).result()

    return {
        'msg': 'success',
    }


@has_permissions(administrator=True)
async def get_messages(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member,
                       channel_id: str,
                       limit: int = 100,
                       ):
    channel = search_text_channel(guild, channel_id)
    if channel is None:
        raise WrongInputException(detail='channel not found')

    return {
        'messages': asyncio.run_coroutine_threadsafe(
            channel.history(limit=limit).flatten(), module.bot.bot.loop).result()
    }


@has_permissions(administrator=True)
async def set_nickname(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member,
                       nickname: str = Body(embed=True),
                       ):
    asyncio.run_coroutine_threadsafe(guild.me.edit(nick=nickname), module.bot.bot.loop).result()

    return {
        'msg': 'success',
    }


@has_permissions(administrator=True)
async def send_voice_audio(module: 'GeneralModule',
                           guild: discord.Guild,
                           member: discord.Member,
                           audio_file: UploadFile = File(),
                           voice_channel: str = Form(),
                           ):
    if not AUDIO_IMPORTED:
        raise WrongInputException(detail='audio not supported')

    stream = BytesIO()
    sound = AudioSegment.from_file(audio_file.file)
    sound.export(stream, format='wav')
    await module.bot.play_audio(
        PCMAudio(stream),
        search_voice_channel(guild, voice_channel)
    )

    return {
        'msg': 'success',
    }


@has_permissions(super_admin=True)
async def set_presence(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member,
                       activity_name: Union[str, None] = Body(embed=True, default=None),
                       activity_type: Union[int, None] = Body(embed=True, default=ActivityType.custom),
                       status_type: Union[str, None] = Body(embed=True, default=Status.online),
                       ):
    asyncio.run_coroutine_threadsafe(
        module.bot.bot.change_presence(
            activity=Activity(type=activity_type, name=activity_name), status=status_type),
        module.bot.bot.loop).result()

    return {
        'msg': 'success',
    }


@has_permissions(super_admin=True)
async def get_emojis(module: 'GeneralModule',
                     guild: discord.Guild,
                     member: discord.Member):
    emojis = module.bot.image_creator.emoji_loader.get_downloaded_emojis()
    send_emojis = []
    for e in emojis:
        with open(os.path.join(module.bot.image_creator.emoji_loader.emoji_path, e['path']), 'rb') as f:
            send_emojis.append({'emoji': e['emoji'], 'base64': base64.b64encode(f.read()).decode()})

    return {
        'msg': 'success',
        'emojis': send_emojis
    }


@has_permissions(super_admin=True)
async def change_emoji(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member,
                       emoji_file: UploadFile = File(),
                       emoji: str = Form(),
                       ):
    if not is_emoji(emoji):
        raise WrongInputException(detail='emoji is wrong')

    if not module.bot.image_creator.emoji_loader.save_downloaded_emojis:
        raise MethodNotAvailableException(detail='cannot save emojis')

    emoji_id = from_char(emoji)
    module.bot.image_creator.emoji_loader.cached_images.clear()
    with open(os.path.join(module.bot.image_creator.emoji_loader.emoji_path,
                           emoji_id + '.png'), 'wb') as f:
        f.write(emoji_file.file.read())
    module.bot.logger.info('saved new image for emoji {}'.format(emoji_id))

    return {
        'msg': 'success',
    }


API_PAGES = [
    Page(path='profile', view_func=get_profile),
    Page(path='settings', view_func=get_settings),
    Page(path='reset-setting', view_func=reset_setting, methods=['POST']),
    Page(path='set-setting', view_func=set_setting, methods=['POST']),

    Page(path='modules', view_func=get_modules),
    Page(path='set-module', view_func=set_module, methods=['POST']),

    Page(path='welcome-image', view_func=welcome_image, methods=['POST']),

    Page(path='invite-links', view_func=get_invite_links),
    Page(path='invite-link', view_func=invite_link, methods=['POST']),
    Page(path='text-channels', view_func=text_channels),
    Page(path='voice-channels', view_func=voice_channels),
    Page(path='roles', view_func=get_roles),
    Page(path='set-role', view_func=set_role, methods=['POST']),
    Page(path='send-message', view_func=send_msg_channel, methods=['POST']),
    Page(path='messages', view_func=get_messages),
    Page(path='nickname', view_func=set_nickname, methods=['POST']),
    Page(path='audio', view_func=send_voice_audio, methods=['POST']),
    Page(path='presence', view_func=set_presence, methods=['POST']),
    Page(path='emojis', view_func=get_emojis),
    Page(path='change-emoji', view_func=change_emoji, methods=['POST']),
]
