from datetime import date
from discord import PublicUserFlags


class ColorDummy:
    def __init__(self, rgb=(0, 255, 0)):
        self.rgb = rgb

    def to_rgb(self):
        return self.rgb


class RoleDummy:
    def __init__(self, uid=0, name='✅DummyRole', color=None):
        self.id = uid
        self.name = name
        if color is None:
            color = ColorDummy()
        self.color = color


class ChannelDummy:
    def __init__(self, uid=0):
        self.id = uid
        self.messages = []

    async def send(self, *args, **kwargs):
        self.messages.append((args, kwargs))


class GuildDummy:
    def __init__(self, uid=0, roles=None, system_channel=None):
        self.id = uid
        self.roles = roles
        self.members = []
        if self.roles is None:
            self.roles = []
        if system_channel is None:
            system_channel = ChannelDummy()
        self.system_channel = system_channel
        self.icon_url = 'https://cdn.discordapp.com/icons/188893186435973121/a_71ba803956e5189b9dab7d5d2d6b331f.png'

    def member_join(self, member):
        self.members.append(member)

    def icon_url_as(self, *args, **kwargs):
        return self.icon_url


class VoiceDummy:
    def __init__(self, channel=None):
        if channel is None:
            channel = ChannelDummy()
        self.channel = channel


class MemberDummy:
    def __init__(self,
                 uid=0,
                 name='Dummy',
                 nick='Dummy',
                 display_name='Dummy',
                 guild=None,
                 bot=False,
                 voice=None):
        self.id = uid
        self.name = name
        self.nick = nick
        self.display_name = display_name
        self.avatar_url = 'https://cdn.discordapp.com/emojis/722162010514653226.png?v=1'
        self.roles = {}
        self.top_role = RoleDummy(0)
        self.discriminator = uid
        self.public_flags = PublicUserFlags()
        self.created_at = date.today()
        self.joined_at = date.today()
        self.premium_since = None
        if guild is None:
            guild = GuildDummy()
        self.guild = guild
        self.guild.member_join(self)
        if voice is None:
            voice = VoiceDummy()
        self.voice = voice
        self.bot = bot
        self.color = ColorDummy()
        self.messages = []

    async def send(self, *args, **kwargs):
        self.messages.append((args, kwargs))

    async def add_roles(self, role):
        self.roles[role.id] = True

    async def remove_roles(self, role):
        if role.id in self.roles:
            del self.roles[role.id]

    def avatar_url_as(self, *args, **kwargs):
        return self.avatar_url


class MessageDummy:
    def __init__(self, uid=0, content='', author=None, guild=None, channel=None):
        self.id = uid
        self.content = content
        if author is None:
            author = MemberDummy()
        self.author = author
        if guild is None:
            guild = GuildDummy()
        self.guild = guild
        if channel is None:
            channel = ChannelDummy()
        self.channel = channel
