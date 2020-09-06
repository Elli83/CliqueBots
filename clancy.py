import discord
from discord.ext import commands, menus

import time
from datetime import datetime
import asyncio
import random

from req import core, mongo, embeds, checks


class Bot(core.Core):
    def __init__(self):
        super().__init__("Clancy", [Events, Commands])

    async def update_status(self):
        await self.change_presence(activity=discord.Activity(name=f"{len(self.users):,d} members", type=discord.ActivityType.listening))


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.update_status()   # Update the member count

    # We are using a custom on_join event instead of the default on_member_join
    # This is so that we can send the message when they get given the main role instead

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # This contradicts the comment above, I know, but this is only temporary
        await self.on_join(member)

    @commands.Cog.listener()
    async def on_join(self, member):
        embed = discord.Embed(description=random.choice(self.bot.config.messages['Join']).replace("{USER}", f"<@{member.id}>"),
                              color=0x33ff33)
        embed.set_footer(text=f"Member #{len(self.bot.users)}")

        await self.bot.config.channels['general'].send(f"Welcome, {member.mention}!", embed=embed)

        await self.bot.update_status()

    @commands.command()   # This just triggers the join event for testing
    async def join(self, ctx, member:discord.Member):
        await self.on_member_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await asyncio.sleep(3)   # Wait for audit logs to update

        type = "Leave"   # Set type to leave by default
        async for entry in member.guild.audit_logs(limit=3, oldest_first=False):   # Loop through the previous 3 audit logs
            if not (datetime.utcnow() - entry.created_at).seconds < 15: continue   # Check whether current entry is from last 15 seconds
            if not entry.target.id == member.id: continue   # Check that affected user is user who left the server
            if entry.action not in [discord.AuditLogAction.kick, discord.AuditLogAction.ban]: continue   # Check that entry is kick or ban

            if entry.action == discord.AuditLogAction.kick:
                type = "Kick"
                break   # Stop checking
            elif entry.action == discord.AuditLogAction.ban:
                type = "Ban"
                break   # Stop checking

        # Set the embed
        embed = discord.Embed(description=random.choice(self.bot.config.messages[type]).replace("{USER}", f"**{member.display_name}**"),
                              color=0xff3333 if type == "Leave" else 0x707070 if type == "Kick" else 0x202020)
        embed.set_footer(text=f"{member.display_name} {'left' if type == 'Leave' else 'was kicked' if type == 'Kick' else 'was banned'}")

        await self.bot.channels['general'].send(embed=embed)   # Send the leave message

        await self.bot.update_status()   # Update the member count

    @commands.command()   # This just triggers the join event for testing
    async def leave(self, ctx, member:discord.Member):
        await self.on_member_remove(member)


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

        body = body.replace("@everyone", "Nice try").replace("@here", "Nice try")

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

                new = new.replace("@everyone", "Nice try").replace("@here", "Nice try")

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