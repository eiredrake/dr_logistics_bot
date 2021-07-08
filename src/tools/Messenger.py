from datetime import datetime

from src.constants.Constants import Status, ActionType, CANCEL_ACTION, MATERIALS_FIELD_NAME, MIND_COST_FIELD_NAME, \
    RESOLVE_FIELD_NAME, NOTES_FIELD_NAME
import discord
from discord.ext import commands

from src.data.ActionData import ActionData
from src.data.EmbedData import EmbedData
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType


class Messenger:

    @staticmethod
    async def send_action_accepted_message(action_data: ActionData):

        components = [
            [
                Button(style=ButtonStyle.red, label=CANCEL_ACTION),
            ]
        ]

        system_message = EmbedData(
            title='ACTION: %s' % action_data.action_type,
            description='%s has started a %s action' % (action_data.action_user.display_name, action_data.action_type),
            color=discord.Color.dark_gold())

        system_message.thumbnail = 'https://static.thenounproject.com/png/106008-200.png'

        system_message.add_field(name='item', value='\t%sx \'%s\'\r\n' % (action_data.quantity, action_data.items),
                                 inline=False)

        if action_data.mind_cost > 0:
            system_message.add_field(name=MIND_COST_FIELD_NAME, value=action_data.mind_cost, inline=True)

        if action_data.resolve_cost > 0:
            system_message.add_field(name=RESOLVE_FIELD_NAME, value=action_data.resolve_cost, inline=False)

        if action_data.time_of_completion is None:
            system_message.add_field(name='time in minutes', value='instant', inline=True)
            system_message.add_field(name='to complete at', value='instant', inline=True)
        else:
            system_message.add_field(name='time in minutes', value=action_data.get_time_cost_in_minutes(), inline=True)
            system_message.add_field(name='to complete at',
                                     value='%s' % action_data.time_of_completion.strftime('%m/%d/%Y %I:%M:%S %p'),
                                     inline=True)

        if action_data.materials is not None:
            system_message.add_field(name=MATERIALS_FIELD_NAME, value=action_data.materials, inline=True)

        if action_data.commentary is not None and len(action_data.commentary) > 0:
            system_message.add_field(name=NOTES_FIELD_NAME, value=action_data.commentary, inline=False)

        outbound_message = await action_data.origin_message.channel\
            .send(embed=system_message.to_embed(), components=components)

        return outbound_message

    @staticmethod
    async def send_postoffice_status_message(ctx: commands.Context, open_status: Status):
        status_description = "The post office is currently [%s]" % open_status
        if open_status == Status.closed:
            status_description += "\r\n\r\nNo actions requiring the post office can be performed at this time."

        status_color = discord.Color.green() if open_status == Status.open else discord.Color.red()

        embed = EmbedData(title='Post office Status', description=status_description, color=status_color)

        embed.thumbnail = 'https://static.thenounproject.com/png/2721472-200.png' if open_status == Status.open else 'https://static.thenounproject.com/png/2640959-200.png '

        await ctx.message.channel.send(embed=embed.to_embed())

    # @staticmethod
    # async def send_action_accepted_message(channel, author: discord.User, items: str,
    #                                        quantity: int,
    #                                        skill: ActionType,
    #                                        mind_cost: int, materials: str, time_cost: int, commentary: str,
    #                                        resolve: int,
    #                                        time_of_completion: datetime):
    #
    #     embed = EmbedData(title='ACTION: %s', description='', color=discord.Color.teal())
    #     embed.thumbnail = 'https://static.thenounproject.com/png/106008-200.png'
    #     embed.add_field(name='mind cost', value=mind_cost, inline=True)
    #
    #     if resolve is not None:
    #         embed.add_field(name='resolve', value=resolve, inline=False)
    #
    #     if time_of_completion is None:
    #         embed.add_field(name='time in minutes', value='instant', inline=True)
    #         embed.add_field(name='to complete at', value='instant', inline=True)
    #     else:
    #         embed.add_field(name='time in minutes', value=time_cost, inline=True)
    #         embed.add_field(name='to complete at', value='%s' % time_of_completion
    #                         .strftime('%m/%d/%Y %I:%M:%S %p'), inline=True)
    #
    #     if materials is not None:
    #         embed.add_field(name='materials', value=materials, inline=True)
    #
    #     if commentary is not None and len(commentary) > 0:
    #         embed.add_field(name='comments', value=commentary, inline=False)
    #
    #     outbound_message = await channel.send(embed=embed.to_embed())
