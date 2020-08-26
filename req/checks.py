from . import mongo, errors

import json

roles = json.load(open("./config/roles.json"))


async def admin(ctx):
    for r in ctx.author.roles:
        if r.id == roles['admin']:
            return True
    return False


async def moderator(ctx):
    if await admin(ctx):
        return True
    for r in ctx.author.roles:
        if r.id == roles['moderator']:
            return True
    return False
