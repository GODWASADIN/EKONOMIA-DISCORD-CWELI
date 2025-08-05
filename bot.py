from economy import load_data, save_data, update_reputation, get_user_data
from discord.ext import commands, tasks
import random
import discord
import os
import time
from tasks import check_lottery
from tasks import set_bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

cooldowns = {
    'work': {},
    'crime': {},
    'slut': {}
}


@bot.event
async def on_ready():
    set_bot(bot)  # przekaż bota do tasks
    print(f"✅ Zalogowano jako {bot.user}")
    
@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')

@bot.check
async def check_prison(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id)

    if user:
        rob_cd = user.get("rob_cd", 0)
        if time.time() < rob_cd:
            return ctx.command.name == "prison"  # pozwól tylko na !prison
    return True
    
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
    cooldown = 300  # 15 minut cooldownu

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
    cooldown = 600  # 1 godzina cooldownu

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
    cooldown = 600  # 45 minut

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

    # Wczytaj biznesy
    try:
        with open("businesses.json", "r", encoding="utf-8") as f:
            businesses = json.load(f)
    except FileNotFoundError:
        return await ctx.send("❌ Nie znaleziono pliku businesses.json.")

    if biznes not in businesses:
        return await ctx.send("❌ Nie ma takiego biznesu.")

    # Wczytaj dane użytkownika
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

    # 🔁 Dopasowanie nazwy biznesu niezależnie od wielkości liter
    user_biznesy_lower = {k.lower(): v for k, v in user['businesses'].items()}
    if user_biznesy_lower.get(biznes, 0) <= 0:
        return await ctx.send("❌ Nie posiadasz tego biznesu.")

    # Oryginalna nazwa z danych użytkownika (np. "Sklep" zamiast "sklep")
    real_name = next((k for k in user['businesses'].keys() if k.lower() == biznes), biznes)

    current_level = user['business_levels'].get(real_name, 1)
    if current_level >= 5:
        return await ctx.send("⚠️ Ten biznes jest już na maksymalnym poziomie (5).")

    base_price = businesses[biznes]['price']
    upgrade_cost = int(base_price * 0.5)

    if user['cash'] < upgrade_cost:
        return await ctx.send(f"❌ Ulepszenie kosztuje **{upgrade_cost}$**, a Ty masz tylko **{user['cash']}$**.")

    # Odejmij kasę
    user['cash'] -= upgrade_cost

    # Zwiększ poziom i zarobek
    user['business_levels'][real_name] = current_level + 1
    current_income = user['custom_income'].get(real_name, businesses[biznes]['income'])
    new_income = int(current_income * 1.2)
    user['custom_income'][real_name] = new_income

    save_data(data)

    await ctx.send(
        f"⬆️ Ulepszono **{real_name.title()}** do poziomu **{current_level + 1}**!\n"
        f"💰 Dochód zwiększony do **{new_income}$/h**\n"
        f"💸 Koszt ulepszenia: {upgrade_cost}$"
    )


import time

@bot.command()
async def pay(ctx, biznes: str, dni: int):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    if dni <= 0:
        return await ctx.send("❌ Liczba dni musi być większa niż 0.")

    biznes = biznes.lower()

    # Wczytaj dane biznesów
    try:
        with open("businesses.json", "r", encoding="utf-8") as f:
            businesses = json.load(f)
    except FileNotFoundError:
        return await ctx.send("❌ Nie znaleziono pliku businesses.json.")

    if biznes not in businesses:
        return await ctx.send("❌ Nie ma takiego biznesu.")

    # Dane gracza
    data = load_data()
    user_id = str(ctx.author.id)
    user = data.setdefault(user_id, {
        'cash': 0,
        'businesses': {},
        'paid_until': {}
    })

    user.setdefault('businesses', {})
    user.setdefault('paid_until', {})

    # Dopasuj nazwę biznesu (case-insensitive)
    user_biznesy_lower = {k.lower(): v for k, v in user['businesses'].items()}
    if user_biznesy_lower.get(biznes, 0) <= 0:
        return await ctx.send("❌ Nie posiadasz tego biznesu.")

    real_name = next((k for k in user['businesses'].keys() if k.lower() == biznes), biznes)

    # Dochód x ilość x 24h
    count = user['businesses'][real_name]
    base_income = businesses[biznes]['income']
    real_income = user.get('custom_income', {}).get(real_name, base_income)

    daily_cost = int(real_income * count * 0.1)
    total_cost = daily_cost * dni

    if user['cash'] < total_cost:
        return await ctx.send(f"❌ Koszt opłacenia **{real_name.title()}** na {dni} dni to **{total_cost}$**, a masz tylko **{user['cash']}$**.")

    user['cash'] -= total_cost

    # Aktualizacja opłaconego czasu
    current_time = int(time.time())
    existing = user['paid_until'].get(real_name, 0)
    new_paid_until = max(existing, current_time) + (dni * 86400)
    user['paid_until'][real_name] = new_paid_until

    save_data(data)

    dt = time.strftime("%Y-%m-%d %H:%M", time.localtime(new_paid_until))
    await ctx.send(
        f"✅ Opłacono **{real_name.title()}** na **{dni} dni** (do **{dt}**)!\n"
        f"💸 Koszt: {total_cost}$ (**{daily_cost}$/dzień x {dni})"
    )



import time

@bot.command()
async def collect(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    data = load_data()
    user = data.setdefault(user_id, {
        'cash': 0,
        'reputation': 0,
        'businesses': {},
        'paid_until': {},
        'custom_income': {},
        'business_levels': {},
        'last_collect': int(time.time())
    })

    now = int(time.time())
    last = user.get("last_collect", now)
    hours_passed = (now - last) // 3600

    if hours_passed < 1:
        return await ctx.send("⏳ Minęła mniej niż 1 godzina od ostatniego zbioru.")

    if not user.get("businesses"):
        return await ctx.send("❌ Nie posiadasz żadnych biznesów.")

    try:
        with open("businesses.json", "r", encoding="utf-8") as f:
            businesses = json.load(f)
    except:
        return await ctx.send("❌ Nie udało się wczytać danych biznesów.")

    total_income = 0
    rep_gain = 0
    lines = []

    for biz, amount in user['businesses'].items():
        biz_key = biz.lower()
        if biz_key not in businesses:
            continue

        info = businesses[biz_key]
        is_paid = user['paid_until'].get(biz, 0) >= now

        if not is_paid:
            lines.append(f"❌ **{biz.title()}**: nieopłacony – brak dochodu")
            continue

        base_income = user.get("custom_income", {}).get(biz, info['income'])
        hourly = base_income * amount
        earned = hourly * hours_passed
        total_income += earned

        if info['type'] == 'legal':
            rep_gain += 2

        lines.append(f"✅ **{biz.title()}** ×{amount} → +{earned}$")

    if total_income == 0:
        return await ctx.send("⚠️ Żaden biznes nie został opłacony. Użyj `!pay <biznes> <dni>`.")

    # Dodaj hajs i reputację
    user['cash'] += total_income
    user['reputation'] += rep_gain
    user['reputation'] = max(min(user['reputation'], 100), -100)
    user['last_collect'] = now

    save_data(data)

    embed = discord.Embed(
        title="📦 Dochód z Biznesów",
        description="\n".join(lines),
        color=discord.Color.green()
    )
    embed.add_field(name="💰 Suma zarobków", value=f"**{total_income}$**", inline=False)
    if rep_gain > 0:
        embed.add_field(name="⭐ Reputacja", value=f"+{rep_gain} pkt (za legalne biznesy)", inline=False)

    await ctx.send(embed=embed)

import time

@bot.command()
async def mojebiznesy(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id, None)

    if not user or not user.get("businesses"):
        return await ctx.send("❌ Nie posiadasz żadnych biznesów.")

    try:
        with open("businesses.json", "r", encoding="utf-8") as f:
            businesses = json.load(f)
    except:
        return await ctx.send("❌ Nie udało się wczytać danych biznesów.")

    lines = []
    now = int(time.time())

    for name, count in user['businesses'].items():
        base_income = businesses.get(name.lower(), {}).get('income', 0)
        level = user.get('business_levels', {}).get(name, 1)
        income = user.get('custom_income', {}).get(name, base_income)
        paid_until = user.get('paid_until', {}).get(name, 0)

        paid_status = "✅ do " + time.strftime("%Y-%m-%d %H:%M", time.localtime(paid_until)) if paid_until > now else "❌ nieopłacony"

        lines.append(
            f"**{name.title()}** ×{count} | 💼 Poziom: {level} | 💸 {income}$/h | {paid_status}"
        )

    embed = discord.Embed(
        title="📊 Twoje Biznesy",
        description="\n".join(lines),
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

@bot.command()
async def przedmioty(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id, {})
    inventory = user.get("items", {})

    if not inventory or sum(inventory.values()) == 0:
        return await ctx.send("🎒 Twój ekwipunek jest pusty.")

    # Wczytaj shop.json (opcjonalnie, dla opisów)
    try:
        with open("shop.json", "r", encoding="utf-8") as f:
            shop = json.load(f)
    except:
        shop = {}

    lines = []
    for item, qty in inventory.items():
        if qty <= 0:
            continue
        full_name = shop.get(item, {}).get("description", item)
        lines.append(f"🔹 **{item.title()}** — ilość: `{qty}`")

    embed = discord.Embed(
        title=f"🎒 Ekwipunek gracza {ctx.author.display_name}",
        description="\n".join(lines),
        color=discord.Color.purple()
    )

    await ctx.send(embed=embed)

import random

@bot.command(aliases=["bj"])
async def blackjack(ctx, bet: int):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id)

    if not user or user['cash'] < bet or bet <= 0:
        return await ctx.send("❌ Nie masz wystarczającej gotówki!")

    def draw_card():
        return random.choice(["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"])

    def calculate_hand(hand):
        total = 0
        aces = 0
        for card in hand:
            if card in ["J", "Q", "K"]:
                total += 10
            elif card == "A":
                aces += 1
                total += 11
            else:
                total += int(card)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    player_hand = [draw_card(), draw_card()]
    dealer_hand = [draw_card(), draw_card()]

    player_total = calculate_hand(player_hand)

    msg = await ctx.send(
        f"🃏 Twoje karty: {', '.join(player_hand)} ({player_total})\n"
        f"🎰 Krupier: {dealer_hand[0]}, ❓\n\n"
        f"🃏 = Dobierz kartę\n✅ = Zatrzymaj się"
    )
    await msg.add_reaction("🃏")
    await msg.add_reaction("✅")

    while True:
        def check(reaction, user_check):
            return (
                user_check == ctx.author and str(reaction.emoji) in ["🃏", "✅"] and reaction.message.id == msg.id
            )

        try:
            reaction, _ = await bot.wait_for("reaction_add", timeout=30.0, check=check)
        except:
            await ctx.send("⏱️ Czas minął!")
            return

        if reaction.emoji == "🃏":
            player_hand.append(draw_card())
            player_total = calculate_hand(player_hand)

            await msg.edit(
                content=f"🃏 Twoje karty: {', '.join(player_hand)} ({player_total})\n"
                        f"🎰 Krupier: {dealer_hand[0]}, ❓\n\n"
                        f"🃏 = Dobierz kartę\n✅ = Zatrzymaj się"
            )

            if player_total > 21:
                user['cash'] -= bet
                save_data(data)
                return await ctx.send(f"💥 Przegrałeś! Twoje karty: {', '.join(player_hand)} ({player_total})")
        elif reaction.emoji == "✅":
            break

    # Krupier dobiera do 17+
    while calculate_hand(dealer_hand) < 17:
        dealer_hand.append(draw_card())

    dealer_total = calculate_hand(dealer_hand)
    player_total = calculate_hand(player_hand)

    result = f"🃏 Twoje karty: {', '.join(player_hand)} ({player_total})\n" \
             f"🎰 Krupier: {', '.join(dealer_hand)} ({dealer_total})\n"

    if player_total > 21:
        user['cash'] -= bet
        result += "💥 Przegrałeś (Bust)!"
    elif dealer_total > 21 or player_total > dealer_total:
        win = int(bet * 2.5 if player_total == 21 and len(player_hand) == 2 else bet * 2)
        user['cash'] += win - bet
        result += f"🏆 Wygrałeś! Zgarnąłeś {win}$!"
    elif player_total == dealer_total:
        result += "🤝 Remis! Stawka zwrócona."
    else:
        user['cash'] -= bet
        result += "❌ Przegrałeś!"

    save_data(data)
    await ctx.send(result)

@bot.command()
async def slots(ctx, bet: int):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id)

    if not user or user['cash'] < bet or bet <= 0:
        return await ctx.send("❌ Nie masz wystarczającej gotówki!")

    symbols = ["🍒", "🍋", "🔔", "⭐", "🍇", "💎"]
    result = [random.choice(symbols) for _ in range(3)]

    await ctx.send(f"🎰 | {' | '.join(result)} |")

    if result.count(result[0]) == 3:
        win = bet * 5
        user['cash'] += win - bet
        msg = f"🎉 3 takie same symbole! Wygrałeś {win}$!"
    elif any(result.count(s) == 2 for s in result):
        win = bet * 2
        user['cash'] += win - bet
        msg = f"🎊 2 takie same symbole! Wygrałeś {win}$!"
    else:
        user['cash'] -= bet
        msg = "💸 Niestety, przegrywasz."

    save_data(data)
    await ctx.send(msg)

@bot.command()
async def coinflip(ctx, bet: int, wybor: str):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id)

    if not user or bet <= 0 or user['cash'] < bet:
        return await ctx.send("❌ Nie masz wystarczającej gotówki!")

    wybor = wybor.lower()
    if wybor not in ["orzeł", "reszka"]:
        return await ctx.send("❌ Wybierz: `orzeł` lub `reszka`.")

    wynik = random.choice(["orzeł", "reszka"])
    await ctx.send(f"🪙 Rzucam monetą... Wypadło: **{wynik.upper()}**!")

    if wybor == wynik:
        user['cash'] += bet  # zysk netto to +1x stawka
        await ctx.send(f"✅ Wygrałeś {bet * 2}$!")
    else:
        user['cash'] -= bet
        await ctx.send("❌ Przegrałeś!")

    save_data(data)


@bot.command()
async def duel(ctx, przeciwnik: discord.Member, stawka: int):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    if przeciwnik == ctx.author:
        return await ctx.send("❌ Nie możesz wyzwać samego siebie!")

    if stawka <= 0:
        return await ctx.send("❌ Stawka musi być większa niż 0!")

    data = load_data()
    user1 = data.get(str(ctx.author.id))
    user2 = data.get(str(przeciwnik.id))

    if not user1 or not user2:
        return await ctx.send("❌ Jeden z graczy nie ma danych w systemie.")

    if user1['cash'] < stawka or user2['cash'] < stawka:
        return await ctx.send("❌ Obaj gracze muszą mieć wystarczającą gotówkę!")

    # Zapytanie o akceptację
    zaproszenie = await ctx.send(
        f"⚔️ {przeciwnik.mention}, zostałeś wyzwany do pojedynku o {stawka}$!\n"
        f"Kliknij ✅ aby zaakceptować (30 sekund)."
    )
    await zaproszenie.add_reaction("✅")

    def check(reaction, user_check):
        return (
            user_check == przeciwnik and
            str(reaction.emoji) == "✅" and
            reaction.message.id == zaproszenie.id
        )

    try:
        await bot.wait_for("reaction_add", timeout=30.0, check=check)
    except:
        return await ctx.send("⌛ Pojedynek nie został zaakceptowany.")

    # Losowanie zwycięzcy
    winner, loser = (ctx.author, przeciwnik) if random.choice([True, False]) else (przeciwnik, ctx.author)

    # Przetwarzanie kasy
    user1['cash'] -= stawka
    user2['cash'] -= stawka
    data[str(winner.id)]['cash'] += stawka * 2

    save_data(data)

    await ctx.send(
        f"🏆 {winner.mention} wygrał pojedynek i zgarnia **{stawka * 2}$**!\n"
        f"💀 {loser.mention} przegrywa stawkę."
    )

@bot.command()
async def lottery(ctx):
    if ctx.channel.name != 'ekonomia':
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id)

    if not user or user['cash'] < 100:
        return await ctx.send("❌ Potrzebujesz 100$, by kupić bilet!")

    # Wczytaj loterię
    try:
        with open("lottery.json", "r", encoding="utf-8") as f:
            lottery_data = json.load(f)
    except:
        lottery_data = {"pot": 0, "players": [], "last_draw": ""}

    if user_id in lottery_data["players"]:
        return await ctx.send("🎟️ Już kupiłeś bilet na dzisiejsze losowanie!")

    user['cash'] -= 100
    lottery_data["pot"] += 100
    lottery_data["players"].append(user_id)

    save_data(data)
    with open("lottery.json", "w", encoding="utf-8") as f:
        json.dump(lottery_data, f, indent=4)

    await ctx.send("🎟️ Bilet kupiony! Powodzenia w losowaniu o 12:00!")

@bot.command()
async def rep(ctx, member: discord.Member = None):
    if ctx.channel.name != "ekonomia":
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    member = member or ctx.author
    user_id = str(member.id)

    data = load_data()
    user = data.get(user_id)

    if not user:
        return await ctx.send("❌ Ten użytkownik nie ma danych w systemie.")

    rep = user.get("reputation", 0)
    await ctx.send(f"⭐ Reputacja użytkownika {member.mention} wynosi: **{rep} pkt**")

import datetime

# DODAJ do load_data(): user.setdefault("redeem_history", {})
# Jeśli jeszcze tego nie masz, by kontrolować dzienne użycia

@bot.command()
async def redeem(ctx, kwota: int):
    if ctx.channel.name != "ekonomia":
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    if kwota <= 0:
        return await ctx.send("❌ Podaj poprawną kwotę (minimum 1000).")

    user_id = str(ctx.author.id)
    data = load_data()
    user = data.get(user_id)

    if not user or user['cash'] < kwota:
        return await ctx.send("❌ Nie masz wystarczającej gotówki.")

    if kwota % 1000 != 0:
        return await ctx.send("❌ Kwota musi być wielokrotnością **1000$**.")

    # Sprawdź dzienny limit
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    redeem_history = user.setdefault("redeem_history", {})
    used_today = redeem_history.get(today, 0)

    max_points_today = 20
    max_kwota_today = max_points_today * 1000
    if used_today + kwota > max_kwota_today:
        return await ctx.send(f"❌ Możesz odkupić reputację tylko do **{max_points_today} pkt** dziennie (**max {max_kwota_today}$**)")

    # Oblicz ile punktów dać
    punkty = int((kwota / 1000) * 10)

    # Odejmij gotówkę, dodaj reputację
    user['cash'] -= kwota
    user['reputation'] += punkty
    if user['reputation'] > 100:
        user['reputation'] = 100  # maksymalnie 100

    redeem_history[today] = used_today + kwota
    save_data(data)

    await ctx.send(f"✅ Wykupiono reputację za {kwota}$! Otrzymujesz **+{punkty} pkt**, aktualna reputacja: **{user['reputation']} pkt**.")

@bot.command()
async def btop(ctx):
    if ctx.channel.name != "ekonomia":
        return await ctx.send("❌ Komenda dostępna tylko na kanale #ekonomia!")

    data = load_data()

    try:
        with open("businesses.json", "r", encoding="utf-8") as f:
            biz_db = json.load(f)
    except:
        return await ctx.send("❌ Nie udało się załadować biznesów.")

    ranking = []

    for user_id, user_data in data.items():
        total_value = 0
        businesses = user_data.get("businesses", {})
        levels = user_data.get("business_levels", {})

        for biz, qty in businesses.items():
            base_price = biz_db.get(biz, {}).get("price", 0)
            level = levels.get(biz, 1)
            for _ in range(qty):
                upgraded_price = base_price + int(base_price * 0.5 * (level - 1))  # wzrost ceny z poziomem
                total_value += upgraded_price

        if total_value > 0:
            ranking.append((int(user_id), total_value))

    if not ranking:
        return await ctx.send("❌ Nikt nie posiada biznesów.")

    ranking.sort(key=lambda x: x[1], reverse=True)
    top = ranking[:10]

    embed = discord.Embed(title="🏢 TOP 10 najbogatszych według wartości biznesów", color=discord.Color.gold())
    for i, (uid, value) in enumerate(top, start=1):
        member = ctx.guild.get_member(uid)
        name = member.display_name if member else f"<@{uid}>"
        embed.add_field(name=f"{i}. {name}", value=f"Wartość: 💸 {value:,}$", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def top(ctx):
    if ctx.channel.name != "ekonomia":
        return await ctx.send("❌ Komenda dostępna tylko na kanale #ekonomia!")

    data = load_data()

    ranking = []

    for user_id, user_data in data.items():
        total = user_data.get("cash", 0) + user_data.get("bank", 0)
        reputation = user_data.get("reputation", 0)
        if total > 0:
            ranking.append((int(user_id), total, reputation))

    if not ranking:
        return await ctx.send("❌ Brak danych do wyświetlenia.")

    ranking.sort(key=lambda x: x[1], reverse=True)
    top = ranking[:10]

    embed = discord.Embed(title="💰 TOP 10 najbogatszych graczy", color=discord.Color.green())
    for i, (uid, total_money, rep) in enumerate(top, start=1):
        member = ctx.guild.get_member(uid)
        name = member.display_name if member else f"<@{uid}>"
        embed.add_field(
            name=f"{i}. {name}",
            value=f"💸 {total_money:,}$ • ⭐ {rep} pkt",
            inline=False
        )

    await ctx.send(embed=embed)

import random
import time

@bot.command()
async def rob(ctx, member: discord.Member):
    if ctx.channel.name != "ekonomia":
        return await ctx.send("❌ Komenda działa tylko na kanale #ekonomia!")

    if member == ctx.author:
        return await ctx.send("❌ Nie możesz okradać samego siebie!")

    user_id = str(ctx.author.id)
    target_id = str(member.id)

    data = load_data()
    user = data.get(user_id)
    target = data.get(target_id)

    if not user or not target:
        return await ctx.send("❌ Obaj użytkownicy muszą mieć dane w systemie.")

    if target["cash"] < 100:
        return await ctx.send("❌ Ten gracz nie ma wystarczającej gotówki, by go okraść!")

    now = time.time()
    cooldown = user.get("rob_cd", 0)
    if now < cooldown:
        remaining = int((cooldown - now) / 60)
        return await ctx.send(f"⏳ Musisz poczekać **{remaining} minut** przed kolejną próbą.")

    # Obniżenie reputacji za próbę
    user["reputation"] = user.get("reputation", 0) - 10

    rep = user.get("reputation", 0)
    chance = 0.6 if rep > -75 else 0.4

    if random.random() < chance:
        # SUKCES
        stolen_percent = random.uniform(0.1, 0.8)
        stolen_amount = int(target["cash"] * stolen_percent)
        stolen_amount = max(50, min(stolen_amount, target["cash"]))

        user["cash"] += stolen_amount
        target["cash"] -= stolen_amount
        user["rob_cd"] = now + 900  # 15 minut cooldown

        save_data(data)

        embed = discord.Embed(
            title="💸 Udana kradzież!",
            description=f"Ukradłeś **{stolen_amount}$** od {member.mention}!"

                        f"📉 Reputacja: `-10` (obecnie: {user['reputation']})",
            color=discord.Color.green()
        )
        return await ctx.send(embed=embed)

    else:
        # PORAŻKA = WIĘZIENIE
        fine = random.randint(300, 900)
        user["cash"] = max(0, user["cash"] - fine)
        user["reputation"] -= 5
        user["rob_cd"] = now + 900  # 15 minut więzienia

        save_data(data)

        embed = discord.Embed(
            title="🚔 Zostałeś złapany!",
            description=(
                f"❌ Próba okradzenia {member.mention} się **nie powiodła**.
"
                f"💸 Grzywna: `{fine}$`
"
                f"📉 Reputacja: `-15 pkt` (obecnie: {user['reputation']})
"
                f"⛓️ Trafiasz do **więzienia na 15 minut!**"
            ),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

        # Dodaj rolę więźnia jeśli istnieje
        prison_role = discord.utils.get(ctx.guild.roles, name="🔒 Więzień")
        if prison_role:
            await ctx.author.add_roles(prison_role)
            await asyncio.sleep(900)  # 15 minut
            await ctx.author.remove_roles(prison_role)

@bot.command()
async def prison(ctx, member: discord.Member = None):
    if ctx.channel.name != "ekonomia":
        return await ctx.send("❌ Komenda dostępna tylko na kanale #ekonomia!")

    member = member or ctx.author
    user_id = str(member.id)

    data = load_data()
    user = data.get(user_id)

    if not user:
        return await ctx.send("❌ Ten gracz nie istnieje w systemie.")

    rob_cd = user.get("rob_cd", 0)
    now = time.time()

    if rob_cd > now:
        remaining = int(rob_cd - now)
        minutes = remaining // 60
        seconds = remaining % 60
        await ctx.send(f"⛓️ {member.display_name} siedzi w więzieniu jeszcze przez **{minutes}m {seconds}s**.")
    else:
        await ctx.send(f"✅ {member.display_name} jest wolny.")
        
bot.run(os.getenv('DISCORD_TOKEN'))
