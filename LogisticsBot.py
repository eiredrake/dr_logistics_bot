import sys
import discord
from discord.ext import commands
import os

from discord_components import DiscordComponents

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dr_logistics_bot.settings')
import django
django.setup()


intents = discord.Intents().default()
intents.members = True
intents.messages = True
intents.dm_messages = True
intents.dm_reactions = True
intents.reactions = True
intents.emojis = True
intents.guild_messages = True
intents.guild_reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print('----------------------------------------')
    print('%s v. %s has connected' % (
        bot.user.display_name,
        os.environ['BOT_VERSION'],
    ))

    path_to_cogs = os.path.join(os.getcwd(), 'src/cogs')
    print("COGS DIR: %s" % path_to_cogs)
    for filename in os.listdir(path_to_cogs):
        if filename.endswith('.py') and filename != '__init__.py':
            module = f'src.cogs.{filename[:-3]}'
            bot.load_extension(module)

    print('----------------------------------------')
    DiscordComponents(bot)

bot.run(os.environ['DISCORD_TOKEN'].strip())
