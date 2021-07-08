import asyncio
import re
from datetime import datetime, timedelta

import discord
import pytz
from aio_timers import Timer
from asgiref.sync import sync_to_async
from discord.ext import commands
from discord.ext.commands import Cog

from logistics.models import ActionRecord
from src.constants.Constants import ActionType, Status, CANCEL_ACTION, MATERIALS_FIELD_NAME, ITEM_FIELD_NAME, \
    MIND_COST_FIELD_NAME, RESOLVE_FIELD_NAME, NOTES_FIELD_NAME, TIME_COST_FIELD_NAME, QUANTITY_FIELD_NAME
from src.constants.RegularExpressions import BASIC_STRING_FIELD_EXPRESSION, TITLE_FIELD_NAME, DESCRIPTION_FIELD_NAME, \
    COLOR_FIELD_NAME, TAGGED_STRING_FIELD_EXPRESSION, FIELD, VALUE, MATERIALS_FIELD_EXPRESSION, \
    ITEM_LIST_FIELD_EXPRESSION, TIME_FIELD_EXPRESSION, QUANTITY_FIELD_EXPRESSION, MIND_COST_FIELD_EXPRESSION, \
    RESOLVE_FIELD_EXPRESSION, NOTES_FIELD_EXPRESSION
from src.data.ActionData import ActionData
from src.data.EmbedData import EmbedData
from src.tools.Messenger import Messenger
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType, Interaction
import os

from src.tools.TimeConverter import TimeConverter


class Action_cog(commands.Cog, name='action commands'):
    def __init__(self, bot: commands.Bot):
        self.action_admin_channel = os.environ['ACTION_ADMIN_CHANNEL']
        self.action_channel_status = Status.closed
        self.server_timezone = os.environ['SERVER_TIMEZONE']

        self.bot = bot
        self.active_actions = list()
        self.action_admin_channel = self.get_action_admin_channel(self.action_admin_channel)
        if self.action_admin_channel is not None:
            print("\t\tAction_cog attached to \'%s\'" % self.action_admin_channel)
            self.action_channel_status = Status.open
        else:
            print("\t\tAction_cog could not attach to channel")
            self.action_channel_status = Status.closed

    def get_action_admin_channel(self, channel_name: str = 'post-office-information'):
        all_channels = list(self.bot.get_all_channels())
        return next(filter(lambda x: x.name == channel_name,  all_channels))

    @commands.command('action',
                      description='Use a skill to complete a timed action such as building.\r\n\taction options: [%s]' % ActionType.to_list(),
                      help='Use a skill to complete a timed action such as building')
    @commands.has_any_role('Admin', 'Staff', 'Full Ticket')
    async def action(self, ctx: commands.Context, action: str, *, parameters: str):
        if ctx.message.author == self.bot:
            return

        if self.action_channel_status == Status.closed:
            await Messenger.send_postoffice_status_message(ctx, self.trade_channel_status)
            return

        message_content = str(ctx.message.content)

        action_data = ActionData()
        try:
            action_data.action_type = ActionType[action.lower()]
        except KeyError:
            await ctx.channel.send("\tUnknown or unsupported skill. Please see /help action for assistance")
            return

        action_data.origin_message = ctx.message
        action_data.action_user = ctx.message.author

        print('command \'%s\' parameters: \'%s\'' % (action, parameters))

        item_list = re.search(ITEM_LIST_FIELD_EXPRESSION, parameters)
        if item_list is None or item_list.group(ITEM_FIELD_NAME) is None:
            await ctx.message.channel.send('Unable to parse your items from your command line \'%s\' please check '
                                           'your command and try again.' % message_content)
            return

        action_data.items = item_list.group('item_list').strip()
        print('items: \'%s\'' % action_data.items)

        # note - trailblazing is the only skill that doesn't cost time. Just mind
        time_cost_group = re.search(TIME_FIELD_EXPRESSION, parameters)
        if time_cost_group is not None:
            action_data.time_cost = int(time_cost_group.group(TIME_COST_FIELD_NAME))

        if action_data.action_type == ActionType.trailblaze:
            action_data.time_cost = 0

        quantity_group = re.search(QUANTITY_FIELD_EXPRESSION, parameters)
        if quantity_group is not None:
            action_data.quantity = int(quantity_group.group(QUANTITY_FIELD_NAME))

        if action_data.quantity <= 0:
            action_data.quantity = 1

        mind_cost_group = re.search(MIND_COST_FIELD_EXPRESSION, parameters)
        if mind_cost_group is not None:
            action_data.mind_cost = int(mind_cost_group.group(MIND_COST_FIELD_NAME))

        resolve_group = re.search(RESOLVE_FIELD_EXPRESSION, parameters)
        if resolve_group is not None:
            action_data.resolve_cost = int(resolve_group.group('resolve'))

        materials_group = re.search(MATERIALS_FIELD_EXPRESSION, parameters)
        if materials_group is not None:
            action_data.materials = materials_group.group(MATERIALS_FIELD_NAME)
        else:
            action_data.materials = 'unspecified'

        commentary_group = re.search(NOTES_FIELD_EXPRESSION, parameters)
        if commentary_group is not None:
            action_data.commentary = str(commentary_group.group(NOTES_FIELD_NAME))

        if action_data.mind_cost > 0 and action_data.quantity > 1:
            action_data.mind_cost *= action_data.quantity

        if action_data.time_cost > 0 and action_data.quantity > 1:
            action_data.time_cost *= action_data.quantity

        current_utc_time = datetime.utcnow()
        server_timezone_object = pytz.timezone(self.server_timezone)

        local_time = current_utc_time.replace(tzinfo=pytz.utc).astimezone(server_timezone_object)
        new_time = server_timezone_object.normalize(local_time)

        action_data.start_time = new_time

        if action_data.action_type is ActionType.trailblaze:
            action_data.time_of_completion = None
            action_data.timer_duration_in_seconds = 1
        else:
            action_data.time_of_completion = new_time + timedelta(minutes=action_data.get_time_cost_in_minutes())

        action_data.action_accept_message = \
            await Messenger.send_action_accepted_message(action_data)

        args = (action_data,)
        timer = Timer(delay=action_data.get_time_cost_in_seconds(), callback=self.action_timer_expired,
                      callback_args=args)

        self.active_actions.append(action_data)

    @Cog.listener()
    async def on_button_click(self, interaction : Interaction):
        message = interaction.message
        message_id = message.id
        clicking_user = interaction.user
        user_id = clicking_user.id
        component = interaction.interacted_component

        action_data = next((x for x in self.active_actions if x.action_accept_message.id == message_id and x.action_user.id == user_id), None)
        if action_data is not None:
            print("Action_cog: '%s' button pressed on message '%s' by '%s'... this one is MINE" % (component.label, message_id, clicking_user.display_name,))
            await self.action_timer_cancelled(action_data)

    @action.error
    async def action_error(self, ctx, error):
        if isinstance(error, TimeoutError):
            origin_id = ctx.message.id
            origin_message_data = await next(filter(lambda x: x.origin_message.id == origin_id, self.active_actions))
            await self.action_timer_expired(origin_message_data)

    async def action_timer_cancelled(self, action_data: ActionData):
        if action_data is None:
            return

        print('Action timer cancelled for user %s' % action_data.action_user.display_name)

        original_embed = action_data.action_accept_message.embeds[0]
        new_embed = EmbedData(title=original_embed.title + ' CANCELLED', description="%s's action was cancelled" % action_data.action_user.display_name,
                              color=discord.Color.dark_red())

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=ITEM_FIELD_NAME):
            materials = EmbedData.get_field_value_by_name(embed=original_embed, field_name=ITEM_FIELD_NAME)
            new_embed.add_field(name=ITEM_FIELD_NAME, value=materials)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=MATERIALS_FIELD_NAME):
            materials = EmbedData.get_field_value_by_name(embed=original_embed, field_name=MATERIALS_FIELD_NAME)
            new_embed.add_field(name=MATERIALS_FIELD_NAME, value=materials)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=MIND_COST_FIELD_NAME):
            mind_cost = EmbedData.get_field_value_by_name(embed=original_embed, field_name=MIND_COST_FIELD_NAME)
            new_embed.add_field(name=MIND_COST_FIELD_NAME, value=mind_cost)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=RESOLVE_FIELD_NAME):
            resolve_cost = EmbedData.get_field_value_by_name(embed=original_embed, field_name=RESOLVE_FIELD_NAME)
            new_embed.add_field(name=RESOLVE_FIELD_NAME, value=resolve_cost)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=NOTES_FIELD_NAME):
            notes = EmbedData.get_field_value_by_name(embed=original_embed, field_name=NOTES_FIELD_NAME)
            new_embed.add_field(name=NOTES_FIELD_NAME, value=notes)

        await action_data.origin_message.author.send(embed=new_embed.to_embed(), components=[], delete_after=3 * 60)
        await self.action_admin_channel.send(embed=new_embed.to_embed(), components=[])
        await action_data.origin_message.delete()
        await action_data.action_accept_message.delete()

        action_record = action_data.to_action_record()
        action_record.action_completed = TimeConverter.now()
        action_record.interrupted = True
        await sync_to_async(action_record.save, thread_sensitive=True)()
        print("Database entry completed")

        self.active_actions.remove(action_data)

    async def action_timer_expired(self, action_data: ActionData):
        if action_data is None:
            return

        print('Action timer expired successfully for user %s' % action_data.action_user.display_name)

        original_embed = action_data.action_accept_message.embeds[0]

        new_embed = EmbedData(title=original_embed.title + ' COMPLETED', description="%s's action has completed successfully" % action_data.action_user.display_name,
                              color=discord.Color.orange())

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=MIND_COST_FIELD_NAME):
            mind_cost = EmbedData.get_field_value_by_name(embed=original_embed, field_name=MIND_COST_FIELD_NAME)
            new_embed.add_field(name=MIND_COST_FIELD_NAME, value=mind_cost)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=ITEM_FIELD_NAME):
            items = EmbedData.get_field_value_by_name(embed=original_embed, field_name=ITEM_FIELD_NAME)
            new_embed.add_field(name=ITEM_FIELD_NAME, value=items)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=RESOLVE_FIELD_NAME):
            resolve = EmbedData.get_field_value_by_name(embed=original_embed, field_name=RESOLVE_FIELD_NAME)
            new_embed.add_field(name=RESOLVE_FIELD_NAME, value=resolve)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=NOTES_FIELD_NAME):
            notes = EmbedData.get_field_value_by_name(embed=original_embed, field_name=NOTES_FIELD_NAME)
            new_embed.add_field(name=NOTES_FIELD_NAME, value=notes)

        await action_data.origin_message.author.send(embed=new_embed.to_embed(), delete_after=3*60)
        await self.action_admin_channel.send(embed=new_embed.to_embed(), components=[])
        await action_data.origin_message.delete()
        await action_data.action_accept_message.delete()

        action_record = action_data.to_action_record()
        action_record.action_completed = TimeConverter.now()
        action_record.interrupted = False
        await sync_to_async(action_record.save, thread_sensitive=True)()
        print("Database entry completed")

        self.active_actions.remove(action_data)


def setup(bot):
    print('\tAction_cog is loading')
    bot.add_cog(Action_cog(bot))
