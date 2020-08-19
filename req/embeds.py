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


class ConfirmTransaction(menus.Menu):
    def __init__(self, message=None):
        super().__init__(timeout=30)
        self.confirm = False

    async def send_initial_message(self, ctx, channel):
        embed=discord.Embed(title="Confirm Transaction",
                            description="React with 👍 to confirm the transaction\n"
                                        "React with 👎 to cancel the transaction")
        return await ctx.send(ctx.author.mention, embed=embed)

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
            await self.message.delete()
        else:
            embed = discord.Embed(title="Transaction Cancelled",
                                  description="You have cancelled the transaction",
                                  color=0xff0000)
            await self.message.edit(content=ctx.author.mention, embed=embed, delete_after=10)

        return self.confirm
