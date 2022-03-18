import os
import threading
import asyncio
from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify, request, send_from_directory, redirect
from flask.logging import default_handler
import logging
import requests
from helpers.dummys import MemberDummy
import base64
from cryptography.fernet import Fernet
from helpers.exceptions import *
from .json_encoder import create_json_encoder

try:
    from pydub import AudioSegment

    PYDUB_IMPORTED = True
except ImportError:
    PYDUB_IMPORTED = False

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import DiscordBot


class Page:
    def __init__(self, path, view_func, methods=None):
        self.path = path
        self.view_func = view_func
        if methods is None:
            methods = ['GET']
        self.methods = methods

    def new(self, path=None, view_func=None, methods=None):
        if path is None:
            path = self.path
        if view_func is None:
            view_func = self.view_func
        if methods is None:
            methods = self.methods
        return Page(path, view_func, methods)


class WebServer(threading.Thread):
    def encrypt(self, s):
        return self.crypter.encrypt(s.encode()).decode()

    def decrypt(self, s):
        return self.crypter.decrypt(s.encode()).decode()

    async def get_member_id(self):
        if 'Authorization' not in request.headers:
            raise UnauthorizedException()
        try:
            token = self.decrypt(request.headers['Authorization'])
        except:
            raise UnauthorizedException('session token not found')
        r = requests.get('https://discord.com/api/users/@me', headers={
            'Authorization': token
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
        except ValueError and TypeError:
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
        encrypted = self.encrypt('{} {}'.format(json['token_type'], json['access_token']))
        return jsonify({'session_token': encrypted}), 200

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

    def guild_member_wrapper(self, func):
        async def _call(*args, **kwargs):
            guild, member = await self.get_member_guild()
            return await func(guild, member, *args, **kwargs)

        return _call

    def __init__(self,
                 name='Webserver',
                 host='0.0.0.0',
                 port=4004,
                 discord_bot: 'DiscordBot' = None,
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
            webserver_secret = Fernet.generate_key()
        else:
            webserver_secret = webserver_secret[:32]
            webserver_secret = webserver_secret + ('0' * max(0, 32 - len(webserver_secret)))
            webserver_secret = base64.urlsafe_b64encode(webserver_secret.encode())
        self.crypter = Fernet(webserver_secret)

        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.static_path = os.path.join(self.root_path, static_path)
        self.app = Flask(
            name,
            root_path=self.root_path,
        )
        self.app.debug = debug
        self.app.json_encoder = create_json_encoder(self.dbot)
        self.app.logger.removeHandler(default_handler)
        self.app.logger.setLevel(logging_level)

        @self.app.errorhandler(Exception)
        def handle_exception(e):
            self.app.log_exception(e)
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

        def _wrapper(func):
            def _call(*args, **kwargs):
                loop = asyncio.new_event_loop()
                task = loop.create_task(func(*args, **kwargs))
                res = loop.run_until_complete(task)
                return res

            return _call

        pages = [
            Page(path=f"{api_base}/get-auth", view_func=self.get_auth_url),
            Page(path=f"{api_base}/create-session", view_func=self.create_session, methods=['POST']),
            Page(path=f"{api_base}/guild", view_func=self.get_guild),
            Page(path=f"{api_base}/guilds", view_func=self.get_guilds),
            Page(path='/<path:path>', view_func=static_file),
            Page(path='/', view_func=send_root),
        ]

        for page in pages:
            self.app.add_url_rule(rule=page.path,
                                  endpoint=page.path,
                                  view_func=_wrapper(page.view_func),
                                  methods=page.methods)

        for page in self.dbot.module_manager.api_pages.all():
            # pass
            # print(page, page.view_func)
            self.app.add_url_rule(rule=f"{api_base}/{page.path}",
                                  endpoint=page.path,
                                  view_func=_wrapper(self.guild_member_wrapper(page.view_func)),
                                  methods=page.methods)

    def run(self):
        http_server = WSGIServer((self.HOST, self.PORT), self.app)
        self.app.logger.debug('starting webserver on {}:{}'.format(self.HOST, self.PORT))
        if self.app.debug:
            self.app.logger.warning('app is running in debug mode')
        http_server.serve_forever()


def main():
    from settings import GLOBAL_SETTINGS

    logging.basicConfig()

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
