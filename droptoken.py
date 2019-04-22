import pandas as pd
import requests
import MySQLdb
import sys


# This is a data warehouse for stakeholders to answer questions about the droptoken players and games, and generally
# explore the data.


class MySQL:

    def __init__(self):
        db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                             user="98point6",  # your username
                             passwd="password",  # your password
                             db="benschwyn_droptoken")
        #cursor allows execution of queries on db
        #exectue queries
        self.connection = db

    def get_connection(self):
        return self.connection

    def is_table_empty(self, tablename, cursor):
        try:
            cursor.execute("SELECT 1 FROM " + tablename + " LIMIT 1;")
            result = cursor.fetchall()
            return len(result) == 0 #if empty return true
        except Exception :
            #table does not exist
            return True

    def populate_games_and_players_table(self, connection):

        cursor = connection.cursor()

        if self.is_table_empty('games_and_players', cursor):

            query = """
                                INSERT INTO games_and_players
                                    SELECT first_player_is_p1.game_id, player1, player2, last_player, result FROM
                                            (SELECT game_id, player_id as player1
                                            FROM game_data
                                            WHERE move_number=1)
                                        AS first_player_is_p1
                                        JOIN
                                            (SELECT game_id, player_id as player2
                                            FROM game_data
                                            WHERE move_number=2)
                                        AS first_player_is_p2
                                        ON first_player_is_p1.game_id=first_player_is_p2.game_id
                                        JOIN
                                        (SELECT game_id, player_id as last_player, result
                                            FROM game_data
                                            WHERE result='draw' or result='win'
                                        ) AS final_move
                                        ON first_player_is_p1.game_id=final_move.game_id
                                """

            cursor.execute(query)
            connection.commit()


    #QUESTION 1
    def percentile_rank(self, connection):

        cursor = connection.cursor()

        if self.is_table_empty("games_won_per_column", cursor):
            print('a;lkfja;ldkfja', sys.stderr)

            query = """
                    INSERT INTO games_won_per_column 
                        SELECT column_number, COUNT(result)
                        FROM
                            (SELECT game_id, column_number
                            FROM game_data
                            WHERE move_number=1
                            ) AS first_move
                            JOIN
                            (SELECT game_id, result
                            FROM game_data
                            WHERE result='win'
                            ) AS winning_move
                        ON first_move.game_id=winning_move.game_id
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

        #check and see if games_and_players does not exist yet, then create it
        self.populate_games_and_players_table(connection)

        print("aj;falskdj;falkdj;f", sys.stderr)
        if self.is_table_empty('games_per_nation', cursor):
            print("aj;falskdj;falkdj;f", sys.stderr)
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

        #check and see if games_and_players table does not exist, then create it
        self.populate_games_and_players_table(connection)

        if emails == "win":
            view_name = "single_game_player_win"
            where_clause = "WHERE B.result='win' and B.player_id=B.last_player;"
        elif emails == "lose":
            view_name = "single_game_player_lose"
            where_clause = "WHERE B.result='win' and B.player_id!=B.last_player;"
        else: #draw
            view_name = "single_game_player_draw"
            where_clause = "WHERE B.result='draw'"


        if self.is_table_empty(view_name, cursor):

            query = "CREATE VIEW " + view_name + """ AS
            
                        /*given the game information for players that played a single game, the win/loss/draw statement
                        is selected from this*/
                        
                        
                        SELECT B.player_id
                        FROM 
                            (
                                
                            /* The innermost union query selects game information for players that played one game
                            as player1 and players that played one game as player2. Since it is possible that a 
                            player could play one game as player1 and and another game as player2, to get only the game
                            info for players of a single game (excusively as player 1 or player2), we have the second
                            'select A.*' statement.*/
                                
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

            cursor.execute(query)
            connection.commit()

    #ALL QUESTIONS
    def create_views_for_3_questions(self):
        connection = self.get_connection()
        #question 1
        self.percentile_rank(connection)
        #question 2
        self.games_per_nation(connection)
        #question 3
        for email_type in ['win', 'lose', 'draw']:
            self.customizable_email(connection, email_type)




def main():

    db = MySQL()
    connection = db.get_connection()

    args = sys.argv[1:]
    if len(args) == 0:
        db.create_views_for_3_questions(connection)

    #check if number in cli
    if '1' in str(args):
        db.percentile_rank(connection)
    if '2' in str(args):
        db.games_per_nation(connection)
    if '3' in str(args):
        if 'win' in str(args):
            emails = 'win'
        elif 'lose' in str(args):
            emails = 'lose'
        elif 'draw' in str(args):
            emails = 'draw'
        db.customizable_email(connection, emails)



if __name__ == "__main__":
    main()
