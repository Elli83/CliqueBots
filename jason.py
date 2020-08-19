import discord
from discord.ext import commands

import random

from req import mongo, core, embeds


class Bot(core.Core):
    def __init__(self):
        super().__init__("Jason", [Events, Commands])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="balance", aliases=["bal", "money", "credits"])
    async def balance(self, ctx, user: discord.Member=None):
        if user:
            await ctx.send(ctx.author.mention, embed=discord.Embed(title="Balance",
                                                                   description=f"{user.mention} currently has {mongo.User(user).bal}cr"))
        else:
            await ctx.send(ctx.author.mention, embed=discord.Embed(title="Balance",
                                                                   description=f"You currently have {mongo.User(ctx.author).bal}cr"))

    @commands.command(name="daily")
    async def daily(self, ctx):
        user = mongo.User(ctx.author)

        if user.daily.ready:
            # Calculate how much the user should get
            amt = 100

            user.bal += amt   # Add the amount to the user balance
            user.daily.claim()   # Update the users last claimed time

            if user.daily.since < 108000:   # Check for streak
                user.daily.streak += 1
            else:
                user.daily.streak = 0

            embed = discord.Embed(title=f"You have claimed your daily {amt}cr!",
                                  description=f"{':white_medium_square:' * user.daily.streak}{':black_medium_square:' * (7 - user.daily.streak)}",   # Display streaks
                                  color=0x33ff33)

            if user.daily.streak >= 7:
                bonusamt = random.randint(400, 500)
                embed.description += f" **STREAK BONUS: {bonusamt}cr**"
                user.bal += bonusamt
                user.daily.streak = 0

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            m, s = divmod(int(user.daily.until), 60)
            h, m = divmod(m, 60)
            text = f"{f'{h}h ' if h > 0 else ''}" \
                   f"{f'{m}m ' if m > 0 else ''}" \
                   f"{f'{s}s' if h == 0 else ''}"
            await ctx.send(ctx.author.mention, embed=embeds.error(f"Your daily credits are not ready yet\n"
                                                                  f"Try again in **{text}**"))

    @commands.command(name="givemoney")
    async def give_money(self, ctx, user: discord.Member, amt: int):
        mongo.User(user).bal += amt



Bot()