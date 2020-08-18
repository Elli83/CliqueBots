import discord
from discord.ext import commands

import math
import json

import core
from req import mongo, errors


class Bot(core.Core):
    def __init__(self):
        super().__init__("Clancy", [Events, Commands])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(embed=discord.Embed(title="Pong!",
                                           description=f"Time taken: {round(self.bot.latency*1000)}ms",
                                           color=0x33ff33))


Bot()