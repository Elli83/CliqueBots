import discord
from discord.ext import commands, menus

import random
import pymongo
import math

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

    @commands.command()
    async def donate(self, ctx, user: discord.Member, amt: int):
        if amt < 1 or user == ctx.author:
            raise commands.UserInputError

        if await embeds.ConfirmTransaction().prompt(ctx):
            await ctx.message.add_reaction('👍')
            mongo.User(ctx.author).bal -= amt
            mongo.User(user).bal += amt

    @commands.command(name="top", aliases=["leaderboard"])
    async def top(self, ctx):
        """embed = discord.Embed(title="Leaderboard",
                              description="What leaderboard would you like to view?\n"
                                          "🇨 Credits\n"
                                          "🇱 Level")
        await ctx.send(ctx.author.mention, embed=embed)"""

        class Leaderboard(menus.ListPageSource):
            def __init__(self, data, per_page=10):
                super().__init__(data, per_page=per_page)
                self.data = data

            async def format_page(self, menu, entries):
                offset = menu.current_page * self.per_page
                embed = discord.Embed(title=f"Leaderboard - Credits",
                                      color=0x33ff33)
                embed.description = '\n'.join(f"` {'{:02d}'.format(i+1)} ` **|** <@{v['ID']}> - {v['Balance']}cr" for i, v in enumerate(entries, start=offset))
                embed.set_footer(text=f"Page {menu.current_page+1} | Your position: {pos}")
                return embed

        top = list(mongo.db['Users'].find({"Balance": {"$gte": 1}}).sort("Balance", -1))
        try:
            pos = [u['ID'] for u in top].index(str(ctx.author.id)) + 1
        except:
            pos = "N/A"
        pages = menus.MenuPages(source=Leaderboard(top))
        pages.remove_button('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f')
        pages.remove_button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f')
        await pages.start(ctx)

    @commands.command(name="givemoney")
    async def give_money(self, ctx, user: discord.Member, amt: int):
        mongo.User(user).bal += amt



Bot()