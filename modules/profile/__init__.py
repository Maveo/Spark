import discord
import discord.commands

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

        async def profile(ctx: discord.commands.context.ApplicationContext,
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

    async def member_create_profile_image_by_template(self, member, template):
        img_buf = await self.bot.image_creator.create(template(
            await self.bot.module_manager.create_extended_profile(member)
        ))
        return discord.File(filename="member.png", fp=img_buf)

    async def member_get_profile_image_template(self, member):
        return self.bot.module_manager.settings.get(member.guild.id, 'PROFILE_IMAGE')

    async def member_create_profile_image(self, member):
        return await self.member_create_profile_image_by_template(
            member, await self.member_get_profile_image_template(member))
