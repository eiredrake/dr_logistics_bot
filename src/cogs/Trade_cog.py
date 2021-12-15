import discord
from asgiref.sync import sync_to_async
from discord.ext import commands
from discord.ext.commands import command, Cog, bot, cog
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionEventType, Interaction

import pytz
from datetime import datetime, timedelta
import re
from aio_timers import Timer
from texttable import Texttable

from src.constants.Constants import DATE_WITH_TWELVE_HOUR_TIME_FORMAT, A_EMOJI, B_EMOJI, CANCEL_EMOJI, OK_EMOJI, \
    ACCEPT_TRADE, CANCEL_TRADE, TradeResponse, FULL_TICKET_ROLE, BOT_COMMANDER_ROLE, WRITER_ROLE, \
    GUIDE_ROLE, STAFF_ROLE, TWELVE_HOUR_TIME_FORMAT
from src.constants.RegularExpressions import BASIC_STRING_FIELD_EXPRESSION, ITEMS_FIELD_NAME, RECIPIENT_FIELD_NAME, \
    RECIPIENT_FIELD_EXPRESSION, TIMEOUT_FIELD_EXPRESSION, TIMEOUT_FIELD_NAME, NOTES_FIELD_EXPRESSION, \
    ITEMS_LIST_FIELD_EXPRESSION, NOTES_FIELD_NAME
from src.data.EmbedData import EmbedData, FieldObject
from src.data.TradeRequest import TradeRequest
import os


class Trade_cog(commands.Cog, name='trade commands'):
    def __init__(self, bot):
        self.bot = bot
        self.active_trades = list()
        self.trade_admin_channel_name = os.environ['TRADE_ADMIN_CHANNEL']
        self.server_timezone = os.environ['SERVER_TIMEZONE']

        self.trade_admin_channel = self.get_trade_admin_channel(self.trade_admin_channel_name)
        if self.trade_admin_channel is not None:
            print("\t\tTrade_cog attached to \'%s\'" % self.trade_admin_channel_name)
        else:
            print("\t\tTrade_cog could not attach to channel")

    def get_trade_admin_channel(self, channel_name: str = 'post-office-information'):
        all_channels = list(self.bot.get_all_channels())
        return next(filter(lambda x: x.name == channel_name, all_channels))

    @commands.has_any_role(BOT_COMMANDER_ROLE, GUIDE_ROLE, STAFF_ROLE)
    @commands.command('trades', description='Displays what trades are currently pending',
                      help='Displays what trades are currently pending')
    async def trades(self, ctx: commands.Context):
        if ctx.message.author == self.bot.user:
            return

        output_message = 'Current Pending Trades: %d\r\n' % len(self.active_trades)
        if len(self.active_trades) > 0:
            table = Texttable()
            table.set_deco(Texttable.HEADER)
            table.set_chars(['-', '|', '+', '='])

            table.add_row(['Player A', 'Player B', 'Items', 'Expire Time'])
            for trade_data in self.active_trades:
                table.add_row([trade_data.player_a_name, trade_data.player_b_name, trade_data.items, trade_data.expire_time.strftime(TWELVE_HOUR_TIME_FORMAT)])

            output_message += table.draw()

        print(output_message)

    @commands.has_any_role(BOT_COMMANDER_ROLE, FULL_TICKET_ROLE, WRITER_ROLE, GUIDE_ROLE, STAFF_ROLE)
    @commands.command('trade', description='Trade items to another user', help='Trade items to another user')
    async def trade(self, ctx: commands.Context, *, parameters: str):
        print("command: /trade received from \'%s\' on guild \'%s\' channel \'%s\'" % (
            ctx.message.author.display_name, ctx.channel.guild.name, ctx.channel.name))
        print("parameters: %s" % parameters)

        if ctx.message.author == self.bot.user:
            return

        if self.trade_admin_channel is None:
            embed = EmbedData(title='Trades are Disabled', description='Trades are currently disabled as the system '
                                                                       'cannot locate the post office channel. Please '
                                                                       'have an admin set the channel using the '
                                                                       '/setchannel command',
                              color=discord.Color.red())
            embed.thumbnail = 'https://static.thenounproject.com/png/89609-200.png'
            ctx.channel.send(embed=embed.to_embed())
            return

        trade_request = TradeRequest()
        trade_request.origin_message = ctx.message
        trade_request.player_a = ctx.message.author

        if hasattr(ctx.message.author, 'nick'):
            trade_request.player_a_name = ctx.message.author.nick
        else:
            trade_request.player_a_name = ctx.message.author.display_name

        item_group = re.search(ITEMS_LIST_FIELD_EXPRESSION, parameters)
        if item_group is None:
            await ctx.message.channel.send("You must specify the items you wish to trade")
            return

        trade_request.items = item_group.group(ITEMS_FIELD_NAME).strip()

        recipient_group = re.search(RECIPIENT_FIELD_EXPRESSION, parameters)
        if recipient_group is None:
            await ctx.message.channel.send("You must specify a recipient of the trade")
            return

        if recipient_group.group(RECIPIENT_FIELD_NAME) is None:
            await ctx.message.channel.send("Unable to locate that user")
            return

        recipient_user = None
        recipient_text = recipient_group.group(RECIPIENT_FIELD_NAME)
        if recipient_text.isnumeric():
            recipient_id = int(recipient_text)
            recipient_user = await ctx.bot.fetch_user(recipient_id)
        else:
            members = list(ctx.message.guild.members)
            recipient_user = next((x for x in members if x.name == recipient_text or x.display_name == recipient_text),
                                  None)

        if recipient_user is None:
            await ctx.message.channel.send("Unable to locate that user")
            return

        trade_request.player_b = recipient_user
        if hasattr(recipient_user, 'nick'):
            trade_request.player_b_name = recipient_user.nick
        else:
            trade_request.player_b_name = recipient_user.display_name

        time_out = 3
        time_out_group = re.search(TIMEOUT_FIELD_EXPRESSION, parameters)
        if time_out_group is not None:
            time_out = int(time_out_group.group(TIMEOUT_FIELD_NAME))

        if time_out > 10:
            time_out = 10
        elif time_out < 0:
            time_out = 1

        commentary_group = re.search(NOTES_FIELD_EXPRESSION, parameters)
        if commentary_group is not None:
            trade_request.comments = str(commentary_group.group(NOTES_FIELD_NAME))

        print('Trade attempt started between \'%s\' and \'%s\' in channel \'%s\'' % (
            trade_request.player_a_name, trade_request.player_b_name, ctx.channel.name))

        trade_request.timeout_in_minutes = time_out
        current_utc_time = datetime.utcnow()
        server_timezone_obj = pytz.timezone(self.server_timezone)

        local_time = current_utc_time.replace(tzinfo=pytz.utc).astimezone(server_timezone_obj)
        trade_request.request_start = local_time

        new_time = server_timezone_obj.normalize(local_time)
        new_time = new_time + timedelta(seconds=trade_request.timeout_in_seconds())

        trade_request.expire_time = new_time

        description = '%s has initiated a trade request.\r\n\r\nThis trade request will expire time shown below\r\nTo ' \
                      'complete the trade both participants must click the accept trade button ' \
                      'or either one may click cancel trade button to cancel it' % (trade_request.player_a.nick,)

        embed_data = EmbedData(title='Trade Request', description=description, color=discord.Color.teal())
        embed_data.add_field(name='player a', value=trade_request.player_a_name)
        embed_data.add_field(name='player b', value=trade_request.player_b_name)
        embed_data.add_field(name='items', value=trade_request.items)

        if trade_request.comments is not None:
            embed_data.add_field(name='comments', value=trade_request.comments)

        embed_data.add_field(name='expires at', value=trade_request.expire_time.
                             strftime(DATE_WITH_TWELVE_HOUR_TIME_FORMAT))
        embed_data.thumbnail = 'https://static.thenounproject.com/png/686718-200.png'

        trade_request.origin_message = ctx.message

        components_a = [
            [
                Button(style=ButtonStyle.green, label=ACCEPT_TRADE),
                Button(style=ButtonStyle.red, label=CANCEL_TRADE),
            ]
        ]

        components_b = [
            [
                Button(style=ButtonStyle.green, label=ACCEPT_TRADE),
                Button(style=ButtonStyle.red, label=CANCEL_TRADE),
            ]
        ]

        player_a_message = await trade_request.player_a.send('incoming message')
        trade_request.player_a_dm_message = player_a_message
        await player_a_message.edit(content='', embed=embed_data.to_embed(trade_request.player_a_dm_message.id),
                                    components=components_a)
        print('Sent trade request to player a')

        player_b_message = await trade_request.player_b.send('incoming message')
        trade_request.player_b_dm_message = player_b_message
        await player_b_message.edit(content='', embed=embed_data.to_embed(trade_request.player_b_dm_message.id),
                                    components=components_b)
        print('Sent trade request to player b')

        trade_request.timer = Timer(delay=trade_request.timeout_in_seconds(), callback=self.trade_timer_expired,
                                    callback_args=(trade_request,))

        print("trade timer added to the pipe with a duration of %s minutes" % trade_request.timeout_in_minutes)
        self.active_trades.append(trade_request)
        print('There are currently ''%d'' trades in the pipe' % len(self.active_trades))

    @Cog.listener()
    async def on_button_click(self, interaction: Interaction):
        message = interaction.message
        message_id = message.id
        clicking_user = interaction.user
        component = interaction.interacted_component

        trade_request = next((x for x in self.active_trades if
                              x.player_a_dm_message.id == message_id or x.player_b_dm_message.id == message_id), None)
        if trade_request is not None:
            await interaction.respond(type=InteractionEventType.DeferredUpdateMessage,
                                      content='%s clicked' % component.label, hidden=False)
            print("Trade_cog: '%s' button pressed on message '%s' by '%s'... this one is MINE" % (
                component.label, message_id, clicking_user.display_name,))

            player_a_responding = trade_request.player_a == interaction.author
            player_b_responding = trade_request.player_b == interaction.author

            if component.label == ACCEPT_TRADE:
                if player_a_responding:
                    trade_request.player_a_response = TradeResponse.accepted
                    print('Trade request accepted by player a')
                elif player_b_responding:
                    trade_request.player_b_response = TradeResponse.accepted
                    print('Trade request accepted by player b')
            elif component.label == CANCEL_TRADE:
                if player_a_responding:
                    trade_request.player_a_response = TradeResponse.cancel
                elif player_b_responding:
                    trade_request.player_b_response = TradeResponse.cancel

            embed = EmbedData(title='Trade Status', description='Status for trade', color=discord.Color.blue())
            embed.add_field(name=trade_request.player_a.display_name, value=trade_request.player_a_response,
                            inline=False)
            embed.add_field(name=trade_request.player_b.display_name, value=trade_request.player_b_response,
                            inline=False)
            embed.add_field(name='items', value=trade_request.items, inline=False)
            embed.add_field(name='trade request expiration', value=trade_request.expire_time.
                            strftime(DATE_WITH_TWELVE_HOUR_TIME_FORMAT))

            await trade_request.player_a_dm_message.edit(embed=embed.to_embed())
            await trade_request.player_b_dm_message.edit(embed=embed.to_embed())

            await interaction.message.edit(embed=embed.to_embed(), components=[])

            if trade_request.player_a_response == TradeResponse.accepted and trade_request.player_b_response == TradeResponse.accepted:
                print('Trade request between \'%s\' and \'%s\' is accepted by both parties. Transmitting to admins' % (
                    trade_request.player_a_name, trade_request.player_b_name))
                # await trade_request.player_a_dm_message.delete()
                # await trade_request.player_b_dm_message.delete()
                try:
                    print("Deleting original request message")
                    await trade_request.origin_message.delete()
                    print("Original request message deleted")
                except discord.errors.Forbidden:
                    print("Cannot delete original request. Missing Permissions")

                admin_message = await self.trade_admin_channel.send(content='incoming message')
                embed = EmbedData(title='Trade Completed', description='The following trade was completed',
                                  color=discord.Color.green())
                embed.add_field(name='from', value=trade_request.player_a_name, inline=False)
                embed.add_field(name='to', value=trade_request.player_b_name, inline=False)
                embed.add_field(name='items', value=trade_request.items, inline=False)
                await admin_message.edit(content='', embed=embed.to_embed(admin_message.id))
                print('Trade request between \'%s\' and \'%s\' transmitted to admins' % (
                    trade_request.player_a_name, trade_request.player_b_name))

                trade_request.timer.cancel()
                self.active_trades.remove(trade_request)
                print('Timer for trade request between \'%s\' and \'%s\' cancelled' % (
                    trade_request.player_a_name, trade_request.player_b_name))

                from logistics.models import TradeTransaction

                transaction = TradeTransaction()
                transaction.transaction_date = trade_request.request_start
                transaction.player_a_discord_id = trade_request.player_a.id
                transaction.player_b_discord_id = trade_request.player_b.id
                transaction.player_a_display_name = trade_request.player_a_name
                transaction.player_b_display_name = trade_request.player_b_name
                transaction.items = trade_request.items
                transaction.comments = trade_request.comments

                await sync_to_async(transaction.save, thread_sensitive=True)()
                print("Database entry completed")

                return

            if trade_request.player_a_response == TradeResponse.cancel or trade_request.player_b_response == TradeResponse.cancel:
                print("Trade request is cancelled. Delete all messages")
                await trade_request.player_a_dm_message.delete()
                await trade_request.player_b_dm_message.delete()
                await trade_request.origin_message.delete()
                await trade_request.player_a.send('Trade request with %s was cancelled' % trade_request.player_b_name)
                await trade_request.player_b.send('Trade request with %s was cancelled' % trade_request.player_a_name)
                print("All Messages Deleted")
                trade_request.timer.cancel()
                self.active_trades.remove(trade_request)

    async def trade_timer_expired(self, trade_request: TradeRequest):
        if trade_request is None:
            return

        print('Trade request between \'%s\' and \'%s\' expired' % (
            trade_request.player_a.nick, trade_request.player_b_name))
        new_embed = EmbedData(title='Trade Request TIMEOUT',
                              description='This trade request has timed out and been cancelled.',
                              color=discord.Color.darker_grey())

        new_embed.add_field(name='from', value=trade_request.player_a_name, inline=True)
        new_embed.add_field(name='to', value=trade_request.player_b_name, inline=True)
        new_embed.add_field(name='items', value=trade_request.items, inline=True)

        await trade_request.player_a_dm_message.delete()
        await trade_request.player_b_dm_message.delete()

        trade_request.player_a_dm_message = await trade_request.player_a_dm_message.channel.send(
            content='incoming message')
        trade_request.player_b_dm_message = await trade_request.player_b_dm_message.channel.send(
            content='incoming message')

        await trade_request.player_a_dm_message.edit(content='',
                                                     embed=new_embed.to_embed(trade_request.player_a_dm_message.id),
                                                     components=[])
        await trade_request.player_b_dm_message.edit(content='',
                                                     embed=new_embed.to_embed(trade_request.player_b_dm_message.id),
                                                     components=[])
        await trade_request.origin_message.delete()

        self.active_trades.remove(trade_request)
        print('There are currently ''%d'' trades left in the pipe' % len(self.active_trades))


def setup(bot):
    print('\tTrade_cog is loading')
    bot.add_cog(Trade_cog(bot))
