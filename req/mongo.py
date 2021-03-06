import discord
from discord.ext import commands

import math
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
        "Daily": {
            "Last": 0,
            "Streak": 0
        },
        "Joined": time.time(),
        "Seen": time.time()
    }

    @staticmethod
    def calc_level(xp):
        return math.floor(math.pow(((xp + 2) / 2), 1 / 3))

    # --------------------------------------------------

    def __init__(self, user:discord.User):
        self.user = user
        self.id = str(user.id)

        if not self._exists(self.id):
            self._create(self.id)

        self.daily = self._Daily(self)

    @property
    def level(self):
        return self.calc_level(self.xp)

    @property
    def xp(self): return self.get("XP")

    async def addxp(self, amt: int, channel: discord.TextChannel=None):
        channel = channel or self.user

        l1 = self.level   # Get level before adding xp
        self.update("XP", self.xp + amt)   # Add xp
        l2 = self.level   # Get level after adding xp

        if l2 > l1:   # Check for level up
            await channel.send(f":tada: **Level up!** ({l1} > {l2})   {self.user.mention if not channel == self.user else ''}")

    @property
    def bal(self): return self.get("Balance")

    @bal.setter
    def bal(self, bal: int):
        if bal < 0:
            raise errors.InsufficientBalance
        self.update("Balance", bal)

    def check_bal(self, amt):
        if self.bal - amt < 0:
            raise errors.InsufficientBalance

    class _Daily:
        def __init__(self, user):
            self.user = user

        @property
        def claimed(self): return self.user.get("Daily")['Last'] or 0

        @property
        def ready(self): return self.claimed < time.time() - 86400

        @property
        def since(self): return time.time() - self.claimed

        @property
        def until(self): return 86400 - (time.time() - self.claimed)

        def claim(self):
            self.user.update("Daily.Last", time.time())

        @property
        def streak(self):
            return self.user.get("Daily")['Streak'] or 0

        @streak.setter
        def streak(self, streak):
            self.user.update("Daily.Streak", streak)

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


class Tag:
    def __init__(self, name):
        self.name = name
        self.body = self.get('Body')
        self.author = self.get('Author')
        self.created = self.get('Created')

    def change(self, new):
        self._update(self.name, "Body", new)

    def remove(self):
        self._remove(self.name)

    def get(self, field):
        return self._get(self.name).get(field)

    # --------------------------------------------------
    # CLASS METHODS
    @classmethod
    def exists(cls, name):
        return len(list(db['Tags'].find({"Name": name}))) > 0

    @classmethod
    def _get(cls, name):
        return db['Tags'].find_one({"Name": name})

    @classmethod
    def get_all(cls):
        return db['Tags'].find({})

    @classmethod
    def _update(cls, name, field, value):
        db['Tags'].update_one({"Name": name}, {"$set": {field: value}})

    @classmethod
    def _create(cls, name, body, author):
        db['Tags'].insert_one({"Name": name, "Body": body, "Author": author, "Created": time.time()})

    @classmethod
    def _remove(cls, name):
        db['Tags'].delete_one({"Name": name})
