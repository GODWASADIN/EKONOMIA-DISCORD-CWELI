import discord
from discord.ext import commands
import os
import sqlite3
import time
import random

TOKEN = os.getenv("DISCORD_TOKEN")  # Pobierany z Railway Variables

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def init_db():
    conn = sqlite3.connect("economy.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            cash INTEGER DEFAULT 0,
            bank INTEGER DEFAULT 0,
            reputation INTEGER DEFAULT 0,
            last_work REAL DEFAULT 0,
            last_crime REAL DEFAULT 0,
            last_slut REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

@bot.event
async def on_ready():
    init_db()
    print(f"✅ Bot zalogowany jako {bot.user}")

@bot.command(name='work')
async def work(ctx):
    user_id = ctx.author.id
    conn = sqlite3.connect("economy.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    cursor.execute("SELECT cash, reputation, last_work FROM users WHERE user_id = ?", (user_id,))
    cash, rep, last_work = cursor.fetchone()

    now = time.time()
    cooldown = 30 * 60
    if now - last_work < cooldown:
        remaining = int((cooldown - (now - last_work)) / 60)
        embed = discord.Embed(
            title="⏳ Praca zablokowana",
            description=f"Poczekaj jeszcze `{remaining}` minut.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        conn.close()
        return

    base_earn = random.randint(20, 100)
    bonus = 0.2 if rep >= 50 else 0
    total_earn = int(base_earn * (1 + bonus))

cursor.execute("""
    UPDATE users
    SET cash = cash + ?, reputation = reputation + 6, last_work = ?
    WHERE user_id = ?
""", (total_earn, now, user_id))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title="💼 Pracowałeś!",
        description=f"Zarobiłeś `{total_earn}$` 💸 i zdobyłeś `+6` reputacji.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Bonus 20% aktywny!" if bonus else "Brak bonusa.")
    await ctx.send(embed=embed)

@bot.command(name='crime')
async def crime(ctx):
    user_id = ctx.author.id
    conn = sqlite3.connect("economy.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    cursor.execute("SELECT cash, reputation, last_crime FROM users WHERE user_id = ?", (user_id,))
    cash, rep, last_crime = cursor.fetchone()

    now = time.time()
    cooldown = 60 * 60
    if now - last_crime < cooldown:
        remaining = int((cooldown - (now - last_crime)) / 60)
        embed = discord.Embed(
            title="🚫 Przestępstwo zablokowane",
            description=f"Poczekaj jeszcze `{remaining}` minut.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        conn.close()
        return

    fail_chance = 0.25
    if rep <= 21:
        fail_chance = 0.10

    if random.random() > fail_chance:
        earned = random.randint(50, 300)
        new_cash = cash + earned
        result = f"✅ Udało Ci się! Ukradłeś `{earned}$` 💸"
        color = discord.Color.green()
    else:
        lost = random.randint(200, 1000)
        new_cash = max(cash - lost, 0)
        result = f"❌ Złapano Cię! Straciłeś `{lost}$` 💸"
        color = discord.Color.red()

    cursor.execute("""
        UPDATE users
        SET cash = ?, reputation = reputation - 5, last_crime = ?
        WHERE user_id = ?
    """, (new_cash, now, user_id))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title="🔫 Przestępstwo",
        description=result + "\n\nReputacja: `-5`",
        color=color
    )
    if rep <= 21:
        embed.set_footer(text="Bonus: tylko 10% szansy na porażkę")
    await ctx.send(embed=embed)

bot.run(TOKEN)
