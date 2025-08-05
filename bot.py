# Główny plik bota
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')

bot.run(os.getenv('DISCORD_TOKEN'))