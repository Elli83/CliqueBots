from discord.ext import commands

from req import core


class Bot(core.Core):
    def __init__(self):
        super().__init__("Ned", [Events, Commands])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


Bot()