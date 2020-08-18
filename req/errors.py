import discord
from discord.ext import commands

import traceback
import sys
import math

from . import embeds


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

        print("Loaded Error Handler")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):   # Check if the command has its own error handler
            return

        ignored = (commands.CommandNotFound)   # A list of errors to ignore
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):   # Ignore particular errors (command not found etc.)
            return

        elif isinstance(error, commands.DisabledCommand):   # Command is disabled
            return await ctx.send(ctx.author.mention, embed=embeds.error(f"Command `{ctx.command}` has been disabled"))

        elif isinstance(error, commands.CheckFailure):   # Insufficient permissions (admin command etc.)
            return await ctx.send(ctx.author.mention, embed=embeds.error(f"You do not have permissions to use `{ctx.command}\n"
                                                                         f"If you believe this is a mistake please contact @Admins`"))

        elif isinstance(error, commands.NoPrivateMessage):   # Command is disabled IN DMs
            return await ctx.send(ctx.author.mention, embed=embeds.error(f"Command `{ctx.command}` cannot be used in DMs"))

        elif isinstance(error, InsufficientLevel):   # Insufficient level
            return await ctx.send(ctx.author.mention, embed=embeds.error(f"You must be level `{error.level}` to use `{ctx.command}`"))

        elif isinstance(error, commands.CommandOnCooldown):   # Command on cooldown
            return await ctx.send(ctx.author.mention, embed=embeds.error(f"Command `{ctx.command}` is on cooldown, try again in {math.ceil(error.retry_after)} seconds"))

        elif isinstance(error, commands.UserInputError):   # User uses command wrong (incorrect arguments etc.)
            return await ctx.send(ctx.author.mention, embed=embeds.error(f"Invalid command usage, use `!help` for more info"))

        elif isinstance(error, InsufficientBalance):   # Users balance would go below 0
            return await ctx.send(ctx.author.mention, embed=embeds.error(f"You do not have enough money!"))

        # If the error doesnt match any of the above then just print it to the console
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# CUSTOM ERROR CLASSES
class InsufficientLevel(commands.CommandError):
    def __init__(self, level, *args, **kwargs):
        self.level = level   # (the level required)
        super().__init__(*args, **kwargs)


class InsufficientBalance(commands.CommandError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
