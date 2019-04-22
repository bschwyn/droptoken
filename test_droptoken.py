from droptoken import *
import sys


def test_db_connectivity():
    try:
        db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                             user="98point6",  # your username
                             passwd="password",  # your password
                             db="benschwyn_droptoken")
        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()
        # Check if anything is returned
        if results:
            connection = True
        else:
            connection = False
    except MySQLdb.Error:
        print('Error connecting to database:')
    assert connection


def test_question1():
    db = MySQL()
    connection = db.get_connection()
    db.percentile_rank(connection)
    connection.close()
    cursor = db.cursor()
    results = cursor.fetchone()

def test_question2():
    db = MySQL()
    connection = db.get_connection()
    db.games_per_nation(connection)
    connection.close()


def test03():
    db = MySQL()
    connection = db.get_connection()
    db.customizable_email(connection, "win")
    db.customizable_email(connection,"lose")
    db.customizable_email(connection, "draw")
    connection.close()


#order of magnitude tests

# percentage points should add up to 1.0
# since there are 10k games total, there are 20k "sides" of games. Assuming no nation plays itself, there should be 20k total games.
# there are approximately 50%