from team import Team, Game
import datetime
import math

anoms = dict()

#all teams are listed in lower case and spaces are separeted by hyphens '-' e.g: abilene-christian vs tennessee
class EloEco:

    def __init__(self, k=75):
        self.count: int = 0
        self.teams: dict = {}
        self.now: datetime.date = datetime.datetime.now()
        self.games: dict = dict()
        self.k = k

    def add_team(self, ateam: Team):
        self.teams[ateam.name] = ateam
        return

    def get_team(self, name: str) -> Team:
        if name in self.teams.keys():
            return self.teams[name]

    def add_game(self, game: Game):
        date = game.date.strftime('%s')
        if date not in self.games.keys():
            self.games[date] = list()
        for games in self.games[date]:
            for element in games[0:2]:
                if element == game.ttwo or element == game.tone:
                    return
        self.games[date].append((game.tone, game.ttwo, game))

    '''
    Inside of class Game:
        Team One,
        Team Two
        Team One Score
        Team Two Score
    
    Inside of class Team:
        Team Name
        Team Elo
    '''
    def calculate_elo(self, game: Game):
        if game.tone not in self.teams.keys():
            print(game.tone, "not registered.")
            return
        if game.ttwo not in self.teams.keys():
            print(game.ttwo, "not registered.")
            return

        winner: Team = None
        loser: Team = None
        winscore: float = 0.0
        losescore: float = 0.0
        if game.tonescore > game.ttwoscore:
            winner = self.teams[game.tone]
            loser = self.teams[game.ttwo]
            winscore = game.tonescore
            losescore = game.ttwoscore
        else:
            winner = self.teams[game.ttwo]
            loser = self.teams[game.tone]
            winscore = game.ttwoscore
            losescore = game.tonescore

        rwin = math.pow(10, winner.elo / 400)
        rlose = math.pow(10, loser.elo / 400)

        exp_win = rwin / (rwin + rlose)
        exp_lose = rlose / (rwin + rlose)

        if exp_win < .40:
            game_date = game.date.strftime('%s')
            if game_date not in anoms.keys():
                anoms[game_date] = 0.0
            anoms[game_date] = anoms[game_date] + (1 / len(self.games[game_date]))

        r_prime_win = winner.elo + self.k * (1 - exp_win)
        r_prime_lose = loser.elo + self.k * (0 - exp_lose)

        ''' "Adaptive Win Loss", Takes into account the baskets scored
            this is here primarily to compensate situations where a team
            that should be expected to outscore a team by many 
            instead wins by a narrow margin.

        # Here is a "normalized" score,
        # A typical basketball game finishes with both teams averaging
        # around 60 points,
        norm_win = math.pow(10, winscore / 15)
        norm_lose = math.pow(10, losescore / 15)

        real_win = norm_win / (norm_lose + norm_win)
        real_lose = norm_lose / (norm_lose + norm_win)
        
        r_prime_win = winner.elo + self.k * (real_win - exp_win)
        r_prime_lose = loser.elo + self.k * (real_lose - exp_lose)
        '''

        winner.elo = r_prime_win
        loser.elo = r_prime_lose
        return

    def expect_win(self, tone: str, ttwo: str):

        if tone not in self.teams.keys():
            print(tone, "not registered.")
            return
        if ttwo not in self.teams.keys():
            print(ttwo, "not registered.")
            return
        teamone: Team = self.teams[tone]
        teamtwo: Team = self.teams[ttwo]

        rone = math.pow(10, teamone.elo / 400)
        rtwo = math.pow(10, teamtwo.elo / 400)

        exp_one = rone / (rone + rtwo)
        exp_two = rtwo / (rone + rtwo)

        print("In the event of ", tone, " vs ", ttwo, ":", tone, exp_one, ";", ttwo, exp_two)

    def top_tier(self):
        tier = dict()
        for name, team in self.teams.items():
            tier[str(team.elo)] = name
        top = sorted(tier.keys(), reverse=True)
        count = 0
        for num in top:
            print(count + 1, tier[num], self.teams[tier[num]].elo)
            count += 1
            if count >= 10:
                pass
        return

    def clean_anomalies(self):
        totanom = 0.0
        for key, val in anoms.items():
            print(key, val)
            totanom += val
        print(len(anoms.keys()))
        print(totanom / len(anoms.keys()))

    def set_k(self, newk: int):
        self.k = newk