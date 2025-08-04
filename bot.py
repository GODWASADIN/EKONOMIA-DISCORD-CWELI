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


ITEMS = {
    "Zdrapka": {
        "price": 500,
        "description": "Losowa wygrana: 100–1000 💰"
    },
    "Zdrapkagold": {
        "price": 3000,
        "description": "Losowa wygrana: 1000–5000 💰"
    },
    "Zdrapkapremium": {
        "price": 7500,
        "description": "Losowa wygrana: 5000–10000 💰"
    },
    "Automaty": {
        "price": 2_500_000,
        "description": "Możliwość tworzenia tymczasowych kanałów głosowych"
    },
    "Nitrobasic": {
        "price": 10_000_000,
        "description": "Prestiżowy przedmiot bez dodatkowych funkcji"
    },
    "Nitro": {
        "price": 30_000_000,
        "description": "Prestiżowy przedmiot bez dodatkowych funkcji"
    }
}


# -----------------------------
# 💼 Biznesy – konfiguracja
# -----------------------------
BUSINESSES = {
    "sklep":         {"price": 25000,  "income": 150,  "rep_effect": 2,  "type": "legal"},
    "restauracja":   {"price": 75000,  "income": 400,  "rep_effect": 2,  "type": "legal"},
    "warsztat":      {"price": 150000, "income": 700,  "rep_effect": 2,  "type": "legal"},
    "firma it":      {"price": 240000, "income": 900,  "rep_effect": 2,  "type": "legal"},
    "marihuana":     {"price": 90000,  "income": 500,  "rep_effect": -5, "type": "illegal"},
    "kokaina":       {"price": 300000, "income": 1000, "rep_effect": -5, "type": "illegal"},
    "kasyno":        {"price": 750000, "income": 2000, "rep_effect": -5, "type": "illegal"},
    "import/export": {"price": 330000, "income": 1000, "rep_effect": -5, "type": "nitro"},
    }
    

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
@commands.cooldown(1, 1800, commands.BucketType.user)  # 30 minut cooldown
async def work(ctx):
    user_id = str(ctx.author.id)
    user = get_user(user_id)

    base_earn = random.randint(20, 100)
    bonus = 1.2 if user['reputation'] >= 50 else 1.0
    total_earn = round(base_earn * bonus)

    user['wallet'] += total_earn
    user['reputation'] += 6
    save_data()

    descriptions = [
        f"Zagrałeś z nikishale customa zarobiłeś 💸 {total_earn}.",
        f"Zbudowałeś heartsteela zarobiłeś 💸 {total_earn}.",
        f"Znalazłeś 💸 {total_earn} pod stolikiem!",
        f"Znalazłeś 💸 {total_earn} we wczorajszych spodniach!",
        f"Weekendy spędzasz na discordzie. Zarabiasz 💸 {total_earn}.",
    ]

    embed = discord.Embed(
        title="🧰 Praca",
        description=random.choice(descriptions),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Gotówka: 💸 {user['wallet']} | Reputacja: {user['reputation']}")
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, 3600, commands.BucketType.user)  # 1 godzina cooldown
async def crime(ctx):
    user_id = str(ctx.author.id)
    user = get_user(user_id)

    # Obniż reputację
    user['reputation'] -= 5

    # Szanse
    fail_chance = 0.20
    if user['reputation'] <= 21:
        fail_chance = 0.10
    elif user['reputation'] <= -75:
        fail_chance = 0.60  # Kara: niższa reputacja = większa szansa porażki

    success = random.random() > fail_chance

    if success:
        amount = random.randint(50, 300)
        user['wallet'] += amount
        result_text = f"Perfekcyjnie zagrałeś smokiem pod heartstela zgarniasz 💸 {amount}."
        color = discord.Color.orange()
    else:
        loss_cash = random.randint(200, 400)
        user['wallet'] = max(0, user['wallet'] - loss_cash)
        jail_time = 30  # minutes, just for reference
        user['reputation'] -= 5  # dodatkowe -5 za więzienie
        result_text = f"Niestety zagrałeś z nikishale ale zbudowałeś buty 💸 {loss_cash}."
        color = discord.Color.red()

    save_data()

    embed = discord.Embed(
        title="🚨 Przestępstwo",
        description=result_text,
        color=color
    )
    embed.set_footer(text=f"Gotówka: 💸 {user['wallet']} | Reputacja: {user['reputation']}")
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, 2700, commands.BucketType.user)  # 45 minut cooldown
async def slut(ctx):
    user_id = str(ctx.author.id)
    user = get_user(user_id)

    # -2 reputacji za każdą próbę
    user['reputation'] -= 2

    success_chance = 0.80
    success = random.random() < success_chance

    if success:
        earnings = random.randint(50, 200)
        user['wallet'] += earnings
        result_text = f"Brawo! Twoja usługa warta 💸 {earnings} zrobiła furorę!"
        color = discord.Color.orange()
    else:
        loss = random.randint(50, 100)
        user['wallet'] = max(0, user['wallet'] - loss)
        result_text = (
            f"Niestety przegrałeś customa.\n"
            f"Budząc się bez portfela, straciłeś 💸 {loss}."
        )
        color = discord.Color.red()


@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    user = get_user(user_id)

    embed = discord.Embed(
        title="💳 Stan konta",
        description=f"Gotówka: 💸 {user['wallet']}\nBank: 🏦 {user['bank']}\nReputacja: {user['reputation']}",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)


@bot.command()
async def deposit(ctx, amount):
    user_id = str(ctx.author.id)
    user = get_user(user_id)

    if amount.lower() == "all":
        amount = user['wallet']
    else:
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send("❌ Podaj poprawną liczbę lub 'all'.")

    if amount <= 0 or amount > user['wallet']:
        return await ctx.send("❌ Nie masz tyle gotówki!")

    user['wallet'] -= amount
    user['bank'] += amount
    save_data()

    await ctx.send(f"💰 Wpłaciłeś 💸 {amount} do banku. Gotówka: 💸 {user['wallet']}, Bank: 🏦 {user['bank']}")


@bot.command()
async def withdraw(ctx, amount):
    user_id = str(ctx.author.id)
    user = get_user(user_id)

    if amount.lower() == "all":
        amount = user['bank']
    else:
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.send("❌ Podaj poprawną liczbę lub 'all'.")

    if amount <= 0 or amount > user['bank']:
        return await ctx.send("❌ Nie masz tyle w banku!")

    user['bank'] -= amount
    user['wallet'] += amount
    save_data()

    await ctx.send(f"💸 Wypłaciłeś {amount} z banku. Gotówka: 💸 {user['wallet']}, Bank: 🏦 {user['bank']}")




@bot.command()
async def buy(ctx, *, business_name):
    user_id = str(ctx.author.id)
    user = get_user(user_id)
    name = business_name.lower()

    if name not in BUSINESSES:
        return await ctx.send("❌ Nie ma takiego biznesu lub przedmiotu.")

    item = BUSINESSES[name]
    price = item["price"]

    # Kara za reputację
    if user["reputation"] <= -50:
        price = int(price * 1.1)  # +10%

    if user["wallet"] < price:
        return await ctx.send(f"❌ Nie masz 💸 {price}, by kupić {name.title()}.")

    # Nitro check (jeśli chcesz dodać potem)
    if item["type"] == "nitro":
        # Możesz tu dodać warunek: ctx.author.premium_since is None
        pass  # na razie każdy może kupić

    # Dodaj biznes
    user["wallet"] -= price
    user["businesses"][name] = {
        "level": 1,
        "last_collected": datetime.utcnow().isoformat(),
        "paid_until": datetime.utcnow().isoformat()
    }

    user["reputation"] += item["rep_effect"]
    save_data()

    embed = discord.Embed(
        title="🛍️ Zakup",
        description=f"Kupiłeś **{name.title()}** za 💸 {price}.",
        color=discord.Color.green()
    )
    embed.add_field(name="Dochód/h", value=f"💸 {item['income']}", inline=True)
    embed.add_field(name="Reputacja", value=f"{item['rep_effect']} pkt", inline=True)
    embed.set_footer(text=f"Nowa reputacja: {user['reputation']} | Gotówka: {user['wallet']}")
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)




@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="📘 Jak działa ekonomia?",
        description="Pełny system zarabiania, reputacji i biznesów",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="💰 Gotówka i bank",
        value=(
            "Zarabiasz gotówkę przez `!work`, `!crime`, `!biznesy`, minigry itp.\n"
            "Możesz wpłacać do banku przez `!deposit`, ale do grania i zakupów potrzebujesz gotówki przy sobie."
        ),
        inline=False
    )

    embed.add_field(
        name="🏢 Biznesy",
        value="Kup legalne i nielegalne biznesy, które generują dochód co godzinę (`!buy`, `!collect`).",
        inline=False
    )

    embed.add_field(
        name="🌟 Reputacja",
        value=(
            "Zwiększa się przy legalnej pracy, maleje przy przestępstwach.\n"
            "`-100` do `+100`. Im wyższa, tym większe bonusy, ale niska = kary!"
        ),
        inline=False
    )

    embed.add_field(
        name="🎰 Minigry",
        value="Blackjack, automaty, rzut monetą – graj gotówką, ryzykuj, wygrywaj (`!bj`, `!slots`, `!coinflip`).",
        inline=False
    )

    embed.add_field(
        name="🔫 Napady",
        value="Możesz okradać innych (`!rob`) – ale tylko gotówkę, nie bank. Szansa na wpadkę = więzienie!",
        inline=False
    )

    embed.add_field(
        name="🎟️ Loteria",
        value="Codziennie o 12:00 losowanie wygranej z puli! (`!lottery`)",
        inline=False
    )

    embed.add_field(
        name="🔥 Eventy",
        value="Co godzinę 20% szansy na event, który mnoży zarobki z `!work`, `!crime`, `!slut` nawet 3x!",
        inline=False
    )

    await ctx.send(embed=embed)



@bot.command()
async def collect(ctx):
    user_id = str(ctx.author.id)
    user = get_user(user_id)

    if not user["businesses"]:
        return await ctx.send("❌ Nie masz żadnych biznesów.")

    now = datetime.utcnow()
    total_income = 0
    total_rep = 0
    messages = []

    for name, info in user["businesses"].items():
        biz = BUSINESSES.get(name)
        if not biz:
            continue  # ignoruj nieznane

        last_collected = datetime.fromisoformat(info["last_collected"])
        paid_until = datetime.fromisoformat(info["paid_until"])

        if now <= paid_until:
            hours = int((now - last_collected).total_seconds() // 3600)
            if hours >= 1:
                level = info.get("level", 1)
                income_per_hour = biz["income"]

                # BONUS: jeśli reputacja ≥ 50 i to legalny biznes
                if biz["type"] == "legal" and user["reputation"] >= 50:
                    income_per_hour = int(income_per_hour * 1.10)

                earned = income_per_hour * hours * level
                total_income += earned
                user["wallet"] += earned
                user["businesses"][name]["last_collected"] = now.isoformat()

                # Reputacja: tylko przy legalnych
                if biz["type"] == "legal":
                    user["reputation"] += 2
                    total_rep += 2

                messages.append(f"🏢 {name.title()}: +💸 {earned} za {hours}h")
        else:
            messages.append(f"⛔ {name.title()} nieopłacony – brak dochodu.")

    save_data()

    if total_income == 0:
        return await ctx.send("⏳ Nie minęła pełna godzina od ostatniego zbierania lub nie masz opłaconych biznesów.")

    embed = discord.Embed(
        title="📦 Zbieranie dochodów",
        description="\n".join(messages),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"💸 +{total_income} | 📈 Reputacja: +{total_rep} | Obecnie: {user['wallet']} 💰")

    await ctx.send(embed=embed)
   
    
    
    @bot.command()
    async def upgrade(ctx, *, business_name):
    user_id = str(ctx.author.id)
    user = get_user(user_id)
    name = business_name.lower()

    if name not in user["businesses"]:
        return await ctx.send("❌ Nie posiadasz tego biznesu.")

    if name not in BUSINESSES:
        return await ctx.send("❌ Ten biznes nie istnieje.")

    level = user["businesses"][name]["level"]
    if level >= 5:
        return await ctx.send("⚠️ Ten biznes ma już maksymalny poziom (5).")

    base_price = BUSINESSES[name]["price"]
    upgrade_cost = int(base_price * 0.5 * level)

    if user["wallet"] < upgrade_cost:
        return await ctx.send(f"❌ Potrzebujesz 💸 {upgrade_cost}, by ulepszyć ten biznes.")

    user["wallet"] -= upgrade_cost
    user["businesses"][name]["level"] += 1
    save_data()

    embed = discord.Embed(
        title="⬆️ Ulepszenie biznesu",
        description=(
            f"Biznes **{name.title()}** awansował na poziom **{level + 1}**!\n"
            f"💸 Koszt ulepszenia: {upgrade_cost}\n"
            f"📈 Dochód/h zwiększony o +20%!"
        ),
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Pozostała gotówka: 💸 {user['wallet']}")
    await ctx.send(embed=embed)



@bot.command()
async def pay(ctx, business_name: str, days: int):
    user_id = str(ctx.author.id)
    user = get_user(user_id)
    name = business_name.lower()

    if name not in user["businesses"]:
        return await ctx.send("❌ Nie posiadasz takiego biznesu.")

    if name not in BUSINESSES:
        return await ctx.send("❌ Ten biznes nie istnieje.")

    if days <= 0:
        return await ctx.send("❌ Podaj liczbę dni większą od zera.")

    level = user["businesses"][name].get("level", 1)
    daily_cost = int((BUSINESSES[name]["income"] * level) * 0.10)
    total_cost = daily_cost * days

    if user["wallet"] < total_cost:
        return await ctx.send(f"❌ Potrzebujesz 💸 {total_cost}, by opłacić {days} dni.")

    # Zapłać
    user["wallet"] -= total_cost

    # Przedłużenie daty
    current_paid = datetime.fromisoformat(user["businesses"][name]["paid_until"])
    now = datetime.utcnow()
    new_paid_until = max(current_paid, now) + timedelta(days=days)

    user["businesses"][name]["paid_until"] = new_paid_until.isoformat()
    save_data()

    embed = discord.Embed(
        title="💸 Opłacenie biznesu",
        description=(
            f"Biznes **{name.title()}** opłacony na **{days} dni**.\n"
            f"🧾 Koszt dzienny: {daily_cost} × {days} dni = 💸 {total_cost}\n"
            f"📆 Nowy termin ważności: `{new_paid_until.strftime('%Y-%m-%d %H:%M')}`"
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Pozostała gotówka: 💸 {user['wallet']}")
    await ctx.send(embed=embed)



@bot.command()
async def buy(ctx, *, name):
    user_id = str(ctx.author.id)
    user = get_user(user_id)
    item_name = name.title()

    # — BIZNES —
    if item_name.lower() in BUSINESSES:
        biz = BUSINESSES[item_name.lower()]
        is_nitro = biz.get("type") == "nitro"
        rep = user["rep"]

        # Tylko Nitro
        if is_nitro and not any(r.name == "Nitro Booster" for r in ctx.author.roles):
            return await ctx.send("🔒 Ten biznes jest tylko dla Nitro Boosterów.")

        # Cena z karą/bonusem
        price = biz["price"]
        if rep <= -50:
            price = int(price * 1.1)
        elif rep >= 50 and biz["type"] == "legal":
            price = int(price * 0.9)

        if user["wallet"] < price:
            return await ctx.send(f"❌ Potrzebujesz 💸 {price}, by kupić ten biznes.")

        # Kup
        user["wallet"] -= price
        user["rep"] += biz["rep_effect"]
        user["businesses"][item_name.lower()] = {
            "level": 1,
            "paid_until": datetime.utcnow().isoformat(),
            "collected_at": datetime.utcnow().isoformat()
        }

        save_data()
        return await ctx.send(
            f"✅ Kupiłeś biznes **{item_name}** za 💸 {price}.\n📈 Reputacja: {user['rep']}")

    # — PRZEDMIOT —
    elif item_name in ITEMS:
        item = ITEMS[item_name]
        price = item["price"]

        if user["wallet"] < price:
            return await ctx.send(f"❌ Potrzebujesz 💸 {price}, by kupić ten przedmiot.")

        user["wallet"] -= price
        user["items"][item_name] = user["items"].get(item_name, 0) + 1

        # Obsługa zdrapek
        if item_name.lower().startswith("Zdrapka".lower()):
            if "premium" in item_name.lower():
                reward = random.randint(5000, 10000)
            elif "gold" in item_name.lower():
                reward = random.randint(1000, 5000)
            else:
                reward = random.randint(100, 1000)
            user["wallet"] += reward
            save_data()
            return await ctx.send(
                f"🎟️ Kupiłeś {item_name} za 💸 {price}!\n💰 Wygrana: {reward} 💸\nGotówka: {user['wallet']}")

        save_data()
        return await ctx.send(f"🛒 Kupiłeś przedmiot **{item_name}** za 💸 {price}!")

    else:
        return await ctx.send("❌ Nie ma takiego biznesu ani przedmiotu.")


import random
import asyncio

def draw_card():
    cards = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 10, 'Q': 10, 'K': 10, 'A': 11
    }
    card = random.choice(list(cards.items()))
    return card

def calculate_total(hand):
    total = sum(card[1] for card in hand)
    # Obsługa Asów
    num_aces = sum(1 for card in hand if card[0] == 'A')
    while total > 21 and num_aces:
        total -= 10
        num_aces -= 1
    return total

@bot.command(aliases=["bj"])
async def blackjack(ctx, amount: int):
    user = get_user_data(ctx.author.id)
    if user["cash"] < amount:
        return await ctx.send("❌ Nie masz wystarczająco gotówki!")

    player_hand = [draw_card(), draw_card()]
    dealer_hand = [draw_card(), draw_card()]

    player_total = calculate_total(player_hand)
    dealer_total = calculate_total(dealer_hand)

    msg = await ctx.send(embed=discord.Embed(
        title="🎲 Blackjack",
        description=(
            f"Twoje karty: {', '.join(card[0] for card in player_hand)} (**{player_total}**)\n"
            f"Karta krupiera: {dealer_hand[0][0]} + ❓\n\n"
            f"Chcesz dobrać kartę za 💰 {amount}?\n"
            "✅ = Tak | ❌ = Nie (10s)"
        ),
        color=discord.Color.dark_blue()
    ).set_image(url="https://media.tenor.com/mYsJhBKt3UoAAAAd/blackjack.gif"))

    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(reaction, user_check):
        return user_check == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == msg.id

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=10.0, check=check)
    except asyncio.TimeoutError:
        return await ctx.send("⌛ Czas minął. Gra anulowana.")

    if str(reaction.emoji) == "✅":
        # Dobierasz
        player_hand.append(draw_card())
        player_total = calculate_total(player_hand)

        if player_total > 21:
            user["cash"] -= amount
            save_user_data(ctx.author.id, user)
            return await ctx.send(f"💥 Przekroczyłeś 21 ({player_total})! Przegrywasz 💸 {amount}.")

    # Krupier dobiera do min. 17
    while dealer_total < 17:
        dealer_hand.append(draw_card())
        dealer_total = calculate_total(dealer_hand)

    result_msg = (
        f"**Twoje karty:** {', '.join(c[0] for c in player_hand)} (**{player_total}**)\n"
        f"**Krupier:** {', '.join(c[0] for c in dealer_hand)} (**{dealer_total}**)\n\n"
    )

    if player_total > 21:
        result_msg += f"❌ Przegrywasz 💸 {amount}!"
        user["cash"] -= amount
    elif dealer_total > 21 or player_total > dealer_total:
        multiplier = 2.5 if player_total == 21 and len(player_hand) == 2 else 2
        winnings = int(amount * multiplier)
        result_msg += f"✅ Wygrałeś **{winnings}** 💸!"
        user["cash"] += winnings
    elif player_total == dealer_total:
        result_msg += "🤝 Remis! Zachowujesz pieniądze."
    else:
        result_msg += f"❌ Przegrywasz 💸 {amount}!"
        user["cash"] -= amount

    save_user_data(ctx.author.id, user)
    await ctx.send(result_msg)

@bot.command()
async def slots(ctx, amount: int):
    async def play_slots():
        user_id = str(ctx.author.id)
        user = get_user_data(user_id)

        if amount <= 0:
            return await ctx.send("❌ Podaj poprawną kwotę.")
        if user["cash"] < amount:
            return await ctx.send("❌ Nie masz tyle gotówki!")

        symbols = ["🍒", "🍋", "💎", "🍀", "🔔"]
        result = [random.choice(symbols) for _ in range(3)]
        counts = {symbol: result.count(symbol) for symbol in symbols}

        win_multiplier = 0
        if 3 in counts.values():
            win_multiplier = 5
        elif 2 in counts.values():
            win_multiplier = 2

        win_amount = amount * win_multiplier
        user["cash"] -= amount

        if win_multiplier > 0:
            user["cash"] += win_amount
            outcome = f"🎉 Wygrałeś **{win_amount}** 💸!"
        else:
            outcome = f"😢 Przegrałeś **{amount}** 💸."

        save_user_data(user_id, user)

        embed = discord.Embed(
            title="🎰 Automat do gry",
            description=f"{' | '.join(result)}\n\n{outcome}",
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"💰 Gotówka: {user['cash']}")
        msg = await ctx.send(embed=embed)

        await msg.add_reaction("🎮")

        def check(reaction, user_reacted):
            return (
                user_reacted == ctx.author
                and str(reaction.emoji) == "🎮"
                and reaction.message.id == msg.id
            )

        try:
            await bot.wait_for("reaction_add", timeout=15.0, check=check)
            await play_slots()  # 🔁 ponowne zagranie
        except asyncio.TimeoutError:
            pass  # nie kliknięto na czas

    await play_slots()


bot.run(TOKEN)
