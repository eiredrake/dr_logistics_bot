import sys
import discord
from discord.ext import commands
from discord_components import DiscordComponents
import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
BASE_DIR = Path(BASE_DIR)

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dr_logistics_web.settings')
# import django
# django.setup()

INSTALLED_APPS = [
    'logistics.apps.LogisticsConfig',
]

intents = discord.Intents().default()
intents.members = True
intents.messages = True
intents.dm_messages = True
intents.dm_reactions = True
intents.reactions = True
intents.emojis = True
intents.guild_messages = True
intents.guild_reactions = True

bot = commands.Bot(command_prefix='~', intents=intents)


@bot.event
async def on_ready():
    print('----------------------------------------')
    print('%s v. %s has connected to %s' % (
        bot.user.display_name,
        os.environ['BOT_VERSION'],
        bot.guilds[0].name
    ))
    print('----------------------------------------')


    cwd = os.getcwd()
    if cwd == '/dr_logistics':
        os.chdir('src')
        cwd = os.getcwd()

    path_to_cogs = os.path.join(cwd, "cogs")
    print("CWD DIR: %s" % cwd)
    print("COGS DIR: %s" % path_to_cogs)
    print("COGS DIR FOUND: %s" % os.path.exists(path_to_cogs))

    for filename in os.listdir(path_to_cogs):
        if filename.endswith('.py') and filename != '__init__.py':

            module = f'cogs.{filename[:-3]}'
            print("LOADING MODULE: %s" % module)

            try:
                bot.load_extension(module)
            except Exception as err:
                print("EXCEPTION LOADING MODULE: %s - %s " % (module, err))

    print('----------------------------------------')
    DiscordComponents(bot)

bot.run(env('DISCORD_TOKEN').strip())
