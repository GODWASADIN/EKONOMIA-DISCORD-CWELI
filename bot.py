# CafeBot - Pełny bot z systemem ekonomii, minigrami, kryptowalutami i biznesami
# Autor: OpenAI + Ty

import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime, timedelta
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

def get_user(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "wallet": 0,
            "bank": 0,
            "reputation": 0,
            "btc": 0.0,
            "last_work": "2000-01-01T00:00:00",
            "last_crime": "2000-01-01T00:00:00",
            "last_slut": "2000-01-01T00:00:00",
            "last_rob": "2000-01-01T00:00:00",
            "jail_until": "2000-01-01T00:00:00",
            "businesses": {},
            "crypto": {},
            "stats": {}
        }
    return data[uid]

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

@bot.command()
async def balance(ctx):
    data = load_data()
    user = get_user(data, ctx.author.id)

    embed = discord.Embed(title=f"💼 {ctx.author.name} – Stan konta", color=discord.Color.gold())
    embed.add_field(name="💰 Gotówka", value=f"{user['wallet']} 💸", inline=False)
    embed.add_field(name="🏦 Bank", value=f"{user.get('bank', 0)} 💰", inline=False)
    embed.add_field(name="📈 Reputacja", value=f"{user['reputation']} 🌟", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def work(ctx):
    data = load_data()
    user = get_user(data, ctx.author.id)
    now = datetime.utcnow()
    last_used = datetime.fromisoformat(user["last_work"])

    if now - last_used < timedelta(minutes=30):
        remaining = timedelta(minutes=30) - (now - last_used)
        return await ctx.send(f'⏳ Użyj ponownie za {remaining.seconds // 60}m {remaining.seconds % 60}s')

    base_earnings = random.randint(20, 100)
    bonus = 1.2 if user["reputation"] >= 50 else 1.0
    earnings = int(base_earnings * bonus)

    user["wallet"] += earnings
    user["reputation"] += 6
    user["last_work"] = now.isoformat()

    save_data(data)
    await ctx.send(f'👷‍♂️ Pracujesz legalnie i zarabiasz 💸 {earnings}.
📈 Reputacja: +6')

bot.run(TOKEN)
