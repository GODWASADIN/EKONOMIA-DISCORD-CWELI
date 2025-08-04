
import discord
from discord.ext import commands, tasks
import json
import random
import asyncio
import os
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

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

@bot.command()
@commands.cooldown(1, 1800, commands.BucketType.user)
async def work(ctx):
    user = get_user(ctx.author.id)
    now = datetime.utcnow()
    earned = random.randint(20, 100)
    bonus = 0
    if user["reputation"] >= 50:
        bonus = int(earned * 0.2)
        earned += bonus
    user["wallet"] += earned
    user["reputation"] += 6
    user["last_work"] = now.isoformat()
    save_user(ctx.author.id, user)
    embed = discord.Embed(title="💼 Praca", description=f"Zarobiłeś {earned} 💸 (+{bonus} bonusu)", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def crime(ctx):
    user = get_user(ctx.author.id)
    success_chance = 0.75
    if user["reputation"] <= 21:
        success_chance = 0.9
    success = random.random() <= success_chance
    if success:
        earned = random.randint(50, 300)
        user["wallet"] += earned
        msg = f"Udało się! Ukradłeś {earned} 💸"
    else:
        lost = random.randint(200, 1000)
        user["wallet"] = max(0, user["wallet"] - lost)
        msg = f"Złapano cię! Straciłeś {lost} 💸"
    user["reputation"] -= 5
    user["last_crime"] = datetime.utcnow().isoformat()
    save_user(ctx.author.id, user)
    await ctx.send(f"🕵️ {msg}")

@bot.command()
@commands.cooldown(1, 2700, commands.BucketType.user)
async def slut(ctx):
    user = get_user(ctx.author.id)
    success = random.random() < 0.8
    if success:
        earned = random.randint(50, 200)
        user["wallet"] += earned
        msg = f"Zarobiłeś {earned} 💸 na brudnej robocie."
    else:
        lost = random.randint(50, 100)
        user["wallet"] = max(0, user["wallet"] - lost)
        msg = f"Nie udało się! Straciłeś {lost} 💸"
    user["reputation"] -= 2
    user["last_slut"] = datetime.utcnow().isoformat()
    save_user(ctx.author.id, user)
    await ctx.send(f"👠 {msg}")

@bot.command()
async def balance(ctx):
    user = get_user(ctx.author.id)
    embed = discord.Embed(title="💰 Twoje konto", color=discord.Color.gold())
    embed.add_field(name="Gotówka", value=f"{user['wallet']} 💸")
    embed.add_field(name="Bank", value=f"{user['bank']} 💰")
    embed.add_field(name="Reputacja", value=f"{user['reputation']}")
    await ctx.send(embed=embed)

@bot.command()
async def deposit(ctx, amount: str):
    user = get_user(ctx.author.id)
    if amount.lower() == "all":
        amount = user["wallet"]
    else:
        amount = int(amount)
    if amount > user["wallet"]:
        return await ctx.send("❌ Nie masz tyle gotówki.")
    user["wallet"] -= amount
    user["bank"] += amount
    save_user(ctx.author.id, user)
    await ctx.send(f"💼 Wpłacono {amount} 💸 do banku.")

@bot.command()
async def withdraw(ctx, amount: str):
    user = get_user(ctx.author.id)
    if amount.lower() == "all":
        amount = user["bank"]
    else:
        amount = int(amount)
    if amount > user["bank"]:
        return await ctx.send("❌ Nie masz tyle w banku.")
    user["bank"] -= amount
    user["wallet"] += amount
    save_user(ctx.author.id, user)
    await ctx.send(f"🏦 Wypłacono {amount} 💸 z banku.")

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    check_lottery.start()

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
        return await ctx.send("❌ Potrzebujesz przynajmniej 100 💸")
    user["wallet"] -= 100
    save_user(ctx.author.id, user)
    data = load_lottery()
    data["pool"] += 100
    if ctx.author.id not in data["players"]:
        data["players"].append(ctx.author.id)
    save_lottery(data)
    await ctx.send("🎟️ Kupiłeś los do loterii!")

@tasks.loop(minutes=1)
async def check_lottery():
    now = datetime.utcnow()
    if now.hour == 12 and now.minute == 0:
        data = load_lottery()
        if data["players"]:
            winner = random.choice(data["players"])
            winner_data = get_user(winner)
            winner_data["wallet"] += data["pool"]
            save_user(winner, winner_data)
            data["pool"] = 0
            data["players"] = []
            save_lottery(data)
            channel = discord.utils.get(bot.get_all_channels(), name="loteria")
            if channel:
                await channel.send(f"🎉 <@{winner}> wygrał loterię!")

bot.run(os.getenv("TOKEN"))


# Lista dostępnych biznesów
BUSINESSES = {
    "sklep": {"price": 25000, "income": 150, "rep": 2, "type": "legal"},
    "restauracja": {"price": 75000, "income": 400, "rep": 2, "type": "legal"},
    "warsztat": {"price": 150000, "income": 700, "rep": 2, "type": "legal"},
    "firma_it": {"price": 240000, "income": 900, "rep": 2, "type": "legal"},
    "marihuana": {"price": 90000, "income": 500, "rep": -5, "type": "illegal"},
    "kokaina": {"price": 300000, "income": 1000, "rep": -5, "type": "illegal"},
    "kasyno": {"price": 750000, "income": 2000, "rep": -5, "type": "illegal"},
    "import_export": {"price": 330000, "income": 1000, "rep": -5, "type": "booster"}
}

@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="🛒 Sklep z biznesami", color=discord.Color.blue())
    for name, biz in BUSINESSES.items():
        bonus = f"+{biz['rep']} rep" if biz['rep'] > 0 else f"{biz['rep']} rep"
        embed.add_field(name=name.capitalize(), value=f"Cena: {biz['price']} 💸\nDochód/h: {biz['income']} 💸\n{bonus}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, business_name: str):
    user = get_user(ctx.author.id)
    business_name = business_name.lower()
    if business_name not in BUSINESSES:
        return await ctx.send("❌ Nie ma takiego biznesu.")

    biz = BUSINESSES[business_name]
    cost = biz["price"]
    if user["reputation"] <= -50:
        cost = int(cost * 1.1)

    if user["wallet"] < cost:
        return await ctx.send("❌ Nie masz wystarczająco pieniędzy.")

    user["wallet"] -= cost
    user["reputation"] += biz["rep"]
    if business_name not in user["businesses"]:
        user["businesses"][business_name] = {"level": 1, "last_collected": datetime.utcnow().isoformat(), "paid_until": 0}
    else:
        user["businesses"][business_name]["level"] += 1
    save_user(ctx.author.id, user)
    await ctx.send(f"✅ Kupiono biznes: {business_name.capitalize()} za {cost} 💸!")

@bot.command()
async def collect(ctx):
    user = get_user(ctx.author.id)
    now = datetime.utcnow()
    total_collected = 0
    for biz_name, info in user["businesses"].items():
        if biz_name not in BUSINESSES:
            continue
        biz = BUSINESSES[biz_name]
        last_collected = datetime.fromisoformat(info["last_collected"])
        hours = int((now - last_collected).total_seconds() // 3600)
        if hours < 1:
            continue
        income = biz["income"]
        if user["reputation"] >= 50 and biz["type"] == "legal":
            income = int(income * 1.1)
        if info.get("paid_until", 0) < hours:
            continue  # nieopłacony biznes
        collected = income * hours * info["level"]
        total_collected += collected
        info["last_collected"] = now.isoformat()
    save_user(ctx.author.id, user)
    user["wallet"] += total_collected
    await ctx.send(f"💼 Zebrano {total_collected} 💸 z biznesów.")


@bot.command()
async def upgrade(ctx, business_name: str):
    user = get_user(ctx.author.id)
    business_name = business_name.lower()
    if business_name not in user["businesses"]:
        return await ctx.send("❌ Nie posiadasz tego biznesu.")

    biz = BUSINESSES.get(business_name)
    if not biz:
        return await ctx.send("❌ Ten biznes nie istnieje.")

    current_level = user["businesses"][business_name]["level"]
    if current_level >= 5:
        return await ctx.send("🔒 Ten biznes osiągnął maksymalny poziom (5).")

    upgrade_cost = int(biz["price"] * 0.5)
    if user["wallet"] < upgrade_cost:
        return await ctx.send(f"❌ Ulepszenie kosztuje {upgrade_cost} 💸. Nie masz wystarczająco pieniędzy.")

    user["wallet"] -= upgrade_cost
    user["businesses"][business_name]["level"] += 1
    save_user(ctx.author.id, user)
    await ctx.send(f"⬆️ Ulepszono {business_name.capitalize()} do poziomu {current_level + 1} za {upgrade_cost} 💸.")

@bot.command()
async def pay(ctx, business_name: str, days: int):
    user = get_user(ctx.author.id)
    business_name = business_name.lower()

    if business_name not in user["businesses"]:
        return await ctx.send("❌ Nie posiadasz tego biznesu.")
    if business_name not in BUSINESSES:
        return await ctx.send("❌ Ten biznes nie istnieje.")

    biz = BUSINESSES[business_name]
    daily_cost = int(biz["income"] * 24 * 0.10)
    total_cost = daily_cost * days

    if user["wallet"] < total_cost:
        return await ctx.send(f"❌ Opłacenie {days} dni kosztuje {total_cost} 💸. Nie masz wystarczająco pieniędzy.")

    user["wallet"] -= total_cost
    user["businesses"][business_name]["paid_until"] += days
    save_user(ctx.author.id, user)
    await ctx.send(f"✅ Opłacono {business_name.capitalize()} na {days} dni. Koszt: {total_cost} 💸.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining = round(error.retry_after, 1)
        await ctx.send(f"🕒 Musisz odczekać jeszcze {remaining} sekundy przed ponownym użyciem komendy.")
    else:
        raise error
