import re

from typing import *
import discord
from discord.utils import get
from imagestack import LinearGradientColor, ImageStackStringParser, SingleColor


def autocomplete_match(s: str, li: List[str]):
    sl = s.lower()
    return filter(lambda s2: sl in s2.lower(), li)


def make_linear_gradient(color_string: str) -> LinearGradientColor:
    stack_color = ImageStackStringParser(color_string).build()
    if not isinstance(stack_color, LinearGradientColor):
        stack_color = LinearGradientColor(SingleColor(stack_color), SingleColor(stack_color))
    return stack_color


def underscore_to_camelcase(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


async def give_role(guild, member: discord.Member, role_id):
    role = get(guild.roles, id=role_id)
    if role is not None and role not in member.roles:
        await member.add_roles(role)


async def remove_role(guild, member: discord.Member, role_id):
    role = get(guild.roles, id=role_id)
    if role is not None and role in member.roles:
        await member.remove_roles(role)


def search_member(guild, search):
    search = str(search)
    if search[:2] == '<@' and search[-1] == '>':
        search = search[2:-1]
        if search[0] == '!':
            search = search[1:]
    if search.isnumeric():
        member = get(guild.members, id=int(search))
        if member is not None and not member.bot:
            return member
    member = get(guild.members, nick=search)
    if member is not None and not member.bot:
        return member
    member = get(guild.members, name=search)
    if member is not None and not member.bot:
        return member
    return None


def search_channel(guild, search, t):
    if search[:2] == '<#' and search[-1] == '>':
        search = search[2:-1]
    if search.isnumeric():
        channel = get(guild.channels, id=int(search), type=t)
        if channel is not None:
            return channel
    channel = get(guild.channels, name=search, type=t)
    if channel is not None:
        return channel
    return None


def search_text_channel(guild, search):
    return search_channel(guild, search, discord.ChannelType.text)


def search_voice_channel(guild, search):
    return search_channel(guild, search, discord.ChannelType.voice)


def only_emojis(text):
    # TO-DO: don't hardcode this
    text = text.replace('️', '')
    regex_pattern = re.compile("[^"
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\U00002500-\U00002BEF"
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", re.UNICODE)
    return regex_pattern.sub(r'', text)


def simple_eval(wanted_type, value):
    if wanted_type is bool:
        return str(value).lower() in ['1', 'true']
    return wanted_type(value)
