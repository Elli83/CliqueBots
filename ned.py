import discord
from discord.ext import commands, menus

import math
import random

from req import core, mongo


class Bot(core.Core):
    def __init__(self):
        super().__init__("Ned", [Events, Commands])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rps", aliases=["rockpaperscissors"])
    async def rps(self, ctx, bet:int):
        if bet < 0:
            raise commands.UserInputError
        mongo.User(ctx.author).check_bal(bet)

        options = ["✊", "✋", "✌"]
        colors = [0xff3333, 0xffff33, 0x33ff33]

        class RpsMenu(menus.Menu):
            def __init__(self):
                super().__init__(clear_reactions_after=True)

                for o in options:
                    self.add_button(menus.Button(emoji=o, action=self.button))

            async def send_initial_message(self, ctx, channel):
                embed = discord.Embed(title="Rock Paper Scissors",
                                      description=f"Ned ❔ : ❔ {ctx.author.display_name}",
                                      color=0xffff33)
                return await ctx.send(embed=embed)

            async def button(self, payload):
                self.play = payload.emoji
                self.stop()

            async def prompt(self, ctx):
                await self.start(ctx, wait=True)
                return str(self.play), self.message

        play, message = await RpsMenu().prompt(ctx)
        oplay = random.choice(options)

        if play == oplay:
            win = 0
            d = f"Ned {oplay} : {play} {ctx.author.display_name}"
        elif (oplay == "✌" and play == "✊") or (oplay == "✊" and play == "✋") or (oplay == "✋" and play == "✌"):
            win = 1
            d = f"Ned {oplay} : {play} **{ctx.author.display_name}**"
        else:
            win = -1
            d = f"**Ned** {oplay} : {play} {ctx.author.display_name}"

        mongo.User(ctx.author).bal += math.floor((bet * win) if win < 1 else (bet * (win/2)))

        embed = discord.Embed(title="Rock Paper Scissors",
                              description=d,
                              color=colors[win+1])
        await message.edit(embed=embed)


Bot()