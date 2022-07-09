import discord
import discord.commands

from helpers.module_hook_manager import INVENTORY_ITEM_ACTION_HOOK, INVENTORY_EQUIPPED_ITEMS_HOOK
from helpers.spark_module import SparkModule
from .settings import SETTINGS
from .web import API_PAGES


class ProfileModule(SparkModule):
    name = 'profile'
    title = 'Profiler Module'
    description = 'A module to display user profile'
    api_pages = API_PAGES
    settings = SETTINGS

    def __init__(self, bot):
        super().__init__(bot)

        async def profile(ctx: discord.ApplicationContext,
                          member: discord.commands.Option(
                              discord.Member,
                              description=bot.i18n.get('LEVELSYSTEM_PROFILE_MEMBER_OPTION'),
                              default=None
                          )):
            if member is None:
                member = ctx.author

            await ctx.defer()

            await ctx.respond(file=await self.member_create_profile_image(member))

        self.commands = [
            discord.SlashCommand(
                func=profile,
                name=self.bot.i18n.get('LEVELSYSTEM_PROFILE_COMMAND'),
                description=self.bot.i18n.get('LEVELSYSTEM_PROFILE_COMMAND_DESCRIPTION'),
            )
        ]

        async def set_custom_profile_card(member: discord.Member, amount, equipped, options):
            pass

        self.bot.module_manager.hooks.add(
            self,
            INVENTORY_ITEM_ACTION_HOOK,
            hook_id='custom-profile-card',
            name='Custom Profile Card',
            options={
                'template': {
                    'type': 'text',
                    'description': self.bot.i18n.get('CUSTOM_PROFILE_CARD_TEMPLATE_DESCRIPTION')
                },
            },
            callback=set_custom_profile_card
        )

        async def replace_custom_profile(member: discord.Member, amount, equipped, options):
            pass

        self.bot.module_manager.hooks.add(
            self,
            INVENTORY_ITEM_ACTION_HOOK,
            hook_id='custom-profile-replace',
            name='Custom Profile Replace',
            options={
                'replace_id': {
                    'type': 'str',
                    'description': 'Replace Id'
                },
                'replace_content': {
                    'type': 'str',
                    'description': 'New content'
                },
            },
            callback=replace_custom_profile
        )

    async def member_create_profile_image_by_template(self, member, template):
        img_buf = await self.bot.image_creator.create_bytes(template(
            **(await self.bot.module_manager.create_extended_profile(member))))
        return discord.File(filename="member.png", fp=img_buf)

    async def member_get_profile_image_template(self, member):
        hook = self.bot.module_manager.hooks.get_one(member.guild.id, INVENTORY_EQUIPPED_ITEMS_HOOK, 'inventory')
        if hook is not None:
            profile_cards = await hook['callback'](member, 'custom-profile-card')
            if profile_cards:
                return self.bot.module_manager.settings.preview(member.guild.id,
                                                                'PROFILE_IMAGE',
                                                                profile_cards[0]['template'])
        return self.bot.module_manager.settings.get(member.guild.id, 'PROFILE_IMAGE')

    async def member_create_profile_image(self, member):
        template = await self.member_get_profile_image_template(member)
        hook = self.bot.module_manager.hooks.get_one(member.guild.id, INVENTORY_EQUIPPED_ITEMS_HOOK, 'inventory')
        if hook is not None:
            profile_replaces = await hook['callback'](member, 'custom-profile-replace')
            for rep in profile_replaces:
                template = template.replace(rep['replace_id'], rep['replace_content'])
        return await self.member_create_profile_image_by_template(
            member, template)
