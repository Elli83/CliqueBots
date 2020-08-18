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
        self.token = json.load(open("./config/tokens.json"))[name]   # Get the token from tokens.json

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

    def run(self):
        print("Logging in...")
        super().run(self.token)   # Calls commands.Bot's run function
