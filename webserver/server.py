import inspect
import os
import logging
import requests
import uvicorn
from fastapi import FastAPI, Header, Body
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from helpers.dummys import MemberDummy
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from helpers.exceptions import *

from typing import TYPE_CHECKING

from webserver.json_encoder import create_custom_json_response_class

if TYPE_CHECKING:
    from bot import DiscordBot


class Page:
    def __init__(self, path, view_func, methods=None, **kwargs):
        self.path = path
        self.view_func = view_func
        if methods is None:
            methods = ['GET']
        self.methods = methods
        self.kwargs = kwargs

    def new(self, path=None, view_func=None, methods=None, **kwargs):
        if path is None:
            path = self.path
        if view_func is None:
            view_func = self.view_func
        if methods is None:
            methods = self.methods
        for key, value in kwargs.items():
            self.kwargs[key] = value
        return Page(path, view_func, methods, **self.kwargs)

    def add_to_app(self, app: FastAPI, path_prefix: str = '', wrapper=None, **kwargs):
        func = self.view_func
        if wrapper is not None:
            func = wrapper(func)
        api_kwargs = self.kwargs.copy()
        for key, value in kwargs.items():
            api_kwargs[key] = value
        if 'name' not in self.kwargs:
            api_kwargs['name'] = self.path
        app.add_api_route(path=f'{path_prefix}{self.path}',
                          endpoint=func,
                          methods=self.methods,
                          **api_kwargs)


class WebServer:
    def encrypt(self, s):
        return self.crypter.encrypt(s.encode()).decode()

    def decrypt(self, s):
        return self.crypter.decrypt(s.encode()).decode()

    async def get_member_id(
            self,
            authorization_token: str,
    ):
        token = self.decrypt(authorization_token)
        r = requests.get('https://discord.com/api/users/@me', headers={
            'Authorization': token
        })
        if r.status_code != 200:
            raise UnauthorizedException(detail='member request not successful')
        json = r.json()
        if 'id' not in json:
            raise UnauthorizedException(detail='id not in member response')
        return int(json['id'])

    async def get_member_guild(
            self,
            authorization_token: str,
            guild_id: str,
    ):
        try:
            guild_id = int(guild_id)
        except ValueError and TypeError:
            raise WrongInputException(detail='guild id wrong format')
        uid = await self.get_member_id(authorization_token)
        guilds = list(filter(lambda x: x.id == guild_id, self.dbot.bot.guilds))
        if len(guilds) != 1:
            raise WrongInputException(detail='guild not found')
        guild = guilds[0]
        member = guild.get_member(uid)
        if member is None:
            if not self.dbot.is_super_admin(uid):
                raise WrongInputException(detail='member not found')
            member = MemberDummy(uid=uid)
        return guild, member

    async def get_auth_url(self):
        return self.JSONResponse({
            'auth_url':
                'https://discord.com/api/oauth2/authorize?client_id={}&redirect_uri={}&response_type={}&scope={}'.format(
                    self.OAUTH2_CLIENT_ID,
                    self.OAUTH2_REDIRECT_URI,
                    'code',
                    'identify'
                )
        })

    async def create_session(
            self,
            code: str = Body(embed=True),
    ):
        r = requests.post('https://discord.com/api/oauth2/token', data={
            'client_id': self.OAUTH2_CLIENT_ID,
            'client_secret': self.OAUTH2_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.OAUTH2_REDIRECT_URI,
            'scope': 'identify'
        })
        if r.status_code != 200:
            raise UnauthorizedException()
        json = r.json()
        if 'access_token' not in json or 'token_type' not in json:
            raise UnauthorizedException()
        encrypted = self.encrypt('{} {}'.format(json['token_type'], json['access_token']))
        return self.JSONResponse({'session_token': encrypted})

    async def get_guild(
            self,
            guild_id: str,
            authorization: str = Header(),
    ):
        guild, member = await self.get_member_guild(authorization, guild_id)
        return self.JSONResponse(guild)

    async def get_guilds(
            self,
            authorization: str = Header(),
    ):
        uid = await self.get_member_id(authorization)
        return self.JSONResponse({'guilds': [
            guild
            for guild in self.dbot.bot.guilds
            if self.dbot.is_super_admin(uid) or guild.get_member(uid) is not None
        ]})

    async def get_i18n(self):
        return self.JSONResponse({'i18n': self.dbot.i18n.raw()})

    def guild_member_wrapper(self, func):

        async def _call(
                guild_id: str,
                authorization: str = Header(),
                *args,
                **kwargs,
        ):
            if guild_id is None:
                raise WrongInputException(detail='guild_id_missing')
            guild, member = await self.get_member_guild(authorization, guild_id)
            response = await func(guild, member, *args, **kwargs)
            if not issubclass(type(response), Response):
                response = self.JSONResponse(response)
            return response

        old_signature = inspect.signature(func)

        params = list(old_signature.parameters.values())

        new_params = list(inspect.signature(_call).parameters.values())

        params.remove(params[0])
        params.remove(params[0])
        params.remove(params[0])

        params.insert(0, new_params[0])
        params.append(new_params[1])

        _call.__signature__ = old_signature.replace(parameters=params)

        return _call

    def __init__(self,
                 discord_bot: 'DiscordBot' = None,
                 oauth2_client_id=None,
                 oauth2_client_secret=None,
                 oauth2_redirect_uri=None,
                 webserver_secret=None,
                 static_path='',
                 debug=False,
                 api_base='fap'
                 ):
        super().__init__()

        self.dbot = discord_bot
        self.JSONResponse = create_custom_json_response_class(self.dbot)

        self.OAUTH2_CLIENT_ID = oauth2_client_id
        self.OAUTH2_CLIENT_SECRET = oauth2_client_secret
        self.OAUTH2_REDIRECT_URI = oauth2_redirect_uri

        self.API_BASE_URL = 'https://discordapp.com/api'
        self.AUTHORIZATION_BASE_URL = self.API_BASE_URL + '/oauth2/authorize'
        self.TOKEN_URL = self.API_BASE_URL + '/oauth2/token'

        if webserver_secret is None:
            webserver_secret = Fernet.generate_key()
        else:
            digest = hashes.Hash(hashes.SHA256())
            digest.update(webserver_secret.encode())
            webserver_secret = base64.urlsafe_b64encode(digest.finalize())
        self.crypter = Fernet(webserver_secret)

        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.static_path = os.path.join(self.root_path, static_path)
        self.app = FastAPI(
            debug=debug,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
        )
        self.app.logger = logging.getLogger('sparkbot-webserver')

        if debug:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=['*'],
                allow_methods=['*'],
                allow_headers=['*'],
            )

        async def send_root():
            return FileResponse(os.path.join(self.static_path, 'index.html'))

        async def static_file(path: str):
            if path.startswith(api_base):
                raise NotFoundException()
            p = os.path.join(self.static_path, path)
            if os.path.isdir(p):
                if p[-1] != '/':
                    return RedirectResponse(path + '/')
                if os.path.isfile(p + 'index.html'):
                    return FileResponse(os.path.join(self.static_path, path + 'index.html'))
            elif os.path.exists(p):
                return FileResponse(os.path.join(self.static_path, path))
            return await send_root()

        api_pages = [
            Page(path='i18n', view_func=self.get_i18n),
            Page(path='get-auth', view_func=self.get_auth_url),
            Page(path='create-session', view_func=self.create_session, methods=['POST']),
            Page(path='guild', view_func=self.get_guild),
            Page(path='guilds', view_func=self.get_guilds),
        ]

        static_pages = [
            Page(path='/', view_func=send_root, include_in_schema=False),
            Page(path='/{path:path}', view_func=static_file, include_in_schema=False),
        ]

        for page in api_pages:
            page.add_to_app(self.app,
                            path_prefix=f'/{api_base}/',
                            tags=['core'])

        if self.dbot is not None:
            for module_name, pages in self.dbot.module_manager.api_pages.items():
                for page in pages:
                    page.add_to_app(self.app,
                                    path_prefix=f'/{api_base}/',
                                    wrapper=self.guild_member_wrapper,
                                    tags=['module '+module_name])

        for page in static_pages:
            page.add_to_app(self.app)

    def run(self):
        uvicorn.run(self.app)


def main():
    from settings import GLOBAL_SETTINGS

    server = WebServer(
        oauth2_client_id=GLOBAL_SETTINGS['APPLICATION_ID'],
        oauth2_client_secret=GLOBAL_SETTINGS['APPLICATION_SECRET'],
        oauth2_redirect_uri=GLOBAL_SETTINGS['OAUTH2_REDIRECT_URI'],
        static_path=GLOBAL_SETTINGS['WEBSERVER_STATIC_PATH'],
        debug=GLOBAL_SETTINGS['WEBSERVER_DEBUG']
    )
    server.run()


if __name__ == '__main__':
    main()
