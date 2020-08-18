import discord
from discord.ext import commands

from req import core


class Bot(core.Core):
    def __init__(self):
        super().__init__("Clancy", [Events, Commands])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["commands"])
    async def help(self, ctx):
        embed = discord.Embed(title="HELP",
                              description="Help page coming soon**™**")
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(ctx.author.mention, embed=discord.Embed(title="Pong!",
                                                               description=f"Time taken: {round(self.bot.latency*1000)}ms",
                                                               color=0x33ff33))


Bot()