import asyncio
import random
import re
import time
from typing import List

import requests
from helpers.spark_module import SparkModule
from helpers.tools import is_valid_emoji
from .settings import SETTINGS
from .web import API_PAGES

import discord

class TournamentsModule(SparkModule):
    name = 'tournaments'
    title = 'Tournaments'
    description = 'Make Tournaments'
    dependencies = []
    api_pages = API_PAGES
    settings = SETTINGS

    async def create_ko_tournament_image_by_template(self, tree, template):
        rounds = []
        i = 1
        while i <= len(tree):
            rounds.append(tree[i-1:i*2-1])
            i *= 2

        img_buf = await self.bot.image_creator.create_bytes(template(rounds=rounds))
        return discord.File(filename="tournament.png", fp=img_buf)
    
    async def create_ko_tournament_image(self, guild_id, tree):
        return await self.create_ko_tournament_image_by_template(tree,
            self.bot.module_manager.settings.get(guild_id, 'KO_TOURNAMENT_IMAGE'))


    def __init__(self, bot):
        super().__init__(bot)

        async def ko_round(ctx: discord.ApplicationContext,
                           option1: str,
                           option2: str,
                           round_time_seconds: int,
                           voting_emoji1: str,
                           voting_emoji2: str,
                           ) -> str:
            msg1 = await ctx.send('{} {}'.format(voting_emoji1, option1))
            msg2 = await ctx.send('{} {}'.format(voting_emoji2, option2))
            msg = await ctx.send('{} seconds remaining...'.format(round_time_seconds))
            await msg.add_reaction(voting_emoji1)
            await msg.add_reaction(voting_emoji2)
            start_time = time.time()
            while True:
                await asyncio.sleep(1)
                remaining_time = round_time_seconds - time.time() + start_time
                if remaining_time < 0:
                    break
                await msg.edit('{:.0f} seconds remaining...'.format(remaining_time))

            msg = await msg.channel.fetch_message(msg.id)
            count1 = 0
            count2 = 0
            for r in msg.reactions:
                if str(r.emoji) == voting_emoji1:
                    count1 = r.count - 1
                elif str(r.emoji) == voting_emoji2:
                    count2 = r.count - 1
            winner = option1
            if count2 > count1:
                winner = option2
            elif count1 == count2 and random.random() < 0.5:
                winner = option2
            await msg1.delete()
            await msg2.delete()
            await msg.delete()
            return winner, count1, count2

        async def ko_tournament(ctx: discord.ApplicationContext,
                                options: List[str],
                                round_time_seconds: int,
                                voting_emoji1: str,
                                voting_emoji2: str,
                                ):
            if len(options) == 0:
                await ctx.respond(embed=discord.Embed(title='No tournament participants provided!',
                                                      color=discord.Color.red()), ephemeral=True)
                return
            if round_time_seconds <= 0:
                await ctx.respond(embed=discord.Embed(title='Round time has to be bigger 0!',
                                                      color=discord.Color.red()), ephemeral=True)
                return
            if voting_emoji1 == voting_emoji2:
                await ctx.respond(embed=discord.Embed(title='Voting emojis for option one and two are the same: "{}"!'.format(voting_emoji1),
                                                      color=discord.Color.red()), ephemeral=True)
                return
            if not is_valid_emoji(voting_emoji1):
                await ctx.respond(embed=discord.Embed(title='"{}" is not a valid emoji!'.format(voting_emoji1),
                                                      color=discord.Color.red()), ephemeral=True)
                return
            if not is_valid_emoji(voting_emoji2):
                await ctx.respond(embed=discord.Embed(title='"{}" is not a valid emoji!'.format(voting_emoji2),
                                                      color=discord.Color.red()), ephemeral=True)
                return
            
            random.shuffle(options)
            tree = [[None, None] for _ in range(len(options) - 1)] + [[x, None] for x in options]
            await ctx.respond(file=await self.create_ko_tournament_image(ctx.guild_id, tree))
            for ti in range(len(tree)-1, 0, -2):
                winner, count1, count2 = await ko_round(ctx, tree[ti-1][0], tree[ti][0], round_time_seconds, voting_emoji1, voting_emoji2)
                tree[ti-1][1] = count1
                tree[ti  ][1] = count2
                tree[int((ti-1)/2)][0] = winner

                await ctx.edit(file=await self.create_ko_tournament_image(ctx.guild_id, tree))
            
        default_voting_emoji1 = '🅰'
        default_voting_emoji2 = '🅱'

        async def vote_tournament_list(ctx: discord.ApplicationContext,
                                       options: discord.Option(
                                        str,
                                        description=bot.i18n.get('VOTE_TOURNAMENT_LIST_OPTIONS'),
                                       ),
                                       round_time_seconds: discord.Option(
                                        int,
                                        default=60,
                                        description=bot.i18n.get('VOTE_TOURNAMENT_ROUND_TIME_OPTION'),
                                       ),
                                       voting_emoji1: discord.Option(
                                        str,
                                        default=default_voting_emoji1,
                                        description=bot.i18n.get('VOTE_TOURNAMENT_EMOJI1_OPTION'),
                                       ),
                                       voting_emoji2: discord.Option(
                                        str,
                                        default=default_voting_emoji2,
                                        description=bot.i18n.get('VOTE_TOURNAMENT_EMOJI2_OPTION'),
                                       ),
                                    ):
            await ctx.defer()
            await ko_tournament(ctx, options.split(','), round_time_seconds, voting_emoji1, voting_emoji2)

        async def vote_tournament_spotify_playlist(ctx: discord.ApplicationContext,
                                       playlist_url: discord.Option(
                                        str,
                                        description=bot.i18n.get('VOTE_TOURNAMENT_SPOTIFY_PLAYLIST_OPTIONS'),
                                       ),
                                       round_time_seconds: discord.Option(
                                        int,
                                        default=60,
                                        description=bot.i18n.get('VOTE_TOURNAMENT_ROUND_TIME_OPTION'),
                                       ),
                                       voting_emoji1: discord.Option(
                                        str,
                                        default=default_voting_emoji1,
                                        description=bot.i18n.get('VOTE_TOURNAMENT_EMOJI1_OPTION'),
                                       ),
                                       voting_emoji2: discord.Option(
                                        str,
                                        default=default_voting_emoji2,
                                        description=bot.i18n.get('VOTE_TOURNAMENT_EMOJI2_OPTION'),
                                       ),
                                    ):
            await ctx.defer()
            playlist_id = re.findall(r'playlist\/(\w+)', playlist_url)

            if len(playlist_id) == 1:
                playlist_id = playlist_id[0]
            else:
                playlist_id = playlist_url

            r = requests.get('https://api.spotifydown.com/trackList/playlist/{}'.format(playlist_id), headers={
                'origin': 'https://spotifydown.com',
                'referer': 'https://spotifydown.com/',
            })

            rjson = None
            try:
                rjson = r.json()
            except:
                pass
            
            if rjson is None or 'trackList' not in rjson:
                await ctx.respond(embed=discord.Embed(title='Could not find playlist with id "{}"!'.format(playlist_id),
                                                      color=discord.Color.red()), ephemeral=True)
                return

            options = [
                '{} - {} (https://open.spotify.com/track/{})'.format(t['artists'], t['title'], t['id'])
                for t in rjson['trackList']
            ]

            await ko_tournament(ctx, options, round_time_seconds, voting_emoji1, voting_emoji2)

        vote_command = discord.SlashCommandGroup(
            name=bot.i18n.get('VOTE_COMMAND'),
            description=bot.i18n.get('VOTE_DESCRIPTION'),
        )
        vote_tournament_command = vote_command.create_subgroup(
            name=bot.i18n.get('VOTE_TOURNAMENT_COMMAND'),
            description=bot.i18n.get('VOTE_TOURNAMENT_DESCRIPTION'),
        )
        vote_tournament_command.subcommands.append(discord.SlashCommand(
            func=vote_tournament_list,
            name=bot.i18n.get('VOTE_TOURNAMENT_LIST_COMMAND'),
            description=bot.i18n.get('VOTE_TOURNAMENT_LIST_DESCRIPTION'),
            parent=vote_tournament_command
        ))
        vote_tournament_command.subcommands.append(discord.SlashCommand(
            func=vote_tournament_spotify_playlist,
            name=bot.i18n.get('VOTE_TOURNAMENT_SPOTIFY_PLAYLIST_COMMAND'),
            description=bot.i18n.get('VOTE_TOURNAMENT_SPOTIFY_PLAYLIST_DESCRIPTION'),
            parent=vote_tournament_command
        ))

        self.commands = [
            vote_command
        ]
