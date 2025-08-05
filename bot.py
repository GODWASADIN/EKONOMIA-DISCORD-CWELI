from economy import load_data, save_data, update_reputation, get_user_data
from discord.ext import commands, tasks
import random
import discord
import os
import time
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

cooldowns = {
    'work': {},
    'crime': {}
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

bot.run(os.getenv('DISCORD_TOKEN'))
