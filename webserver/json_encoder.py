import json
from typing import TYPE_CHECKING

from discord import Member, ClientUser, User, Guild, Invite, TextChannel, VoiceChannel, Message, Permissions
from fastapi.responses import JSONResponse

from helpers.db import InventoryItemType, WheelspinProbability
from helpers.dummys import MemberDummy
from datetime import datetime
from imagestack_svg.imageresolve import ImageStackResolveString

from helpers.spark_module import SparkModule

if TYPE_CHECKING:
    from bot import DiscordBot


def create_custom_json_response_class(bot: 'DiscordBot'):
    class CustomEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return datetime.timestamp(o) * 1000

            if isinstance(o, Member) or isinstance(o, MemberDummy):
                return {
                    'id': str(o.id),
                    'tag': str(o.discriminator),
                    'nick': str(o.display_name),
                    'name': str(o.name),
                    'avatar_url': str(o.display_avatar),
                    'top_role': str(o.top_role.name),
                }
            if isinstance(o, ClientUser) or isinstance(o, User):
                return {
                    'id': str(o.id),
                    'nick': str(o.display_name),
                    'name': str(o.name),
                    'avatar_url': str(o.display_avatar),
                }
            if isinstance(o, Guild):
                icon_url = o.icon
                if icon_url is not None:
                    icon_url = str(icon_url)
                return {
                    'id': str(o.id),
                    'name': str(o.name),
                    'icon_url': icon_url,
                    'active_modules': bot.module_manager.get_activated_modules(o.id)
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
            if isinstance(o, Permissions):
                return {perm: getattr(o, perm) for perm in Permissions.VALID_FLAGS.keys()}
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

            if isinstance(o, SparkModule):
                return {
                    'name': o.name,
                    'title': o.title,
                    'description': o.description,
                    'dependencies': o.dependencies,
                    'dependency_for': o.dependency_for,
                    'is_optional': o.optional
                }

            if isinstance(o, SparkModule):
                return {
                    'name': o.name,
                    'title': o.title,
                    'description': o.description,
                    'dependencies': o.dependencies,
                    'dependency_for': o.dependency_for,
                    'is_optional': o.optional
                }

            if isinstance(o, InventoryItemType):
                return {
                    'id': o.id,
                    'name': o.name,
                    'rarity_id': o.rarity_id,
                    'always_visible': o.always_visible,
                    'tradable': o.tradable,
                    'equippable': o.equippable,
                    'useable': o.useable,
                    'actions': json.loads(o.actions),
                }

            if isinstance(o, WheelspinProbability):
                return {
                    'id': o.id,
                    'item_type_id': o.item_type_id,
                    'probability': o.probability,
                    'amount': o.amount,
                    'sound': o.sound,
                }
            return json.JSONEncoder.default(self, o)

    class CustomJSONResponse(JSONResponse):
        def render(self, content) -> bytes:
            return json.dumps(
                content,
                cls=CustomEncoder,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")

    return CustomJSONResponse
