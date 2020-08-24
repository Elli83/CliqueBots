import discord
from discord.ext import commands

import json

from req import mongo, errors


class Core(commands.Bot):
    """
    This is the core code for all bots to share
    All 4 bot classes inherit this class

    To initialise just use super().__init__("NAME", [list of cog classes])
    """

    def __init__(self, name, cogs=None):
        print("Starting bot...")
        super().__init__(command_prefix="!")   # Initialises the commands.Bot class
        self.token = self.config.tokens[name]   # Get the token from tokens.json

        self.remove_command("help")   # Remove the default help command

        # Load all cogs
        for c in cogs:
            self.add_cog(c(self))
            print("Loaded " + c.__name__)

        self.add_cog(errors.ErrorHandler(self))   # Load the custom error handler

        self.run()   # Start the bot

    async def on_ready(self):
        print(f"Logged in as {self.user.name}#{self.user.discriminator}")
        print("Bot ready!")

    @property
    def config(self):
        return Config(self)

    @property
    def channels(self):
        return self.config.channels

    def run(self):
        print("Logging in...")
        super().run(self.token)   # Calls commands.Bot's run function


class Config():
    def __init__(self, bot):
        self.bot = bot

        self.feeds = self.load("feeds")
        self.houses = self.load("houses")
        self.intros = self.load("intros")
        self.messages = self.load("messages")
        self.settings = self.load("settings")
        self.tokens = self.load("tokens")
        self.welcome = self.load("welcome")

    @property
    def channels(self):
        f = self.load("channels")
        c = {}
        for k, v in f.items():
            c[k] = self.bot.get_channel(v)
        return c

    def load(self, name):
        return json.load(open(f"./config/{name}.json"))