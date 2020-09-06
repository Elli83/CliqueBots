import discord
from discord.ext import commands

from req import core


class Bot(core.Core):
    def __init__(self):
        super().__init__("Nico", [Events, Commands])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="ticket", aliases=["t"], invoke_without_command=True)
    async def ticket(self, ctx, *, info=None):
        perms = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.get_role(self.bot.config.roles['moderator']): discord.PermissionOverwrite(read_messages=True),
            ctx.guild.get_role(self.bot.config.roles['admin']): discord.PermissionOverwrite(read_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True)
        }
        ch = await ctx.guild.create_text_channel(name="ticket", category=self.bot.get_channel(748286304944390264), overwrites=perms)

        embed=discord.Embed(title=f"{ctx.author.display_name} opened a ticket",
                            description=info,
                            color=0xfefefe)
        m = await ch.send("@everyone", embed=embed)
        await m.pin()

    @ticket.command(name="add")
    async def ticket_add(self, ctx, user:discord.Member):
        await ctx.channel.edit(overwrites={**ctx.channel.overwrites, user: discord.PermissionOverwrite(read_messages=True)})
        m = await ctx.channel.send(user.mention, embed=discord.Embed(description=f"**{ctx.author.display_name}** added **{user.display_name}**", color=0x22cc22))
        await m.pin()

    @ticket.command(name="remove")
    async def ticket_remove(self, ctx, user:discord.Member):
        await ctx.channel.edit(overwrites={**ctx.channel.overwrites, user: discord.PermissionOverwrite(read_messages=None)})
        m = await ctx.channel.send(user.mention, embed=discord.Embed(description=f"**{ctx.author.display_name}** removed **{user.display_name}**", color=0xcc2222))

    @ticket.command(name="comment")
    async def ticket_comment(self, ctx, *, body):
        m = await ctx.send(embed=discord.Embed(title=f"Comment by {ctx.author.display_name}",
                                               description=body,
                                               color=0x33aaff))
        await m.pin()

    @ticket.command(name="close")
    async def ticket_close(self, ctx):
        await ctx.channel.edit(overwrites={**ctx.channel.overwrites, ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False)})


Bot()