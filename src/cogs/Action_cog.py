import re
from datetime import datetime, timedelta

import discord
import pytz
from aio_timers import Timer
from asgiref.sync import sync_to_async
from discord.ext import commands
from discord.ext.commands import Cog
from discord_components import Interaction
from texttable import Texttable

from src.constants.Constants import Status, BOT_COMMANDER_ROLE, GUIDE_ROLE, STAFF_ROLE, TWELVE_HOUR_TIME_FORMAT, \
    WRITER_ROLE, FULL_TICKET_ROLE, ActionType, LockedActionType
from src.constants.RegularExpressions import ITEMS_LIST_FIELD_EXPRESSION, ITEMS_FIELD_NAME, DISCORD_USER_ID_EXPRESSION, \
    DISCORD_USER_ID_FIELD_NAME, TIME_FIELD_EXPRESSION, TIME_COST_FIELD_NAME, QUANTITY_FIELD_EXPRESSION, \
    QUANTITY_FIELD_NAME, MIND_COST_FIELD_EXPRESSION, MIND_COST_FIELD_NAME, RESOLVE_FIELD_EXPRESSION, \
    MATERIALS_FIELD_EXPRESSION, MATERIALS_FIELD_NAME, NOTES_FIELD_EXPRESSION, NOTES_FIELD_NAME, RESOLVE_FIELD_NAME
from src.data.ActionData import ActionData
from src.data.EmbedData import EmbedData
from src.tools.Messenger import Messenger
from src.tools.TimeConverter import TimeConverter
import os


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
        return next(filter(lambda x: x.name == channel_name, all_channels))

    @commands.has_any_role(BOT_COMMANDER_ROLE, GUIDE_ROLE, STAFF_ROLE)
    @commands.command('actions', description='Displays what actions are currently pending',
                      help='Displays what actions are currently pending')
    async def actions(self, ctx: commands.Context):
        if ctx.message.author == self.bot.user:
            return

        output_message = 'Current Pending Actions: %d\r\n' % len(self.active_actions)
        if len(self.active_actions) > 0:
            table = Texttable()
            table.set_deco(Texttable.HEADER)
            table.set_chars(['-', '|', '+', '='])

            table.add_row(['Player', 'Type', 'Items', 'Mind', 'Time', 'Resolve', 'Start Time', 'Completed Time'])
            for action_data in self.active_actions:
                table.add_row(
                    [action_data.action_user, str(action_data.action_type), action_data.items, action_data.mind_cost,
                     action_data.time_cost, action_data.resolve_cost,
                     action_data.start_time.strftime(TWELVE_HOUR_TIME_FORMAT),
                     action_data.time_of_completion.strftime(TWELVE_HOUR_TIME_FORMAT)])

            output_message += table.draw()

        print(output_message)

    @commands.command('status', description='Checks the current status of the dr_logistics_bot in this channel')
    @commands.has_any_role(BOT_COMMANDER_ROLE, WRITER_ROLE, GUIDE_ROLE, STAFF_ROLE, FULL_TICKET_ROLE)
    async def status(self, ctx: commands.command):
        if ctx.message.author == self.bot:
            return

        send_embed_permission = False
        send_message_permission = False

        embed_data = EmbedData(title='dr_logistics_bot',
                               description='If you are seeing this response, that means the dr_logistics_bot can '
                                           'see and interact with the current channel',
                               color=discord.Color.gold())
        embed_data.add_field(name='Holla back', value=ctx.message.author.display_name)
        await ctx.channel.send(embed=embed_data.to_embed())
        print('channel \'%s\' has correct permissions' % ctx.channel.name)

    @status.error
    async def status_error(self, ctx, error):
        output_message = 'Error on channel \'%s\': %s' % (ctx.channel.name, error)
        print(output_message)
        await ctx.message.channel.send(output_message)

    @commands.command('postoffice',
                      description='[%s] opens or Closes the post office. Optionally use \'global\' flag to announce to everyone' % Status.to_list(),
                      help='[%s] opens or closes the post office. Optionally use \'global\' flag to announce to everyone' % Status.to_list())
    @commands.has_any_role(BOT_COMMANDER_ROLE, WRITER_ROLE, GUIDE_ROLE, STAFF_ROLE)
    async def postoffice(self, ctx: commands.Context, status_parameter: str, global_flag: str = ''):
        if ctx.message.author == self.bot:
            return

        print("command: /action received from \'%s\' on guild \'%s\' channel \'%s\'" % (
        ctx.message.author.display_name, ctx.channel.guild.name, ctx.channel.name))
        print('parameters: %s %s' % (status_parameter, global_flag))

        self.action_channel_status = Status.parse(status_parameter)

        if 'global' in global_flag:
            await Messenger.send_global_postoffice_status_message(ctx, self.action_channel_status)
        else:
            verb = "opened" if self.action_channel_status == Status.open else "closed"
            message = '%s has %s the post office' % (ctx.message.author.display_name, verb)
            await ctx.channel.send(message)

    @commands.command('action',
                      description='Use a skill to complete a timed action such as building.\r\n\taction options: [%s]' % ActionType.to_list(),
                      help='Use a skill to complete a timed action such as building')
    @commands.has_any_role(BOT_COMMANDER_ROLE, WRITER_ROLE, GUIDE_ROLE, FULL_TICKET_ROLE, STAFF_ROLE)
    async def action(self, ctx: commands.Context, action: str, *, parameters: str):
        if ctx.message.author == self.bot:
            return

        print("command: /action received from \'%s\' on guild \'%s\' channel \'%s\'" % (
        ctx.message.author.display_name, ctx.channel.guild.name, ctx.channel.name))
        print('parameters: %s' % parameters)

        message_content = str(ctx.message.content)

        action_data = ActionData()
        try:
            action_data.action_type = ActionType[action.lower()]
        except KeyError:
            await ctx.channel.send("\tUnknown or unsupported skill. Please see /help action for assistance")
            return

        if self.action_channel_status == Status.closed:
            if LockedActionType.is_locked_action(action_data.action_type):
                print('postoffice is closed, rejecting action')
                await Messenger.send_postoffice_status_message(ctx, self.action_channel_status)
                return

        action_data.origin_message = ctx.message
        action_data.action_user = ctx.message.author

        print('--------------------------------------------------------')
        print('command \'%s\' parameters: \'%s\'' % (action, parameters))

        print('%s beginning action processing' % ctx.message.author.display_name)

        item_list = re.search(ITEMS_LIST_FIELD_EXPRESSION, parameters)
        if item_list is None or item_list.group(ITEMS_FIELD_NAME) is None:
            await ctx.message.channel.send('Unable to parse your items from your command line \'%s\' please check '
                                           'your command and try again.' % message_content)
            return

        action_data.items = item_list.group(ITEMS_FIELD_NAME).strip()
        print('items: \'%s\'' % action_data.items)

        discord_user_name = None
        discord_user_id_group = re.search(DISCORD_USER_ID_EXPRESSION, parameters)
        if discord_user_id_group is not None:
            discord_user_id = discord_user_id_group.group(DISCORD_USER_ID_FIELD_NAME)
            if discord_user_id.isnumeric():
                discord_user_id = int(discord_user_id)
                discord_user = await self.bot.fetch_user(int(discord_user_id))
                discord_user_name = "@" + discord_user.display_name
                parameters = re.sub(DISCORD_USER_ID_EXPRESSION, discord_user_name, parameters)

        # note - trailblazing is the only skill that doesn't cost time. Just mind
        time_cost_group = re.search(TIME_FIELD_EXPRESSION, parameters)
        if time_cost_group is not None:
            action_data.time_cost = int(time_cost_group.group(TIME_COST_FIELD_NAME))

        if action_data.action_type == ActionType.trailblaze:
            action_data.time_cost = 0

        print('time_cost: %s' % action_data.time_cost)

        quantity_group = re.search(QUANTITY_FIELD_EXPRESSION, parameters)
        if quantity_group is not None:
            action_data.quantity = int(quantity_group.group(QUANTITY_FIELD_NAME))

        if action_data.quantity <= 0:
            action_data.quantity = 1

        print('qyt: %s' % action_data.quantity)

        mind_cost_group = re.search(MIND_COST_FIELD_EXPRESSION, parameters)
        if mind_cost_group is not None:
            action_data.mind_cost = int(mind_cost_group.group(MIND_COST_FIELD_NAME))

        print('mind_cost: %s' % action_data.mind_cost)

        resolve_group = re.search(RESOLVE_FIELD_EXPRESSION, parameters)
        if resolve_group is not None:
            action_data.resolve_cost = int(resolve_group.group('resolve'))

        print('resolve_cost: %s' % action_data.resolve_cost)

        materials_group = re.search(MATERIALS_FIELD_EXPRESSION, parameters)
        if materials_group is not None:
            action_data.materials = materials_group.group(MATERIALS_FIELD_NAME)
        else:
            action_data.materials = 'unspecified'

        print('materials: %s' % action_data.materials)

        commentary_group = re.search(NOTES_FIELD_EXPRESSION, parameters)
        if commentary_group is not None:
            action_data.commentary = str(commentary_group.group(NOTES_FIELD_NAME))

        print('notes: \'%s\'' % action_data.commentary)

        if action_data.mind_cost > 0 and action_data.quantity > 1:
            action_data.mind_cost *= action_data.quantity

        if action_data.time_cost > 0 and action_data.quantity > 1:
            action_data.time_cost *= action_data.quantity

        current_utc_time = datetime.utcnow()
        server_timezone_object = pytz.timezone(self.server_timezone)

        local_time = current_utc_time.replace(tzinfo=pytz.utc).astimezone(server_timezone_object)
        new_time = server_timezone_object.normalize(local_time)

        action_data.start_time = new_time

        print('start time: %s' % action_data.start_time)

        if action_data.action_type is ActionType.trailblaze:
            action_data.time_of_completion = None
            action_data.timer_duration_in_seconds = 1
        else:
            action_data.time_of_completion = new_time + timedelta(minutes=action_data.get_time_cost_in_minutes())

        print('Sending accept message')
        action_data.action_accept_message = \
            await Messenger.send_action_accepted_message(action_data)

        args = (action_data,)
        timer = Timer(delay=action_data.get_time_cost_in_seconds(), callback=self.action_timer_expired,
                      callback_args=args)

        print('Timer set. Action prep complete')
        self.active_actions.append(action_data)

        print('--------------------------------------------------------')

    @Cog.listener()
    async def on_button_click(self, interaction: Interaction):
        message = interaction.message
        message_id = message.id
        clicking_user = interaction.user
        user_id = clicking_user.id
        component = interaction.interacted_component

        action_data = next((x for x in self.active_actions if
                            x.action_accept_message.id == message_id and x.action_user.id == user_id), None)
        if action_data is not None:
            print("Action_cog: '%s' button pressed on message '%s' by '%s'... this one is MINE" % (
            component.label, message_id, clicking_user.display_name,))
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
        new_embed = EmbedData(title=original_embed.title + ' CANCELLED',
                              description="%s's action was cancelled" % action_data.action_user.display_name,
                              color=discord.Color.dark_red())

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=ITEMS_FIELD_NAME):
            materials = EmbedData.get_field_value_by_name(embed=original_embed, field_name=ITEMS_FIELD_NAME)
            new_embed.add_field(name=ITEMS_FIELD_NAME, value=materials)

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

        new_embed = EmbedData(title=original_embed.title + ' COMPLETED',
                              description="%s's action has completed successfully" % action_data.action_user.display_name,
                              color=discord.Color.orange())

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=MIND_COST_FIELD_NAME):
            mind_cost = EmbedData.get_field_value_by_name(embed=original_embed, field_name=MIND_COST_FIELD_NAME)
            new_embed.add_field(name=MIND_COST_FIELD_NAME, value=mind_cost)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=ITEMS_FIELD_NAME):
            items = EmbedData.get_field_value_by_name(embed=original_embed, field_name=ITEMS_FIELD_NAME)
            new_embed.add_field(name=ITEMS_FIELD_NAME, value=items)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=RESOLVE_FIELD_NAME):
            resolve = EmbedData.get_field_value_by_name(embed=original_embed, field_name=RESOLVE_FIELD_NAME)
            new_embed.add_field(name=RESOLVE_FIELD_NAME, value=resolve)

        if EmbedData.field_exists_by_name(embed=original_embed, field_name=NOTES_FIELD_NAME):
            notes = EmbedData.get_field_value_by_name(embed=original_embed, field_name=NOTES_FIELD_NAME)
            new_embed.add_field(name=NOTES_FIELD_NAME, value=notes)

        await action_data.origin_message.author.send(embed=new_embed.to_embed(), delete_after=3 * 60)
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
