import re

from typing import *
import discord
from discord.utils import get


def autocomplete_match(s: str, li: List[str]):
    sl = s.lower()
    return filter(lambda s2: sl in s2.lower(), li)


def make_linear_gradient(color_string: str) -> Tuple:
    if color_string.startswith('LinearGradientColor'):
        color_string = color_string[20:-1]
    color_string = ''.join(color_string.split())
    spl = color_string.split('),(')
    if len(spl) == 1:
        t = tuple([int(x) for x in spl[0][1:-1].split(',')])
        return t, t
    return tuple([int(x) for x in spl[0][1:].split(',')]), tuple([int(x) for x in spl[1].split(')')[0].split(',')])


def svg_color_definition_with_id(color1: Tuple, color2: Tuple, cid: str):
    return '<linearGradient id="{}">\n' \
           '<stop offset="0%" stop-color="rgb({}, {}, {})" />\n' \
            '<stop offset="100%" stop-color="rgb({}, {}, {})" />\n' \
           '</linearGradient>'.format(cid, color1[0], color1[1], color1[2], color2[0], color2[1], color2[2])


def html_color(color1: Tuple, color2: Tuple):
    return 'linear-gradient(to right, rgb({}, {}, {}), rgb({}, {}, {}));'.format(
        color1[0], color1[1], color1[2], color2[0], color2[1], color2[2])


def decapitalize(s):
    if not s:
        return s
    return s[0].lower() + s[1:]


def underscore_to_camelcase(word):
    return ''.join(x.capitalize() for x in word.split('_'))


def underscore_to_spaces(word):
    return ' '.join(x for x in word.split('_'))


def camelcase_to_underscore(word):
    found = re.findall('[A-Z][^A-Z]*', word)
    if len(found) == 0:
        return decapitalize(word)
    return '_'.join(decapitalize(x) for x in found)


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


def is_valid_emoji(emoji):
    t = discord.PartialEmoji.from_str(emoji)
    if t.is_custom_emoji():
        return True
    if len(emoji) == len(only_emojis(emoji)) == 1:
        return True
    return False


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
