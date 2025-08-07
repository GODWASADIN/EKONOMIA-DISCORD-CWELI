import json
import random
import discord
from discord.ext import tasks

LOTTERY_FILE = "lottery.json"
LOTTERY_CHANNEL_ID = 123456789012345678  # <- wpisz tutaj ID kanału do ogłaszania zwycięzcy

def add_lottery_entry(user_id):
    try:
        with open(LOTTERY_FILE, "r") as f:
            entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        entries = []
    entries.append(user_id)
    with open(LOTTERY_FILE, "w") as f:
        json.dump(entries, f)

def clear_lottery_entries():
    with open(LOTTERY_FILE, "w") as f:
        json.dump([], f)

def get_lottery_entries():
    try:
        with open(LOTTERY_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Komenda do kupna losu możesz dać np. do osobnego coga/komendy:
async def buy_ticket(ctx):
    user_id = ctx.author.id
    entries = get_lottery_entries()
    if user_id in entries:
        await ctx.send("❌ Już masz los na dzisiaj!")
        return
    add_lottery_entry(user_id)
    await ctx.send("✅ Kupiłeś los! Powodzenia!")

# Codzienne losowanie
async def run_lottery(bot):
    entries = get_lottery_entries()
    if not entries:
        print("Brak uczestników loterii.")
        return
    winner_id = random.choice(entries)
    winner = None

    # Szukamy zwycięzcy na wszystkich serwerach bota (możesz ograniczyć do jednego serwera)
    for guild in bot.guilds:
        member = guild.get_member(winner_id)
        if member:
            winner = member
            break

    # Kanał do ogłoszenia
    channel = bot.get_channel(LOTTERY_CHANNEL_ID)
    if channel and winner:
        await channel.send(f"🎉 LOTERIA! Gratulacje {winner.mention}, wygrałeś dzisiejszą loterię!")
    elif channel:
        await channel.send("Loteria odbyła się, ale nie znaleziono zwycięzcy na serwerze.")
    else:
        print("Nie znaleziono kanału do ogłoszenia loterii.")

    clear_lottery_entries()
