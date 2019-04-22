from droptoken import *
import sys


#test

#make a bash script
#fails intelligently
#chunked intelligently

#put tests in other file
#is the first query correct
#is the second query correct
#is the third query correct
#use pytest or something more professional
#check tests with small amount of data

def testtest():
    assert 1 == 1

def test_db_connectivity():
    print('alkfj;alkdfj;aldkfja;')
    try:
        db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                             user="98point6",  # your username
                             passwd="password",  # your password
                             db="mydb")
        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()
        # Check if anything at all is returned
        if results:
            connection =  True
        else:
            connection =  False
    except MySQLdb.Error:
        print('Error connecting to database:')
    assert connection


def test01():
    db = MySQL()
    connection = db.get_connection()
    db.percentile_rank(connection)
    connection.close()
    cursor = db.cursor()
    results = cursor.fetchone()

    assert results == [5]

"""
def test02():
    bla = MySQL()
    connection = bla.get_connection()
    bla.create_games_and_players_table(connection)
    connection.close()
    assert 4==5

def test03():
    bla = MySQL()
    connection = bla.get_connection()
    bla.customizable_email(connection, "win")
    bla.customizable_email(connection,"lose")
    bla.customizable_email(connection, "draw")
    connection.close()
    assert True



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

"""