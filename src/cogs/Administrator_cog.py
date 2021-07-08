import re

import discord
from discord.ext import commands

from src.constants.RegularExpressions import BASIC_STRING_FIELD_EXPRESSION, TITLE_FIELD_NAME, DESCRIPTION_FIELD_NAME, \
    COLOR_FIELD_NAME, TAGGED_STRING_FIELD_EXPRESSION, FIELD, VALUE
from src.data.EmbedData import EmbedData


class Administrator_cog(commands.Cog, name='administrator commands'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command('clear', description='Clears the current channel', help='Deletes all messages in the current channel')
    @commands.has_any_role('Admin')
    async def clear(self, ctx, limit: int = 9999):
        print('Clearing channel messages')
        messages = await ctx.message.channel.history(limit=limit).flatten()
        for message in messages:
            if message.pinned is False:
                await message.delete()

        print('Messages cleared')

    @commands.command('post', description='Post a message as an embed to the current channel', help='Posts a message as an embed to the current channel')
    @commands.has_any_role('Admin', 'Staff', 'bot_testing')
    async def post(self, ctx: commands.Context, *, arguments: str):
        if ctx.message.author == self.bot:
            return

        embed_data = EmbedData()
        title = None
        title_group = re.search(BASIC_STRING_FIELD_EXPRESSION % TITLE_FIELD_NAME, arguments)
        if title_group is None:
            raise discord.ext.commands.MissingRequiredArgument('You must specify a %s for the message' % TITLE_FIELD_NAME)
        else:
            embed_data.title = title_group.group(TITLE_FIELD_NAME).strip()

        description = None
        expression = TAGGED_STRING_FIELD_EXPRESSION % (DESCRIPTION_FIELD_NAME, DESCRIPTION_FIELD_NAME)
        description_group = re.search(expression, arguments)
        if description_group is None:
            raise discord.ext.commands.MissingRequiredArgument('You must specify a %s for the message' % DESCRIPTION_FIELD_NAME)
        else:
            embed_data.description = description_group.group(DESCRIPTION_FIELD_NAME).strip()

        color = discord.Color.default()
        color_group = re.search(TAGGED_STRING_FIELD_EXPRESSION % (COLOR_FIELD_NAME, COLOR_FIELD_NAME), arguments)
        if color_group is not None:
            embed_data.color = int(hex(int(color_group.group(COLOR_FIELD_NAME).replace("#", ""), 16)), 0)

        message = await ctx.channel.send('editing...')

        embed = embed_data.to_embed(message.id)
        await message.edit(content='', embed=embed)

    @commands.command('edit')
    @commands.has_any_role('Admin', 'Staff')
    async def edit(self, ctx, messageId: int, *, arguments):
        message = await ctx.channel.fetch_message(messageId)
        if ctx.message.author == self.bot:
            return

        if message is None:
            raise discord.ext.commands.MissingRequiredArgument("Cannot find message")

        embed = message.embeds[0]
        if embed is None:
            raise discord.ext.commands.MissingRequiredArgument("Message has no embeds")

        field = None
        field_group = re.search(TAGGED_STRING_FIELD_EXPRESSION % (FIELD, FIELD), arguments)
        if field_group is None:
            raise discord.ext.commands.MissingRequiredArgument("You must specify a field to edit")

        field = field_group.group('field').strip()

        value = None

        value_regex = TAGGED_STRING_FIELD_EXPRESSION % (VALUE, VALUE)
        if field == 'thumbnail' or field == 'image':
            value_regex = r"/value\s?:?\s?['|\"](?P<value>.*)['|\"]"
        elif field == 'color':
            value_regex = r'/value\s?:?\s?(?P<value>#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}))'

        value_group = re.search(value_regex, arguments)
        if value_group is None:
            raise discord.ext.commands.MissingRequiredArgument(
                "You must specify a value for the field you wish to edit")

        value = value_group.group('value').strip()

        in_line = True
        in_line_group = re.search(r'/inline:?\s?(?P<inline>[true|false|yes|no|t|f|y|n])', arguments.lower())
        if in_line_group is not None:
            in_line_group = in_line_group.group('inline')
            if in_line_group is not None:
                in_line = bool(in_line_group)

        if len(value) > 0:
            if field == 'title':
                embed = EmbedData.copy_embed(embed, title=value)
            elif field == 'description':
                embed = EmbedData.copy_embed(embed, description=value)
            elif field == 'color':
                value = int(hex(int(value.replace("#", ""), 16)), 0)
                embed = EmbedData.copy_embed(embed, color=value)
            elif field == 'thumbnail':
                embed.set_thumbnail(url=value)
            elif field == 'image':
                embed.set_image(url=value)
            else:
                field_index = next((i for i, item in enumerate(embed.fields) if item.name == field), -1)
                if field_index > -1:
                    embed.set_field_at(field_index, name=field, value=value, inline=in_line)
                else:
                    embed.add_field(name=field, value=value, inline=in_line)

        await message.edit(embed=embed)

    @edit.error
    async def edit_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send(error)


def setup(bot):
    print('\tAdministrator_cog is loading')
    bot.add_cog(Administrator_cog(bot))
