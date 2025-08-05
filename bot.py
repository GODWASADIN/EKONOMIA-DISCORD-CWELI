import discord
from discord.ext import commands
import os  # <--- brakujący import

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')

bot.run(os.getenv('DISCORD_TOKEN'))
