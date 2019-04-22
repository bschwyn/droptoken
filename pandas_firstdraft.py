#some of these queries are incorrect, but writing them out here was helpful for my thoughts

import pandas as pd
import requests


class Pandas:

    #dataframe gets extracted and put into pandas
    def __init__(self, df):
        self.df = df

    def first_moves_game_id_and_column(self):
        #returns list of moves where all moves are the first one, and column number
        #[(first move column number, game_id)]
        filter = self.df["move_number"]==1
        data = self.df.where(filter, inplace = False) #### [moves are first one]
        #leaves NaN's
        game_id_and_column = data[['game_id', 'column']]
        return game_id_and_column

    def game_numbers_and_win(self):

        #takes first_moves_list and returns list of game_numbers
        #[(game_id, win), ... ]
        game_ids_and_result = self.df[self.df["result"].notnull()]
        game_ids_and_win = game_ids_and_result.where(game_ids_and_result['result'] =='win', inplace=False).dropna()
        return game_ids_and_win

    def wins_per_column(self):
        #matches first_move_column number/game_id w/ game_id/win to get [(first_move_col_number, win), ... ]
        #seems like there are two possibilities here:
        #1 is to put all of the first things in a hash table and access them via the second
        #2 is to do a join
        game_id_and_column = self.first_moves_game_id_and_column()
        game_id_and_win = self.game_numbers_and_win()


        #so expensive that it doesn't work
        """ win_and_column = pd.merge(left=game_id_and_column,
                                  right = game_id_and_win,
                                  left_on='game_id',
                                  right_on='game_id',
                                  how='inner')"""

        d = {}
        for index, row in game_id_and_column.iterrows():
            game_id = row['game_id']
            column = row['column']
            d[game_id] = column
        wins_per_column = [0]*4
        for index, row in game_id_and_win.iterrows():
            game_id = row['game_id']
            col = int(d[game_id])
            wins_per_column[col-1] +=1

        return wins_per_column

    def percentile_wins_per_column(self, wins_per_column):
        #takes wins_per_column, outputs percentile_wins_per_column
        #[(column_number, win), ... ] ---> [(col 1, % wins), ... (col4, %wins)]
        total_wins = sum(wins_per_column)
        #possible tie
        percentile_wins_per_column = [round(wins/total_wins, 3) for wins in wins_per_column]
        return percentile_wins_per_column

    def best_columnn_to_win(self):
        wins_per_column = self.wins_per_column()
        percentile_wins_per_column = self.percentile_wins_per_column(wins_per_column)
        return percentile_wins_per_column.index(max(percentile_wins_per_column)) +1

    def create_second_table(self):
        #creates a table of games, player1, player2, and result
        df = self.df
        moves_1 = df[df.move_number == 1]
        moves_2 = df[df.move_number == 2]
        results = df[df.result.notna()]
        d2 = moves_1.merge(right=moves_2, how='inner', left_on='game_id', right_on='game_id')
        d2 = d2.merge(right = results, how='inner', left_on='game_id', right_on='game_id')
        d2 = d2[['game_id','player_id', 'player_id_x', 'player_id_y', 'result']] #also maybe 1st move
        d2.rename(columns = {'player_id': 'last_player'}, inplace=True)
        print(d2.columns.values)
        return d2

    def games_per_nation(self):
        #goes through database
        #returns list of tuples [(nation, #games), ...]

        #go through games
        #get both players for each game to get list of players
        #get player, game count per player

        #create a table of move1 and move2s, merge those two tables
        #to create table of game, player1, player2, result
        players_and_games = self.create_second_table()

        #make a table of players and how many games they are in
        #several possibilities:
            #1)make player to #games dict,
                #make nations dict. Go through player-to-nation db and do nation-to-player*#games = nation-to-games
            #2) make game to player dict (more space)
                #go through
        #3 make player-nation table from json, and then do a join, count nations and games

        players = {}
        for  index, row in players_and_games.iterrows():
            game_id = row['game_id']
            player_1 = row['player_id_x']
            player_2 = row['player_id_y']

            if player_1 in players:
                players[player_1] +=1
            else:
                players[player_1] = 1
            if player_2 in players:
                players[player_2] +=1
            else:
                players[player_1] = 1

        nations = {}

        # then page through entire json player thingy
        # get nation/player
        # lookup nation, lookup player and how many games that player played
        # add that to nation count

        params = {'Accept': 'application/json'}
        url = 'https://x37sv76kth.execute-api.us-west-1.amazonaws.com/prod/users?page='
        page = 0
        r = requests.get(url = url + str(page), params = params)


        #iterate through entire json player library thing (should take approx 5 minutes)
        json_array = r.json()
        while json_array: #while json is not empty...
            for object in json_array: #10 objects
                id = object['id']
                nat = object['data']['nat']
                if id in players:
                    if nat in nations:
                        nations[nat] += players[id]
                    else:
                        nations[nat] = players[id]
            page +=1
            r = requests.get(url=url+str(page), params=params)
            json_array = r.json()

        #return games per nation
        return nations

    def one_game_players(self):
        #return players with one game

        players_and_games = self.create_second_table()
        # make a table of players and how many games they are in
        players = {}
        for index, row in players_and_games.iterrows():
            game_id = row['game_id']
            player_1 = row['player_id_x']
            player_2 = row['player_id_y']
            result = row['result']
            last_player = row['last_player']

            if player_1 in players:
                players[player_1] = None
            else:
                players[player_1] = {'game_id': game_id, 'result':result, 'last_player': last_player}
            if player_2 in players:
                players[player_2] = None
            else:
                players[player_1] = {'game_id': game_id, 'result':result, 'last_player': last_player}

        #filter out players that were only in one game
        one_game_players = {player: game_id for player, game_id in players.items() if game_id is not None}

        print(len(one_game_players))

        return one_game_players


    def customizable_email(self, game_result):
        #need single game_players, result, and winner

        df = self.create_second_table()
        one_game_players = self.one_game_players()
        if game_result == 'win':
            #get game_id
            #given player that played a game and win, and winner.
            players = [player for player, dict in one_game_players.items()
                       if dict['result'] == 'win' and dict['last_player'] == player]
            email_content = "email for single-game-winners"
        elif game_result == 'lose':
            players = [player for player, dict in one_game_players.items()
                       if dict['result'] == 'win' and dict['last_player'] != player]
            email_content = "email for single-game-losers"
        elif game_result == 'draw':
            players = [player for player, dict in one_game_players.items()
                       if dict['result'] == 'draw']
            email_content = "email for single-game-draw"
        return players, email_content



#tests
def p1():
    df = pd.read_csv('~/Projects/droptoken/game_data.csv')
    x = Pandas(df)
    best_column_to_win = x.best_columnn_to_win()
    print(best_column_to_win)
    print(best_column_to_win == 2)

def p2():
    #create
    df = pd.read_csv('~/Projects/droptoken/game_data.csv')
    x = Pandas(df)
    bla = x.games_per_nation()
    print(x)
    #print(bla)

def p3():
    #test for winners
    df = pd.read_csv('~/Projects/droptoken/game_data.csv')
    x = Pandas(df)
    bla = x.customizable_email('win')
    return bla
