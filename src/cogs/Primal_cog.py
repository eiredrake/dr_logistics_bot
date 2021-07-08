import discord
from discord import DMChannel, ChannelType
from discord.ext import commands
from discord.ext.commands import Cog, bot
import pytz
from datetime import datetime, timedelta

from src.constants.Constants import DATE_WITH_TWELVE_HOUR_TIME_FORMAT
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
import os

from src.data.EmbedData import EmbedData


class Primal_cog(commands.Cog, name='primal commands'):
    def __init__(self, bot):
        self.bot = bot
        self.server_timezone = os.environ['SERVER_TIMEZONE']

    @commands.command(name='time', description='Displays the current time', help='displays the server\'s time settings')
    async def time(self, ctx):
        if ctx.message.author == self.bot.user:
            return

        current_utc_time = datetime.utcnow()
        server_timezone_object = pytz.timezone(self.server_timezone)
        local_time = current_utc_time.replace(tzinfo=pytz.utc).astimezone(server_timezone_object)
        new_time = server_timezone_object.normalize(local_time)
        timezone_abbreviation = local_time.tzname()

        await ctx.channel.send('Server timezone: %s\r\nCurrent time is: %s' % (timezone_abbreviation,
                                                                               new_time.strftime
                                                                               (DATE_WITH_TWELVE_HOUR_TIME_FORMAT)))

    @commands.command('test')
    @commands.has_any_role('Admin')
    async def test(self, ctx):
        embed = EmbedData(title='Test', description='Testing, ignore this message', color=discord.Color.red())

        components = [
            Button(style=ButtonStyle.red, label="red"),
        ]

        message = await ctx.channel.send(embed=embed.to_embed(), components=components)

        response = await self.bot.wait_for(event='button_click', check=lambda i: i.component.label is not None, timeout=999)
        await response.respond(
            type=InteractionType.ChannelMessageWithSource,
            content=f'{response.component.label} clicked'
        )

    @commands.command('purge')
    @commands.has_any_role('Admin', 'Staff', 'bot_testing')
    async def purge(self, ctx):
        author = ctx.message.author
        private_channels = self.bot.user
        print('Attempting to purge private messages to bot')
        dm_channel = None
        channels = self.bot.private_channels
        for channel in channels:
            if channel.type is ChannelType.private:
                if channel.recipient == author:
                    dm_channel = channel
                    break

        if dm_channel is not None:
            messages = await channel.history(limit=999).flatten()
            for message in messages:
                message_id = int(message.id)
                message_bar = await dm_channel.fetch_message(message_id)
                if message_bar.author == self.bot.user:
                    await message_bar.delete()

            print('Purge completed')


def setup(bot):
    print('\tPrimal_cog is loading')
    bot.add_cog(Primal_cog(bot))
