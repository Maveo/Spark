import os
import threading
import asyncio
from flask import Flask, session, redirect, request, url_for, render_template, jsonify
from imagestack import VisitorHtml, ImageStackResolve, ImageStack, ListLayer, LengthVariable
from requests_oauthlib import OAuth2Session
import logging


class Page:
    def __init__(self, path, view_func, methods=None):
        self.path = path
        self.view_func = view_func
        if methods is None:
            methods = ['GET']
        self.methods = methods


class WebServer(threading.Thread):
    async def is_signed_in(self):
        return session.get('oauth2_token') is not None

    async def get_member_id(self):
        if session.get('member_id') is None:
            discord = self.make_session(token=session.get('oauth2_token'))

            while True:
                user_response = discord.get(self.API_BASE_URL + '/users/@me')
                if user_response.status_code == 200:
                    break
                response_json = user_response.json()
                if 'retry_after' in response_json:
                    await asyncio.sleep(int(response_json['retry_after']/1000))
                else:
                    raise Exception('could not find id in response')

            session['member_id'] = int(user_response.json()['id'])

        return session.get('member_id')

    async def entry(self):
        return render_template('login.html')

    async def login(self):
        if await self.is_signed_in():
            return redirect(url_for('/home'))
        scope = request.args.get(
            'scope',
            'identify'
        )
        discord = self.make_session(scope=scope.split(' '))
        authorization_url, state = discord.authorization_url(self.AUTHORIZATION_BASE_URL)
        session['oauth2_state'] = state
        return redirect(authorization_url)

    async def logout(self):
        session.clear()
        return redirect(url_for('/'))

    async def oauth2(self):
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

        guilds = [guild for guild in self.dbot.bot.guilds
                  if guild.get_member(await self.get_member_id()) is not None]
        return render_template('home.html', guilds=guilds)

    async def guild(self, guild_id, **kwargs):
        if not await self.is_signed_in():
            return redirect(url_for('/'))

        try:
            guild_id = int(guild_id)
        except ValueError:
            return render_template('guild-not-in.html')
        guilds = list(filter(lambda x: x.id == guild_id, self.dbot.bot.guilds))
        if len(guilds) != 1:
            return render_template('guild-not-in.html')
        guild = guilds[0]
        member = guild.get_member(await self.get_member_id())
        if member is None:
            return render_template('guild-not-in.html')

        if 'path' in kwargs and kwargs['path'] == 'settings':
            if not member.guild_permissions.administrator:
                return render_template('guild-no-permissions.html')

            if request.method == 'POST':
                res = await self.dbot.set_setting(guild.id, request.form['key'], request.form['value'])
                if not res:
                    return jsonify('Value could not be set'), 400
                setting = await self.dbot.get_setting(guild.id, request.form['key'])
                return jsonify(str(setting)), 200
            settings = await self.dbot.get_settings(guild.id)
            return render_template('guild-settings.html',
                                   guild=guild,
                                   settings=settings)
        ranked_users = await self.dbot.get_ranking(guild)
        user_infos = await self.dbot.get_advanced_user_infos(guild, ranked_users)

        profile_template = await self.dbot.get_setting(guild.id, 'PROFILE_IMAGE')
        users_html = []
        v = None
        for user in user_infos:
            user_image = profile_template(user)
            v = VisitorHtml(self.dbot.image_creator)
            layers_html = []
            for layer in user_image.layers:
                layers_html.append(layer.accept(v))
            users_html.append('<div style="display:flex;" data-tilt data-tilt-scale="1.05" data-tilt-max="5">'
                              '<div style="position:relative;width:{}px;height:{}px;margin-bottom:20px;">'
                              '{}'
                              '</div>'
                              '</div>'
                              .format(v.max_size[0], v.max_size[1], ''.join(layers_html)))
        style = None
        if v is not None:
            style = v.style_html()
        ranking_html = '<style>{}</style><div style="position:relative;">{}</div>'.format(style, ''.join(users_html))
        # im = (await self.dbot.get_setting(guild.id, 'RANKING_IMAGE'))(user_infos)
        #
        # ranking_html = self.dbot.image_creator.create_html(im)

        return render_template('guild-leaderboard.html', guild=guild, ranking_html=ranking_html)

    def __init__(self,
                 name='Webserver',
                 host='0.0.0.0',
                 port=4004,
                 discord_bot=None,
                 oauth2_client_id=None,
                 oauth2_client_secret=None,
                 oauth2_redirect_uri=None,
                 debug=False,
                 logging_level=logging.WARNING
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

        self.pages = [
            Page(path='/', view_func=self.entry),
            Page(path='/login', view_func=self.login),
            Page(path='/logout', view_func=self.logout),
            Page(path='/oauth2', view_func=self.oauth2),
            Page(path='/home', view_func=self.home),
            Page(path='/guild/<string:guild_id>/', view_func=self.guild),
            Page(path='/guild/<string:guild_id>/<path:path>', view_func=self.guild, methods=['GET', 'POST']),
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
        oauth2_client_id=GLOBAL_SETTINGS['APPLICATION_ID'],
        oauth2_client_secret=GLOBAL_SETTINGS['APPLICATION_SECRET'],
        oauth2_redirect_uri=GLOBAL_SETTINGS['OAUTH2_REDIRECT_URI'],
        debug=True
    )
    a.run()
    # a.start()


if __name__ == '__main__':
    main()
