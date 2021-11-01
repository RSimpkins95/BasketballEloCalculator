import requests
from bs4 import BeautifulSoup
from eloeco import EloEco
from team import Team, Game
import pickle
import time


testelo: EloEco = None
try:
    testelo = pickle.load(open('elosystem.p', 'rb'))
except FileNotFoundError:
    sourcepage = 'https://www.sports-reference.com/cbb/schools/'

    rooturl = 'https://www.sports-reference.com'

    scheduleurl = '2021-schedule.html'

    sourcehtml = requests.get(sourcepage)
    bbsoup = BeautifulSoup(sourcehtml.content, 'html.parser')

    testhtml = ''

    count = 0
    testelo = EloEco()

    for link in bbsoup.findAll('td', {'data-stat': 'school_name'}):
        teamlink: str = link.a['href']
        print(teamlink)
        teamname = teamlink.split('/')[-2]
        testhtml = rooturl + teamlink + scheduleurl
        print("We are going to evaluate:", testhtml)
        time.sleep(.5)
        schedulehtml = requests.get(testhtml)
        schedsoup = BeautifulSoup(schedulehtml.content, 'html.parser')
        table = schedsoup.findChildren('table', {'id': 'schedule'})

        try:
            schedule = table[0]
            abilteam = Team(teamname)
            testelo.add_team(abilteam)
            rows = schedule.findChildren('tr')

            for row in rows:
                if "\n" not in row:
                    soup = BeautifulSoup(str(row), 'lxml')
                    columns = soup.find_all('td')
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