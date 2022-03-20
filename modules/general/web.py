import asyncio
import base64
import os
from io import BytesIO

import discord
from discord import PCMAudio, ActivityType, Status, Activity
from flask import jsonify, request, send_file
from imagestack import is_emoji, from_char

from helpers.exceptions import WrongInputException, MethodNotAvailableException
from helpers.module_pages import has_permissions
from helpers.tools import search_text_channel, search_voice_channel
from webserver import Page

from typing import TYPE_CHECKING

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
    return jsonify(await module.bot.module_manager.create_extended_profile(member)), 200


@has_permissions(administrator=True)
async def get_settings(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member):
    return jsonify({
        'categories': module.bot.module_manager.settings.categories(guild.id),
        'settings': module.bot.module_manager.settings.all_as_dict(guild.id)
    }), 200


@has_permissions(administrator=True)
async def reset_setting(module: 'GeneralModule',
                        guild: discord.Guild,
                        member: discord.Member):
    json = request.get_json()
    if json is None or 'key' not in json:
        raise WrongInputException('setting key or value not provided')
    if json['key'] not in module.bot.module_manager.settings.keys(guild.id):
        raise WrongInputException('setting key not correct')
    module.bot.module_manager.settings.remove(guild.id, json['key'])

    return jsonify({
        'msg': 'success',
        'value': module.bot.module_manager.settings.get(guild.id, json['key'])
    }), 200


@has_permissions(administrator=True)
async def set_setting(module: 'GeneralModule',
                      guild: discord.Guild,
                      member: discord.Member):
    json = request.get_json()
    if json is None or 'key' not in json or 'value' not in json:
        raise WrongInputException('setting key or value not provided')
    if json['key'] not in module.bot.module_manager.settings.keys(guild.id):
        raise WrongInputException('setting key not correct')
    if not module.bot.module_manager.settings.set(guild.id, json['key'], json['value']):
        raise WrongInputException('setting value not correct')

    return jsonify({
        'msg': 'success',
        'value': module.bot.module_manager.settings.get(guild.id, json['key'])
    }), 200


@has_permissions(administrator=True)
async def get_modules(module: 'GeneralModule',
                      guild: discord.Guild,
                      member: discord.Member):
    return jsonify({
        'modules': list(module.bot.module_manager.values())
    }), 200


@has_permissions(administrator=True)
async def set_module(module: 'GeneralModule',
                     guild: discord.Guild,
                     member: discord.Member):
    json = request.get_json()
    if json is None or 'module' not in json or 'activate' not in json:
        raise WrongInputException('module or activate not provided')
    if json['activate']:
        await module.bot.module_manager.activate_module(guild.id, json['module'], True)
    else:
        await module.bot.module_manager.deactivate_module(guild.id, json['module'], True)
    return jsonify({'msg': 'success'}), 200


async def welcome_image(module: 'GeneralModule',
                        guild: discord.Guild,
                        member: discord.Member):
    json = request.get_json()
    if json is None or 'preview' not in json:
        img = await module.member_create_welcome_image(member)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    try:
        preview = module.bot.module_manager.settings.preview(guild.id, 'WELCOME_IMAGE', json['preview'])
    except:
        raise WrongInputException('setting preview not correct')

    img = await module.member_create_welcome_image_by_template(member, preview)
    return send_file(
        img.fp,
        attachment_filename=img.filename,
        mimetype='image/png'
    )


@has_permissions(administrator=True)
async def get_invite_links(module: 'GeneralModule',
                           guild: discord.Guild,
                           member: discord.Member):
    return jsonify({
        'invite_links': asyncio.run_coroutine_threadsafe(guild.invites(), module.bot.bot.loop).result()
    }), 200


@has_permissions(administrator=True)
async def invite_link(module: 'GeneralModule',
                      guild: discord.Guild,
                      member: discord.Member):
    json = request.get_json()
    if json is None:
        json = {}

    channel = None
    if 'search_channel' in json:
        channel = search_text_channel(guild, json['search_channel'])
        del json['search_channel']
    if channel is None:
        channel = guild.system_channel
    return jsonify({
        'invite_link': asyncio.run_coroutine_threadsafe(
            channel.create_invite(**json), module.bot.bot.loop).result()
    }), 200


@has_permissions(administrator=True)
async def text_channels(module: 'GeneralModule',
                        guild: discord.Guild,
                        member: discord.Member):
    return jsonify({
        'text_channels': guild.text_channels
    }), 200


@has_permissions(administrator=True)
async def voice_channels(module: 'GeneralModule',
                         guild: discord.Guild,
                         member: discord.Member):
    return jsonify({
        'voice_channels': guild.voice_channels
    }), 200


@has_permissions(administrator=True)
async def send_msg_channel(module: 'GeneralModule',
                           guild: discord.Guild,
                           member: discord.Member):
    json = request.get_json()
    if json is None or 'channel_id' not in json or 'message' not in json:
        raise WrongInputException('channel_id or message not provided')

    channel = search_text_channel(guild, json['channel_id'])
    if channel is None:
        raise WrongInputException('channel not found')

    asyncio.run_coroutine_threadsafe(channel.send(str(json['message'])), module.bot.bot.loop).result()

    return jsonify({
        'msg': 'success',
    }), 200


@has_permissions(administrator=True)
async def get_messages(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member):
    params = request.args
    if params is None or 'channel_id' not in params:
        raise WrongInputException('channel_id not provided')

    channel = search_text_channel(guild, params['channel_id'])
    if channel is None:
        raise WrongInputException('channel not found')

    limit = 100
    if 'limit' in params and str(params['limit']).isnumeric():
        limit = int(params['limit'])

    return jsonify({
        'messages': asyncio.run_coroutine_threadsafe(
            channel.history(limit=limit).flatten(), module.bot.bot.loop).result()
    }), 200


@has_permissions(administrator=True)
async def set_nickname(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member):
    json = request.get_json()
    if json is None or 'nickname' not in json:
        raise WrongInputException('nickname not provided')

    asyncio.run_coroutine_threadsafe(guild.me.edit(nick=json['nickname']), module.bot.bot.loop).result()

    return jsonify({
        'msg': 'success',
    }), 200


@has_permissions(administrator=True)
async def send_voice_audio(module: 'GeneralModule',
                           guild: discord.Guild,
                           member: discord.Member):
    if 'audio_file' not in request.files or 'voice_channel' not in request.form:
        raise WrongInputException('audio_file or voice_channel not provided')

    if not AUDIO_IMPORTED:
        raise WrongInputException('audio not supported')

    stream = BytesIO()
    sound = AudioSegment.from_file(request.files['audio_file'])
    sound.export(stream, format='wav')
    await module.bot.play_audio(
        PCMAudio(stream),
        search_voice_channel(guild, request.form['voice_channel'])
    )

    # request.files['audio_file'].save('__temp.mp3')
    # await self.dbot.play_audio(
    #     FFmpegPCMAudio('__temp.mp3'),
    #     await self.dbot.search_voice_channel(guild, request.form['voice_channel'])
    # )

    return jsonify({
        'msg': 'success',
    }), 200


@has_permissions(super_admin=True)
async def set_presence(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member):
    json = request.get_json()
    if json is None:
        json = {}

    if 'activity_name' not in json:
        json['activity_name'] = None
    if 'activity_type' not in json or json['activity_type'] is None:
        json['activity_type'] = ActivityType.custom
    if 'status_type' not in json or json['status_type'] is None:
        json['status_type'] = Status.online

    asyncio.run_coroutine_threadsafe(
        module.bot.bot.change_presence(
            activity=Activity(type=json['activity_type'], name=json['activity_name']), status=json['status_type']),
        module.bot.bot.loop).result()

    return jsonify({
        'msg': 'success',
    }), 200


@has_permissions(super_admin=True)
async def get_emojis(module: 'GeneralModule',
                     guild: discord.Guild,
                     member: discord.Member):
    emojis = module.bot.image_creator.get_downloaded_emojis()
    send_emojis = []
    for e in emojis:
        with open(os.path.join(module.bot.image_creator.emoji_path, e['path']), 'rb') as f:
            send_emojis.append({'emoji': e['emoji'], 'base64': base64.b64encode(f.read()).decode()})

    return jsonify({
        'msg': 'success',
        'emojis': send_emojis
    }), 200


@has_permissions(super_admin=True)
async def change_emoji(module: 'GeneralModule',
                       guild: discord.Guild,
                       member: discord.Member):
    if 'emoji_file' not in request.files or 'emoji' not in request.form:
        raise WrongInputException('emoji_file or emoji not provided')

    if not is_emoji(request.form['emoji']):
        raise WrongInputException('emoji is wrong')

    if not module.bot.image_creator.save_downloaded_emojis:
        raise MethodNotAvailableException('cannot save emojis')

    emoji_id = from_char(request.form['emoji'])
    request.files['emoji_file'].save(os.path.join(module.bot.image_creator.emoji_path,
                                                  emoji_id + '.png'))
    module.bot.logger.info('saved new image for emoji {}'.format(emoji_id))

    return jsonify({
        'msg': 'success',
    }), 200


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
    Page(path='send-message', view_func=send_msg_channel, methods=['POST']),
    Page(path='messages', view_func=get_messages),
    Page(path='nickname', view_func=set_nickname, methods=['POST']),
    Page(path='audio', view_func=send_voice_audio, methods=['POST']),
    Page(path='presence', view_func=set_presence, methods=['POST']),
    Page(path='emojis', view_func=get_emojis),
    Page(path='change-emoji', view_func=change_emoji, methods=['POST']),
]
