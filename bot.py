from economy import load_data, save_data, update_reputation, get_user_data
from discord.ext import commands, tasks
import random
import discord
import os
import time
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

cooldowns = {}

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
    cooldown_crime = 3600  # 1 godzina cooldownu

    if user_id in cooldowns and current_time - cooldowns[user_id] < cooldown_crime:
        remaining = int((cooldown_crime - (current_time - cooldowns[user_id])) / 60)
        return await ctx.send(f"⏳ Musisz poczekać jeszcze {remaining} min, by ponownie próbować przestępstwa!")

    user = get_user_data(user_id)
    
    # Sprawdzenie bonusu reputacji
    fail_chance = 0.2
    if user['reputation'] <= 21:
        fail_chance = 0.1

    update_reputation(user_id, -5)  # -5 reputacji za próbę przestępstwa

    roll = random.random()

    if roll > fail_chance:
        earnings = random.randint(50, 300)
        user['cash'] += earnings
        save_data(load_data())
        result_msg = f"✅ Udało się! Zarobiłeś **{earnings}$**!"
        color = discord.Color.green()
    else:
        loss = random.randint(200, 1000)
        user['cash'] -= loss
        if user['cash'] < 0:
            user['cash'] = 0
        save_data(load_data())
        result_msg = f"🚨 Wpadłeś! Straciłeś **{loss}$**!"
        color = discord.Color.red()

    cooldowns[user_id] = current_time

    embed = discord.Embed(
        title="🕵️ Próba przestępstwa!",
        description=f"{result_msg}\nReputacja: **-5 pkt**.",
        color=color
    )
    await ctx.send(embed=embed)

bot.run(os.getenv('DISCORD_TOKEN'))
