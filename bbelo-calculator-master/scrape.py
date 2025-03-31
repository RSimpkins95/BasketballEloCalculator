import sys
from random import random, uniform
import requests
from bs4 import BeautifulSoup
from eloeco import EloEco
from team import Team, Game
import pickle
import time


testelo: EloEco = None
try:
    testelo = pickle.load(open('elosystem.p', 'rb'))

    print('[INFO] Pickle file found, loaded existing Elo system.')

    # Inspect the loaded object
    print(f"Teams loaded: {len(testelo.teams)}")
    print(f"Games loaded: {sum(len(g) for g in testelo.games.values())}")

except FileNotFoundError:
    sourcepage = 'https://www.sports-reference.com/cbb/schools/'
    rooturl = 'https://www.sports-reference.com'
    scheduleurl = '2025-schedule.html'
    sourcehtml = requests.get(sourcepage)
    bbsoup = BeautifulSoup(sourcehtml.content, 'html.parser')
    testhtml = ''
    testelo = EloEco()

    for link in bbsoup.find_all('td', {'data-stat': 'school_name'}):
        teamlink: str = link.a['href']
        print(teamlink)

        if "/men/" not in teamlink:
            continue

        teamname = teamlink.split('/')[-3]
        testhtml = rooturl + teamlink + scheduleurl
        print("We are going to evaluate:", testhtml)
        time.sleep(uniform(3.0, 5.0))
        schedulehtml = requests.get(testhtml)

        if "we block traffic that we think is from a bot" in schedulehtml.text:
            print("[WARNING] Detected block, exiting scraper.")
            sys.exit(0)

        schedsoup = BeautifulSoup(schedulehtml.content, 'html.parser')
        table = schedsoup.find_all('table', {'id': 'schedule'})

        try:
            schedule = table[0]
            abilteam = Team(teamname)
            testelo.add_team(abilteam)
            rows = schedule.find_all('tr')

            for row in rows:
                if "\n" not in row:
                    columns = row.find_all('td')
                    date: str = ''
                    gtype: str = ''
                    tone: str = teamname
                    ttwo: str = ''
                    tonescore: int = ''
                    ttwoscore: int = ''
                    ot: bool = False
                    # Comment out later
                    for col in columns:
                        stat = str(col.attrs['data-stat'])
                        val = str(col.text)
                        hrefs = col.find_all('a')

                        if hrefs:
                            if stat == 'opp_name':
                                ttwo = str(hrefs[0]).split("/")[3]

                        if stat == 'date_game' and val:
                            date = str(val)
                        elif stat == 'opp_pts' and val:
                            ttwoscore = int(val)
                        elif stat == 'pts' and val:
                            tonescore = int(val)
                        elif stat == 'game_type' and val:
                            gtype = str(val)
                        elif stat == 'overtimes' and val:
                            ot = True

                    if ttwo and ttwoscore and tonescore:
                        game = Game(date, gtype, tone, ttwo, tonescore, ttwoscore, ot)
                        testelo.add_game(game)

        except IndexError as e:
            print(e)

    pickle.dump(testelo, open('elosystem.p', 'wb'))

    print(testelo.games)

game_dates = sorted(testelo.games.keys())

for game_list in testelo.games.values():  # each value is a list of tuples
    for game_tuple in game_list:
        game = game_tuple[2]  # grab the Game object from the tuple
        print(f"{game.tone} ({game.tonescore}) vs {game.ttwo} ({game.ttwoscore}) on {game.date}")

newk = int(input("Enter a k: "))
testelo.set_k(newk)

for day in game_dates:
    for dailygame in testelo.games[day]:
        testelo.calculate_elo(dailygame[2])

testelo.clean_anomalies()
testelo.top_tier()


while(1):
    test1 = input("Enter first team: ")
    test2 = input("Enter second team: ")
    testelo.expect_win(test1, test2)