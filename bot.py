
import discord
from discord.ext import commands, tasks
import json
import random
import asyncio
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Ładowanie danych użytkowników
def get_user(user_id):
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

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
        with open("users.json", "w") as f:
            json.dump(data, f, indent=4)

    return data[uid]

def save_user(user_id, user_data):
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    data[str(user_id)] = user_data
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# Przykładowa komenda !work
@bot.command()
@commands.cooldown(1, 1800, commands.BucketType.user)  # 30 minut
async def work(ctx):
    user = get_user(ctx.author.id)
    now = datetime.utcnow()
    min_earn = 20
    max_earn = 100
    earned = random.randint(min_earn, max_earn)
    bonus = 0

    if user["reputation"] >= 50:
        bonus = int(earned * 0.2)
        earned += bonus

    user["wallet"] += earned
    user["reputation"] += 6
    user["last_work"] = now.isoformat()

    save_user(ctx.author.id, user)

    embed = discord.Embed(
        title="💼 Praca wykonana!",
        description=f"Zarobiłeś {earned} 💸 (bonus: {bonus} 💸)
Reputacja: +6",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    check_lottery.start()

# Przykładowa loteria
LOTTERY_FILE = "lottery.json"

def load_lottery():
    try:
        with open(LOTTERY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"pool": 0, "players": []}

def save_lottery(data):
    with open(LOTTERY_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.command()
async def lottery(ctx):
    user = get_user(ctx.author.id)
    if user["wallet"] < 100:
        await ctx.send("❌ Nie masz wystarczającej ilości gotówki (💸 100).")
        return

    user["wallet"] -= 100
    save_user(ctx.author.id, user)

    lottery_data = load_lottery()
    lottery_data["pool"] += 100
    if ctx.author.id not in lottery_data["players"]:
        lottery_data["players"].append(ctx.author.id)
    save_lottery(lottery_data)

    await ctx.send(f"🎟️ Kupiono los! Aktualna pula: 💸 {lottery_data['pool']}")

@tasks.loop(minutes=1)
async def check_lottery():
    now = datetime.utcnow()
    if now.hour == 12 and now.minute == 0:
        data = load_lottery()
        if data["players"]:
            winner_id = random.choice(data["players"])
            winner = get_user(winner_id)
            winner["wallet"] += data["pool"]
            save_user(winner_id, winner)

            channel = discord.utils.get(bot.get_all_channels(), name="loteria")
            if channel:
                await channel.send(f"🎉 Gratulacje <@{winner_id}>! Wygrałeś loterię i zgarnąłeś 💸 {data['pool']}!")

            data["pool"] = 0
            data["players"] = []
            save_lottery(data)

bot.run("TU_WKLEJ_TOKEN")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining = round(error.retry_after, 1)
        await ctx.send(f"🕒 Musisz odczekać {remaining}s przed ponownym użyciem tej komendy.")
    else:
        raise error


@bot.command()
async def reputation(ctx):
    user = get_user(str(ctx.author.id))
    rep = user["reputation"]
    await ctx.send(f"📈 Twoja reputacja: {rep}")
