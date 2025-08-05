from discord.ext import tasks
import datetime
import json
import random
import discord
from economy import load_data, save_data  # zakładamy, że masz te funkcje
from bot import bot  # zakładamy, że Twój bot jest nazwany "bot"

@tasks.loop(minutes=1)
async def check_lottery():
    now = datetime.datetime.now()
    if now.hour == 12 and now.minute == 0:
        try:
            with open("lottery.json", "r", encoding="utf-8") as f:
                lottery_data = json.load(f)
        except:
            return

        today = now.strftime("%Y-%m-%d")
        if lottery_data.get("last_draw") == today:
            return  # już losowano dzisiaj

        players = lottery_data.get("players", [])
        pot = lottery_data.get("pot", 0)

        if not players or pot == 0:
            return  # nic do losowania

        winner_id = random.choice(players)
        data = load_data()

        if winner_id in data:
            data[winner_id]["cash"] += pot
            save_data(data)

            channel = discord.utils.get(bot.get_all_channels(), name="ekonomia")
            if channel:
                await channel.send(f"🏆 **Loteria!** Wylosowano zwycięzcę!\n🎉 Gratulacje <@{winner_id}> – wygrywasz **{pot}$**!")

        # Reset
        lottery_data["pot"] = 0
        lottery_data["players"] = []
        lottery_data["last_draw"] = today
        with open("lottery.json", "w", encoding="utf-8") as f:
            json.dump(lottery_data, f, indent=4)