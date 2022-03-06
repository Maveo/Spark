import os
import threading
import asyncio
import werkzeug
from flask.json import JSONEncoder
from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify, request, send_from_directory, redirect, send_file
from discord import Member, Guild
import logging
import requests
from enums import ENUMS
from imagestack import ImageStackResolveString
import json as jsonm
from helpers import tools
from helpers.dummys import RoleDummy


class JSONDiscordCustom(JSONEncoder):
    def default(self, o):
        if isinstance(o, Member):
            return {
                'id': str(o.id),
                'nick': str(o.display_name),
                'name': str(o.name),
                'avatar_url': str(o.avatar_url),
                'top_role': str(o.top_role.name),
            }
        if isinstance(o, Guild):
            return {
                'id': str(o.id),
                'name': str(o.name),
                'icon_url': str(o.icon_url),
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
        r = requests.get('https://discord.com/api/users/@me', headers={
            'Authorization': request.headers['Authorization']
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
            raise WrongInputException('member not found')
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
        return jsonify({'session_token': '{} {}'.format(json['token_type'], json['access_token'])}), 200

    async def get_guild(self):
        guild, member = await self.get_member_guild()
        return jsonify(guild), 200

    async def get_guilds(self):
        uid = await self.get_member_id()
        return jsonify({'guilds': [
            guild
            for guild in self.dbot.bot.guilds
            if guild.get_member(uid) is not None
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

        if not member.guild_permissions.administrator:
            raise UnauthorizedException('not authorized for settings')

        return jsonify({
            'categories': self.dbot.setting_categories,
            'settings': await self.dbot.get_settings_dicts(guild.id)
        }), 200

    async def reset_setting(self):
        guild, member = await self.get_member_guild()

        if not member.guild_permissions.administrator:
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

        if not member.guild_permissions.administrator:
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

    def __init__(self,
                 name='Webserver',
                 host='0.0.0.0',
                 port=4004,
                 discord_bot=None,
                 oauth2_client_id=None,
                 oauth2_client_secret=None,
                 oauth2_redirect_uri=None,
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

        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.static_path = os.path.join(self.root_path, static_path)
        self.app = Flask(
            name,
            root_path=self.root_path,
        )
        self.app.debug = debug
        self.app.json_encoder = JSONDiscordCustom

        @self.app.errorhandler(werkzeug.exceptions.HTTPException)
        def handle_exception(e):
            return jsonify({
                'code': e.code,
                'name': e.name,
                'description': e.description,
            }), e.code

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
