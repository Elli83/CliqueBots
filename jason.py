import discord
from discord.ext import commands

from req import mongo, core


class Bot(core.Core):
    def __init__(self):
        super().__init__("Jason", [Events, Commands])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx, user: discord.Member=None):
        if user:
            await ctx.send(ctx.author.mention, embed=discord.Embed(title="Balance",
                                                                   description=f"{user.mention} currently has {mongo.User(user).bal}cr"))
        else:
            await ctx.send(ctx.author.mention, embed=discord.Embed(title="Balance",
                                                                   description=f"You currently have {mongo.User(ctx.author).bal}cr"))

    @commands.command(name="givemoney")
    async def give_money(self, user: discord.Member, amt: int):




Bot()