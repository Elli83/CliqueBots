import discord
from discord.ext import menus


def error(body, title="ERROR"):
    embed = discord.Embed(title=title,
                          description=body,
                          color=0xff3333)
    return embed


def success(body, title="SUCCESS"):
    embed = discord.Embed(title=title,
                          description=body,
                          color=0x33ff33)
    return embed


class Confirm(menus.Menu):
    def __init__(self, embed, yesembed=None, noembed=None):
        super().__init__(timeout=30)
        self.embed = embed
        self.yesembed = yesembed
        self.noembed = noembed
        self.confirm = False

    async def send_initial_message(self, ctx, channel):
        return await ctx.send(ctx.author.mention, embed=self.embed)

    @menus.button('\N{THUMBS UP SIGN}')
    async def on_confirm(self, payload):
        self.confirm = True
        self.stop()

    @menus.button('\N{THUMBS DOWN SIGN}')
    async def on_deny(self, payload):
        self.confirm = False
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait=True)

        await self.message.clear_reactions()

        if self.confirm:
            if self.yesembed:
                await self.message.edit(embed=self.yesembed)
            else:
                await self.message.delete()
        else:
            if self.noembed:
                await self.message.edit(embed=self.noembed)
            else:
                await self.message.delete()

        return self.confirm


async def confirm(ctx, embed=None, yesembed=None, noembed=None):
    if embed is None:
        embed = discord.Embed(title="Confirmation",
                              description="Are you sure?")

    return await Confirm(embed, yesembed, noembed).prompt(ctx)


async def confirm_transaction(ctx):
    embed = discord.Embed(title="Confirm Transaction",
                          description="React with 👍 to confirm the transaction\n"
                                      "React with 👎 to cancel the transaction")

    noembed = discord.Embed(title="Transaction Cancelled",
                            description="You have cancelled the transaction",
                            color=0xff3333)

    return await confirm(ctx, embed, noembed=noembed)

