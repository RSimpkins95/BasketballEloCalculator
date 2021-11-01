import datetime
import random
import sys


class Game:
    def __init__(self, date: str, gtype: str, tone: str, ttwo: str, tonescore: int, ttwoscore: int, ot: bool = False):
        self.id: int = random.randint(0, sys.maxsize)
        self.date: datetime.datetime = datetime.datetime.strptime(date, "%a, %b %d, %Y")
        self.type: str = gtype
        self.tone: str = tone
        self.ttwo: str = ttwo
        self.tonescore: str = tonescore
        self.ttwoscore: str = ttwoscore
        self.overtime: bool = ot

    def print_me_daddy(self):
        print("id:", self.id, "Team:", self.tone, "vs", self.ttwo, "results", self.tonescore, "-", self.ttwoscore, "on", self.date)


class Team:

    def __init__(self, name: str):
        self.name: str = name
        self.games: dict = {}
        self.elo: int = 1600

    def set_elo(self, elo):
        self.elo = elo

    def get_elo(self) -> int:
        return self.elo
