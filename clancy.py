import discord
from discord.ext import commands, menus

import time

from req import core, mongo, embeds, checks


class Bot(core.Core):
    def __init__(self):
        super().__init__("Clancy", [Events, Commands])


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["commands"])
    async def help(self, ctx):
        embed = discord.Embed(title="HELP",
                              description="Help page coming soon**™**")
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(ctx.author.mention, embed=discord.Embed(title="Pong!",
                                                               description=f"Time taken: {round(self.bot.latency*1000)}ms",
                                                               color=0x33ff33))

    @commands.command(name="tags")
    async def tags(self, ctx):
        tags = []
        utags = []

        for t in list(mongo.Tag.get_all()):
            print(t['Name'])
            if t['Author'] == ctx.author.id:
                utags.append(t)
            else:
                tags.append(t)

        embed=discord.Embed(title="Tags",
                            description=' '.join([f"`{tag['Name']}`" for tag in tags]) or "There are no tags!")

        embed.add_field(name="Your tags",
                        value=' '.join([f"`{tag['Name']}`" for tag in utags]) or "You have not created any tags!")

        return await ctx.send(embed=embed)

    @commands.group(name="tag", aliases=["t"], invoke_without_command=True)
    async def tag(self, ctx, tag):
        if mongo.Tag.exists(tag):
            await ctx.send(mongo.Tag(tag).body)
        else:
            await ctx.send(ctx.author.mention, embed=embeds.error(f"The tag {tag} does not exist!"))

    @tag.command(name="create")
    async def tag_create(self, ctx, name=None, *, body=None):
        if not name:
            embed = discord.Embed(title="Tag Creator - Name",
                                  description="What would you like to call your tag?")
            embed.set_footer(text="This is used for the command to call your tag")
            await ctx.send(ctx.author.mention, embed=embed)
            name = await self.bot.wait_for('message', check=lambda m: m.channel.id == ctx.channel.id and m.author.id == ctx.author.id)
            name = name.content

        if mongo.Tag.exists(name):
            await ctx.send(embed=embeds.error(f"The tag `{name}` already exists!"))
            return

        if not body:
            embed = discord.Embed(title="Tag Creator - Body",
                                  description="What would you like your tag to say?")
            await ctx.send(ctx.author.mention, embed=embed)
            body = await self.bot.wait_for('message', check=lambda m: m.channel.id == ctx.channel.id and m.author.id == ctx.author.id)
            body = body.content

        embed = discord.Embed(title="Tag Creator",
                              description=f"Are you sure you would like to create the tag `{name}`")
        embed.set_footer(text="Creating a tag costs 50cr")

        noembed = discord.Embed(title="Tag Creator",
                                description="You have cancelled tag creation")

        if await embeds.confirm(ctx, embed=embed, noembed=noembed):
            mongo.User(ctx.author).bal -= 50
            mongo.Tag._create(name, body, ctx.author.id)
            await ctx.send(ctx.author.mention, embed=embeds.success(f"You have created the tag `{name}`\n"
                                                                    f"You can use it with `!tag {name}`"))

    @tag.command(name="edit")
    async def tag_edit(self, ctx, name, *, new=None):
        if mongo.Tag.exists(name):
            tag = mongo.Tag(name)
            if tag.author == ctx.author.id or checks.admin(ctx):
                if not new:
                    embed = discord.Embed(title="Tag Editor",
                                          description=f"What would you like the new content of {name} to be?")
                    await ctx.send(ctx.author.mention, embed=embed)
                    new = await self.bot.wait_for('message', check=lambda m: m.channel.id == ctx.channel.id and m.author.id == ctx.author.id)
                    new = new.content

                embed = discord.Embed(title="Tag Editor",
                                      description=f"Are you sure you would like to edit the tag `{name}`")
                if tag.author == ctx.author.id:
                    embed.set_footer(text="Editing a tag costs 25cr")

                if await embeds.confirm(ctx, embed=embed):
                    if tag.author == ctx.author.id:
                        mongo.User(ctx.author).bal -= 25
                    tag.change(new)
                    await ctx.send(ctx.author.mention, embed=embeds.success(f"You have edited the tag `{name}`\n"
                                                                            f"You can use it with `!tag {name}`"))
            else:
                await ctx.send(embed=embeds.error(f"You do not have permissions to edit the tag {name}"))
        else:
            raise commands.UserInputError

    @tag.command(name="remove", aliases=["delete"])
    @commands.has_permissions()
    async def tag_delete(self, ctx, name):
        if mongo.Tag.exists(name):
            tag = mongo.Tag(name)
            if ctx.author.id == tag.author or checks.moderator(ctx):
                embed = discord.Embed(title="Delete Tag",
                                      description=f"Are you sure you want to delete the tag {name}?")
                if await embeds.confirm(ctx, embed):
                    mongo.Tag(name).remove()
                    await ctx.send(ctx.author.mention, embed=embeds.success(f"You have deleted the name {name}"))
            else:
                await ctx.send(ctx.author.mention, embed=embeds.error(f"You do not have permission to delete the tag {name}"))
        else:
            await ctx.send(ctx.author.mention, embed=embeds.error(f"The tag {name} does not exist"))

    @tag.command(name="info", aliases=["about"])
    async def tag_info(self, ctx, name):
        if mongo.Tag.exists(name):
            tag = mongo.Tag(name)

            embed = discord.Embed(title=f"Tag: {name}")
            
            embed.add_field(name="Author", value=f"<@{tag.author}>")
            embed.add_field(name="Created On", value=time.strftime("%D @ %R UTC", time.gmtime(tag.created)))

            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embeds.error(f"The tag {name} does not exist!"))



Bot()