import pandas as pd
import requests
import MySQLdb

#correctness
#testing and #validation, testing verifies that the program is correct
#test queries separately

#if i care about uptime, then use postgres instead of mysql for backups

# droptoken takes place on a 4x4 grid, a token is dropped along a column and goes to the lowest unoccupied row of the
# board. A player wins when they have 4 tokens next to ech other either along a row, in a column, or on a diagonal. If
# the board is filled, and nobody has won, then the game is a draw. Each player takes a turn, starting with player 1,
# until the game is either a win or a draw. If a player tries to put a token in a column that is already full, that
# results in an error state, and the player must play again until the play is a valid move.

# This is a data warehouse for stakeholders to answer questions about the droptoken players and games, and generally
# explore the data.

#columns of the original database are
# game_id, player_id, move_number, column, result (win, NaN, or draw)
# db has 145k lines

#a player profile API contains a bunch of json data for each player id, including nationality, with 10 players per page
# has ~5000 players, 10 per page

#The data warehouse should enable its custoers to easily run the following analysis
# 1. What is the percentile rank of each column used as the first move in a game?
# 2. How many games has each nationality participated in?
# 3. Come up with a list of players that have won a single game, lost a single game, or drew a single game. Send a
#    different email to each possibility.


#note:
#some data is messy, some of the game_id's are weird strings of values

#memory usage:
#2.3 MB for 145k lines --- 15.8 bytes/line, 10,000 games: 14.5 lines/game
#10,000,000 games: 2.3 GB, 145,000,000 lines

#~5000 players, 10/page, 2min12s to go through 500 pages ~0.384s/page, 8.3 KB per request, 4.15 MB total
#~5,000,000 players 10/page estimated 2.2 days. 4GB total
#things to do: Cache the result of the games/perNation
#when the players database is updated then


#choosing a database
#relational database, since it's pretty simple and flat
#pandas --- limit is my memory
# databases give concurrency, locking, constraints
#RedShift --- $.25/hr ---> 250$/TB/yr ---> probably much better if I'm scaling to Terabytes that won't fit in memeory
#PostGreSQL --- Open source, has good documentation, runs slightly faster than pandas when configured correctly
# as benchmarked by https://medium.com/carwow-product-engineering/sql-vs-pandas-how-to-balance-tasks-between-server-and-client-side-9e2f6c95677
# harder to scale horizontally than mongodb
# https://hackr.io/blog/postgresql-vs-mysql has more 'vs' info
#MySQL --- open source, bought by oracle


#postgres it is
#username: postgres
#hostname: 127.0.0.0
#db_name: postgres_db

#mongodb vs postgres for json data

#what are the actual concerns here?
#does it need to be able to scale to a distributed system? --- No, all of the information can fit on disk
#note that the entire database can fit in memory
#how long will each query take?
#how many queries will happen?
#will there be caching for the results of the queries?
#if there is caching for the results of the queries, how do update the cache?
#do I need to worry about horizontal scaling (more machines) or just vertical scaling (increase memory/ram




#test


#there is probably some fancy way of doing this where the analysis class implements some interface
#which calls some class on the sub class. Some subclasses implement things which call some or other database
#other subclasses might implement some other thingy for some other database
#this allows different databases and queries to be implemented

#god that sounds hard

#yeah that sounds like it will take a long time, but I at least know what it is talking about.
#it is probably fine to just do a normal one first.

#in case more queries are added... this would mean....?
#--- a new thing would be added to the interface, and then new implementations for each database

#make a bash script
#fails intelligently
#chunked intelligently



#bash script
#download mysql
#setup mysql
#make a virtual env
#install stuff
#download requirements
#upload the data in python or in bash?
#upload in bash, analysis in python

#alleviate your flinches early --- do something to make it less flinchy

#run script to get json data

#make table of id, nation and put in mysql also



#put tests in other file
#is the first query correct
#is the second query correct
#is the third query correct
#use pytest or something more professional
#check tests with small amount of data

#i have to connect to a specific database

class MySQL:

    def __init__(self):
        db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                             user="98point6",  # your username
                             passwd="password",  # your password
                             db="mydb")
        #cursor allows execution of queries on db
        #exectue queries
        self.connection = db

    def get_connection(self):
        return self.connection

    def is_table_empty(self, tablename, cursor):
        cursor.execute("SELECT 1 FROM " + tablename + " LIMIT 1;")
        result = cursor.fetchall()
        return len(result) == 0


    def create_games_and_players_table(self, connection):

        cursor = connection.cursor()

        if self.is_table_empty('games_and_players', cursor):

            query = """
                                INSERT INTO games_and_players
                                    SELECT A.game_id, player1, player2, last_player, result FROM
                                            (SELECT game_id, player_id as player1
                                            FROM game_data
                                            WHERE move_number=1)
                                        AS A
                                        JOIN
                                            (SELECT game_id, player_id as player2
                                            FROM game_data
                                            WHERE move_number=2)
                                        AS B
                                        ON A.game_id=B.game_id
                                        JOIN
                                        (SELECT game_id, player_id as last_player, result
                                            FROM game_data
                                            WHERE result='draw' or result='win'
                                        ) AS C
                                        ON A.game_id=C.game_id
                                """

            cursor.execute(query)
            connection.commit()


    #QUESTION 1
    def percentile_rank_results(self, connection):

        cursor = connection.cursor()

        if self.is_table_empty("games_won_per_column", cursor):

            query = """
                    INSERT INTO games_won_per_column 
                        SELECT column_number, COUNT(result)
                        FROM
                            (SELECT game_id, column_number
                            FROM game_data
                            WHERE move_number=1
                            ) AS A
                            JOIN
                            (SELECT game_id, result
                            FROM game_data
                            WHERE result='win'
                            ) AS B
                        ON A.game_id=B.game_id
                        GROUP BY column_number;
            """
            cursor.execute(query)

            view_query = """
                        CREATE VIEW percentile_column_rank AS
                            SELECT column_number, games/(SELECT SUM(games) FROM games_won_per_column) AS percent_WIN
                            FROM games_won_per_column
                        """
            cursor.execute(view_query)

            connection.commit()

    #QUESTION 2
    def games_per_nation(self, connection):
        cursor = connection.cursor()
        query = """
                CREATE VIEW games_per_nation AS
                SELECT nation, COUNT(game_id)
                FROM 
                    (games_and_players as A
                    JOIN
                    apitable AS B
                    ON A.player1=B.player_id OR A.player2=B.player_id)
                GROUP BY nation
                """
        cursor.execute(query)

        connection.commit()

    #QUESTION 3
    def customizable_email(self, connection, emails):
        cursor = connection.cursor()

        if emails == "win":
            view_name = "single_game_player_win"
            where_clause = "WHERE B.result='win' and B.player_id=B.last_player;"
        elif emails == "lose":
            view_name = "single_game_player_lose"
            where_clause = "WHERE B.result='win' and B.player_id!=B.last_player;"
        else: #draw
            view_name = "single_game_player_draw"
            where_clause = "WHERE B.result='draw'"


        # the inner select with the union gets information for players that played one game as player1, or as player2.
        # the next level select (SELECT A.* from...) removes the info for players that played 1 game as player1 and
        # as player 2.

        query = "CREATE VIEW " + view_name + """ AS
                    SELECT B.player_id
                    FROM 
                        (
                            SELECT A.* FROM
	                            (
	                                (SELECT game_id, player1 as player_id, last_player, result 
		                            FROM games_and_players 
		                            GROUP BY player1 
		                            HAVING count(player1)=1) 
	                            UNION 
		                            (SELECT game_id, player2 as player_id, last_player, result 
		                            FROM games_and_players 
		                            GROUP BY player2 
		                            HAVING COUNT(player2)=1)
	                            ) AS A
                            GROUP BY A.player_id
                            HAVING COUNT(A.player_id)=1
                        ) AS B """+ where_clause

        print(query)
        cursor.execute(query)
        connection.commit()

    #QUESTION 3
    def create_views_for_3_questions(self):
        connection = self.get_connection()
        #question 1
        self.percentile_rank(connection)
        #question 2
        self.create_games_and_players_table(connection)
        self.games_per_nation(connection)
        #question 3
        self.customizable_email(connection)



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

def cli(args):
    if len(args) == 0:
        #do default behavior
        pass
    elif args:
        pass
    else:
        pass

print('running')

#add a csv
#make a new table

def test01():
    bla = MySQL()
    connection = bla.get_connection()
    bla.percentile_rank(connection)
    connection.close()

def test02():
    bla = MySQL()
    connection = bla.get_connection()
    bla.create_games_and_players_table(connection)
    connection.close()

def test03():
    bla = MySQL()
    connection = bla.get_connection()
    bla.customizable_email(connection, "win")
    bla.customizable_email(connection,"lose")
    bla.customizable_email(connection, "draw")
    connection.close()

test03()

#test03()

def test1():
    df = pd.read_csv('~/Projects/droptoken/game_data.csv')
    x = Pandas(df)
    best_column_to_win = x.best_columnn_to_win()
    print(best_column_to_win)
    print(best_column_to_win == 2)

def test2():
    #create
    df = pd.read_csv('~/Projects/droptoken/game_data.csv')
    x = Pandas(df)
    bla = x.games_per_nation()
    print(x)
    #print(bla)

def test3():
    #test for winners
    df = pd.read_csv('~/Projects/droptoken/game_data.csv')
    x = Pandas(df)
    bla = x.customizable_email('win')
    return bla

#test3()

#todo
#nice looking tests
#scalable database
#streams??????
#how much memory can the output use
#different types of errors