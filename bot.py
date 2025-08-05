from economy import load_data, save_data, update_reputation, get_user_data
from discord.ext import commands, tasks
import random
import discord
import os
import time
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

cooldowns = {
    'work': {},
    'crime': {},
    'slut': {}
}

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')

@bot.command()
async def bal(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("Komenda działa tylko na kanale #ekonomia!")

    user = get_user_data(ctx.author.id)
    embed = discord.Embed(title=f"Stan {ctx.author.name}", color=discord.Color.green())
    embed.add_field(name="💵 Gotówka", value=f"{user['cash']} $")
    embed.add_field(name="🏦 Bank", value=f"{user['bank']} $")
    embed.add_field(name="⭐ Reputacja", value=f"{user['reputation']} pkt")
    await ctx.send(embed=embed)

@bot.command()
async def work(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    current_time = time.time()
    cooldown = 1800  # 30 minut cooldownu

    # sprawdzenie cooldownu
    if user_id in cooldowns and current_time - cooldowns[user_id] < cooldown:
        remaining = int((cooldown - (current_time - cooldowns[user_id])) / 60)
        return await ctx.send(f"⏳ Musisz poczekać jeszcze {remaining} min, by ponownie pracować!")

    earnings = random.randint(20, 100)

    # Sprawdzenie bonusu reputacji
    user = get_user_data(user_id)
    if user['reputation'] >= 50:
        earnings = int(earnings * 1.2)
        bonus_msg = " (+20% bonus za reputację!)"
    else:
        bonus_msg = ""

    data = load_data()
    user_data = data.setdefault(user_id, {'cash': 0, 'bank': 0, 'reputation': 0})
    user_data['cash'] += earnings
    save_data(data)

    update_reputation(user_id, 6)  # +6 reputacji za pracę
    cooldowns[user_id] = current_time  # ustawienie cooldownu

    embed = discord.Embed(
        title="💼 Praca zakończona!",
        description=f"Zarobiłeś **{earnings}$**{bonus_msg}\nTwoja reputacja wzrosła o **+6 pkt**!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@bot.command()
async def crime(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    current_time = time.time()
    cooldown = 3600  # 1 godzina cooldownu

    # cooldown tylko dla !crime
    if user_id in cooldowns['crime'] and current_time - cooldowns['crime'][user_id] < cooldown:
        remaining = int((cooldown - (current_time - cooldowns['crime'][user_id])) / 60)
        return await ctx.send(f"⏳ Musisz poczekać jeszcze {remaining} min, by ponownie próbować przestępstwa!")

    # Pobranie i przygotowanie danych użytkownika
    data = load_data()
    user = data.setdefault(user_id, {'cash': 0, 'bank': 0, 'reputation': 0})

    chance = random.randint(1, 100)
    success_chance = 75
    fail_chance = 20

    # Bonus: mniejsza szansa na porażkę przy reputacji ≤ 21
    if user['reputation'] <= 21:
        fail_chance = 10

    # Wynik akcji
    if chance <= success_chance:
        earnings = random.randint(50, 300)
        user['cash'] += earnings
        result_msg = f"🕶️ Udało się! Zarobiłeś **{earnings}$**!"
    elif chance <= success_chance + fail_chance:
        penalty = random.randint(200, 1000)
        penalty = min(penalty, user['cash'])  # nie możesz stracić więcej niż masz
        user['cash'] -= penalty
        result_msg = f"🚔 Zostałeś złapany! Tracisz **{penalty}$**!"
    else:
        result_msg = "😐 Nic się nie wydarzyło... nie zarobiłeś ani nie straciłeś."

    # Zmiana reputacji
    user['reputation'] -= 5
    user['reputation'] = max(min(user['reputation'], 100), -100)

    # Zapis danych i cooldownu
    cooldowns['crime'][user_id] = current_time
    save_data(data)

    # Odpowiedź
    embed = discord.Embed(
        title="🔪 Próba przestępstwa",
        description=f"{result_msg}\nTwoja reputacja spadła o **-5 pkt**!",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)


@bot.command()
async def slut(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    current_time = time.time()
    cooldown = 2700  # 45 minut

    if user_id in cooldowns['slut'] and current_time - cooldowns['slut'][user_id] < cooldown:
        remaining = int((cooldown - (current_time - cooldowns['slut'][user_id])) / 60)
        return await ctx.send(f"⏳ Musisz poczekać jeszcze {remaining} min, by ponownie wykonać brudną robotę!")

    data = load_data()
    user = data.setdefault(user_id, {'cash': 0, 'bank': 0, 'reputation': 0})

    chance = random.randint(1, 100)

    if chance <= 80:  # 80% sukcesu
        earnings = random.randint(50, 200)
        user['cash'] += earnings
        result_msg = f"💋 Zarobiłeś **{earnings}$** wykonując brudną robotę."
    else:
        loss = random.randint(50, 100)
        loss = min(loss, user['cash'])
        user['cash'] -= loss
        result_msg = f"💔 Nie udało się! Straciłeś **{loss}$**."

    # -2 reputacji
    user['reputation'] -= 2
    user['reputation'] = max(min(user['reputation'], 100), -100)

    cooldowns['slut'][user_id] = current_time
    save_data(data)

    embed = discord.Embed(
        title="🔞 Brudna robota",
        description=f"{result_msg}\nTwoja reputacja spadła o **-2 pkt**.",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

@bot.command()
async def deposit(ctx, amount: str):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("Komenda działa tylko na kanale #ekonomia!")

    data = load_data()
    user_id = str(ctx.author.id)
    user = data.setdefault(user_id, {'cash': 0, 'bank': 0, 'reputation': 0})

    if amount.lower() == "all":
        amount = user['cash']
    elif amount.isdigit():
        amount = int(amount)
    else:
        return await ctx.send("❌ Podaj liczbę lub użyj `all`.")

    if amount <= 0 or amount > user['cash']:
        return await ctx.send("❌ Nie masz tyle gotówki, by to wpłacić.")

    user['cash'] -= amount
    user['bank'] += amount
    save_data(data)

    await ctx.send(f"🏦 Wpłacono **{amount}$** do banku!")


@bot.command()
async def withdraw(ctx, amount: str):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("Komenda działa tylko na kanale #ekonomia!")

    data = load_data()
    user_id = str(ctx.author.id)
    user = data.setdefault(user_id, {'cash': 0, 'bank': 0, 'reputation': 0})

    if amount.lower() == "all":
        amount = user['bank']
    elif amount.isdigit():
        amount = int(amount)
    else:
        return await ctx.send("❌ Podaj liczbę lub użyj `all`.")

    if amount <= 0 or amount > user['bank']:
        return await ctx.send("❌ Nie masz tyle pieniędzy w banku.")

    user['bank'] -= amount
    user['cash'] += amount
    save_data(data)

    await ctx.send(f"💸 Wypłacono **{amount}$** z banku!")


import json

@bot.command()
async def buy(ctx, nazwa: str):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    nazwa = nazwa.lower()

    # Wczytanie danych użytkownika
    data = load_data()
    user_id = str(ctx.author.id)
    user = data.setdefault(user_id, {
        'cash': 0,
        'bank': 0,
        'reputation': 0,
        'businesses': {},
        'items': {}
    })
    user.setdefault('businesses', {})
    user.setdefault('items', {})

    # Spróbuj załadować biznesy
    try:
        with open("businesses.json", "r", encoding="utf-8") as f:
            businesses = json.load(f)
    except:
        businesses = {}

    # Spróbuj załadować sklep
    try:
        with open("shop.json", "r", encoding="utf-8") as f:
            shop = json.load(f)
    except:
        shop = {}

    # 🏢 Kup biznes
    if nazwa in businesses:
        b = businesses[nazwa]
        cena = b['price']
        if user['reputation'] <= -50:
            cena = int(cena * 1.1)

        if user['cash'] < cena:
            return await ctx.send(f"❌ Potrzebujesz **{cena}$**, a masz tylko **{user['cash']}$**.")

        user['cash'] -= cena
        user['businesses'][nazwa] = user['businesses'].get(nazwa, 0) + 1

        if b['type'] in ['illegal', 'booster_only']:
            user['reputation'] -= 5
            rep_info = "-5 reputacji"
        else:
            rep_info = "brak zmian"

        user['reputation'] = max(min(user['reputation'], 100), -100)
        save_data(data)

        return await ctx.send(
            f"✅ Kupiłeś **{nazwa.title()}** za **{cena}$**.\n📈 Reputacja: {rep_info} → teraz **{user['reputation']} pkt**."
        )

    # 🛍️ Kup przedmiot ze sklepu
    elif nazwa in shop:
        item = shop[nazwa]
        cena = item['price']

        if user['cash'] < cena:
            return await ctx.send(f"❌ Przedmiot kosztuje **{cena}$**, a Ty masz **{user['cash']}$**.")

        user['cash'] -= cena
        user['items'][nazwa] = user['items'].get(nazwa, 0) + 1
        save_data(data)

        return await ctx.send(
            f"🛍️ Kupiłeś przedmiot **{nazwa.title()}** za **{cena}$**!\nOpis: {item['description']}"
        )

    else:
        return await ctx.send("❌ Nie znaleziono takiego biznesu ani przedmiotu.")

OWNER_ID = 987130076866949230  # ← upewnij się, że nie ma żadnego wcięcia

@bot.command()
async def dodajkase(ctx, member: discord.Member, kwota: int):
    if ctx.author.id != OWNER_ID:
        return await ctx.send("❌ Tylko właściciel bota może używać tej komendy.")

    if kwota <= 0:
        return await ctx.send("❌ Podaj poprawną kwotę większą niż 0.")

    data = load_data()
    user = data.setdefault(str(member.id), {
        'cash': 0,
        'bank': 0,
        'reputation': 0,
        'businesses': {}
    })

    user['cash'] += kwota
    save_data(data)

    await ctx.send(f"✅ Dodano {kwota}$ użytkownikowi {member.mention}!")


@bot.command()
async def shop(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    try:
        with open("shop.json", "r", encoding="utf-8") as f:
            shop_data = json.load(f)
    except FileNotFoundError:
        return await ctx.send("❌ Nie znaleziono pliku `shop.json`.")

    embed = discord.Embed(
        title="🛒 Sklep - Przedmioty",
        description="Dostępne przedmioty do kupienia:\n\nUżyj `!buy <nazwa>` do zakupu.",
        color=discord.Color.orange()
    )

    for name, item in shop_data.items():
        embed.add_field(
            name=f"{name.title()}  – 💰 {item['price']}$",
            value=f"{item['description']}",
            inline=False
        )

    embed.set_footer(text="Użyj !buy <nazwa> do zakupu")
    await ctx.send(embed=embed)


import random

def use_ticket(ctx, user_id, item_key, min_reward, max_reward, display_name):
    data = load_data()
    user = data.get(str(user_id), None)
    if not user:
        return None, f"❌ Nie znaleziono danych użytkownika."

    user.setdefault('items', {})
    if user['items'].get(item_key, 0) <= 0:
        return None, f"❌ Nie masz żadnej **{display_name}**."

    # Zużycie itemu
    user['items'][item_key] -= 1
    reward = random.randint(min_reward, max_reward)
    user['cash'] += reward
    save_data(data)

    embed = discord.Embed(
        title=f"🎉 {display_name}!",
        description=f"Wygrałeś **{reward}$** 💰",
        color=discord.Color.green()
    )
    embed.set_footer(text="Zdrap więcej, by wygrać więcej!")
    return embed, None

@bot.command()
async def zdrapka(ctx):
    embed, error = use_ticket(ctx, ctx.author.id, "zdrapka", 100, 1000, "Zwykła Zdrapka")
    await ctx.send(embed=embed) if embed else await ctx.send(error)

@bot.command()
async def zdrapkag(ctx):
    embed, error = use_ticket(ctx, ctx.author.id, "zdrapkagold", 1000, 5000, "Złota Zdrapka")
    await ctx.send(embed=embed) if embed else await ctx.send(error)

@bot.command()
async def zdrapkap(ctx):
    embed, error = use_ticket(ctx, ctx.author.id, "zdrapkapremium", 5000, 10000, "Premium Zdrapka")
    await ctx.send(embed=embed) if embed else await ctx.send(error)


@bot.command()
async def invest(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    try:
        with open("businesses.json", "r", encoding="utf-8") as f:
            businesses = json.load(f)
    except FileNotFoundError:
        return await ctx.send("❌ Nie znaleziono pliku `businesses.json`.")

    embed = discord.Embed(
        title="💼 Dostępne Biznesy – Inwestycje",
        description="Kup biznes komendą `!buy <nazwa>`",
        color=discord.Color.blue()
    )

    # Podzielone według typu
    legal = ""
    illegal = ""
    booster = ""

    for name, b in businesses.items():
        line = f"**{name.title()}** – 💸 {b['price']:,}$, 💰 {b['income']}/h"
        if b['type'] == "legal":
            line += f", 🟢 +{b['rep_on_collect']} rep / zbieranie\n"
            legal += line
        elif b['type'] == "illegal":
            line += f", 🔴 {b['rep_on_collect']} rep / zakup\n"
            illegal += line
        elif b['type'] == "booster_only":
            line += f", 🟣 {b['rep_on_collect']} rep / zakup\n"
            booster += line

    if legal:
        embed.add_field(name="🟢 Legalne Biznesy", value=legal, inline=False)
    if illegal:
        embed.add_field(name="🔴 Nielegalne Biznesy", value=illegal, inline=False)
    if booster:
        embed.add_field(name="🟣 Biznesy dla Nitro Boosterów", value=booster, inline=False)

    embed.set_footer(text="Bonus: +10% dochodu przy reputacji ≥ 50 • Kara: +10% ceny przy reputacji ≤ -50")

    await ctx.send(embed=embed)


@bot.command()
async def upgrade(ctx, biznes: str):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    biznes = biznes.lower()
    try:
        with open("businesses.json", "r", encoding="utf-8") as f:
            businesses = json.load(f)
    except FileNotFoundError:
        return await ctx.send("❌ Nie znaleziono pliku businesses.json.")

    if biznes not in businesses:
        return await ctx.send("❌ Nie ma takiego biznesu.")

    data = load_data()
    user_id = str(ctx.author.id)
    user = data.setdefault(user_id, {
        'cash': 0,
        'bank': 0,
        'reputation': 0,
        'businesses': {},
        'business_levels': {},
        'custom_income': {}
    })

    user.setdefault('businesses', {})
    user.setdefault('business_levels', {})
    user.setdefault('custom_income', {})

    if user['businesses'].get(biznes, 0) <= 0:
        return await ctx.send("❌ Nie posiadasz tego biznesu.")

    current_level = user['business_levels'].get(biznes, 1)
    if current_level >= 5:
        return await ctx.send("⚠️ Ten biznes jest już na maksymalnym poziomie (5).")

    base_price = businesses[biznes]['price']
    upgrade_cost = int(base_price * 0.5)

    if user['cash'] < upgrade_cost:
        return await ctx.send(f"❌ Ulepszenie kosztuje **{upgrade_cost}$**, a Ty masz tylko **{user['cash']}$**.")

    # Odejmij kasę
    user['cash'] -= upgrade_cost

    # Zwiększ poziom
    user['business_levels'][biznes] = current_level + 1

    # Zwiększ zarobki o +20%
    current_income = user['custom_income'].get(biznes, businesses[biznes]['income'])
    new_income = int(current_income * 1.2)
    user['custom_income'][biznes] = new_income

    save_data(data)

    await ctx.send(
        f"⬆️ Ulepszono **{biznes.title()}** do poziomu **{current_level + 1}**!\n"
        f"💰 Dochód zwiększony do **{new_income}$/h**\n"
        f"💸 Koszt ulepszenia: {upgrade_cost}$"
    )

bot.run(os.getenv('DISCORD_TOKEN'))
