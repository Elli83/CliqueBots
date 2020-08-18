import discord


def error(body, title="ERROR"):
    embed = discord.Embed(title=title,
                          description=body,
                          color=0xff3333)
    return embed


def success(body, title="SUCCESS"):
    embed = discord.Embed(title=title,
                          description=body,
                          color=0x33ff33)
