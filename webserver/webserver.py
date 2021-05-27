import os
import threading
import asyncio
from flask import Flask, session, redirect, request, url_for, render_template
from requests_oauthlib import OAuth2Session
import logging


class WebServer(threading.Thread):
    async def is_signed_in(self):
        return session.get('oauth2_token') is not None

    async def entry(self):
        return render_template('login.html')

    async def login(self):
        if await self.is_signed_in():
            return redirect(url_for('/home'))
        scope = request.args.get(
            'scope',
            'identify email guilds'
        )
        discord = self.make_session(scope=scope.split(' '))
        authorization_url, state = discord.authorization_url(self.AUTHORIZATION_BASE_URL)
        session['oauth2_state'] = state
        return redirect(authorization_url)

    async def logout(self):
        session.clear()
        return redirect(url_for('/'))

    async def oath2(self):
        if request.values.get('error'):
            return request.values['error']
        discord = self.make_session(state=session.get('oauth2_state'))
        token = discord.fetch_token(
            token_url=self.TOKEN_URL,
            client_id=self.OAUTH2_CLIENT_ID,
            client_secret=self.OAUTH2_CLIENT_SECRET,
            authorization_response=request.url
        )
        session['oauth2_token'] = token
        return redirect(url_for('/home'))

    async def home(self):
        if not await self.is_signed_in():
            return redirect(url_for('/'))
        discord = self.make_session(token=session.get('oauth2_token'))

        while True:
            guilds_response = discord.get(self.API_BASE_URL + '/users/@me/guilds')
            if guilds_response.status_code == 200:
                break
            response_json = guilds_response.json()
            if 'retry_after' in response_json:
                await asyncio.sleep(int(response_json['retry_after']/1000))
            else:
                return render_template('error.html')

        user_guild_ids = list(map(lambda x: int(x['id']), guilds_response.json()))
        guilds = [x for x in self.dbot.bot.guilds if x.id in user_guild_ids]
        return render_template('home.html', guilds=guilds)

    async def guild(self, guild_id, **kwargs):
        if not await self.is_signed_in():
            return redirect(url_for('/'))
        try:
            guild_id = int(guild_id)
        except ValueError:
            return render_template('not_in_guild.html')
        guilds = list(filter(lambda x: x.id == guild_id, self.dbot.bot.guilds))
        if len(guilds) != 1:
            return render_template('not_in_guild.html')
        guild = guilds[0]
        ranked_users = await self.dbot.get_ranking(guild)
        user_infos = await self.dbot.get_advanced_user_infos(guild, ranked_users)
        return render_template('guild.html', guild=guilds[0], ranking=user_infos)

    def __init__(self,
                 name='Webserver',
                 host='0.0.0.0',
                 port=4004,
                 discord_bot=None,
                 oath2_client_id=None,
                 oath2_client_secret=None,
                 oath2_redirect_uri=None,
                 debug=False,
                 logging_level=logging.WARNING
                 ):
        super().__init__()

        log = logging.getLogger('werkzeug')
        log.setLevel(logging_level)

        self.HOST = host
        self.PORT = port

        self.dbot = discord_bot

        self.OAUTH2_CLIENT_ID = oath2_client_id
        self.OAUTH2_CLIENT_SECRET = oath2_client_secret
        self.OAUTH2_REDIRECT_URI = oath2_redirect_uri

        if 'http://' in self.OAUTH2_REDIRECT_URI:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

        self.API_BASE_URL = 'https://discordapp.com/api'
        self.AUTHORIZATION_BASE_URL = self.API_BASE_URL + '/oauth2/authorize'
        self.TOKEN_URL = self.API_BASE_URL + '/oauth2/token'

        self.app = Flask(
            name,
            root_path=os.path.dirname(os.path.abspath(__file__)),
            template_folder='templates',
            static_folder='static',
        )
        self.app.debug = debug
        self.app.config['SECRET_KEY'] = self.OAUTH2_CLIENT_SECRET

        self.pages = {
            '/': self.entry,
            '/login': self.login,
            '/logout': self.logout,
            '/oath2': self.oath2,
            '/home': self.home,
            '/guild/<string:guild_id>/': self.guild,
            '/guild/<string:guild_id>/<path:path>': self.guild,
        }

        def _wrapper(func):
            def _call(*args, **kwargs):
                loop = asyncio.new_event_loop()
                task = loop.create_task(func(*args, **kwargs))
                res = loop.run_until_complete(task)
                return res
            return _call

        for key, value in self.pages.items():
            self.app.add_url_rule(rule=key, endpoint=key, view_func=_wrapper(value))

    @staticmethod
    def token_updater(token):
        session['oauth2_token'] = token

    def make_session(self, token=None, state=None, scope=None):
        return OAuth2Session(
            client_id=self.OAUTH2_CLIENT_ID,
            token=token,
            state=state,
            scope=scope,
            redirect_uri=self.OAUTH2_REDIRECT_URI,
            auto_refresh_kwargs={
                'client_id': self.OAUTH2_CLIENT_ID,
                'client_secret': self.OAUTH2_CLIENT_SECRET,
            },
            auto_refresh_url=self.TOKEN_URL,
            token_updater=self.token_updater)

    def run(self):
        self.app.run(host=self.HOST, port=self.PORT)


def main():
    from settings import GLOBAL_SETTINGS

    a = WebServer(
        oath2_client_id=GLOBAL_SETTINGS['APPLICATION_ID'],
        oath2_client_secret=GLOBAL_SETTINGS['APPLICATION_SECRET'],
        oath2_redirect_uri=GLOBAL_SETTINGS['OATH2_REDIRECT_URI'],
        debug=True
    )
    a.run()
    # a.start()


if __name__ == '__main__':
    main()
