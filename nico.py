import discord
from discord.ext import commands

import json

import core
from req import mongo, errors


class Bot(core.Core):
    def __init__(self):
        super().__init__("Nico", [Events, Commands])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


Bot()