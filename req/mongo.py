import discord
from discord.ext import commands
import time
import json

from pymongo import MongoClient

from . import errors

config = json.load(open("config/settings.json"))

client = MongoClient(config['mongo']['uri'])
db = client[config['mongo']['db']]


class User:
    defaults = {
        "Balance": 0,
        "XP": 0,
        "Inventory": {
            "Roles": [],
            "Backgrounds": []
        },
        "Joined": time.time(),
        "Seen": time.time()
    }

    # --------------------------------------------------

    def __init__(self, user):
        if type(user) in [discord.User, discord.Member]: user = user.id
        self.id = str(user)

        if not self._exists(self.id):
            self._create(self.id)

    # BALANCE
    @property
    def bal(self): return self.get("Balance")

    @bal.setter
    def bal(self, bal: int):
        if bal < 0:
            raise errors.InsufficientBalance
        self.update("Balance", bal)

    # CORE FUNCTIONS
    def get(self, field):
        return self._get(self.id).get(field)

    def update(self, field, value):
        self._update(self.id, field, value)

    # --------------------------------------------------
    # CLASS METHODS

    @classmethod
    def _exists(cls, id):
        return len(list(db['Users'].find({"ID": str(id)}))) > 0

    @classmethod
    def _get(cls, id):
        return db['Users'].find_one({"ID": str(id)})

    @classmethod
    def _update(cls, id, field, value):
        db['Users'].update_one({"ID": str(id)}, {"$set": {field: value}})

    @classmethod
    def _create(cls, id):
        db['Users'].insert_one({"ID": str(id), **cls.defaults})

