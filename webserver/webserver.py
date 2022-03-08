import os
import threading
import asyncio
from datetime import datetime
import werkzeug
from flask.json import JSONEncoder
from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify, request, send_from_directory, redirect, send_file
import secrets
import jwt
from discord import Member, ClientUser, User, Guild, Invite, TextChannel, VoiceChannel, Message
import logging
import requests
from enums import ENUMS
from imagestack import ImageStackResolveString
import json as jsonm
from helpers import tools
from helpers.dummys import RoleDummy, MemberDummy


class JSONDiscordCustom(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return datetime.timestamp(o)*1000
        if isinstance(o, Member) or isinstance(o, MemberDummy):
            return {
                'id': str(o.id),
                'nick': str(o.display_name),
                'name': str(o.name),
                'avatar_url': str(o.avatar_url),
                'top_role': str(o.top_role.name),
            }
        if isinstance(o, ClientUser) or isinstance(o, User):
            return {
                'id': str(o.id),
                'nick': str(o.display_name),
                'name': str(o.name),
                'avatar_url': str(o.avatar_url),
            }
        if isinstance(o, Guild):
            return {
                'id': str(o.id),
                'name': str(o.name),
                'icon_url': str(o.icon_url),
            }
        if isinstance(o, Invite):
            return {
                'channel': o.channel,
                'code': o.code,
                'inviter': o.inviter,
                'max_age': o.max_age,
                'max_uses': o.max_uses,
                'revoked': o.revoked,
                'temporary': o.temporary,
                'url': o.url,
                'uses': o.uses,
            }
        if isinstance(o, TextChannel) or isinstance(o, VoiceChannel):
            return {
                'id': str(o.id),
                'name': str(o.name),
            }
        if isinstance(o, Message):
            return {
                'id': str(o.id),
                'author': o.author,
                'content': str(o.clean_content),
                'created_at': o.created_at,
            }
        if isinstance(o, ImageStackResolveString):
            return str(o)
        return JSONEncoder.default(self, o)


class UnauthorizedException(werkzeug.exceptions.HTTPException):
    code = 401


class UnknownException(werkzeug.exceptions.HTTPException):
    code = 400


class WrongInputException(werkzeug.exceptions.HTTPException):
    code = 400


class Page:
    def __init__(self, path, view_func, methods=None):
        self.path = path
        self.view_func = view_func
        if methods is None:
            methods = ['GET']
        self.methods = methods


class WebServer(threading.Thread):
    async def get_member_id(self):
        if 'Authorization' not in request.headers:
            raise UnauthorizedException()
        try:
            token = jwt.decode(request.headers['Authorization'], self.webserver_secret, algorithms="HS256")
        except:
            raise UnauthorizedException('session token not found')
        r = requests.get('https://discord.com/api/users/@me', headers={
            'Authorization': token['session_token']
        })
        if r.status_code != 200:
            raise UnauthorizedException('member request not successful')
        json = r.json()
        if 'id' not in json:
            raise UnauthorizedException('id not in member response')
        return int(json['id'])

    async def get_member_guild(self):
        if 'guild_id' not in request.args:
            raise WrongInputException('guild_id not provided')
        try:
            guild_id = int(request.args['guild_id'])
        except ValueError or TypeError:
            raise WrongInputException('guild_id wrong format')
        uid = await self.get_member_id()
        guilds = list(filter(lambda x: x.id == guild_id, self.dbot.bot.guilds))
        if len(guilds) != 1:
            raise WrongInputException('guild not found')
        guild = guilds[0]
        member = guild.get_member(uid)
        if member is None:
            if not self.dbot.is_super_admin(uid):
                raise WrongInputException('member not found')
            member = MemberDummy(uid=uid)
        return guild, member

    async def get_auth_url(self):
        return jsonify({
            'auth_url':
                'https://discord.com/api/oauth2/authorize?client_id={}&redirect_uri={}&response_type={}&scope={}'
                    .format(
                    self.OAUTH2_CLIENT_ID,
                    self.OAUTH2_REDIRECT_URI,
                    'code',
                    'identify'
                )
        }), 200

    async def create_session(self):
        json = request.get_json()
        if json is None or 'code' not in json:
            raise WrongInputException('code not provided')
        r = requests.post('https://discord.com/api/oauth2/token', data={
            'client_id': self.OAUTH2_CLIENT_ID,
            'client_secret': self.OAUTH2_CLIENT_SECRET,
            'code': json['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': self.OAUTH2_REDIRECT_URI,
            'scope': 'identify'
        })
        if r.status_code != 200:
            raise UnauthorizedException('error while authorizing with discord')
        json = r.json()
        if 'access_token' not in json or 'token_type' not in json:
            raise UnauthorizedException('error while authorizing with discord')
        jwtoken = {
            'session_token': '{} {}'.format(json['token_type'], json['access_token'])
        }
        if 'expires_in' in json:
            jwtoken['exp'] = datetime.timestamp(datetime.now()) + json['expires_in']
        encoded_jwt = jwt.encode(jwtoken, self.webserver_secret, algorithm="HS256")
        return jsonify({'session_token': encoded_jwt}), 200

    async def get_guild(self):
        guild, member = await self.get_member_guild()
        return jsonify(guild), 200

    async def get_guilds(self):
        uid = await self.get_member_id()
        return jsonify({'guilds': [
            guild
            for guild in self.dbot.bot.guilds
            if self.dbot.is_super_admin(uid) or guild.get_member(uid) is not None
        ]}), 200

    async def user_profile(self):
        guild, member = await self.get_member_guild()
        return jsonify(await self.dbot.get_user_info(member)), 200

    async def get_promo_code(self):
        guild, member = await self.get_member_guild()
        return jsonify({'promo_code': await self.dbot.create_promo_code(member)}), 200

    async def redeem_promo_code(self):
        guild, member = await self.get_member_guild()
        if not await self.dbot.can_redeem_promo_code(member):
            raise WrongInputException('promo code usage forbidden')
        json = request.get_json()
        if json is None or 'promo_code' not in json:
            raise WrongInputException('promo_code not provided')
        promo = await self.dbot.get_promo_code(member, json['promo_code'])
        if promo is None:
            raise WrongInputException('invalid promo code')
        res = await self.dbot.use_promo_code(member, promo)
        if not res:
            raise WrongInputException('promo code already used')
        return jsonify({'msg': 'success'}), 200

    async def get_ranking(self):
        guild, member = await self.get_member_guild()
        return jsonify(await self.dbot.get_advanced_user_infos(guild, await self.dbot.get_ranking(guild))), 200

    async def boost_user(self):
        guild, member = await self.get_member_guild()
        json = request.get_json()
        if json is None or 'username' not in json:
            raise WrongInputException('username not provided')
        boost_member = await self.dbot.search_member(guild, json['username'])
        if boost_member is None:
            raise WrongInputException('user not found')

        res = await self.dbot.set_boost_user(member, boost_member)
        if res == ENUMS.BOOST_SUCCESS:
            return jsonify({'msg': 'success'}), 200
        elif res == ENUMS.BOOSTING_YOURSELF_FORBIDDEN:
            raise WrongInputException('boosting yourself forbidden')
        raise WrongInputException('boost has not expired yet')

    async def get_settings(self):
        guild, member = await self.get_member_guild()

        if not self.dbot.is_admin(member):
            raise UnauthorizedException('not authorized for settings')

        return jsonify({
            'categories': self.dbot.setting_categories,
            'settings': await self.dbot.get_settings_dicts(guild.id)
        }), 200

    async def reset_setting(self):
        guild, member = await self.get_member_guild()

        if not self.dbot.is_admin(member):
            raise UnauthorizedException('not authorized for settings')

        json = request.get_json()
        if json is None or 'key' not in json:
            raise WrongInputException('setting key not provided')
        if json['key'] not in self.dbot.default_guild_settings:
            raise WrongInputException('setting key not correct')
        await self.dbot.remove_setting(guild.id, json['key'])

        return jsonify({
            'msg': 'success',
            'value': await self.dbot.get_setting(guild.id, json['key'])
        }), 200

    async def set_setting(self):
        guild, member = await self.get_member_guild()

        if not self.dbot.is_admin(member):
            raise UnauthorizedException('not authorized for settings')

        json = request.get_json()
        if json is None or 'key' not in json or 'value' not in json:
            raise WrongInputException('setting key or value not provided')
        if json['key'] not in self.dbot.default_guild_settings:
            raise WrongInputException('setting key not correct')
        if not await self.dbot.set_setting(guild.id, json['key'], json['value']):
            raise WrongInputException('setting value not correct')

        return jsonify({
            'msg': 'success',
            'value': await self.dbot.get_setting(guild.id, json['key'])
        }), 200

    async def welcome_image(self):
        guild, member = await self.get_member_guild()

        json = request.get_json()
        if json is None or 'preview' not in json:
            img = await self.dbot.member_create_welcome_image(member)
            return send_file(
                img.fp,
                attachment_filename=img.filename,
                mimetype='image/png'
            )

        value = jsonm.dumps(json['preview'])
        try:
            default_type = type(self.dbot.default_guild_settings['WELCOME_IMAGE'].value)
            preview = tools.simple_eval(default_type, jsonm.loads(value))
        except:
            raise WrongInputException('setting preview not correct')

        img = await self.dbot.member_create_welcome_image_by_template(member, preview)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    async def profile_image(self):
        guild, member = await self.get_member_guild()

        json = request.get_json()
        if json is None or 'preview' not in json:
            img = await self.dbot.member_create_profile_image(member)
            return send_file(
                img.fp,
                attachment_filename=img.filename,
                mimetype='image/png'
            )

        value = jsonm.dumps(json['preview'])
        try:
            default_type = type(self.dbot.default_guild_settings['PROFILE_IMAGE'].value)
            preview = tools.simple_eval(default_type, jsonm.loads(value))
        except:
            raise WrongInputException('setting preview not correct')

        img = await self.dbot.member_create_profile_image_by_template(member, preview)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    async def ranking_image(self):
        guild, member = await self.get_member_guild()

        json = request.get_json()
        if json is None or 'preview' not in json:
            img = await self.dbot.create_leaderboard_image(member)
            return send_file(
                img.fp,
                attachment_filename=img.filename,
                mimetype='image/png'
            )

        value = jsonm.dumps(json['preview'])
        try:
            default_type = type(self.dbot.default_guild_settings['RANKING_IMAGE'].value)
            preview = tools.simple_eval(default_type, jsonm.loads(value))
        except:
            raise WrongInputException('setting preview not correct')

        img = await self.dbot.create_leaderboard_image_by_template(member, preview)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    async def level_up_image(self):
        guild, member = await self.get_member_guild()

        json = request.get_json()
        if json is None or 'preview' not in json:
            img = await self.dbot.member_create_level_up_image(member, 42, 69)
            return send_file(
                img.fp,
                attachment_filename=img.filename,
                mimetype='image/png'
            )

        value = jsonm.dumps(json['preview'])
        try:
            default_type = type(self.dbot.default_guild_settings['LEVEL_UP_IMAGE'].value)
            preview = tools.simple_eval(default_type, jsonm.loads(value))
        except:
            raise WrongInputException('setting preview not correct')

        img = await self.dbot.member_create_level_up_image_by_template(member, 42, 69, preview)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    async def rank_up_image(self):
        guild, member = await self.get_member_guild()

        role = RoleDummy()

        json = request.get_json()
        if json is None or 'preview' not in json:
            img = await self.dbot.member_create_rank_up_image(member, 42, 69, role, role)
            return send_file(
                img.fp,
                attachment_filename=img.filename,
                mimetype='image/png'
            )

        value = jsonm.dumps(json['preview'])
        try:
            default_type = type(self.dbot.default_guild_settings['RANK_UP_IMAGE'].value)
            preview = tools.simple_eval(default_type, jsonm.loads(value))
        except:
            raise WrongInputException('setting preview not correct')

        img = await self.dbot.member_create_rank_up_image_by_template(member, 42, 69, role, role, preview)
        return send_file(
            img.fp,
            attachment_filename=img.filename,
            mimetype='image/png'
        )

    async def get_invite_links(self):
        guild, member = await self.get_member_guild()

        if not self.dbot.is_admin(member):
            raise UnauthorizedException('not authorized')

        return jsonify({
            'invite_links': asyncio.run_coroutine_threadsafe(guild.invites(), self.dbot.bot.loop).result()
        }), 200

    async def invite_link(self):
        guild, member = await self.get_member_guild()

        if not self.dbot.is_admin(member):
            raise UnauthorizedException('not authorized')

        json = request.get_json()
        if json is None:
            json = {}

        channel = None
        if 'search_channel' in json:
            channel = await self.dbot.search_text_channel(guild, json['search_channel'])
            del json['search_channel']
        if channel is None:
            channel = guild.system_channel
        return jsonify({
            'invite_link': asyncio.run_coroutine_threadsafe(
                channel.create_invite(**json), self.dbot.bot.loop).result()
        }), 200

    async def text_channels(self):
        guild, member = await self.get_member_guild()

        if not self.dbot.is_admin(member):
            raise UnauthorizedException('not authorized')

        return jsonify({
            'text_channels': guild.text_channels
        }), 200

    async def send_msg_channel(self):
        guild, member = await self.get_member_guild()

        if not self.dbot.is_admin(member):
            raise UnauthorizedException('not authorized')

        json = request.get_json()
        if json is None or 'channel_id' not in json or 'message' not in json:
            raise WrongInputException('channel_id or message not provided')

        channel = await self.dbot.search_text_channel(guild, json['channel_id'])
        if channel is None:
            raise WrongInputException('channel not found')

        asyncio.run_coroutine_threadsafe(channel.send(str(json['message'])), self.dbot.bot.loop).result()

        return jsonify({
            'msg': 'success',
        }), 200

    async def get_messages(self):
        guild, member = await self.get_member_guild()

        if not self.dbot.is_admin(member):
            raise UnauthorizedException('not authorized')

        params = request.args
        if params is None or 'channel_id' not in params:
            raise WrongInputException('channel_id not provided')

        channel = await self.dbot.search_text_channel(guild, params['channel_id'])
        if channel is None:
            raise WrongInputException('channel not found')

        limit = 100
        if 'limit' in params and str(params['limit']).isnumeric():
            limit = int(params['limit'])

        return jsonify({
            'messages': asyncio.run_coroutine_threadsafe(
                channel.history(limit=limit).flatten(), self.dbot.bot.loop).result()
        }), 200

    async def set_nickname(self):
        guild, member = await self.get_member_guild()

        if not self.dbot.is_admin(member):
            raise UnauthorizedException('not authorized')

        json = request.get_json()
        if json is None or 'nickname' not in json:
            raise WrongInputException('nickname not provided')

        asyncio.run_coroutine_threadsafe(guild.me.edit(nick=json['nickname']), self.dbot.bot.loop).result()

        return jsonify({
            'msg': 'success',
        }), 200

    def __init__(self,
                 name='Webserver',
                 host='0.0.0.0',
                 port=4004,
                 discord_bot=None,
                 oauth2_client_id=None,
                 oauth2_client_secret=None,
                 oauth2_redirect_uri=None,
                 webserver_secret=None,
                 static_path=None,
                 debug=False,
                 logging_level=logging.WARNING,
                 api_base='/fap'
                 ):
        super().__init__()

        log = logging.getLogger('werkzeug')
        log.setLevel(logging_level)

        self.HOST = host
        self.PORT = port

        self.dbot = discord_bot

        self.OAUTH2_CLIENT_ID = oauth2_client_id
        self.OAUTH2_CLIENT_SECRET = oauth2_client_secret
        self.OAUTH2_REDIRECT_URI = oauth2_redirect_uri

        self.API_BASE_URL = 'https://discordapp.com/api'
        self.AUTHORIZATION_BASE_URL = self.API_BASE_URL + '/oauth2/authorize'
        self.TOKEN_URL = self.API_BASE_URL + '/oauth2/token'

        if webserver_secret is None:
            webserver_secret = secrets.token_urlsafe(16)
        self.webserver_secret = webserver_secret

        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.static_path = os.path.join(self.root_path, static_path)
        self.app = Flask(
            name,
            root_path=self.root_path,
        )
        self.app.debug = debug
        self.app.json_encoder = JSONDiscordCustom

        @self.app.errorhandler(Exception)
        def handle_exception(e):
            if isinstance(e, werkzeug.exceptions.HTTPException):
                return jsonify({
                    'code': e.code,
                    'name': e.name,
                    'description': e.description,
                }), e.code

            return jsonify({
                'code': 400,
                'name': type(e).__name__,
                'description': str(e),
            }), 400

        if debug:
            @self.app.after_request
            def after_request_func(response):
                header = response.headers
                header['Access-Control-Allow-Origin'] = '*'
                header['Access-Control-Allow-Headers'] = '*'
                header['Access-Control-Allow-Methods'] = '*'
                return response

        async def send_root():
            return send_from_directory(self.static_path, 'index.html')

        async def static_file(path):
            p = os.path.join(self.static_path, path)
            if os.path.isdir(p):
                if p[-1] != '/':
                    return redirect(path + '/')
                if os.path.isfile(p + 'index.html'):
                    return send_from_directory(self.static_path, path + 'index.html')
            elif os.path.exists(p):
                return send_from_directory(self.static_path, path)
            return await send_root()

        self.pages = [
            Page(path=api_base + '/get-auth', view_func=self.get_auth_url),
            Page(path=api_base + '/create-session', view_func=self.create_session, methods=['POST']),
            Page(path=api_base + '/guild', view_func=self.get_guild),
            Page(path=api_base + '/guilds', view_func=self.get_guilds),
            Page(path=api_base + '/profile', view_func=self.user_profile),
            Page(path=api_base + '/promo', view_func=self.get_promo_code),
            Page(path=api_base + '/boost', view_func=self.boost_user, methods=['POST']),
            Page(path=api_base + '/redeem', view_func=self.redeem_promo_code, methods=['POST']),
            Page(path=api_base + '/ranking', view_func=self.get_ranking),
            Page(path=api_base + '/settings', view_func=self.get_settings),
            Page(path=api_base + '/reset-setting', view_func=self.reset_setting, methods=['POST']),
            Page(path=api_base + '/set-setting', view_func=self.set_setting, methods=['POST']),
            Page(path=api_base + '/welcome-image', view_func=self.welcome_image, methods=['POST']),
            Page(path=api_base + '/profile-image', view_func=self.profile_image, methods=['POST']),
            Page(path=api_base + '/ranking-image', view_func=self.ranking_image, methods=['POST']),
            Page(path=api_base + '/level-up-image', view_func=self.level_up_image, methods=['POST']),
            Page(path=api_base + '/rank-up-image', view_func=self.rank_up_image, methods=['POST']),
            Page(path=api_base + '/invite-links', view_func=self.get_invite_links),
            Page(path=api_base + '/invite-link', view_func=self.invite_link, methods=['POST']),
            Page(path=api_base + '/text-channels', view_func=self.text_channels),
            Page(path=api_base + '/send-message', view_func=self.send_msg_channel, methods=['POST']),
            Page(path=api_base + '/messages', view_func=self.get_messages),
            Page(path=api_base + '/nickname', view_func=self.set_nickname, methods=['POST']),
            Page(path='/<path:path>', view_func=static_file),
            Page(path='/', view_func=send_root),
        ]

        def _wrapper(func):
            def _call(*args, **kwargs):
                loop = asyncio.new_event_loop()
                task = loop.create_task(func(*args, **kwargs))
                res = loop.run_until_complete(task)
                return res

            return _call

        for page in self.pages:
            self.app.add_url_rule(rule=page.path,
                                  endpoint=page.path,
                                  view_func=_wrapper(page.view_func),
                                  methods=page.methods)

    def run(self):
        http_server = WSGIServer((self.HOST, self.PORT), self.app)
        print('starting webserver on {}:{}'.format(self.HOST, self.PORT))
        if self.app.debug:
            print('WARNING app is running in debug mode')
        http_server.serve_forever()


def main():
    from settings import GLOBAL_SETTINGS

    a = WebServer(
        oauth2_client_id=GLOBAL_SETTINGS['APPLICATION_ID'],
        oauth2_client_secret=GLOBAL_SETTINGS['APPLICATION_SECRET'],
        oauth2_redirect_uri=GLOBAL_SETTINGS['OAUTH2_REDIRECT_URI'],
        static_path=GLOBAL_SETTINGS['WEBSERVER_STATIC_PATH'],
        debug=GLOBAL_SETTINGS['WEBSERVER_DEBUG']
    )
    a.run()


if __name__ == '__main__':
    main()
