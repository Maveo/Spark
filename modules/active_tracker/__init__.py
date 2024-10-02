import time

from helpers.spark_module import SparkModule
from helpers.tools import previous_timestamp_unix, search_text_channel
from .settings import SETTINGS
from .web import API_PAGES
import discord
from discord.utils import get


class ActiveTrackerModule(SparkModule):
    name = 'active_tracker'
    title = 'Active Tracker'
    description = 'This module tracks how active users are.'
    dependencies = []
    api_pages = API_PAGES
    settings = SETTINGS

    def __init__(self, bot):
        super().__init__(bot)

        async def activity_leaderboard(ctx: discord.ApplicationContext):
            await ctx.defer()
            await ctx.respond(file=await self.create_activity_leaderboard_image(ctx.author.guild))

        self.commands = [
            discord.SlashCommand(
                func=activity_leaderboard,
                name=self.bot.i18n.get('ACTIVITY_LEADERBOARD_COMMAND'),
                description=self.bot.i18n.get('ACTIVITY_LEADERBOARD_COMMAND_DESCRIPTION'),
            )
        ]

    async def interval_update(self, current_time, guild: discord.Guild):
        await self.check_send_activity_message(guild, current_time)

        for voice_channel in guild.voice_channels:
            if voice_channel.id != guild.afk_channel.id:
                for member in voice_channel.members:
                    await self.track_mute(member, current_time)

    async def check_send_activity_message(self, guild: discord.Guild, current_time):
        channel_id = self.bot.module_manager.settings.get(guild.id, 'ACTIVITY_IMAGE_INTERVAL_CHANNEL')
        if channel_id == '':
            return
        channel = search_text_channel(guild, channel_id)
        if channel is None:
            return
        activity_message = self.bot.db.get_activity_message(guild.id)

        interval = 3600 * self.bot.module_manager.settings.get(guild.id, 'ACTIVITY_IMAGE_INTERVAL_HOURS')
        interval_start = 3600 * self.bot.module_manager.settings.get(guild.id, 'ACTIVITY_IMAGE_INTERVAL_START_TIME')

        wanted_last_message = int(previous_timestamp_unix(interval_start, interval, current_time))

        if activity_message is not None and activity_message.last_sent == wanted_last_message:
            return

        await channel.send(file=await self.create_activity_leaderboard_image(guild))
        users = self.bot.db.get_active_tracked_users(guild.id)
        for user in users:
            self.bot.db.update_active_tracked_user(guild.id, user.user_id, {'interval_muted_time': 0})
        self.bot.db.update_activity_message(guild.id, {'last_sent': wanted_last_message})


    async def on_voice_state_update(self,
                                member: discord.Member,
                                before: discord.VoiceState,
                                after: discord.VoiceState):
        if not await self.active_tracking_allowed(member):
            return
        t = time.time()
        await self.track_mute(member, t)

    async def check_active_tracked_user(self, member: discord.Member):
        if self.bot.db.get_active_tracked_user(member.guild.id, member.id) is None:
            self.bot.db.update_active_tracked_user(member.guild.id, member.id, {
                'interval_muted_time': 0,
                'muted_time': 0,
            })

    async def is_muted(self, member: discord.Member):
        return member.voice is not None and (member.voice.self_mute or member.voice.mute)

    async def track_mute(self, member: discord.Member, current_time):
        if not await self.active_tracking_allowed(member):
            return
        
        await self.check_active_tracked_user(member)
        active_tracked_user = self.bot.db.get_active_tracked_user(member.guild.id, member.id)

        muted = await self.is_muted(member)
        if active_tracked_user.last_muted is None and not muted:
            return
        
        if active_tracked_user.last_muted is None and muted:
            self.bot.db.update_active_tracked_user(member.guild.id, member.id, {'last_muted': current_time})
            return

        self.bot.db.update_active_tracked_user(member.guild.id, member.id, {
            'interval_muted_time': active_tracked_user.interval_muted_time + current_time - active_tracked_user.last_muted,
            'muted_time': active_tracked_user.muted_time + current_time - active_tracked_user.last_muted,
            'last_muted': current_time if muted else None,
        })
        

    async def active_tracking_allowed(self, member: discord.Member):
        return self.bot.module_manager.settings.get(member.guild.id, 'ALLOW_BOT_ACTIVE_TRACKING') or not member.bot

    async def get_interval_ranking_rank(self, member):
        return list(map(lambda x: x.user_id, await self.get_interval_ranking(member.guild))).index(member.id) + 1

    async def get_interval_ranking(self, guild):
        users = self.bot.db.get_active_tracked_users(guild.id)
        users = sorted(users, key=lambda x: x.interval_muted_time, reverse=True)
        for i in range(len(users)):
            users[i].rank = i + 1
        return users
    
    async def get_advanced_user_infos(self, member, user):
        name = member.display_name
        return {
            'member': member,
            'rank': user.rank,
            'name': name,
            'color': member.color.to_rgb(),
            'avatar_url': str(member.display_avatar.with_format('png')),
            'muted_time': user.muted_time,
            'interval_muted_time': user.interval_muted_time,
        }
    
    async def get_advanced_acive_tracked_user_infos(self, member):
        user = self.bot.db.get_active_tracked_user(member.guild.id, member.id)
        user.rank = await self.get_interval_ranking_rank(member)
        return await self.get_advanced_user_infos(member, user)

    async def users_get_advanced_infos(self, guild, active_users):
        user_infos = []
        for user in active_users:
            member = get(guild.members, id=int(user.user_id))
            if member is not None and await self.active_tracking_allowed(member):
                user_infos.append(await self.get_advanced_user_infos(member, user))
        return user_infos

    async def create_activity_image_by_template(self, guild, activity_users, template):
        data_obj = await self.users_get_advanced_infos(guild, activity_users)
        activity_message = self.bot.db.get_activity_message(guild.id)
        last_interval = 0
        current_duration = 0
        if activity_message is not None:
            last_interval = activity_message.last_interval
            current_duration = time.time() - last_interval
        img_buf = await self.bot.image_creator.create_bytes(template(users=data_obj, last_interval=last_interval, current_duration=current_duration), max_size=(-1, 8000))
        return discord.File(filename="activity.png", fp=img_buf)

    async def create_activity_image(self, guild, ranked_users):
        return await self.create_activity_image_by_template(
            guild, ranked_users, self.bot.module_manager.settings.get(guild.id, 'ACTIVITY_IMAGE'))

    async def create_activity_leaderboard_image_by_template(self, guild, template):
        ranking = await self.get_interval_ranking(guild)
        return await self.create_activity_image_by_template(
            guild, ranking[:self.bot.module_manager.settings.get(guild.id, 'ACTIVITY_LEADERBOARD_AMOUNT')], template)

    async def create_activity_leaderboard_image(self, guild):
        ranking = await self.get_interval_ranking(guild)
        return await self.create_activity_image(
            guild, ranking[:self.bot.module_manager.settings.get(guild.id, 'ACTIVITY_LEADERBOARD_AMOUNT')])
