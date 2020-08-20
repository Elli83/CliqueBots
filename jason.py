import discord
from discord.ext import commands, menus

import random
import pymongo
import math
import json

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
            if ctx.author in ctx.guild.premium_subscribers:
                amt += 50
            if mongo.User(ctx.author).isBirthday():
                amt *= 2

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

        if await embeds.confirm_transaction(ctx):
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

                try:
                    pos = [u['ID'] for u in top].index(str(ctx.author.id)) + 1
                except:
                    pos = "N/A"

                embed.set_footer(text=f"Page {menu.current_page+1} | Your position: {pos}")
                return embed

        top = list(mongo.db['Users'].find({"Balance": {"$gte": 1}}).sort("Balance", -1))
        pages = menus.MenuPages(source=Leaderboard(top))
        pages.remove_button('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f')
        pages.remove_button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f')
        await pages.start(ctx)

    @commands.command(name="sub", aliases=["subscribe", "feed", "feeds"])
    async def sub(self, ctx):
        feeds = json.load(open("config/feeds.json"))

        class FeedsMenu(menus.Menu):
            def __init__(self):
                super().__init__()

                self.embed = discord.Embed(title="Feeds")
                for i, f in enumerate(feeds):
                    self.embed.add_field(name=f"{i + 1}. {f['Name']}", value=f['Description'])
                    button = menus.Button(f'{i+1}\N{COMBINING ENCLOSING KEYCAP}', self.button)

                    self.add_button(button)

            async def send_initial_message(self, ctx, channel):
                return await ctx.send(ctx.author.mention, embed=self.embed)

            async def button(self, payload):
                res = int(payload.emoji.name[0])
                feed = feeds[res-1]
                role = ctx.guild.get_role(feed['RoleID'])

                if role in ctx.author.roles:
                    await self.message.clear_reactions()

                    await self.message.edit(embed=embeds.error(f"You are already subscribed to `{feed['Name']}`\n"
                                                               f"Would you like to unsubscribe?"))

                    class UnsubConfirm(menus.Menu):
                        def __init__(self, message):
                            super().__init__()
                            self.message = message

                        @menus.button('\N{THUMBS UP SIGN}')
                        async def yes(self, payload):
                            await self.message.clear_reactions()
                            await ctx.author.remove_roles(role)
                            await self.message.edit(embed=embeds.success(f"You have unsubscribed from `{feed['Name']}`"))

                        @menus.button('\N{THUMBS DOWN SIGN}')
                        async def no(self, payload):
                            await self.message.delete()

                    await UnsubConfirm(self.message).start(ctx)
                else:
                    await ctx.author.add_roles(role)
                    await self.message.clear_reactions()
                    await self.message.edit(embed=embeds.success(f"You have subscribed to `{feed['Name']}`"))

        await FeedsMenu().start(ctx)

    @commands.command(name="givemoney")
    async def give_money(self, ctx, user: discord.Member, amt: int):
        mongo.User(user).bal += amt



Bot()