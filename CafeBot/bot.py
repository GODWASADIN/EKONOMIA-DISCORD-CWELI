import discord
from discord.ext import commands
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="📋 Dostępne komendy:", color=discord.Color.gold())
        embed.description = (
            "・!work – Pracuj i zarób pieniądze
"
            "・!crime – Podejmij się przestępstwa
"
            "・!slut – Zarabiaj jako prostytutka
"
            "・!balance – Sprawdź stan konta
"
            "・!deposit – Wpłać gotówkę do banku
"
            "・!withdraw – Wypłać gotówkę z banku
"
            "・!buy – Kup biznes lub przedmiot
"
            "・!shop – Zobacz sklep
"
            "・!sell – Sprzedaj biznes
"
            "・!collect – Zbierz zyski z biznesów
"
            "・!upgrade – Ulepsz biznes
"
            "・!pay – Opłać biznes
"
            "・!bj – Zagraj w blackjacka
"
            "・!slots – Zagraj na automatach
"
            "・!coinflip – Rzut monetą
"
            "・!duel – Wyzwanie na pojedynek
"
            "・!roulette – Zagraj w ruletkę
"
            "・!invest – Zainwestuj gotówkę
"
            "・!checkinvest – Sprawdź inwestycje
"
            "・!lottery – Kup bilet na loterię
"
            "・!rob – Okradnij gracza
"
            "・!rep – Sprawdź reputację
"
            "・!redeem – Odkup reputację
"
            "・!top – Ranking najbogatszych
"
            "・!btop – Ranking biznesmenów
"
            "・!crypto – Zarządzanie BTC"
        )
        await ctx.send(embed=embed)
    else:
        raise error

bot.run(TOKEN)
