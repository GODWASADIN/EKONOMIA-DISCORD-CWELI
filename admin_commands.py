import discord
from discord.ext import commands
from economy import load_data, save_data

OWNER_ID = 987130076866949230  # Twój ID

def is_owner():
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_owner()
    async def addrep(self, ctx, member: discord.Member, amount: int = 1):
        data = load_data()
        user = data.setdefault(str(member.id), {"reputation": 0, "cash": 0, "bank": 0})
        user["reputation"] += amount
        save_data(data)
        await ctx.send(f"✅ Dodano {amount} punktów reputacji dla {member.mention}!")

    @commands.command()
    @is_owner()
    async def remrep(self, ctx, member: discord.Member, amount: int = 1):
        data = load_data()
        user = data.setdefault(str(member.id), {"reputation": 0, "cash": 0, "bank": 0})
        user["reputation"] -= amount
        save_data(data)
        await ctx.send(f"✅ Odjęto {amount} punktów reputacji od {member.mention}!")

    @commands.command()
    @is_owner()
    async def addcash(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Podaj kwotę większą niż 0.")

        data = load_data()
        user = data.setdefault(str(member.id), {"cash": 0, "bank": 0, "reputation": 0})
        user["cash"] += amount
        save_data(data)
        await ctx.send(f"✅ Dodano {amount}$ użytkownikowi {member.mention}!")

    @commands.command()
    @is_owner()
    async def removecash(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Podaj kwotę większą niż 0.")

        data = load_data()
        user = data.setdefault(str(member.id), {"cash": 0, "bank": 0, "reputation": 0})
        if user["cash"] < amount:
            return await ctx.send("❌ Użytkownik nie ma wystarczająco gotówki.")
        user["cash"] -= amount
        save_data(data)
        await ctx.send(f"✅ Odjęto {amount}$ użytkownikowi {member.mention}!")

    @commands.command()
    @is_owner()
    async def drawlottery(self, ctx):
        try:
            from lottery import run_lottery
        except ImportError:
            return await ctx.send("❌ Nie znaleziono modułu `lottery.py` z funkcją `run_lottery(bot)`.")

        await run_lottery(ctx.bot)
        await ctx.send("🎉 Loteria została ręcznie uruchomiona!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dodajbank(self, ctx, user: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Podaj prawidłową kwotę!")

        data = load_data()
        user_id = str(user.id)
        if user_id not in data:
            data[user_id] = {"cash": 0, "bank": 0, "reputation": 0}

        data[user_id]["bank"] = data[user_id].get("bank", 0) + amount
        save_data(data)

        await ctx.send(f"✅ Dodano {amount:,}$ do banku użytkownika {user.mention}!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def odejmijbank(self, ctx, user: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send("❌ Podaj prawidłową kwotę!")

        data = load_data()
        user_id = str(user.id)
        if user_id not in data:
            return await ctx.send("❌ Ten użytkownik nie ma żadnych danych bankowych!")

        current_bank = data[user_id].get("bank", 0)
        if current_bank < amount:
            return await ctx.send(f"❌ Użytkownik {user.mention} nie ma tyle pieniędzy w banku! (ma {current_bank:,}$)")

        data[user_id]["bank"] = current_bank - amount
        save_data(data)

        await ctx.send(f"✅ Odjęto {amount:,}$ z banku użytkownika {user.mention}!")
